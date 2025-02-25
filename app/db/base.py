from routes.auth import router as auth_router
from routes.users import router as users_router
from routes.admin import router as admin_router
from routes.login_history import router as history_router
from routes.oauth import vk, yandex
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, func
from fastapi import APIRouter

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Дата и время создания записи"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Дата и время последнего обновления записи"
    )

    def to_dict(self):
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
            if c.name not in ['created_at', 'updated_at']
        }

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"

main_router = APIRouter()

main_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
main_router.include_router(users_router, prefix="/users", tags=["Users"])
main_router.include_router(admin_router, prefix="/admin", tags=["Admin"])
main_router.include_router(history_router, prefix="/history", tags=["History"])
main_router.include_router(vk.router, prefix="/oauth/vk", tags=["OAuth"])
main_router.include_router(yandex.router, prefix="/oauth/yandex", tags=["OAuth"])