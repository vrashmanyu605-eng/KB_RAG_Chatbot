from pydantic import BaseModel, Field


class EvaluationRequest(BaseModel):
    question: str = Field(min_length=1, max_length=8000)
    answer: str = Field(min_length=1, max_length=12000)
    contexts: list[str] | None = Field(default=None, max_length=20)
    top_k: int | None = Field(default=None, ge=1, le=20)


class EvaluationScores(BaseModel):
    relevance: int = Field(ge=0, le=5)
    recall: int = Field(ge=0, le=5)
    precision: int = Field(ge=0, le=5)


class EvaluationResponse(EvaluationScores):
    rationales: dict[str, str]
    evaluated_context_count: int
