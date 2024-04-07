from pydantic import ConfigDict, Field, validator

from app.schemas.base import BaseModel


class DistanceSchema(BaseModel):
    auto: str
    public_transport: str
    on_foot: str

    model_config = ConfigDict(from_attributes=True)



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
    distances: dict[str, DistanceSchema] | None = None
    images_of_closest_places: dict[str, list[str]] | None =None

    model_config = ConfigDict(from_attributes=True)


class PhotoSchemaDetails(PhotoSchema):
    similar: list[PhotoSchema]

    model_config = ConfigDict(from_attributes=True)
