from sqladmin.authentication import AuthenticationBackend
from fastapi import Request
from app.core.auth import fastapi_users, get_user_manager

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        user = await fastapi_users.current_user()(request)

        if not user.is_active or not user.is_superuser:
            return False

        request.session.update({"token": request.headers.get("Authorization")})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request):
        token = request.session.get("token")
        if not token:
            return None

        # Подставляем токен в заголовок, чтобы FastAPI Users его "увидел"
        request.headers.__dict__["_list"].append(
            (b"authorization", token.encode())
        )

        user = await fastapi_users.current_user()(request)
        if user.is_active and user.is_superuser:
            return user
        return None