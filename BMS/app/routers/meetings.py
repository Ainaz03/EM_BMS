# src/api/endpoints/meetings.py
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, delete, select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_async_session
from app.core.auth import current_active_user
from app.models.user import User, UserRole, meeting_participants_association
from app.models.meeting import Meeting
from app.schemas.meeting import MeetingRead, MeetingCreate, MeetingUpdate


router = APIRouter(prefix="/meetings", tags=["Meetings"])


# --------------------------
# Вспомогательные функции
# --------------------------

async def get_meeting_or_404(meeting_id: int, db: AsyncSession) -> Meeting:
    res = await db.execute(
        select(Meeting)
        .options(selectinload(Meeting.participants))
        .where(Meeting.id == meeting_id)
    )
    meeting = res.scalars().first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Встреча не найдена")
    return meeting

async def check_time_conflicts(
    user_ids: List[int],
    start: datetime,
    end: datetime,
    db: AsyncSession,
    exclude_meeting_id: int | None = None
):
    """
    Проверяет, что у каждого пользователя из списка нет пересечения по времени с другими встречами.
    """
    for uid in user_ids:
        stmt = (
            select(Meeting)
            .join(meeting_participants_association)
            .where(meeting_participants_association.c.user_id == uid)
            .where(
                and_(
                    Meeting.start_time < end,
                    Meeting.end_time > start
                )
            )
        )
        if exclude_meeting_id:
            stmt = stmt.where(Meeting.id != exclude_meeting_id)

        res = await db.execute(stmt)
        if res.scalars().first():
            raise HTTPException(
                status_code=400,
                detail=f"Пользователь {uid} уже занят в это время"
            )


# --------------------------
# Эндпоинты
# --------------------------

@router.get(
    "/",
    response_model=List[MeetingRead],
    description="Список встреч текущего пользователя."
)
async def list_meetings(
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    res = await db.execute(
        select(Meeting)
        .options(selectinload(Meeting.participants))
        .join(meeting_participants_association)
        .where(meeting_participants_association.c.user_id == current_user.id)
    )
    meetings = res.scalars().all()
    return meetings


@router.post(
    "/",
    response_model=MeetingRead,
    status_code=status.HTTP_201_CREATED,
    description="Создание новой встречи. Проверяет, чтобы не было пересечений у участников."
)
async def create_meeting(
    meeting_in: MeetingCreate,
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    # Включаем создателя в participants, если не указан
    participants = set(meeting_in.participants)
    participants.add(current_user.id)

    # Проверка временных пересечений
    await check_time_conflicts(
        list(participants),
        meeting_in.start_time,
        meeting_in.end_time,
        db
    )

    # Проверяем, что все участники существуют
    res = await db.execute(select(User).where(User.id.in_(participants)))
    users = res.scalars().all()
    if len(users) != len(participants):
        raise HTTPException(status_code=404, detail="Один или несколько участников не найдены")

    meeting = Meeting(
        title=meeting_in.title,
        start_time=meeting_in.start_time,
        end_time=meeting_in.end_time,
        creator_id=current_user.id,
        participants=users
    )

    db.add(meeting)
    await db.commit()
    await db.refresh(meeting)
    return meeting


@router.put(
    "/{meeting_id}",
    response_model=MeetingRead,
    description="Обновление встречи (только создатель). Проверка пересечений."
)
async def update_meeting(
    meeting_id: int,
    meeting_in: MeetingUpdate,
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    meeting = await get_meeting_or_404(meeting_id, db)

    if meeting.creator_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Только создатель или админ может изменять встречу")

    data = meeting_in.model_dump(exclude_none=True)
    new_start = data.get("start_time", meeting.start_time)
    new_end = data.get("end_time", meeting.end_time)
    new_participants = data.get("participants", [u.id for u in meeting.participants])
    new_participants = set(new_participants)
    new_participants.add(meeting.creator_id)

    # Проверка пересечений (исключаем саму себя)
    await check_time_conflicts(
        list(new_participants),
        new_start,
        new_end,
        db,
        exclude_meeting_id=meeting_id
    )

    # Обновляем поля
    # 1) обновляем основные колонки
    await db.execute(
        update(Meeting)
        .where(Meeting.id == meeting_id)
        .values(
            title=data.get("title", meeting.title),
            start_time=new_start,
            end_time=new_end
        )
    )
    # 2) обновляем участников через association table
    # проще всего: удалить старые связи и добавить новые
    await db.execute(
        delete(meeting_participants_association)
        .where(meeting_participants_association.c.meeting_id == meeting_id)
    )
    # вставляем новые
    for uid in new_participants:
        await db.execute(
            meeting_participants_association.insert().values(
                meeting_id=meeting_id,
                user_id=uid
            )
        )

    await db.commit()
    return await get_meeting_or_404(meeting_id, db)


@router.delete(
    "/{meeting_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Удаление встречи (только создатель или админ)."
)
async def delete_meeting(
    meeting_id: int,
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    meeting = await get_meeting_or_404(meeting_id, db)

    if meeting.creator_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Только создатель или админ может удалять встречу")

    await db.execute(delete(Meeting).where(Meeting.id == meeting_id))
    await db.commit()