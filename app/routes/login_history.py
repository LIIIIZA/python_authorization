from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.dependencies import get_db
from app.core.security import get_current_user
from app.crud.login_history import LoginHistoryCRUD
from app.schemas.login_history import LoginHistoryResponse

router = APIRouter()

@router.get("", response_model=list[LoginHistoryResponse])
async def get_login_history(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    history_crud = LoginHistoryCRUD(db)
    return history_crud.get_by_user(current_user["id"], skip=skip, limit=limit)