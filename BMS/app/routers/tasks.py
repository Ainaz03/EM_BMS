from asyncio import Task
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_session
from app.core.auth import current_active_user
from app.models.user import User
from app.models.evaluation import Evaluation
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.schemas.evaluation import EvaluationCreate, EvaluationRead


router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_session),
    user: User = Depends(current_active_user)
):
    """Создание новой задачи в команде пользователя."""
    if not user.team_id:
        raise HTTPException(status_code=400, detail="User is not part of any team")
        
    task_data = task_in.dict()
    new_task = Task(
        **task_data,
        creator_id=user.id,
        team_id=user.team_id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@router.get("/", response_model=List[TaskRead])
def get_team_tasks(
    db: Session = Depends(get_session),
    user: User = Depends(current_active_user)
):
    """Получение всех задач команды, в которой состоит пользователь."""
    if not user.team_id:
        return []
    tasks = db.query(Task).filter(Task.team_id == user.team_id).all()
    return tasks


@router.put("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_session),
    user: User = Depends(current_active_user)
):
    """Обновление задачи."""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if db_task.team_id != user.team_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task


@router.post("/evaluations/", response_model=EvaluationRead, status_code=status.HTTP_201_CREATED)
def create_evaluation(
    eval_in: EvaluationCreate,
    db: Session = Depends(get_session),
    user: User = Depends(current_active_user) # Предполагается, что оценивает менеджер
):
    """Создание оценки для выполненной задачи."""
    task = db.query(Task).filter(Task.id == eval_in.task_id).first()
    if not task or task.team_id != user.team_id:
        raise HTTPException(status_code=404, detail="Task not found or not in your team")
    if task.status != "done":
        raise HTTPException(status_code=400, detail="Can only evaluate 'done' tasks")
    
    evaluation = Evaluation(
        score=eval_in.score,
        comment=eval_in.comment,
        task_id=eval_in.task_id,
        user_id=task.assignee_id # Оценка ставится исполнителю задачи
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    return evaluation
