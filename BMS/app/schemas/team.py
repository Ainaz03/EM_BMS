from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional

from app.schemas.user import UserRead


class TeamBase(BaseModel):
    """Базовая схема команды."""
    name: str = Field(max_length=100)


class TeamCreate(TeamBase):
    """Схема для создания команды. Admin_id будет добавлен на уровне эндпоинта."""
    pass


class TeamUpdate(BaseModel):
    """Схема для обновления названия команды."""
    name: Optional[str] = Field(None, max_length=100)


class TeamRead(TeamBase):
    """Схема для чтения данных команды, включая её участников."""
    id: int
    admin_id: int
    invite_code: Optional[str] = None
    members: List[UserRead] = [] # Возвращаем список пользователей с их данными

    model_config = ConfigDict(from_attributes=True)
    
class TeamMemberAdd(BaseModel):
    user_id: int = Field(..., ge=1)
    