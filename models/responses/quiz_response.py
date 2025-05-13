from typing import Optional

from pydantic import BaseModel

from models.responses.category_short_response import CategoryShort
from models.responses.question_response import Question
from models.responses.user_profile_response import UserProfile


class Quiz(BaseModel):
    id: int
    user_id: int
    total_rate: float
    rate_count: int
    category_id: int
    approved: bool
    title: str
    description: str
    user: UserProfile
    questions: Optional[list[Question]]
    category: CategoryShort

Quiz.model_rebuild()