from pydantic import BaseModel, Field


class CategoryRequest(BaseModel):
    name: str = Field(..., max_length=60, min_length=3)
    description: str = Field(..., max_length=350, min_length=3)