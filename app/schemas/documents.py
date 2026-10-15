from pydantic import BaseModel


class IngestFileResult(BaseModel):
    filename: str
    document_id: str
    status: str | None
    ingested: bool
    chunks_created: int
    message: str
