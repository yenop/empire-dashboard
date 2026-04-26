from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_username
from app.models import AgentModel, AgentStatus, AppModel, AppStatus, IntelModel
from app.schemas import AppSummaryOut, DashboardOut, IntelItemOut, KpiOut

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardOut)
def get_dashboard(
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> DashboardOut:
    mrr = db.scalar(select(func.coalesce(func.sum(AppModel.mrr), 0))) or Decimal("0")
    apps_live = db.scalar(
        select(func.count()).select_from(AppModel).where(AppModel.status == AppStatus.live)
    ) or 0
    agents_active = db.scalar(
        select(func.count())
        .select_from(AgentModel)
        .where(AgentModel.status == AgentStatus.active)
    ) or 0
    churn_avg = db.scalar(select(func.avg(AppModel.churn_rate))) or Decimal("0")
    downloads = db.scalar(select(func.coalesce(func.sum(AppModel.downloads), 0))) or 0
    aso_avg = db.scalar(select(func.avg(AppModel.aso_score))) or Decimal("0")

    apps_rows = db.scalars(select(AppModel).order_by(AppModel.name)).all()
    apps = [
        AppSummaryOut(
            id=a.id,
            name=a.name,
            niche=a.niche,
            icon=a.icon,
            color=a.color,
            mrr=a.mrr,
            conversion_rate=a.conversion_rate,
            status=a.status.value,
        )
        for a in apps_rows
    ]

    intel_rows = (
        db.scalars(select(IntelModel).order_by(IntelModel.created_at.desc()).limit(12))
        .all()
    )
    intel = [IntelItemOut.from_row(i) for i in intel_rows]

    return DashboardOut(
        kpis=KpiOut(
            mrr_total=Decimal(str(mrr)),
            apps_live=int(apps_live),
            agents_active=int(agents_active),
            churn_avg=Decimal(str(churn_avg)),
            downloads_month=int(downloads),
            aso_score_avg=Decimal(str(aso_avg)),
        ),
        apps=apps,
        intel=intel,
    )
