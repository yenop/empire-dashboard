"""Conversations Wire liées aux jobs OpenClaw (partagé wire + tasks)."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import WireConversationModel
from app.services import openclaw_cron as oc


def title_for_openclaw_job(jid: str) -> str:
    spec = oc.spec_for_job_id(jid)
    if spec:
        return f"{spec['name']} — {spec['label']}"
    return f"OpenClaw job {jid[:8]}…"


def get_or_create_openclaw_conversation(db: Session, job_id: str) -> WireConversationModel:
    jid = oc.norm_uuid(job_id)
    if not jid:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="conversation_id OpenClaw invalide"
        )
    conv = db.scalars(
        select(WireConversationModel).where(WireConversationModel.openclaw_job_id == jid)
    ).first()
    if conv:
        return conv
    conv = WireConversationModel(title=title_for_openclaw_job(jid), openclaw_job_id=jid)
    db.add(conv)
    db.flush()
    return conv
