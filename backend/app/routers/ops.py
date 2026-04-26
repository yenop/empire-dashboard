from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_username
from app.models import (
    ApiKeyRequestModel,
    ApiKeyRequestStatus,
    ContentPipelineModel,
    NicheCandidateModel,
    SeoRankModel,
)

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
