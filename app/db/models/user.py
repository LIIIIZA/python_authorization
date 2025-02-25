from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import relationship
from app.db.base import BaseModel
from app.schemas.user import UserRole

class User(BaseModel):
    """Модель пользователя системы"""
    __tablename__ = "users"

    email = Column(
        String(255), 
        unique=True, 
        index=True,
        nullable=False,
        comment="Email пользователя (уникальный идентификатор)"
    )
    
    hashed_password = Column(
        String(1024),
        nullable=True,  
        comment="Хэшированный пароль"
    )
    
    role = Column(
        Enum(UserRole),
        default=UserRole.USER,
        nullable=False,
        comment="Роль пользователя в системе"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Флаг активности аккаунта"
    )
    
    yandex_id = Column(
        String(50),
        unique=True,
        index=True,
        nullable=True,
        comment="Идентификатор Yandex OAuth"
    )
    
    login_history = relationship(
        "LoginHistory",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )