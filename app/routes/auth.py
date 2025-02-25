from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.tasks.telegram import telegram
from app.core.rabbitmq import publish_message
from fastapi.security import OAuth2PasswordBearer
from app.db.dependencies import get_db
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    add_to_blacklist
)
from app.crud.user import UserCRUD
from app.schemas.token import Token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/register", response_model=Token)
async def register(
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    user_crud = UserCRUD(db)
    if user_crud.get_by_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = user_crud.create(
        email=email,
        hashed_password=get_password_hash(password)
    )
    publish_message('registrations', {'email': user.email})
    return {
        "access_token": create_access_token(user.id, user.role),
        "token_type": "bearer"
    }

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = UserCRUD(db).get_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials"
        )
    
    return {
        "access_token": create_access_token(user.id, user.role),
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    add_to_blacklist(token, timedelta(minutes=15).total_seconds())
    return {"message": "Successfully logged out"}