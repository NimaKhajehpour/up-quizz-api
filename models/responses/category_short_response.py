from pydantic import BaseModel


class CategoryShort(BaseModel):
    id: int
    name: str
    description: str