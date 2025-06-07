from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional

from app.models.user import UserRole


class UserBase(BaseModel):
    """Базовая схема пользователя."""
    email: EmailStr
    role: UserRole = UserRole.USER


class UserCreate(UserBase):
    """Схема для создания пользователя (регистрация)."""
    password: str = Field(min_length=8, description="Пароль должен быть не менее 8 символов")


class UserUpdate(BaseModel):
    """Схема для обновления данных пользователя."""
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None


class UserRead(UserBase):
    """Схема для чтения данных пользователя из БД."""
    id: int
    team_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
