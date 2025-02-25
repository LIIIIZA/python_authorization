from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .admin import router as admin_router
from .login_history import router as history_router
from .oauth import vk, yandex

main_router = APIRouter()

main_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
main_router.include_router(users_router, prefix="/users", tags=["Users"])
main_router.include_router(admin_router, prefix="/admin", tags=["Admin"])
main_router.include_router(history_router, prefix="/history", tags=["History"])
main_router.include_router(vk.router, prefix="/oauth/vk", tags=["OAuth"])
main_router.include_router(yandex.router, prefix="/oauth/yandex", tags=["OAuth"])
