from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.auth import current_active_user
from app.models.team import Team
from app.models.user import User
from app.schemas.team import TeamRead, TeamCreate, TeamMemberAdd

router = APIRouter(prefix="/teams", tags=["Teams"])

@router.post("/", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_in: TeamCreate,
    db: AsyncSession = Depends(get_async_session),
    user=Depends(current_active_user),
):
    """Создание новой команды. Текущий пользователь становится её владельцем."""
    stmt = Team.__table__.insert().values(
        **team_in.model_dump(),
        owner_id=user.id
    ).returning(Team)
    result = await db.execute(stmt)
    team = result.scalar_one()
    await db.commit()
    return team

@router.get("/{team_id}", response_model=TeamRead)
async def get_team(
    team_id: int,
    db: AsyncSession = Depends(get_async_session),
    user=Depends(current_active_user),
):
    """Получение информации о команде."""
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(404, "Team not found")
    if team.owner_id != user.id and user.team_id != team.id:
        raise HTTPException(403, "Not enough permissions")
    return team

@router.post("/{team_id}/members", status_code=status.HTTP_204_NO_CONTENT)
async def add_team_member(
    team_id: int,
    payload: TeamMemberAdd,
    db: AsyncSession = Depends(get_async_session),
    current_user=Depends(current_active_user),
):
    """Добавление пользователя в команду (только для владельца)."""
    # Проверяем команду и права
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team or team.owner_id != current_user.id:
        raise HTTPException(403, "Not allowed or team not found")

    # Проверяем пользователя
    result = await db.execute(select(User).where(User.id == payload.user_id))
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(404, "User to add not found")

    # Обновляем поле team_id
    stmt = (
        update(User)
        .where(User.id == payload.user_id)
        .values(team_id=team_id)
    )
    await db.execute(stmt)
    await db.commit()
    # Нет тела ответа
    return
