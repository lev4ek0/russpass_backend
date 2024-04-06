import asyncio
from sqlalchemy import Column, Table

from sqlalchemy.schema import MetaData
from pgvector.sqlalchemy import Vector
from sqlalchemy import Integer, String

from app.db import engine
metadata = MetaData()
Photo = ...
Tag = ...
PhotoTag = ...

async def create_all():
    global Photo, Tag, PhotoTag
    async with engine.begin() as conn:
        await conn.run_sync(metadata.reflect)
        Photo = metadata.tables["admin_app_photo"]
        Tag = metadata.tables["admin_app_photo"]
        PhotoTag = metadata.tables["admin_app_photo_tags"]

asyncio.run(create_all())
