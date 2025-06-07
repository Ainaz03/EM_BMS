from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.database import Base
from app.models.user import User


# --- Основная модель ---

class Team(Base):
    """Модель команды/компании"""
    __tablename__ = 'teams'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    invite_code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=True)
    
    # Связь с админом команды
    admin_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    admin: Mapped["User"] = relationship(foreign_keys=[admin_id])

    # Связь с участниками команды
    members: Mapped[list["User"]] = relationship("User", back_populates="team", foreign_keys="[User.team_id]")
