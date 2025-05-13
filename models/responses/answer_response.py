from pydantic import BaseModel


class Answer(BaseModel):
    id: int
    question_id: int
    text: str
    isCorrect: bool

