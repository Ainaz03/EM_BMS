from fastapi import FastAPI, Depends

from app.routers.auth import router as auth_router
from app.core.auth import current_active_user
from app.models.user import User

app = FastAPI(
    title="Business Management System"
)

# Подключаем роутер аутентификации с общим префиксом /auth
app.include_router(auth_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Business Management System API"}
