from typing import Annotated, AsyncGenerator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import async_session_factory
from app.utils import UserDataDataclass, decode_jwt_token


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async_session: AsyncSession = async_session_factory()  # type: ignore
    try:
        yield async_session
    finally:
        await async_session.close()


Session = Annotated[AsyncSession, Depends(get_async_session)]


http_bearer = HTTPBearer()
Token = Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)]


async def get_profile_from_jwt(token: Token) -> UserDataDataclass:
    """
    Авторизация с помощью JWT токена.
    Получение profile_id из accessToken сервиса Auth.
    """
    return decode_jwt_token(token.credentials, settings.AUTH_SECRET_KEY)


UserData = Annotated[UserDataDataclass, Depends(get_profile_from_jwt)]
