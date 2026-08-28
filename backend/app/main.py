import uuid
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.errors import validation_exception_handler, generic_exception_handler
from app.modules.health.router import router as health_router
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.crops.router import router as crops_router
from app.modules.markets.router import router as markets_router
from app.modules.prices.router import router as prices_router
from app.modules.lots.router import router as lots_router
from app.modules.matching.router import router as matching_router

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        rid = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = rid
        start = time.time()
        response = await call_next(request)
        response.headers["X-Request-ID"] = rid
        response.headers["X-Process-Time-ms"] = str(round((time.time() - start) * 1000, 2))
        return response

    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    app.include_router(health_router, prefix=settings.api_v1_prefix)
    app.include_router(auth_router, prefix=settings.api_v1_prefix)
    app.include_router(users_router, prefix=settings.api_v1_prefix)
    app.include_router(crops_router, prefix=settings.api_v1_prefix)
    app.include_router(markets_router, prefix=settings.api_v1_prefix)
    app.include_router(prices_router, prefix=settings.api_v1_prefix)
    app.include_router(lots_router, prefix=settings.api_v1_prefix)
    app.include_router(matching_router, prefix=settings.api_v1_prefix)

    @app.get("/", include_in_schema=False)
    def root():
        return {
            "success": True,
            "data": {"name": settings.app_name, "version": settings.app_version, "docs": "/docs"},
            "message": "KrishiLink API 2.0 — see /docs",
            "request_id": None,
        }

    return app

app = create_app()
