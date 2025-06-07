# src/api/endpoints/meetings.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List

from app.core.database import get_async_session
from app.core.auth import current_active_user
from app.models.user import User
from app.models.meeting import Meeting
from app.schemas.meeting import MeetingRead, MeetingCreate


router = APIRouter(prefix="/meetings", tags=["Meetings"])


@router.post("/", response_model=MeetingRead, status_code=status.HTTP_201_CREATED)
def create_meeting(
    meeting_in: MeetingCreate,
    db: Session = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    """Создание встречи и добавление участников."""
    if not user.team_id:
        raise HTTPException(status_code=400, detail="User is not part of any team")

    # Проверка наложения времени (упрощенная)
    overlapping_meeting = db.query(Meeting).filter(
        Meeting.team_id == user.team_id,
        or_(
            Meeting.start_time.between(meeting_in.start_time, meeting_in.end_time),
            Meeting.end_time.between(meeting_in.start_time, meeting_in.end_time)
        )
    ).first()

    if overlapping_meeting:
        raise HTTPException(status_code=409, detail="Meeting time overlaps with an existing meeting")

    participants = db.query(User).filter(
        User.id.in_(meeting_in.participant_ids),
        User.team_id == user.team_id
    ).all()
    
    if len(participants) != len(meeting_in.participant_ids):
        raise HTTPException(status_code=400, detail="One or more participants not found in the team")

    new_meeting = Meeting(
        title=meeting_in.title,
        start_time=meeting_in.start_time,
        end_time=meeting_in.end_time,
        team_id=user.team_id,
        participants=participants
    )
    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)
    return new_meeting


@router.get("/", response_model=List[MeetingRead])
def get_user_meetings(
    db: Session = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    """Получение всех встреч, в которых участвует пользователь."""
    return user.meetings

@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_meeting(
    meeting_id: int,
    db: Session = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    """Отмена встречи."""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    # Предположим, что отменить может только участник или создатель в той же команде
    if meeting.team_id != user.team_id:
         raise HTTPException(status_code=403, detail="Not enough permissions")

    db.delete(meeting)
    db.commit()
    