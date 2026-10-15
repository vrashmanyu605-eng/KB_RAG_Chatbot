from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.documents import IngestFileResult
from app.services.ingestion import ingest_document

router = APIRouter(tags=["ingestion"])

SUPPORTED_CONTENT_TYPES = {
    "text/markdown",
    "text/plain",
    "application/octet-stream",
}


@router.post("/documents", response_model=list[IngestFileResult])
def upload_documents(
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
) -> list[IngestFileResult]:
    results = []
    for upload in files:
        if not upload.filename:
            raise HTTPException(status_code=400, detail="Every uploaded file needs a filename.")
        if not upload.filename.lower().endswith((".md", ".txt")):
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported file type for {upload.filename}; upload .md or .txt files.",
            )
        if upload.content_type not in SUPPORTED_CONTENT_TYPES:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported content type for {upload.filename}.",
            )
        try:
            raw_content = upload.file.read()
            content = raw_content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise HTTPException(
                status_code=422,
                detail=f"{upload.filename} must be UTF-8 encoded.",
            ) from exc
        try:
            result = ingest_document(
                db=db,
                filename=upload.filename,
                content=content,
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        results.append(result)
    return results
