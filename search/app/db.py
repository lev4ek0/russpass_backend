"""
Sets up postgres connection pool.
"""

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine,  AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    echo=settings.LOG_QUERIES,
    connect_args={"server_settings": {"jit": "off"}},
    # Нужно для работы сelery, чтобы не использовать один и тот же AsyncEngine в разных циклах событий
    poolclass=NullPool,
)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
