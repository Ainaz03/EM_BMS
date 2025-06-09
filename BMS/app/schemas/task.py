from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from enum import Enum

from app.schemas.comment import CommentRead
from app.schemas.evaluation import EvaluationRead


# --- Статусы задач ---
class TaskStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"

# --- Основные задачи ---
class TaskBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Описание")
    deadline: Optional[datetime] = Field(None, description="Дедлайн задачи")
    assignee_id: int = Field(..., description="ID исполнителя")

class TaskCreate(TaskBase):
    ...

class TaskUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: Optional[str] = Field(None, description="Новое название")
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    assignee_id: Optional[int] = None
    status: Optional[TaskStatus] = None

class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    creator_id: int
    assignee_id: int
    created_at: datetime
    deadline: Optional[datetime]
    comments: List[CommentRead]
    evaluations: List[EvaluationRead]
