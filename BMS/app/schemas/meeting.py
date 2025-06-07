from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional

from app.schemas.user import UserRead


class MeetingBase(BaseModel):
    """Базовая схема встречи."""
    title: str = Field(max_length=200)
    start_time: datetime
    end_time: datetime


class MeetingCreate(MeetingBase):
    """Схема для создания встречи."""
    # При создании встречи передаем список ID пользователей-участников
    participant_ids: List[int]


class MeetingUpdate(BaseModel):
    """Схема для обновления встречи."""
    title: Optional[str] = Field(None, max_length=200)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    participant_ids: Optional[List[int]] = None


class MeetingRead(MeetingBase):
    """Схема для чтения данных о встрече."""
    id: int
    creator: UserRead # Показываем создателя встречи
    participants: List[UserRead] = [] # Показываем всех участников

    model_config = ConfigDict(from_attributes=True)
