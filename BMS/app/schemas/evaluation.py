from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


# --- Оценки ---
class EvaluationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    score: int
    evaluator_id: int
    created_at: datetime

class EvaluationCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    score: int = Field(..., ge=1, le=5, description="Оценка от 1 до 5")