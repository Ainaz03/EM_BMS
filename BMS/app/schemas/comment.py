from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

from app.schemas.user import UserRead


class CommentBase(BaseModel):
    """Базовая схема комментария."""
    text: str


class CommentCreate(CommentBase):
    """Схема для создания комментария. Task_id и author_id будут добавлены в эндпоинте."""
    pass


class CommentUpdate(BaseModel):
    """Схема для редактирования комментария."""
    text: Optional[str] = None


class CommentRead(CommentBase):
    """Схема для чтения комментария."""
    id: int
    created_at: datetime
    task_id: int
    author_id: int
    author: UserRead

    model_config = ConfigDict(from_attributes=True)
