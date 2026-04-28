"""Auto-check phase deliverables from DB signals (cron / background loop)."""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import NicheCandidateModel, PhaseDeliverableModel


def _mark_checked(db: Session, phase: int, key: str) -> bool:
    """Returns True if a row was updated."""
    row = db.scalars(
        select(PhaseDeliverableModel).where(
            PhaseDeliverableModel.phase == phase,
            PhaseDeliverableModel.key == key,
        )
    ).first()
    if not row or row.checked_at is not None:
        return False
    row.checked_at = datetime.now(timezone.utc)
    row.checked_by = "auto"
    return True


def auto_check_deliverables(db: Session, phase: int) -> None:
    """Apply measurable rules for the current phase; commits once if anything changed."""
    changed = False
    if phase == 1:
        niches_count = (
            db.scalar(select(func.count()).select_from(NicheCandidateModel)) or 0
        )
        if niches_count >= 5:
            changed |= _mark_checked(db, phase, "niches_candidates")

        top = db.scalars(
            select(NicheCandidateModel).where(NicheCandidateModel.score_seo >= 75)
        ).first()
        if top:
            changed |= _mark_checked(db, phase, "niche_scored")

    if changed:
        db.commit()
