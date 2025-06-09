from fastapi_users import schemas
from typing import Optional
from pydantic import EmailStr

from app.models.user import UserRole


class UserRead(schemas.BaseUser[int]):
    role: UserRole
    team_id: Optional[int] = None


class UserCreate(schemas.BaseUserCreate):
    role: Optional[UserRole] = UserRole.USER


class UserUpdate(schemas.BaseUserUpdate):
    role: Optional[UserRole] = None
