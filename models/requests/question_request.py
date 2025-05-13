from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    quiz_id: int
    text: str = Field(..., min_length=3, max_length=450)