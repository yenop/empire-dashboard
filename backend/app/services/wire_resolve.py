"""Resolve Wire conversation id for an agent (OpenClaw job UUID from AGENTS_MAP, or DB heuristic)."""

from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models import WireConversationModel, WireMessageModel
from app.services import openclaw_cron as oc
from app.services.wire_messages import wire_timeline_sort_key

_BROADCAST_TOS = frozenset(("", "all", "*", "everyone"))


def _is_broadcast_to(to_id: str | None) -> bool:
    if to_id is None:
        return True
    return str(to_id).strip().lower() in _BROADCAST_TOS


def resolve_conversation_id_for_agent(db: Session, agent_id: str) -> str | None:
    """
    OpenClaw: first wire conversation whose agent_key matches (from AGENTS_MAP + jobId).
    Database: conversation (among recent ids) whose latest non-broadcast message involves the agent.
    """
    items = oc.build_wire_conversations()
    if items is not None:
        for it in items:
            if it.get("agent_key") == agent_id and it.get("id") is not None:
                return str(it["id"])
        return None

    rows = db.scalars(
        select(WireConversationModel.id)
        .order_by(desc(WireConversationModel.id))
        .limit(120)
    ).all()
    best_id: int | None = None
    best_key: float = -1.0
    for (cid,) in rows:
        last = db.scalars(
            select(WireMessageModel)
            .where(WireMessageModel.conversation_id == cid)
            .order_by(
                WireMessageModel.created_at.desc(),
                WireMessageModel.id.desc(),
            )
            .limit(1)
        ).first()
        if not last or _is_broadcast_to(last.to_agent_id):
            continue
        if last.to_agent_id != agent_id and last.from_agent_id != agent_id:
            continue
        ts_iso = last.created_at.isoformat() if last.created_at else None
        tkey = wire_timeline_sort_key({"created_at": ts_iso})
        if tkey >= best_key:
            best_key = tkey
            best_id = cid
    return str(best_id) if best_id is not None else None
