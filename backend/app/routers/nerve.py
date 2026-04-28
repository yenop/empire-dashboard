from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.deps import get_current_username
from app.models import AgentModel, NerveFileModel
from app.services import nerve_files as nf
from app.workflow_phases import NERVE_LABELS, NERVE_SLUGS

router = APIRouter(prefix="/api/nerve", tags=["nerve"])


class NerveFileUpdate(BaseModel):
    content: str = Field(..., max_length=500_000)


def _nerve_storage_mode() -> str:
    s = get_settings()
    st = (s.nerve_storage or "database").lower()
    if st not in ("database", "filesystem"):
        return "database"
    return st


@router.get("/slugs")
def list_slugs(_username: str = Depends(get_current_username)) -> list[dict[str, str]]:
    return [{"slug": s, "label": NERVE_LABELS[s]} for s in NERVE_SLUGS]


@router.get("/meta")
def nerve_meta(_username: str = Depends(get_current_username)) -> dict[str, str]:
    st = _nerve_storage_mode()
    if st == "filesystem":
        label = "Fichiers OpenClaw (OPENCLAW_DIR)"
    else:
        label = "Base Empire (nerve_files)"
    return {"storage": st, "source_label": label}


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
    if _nerve_storage_mode() == "filesystem":
        settings = get_settings()
        try:
            content = nf.read_nerve_file(agent_id, slug, settings)
        except nf.NervePathError as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    else:
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
    if _nerve_storage_mode() == "filesystem":
        settings = get_settings()
        try:
            nf.write_nerve_file(agent_id, slug, body.content, settings)
        except nf.NervePathError as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
        except OSError as e:
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Cannot write nerve file: {e}",
            ) from e
        content = nf.read_nerve_file(agent_id, slug, settings)
    else:
        row = db.get(NerveFileModel, (agent_id, slug))
        if not row:
            row = NerveFileModel(agent_id=agent_id, slug=slug, content=body.content)
            db.add(row)
        else:
            row.content = body.content
        db.commit()
        db.refresh(row)
        content = row.content
    return {
        "agent_id": agent_id,
        "slug": slug,
        "label": NERVE_LABELS[slug],
        "content": content,
    }
