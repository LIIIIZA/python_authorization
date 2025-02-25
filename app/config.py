from pydantic import BaseSettings, PostgresDsn, RedisDsn, AnyUrl
from typing import Optional

class Settings(BaseSettings):
    ENV: str = "dev"
    DEBUG: bool = False
    PROJECT_NAME: str = "Auth Service"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: PostgresDsn = "postgresql+asyncpg://postgres:postgres@localhost:5432/db"
    
    JWT_SECRET_KEY: str = "secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    YANDEX_CLIENT_ID: Optional[str] = '908fb316ca546d09bb0097e660a28fc'
    YANDEX_CLIENT_SECRET: Optional[str] = '0f418a12184a42b9bb094198b43490cc'
    YANDEX_REDIRECT_URI: Optional[AnyUrl] = 'https://oauth.yandex.ru/verification_code'

    TELEGRAM_TOKEN: Optional[str] = '7929653036:AAFfX6nwtSoUh4IYiOsJRwKaKcShtdMHdtM'
    REDIS_URL: RedisDsn = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

