from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .context import current_request_id
from .disclaimer import DISCLAIMER


class ApiError(Exception):
    def __init__(self, status_code: int, code: str, message: str, *,
                 fallback: str | None = None, headers: dict[str, str] | None = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.fallback = fallback
        self.headers = headers or {}


def envelope(status: int, code: str, message: str, fallback: str | None = None,
             headers: dict[str, str] | None = None) -> JSONResponse:
    body = {
        "request_id": current_request_id(),
        "error": {"code": code, "message": message, "fallback": fallback},
        "disclaimer": DISCLAIMER,
    }
    return JSONResponse(body, status_code=status, headers=headers)


def register_error_handlers(app) -> None:
    @app.exception_handler(ApiError)
    async def _api_error(_: Request, exc: ApiError):
        return envelope(exc.status_code, exc.code, exc.message, exc.fallback, exc.headers)

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, exc: RequestValidationError):
        return envelope(422, "VALIDATION_ERROR", "The request was not valid. Please check the fields and try again.")

    @app.exception_handler(StarletteHTTPException)
    async def _http(_: Request, exc: StarletteHTTPException):
        return envelope(exc.status_code, "HTTP_ERROR", str(exc.detail))

    @app.exception_handler(Exception)
    async def _unhandled(_: Request, exc: Exception):
        return envelope(500, "INTERNAL_ERROR", "Something went wrong. You can still enter medicine names by typing.",
                        fallback="manual_entry")
