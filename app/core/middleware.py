import time
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from .config import settings
from .logger import logger
from .redis import redis_manager

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"Request error: {str(e)}")
            raise
        
        process_time = time.time() - start_time
        logger.info(
            f"Method={request.method} "
            f"Path={request.url.path} "
            f"Status={response.status_code} "
            f"Time={process_time:.3f}s"
        )
        
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.update({
            "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        })
        return response

class RateLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if settings.ENV == "prod":
            client_ip = request.client.host
            key = f"rate_limit:{client_ip}"
            
            conn = redis_manager.get_connection()
            if conn:
                current = conn.incr(key)
                if current == 1:
                    conn.expire(key, 60)
                
                if current > 100:
                    raise HTTPException(
                        status_code=429, 
                        detail="Too many requests"
                    )
        
        return await call_next(request)