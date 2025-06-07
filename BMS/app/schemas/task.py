from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional

from app.schemas.comment import CommentRead
from app.models.task import TaskStatus
from app.schemas.user import UserRead


class TaskBase(BaseModel):
    """Базовая схема задачи."""
    title: str = Field(max_length=200)
    description: Optional[str] = None
    deadline: Optional[datetime] = None


class TaskCreate(TaskBase):
    """Схема для создания задачи."""
    assignee_id: int


class TaskUpdate(BaseModel):
    """Схема для обновления задачи."""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    deadline: Optional[datetime] = None
    assignee_id: Optional[int] = None


class TaskRead(TaskBase):
    """Схема для чтения задачи со всеми связанными данными."""
    id: int
    created_at: datetime
    status: TaskStatus
    team_id: int
    
    creator: UserRead # Показываем создателя
    assignee: UserRead # Показываем исполнителя
    comments: List[CommentRead] = [] # Показываем все комментарии к задаче

    model_config = ConfigDict(from_attributes=True)
