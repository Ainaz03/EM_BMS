from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional

from app.schemas.user import UserRead


class MeetingBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str = Field(..., min_length=1, max_length=200, description="Тема встречи")
    start_time: datetime = Field(..., description="Время начала встречи")
    end_time: datetime = Field(..., description="Время окончания встречи")
    participants: List[int] = Field(
        ..., 
        description="Список ID пользователей-участников встречи (включая создателя)"
    )

class MeetingCreate(MeetingBase):
    ...

class MeetingUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    participants: Optional[List[int]] = None

class MeetingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    start_time: datetime
    end_time: datetime
    creator_id: int
    participants: List[int]