# src/api/endpoints/calendar.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import cast, Date, and_
from typing import Optional
from datetime import date, datetime, timedelta
import calendar

from app.core.database import get_async_session
from app.core.auth import current_active_user
from BMS.app.models.user import User
from BMS.app.models.meeting import Meeting
from BMS.app.models.task import Task
from BMS.app.schemas.calendar import CalendarView


router = APIRouter(prefix="/calendar", tags=["Calendar"])

@router.get("/day", response_model=CalendarView)
def get_daily_view(
    date_str: Optional[str] = None, # Формат YYYY-MM-DD
    db: Session = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    """
    Получение списка задач и встреч на конкретный день.
    Если дата не указана, используется сегодняшний день.
    """
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD."
        )

    # Задачи, назначенные пользователю, с дедлайном в этот день
    tasks = db.query(Task).filter(
        Task.assignee_id == user.id,
        cast(Task.deadline, Date) == target_date
    ).all()
    
    # Встречи, в которых пользователь участвует и которые проходят в этот день
    # (встреча может длиться несколько дней)
    meetings = db.query(Meeting).join(Meeting.participants).filter(
        User.id == user.id,
        cast(Meeting.start_time, Date) <= target_date,
        cast(Meeting.end_time, Date) >= target_date
    ).all()
    
    return CalendarView(tasks=tasks, meetings=meetings)


@router.get("/month", response_model=CalendarView)
def get_monthly_view(
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    """
    Получение списка задач и встреч на конкретный месяц.
    Если год или месяц не указаны, используются текущие.
    """
    today = date.today()
    target_year = year or today.year
    target_month = month or today.month

    if not 1 <= target_month <= 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid month. Must be between 1 and 12."
        )

    # Определяем первый и последний день месяца
    _, num_days = calendar.monthrange(target_year, target_month)
    start_date = date(target_year, target_month, 1)
    end_date = date(target_year, target_month, num_days)

    # Конвертируем в datetime для корректного сравнения
    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())
    
    # Задачи, назначенные пользователю, с дедлайном в этом месяце
    tasks = db.query(Task).filter(
        Task.assignee_id == user.id,
        Task.deadline.between(start_dt, end_dt)
    ).all()

    # Встречи, которые пересекаются с этим месяцем
    meetings = db.query(Meeting).join(Meeting.participants).filter(
        User.id == user.id,
        # Проверка на пересечение временных интервалов
        Meeting.start_time <= end_dt,
        Meeting.end_time >= start_dt
    ).all()
    
    return CalendarView(tasks=tasks, meetings=meetings)
