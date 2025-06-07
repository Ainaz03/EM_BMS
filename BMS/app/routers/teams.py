from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List

from app.core.database import get_async_session
from app.core.auth import current_active_user
from app.models.user import User
from app.models.team import Team
from app.schemas.team import TeamRead, TeamCreate


router = APIRouter(prefix="/teams", tags=["Teams"])


@router.post("/", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
def create_team(
    team_in: TeamCreate,
    db: Session = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    """Создание новой команды. Текущий пользователь становится её владельцем."""
    db_team = Team(**team_in.dict(), owner_id=user.id)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team


@router.get("/{team_id}", response_model=TeamRead)
def get_team(
    team_id: int,
    db: Session = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    """Получение информации о команде."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    # Проверка, что пользователь является членом или владельцем команды
    if user.team_id != team.id and team.owner_id != user.id:
         raise HTTPException(status_code=403, detail="Not enough permissions")
    return team


@router.post("/{team_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def add_team_member(
    team_id: int,
    user_id: int,
    db: Session = Depends(get_async_session),
    current_user: User = Depends(current_active_user)
):
    """Добавление пользователя в команду (только для владельца)."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team or team.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed or team not found")
    
    member_to_add = db.query(User).filter(User.id == user_id).first()
    if not member_to_add:
        raise HTTPException(status_code=404, detail="User to add not found")

    member_to_add.team_id = team_id
    db.commit()
