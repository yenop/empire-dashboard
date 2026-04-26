from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_username
from app.models import AgentModel, NerveFileModel
from app.workflow_phases import NERVE_LABELS, NERVE_SLUGS

router = APIRouter(prefix="/api/nerve", tags=["nerve"])


class NerveFileUpdate(BaseModel):
    content: str = Field(..., max_length=500_000)


@router.get("/slugs")
def list_slugs(_username: str = Depends(get_current_username)) -> list[dict[str, str]]:
    return [{"slug": s, "label": NERVE_LABELS[s]} for s in NERVE_SLUGS]


@router.get("/agents")
def list_agents_with_nerve(
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> list[dict]:
    agents = db.scalars(select(AgentModel).order_by(AgentModel.name)).all()
    out = []
    for a in agents:
        out.append(
            {
                "id": a.id,
                "name": a.name,
                "emoji": a.emoji,
                "color": a.color,
                "slugs": list(NERVE_SLUGS),
            }
        )
    return out


@router.get("/{agent_id}/{slug}")
def get_nerve_file(
    agent_id: str,
    slug: str,
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> dict:
    if slug not in NERVE_SLUGS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Unknown slug")
    if not db.get(AgentModel, agent_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Agent not found")
    row = db.get(NerveFileModel, (agent_id, slug))
    content = row.content if row else ""
    return {
        "agent_id": agent_id,
        "slug": slug,
        "label": NERVE_LABELS[slug],
        "content": content,
    }


@router.put("/{agent_id}/{slug}")
def put_nerve_file(
    agent_id: str,
    slug: str,
    body: NerveFileUpdate,
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> dict:
    if slug not in NERVE_SLUGS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Unknown slug")
    if not db.get(AgentModel, agent_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Agent not found")
    row = db.get(NerveFileModel, (agent_id, slug))
    if not row:
        row = NerveFileModel(agent_id=agent_id, slug=slug, content=body.content)
        db.add(row)
    else:
        row.content = body.content
    db.commit()
    db.refresh(row)
    return {
        "agent_id": agent_id,
        "slug": slug,
        "label": NERVE_LABELS[slug],
        "content": row.content,
    }
