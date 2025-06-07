from datetime import datetime

from sqlalchemy import DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.database import Base
from app.models.user import User
from app.models.task import Task


# --- Основная модель ---

class Evaluation(Base):
    """Модель оценки выполненной задачи"""
    __tablename__ = 'evaluations'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Какую задачу оценили
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey('tasks.id'), unique=True)
    task: Mapped["Task"] = relationship("Task", back_populates="evaluations")

    # Кто оценил (менеджер/админ)
    evaluator_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    evaluator: Mapped["User"] = relationship("User")
