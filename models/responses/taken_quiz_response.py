from pydantic import BaseModel


class TakenQuiz(BaseModel):
    id: int
    correct_answers: int
    total_answers: int
    quiz_name: str
    quiz_description: str
