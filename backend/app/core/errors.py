from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uuid


def request_id_var() -> str:
    return str(uuid.uuid4())


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    rid = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "data": None,
            "message": "Validation failed",
            "code": "VALIDATION_ERROR",
            "details": exc.errors(),
            "request_id": rid,
        },
    )


async def generic_exception_handler(request: Request, exc: Exception):
    rid = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "data": None,
            "message": "Internal server error",
            "code": "INTERNAL_ERROR",
            "request_id": rid,
        },
    )
