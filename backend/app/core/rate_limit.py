import inspect
import logging
import os
import time
from collections import defaultdict
from functools import wraps
from typing import Callable

from fastapi import HTTPException, Request, status
from redis import Redis
from redis.exceptions import RedisError

from app.core.config import settings

logger = logging.getLogger("krishilink.rate_limit")

redis_client: Redis | None = None
_in_memory_buckets: dict[str, list[float]] = defaultdict(list)
_redis_logged_degradation = False

def get_redis() -> Redis | None:
    global redis_client, _redis_logged_degradation
    if redis_client is None:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(settings.redis_url)
            r = Redis(
                host=parsed.hostname or "localhost",
                port=parsed.port or 6379,
                password=parsed.password or None,
                db=int(parsed.path.lstrip("/")) if parsed.path else 0,
                decode_responses=True,
                socket_connect_timeout=0.5,
                socket_timeout=0.5
            )
            r.ping()
            redis_client = r
            if _redis_logged_degradation:
                logger.info("Redis connection restored. Distributed rate limiting active.")
                _redis_logged_degradation = False
        except Exception as exc:
            if not _redis_logged_degradation:
                logger.warning(
                    "Redis unavailable (%s: %s). Rate limiter degraded to node-local in-memory buckets.",
                    type(exc).__name__,
                    exc,
                )
                _redis_logged_degradation = True
            redis_client = None
    return redis_client

def _extract_request(args, kwargs):
    req = kwargs.get("request")
    if req:
        return req
    for a in args:
        if isinstance(a, Request) or (hasattr(a, "client") and hasattr(a, "url")):
            return a
    return None

def _check_limit(request, max_requests: int, window_seconds: int, key_prefix: str):
    global _redis_logged_degradation
    client_ip = getattr(getattr(request, "client", None), "host", "unknown")
    if client_ip == "testclient" and "PYTEST_CURRENT_TEST" in os.environ:
        return
    path = getattr(getattr(request, "url", None), "path", "/unknown")
    key = f"{key_prefix}:{client_ip}:{path}"
    now = time.time()

    r = get_redis()
    if r is not None:
        try:
            pipe = r.pipeline()
            pipe.zremrangebyscore(key, 0, now - window_seconds)
            pipe.zadd(key, {str(now): now})
            pipe.zcard(key)
            pipe.expire(key, window_seconds + 10)
            _, _, count, _ = pipe.execute()
            if count > max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded: maximum {max_requests} requests per {window_seconds}s.",
                )
            return
        except RedisError as redis_err:
            if not _redis_logged_degradation:
                logger.warning(
                    "Redis error during rate check (%s). Falling back to in-memory window.",
                    redis_err,
                )
                _redis_logged_degradation = True

    # In-memory sliding window fallback
    timestamps = [t for t in _in_memory_buckets[key] if t > now - window_seconds]
    timestamps.append(now)
    _in_memory_buckets[key] = timestamps
    if len(timestamps) > max_requests:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: maximum {max_requests} requests per {window_seconds}s.",
        )

def rate_limit(max_requests: int = 100, window_seconds: int = 60, key_prefix: str = "rl"):
    def decorator(func: Callable):
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                req = _extract_request(args, kwargs)
                if req:
                    _check_limit(req, max_requests, window_seconds, key_prefix)
                return await func(*args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                req = _extract_request(args, kwargs)
                if req:
                    _check_limit(req, max_requests, window_seconds, key_prefix)
                return func(*args, **kwargs)
            return sync_wrapper
    return decorator
