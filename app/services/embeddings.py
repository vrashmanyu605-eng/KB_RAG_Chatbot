from collections.abc import Sequence

from google import genai
from google.genai import types

from app.config import get_settings


def embed_texts(
    texts: Sequence[str], task_type: str
) -> list[list[float]]:
    settings = get_settings()
    if not settings.google_api_key:
        raise RuntimeError("Set GOOGLE_API_KEY before requesting Gemini embeddings.")
    client = genai.Client(api_key=settings.google_api_key)
    vectors: list[list[float]] = []
    batch_size = 100
    for offset in range(0, len(texts), batch_size):
        response = client.models.embed_content(
            model=settings.embedding_model,
            contents=list(texts[offset : offset + batch_size]),
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=settings.embedding_dimensions,
            ),
        )
        if not response.embeddings:
            raise RuntimeError("Gemini returned no embeddings.")
        vectors.extend(
            [list(embedding.values) for embedding in response.embeddings]
        )
    if len(vectors) != len(texts):
        raise RuntimeError("Gemini returned an unexpected number of embeddings.")
    return vectors
