from typing import Optional

from pydantic import BaseModel


class UserProfile(BaseModel):
    id: int
    display_name: str
    username: str
    about: Optional[str]
    role: str