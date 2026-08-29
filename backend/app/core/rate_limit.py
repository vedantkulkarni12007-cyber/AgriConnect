import time
from functools import wraps
from typing import Callable

from fastapi import HTTPException, Request, status
from redis import Redis

from app.core.config import settings

redis_client: Redis | None = None

def get_redis() -> Redis:
    global redis_client
    if redis_client is None:
        from urllib.parse import urlparse
        parsed = urlparse(settings.redis_url)
        redis_client = Redis(
            host=parsed.hostname or "localhost",
            port=parsed.port or 6379,
            password=parsed.password or None,
            db=int(parsed.path.lstrip("/")) if parsed.path else 0,
            decode_responses=True,
        )
    return redis_client

def rate_limit(max_requests: int = 100, window_seconds: int = 60, key_prefix: str = "rl"):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            r = get_redis()
            client_ip = request.client.host if request.client else "unknown"
            key = f"{key_prefix}:{client_ip}:{request.url.path}"
            now = time.time()
            pipe = r.pipeline()
            pipe.zremrangebyscore(key, 0, now - window_seconds)
            pipe.zadd(key, {str(now): now})
            pipe.zcard(key)
            pipe.expire(key, window_seconds + 10)
            _, _, count, _ = pipe.execute()
            if count > max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded: {max_requests} requests per {window_seconds}s",
                )
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
