"""Shared Wire message fetch + dashboard outbound (used by wire and niche-process routers)."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models import AgentModel, WireConversationModel, WireMessageModel
from app.services import openclaw_cron as oc
from app.services.openclaw_wire_db import get_or_create_openclaw_conversation
from app.services.wire_outbound import append_nerve_note


class WireMessageError(Exception):
    """Invalid request (bad id, volume, agent mismatch)."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class WireConversationNotFound(WireMessageError):
    def __init__(self, detail: str = "Conversation introuvable") -> None:
        super().__init__(404, detail)


def db_messages_for_openclaw_job(db: Session, job_id: str) -> list[dict]:
    jid = oc.norm_uuid(job_id)
    if not jid:
        return []
    conv = db.scalars(
        select(WireConversationModel).where(WireConversationModel.openclaw_job_id == jid)
    ).first()
    if not conv:
        return []
    msgs = db.scalars(
        select(WireMessageModel)
        .where(WireMessageModel.conversation_id == conv.id)
        .order_by(WireMessageModel.created_at.desc(), WireMessageModel.id.desc())
    ).all()
    return [
        {
            "id": f"db-{m.id}",
            "from_agent_id": m.from_agent_id,
            "to_agent_id": m.to_agent_id,
            "body": m.body,
            "created_at": m.created_at.isoformat() if m.created_at else None,
            "source": "dashboard",
            "meta": None,
            "human_status": m.human_status.value,
            "ack_at": m.ack_at.isoformat() if m.ack_at else None,
            "applied_at": m.applied_at.isoformat() if m.applied_at else None,
        }
        for m in msgs
    ]


def wire_timeline_sort_key(item: dict) -> float:
    raw = item.get("created_at")
    if not raw:
        return 0.0
    return oc._parse_ts_sort_key(str(raw))


def merge_openclaw_and_db_messages(oc_list: list[dict], db_list: list[dict]) -> list[dict]:
    merged = oc_list + db_list
    merged.sort(key=wire_timeline_sort_key, reverse=True)
    return merged


def fetch_messages_for_conversation(db: Session, conv_id: str) -> list[dict]:
    """Same result shape as GET /api/wire/conversations/{id}/messages."""
    oc_list = oc.wire_messages_for_job(conv_id)
    if oc_list is not None:
        db_extra = db_messages_for_openclaw_job(db, conv_id)
        if db_extra:
            return merge_openclaw_and_db_messages(oc_list, db_extra)
        return oc_list

    try:
        conv_id_int = int(conv_id)
    except ValueError as e:
        raise WireConversationNotFound(
            "Conversation introuvable (id OpenClaw ou numérique attendu)"
        ) from e
    conv = db.get(WireConversationModel, conv_id_int)
    if not conv:
        raise WireConversationNotFound()
    msgs = db.scalars(
        select(WireMessageModel)
        .where(WireMessageModel.conversation_id == conv_id_int)
        .order_by(
            WireMessageModel.created_at.desc(),
            WireMessageModel.id.desc(),
        )
    ).all()
    return [
        {
            "id": m.id,
            "from_agent_id": m.from_agent_id,
            "to_agent_id": m.to_agent_id,
            "body": m.body,
            "created_at": m.created_at.isoformat() if m.created_at else None,
            "source": "database",
            "meta": None,
            "human_status": m.human_status.value,
            "ack_at": m.ack_at.isoformat() if m.ack_at else None,
            "applied_at": m.applied_at.isoformat() if m.applied_at else None,
        }
        for m in msgs
    ]


def post_dashboard_message(
    db: Session,
    *,
    body: str,
    to_agent_id: str,
    conversation_id: str,
    push_to_nerve: bool,
) -> dict:
    """Create one dashboard → agent message; same rules as POST /api/wire/messages."""
    if not db.get(AgentModel, to_agent_id):
        raise WireMessageError(404, "Agent destinataire introuvable")

    oc_volume = oc.oc_root().exists() and oc.oc_root().is_dir()
    conv_raw = conversation_id.strip()
    conv: WireConversationModel | None = None

    try:
        conv_num = int(conv_raw)
    except ValueError:
        conv_num = None

    if conv_num is not None:
        conv = db.get(WireConversationModel, conv_num)
        if not conv:
            raise WireConversationNotFound()
    else:
        jid = oc.norm_uuid(conv_raw)
        try:
            UUID(conv_raw)
        except ValueError as e:
            raise WireMessageError(
                400, "conversation_id doit être un entier ou un UUID de job OpenClaw"
            ) from e
        if not jid:
            raise WireMessageError(400, "UUID conversation invalide")
        if not oc_volume:
            raise WireMessageError(
                400, "Volume OpenClaw non monté — utilisez l’id numérique de conversation"
            )
        dash = oc.dashboard_agent_id_for_job(jid)
        if dash and dash != to_agent_id:
            raise WireMessageError(
                400, "L’agent ne correspond pas à ce fil OpenClaw"
            )
        conv = get_or_create_openclaw_conversation(db, jid)

    msg = WireMessageModel(
        conversation_id=conv.id,
        from_agent_id="dashboard",
        to_agent_id=to_agent_id,
        body=body.strip(),
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    nerve_ok = False
    nerve_err: str | None = None
    if push_to_nerve:
        nerve_ok, nerve_err = append_nerve_note(
            db,
            to_agent_id,
            body.strip(),
            message_id=msg.id,
            human_status="sent",
        )

    return {
        "ok": True,
        "message_id": msg.id,
        "conversation_id": conv.id,
        "nerve_appended": nerve_ok,
        "nerve_error": nerve_err,
    }
