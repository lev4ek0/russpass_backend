import datetime
import io
from dataclasses import dataclass
from datetime import tzinfo
from typing import Annotated, Any
from uuid import UUID, uuid4

import aiofiles
import jwt
import pytz
from fastapi import Depends, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from PIL import Image

from app.config import MEDIA_DIR
from app.exceptions import (
    APIException,
    ErrorCodes,
    FieldErrorSchema,
    NonFieldErrorSchema,
)

JWT_ALGORITHM = "HS256"
AUDIENCE = ["fastapi-users:auth"]

BAD_TOKEN_EXCEPTION = APIException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    non_field_errors=[
        NonFieldErrorSchema(message="Некорректный JWT", code=ErrorCodes.WRONG_JWT)
    ],
    headers={"WWW-Authenticate": "Bearer"},
)

EXPIRED_TOKEN_EXCEPTION = APIException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    non_field_errors=[
        NonFieldErrorSchema(message="Просроченный JWT", code=ErrorCodes.EXPIRED_JWT)
    ],
    headers={"WWW-Authenticate": "Bearer"},
)


@dataclass
class UserDataDataclass:
    permissions: list[str]
    profile_id: UUID
    is_editor: bool


def decode_jwt_token(token: str, secret_key: str) -> UserDataDataclass:
    try:
        data = jwt.decode(
            token, secret_key, algorithms=[JWT_ALGORITHM], audience=AUDIENCE
        )
    except jwt.exceptions.ExpiredSignatureError:
        raise EXPIRED_TOKEN_EXCEPTION
    except jwt.exceptions.PyJWTError:
        raise BAD_TOKEN_EXCEPTION

    try:
        user_id = data.get("sub")
        permissions = data.get("permissions")
        return UserDataDataclass(
            permissions=permissions, profile_id=UUID(user_id)
        )
    except (ValueError, TypeError):
        raise BAD_TOKEN_EXCEPTION


def verify_image(contents: Any) -> None:
    """
    Проверяет, что файл действительно является изображением,
    с помощью PIL.
    """
    try:
        img = Image.open(io.BytesIO(contents))
        img.verify()
    except Exception as exc:
        raise APIException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            errors=[
                FieldErrorSchema(
                    field="files", code="Загруженный файл не является изображением"
                )
            ],
        ) from exc


async def save_file(file: UploadFile) -> str:
    try:
        # Проверка формата
        extension = file.filename.split(".")[-1]
        if extension not in ("png", "jpg", "jpeg", "tiff", "bmp"):
            raise APIException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                errors=[
                    FieldErrorSchema(
                        field="files", code="Неподдерживаемый формат изображения"
                    )
                ],
            )

        contents = await file.read()

        save_filename = str(uuid4()) + "." + extension
        save_file_path = MEDIA_DIR / "user_files" / save_filename

        # Проверка того, что файл действительно является изображением
        await run_in_threadpool(verify_image, contents)

        async with aiofiles.open(save_file_path, mode="wb") as f:
            await f.write(contents)
    finally:
        await file.close()
    return str(save_file_path)


async def zone_param(zone: str = "Europe/Moscow") -> tzinfo:
    return pytz.timezone(zone)


Zone = Annotated[tzinfo, Depends(zone_param)]


def datetime_as_string(date: datetime, zone: tzinfo) -> str:
    return date.astimezone(zone).strftime("%d.%m.%Y ⦁ %H:%M")


def sqlalchemy_model_to_dict(model, excludes: list[str] | None = None) -> dict:
    db_obj_dict = model.__dict__.copy()
    del db_obj_dict["_sa_instance_state"]
    for key in (attr for attr in dir(model) if not attr.startswith("_")):
        if key not in db_obj_dict:
            try:
                db_obj_dict[key] = getattr(model, key)
            except:
                pass
    for exclude in excludes or []:
        if exclude in db_obj_dict:
            del db_obj_dict[exclude]
    return db_obj_dict
