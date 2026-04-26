from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_username
from app.models import WireConversationModel, WireMessageModel

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
                "preview": (last.body[:160] + "…") if last and len(last.body) > 160 else (last.body if last else ""),
            }
        )
    return {"total": int(total), "items": previews}


@router.get("/conversations/{conv_id}/messages")
def list_messages(
    conv_id: int,
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> list[dict]:
    conv = db.get(WireConversationModel, conv_id)
    if not conv:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Conversation introuvable")
    msgs = db.scalars(
        select(WireMessageModel)
        .where(WireMessageModel.conversation_id == conv_id)
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
