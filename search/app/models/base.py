import asyncio
from sqlalchemy import Column, Table

from sqlalchemy.schema import MetaData
from pgvector.sqlalchemy import Vector

from app.db import engine
metadata = MetaData()
Photo = ...

async def create_all():
    global Photo
    async with engine.begin() as conn:
        await conn.run_sync(metadata.reflect)
        Photo = Table("admin_app_photo", metadata, Column(
            "embeding", Vector(dim=512)
        ))


asyncio.run(create_all())
