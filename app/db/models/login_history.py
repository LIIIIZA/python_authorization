from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import INET
from app.db.base import BaseModel

class LoginHistory(BaseModel):
    __tablename__ = "login_history"

    user_id = Column(
        String(50),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID пользователя"
    )
    
    auth_method = Column(
        String(50),
        nullable=False,
        comment="Метод аутентификации (jwt/yandex/vk)"
    )
    
    ip_address = Column(
        INET,
        nullable=True,
        comment="IP-адрес клиента"
    )
    
    user_agent = Column(
        String(512),
        nullable=True,
        comment="User-Agent клиента"
    )
    
    user = relationship(
        "User",
        back_populates="login_history",
        foreign_keys=[user_id]
    )
