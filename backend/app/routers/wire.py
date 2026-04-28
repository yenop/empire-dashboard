from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, nulls_last, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.deps import get_current_username
from app.models import (
    AgentModel,
    WireConversationModel,
    WireMessageModel,
    WireMessageStatus,
)
from app.services import openclaw_cron as oc
from app.services.openclaw_wire_db import get_or_create_openclaw_conversation
from app.services.wire_outbound import append_nerve_note

router = APIRouter(prefix="/api/wire", tags=["wire"])

_BROADCAST_TOS = frozenset(("", "all", "*", "everyone"))


def _is_broadcast_to(to_id: str | None) -> bool:
    if to_id is None:
        return True
    return str(to_id).strip().lower() in _BROADCAST_TOS


def _pole_agent_id_for_message(m: WireMessageModel | None) -> str | None:
    if not m:
        return None
    if m.from_agent_id and m.from_agent_id != "dashboard":
        return m.from_agent_id
    if m.to_agent_id and not _is_broadcast_to(m.to_agent_id) and m.to_agent_id != "dashboard":
        return m.to_agent_id
    if m.from_agent_id == "dashboard" and m.to_agent_id and not _is_broadcast_to(m.to_agent_id):
        return m.to_agent_id
    return None


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


def _wire_timeline_sort_key(item: dict) -> float:
    raw = item.get("created_at")
    if not raw:
        return 0.0
    return oc._parse_ts_sort_key(str(raw))


def _merge_openclaw_and_db_messages(
    oc_list: list[dict], db_list: list[dict]
) -> list[dict]:
    merged = oc_list + db_list
    merged.sort(key=_wire_timeline_sort_key, reverse=True)
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
        n_broadcast = sum(1 for it in oc_items if it.get("last_is_broadcast"))
        n_conv = len(oc_items) - n_broadcast
        n_msg = sum(int(it.get("message_count") or 0) for it in oc_items)
        total = len(oc_items)
        sliced = oc_items[offset : offset + limit]
        return {
            "total": total,
            "items": sliced,
            "source": "openclaw",
            "stats": {
                "messages": n_msg,
                "broadcasts": n_broadcast,
                "conversations": n_conv,
                "threads": total,
            },
        }

    total = db.scalar(select(func.count()).select_from(WireConversationModel)) or 0
    last_mx = (
        select(
            WireMessageModel.conversation_id.label("cid"),
            func.max(WireMessageModel.created_at).label("last_at"),
        )
        .group_by(WireMessageModel.conversation_id)
        .subquery()
    )
    rows = list(
        db.scalars(
            select(WireConversationModel)
            .outerjoin(last_mx, WireConversationModel.id == last_mx.c.cid)
            .order_by(
                nulls_last(last_mx.c.last_at.desc()),
                desc(WireConversationModel.id),
            )
            .offset(offset)
            .limit(limit)
        )
        .all()
    )
    all_agent_ids: set[str] = set()
    last_by_cid: dict[int, WireMessageModel | None] = {}
    for c in rows:
        last = (
            db.scalars(
                select(WireMessageModel)
                .where(WireMessageModel.conversation_id == c.id)
                .order_by(
                    WireMessageModel.created_at.desc(),
                    WireMessageModel.id.desc(),
                )
                .limit(1)
            )
            .first()
        )
        last_by_cid[c.id] = last
        if last:
            p = _pole_agent_id_for_message(last)
            if p:
                all_agent_ids.add(p)
    id_rows = (
        [db.get(AgentModel, aid) for aid in all_agent_ids] if all_agent_ids else []
    )
    agent_pole: dict[str, str] = {}
    for a in id_rows:
        if a:
            agent_pole[a.id] = a.pole
    n_msg_db = int(
        db.scalar(select(func.count()).select_from(WireMessageModel)) or 0
    )
    n_broadcast_db = int(
        db.scalar(
            select(func.count())
            .select_from(WireMessageModel)
            .where(
                WireMessageModel.to_agent_id.is_(None)
                | WireMessageModel.to_agent_id.in_(("all", "*", "everyone"))
            )
        )
        or 0
    )
    n_direct = max(0, n_msg_db - n_broadcast_db)
    previews: list[dict] = []
    for c in rows:
        last = last_by_cid.get(c.id)
        n_msg = db.scalar(
            select(func.count())
            .select_from(WireMessageModel)
            .where(WireMessageModel.conversation_id == c.id)
        )
        is_bc = last is not None and _is_broadcast_to(last.to_agent_id)
        pole_aid = _pole_agent_id_for_message(last) if last else None
        last_pole = agent_pole.get(pole_aid) if pole_aid else None
        last_at_iso = (
            last.created_at.isoformat()
            if last and last.created_at
            else (c.created_at.isoformat() if c.created_at else None)
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
                "last_message_at": last_at_iso,
                "last_is_broadcast": is_bc,
                "last_pole": last_pole,
                "last_from_agent_id": last.from_agent_id if last else None,
                "last_to_agent_id": last.to_agent_id if last else None,
            }
        )
    return {
        "total": int(total),
        "items": previews,
        "source": "database",
        "stats": {
            "messages": n_msg_db,
            "broadcasts": n_broadcast_db,
            "conversations": n_direct,
            "threads": int(total or 0),
        },
    }


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


class WireCreateConversationBody(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)


@router.post("/conversations", status_code=status.HTTP_201_CREATED)
def create_conversation(
    payload: WireCreateConversationBody,
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> dict:
    t = " ".join(payload.title.split())
    conv = WireConversationModel(title=t)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return {
        "id": conv.id,
        "title": conv.title,
        "created_at": conv.created_at.isoformat() if conv.created_at else None,
    }


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
        nerve_ok, nerve_err = append_nerve_note(
            db,
            payload.to_agent_id,
            payload.body,
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


class WireStatusBody(BaseModel):
    status: Literal["approved", "rework"]
    note: str = ""


@router.patch("/messages/{message_id}/status")
def set_message_status(
    message_id: int,
    body: WireStatusBody,
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> dict:
    msg = db.get(WireMessageModel, message_id)
    if not msg:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Message introuvable")

    if body.status == "approved":
        msg.human_status = WireMessageStatus.approved
    else:
        msg.human_status = WireMessageStatus.rework
    db.commit()
    db.refresh(msg)

    note_text = (body.note or "").strip() or msg.body
    target_agent = msg.to_agent_id
    if not target_agent:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Message sans destinataire — impossible d’écrire sur le Nerve",
        )
    append_nerve_note(
        db,
        target_agent,
        note_text,
        message_id=message_id,
        human_status=body.status,
    )
    return {"status": msg.human_status.value}


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

    # Push dans le Nerve (HEARTBEAT) de l'agent destinataire pour qu'il reçoive le message
    nerve_ok, nerve_err = False, None
    if payload.to_agent_id:
        nerve_ok, nerve_err = append_nerve_note(db, payload.to_agent_id, payload.body)

    return {"ok": True, "conversation_id": conv.id, "message_id": msg.id, "nerve_appended": nerve_ok, "nerve_error": nerve_err}
