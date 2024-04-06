from pydantic import Field
from app.schemas.base import BaseModel

class PhotoSchema(BaseModel):
    id: int
    image: str
    height: int
    width: int
    extention: str
    tags: list[str] = Field(..., default_factory=dict)
