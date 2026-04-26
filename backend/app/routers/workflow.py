from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_username
from app.models import WorkflowStateModel
from app.workflow_phases import PHASES

router = APIRouter(prefix="/api/workflow", tags=["workflow"])


def _workflow_payload(db: Session) -> dict:
    st = _get_state(db)
    phase = max(1, min(10, st.phase))
    current = next((p for p in PHASES if p["index"] == phase), PHASES[0])
    lit = list(current["agents"])
    return {
        "phase": phase,
        "last_validated_at": st.last_validated_at.isoformat()
        if st.last_validated_at
        else None,
        "phases": PHASES,
        "current": current,
        "lit_agent_ids": lit,
    }


def _get_state(db: Session) -> WorkflowStateModel:
    row = db.get(WorkflowStateModel, 1)
    if not row:
        row = WorkflowStateModel(id=1, phase=1)
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


@router.get("")
def get_workflow(
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> dict:
    return _workflow_payload(db)


@router.post("/advance")
def advance_phase(
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> dict:
    st = _get_state(db)
    if st.phase >= 10:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Déjà à la phase 10. Réinitialisez côté ops si besoin.",
        )
    st.phase = st.phase + 1
    st.last_validated_at = datetime.now(timezone.utc)
    db.add(st)
    db.commit()
    db.refresh(st)
    return _workflow_payload(db)


@router.post("/reset")
def reset_phase(
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> dict:
    st = _get_state(db)
    st.phase = 1
    st.last_validated_at = None
    db.add(st)
    db.commit()
    return _workflow_payload(db)
