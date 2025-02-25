from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from db.models.login_history import LoginHistory

class LoginHistoryCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: UUID,
        auth_method: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> LoginHistory:
        history_entry = LoginHistory(
            user_id=user_id,
            auth_method=auth_method,
            user_agent=user_agent,
            ip_address=ip_address,
            timestamp=datetime.utcnow()
        )
        self.db.add(history_entry)
        self.db.commit()
        self.db.refresh(history_entry)
        return history_entry

    def get_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[LoginHistory]:
        return (
            self.db.query(LoginHistory)
            .filter(LoginHistory.user_id == user_id)
            .order_by(LoginHistory.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_last_login(
        self,
        user_id: UUID
    ) -> Optional[LoginHistory]:
        return (
            self.db.query(LoginHistory)
            .filter(LoginHistory.user_id == user_id)
            .order_by(LoginHistory.timestamp.desc())
            .first()
        )