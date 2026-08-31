import uuid

from fastapi import Request
from fastapi.responses import JSONResponse


def envelope(
    success: bool,
    data,
    message: str,
    request: Request | None = None,
    code: str | None = None,
    details=None,
    status_code: int = 200,
):
    rid = getattr(request.state, "request_id", None) if request else None
    if not rid:
        rid = request.headers.get("X-Request-ID", str(uuid.uuid4())) if request else str(uuid.uuid4())
    body = {"success": success, "data": data, "message": message, "request_id": rid}
    if code:
        body["code"] = code
    if details is not None:
        body["details"] = details
    return JSONResponse(status_code=status_code, content=body)


def paginated_envelope(items, total: int, page: int, limit: int, request: Request, message="OK"):
    rid = getattr(request.state, "request_id", str(uuid.uuid4())) if request else str(uuid.uuid4())
    return {
        "success": True,
        "data": {"items": items, "total": total, "page": page, "limit": limit, "pages": (total + limit - 1) // limit},
        "message": message,
        "request_id": rid,
    }
