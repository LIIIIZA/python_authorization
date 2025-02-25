from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.dependencies import get_db
from app.core.security import get_admin_user
from app.crud.user import UserCRUD
from app.schemas.user import UserResponse

router = APIRouter()

@router.get("/users", response_model=list[UserResponse])
async def read_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    return UserCRUD(db).list_users(skip=skip, limit=limit)

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    user_crud = UserCRUD(db)
    user = user_crud.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_crud.delete(user)
    return {"message": "User deleted"}