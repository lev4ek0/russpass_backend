import typing
from enum import StrEnum, auto
from typing import Annotated, Any
from uuid import UUID

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.utils import is_body_allowed_for_status_code
from pydantic import Field, ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from app.schemas.base import BaseModel

# Аналог `OpenAPIResponseType` из fastapi_users
ResponseType = dict[int | str, dict[str, Any]]


class FieldErrorSchema(BaseModel):
    field: Annotated[
        str, Field(..., json_schema_extra={"description": "Название поля с ошибкой"})
    ]
    code: Annotated[str, Field(..., json_schema_extra={"description": "Код ошибки"})]


class ErrorType(StrEnum):
    ALERT = auto()


class ErrorCodes(StrEnum):
    WRONG_INPUT = auto()
    WRONG_JWT = auto()
    EXPIRED_JWT = auto()
    INTERNAL_SERVICE_UNAVAILABLE = auto()


class NonFieldErrorSchema(BaseModel):
    message: Annotated[
        str, Field(..., json_schema_extra={"description": "Текст ошибки"})
    ]
    code: Annotated[
        ErrorCodes, Field(..., json_schema_extra={"description": "Код ошибки"})
    ]
    id: Annotated[
        UUID | None,
        Field(
            ...,
            json_schema_extra={
                "description": "Айди объекта, с которым произошла ошибка"
            },
        ),
    ] = None
    type: Annotated[
        ErrorType | None,
        Field(..., json_schema_extra={"description": "Тип ошибки (алерт и тд)"}),
    ] = None


class APIExceptionSchema(BaseModel):
    non_field_errors: Annotated[
        list[NonFieldErrorSchema],
        Field(None, json_schema_extra={"description": "Ошибки запроса в целом"}),
    ]
    errors: Annotated[
        list[FieldErrorSchema],
        Field(None, json_schema_extra={"description": "Ошибки в полях"}),
    ]


class APIException(Exception):
    """
    Исключение, которое нужно поднимать в коде для возвращения HTTP ответа
    с ошибкой по API.
    """

    def __init__(
        self,
        status_code: int,
        headers: dict | None = None,
        non_field_errors: list | None = None,
        errors: list | None = None,
        **kwargs: ErrorCodes
    ) -> None:
        """
        :param status_code: статус код ответа
        :param headers: дополнительные заголовки ответа
        :param non_field_errors: код или список кодов ошибок, которые относятся
        к запросу в целом
        :param kwargs: ошибки в полях форм. Здесь название передаваемого аргумента --
        название поля, в котором допущена ошибка; значение -- код ошибки.
        """
        if not non_field_errors and not kwargs and not errors:
            raise ValueError("non_field_errors, errors or kwarg error should be passed")
        self.status_code = status_code
        self.headers = headers
        self.non_field_errors = non_field_errors or []
        self.errors = errors or []
        for field_name, code in kwargs.items():
            self.errors.append(FieldErrorSchema(field=field_name, code=code))

    def to_schema(self) -> APIExceptionSchema:
        return APIExceptionSchema(
            non_field_errors=self.non_field_errors, errors=self.errors
        )


async def api_exception_handler(request: Request, exc: APIException) -> Response:
    headers = getattr(exc, "headers", None)
    if not is_body_allowed_for_status_code(exc.status_code):
        return Response(status_code=exc.status_code, headers=headers)
    return JSONResponse(
        exc.to_schema().model_dump(), status_code=exc.status_code, headers=headers
    )


async def client_exception_handler(request: Request, exc: APIException) -> Response:
    return Response(exc.detail, status_code=exc.status_code, headers=exc.headers)


class ClientException(HTTPException):
    """
    Исключение для обработки ошибок API сторонних клиентов
    """

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: typing.Optional[typing.Mapping[str, str]],
    ):
        self.status_code = status_code
        self.detail = detail
        self.headers = headers


# Дополнять по мере необходимости
pydantic_errors_to_codes = {
    "The part after the @-sign is not valid. It should have a period.": "incorrect_email",
    "Field required": "field_required",
    "The part after the @-sign is not valid. It is not within a valid top-level domain.": "incorrect_email",
}


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError | ValidationError
) -> JSONResponse:
    non_field_errors = []
    errors = []
    for error in exc.errors():
        if error["loc"] == ("body",):
            text = error["msg"].lstrip("Value error, ")
            non_field_errors.append(
                NonFieldErrorSchema(message=text, code=ErrorCodes.WRONG_INPUT)
            )
        else:
            if "ctx" in error and isinstance(error["ctx"].get("error"), ValueError):
                errors.append(
                    FieldErrorSchema(
                        field=(
                            str(error["loc"][1])
                            if len(error["loc"]) > 1
                            else error["loc"][0]
                        ),
                        code=error["msg"].lstrip("Value error, "),
                    )
                )
            elif (
                "ctx" in error
                and error["ctx"].get("reason") in pydantic_errors_to_codes
            ):
                errors.append(
                    FieldErrorSchema(
                        field=(
                            str(error["loc"][1])
                            if len(error["loc"]) > 1
                            else error["loc"][0]
                        ),
                        code=pydantic_errors_to_codes[error["ctx"].get("reason")],
                    )
                )
            elif error["msg"] in pydantic_errors_to_codes:
                errors.append(
                    FieldErrorSchema(
                        field=(
                            str(error["loc"][1])
                            if len(error["loc"]) > 1
                            else error["loc"][0]
                        ),
                        code=pydantic_errors_to_codes[error["msg"]],
                    )
                )
            else:
                errors.append(
                    FieldErrorSchema(field=str(error["loc"]), code=error["msg"])
                )

    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content=APIExceptionSchema(
            non_field_errors=non_field_errors, errors=errors
        ).model_dump(),
    )
