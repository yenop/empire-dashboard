"""Création de tâches pour intégrations machine (OpenClaw, scripts) via `X-Empire-Internal-Key`."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_internal_api_key
from app.schemas import TaskCreate, TaskOut
from app.services import task_ops

router = APIRouter(prefix="/api/internal/tasks", tags=["internal"])


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def internal_create_task(
    body: TaskCreate,
    _auth: None = Depends(require_internal_api_key),
    db: Session = Depends(get_db),
) -> TaskOut:
    t = task_ops.create_task_from_body(db, body)
    return task_ops.task_to_out(t)
