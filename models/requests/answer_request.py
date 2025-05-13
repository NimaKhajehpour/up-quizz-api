from pydantic import BaseModel, Field


class AnswerRequest(BaseModel):
    question_id: int
    text: str = Field(..., max_length=150, min_length=3)
    isCorrect: bool