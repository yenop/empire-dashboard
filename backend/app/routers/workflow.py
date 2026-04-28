from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_username
from app.models import PhaseDeliverableModel, WorkflowStateModel
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


@router.get("/deliverables")
def list_deliverables(
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> list[dict]:
    st = _get_state(db)
    phase = max(1, min(10, st.phase))
    rows = db.scalars(
        select(PhaseDeliverableModel)
        .where(PhaseDeliverableModel.phase == phase)
        .order_by(PhaseDeliverableModel.id)
    ).all()
    phase_def = next((p for p in PHASES if p["index"] == phase), PHASES[0])
    defs = phase_def.get("deliverables") or []
    auto_by_key: dict[str, str | None] = {
        str(d["key"]): d.get("auto_check") for d in defs
    }
    out: list[dict] = []
    for r in rows:
        out.append(
            {
                "key": r.key,
                "label": r.label,
                "required": r.required,
                "checked_at": r.checked_at.isoformat() if r.checked_at else None,
                "checked_by": r.checked_by,
                "auto_check": auto_by_key.get(r.key),
            }
        )
    return out


@router.patch("/deliverables/{key}/check")
def check_deliverable(
    key: str,
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> dict:
    st = _get_state(db)
    phase = max(1, min(10, st.phase))
    row = db.scalars(
        select(PhaseDeliverableModel).where(
            PhaseDeliverableModel.phase == phase,
            PhaseDeliverableModel.key == key,
        )
    ).first()
    if not row:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Livrable « {key} » introuvable pour la phase {phase}.",
        )
    if not row.checked_at:
        row.checked_at = datetime.now(timezone.utc)
        row.checked_by = "human"
        db.add(row)
        db.commit()
        db.refresh(row)
    return {
        "key": row.key,
        "checked_at": row.checked_at.isoformat() if row.checked_at else None,
        "checked_by": row.checked_by,
    }


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

    phase = max(1, min(10, st.phase))
    unchecked = (
        db.scalar(
            select(func.count())
            .select_from(PhaseDeliverableModel)
            .where(
                PhaseDeliverableModel.phase == phase,
                PhaseDeliverableModel.required.is_(True),
                PhaseDeliverableModel.checked_at.is_(None),
            )
        )
        or 0
    )
    if unchecked > 0:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=(
                f"{unchecked} livrable(s) requis non validé(s) pour la phase {phase}"
            ),
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
    db.execute(
        update(PhaseDeliverableModel).values(checked_at=None, checked_by=None)
    )
    db.commit()
    db.refresh(st)
    return _workflow_payload(db)
