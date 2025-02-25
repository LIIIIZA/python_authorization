from fastapi import APIRouter, Request, Depends, HTTPException
import httpx
from urllib.parse import urlencode
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import generate_csrf_state, validate_csrf_state, create_access_token
from app.db.dependencies import get_db
from app.crud.user import UserCRUD

router = APIRouter()

@router.get("/auth")
async def auth_yandex(request: Request):
    params = {
        "client_id": settings.YANDEX_CLIENT_ID,
        "redirect_uri": settings.YANDEX_REDIRECT_URI,
        "response_type": "code",
        "state": generate_csrf_state(request)
    }
    return {"auth_url": f"https://oauth.yandex.ru/authorize?{urlencode(params)}"}

@router.get("/callback")
async def yandex_callback(
    request: Request,
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    if not validate_csrf_state(request, state):
        raise HTTPException(status_code=400, detail="Invalid CSRF token")
    
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth.yandex.ru/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": settings.YANDEX_CLIENT_ID,
                "client_secret": settings.YANDEX_CLIENT_SECRET
            }
        )
        
        user_info = await client.get(
            "https://login.yandex.ru/info",
            headers={"Authorization": f"OAuth {token_response.json()['access_token']}"}
        )
        
        user_crud = UserCRUD(db)
        user = user_crud.get_by_yandex_id(user_info["id"])
        if not user:
            user = user_crud.create_with_oauth(
                provider="yandex",
                oauth_id=user_info["id"],
                email=user_info.get("default_email")
            )
        
        return {"access_token": create_access_token(user.id, user.role)}