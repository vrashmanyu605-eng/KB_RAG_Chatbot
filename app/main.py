from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import initialize_database
from app.routers import chat, evaluation, ingestion


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="Knowledge Base API",
    description="File ingestion, vector search, provider-agnostic chat, and LLM evaluation.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(ingestion.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(evaluation.router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
