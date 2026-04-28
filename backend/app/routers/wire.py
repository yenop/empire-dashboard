from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.deps import get_current_username
from app.models import AgentModel, WireConversationModel, WireMessageModel
from app.services import openclaw_cron as oc
from app.services.openclaw_wire_db import get_or_create_openclaw_conversation
from app.services.wire_outbound import append_nerve_note

router = APIRouter(prefix="/api/wire", tags=["wire"])


def _db_messages_for_openclaw_job(db: Session, job_id: str) -> list[dict]:
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
        .order_by(WireMessageModel.created_at, WireMessageModel.id)
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
        }
        for m in msgs
    ]


def _wire_timeline_sort_key(item: dict) -> float:
    raw = item.get("created_at")
    if not raw:
        return 0.0
    return oc._parse_ts_sort_key(str(raw))


def _merge_openclaw_and_db_messages(
    oc_list: list[dict], db_list: list[dict]
) -> list[dict]:
    merged = oc_list + db_list
    merged.sort(key=_wire_timeline_sort_key)
    return merged


@router.get("/conversations")
def list_conversations(
    limit: int = 80,
    offset: int = 0,
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> dict:
    limit = max(1, min(200, limit))
    offset = max(0, offset)

    oc_items = oc.build_wire_conversations()
    if oc_items is not None:
        total = len(oc_items)
        sliced = oc_items[offset : offset + limit]
        return {
            "total": total,
            "items": sliced,
            "source": "openclaw",
        }

    total = db.scalar(select(func.count()).select_from(WireConversationModel)) or 0
    rows = (
        db.scalars(
            select(WireConversationModel)
            .order_by(WireConversationModel.id.desc())
            .offset(offset)
            .limit(limit)
        )
        .all()
    )
    previews: list[dict] = []
    for c in rows:
        last = (
            db.scalars(
                select(WireMessageModel)
                .where(WireMessageModel.conversation_id == c.id)
                .order_by(WireMessageModel.id.desc())
                .limit(1)
            )
            .first()
        )
        n_msg = db.scalar(
            select(func.count())
            .select_from(WireMessageModel)
            .where(WireMessageModel.conversation_id == c.id)
        )
        previews.append(
            {
                "id": c.id,
                "title": c.title,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "message_count": int(n_msg or 0),
                "preview": (last.body[:160] + "…")
                if last and len(last.body) > 160
                else (last.body if last else ""),
            }
        )
    return {"total": int(total), "items": previews, "source": "database"}


@router.get("/conversations/{conv_id}/messages")
def list_messages(
    conv_id: str,
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> list[dict]:
    oc_list = oc.wire_messages_for_job(conv_id)
    if oc_list is not None:
        db_extra = _db_messages_for_openclaw_job(db, conv_id)
        if db_extra:
            return _merge_openclaw_and_db_messages(oc_list, db_extra)
        return oc_list

    try:
        conv_id_int = int(conv_id)
    except ValueError as e:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Conversation introuvable (id OpenClaw ou numérique attendu)",
        ) from e
    conv = db.get(WireConversationModel, conv_id_int)
    if not conv:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Conversation introuvable")
    msgs = db.scalars(
        select(WireMessageModel)
        .where(WireMessageModel.conversation_id == conv_id_int)
        .order_by(WireMessageModel.created_at, WireMessageModel.id)
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
        }
        for m in msgs
    ]


class WireOutboundPayload(BaseModel):
    """Message Dashboard → agent (fil sélectionné)."""

    body: str = Field(..., min_length=1, max_length=50_000)
    to_agent_id: str = Field(..., min_length=1, max_length=50)
    conversation_id: str = Field(
        ...,
        description="Id conversation : entier (mode DB) ou UUID job OpenClaw",
    )
    push_to_nerve: bool = True


@router.post("/messages")
def post_wire_message(
    payload: WireOutboundPayload,
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> dict:
    if not db.get(AgentModel, payload.to_agent_id):
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="Agent destinataire introuvable"
        )

    oc_volume = oc.oc_root().exists() and oc.oc_root().is_dir()
    conv_raw = payload.conversation_id.strip()
    conv: WireConversationModel | None = None

    try:
        conv_num = int(conv_raw)
    except ValueError:
        conv_num = None

    if conv_num is not None:
        conv = db.get(WireConversationModel, conv_num)
        if not conv:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail="Conversation introuvable"
            )
    else:
        jid = oc.norm_uuid(conv_raw)
        try:
            UUID(conv_raw)
        except ValueError as e:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="conversation_id doit être un entier ou un UUID de job OpenClaw",
            ) from e
        if not jid:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, detail="UUID conversation invalide"
            )
        if not oc_volume:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="Volume OpenClaw non monté — utilisez l’id numérique de conversation",
            )
        dash = oc.dashboard_agent_id_for_job(jid)
        if dash and dash != payload.to_agent_id:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="L’agent ne correspond pas à ce fil OpenClaw",
            )
        conv = get_or_create_openclaw_conversation(db, jid)

    msg = WireMessageModel(
        conversation_id=conv.id,
        from_agent_id="dashboard",
        to_agent_id=payload.to_agent_id,
        body=payload.body.strip(),
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    nerve_ok = False
    nerve_err: str | None = None
    if payload.push_to_nerve:
        nerve_ok, nerve_err = append_nerve_note(db, payload.to_agent_id, payload.body)

    return {
        "ok": True,
        "message_id": msg.id,
        "conversation_id": conv.id,
        "nerve_appended": nerve_ok,
        "nerve_error": nerve_err,
    }


class WireWebhookPayload(BaseModel):
    conversation_title: str
    from_agent_id: str
    to_agent_id: str | None = None
    body: str
    secret: str


@router.post("/webhook")
def wire_webhook(
    payload: WireWebhookPayload,
    db: Session = Depends(get_db),
) -> dict:
    # Vérification secret basique
    settings = get_settings()
    if payload.secret != settings.empire_jwt_secret:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid secret")

    # Trouver ou créer la conversation du jour
    from datetime import date
    today_title = f"{payload.conversation_title} — {date.today().isoformat()}"
    conv = db.scalars(
        select(WireConversationModel)
        .where(WireConversationModel.title == today_title)
    ).first()

    if not conv:
        conv = WireConversationModel(title=today_title)
        db.add(conv)
        db.flush()

    msg = WireMessageModel(
        conversation_id=conv.id,
        from_agent_id=payload.from_agent_id,
        to_agent_id=payload.to_agent_id,
        body=payload.body,
    )
    db.add(msg)
    db.commit()
    return {"ok": True, "conversation_id": conv.id, "message_id": msg.id}
