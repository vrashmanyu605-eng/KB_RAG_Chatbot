from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import DocumentChunk
from app.services.embeddings import embed_texts


def retrieve_chunks(
    db: Session, query: str, top_k: int | None = None
) -> list[DocumentChunk]:
    query_vector = embed_texts([query], task_type="RETRIEVAL_QUERY")[0]
    limit = top_k or get_settings().retrieval_top_k
    statement = (
        select(DocumentChunk)
        .where(
            (DocumentChunk.status.is_(None))
            | (~DocumentChunk.status.ilike("unverified"))
        )
        .order_by(DocumentChunk.embedding.cosine_distance(query_vector))
        .limit(limit)
    )
    return list(db.scalars(statement).all())
