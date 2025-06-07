import enum

from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.database import Base
from app.models.task import Task
from app.models.team import Team
from app.models.meeting import Meeting


# --- Вспомогательные перечисления (Enums) ---

class UserRole(str, enum.Enum):
    """Роли пользователей"""
    ADMIN = "admin"      # Админ команды, может всё в рамках команды
    MANAGER = "manager"  # Менеджер, может создавать задачи и управлять ими
    USER = "user"        # Обычный сотрудник, может только выполнять задачи


# --- Ассоциативная таблица для связи "многие-ко-многим" между Встречами и Пользователями ---
# У одной встречи много участников, и один пользователь может участвовать во многих встречах.

meeting_participants_association = Table(
    'meeting_participants',
    Base.metadata,
    Column('meeting_id', Integer, ForeignKey('meetings.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)


# --- Основная модель ---

class User(Base):
    """Модель пользователя"""
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)
    
    # Связь с командой: у пользователя может быть одна команда
    team_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('teams.id'), nullable=True)
    team: Mapped["Team"] = relationship(back_populates="members", foreign_keys=[team_id])

    # Задачи, которые пользователь создал (для менеджеров/админов)
    created_tasks: Mapped[list["Task"]] = relationship("Task", back_populates="creator", foreign_keys="Task.creator_id")
    # Задачи, которые назначены пользователю
    assigned_tasks: Mapped[list["Task"]] = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id")
    
    # Встречи, в которых пользователь участвует
    meetings: Mapped[list["Meeting"]] = relationship(
        "Meeting",
        secondary=meeting_participants_association,
        back_populates="participants"
    )
