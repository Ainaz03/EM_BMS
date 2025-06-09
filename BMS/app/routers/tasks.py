from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List

from app.models.task import Comment, Task, TaskStatus
from app.models.team import Team
from app.schemas.comment import CommentCreate, CommentRead
from app.core.database import get_async_session
from app.core.auth import current_active_user
from app.models.user import User, UserRole
from app.models.evaluation import Evaluation
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.schemas.evaluation import EvaluationCreate, EvaluationRead


router = APIRouter(prefix="/tasks", tags=["Tasks"])


# -------------------------
# Вспомогательные функции
# -------------------------

async def get_team_or_404(team_id: int, db: AsyncSession):
    res = await db.execute(select(Team).where(Team.id == team_id))
    team = res.scalars().first()
    if not team:
        raise HTTPException(status_code=404, detail="Команда не найдена")
    return team

async def get_task_or_404(task_id: int, db: AsyncSession):
    res = await db.execute(
        select(Task)
        .options(
            selectinload(Task.comments),
            selectinload(Task.evaluations)
        )
        .where(Task.id == task_id)
    )
    task = res.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


# -------------------------
# Эндпоинты по задачам
# -------------------------

@router.get(
    "/",
    response_model=List[TaskRead],
    description="Список задач вашей команды (всех участников)."
)
async def list_tasks(
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    if not current_user.team_id:
        return []

    # Если глобальный админ, отдать все
    stmt = select(Task).options(
        selectinload(Task.comments),
        selectinload(Task.evaluations)
    )
    # иначе — только задачи своей команды
    if current_user.role != UserRole.ADMIN:
        # связываем через assignee или creator, у вас может быть team_id у Task
        stmt = stmt.where(
            (Task.assignee.has(team_id=current_user.team_id)) |
            (Task.creator.has(team_id=current_user.team_id))
        )
    res = await db.execute(stmt)
    tasks = res.scalars().all()
    return tasks


@router.post(
    "/",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    description="Создание новой задачи. Доступно менеджерам и администраторам команды."
)
async def create_task(
    task_in: TaskCreate,
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    # Проверка роли
    if current_user.role not in (UserRole.ADMIN, UserRole.MANAGER):
        raise HTTPException(403, detail="Недостаточно прав для создания задачи")
    if not current_user.team_id:
        raise HTTPException(400, detail="Вы не состоите ни в одной команде")

    # Проверяем, что исполнитель из вашей команды
    res_u = await db.execute(select(User).where(User.id == task_in.assignee_id))
    assignee = res_u.scalars().first()
    if not assignee or assignee.team_id != current_user.team_id:
        raise HTTPException(404, detail="Исполнитель не найден в вашей команде")

    task = Task(
        title=task_in.title,
        description=task_in.description,
        deadline=task_in.deadline,
        creator_id=current_user.id,
        assignee_id=task_in.assignee_id
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.put(
    "/{task_id}",
    response_model=TaskRead,
    description="Обновление задачи. Доступно создателю, менеджеру и администратору команды."
)
async def update_task(
    task_id: int,
    task_in: TaskUpdate,
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    task = await get_task_or_404(task_id, db)

    # Проверка прав
    allowed = (
        current_user.role == UserRole.ADMIN or
        (current_user.role == UserRole.MANAGER and task.creator.team_id == current_user.team_id) or
        task.creator_id == current_user.id
    )
    if not allowed:
        raise HTTPException(403, detail="Нет прав на изменение этой задачи")

    # Применяем обновления
    data = task_in.model_dump(exclude_none=True)
    await db.execute(update(Task).where(Task.id == task_id).values(**data))
    await db.commit()

    return await get_task_or_404(task_id, db)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Удаление задачи. Доступно создателю и администратору команды."
)
async def delete_task(
    task_id: int,
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    task = await get_task_or_404(task_id, db)

    # Только создатель или глобальный админ может удалять
    if not (
        current_user.role == UserRole.ADMIN or
        task.creator_id == current_user.id
    ):
        raise HTTPException(403, detail="Нет прав на удаление этой задачи")

    await db.execute(delete(Task).where(Task.id == task_id))
    await db.commit()


# -------------------------
# Эндпоинты по комментариям
# -------------------------

@router.post(
    "/{task_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
    description="Добавление комментария к задаче."
)
async def add_comment(
    task_id: int,
    comment_in: CommentCreate,
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    task = await get_task_or_404(task_id, db)
    # Любой участник команды может комментировать
    if current_user.role != UserRole.ADMIN and current_user.team_id not in (task.creator.team_id, task.assignee.team_id):
        raise HTTPException(403, detail="Нет доступа к комментированию этой задачи")

    comment = Comment(text=comment_in.text, author_id=current_user.id, task_id=task_id)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment

@router.get(
    "/{task_id}/comments",
    response_model=List[CommentRead],
    description="Список комментариев задачи."
)
async def list_comments(
    task_id: int,
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    task = await get_task_or_404(task_id, db)
    return task.comments


# -------------------------
# Эндпоинты по оценкам
# -------------------------

@router.post(
    "/{task_id}/evaluations",
    response_model=EvaluationRead,
    status_code=status.HTTP_201_CREATED,
    description="Оценка выполненной задачи (1–5). Доступно менеджерам и администраторам после статуса DONE."
)
async def add_evaluation(
    task_id: int,
    eval_in: EvaluationCreate,
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    task = await get_task_or_404(task_id, db)

    if task.status != TaskStatus.DONE:
        raise HTTPException(400, detail="Задача ещё не выполнена")

    if current_user.role not in (UserRole.ADMIN, UserRole.MANAGER):
        raise HTTPException(403, detail="Только менеджер или администратор может выставлять оценки")

    # Проверяем, что оценка ещё не выставлена
    existing = await db.execute(select(Evaluation).where(Evaluation.task_id == task_id))
    if existing.scalars().first():
        raise HTTPException(400, detail="Оценка для этой задачи уже выставлена")

    eval_obj = Evaluation(
        score=eval_in.score,
        evaluator_id=current_user.id,
        task_id=task_id
    )
    db.add(eval_obj)
    await db.commit()
    await db.refresh(eval_obj)
    return eval_obj

@router.get(
    "/{task_id}/evaluations",
    response_model=List[EvaluationRead],
    description="Получить оценки по задаче."
)
async def list_evaluations(
    task_id: int,
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    task = await get_task_or_404(task_id, db)
    return task.evaluations