from datetime import datetime

from sqlalchemy import DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.database import Base
from app.models.user import meeting_participants_association


# --- Основная модель ---

class Meeting(Base):
    """Модель встречи"""
    __tablename__ = 'meetings'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Кто создал встречу
    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    creator: Mapped["User"] = relationship("User")
    
    # Участники встречи (многие-ко-многим)
    participants: Mapped[list["User"]] = relationship(
        "User",
        secondary=meeting_participants_association,
        back_populates="meetings"
    )