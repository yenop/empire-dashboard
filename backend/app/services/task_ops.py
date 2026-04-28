"""Création / mise à jour / suppression de tâches + compteurs agents + notification Wire."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import (
    AgentModel,
    AppModel,
    IntelModel,
    IntelStatus,
    TaskModel,
    TaskPriority,
    TaskStatus,
    WireMessageModel,
)
from app.schemas import TaskCreate, TaskOut, TaskUpdate
from app.services import openclaw_cron as oc
from app.services.openclaw_wire_db import get_or_create_openclaw_conversation


def task_to_out(t: TaskModel) -> TaskOut:
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


def normalize_task_ids(agent_id: str | None, app_id: str | None) -> tuple[str | None, str | None]:
    a = (agent_id or "").strip() or None
    p = (app_id or "").strip() or None
    return a, p


def validate_task_fks(db: Session, agent_id: str | None, app_id: str | None) -> None:
    if agent_id is not None:
        if not db.get(AgentModel, agent_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Agent not found")
    if app_id is not None:
        if not db.get(AppModel, app_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="App not found")


def recount_agent_tasks(db: Session, agent_id: str | None) -> None:
    if not agent_id:
        return
    n = (
        db.scalar(
            select(func.count()).select_from(TaskModel).where(TaskModel.agent_id == agent_id)
        )
        or 0
    )
    row = db.get(AgentModel, agent_id)
    if row:
        row.tasks_count = int(n)


def load_task_with_relations(db: Session, task_id: int) -> TaskModel:
    return db.scalars(
        select(TaskModel)
        .where(TaskModel.id == task_id)
        .options(joinedload(TaskModel.agent), joinedload(TaskModel.app))
    ).unique().one()


def append_wire_task_notification(
    db: Session, *, dashboard_agent_id: str, task_id: int, task_title: str
) -> None:
    jid = oc.first_openclaw_job_id_for_dashboard_agent(dashboard_agent_id)
    if not jid:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Aucun job OpenClaw mappé pour cet agent",
        )
    root = oc.oc_root()
    if not root.exists() or not root.is_dir():
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Volume OpenClaw non monté",
        )
    conv = get_or_create_openclaw_conversation(db, jid)
    body = f"[Tâche #{task_id}] {task_title.strip()}"
    db.add(
        WireMessageModel(
            conversation_id=conv.id,
            from_agent_id="dashboard",
            to_agent_id=dashboard_agent_id,
            body=body,
        )
    )


def create_task_from_body(db: Session, body: TaskCreate) -> TaskModel:
    ag, ap = normalize_task_ids(body.agent_id, body.app_id)
    validate_task_fks(db, ag, ap)
    try:
        st = TaskStatus(body.status)
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid status") from e
    pr = TaskPriority.medium
    if body.priority:
        try:
            pr = TaskPriority(body.priority)
        except ValueError:
            pr = TaskPriority.medium
    t = TaskModel(
        title=body.title.strip(),
        agent_id=ag,
        app_id=ap,
        status=st,
        priority=pr,
    )
    db.add(t)
    db.flush()
    if body.notify_wire:
        if not ag:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="notify_wire requires agent_id",
            )
        append_wire_task_notification(
            db, dashboard_agent_id=ag, task_id=t.id, task_title=t.title
        )
    recount_agent_tasks(db, ag)
    db.commit()
    return load_task_with_relations(db, t.id)


def apply_task_update(db: Session, t: TaskModel, body: TaskUpdate) -> TaskModel:
    patch = body.model_dump(exclude_unset=True)
    old_agent = t.agent_id
    if "title" in patch and patch["title"] is not None:
        t.title = str(patch["title"]).strip()
    if "status" in patch:
        try:
            t.status = TaskStatus(patch["status"])
        except ValueError as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid status") from e
    if "priority" in patch:
        try:
            t.priority = TaskPriority(patch["priority"])
        except ValueError as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid priority") from e
    if "agent_id" in patch:
        ag, _ = normalize_task_ids(patch.get("agent_id"), None)
        validate_task_fks(db, ag, t.app_id)
        t.agent_id = ag
    if "app_id" in patch:
        _, ap = normalize_task_ids(None, patch.get("app_id"))
        validate_task_fks(db, t.agent_id, ap)
        t.app_id = ap
    recount_agent_tasks(db, old_agent)
    recount_agent_tasks(db, t.agent_id)

    if "status" in patch and t.intel_item_id:
        intel = db.get(IntelModel, t.intel_item_id)
        if intel:
            if t.status == TaskStatus.inprogress:
                intel.status = IntelStatus.implementing
            elif t.status == TaskStatus.done:
                intel.status = IntelStatus.implemented
                intel.implemented_at = datetime.now(timezone.utc)

    db.commit()
    return load_task_with_relations(db, t.id)


def delete_task_by_id(db: Session, task_id: int) -> None:
    t = db.get(TaskModel, task_id)
    if not t:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Task not found")
    aid = t.agent_id
    db.delete(t)
    db.commit()
    recount_agent_tasks(db, aid)
