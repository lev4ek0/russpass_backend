import enum
from typing import Any, Union

from fastapi import status
from httpx import AsyncClient, HTTPError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

from app.exceptions import (
    APIException,
    ClientException,
    ErrorCodes,
    NonFieldErrorSchema,
)


class HTTPMethods(enum.StrEnum):
    GET = enum.auto()
    POST = enum.auto()
    PATCH = enum.auto()
    DELETE = enum.auto()
    PUT = enum.auto()


CONNECTION_TIMEOUT = 60
MAX_RETRIES = 10

ResponseType = Union[list, dict]


class BaseClient:
    def __init__(self, base_url: str, headers: dict[str, Any] | None = None) -> None:
        self._base_url = base_url
        self._headers = headers

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_random_exponential(multiplier=2, max=120),
        retry=retry_if_exception_type(APIException),
        reraise=True,
    )
    async def _make_request(
        self,
        method: HTTPMethods,
        url: str,
        **kwargs,
    ) -> ResponseType:
        try:
            async with AsyncClient(
                base_url=self._base_url,
                headers=self._headers,
                timeout=CONNECTION_TIMEOUT,
            ) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    **kwargs,
                )

                if response.status_code >= 300:
                    raise ClientException(
                        status_code=response.status_code,
                        detail=response.content,
                        headers=response.headers,
                    )
                return response.json()
        except HTTPError:
            raise APIException(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                non_field_errors=[
                    NonFieldErrorSchema(
                        message="Один из внутренних сервисов не отвечает. Пожалуйста, попробуйте позже",
                        code=ErrorCodes.INTERNAL_SERVICE_UNAVAILABLE,
                    )
                ],
            )

    async def _get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        **kwargs,
    ) -> ResponseType:
        return await self._make_request(
            method=HTTPMethods.GET,
            url=url,
            params=params,
            **kwargs,
        )

    async def _post(
        self,
        url: str,
        json: dict | list | None = None,
        **kwargs,
    ) -> ResponseType:
        return await self._make_request(
            method=HTTPMethods.POST,
            url=url,
            json=json,
            **kwargs,
        )

    async def _patch(
        self,
        url: str,
        json: dict | list | None = None,
        **kwargs,
    ) -> ResponseType:
        return await self._make_request(
            method=HTTPMethods.PATCH,
            url=url,
            json=json,
            **kwargs,
        )

    async def _put(
        self,
        url: str,
        json: dict | list | None = None,
        **kwargs,
    ) -> ResponseType:
        return await self._make_request(
            method=HTTPMethods.PUT,
            url=url,
            json=json,
            **kwargs,
        )

    async def _delete(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        **kwargs,
    ) -> ResponseType:
        return await self._make_request(
            method=HTTPMethods.DELETE,
            url=url,
            params=params,
            **kwargs,
        )
