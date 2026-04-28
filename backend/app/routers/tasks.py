from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_current_username
from app.models import TaskModel
from app.schemas import TaskCreate, TaskOut, TaskUpdate
from app.services import task_ops

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskOut])
def list_tasks(
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> list[TaskOut]:
    q = (
        select(TaskModel)
        .options(joinedload(TaskModel.agent), joinedload(TaskModel.app))
        .order_by(TaskModel.id.desc())
    )
    rows = db.scalars(q).unique().all()
    return [task_ops.task_to_out(t) for t in rows]


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    body: TaskCreate,
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> TaskOut:
    t = task_ops.create_task_from_body(db, body)
    return task_ops.task_to_out(t)


@router.put("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    body: TaskUpdate,
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> TaskOut:
    t = db.get(TaskModel, task_id)
    if not t:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Task not found")
    t = task_ops.apply_task_update(db, t, body)
    return task_ops.task_to_out(t)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> None:
    task_ops.delete_task_by_id(db, task_id)
