from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_username
from app.models import WireConversationModel, WireMessageModel
from app.services import openclaw_cron as oc

router = APIRouter(prefix="/api/wire", tags=["wire"])


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
        }
        for m in msgs
    ]
