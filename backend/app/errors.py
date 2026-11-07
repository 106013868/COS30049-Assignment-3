"""
errors.py
turns every error into one JSON format: {"error": {"code": ..., "message": ...}}
"""
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# error code for each HTTP status the API can return
STATUS_CODES = {
    400: "BAD_REQUEST",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    411: "LENGTH_REQUIRED",
    413: "PAYLOAD_TOO_LARGE",
    422: "VALIDATION_ERROR",
    500: "INTERNAL_ERROR",
    503: "SERVICE_UNAVAILABLE",
}


def error_response(status_code: int, message: str, headers: dict | None = None) -> JSONResponse:
    code = STATUS_CODES.get(status_code, "ERROR")
    return JSONResponse(status_code=status_code,
                        content={"error": {"code": code, "message": message}},
                        headers=headers)


async def validation_error_handler(request: Request, exc: RequestValidationError):
    first = exc.errors()[0]
    field = first["loc"][-1]
    message = first["msg"].removeprefix("Value error, ")
    # replace Pydantic's wording with clearer messages for the common cases
    if first["type"] == "string_too_short":
        message = "Please enter a URL."
    elif first["type"] == "string_too_long":
        message = f"URL must be {first['ctx']['max_length']} characters or fewer."
    elif first["type"] == "missing":
        message = f"The '{field}' field is required."
    elif first["type"] in ("json_invalid", "model_attributes_type"):
        message = "Request body must be JSON like {\"url\": \"example.com\"}."
    return error_response(422, message)


async def http_error_handler(request: Request, exc: StarletteHTTPException):
    return error_response(exc.status_code, str(exc.detail), getattr(exc, "headers", None))