from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_username
from app.models import (
    ApiKeyRequestModel,
    ApiKeyRequestStatus,
    ContentPipelineModel,
    IntelModel,
    IntelStatus,
    NicheCandidateModel,
    SeoRankModel,
    TaskModel,
    TaskPriority,
    TaskStatus,
)
from app.services.task_ops import recount_agent_tasks
from app.services.wire_outbound import append_nerve_note

router = APIRouter(prefix="/api/ops", tags=["ops"])


WORKFLOW_CRONS: list[dict[str, str]] = [
    {"id": "p1_marlene", "label": "Recherche niches (Marlène)", "schedule": "0 */2 * * *", "phase": "1"},
    {"id": "p1_gaston", "label": "Analyse SEO niches (Gaston)", "schedule": "0 1-23/2 * * *", "phase": "1"},
    {"id": "intel_x", "label": "Veille X e-com (Marcel)", "schedule": "0 20 * * *", "phase": "quotidien"},
    {"id": "intel_yt", "label": "Veille YouTube (Marcel)", "schedule": "0 21 * * *", "phase": "quotidien"},
    {"id": "intel_edith", "label": "Synthèse intel (Édith)", "schedule": "0 22 * * *", "phase": "quotidien"},
    {"id": "intel_pod", "label": "Veille POD X (Édith)", "schedule": "0 23 * * *", "phase": "quotidien"},
    {"id": "yvon_night", "label": "Proactivité nocturne (Yvon)", "schedule": "0 1-7 * * *", "phase": "01h–08h"},
    {"id": "qa_simon", "label": "Revue QA post-rédaction (Simone)", "schedule": "0 * * * *", "phase": "production"},
]


@router.get("/crons")
def list_crons(_username: str = Depends(get_current_username)) -> list[dict[str, str]]:
    return WORKFLOW_CRONS


@router.get("/niches")
def list_niches(
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> list[dict]:
    rows = db.scalars(
        select(NicheCandidateModel).order_by(NicheCandidateModel.id.desc()).limit(40)
    ).all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "summary": r.summary,
            "score_seo": r.score_seo,
            "status": r.status.value if hasattr(r.status, "value") else str(r.status),
            "source_agents": r.source_agents,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@router.get("/content-pipeline")
def list_content(
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> list[dict]:
    rows = db.scalars(
        select(ContentPipelineModel).order_by(ContentPipelineModel.updated_at.desc()).limit(40)
    ).all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "agent_id": r.agent_id,
            "app_id": r.app_id,
            "stage": r.stage.value if hasattr(r.stage, "value") else str(r.stage),
            "excerpt": r.excerpt,
            "updated_at": r.updated_at.isoformat() if r.updated_at else None,
        }
        for r in rows
    ]


@router.get("/seo-ranks")
def list_seo(
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> list[dict]:
    rows = db.scalars(select(SeoRankModel).order_by(SeoRankModel.tracked_at.desc()).limit(50)).all()
    return [
        {
            "id": r.id,
            "keyword": r.keyword,
            "app_id": r.app_id,
            "position": r.position,
            "url": r.url,
            "tracked_at": r.tracked_at.isoformat() if r.tracked_at else None,
        }
        for r in rows
    ]


@router.get("/api-requests")
def list_api_requests(
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> list[dict]:
    rows = db.scalars(
        select(ApiKeyRequestModel).order_by(ApiKeyRequestModel.id.desc()).limit(50)
    ).all()
    return [
        {
            "id": r.id,
            "agent_id": r.agent_id,
            "service_name": r.service_name,
            "reason": r.reason,
            "status": r.status.value if hasattr(r.status, "value") else str(r.status),
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


class ApiRequestPatch(BaseModel):
    status: Literal["fulfilled", "rejected", "approved"]


@router.patch("/api-requests/{req_id}")
def patch_api_request(
    req_id: int,
    body: ApiRequestPatch,
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> dict:
    row = db.get(ApiKeyRequestModel, req_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Demande introuvable")
    row.status = ApiKeyRequestStatus(body.status)
    db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "agent_id": row.agent_id,
        "service_name": row.service_name,
        "reason": row.reason,
        "status": row.status.value,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


def _intel_priority_to_task_priority(p: str | None) -> TaskPriority:
    key = (p or "normal").strip().lower()
    mapping: dict[str, TaskPriority] = {
        "low": TaskPriority.low,
        "normal": TaskPriority.medium,
        "medium": TaskPriority.medium,
        "high": TaskPriority.high,
        "critical": TaskPriority.critical,
    }
    return mapping.get(key, TaskPriority.medium)


_DECIDE_STATUSES = frozenset(
    {
        IntelStatus.new,
        IntelStatus.reviewed,
        IntelStatus.pending_decision,
    }
)


class IntelDecisionBody(BaseModel):
    action: Literal["approve", "reject"]
    note: str | None = Field(default=None, max_length=8000)
    priority: str | None = Field(
        default="normal",
        description="low | normal | high | critical",
    )


@router.patch("/intel/{item_id}/decide")
def decide_intel(
    item_id: int,
    body: IntelDecisionBody,
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> dict:
    item = db.get(IntelModel, item_id)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Intel introuvable")
    if item.status not in _DECIDE_STATUSES:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Statut incompatible avec une décision (attendu: à décider)",
        )

    if body.action == "reject":
        item.status = IntelStatus.rejected
        item.decision_note = body.note
        item.decision_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(item)
        return {"status": item.status.value, "task_id": None}

    pr = _intel_priority_to_task_priority(body.priority)
    item.priority = (body.priority or "normal").strip().lower()
    item.decision_note = body.note
    item.decision_at = datetime.now(timezone.utc)
    item.status = IntelStatus.approved

    task = TaskModel(
        title=f"[Intel] {item.title}",
        agent_id=item.agent_id,
        app_id=None,
        status=TaskStatus.todo,
        priority=pr,
        intel_item_id=item.id,
    )
    db.add(task)
    db.flush()
    item.task_id = task.id
    recount_agent_tasks(db, item.agent_id)

    note_txt = (
        f"INTEL APPROUVÉ — {item.title}\nPriorité: {item.priority}\nNote: {body.note or '—'}"
    )
    if item.agent_id:
        ok, _ = append_nerve_note(db, item.agent_id, note_txt)
        if not ok:
            db.commit()
    else:
        db.commit()

    db.refresh(item)
    db.refresh(task)
    return {"status": item.status.value, "task_id": item.task_id}


@router.patch("/intel/{item_id}/verify")
def verify_intel(
    item_id: int,
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> dict:
    item = db.get(IntelModel, item_id)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Intel introuvable")
    if item.status != IntelStatus.implemented:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Seules les entrées au statut « implemented » peuvent être vérifiées",
        )
    item.status = IntelStatus.verified
    item.verified_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(item)
    return {"status": item.status.value, "verified_at": item.verified_at.isoformat() if item.verified_at else None}
