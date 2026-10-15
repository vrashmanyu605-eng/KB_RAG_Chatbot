from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import DocumentChunk
from app.schemas.documents import IngestFileResult
from app.services.chunking import chunk_text
from app.services.document_parser import parse_document
from app.services.embeddings import embed_texts


def ingest_document(
    db: Session,
    filename: str,
    content: str,
) -> IngestFileResult:
    metadata, body = parse_document(content)
    raw_status = metadata.get("status")
    status = str(raw_status).strip() if raw_status is not None else None
    raw_document_id = metadata.get("doc_id")
    document_id = (
        str(raw_document_id).strip()
        if raw_document_id is not None and str(raw_document_id).strip()
        else filename
    )

    if status is not None and (status.casefold() == "unverified" or status.casefold() == "deprecated"):
        return IngestFileResult(
            filename=filename,
            document_id=document_id,
            status=status,
            ingested=False,
            chunks_created=0,
            message="Skipped because the document status is unverified.",
        )

    chunks = chunk_text(
        body,
        chunk_size=get_settings().chunk_size,
        overlap=get_settings().chunk_overlap,
    )
    if not chunks:
        raise ValueError(f"{filename} has no document body to ingest.")

    vectors = embed_texts(chunks, task_type="RETRIEVAL_DOCUMENT")
    if len(vectors) != len(chunks):
        raise RuntimeError("Embedding count does not match document chunk count.")

    tagged_chunks = [
        DocumentChunk(
            document_id=document_id,
            chunk_index=index,
            content=chunk,
            embedding=vector,
            status=status,
            metadata_={
                **metadata,
                "document_id": document_id,
                "source_file": filename,
                "chunk_index": index,
                "chunk_count": len(chunks),
            },
        )
        for index, (chunk, vector) in enumerate(zip(chunks, vectors, strict=True))
    ]
    try:
        db.execute(
            delete(DocumentChunk).where(DocumentChunk.document_id == document_id)
        )
        db.add_all(tagged_chunks)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return IngestFileResult(
        filename=filename,
        document_id=document_id,
        status=status,
        ingested=True,
        chunks_created=len(chunks),
        message="Document ingested successfully.",
    )
