from pydantic import BaseModel, Field


class QuizRequest(BaseModel):
    category_id: int
    title: str = Field(..., min_length=3, max_length=60)
    description: str = Field(..., min_length=3, max_length=450)