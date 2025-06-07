import enum
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.database import Base
from app.models.user import User
from app.models.task import Task
from app.models.evaluation import Evaluation


# --- Вспомогательные перечисления (Enums) ---

class TaskStatus(str, enum.Enum):
    """Статусы задач"""
    OPEN = "open"                # Открыта
    IN_PROGRESS = "in_progress"  # В работе
    DONE = "done"                # Выполнена


# --- Основная модель ---

class Task(Base):
    """Модель задачи"""
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.OPEN)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Кто создал задачу
    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    creator: Mapped["User"] = relationship("User", back_populates="created_tasks", foreign_keys=[creator_id])
    
    # Кому назначена задача
    assignee_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    assignee: Mapped["User"] = relationship("User", back_populates="assigned_tasks", foreign_keys=[assignee_id])
    
    # Комментарии к задаче
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="task")
    
    # Оценки задачи
    evaluations: Mapped[list["Evaluation"]] = relationship("Evaluation", back_populates="task")

    
# --- Вспомогательные модели ---

class Comment(Base):
    """Модель комментария к задаче"""
    __tablename__ = 'comments'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey('tasks.id'))
    task: Mapped["Task"] = relationship("Task", back_populates="comments")

    author_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    author: Mapped["User"] = relationship("User")
