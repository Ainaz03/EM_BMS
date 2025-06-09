from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, ConfigDict, Field

from app.core.database import get_async_session
from app.models.team import Team
from app.models.user import User, UserRole
from app.core.auth import current_active_user
from app.utils.codegen import generate_unique_invite_code
from app.schemas.team import TeamMemberRoleUpdate, TeamRead, TeamCreate, TeamMemberAdd

router = APIRouter(prefix="/teams", tags=["Команды"])

@router.post(
    "/",
    response_model=TeamRead,
    status_code=status.HTTP_201_CREATED,
    description="Создание новой команды. Текущий пользователь становится её администратором."
)
async def create_team(
    team_in: TeamCreate,
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Только администратор системы или менеджер может создавать команду")

    code = await generate_unique_invite_code(db)

    team = Team(
        name=team_in.name,
        invite_code=code,
        admin_id=current_user.id
    )
    db.add(team)
    await db.commit()
    await db.refresh(team)

    return TeamRead(
        id=team.id,
        name=team.name,
        invite_code=team.invite_code,
        admin_id=team.admin_id,
        members=[]
    )


@router.get(
    "/{team_id}",
    response_model=TeamRead,
    description="Просмотр информации о команде по её ID. " \
    "Доступно глобальным администраторам."
)
async def read_team(
    team_id: int,
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    if current_user.role != UserRole.ADMIN and team.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к информации этой команды")

    res = await db.execute(select(Team).options(selectinload(Team.members)).where(Team.id == team_id))
    team = res.scalars().first()
    if not team:
        raise HTTPException(status_code=404, detail="Команда не найдена")

    return TeamRead(
        id=team.id,
        name=team.name,
        invite_code=team.invite_code,
        admin_id=team.admin_id,
        members=[u.id for u in team.members]
    )


@router.post(
    "/{team_id}/members",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Добавление участника в команду по его user_id. " \
    "Доступно только администратору команды или глобальному администратору."
)
async def add_member(
    team_id: int,
    member_in: TeamMemberAdd,
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    if current_user.role != UserRole.ADMIN and team.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только администратор команды или системы может добавлять участников")
    
    res = await db.execute(select(Team).options(selectinload(Team.members)).where(Team.id == team_id))
    team = res.scalars().first()
    if not team:
        raise HTTPException(status_code=404, detail="Команда не найдена")

    res_u = await db.execute(select(User).where(User.id == member_in.user_id))
    user = res_u.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    team.members.append(user)
    await db.commit()


@router.delete(
    "/{team_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Удаление участника из команды по его user_id. " \
    "Доступно только администратору команды или глобальному администратору."
)
async def remove_member(
    team_id: int,
    user_id: int,
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    if current_user.role != UserRole.ADMIN and team.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только администратор команды или системы может удалять участников")

    res = await db.execute(select(Team).options(selectinload(Team.members)).where(Team.id == team_id))
    team = res.scalars().first()
    if not team:
        raise HTTPException(status_code=404, detail="Команда не найдена")

    res_u = await db.execute(select(User).where(User.id == user_id))
    user = res_u.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user in team.members:
        team.members.remove(user)
        await db.commit()


@router.patch(
    "/{team_id}/members/{user_id}/role",
    status_code=status.HTTP_204_NO_CONTENT,
    description=(
        "Изменение роли участника команды. "
        "Доступно только администратору команды или глобальному администратору."
    )
)
async def update_member_role(
    team_id: int,
    user_id: int,
    role_in: TeamMemberRoleUpdate,
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    # --- 1. Проверка доступа: админ системы или админ команды ---
    # Загружаем команду
    res = await db.execute(
        select(Team).where(Team.id == team_id)
    )
    team = res.scalars().first()
    if not team:
        raise HTTPException(status_code=404, detail="Команда не найдена")

    if not (current_user.role == UserRole.ADMIN or team.admin_id == current_user.id):
        raise HTTPException(status_code=403, detail="Только администратор команды или системы может менять роли")

    # --- 2. Проверяем, что пользователь состоит в команде ---
    res_u = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = res_u.scalars().first()
    if not user or user.team_id != team_id:
        raise HTTPException(status_code=404, detail="Участник не найден или не состоит в этой команде")

    # --- 3. Не даём понижать роль администратора команды ---
    if user.id == team.admin_id:
        raise HTTPException(status_code=400, detail="Нельзя менять роль администратора команды")

    # --- 4. Обновляем роль ---
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(role=role_in.role)
    )
    await db.commit()