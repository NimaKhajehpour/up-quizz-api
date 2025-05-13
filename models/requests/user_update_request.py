from typing import Optional

from pydantic import BaseModel, Field


class UserUpdateRequest(BaseModel):
    display_name: str = Field(..., max_length=100, min_length=2)
    about: Optional[str] = Field(None, max_length=300, min_length=10)