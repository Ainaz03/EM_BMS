from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

from app.models.user import UserRole


class TeamCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(..., min_length=1, max_length=100, description="Название команды")


class TeamRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    invite_code: Optional[str] = ''
    admin_id: int
    members: list[int]


class TeamMemberAdd(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int = Field(..., description="ID пользователя, которого нужно добавить в команду")

class TeamMemberRoleUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    role: UserRole = Field(..., description="Роль участника в рамках команды: MANAGER или USER")