from typing import Optional

from pydantic import BaseModel

from models.responses.answer_response import Answer


class Question(BaseModel):
    id: int
    quiz_id: int
    answers: Optional[list[Answer]]
    text: str

Question.model_rebuild()