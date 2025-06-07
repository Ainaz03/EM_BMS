from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

from app.schemas.user import UserRead


class EvaluationBase(BaseModel):
    """Базовая схема оценки."""
    score: int = Field(ge=1, le=5, description="Оценка от 1 до 5")


class EvaluationCreate(EvaluationBase):
    """Схема для создания оценки. Evaluator_id будет взят из текущего пользователя."""
    task_id: int


class EvaluationRead(EvaluationBase):
    """Схема для чтения оценки."""
    id: int
    created_at: datetime
    task_id: int
    evaluator_id: int
    evaluator: UserRead

    model_config = ConfigDict(from_attributes=True)
