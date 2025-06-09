# app/routers/calendar.py

from datetime import datetime, date, time
import calendar as pycal
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_async_session
from app.core.auth import current_active_user
from app.models.user import User
from app.models.task import Task
from app.models.meeting import Meeting

router = APIRouter(prefix="/calendar", tags=["Календарь"])


# ------------------------
# Вспомогательные функции
# ------------------------

async def get_tasks_for_date(
    db: AsyncSession, team_id: int, target: date
) -> List[Task]:
    stmt = (
        select(Task)
        .where(Task.deadline != None)
        .where(func.date(Task.deadline) == target)
    )
    # Если у вас нет team_id прямо в Task, фильтруйте по assignee.team_id или creator.team_id
    stmt = stmt.where(
        (Task.assignee.has(team_id=team_id)) |
        (Task.creator.has(team_id=team_id))
    )
    res = await db.execute(stmt)
    return res.scalars().all()


async def get_meetings_for_date(
    db: AsyncSession, user_id: int, target: date
) -> List[Meeting]:
    stmt = (
        select(Meeting)
        .options(selectinload(Meeting.participants))
        .where(func.date(Meeting.start_time) == target)
        .join(Meeting.participants)
        .where(Meeting.participants.any(id=user_id))
    )
    res = await db.execute(stmt)
    return res.scalars().all()


# ------------------------
# Эндпоинты
# ------------------------

@router.get(
    "/daily/{target_date}",
    response_class=PlainTextResponse,
    description="Дневной вид: текстовая таблица задач и встреч на указанную дату YYYY-MM-DD"
)
async def daily_calendar(
    target_date: str,
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    try:
        d = datetime.fromisoformat(target_date).date()
    except ValueError:
        raise HTTPException(400, "Неверный формат даты, ожидается YYYY-MM-DD")

    if not current_user.team_id:
        return "Вы не состоите в команде."

    tasks = await get_tasks_for_date(db, current_user.team_id, d)
    meetings = await get_meetings_for_date(db, current_user.id, d)

    # Формируем строки таблицы
    lines = ["Время      | Тип     | Заголовок"]
    lines.append("-" * 40)
    for t in sorted(tasks, key=lambda x: x.deadline or datetime.min):
        tm = t.deadline.time().strftime("%H:%M") if t.deadline else "--:--"
        lines.append(f"{tm:<10}| Задача  | {t.title}")
    for m in sorted(meetings, key=lambda x: x.start_time):
        tm = m.start_time.time().strftime("%H:%M")
        lines.append(f"{tm:<10}| Встреча| {m.title}")
    if len(lines) == 2:
        lines.append("Событий нет.")
    return "\n".join(lines)


@router.get(
    "/monthly/{year}/{month}",
    response_class=PlainTextResponse,
    description="Месячный вид: текстовая таблица с количеством задач и встреч на каждый день"
)
async def monthly_calendar(
    year: int,
    month: int,
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    if not 1 <= month <= 12:
        raise HTTPException(400, "Месяц должен быть от 1 до 12")

    if not current_user.team_id:
        return "Вы не состоите в команде."

    # Подготовим шапку таблицы
    _, days_in_month = pycal.monthrange(year, month)
    header = "Дата       | Задач | Встреч"
    lines = [header, "-" * len(header)]

    # Для каждого дня считаем задачи и встречи
    for day in range(1, days_in_month + 1):
        d = date(year, month, day)
        tasks = await get_tasks_for_date(db, current_user.team_id, d)
        meetings = await get_meetings_for_date(db, current_user.id, d)
        lines.append(f"{d.isoformat():<10}| {len(tasks):^5} | {len(meetings):^6}")

    return "\n".join(lines)
