from fastapi import APIRouter

from app.core.auth import auth_backend, fastapi_users
from app.schemas.user import UserRead, UserCreate


router = APIRouter(prefix="/auth")


# Роутер для регистрации
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/register"
)

# Роутер для логина/аутентификации
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt"
)

# Роутер для сброса пароля
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/forgot-password"
)
