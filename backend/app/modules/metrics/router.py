from fastapi import APIRouter, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

router = APIRouter(tags=["observability"])

REQUEST_COUNT = Counter("krishilink_requests_total", "Total requests", ["method","path","status"])
REQUEST_LATENCY = Histogram("krishilink_request_duration_seconds", "Request latency")

@router.get("/metrics", include_in_schema=False)
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
