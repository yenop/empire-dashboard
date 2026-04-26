from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_username
from app.models import AgentModel
from app.schemas import AgentOut

router = APIRouter(prefix="/api/agents", tags=["agents"])


def _skills_for_agent(row: AgentModel) -> dict[str, int]:
    base = min(100, max(10, int(row.xp * 2)))
    pole = row.pole
    skills = {
        "Stratégie": base,
        "Exécution": min(100, base + 5),
        "Communication": max(10, base - 10),
    }
    if pole in ("recherche", "intelligence"):
        skills["Données"] = min(100, base + 8)
    if pole == "production":
        skills["Craft"] = min(100, base + 12)
    return skills


@router.get("", response_model=list[AgentOut])
def list_agents(
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> list[AgentOut]:
    rows = db.scalars(select(AgentModel).order_by(AgentModel.name)).all()
    return [AgentOut.model_validate(r) for r in rows]


@router.get("/{agent_id}", response_model=dict[str, Any])
def get_agent(
    agent_id: str,
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    row = db.get(AgentModel, agent_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Agent not found")
    data = AgentOut.model_validate(row).model_dump()
    data["skills"] = _skills_for_agent(row)
    return data
