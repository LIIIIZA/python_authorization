import redis
from typing import Optional
from .config import settings
from .logger import logger

class RedisManager:
    def __init__(self):
        self._pool = None

    def init_redis(self):
        try:
            self._pool = redis.ConnectionPool.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_timeout=5,
                max_connections=20
            )
            logger.info("Redis connection pool initialized")
        except Exception as e:
            logger.error(f"Redis init error: {str(e)}")
            raise

    def get_connection(self) -> Optional[redis.Redis]:
        if not self._pool:
            self.init_redis()
        
        try:
            return redis.Redis(connection_pool=self._pool)
        except Exception as e:
            logger.error(f"Redis connection error: {str(e)}")
            return None

    async def close(self):
        if self._pool:
            self._pool.disconnect()
            logger.info("Redis connections closed")


redis_manager = RedisManager()