"""Métriques de flux Intel (délai décision, implémentation, blocages)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import IntelModel, IntelStatus
from app.schemas import IntelPipelineKpiOut


def _as_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def compute_intel_pipeline_kpis(db: Session) -> IntelPipelineKpiOut:
    st = IntelStatus

    rows_decided = db.scalars(select(IntelModel).where(IntelModel.decision_at.isnot(None))).all()
    avg_days: float | None = None
    if rows_decided:
        deltas: list[float] = []
        for r in rows_decided:
            ca, da = r.created_at, r.decision_at
            if ca and da and da >= ca:
                deltas.append((da - ca).total_seconds() / 86400.0)
        if deltas:
            avg_days = sum(deltas) / len(deltas)

    den = (
        db.scalar(
            select(func.count())
            .select_from(IntelModel)
            .where(
                IntelModel.status.in_(
                    [st.approved, st.implementing, st.implemented, st.verified]
                )
            )
        )
        or 0
    )
    num = (
        db.scalar(
            select(func.count())
            .select_from(IntelModel)
            .where(IntelModel.status.in_([st.implemented, st.verified]))
        )
        or 0
    )
    rate = (num / float(den) * 100.0) if den else None

    approved_no_task = (
        db.scalar(
            select(func.count())
            .select_from(IntelModel)
            .where(IntelModel.status == st.approved, IntelModel.task_id.is_(None))
        )
        or 0
    )

    cutoff = datetime.now(timezone.utc) - timedelta(days=14)
    impl_rows = (
        db.scalars(
            select(IntelModel)
            .where(IntelModel.status == st.implementing)
            .options(joinedload(IntelModel.task))
        )
        .unique()
        .all()
    )
    stuck = 0
    for i in impl_rows:
        ref = None
        if i.task:
            ref = _as_utc(i.task.updated_at)
        if ref is None:
            ref = _as_utc(getattr(i, "updated_at", None))
        if ref is None:
            ref = _as_utc(i.created_at)
        if ref is not None and ref <= cutoff:
            stuck += 1

    return IntelPipelineKpiOut(
        avg_days_new_to_decision=avg_days,
        avg_days_alert=bool(avg_days is not None and avg_days > 7.0),
        implementation_rate_pct=rate,
        implementation_rate_alert=bool(rate is not None and rate < 70.0),
        approved_without_task=int(approved_no_task),
        approved_without_task_alert=int(approved_no_task) > 0,
        implementing_stuck_over_14d=stuck,
        implementing_stuck_alert=stuck > 0,
    )
