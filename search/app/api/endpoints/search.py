import shutil
import tempfile
from fastapi import APIRouter, UploadFile
from sqlalchemy import select

from app.api.deps import Session
from app.services.triton_inference import TritonClient
from app.models.base import Photo

router = APIRouter()


@router.get("")
async def get_similar(
    session: Session,
    file: UploadFile | None = None,
):
    try:
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
            
            client = TritonClient('tritonserver:8000', '/app/bpe.model')

            res = client.inference_image(temp_file_path)
            print(res.shape)
            stmt = select(Photo).order_by(Photo.c.embeding.l2_distance(res)).limit(5)

            result = await session.execute(stmt)
            items = result.scalars().all()

            import logging
            logging.error(items)
    finally:
        file.file.close()

    # res = client.inference_image("1.jpg")
    return res.shape
