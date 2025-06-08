from fastapi import APIRouter

from app.core.auth import auth_backend, fastapi_users
from app.schemas.user import UserRead, UserCreate, UserUpdate

router = APIRouter(prefix="/auth", tags=["auth"])

# Регистрация
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate))

# Логин
router.include_router(
    fastapi_users.get_auth_router(auth_backend))

# Сброс пароля (запрос токена и сброс)
router.include_router(
    fastapi_users.get_reset_password_router())

# Верификация email — передаём схему для чтения пользователя
router.include_router(
    fastapi_users.get_verify_router(UserRead))

# CRUD пользователей (только админы)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate))
