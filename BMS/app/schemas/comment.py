from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


# --- Комментарии ---
class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    text: str
    author_id: int
    created_at: datetime

class CommentCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    text: str = Field(..., description="Текст комментария")