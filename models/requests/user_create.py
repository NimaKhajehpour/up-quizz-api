import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from utils.regex_validator import USERNAME, PASSWORD


class UserCreate(BaseModel):
    display_name: str = Field(..., max_length=100, min_length=2)
    username: str = Field(..., max_length=20, min_length=3)
    about: Optional[str] = Field(None, max_length=300, min_length=10)
    password: str = Field(..., min_length=8)

    @field_validator("username")
    def validate_username(cls, v):
        if not re.fullmatch(USERNAME, v):
            raise ValueError("Username must be 3-20 characters and contain only letters, numbers, or underscores.")
        return v

    @field_validator("password")
    def validate_password(cls, v):
        # Manually check password rules since lookaheads are not allowed
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r"[@$!%*?&]", v):
            raise ValueError("Password must contain at least one special character (@$!%*?&).")
        return v