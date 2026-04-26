from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_current_username
from app.models import AgentModel, AppModel, TaskModel, TaskPriority, TaskStatus
from app.schemas import TaskCreate, TaskOut, TaskUpdate

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def _task_to_out(t: TaskModel) -> TaskOut:
    ag = t.agent
    ap = t.app
    st = t.status
    pr = t.priority
    return TaskOut(
        id=t.id,
        title=t.title,
        agent_id=t.agent_id,
        app_id=t.app_id,
        status=st.value if hasattr(st, "value") else str(st),
        priority=pr.value if hasattr(pr, "value") else str(pr),
        agent_emoji=ag.emoji if ag else None,
        agent_name=ag.name if ag else None,
        app_name=ap.name if ap else None,
        app_color=ap.color if ap else None,
    )


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
    return [_task_to_out(t) for t in rows]


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    body: TaskCreate,
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> TaskOut:
    try:
        st = TaskStatus(body.status)
    except ValueError:
        raise HTTPException(400, detail="Invalid status") from None
    pr = TaskPriority.medium
    if body.priority:
        try:
            pr = TaskPriority(body.priority)
        except ValueError:
            pr = TaskPriority.medium
    t = TaskModel(
        title=body.title,
        agent_id=body.agent_id,
        app_id=body.app_id,
        status=st,
        priority=pr,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    t = (
        db.scalars(
            select(TaskModel)
            .where(TaskModel.id == t.id)
            .options(joinedload(TaskModel.agent), joinedload(TaskModel.app))
        )
        .unique()
        .one()
    )
    return _task_to_out(t)


@router.put("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    body: TaskUpdate,
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> TaskOut:
    t = db.get(TaskModel, task_id)
    if not t:
        raise HTTPException(404, detail="Task not found")
    patch = body.model_dump(exclude_unset=True)
    if "title" in patch:
        t.title = patch["title"]
    if "status" in patch:
        try:
            t.status = TaskStatus(patch["status"])
        except ValueError:
            raise HTTPException(400, detail="Invalid status") from None
    if "priority" in patch:
        try:
            t.priority = TaskPriority(patch["priority"])
        except ValueError:
            raise HTTPException(400, detail="Invalid priority") from None
    if "agent_id" in patch:
        t.agent_id = patch["agent_id"]
    if "app_id" in patch:
        t.app_id = patch["app_id"]
    db.commit()
    db.refresh(t)
    t = (
        db.scalars(
            select(TaskModel)
            .where(TaskModel.id == t.id)
            .options(joinedload(TaskModel.agent), joinedload(TaskModel.app))
        )
        .unique()
        .one()
    )
    return _task_to_out(t)
