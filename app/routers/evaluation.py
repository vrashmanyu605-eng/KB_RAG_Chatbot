from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.evaluation import EvaluationRequest, EvaluationResponse
from app.services.evaluation import evaluate_answer

router = APIRouter(tags=["evaluation"])


@router.post("/evaluations", response_model=EvaluationResponse)
def evaluate(
    request: EvaluationRequest,
    db: Session = Depends(get_db),
) -> EvaluationResponse:
    return evaluate_answer(db, request)
