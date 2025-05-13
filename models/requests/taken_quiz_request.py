from pydantic import BaseModel, Field


class TakenQuizRequest(BaseModel):
    quiz_id: int
    correct_answers: int = Field(..., ge=0)
    total_answers: int = Field(..., gt=0)