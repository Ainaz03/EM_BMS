from typing import List
from pydantic import BaseModel, ConfigDict

from app.schemas.meeting import MeetingRead
from app.schemas.task import TaskRead


# Схема для ответа от календаря
class CalendarView(BaseModel):
    tasks: List[TaskRead]
    meetings: List[MeetingRead]