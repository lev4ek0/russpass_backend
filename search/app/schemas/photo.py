from pydantic import Field, validator
from app.schemas.base import BaseModel

class PhotoSchema(BaseModel):
    id: int
    image: str = Field(..., description="Path to the image")
    name: str | None

    @validator('image')
    def add_media_prefix(cls, v):
        return "media/" + v

    height: int
    width: int
    extention: str
    tags: list[str] = Field(..., default_factory=list)
