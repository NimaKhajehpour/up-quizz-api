from typing import Optional

from pydantic import BaseModel

# from models.responses.quiz_response import Quiz


class Category(BaseModel):
    id: int
    name: str
    description: str
    approved: bool