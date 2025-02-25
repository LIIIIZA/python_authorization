import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, status

from .core.config import settings
from .core.logger import setup_logging
from .core.middleware import log_requests, security_headers, LoggingMiddleware, SecurityHeadersMiddleware, RateLimiterMiddleware
from .db.session import engine, SessionLocal, check_db_connection
from .core.redis import redis, ping_redis
from .routes import main_router
from .cli import cli as app_cli

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Контекст жизненного цикла приложения"""
    setup_logging()
    logging.info("Starting application...")

    if not check_db_connection():
        logging.error("Database connection failed!")
        raise RuntimeError("Database connection failed")
    
    if not ping_redis():
        logging.error("Redis connection failed!")
        raise RuntimeError("Redis connection failed")
    
    yield  
    

    logging.info("Shutting down application...")
    await redis.close()
    engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

app.middleware("http")(log_requests)
app.middleware("http")(security_headers)
app.add_middleware(LoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimiterMiddleware)

app.include_router(main_router)

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "OK",
        "database": "connected" if check_db_connection() else "disconnected",
        "redis": "connected" if ping_redis() else "disconnected"
    }

app.cli = app_cli

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_config=None
    )
