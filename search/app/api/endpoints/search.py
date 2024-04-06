import shutil
import tempfile
from fastapi import APIRouter, UploadFile
from fastapi_pagination import Page, paginate
from app.schemas.photo import PhotoSchema
from sqlalchemy import select

from app.api.deps import Session
from app.services.triton_inference import TritonClient
from app.models.base import Photo
from sqlalchemy.orm import selectinload

router = APIRouter()


@router.post("/photo")
async def search_by_photo(
    session: Session,
    file: UploadFile,
) -> Page[PhotoSchema]:
    try:
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
            
            client = TritonClient('tritonserver:8000', '/app/bpe.model')

            res = client.inference_image(temp_file_path)
            stmt = select(Photo).order_by(Photo.c.embeding.l2_distance(res)).limit(50)

            result = await session.execute(stmt)
            items = result.all()
    finally:
        file.file.close()
    return paginate(items)


@router.get("/text")
async def search_by_text(
    session: Session,
    text: str,
) -> Page[PhotoSchema]:
    client = TritonClient('tritonserver:8000', '/app/bpe.model')

    res = client.inference_text(text)
    stmt = select(Photo).order_by(Photo.c.embeding.l2_distance(res)).limit(50)

    result = await session.execute(stmt)
    items = result.all()
    return paginate(items)
