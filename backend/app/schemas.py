from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginBody(BaseModel):
    username: str
    password: str


class AgentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: str
    name: str
    role: str
    pole: str
    emoji: str
    color: str
    status: str
    xp: int
    max_xp: int
    rank_label: str
    tasks_count: int
    messages_count: int


class AppOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: str
    name: str
    niche: str
    icon: str
    color: str
    mrr: Decimal
    downloads: int
    conversion_rate: Decimal
    churn_rate: Decimal
    aso_score: int
    status: str


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    agent_id: str | None
    app_id: str | None
    status: str
    priority: str
    agent_emoji: str | None = None
    agent_name: str | None = None
    app_name: str | None = None
    app_color: str | None = None


class TaskCreate(BaseModel):
    title: str
    agent_id: str | None = None
    app_id: str | None = None
    status: str = "todo"
    priority: str = "medium"


class TaskUpdate(BaseModel):
    title: str | None = None
    status: str | None = None
    priority: str | None = None
    agent_id: str | None = None
    app_id: str | None = None


class IntelItemOut(BaseModel):
    id: int
    title: str
    source: str
    type: str
    score: int | None
    status: str
    created_at: datetime

    @classmethod
    def from_row(cls, row: Any) -> "IntelItemOut":
        it = row.intel_type
        st = row.status
        return cls(
            id=row.id,
            title=row.title,
            source=row.source,
            type=it.value if hasattr(it, "value") else str(it),
            score=row.score,
            status=st.value if hasattr(st, "value") else str(st),
            created_at=row.created_at,
        )


class KpiOut(BaseModel):
    mrr_total: Decimal
    apps_live: int
    agents_active: int
    churn_avg: Decimal
    downloads_month: int
    aso_score_avg: Decimal


class AppSummaryOut(BaseModel):
    id: str
    name: str
    niche: str
    icon: str
    color: str
    mrr: Decimal
    conversion_rate: Decimal
    status: str


class DashboardOut(BaseModel):
    kpis: KpiOut
    apps: list[AppSummaryOut]
    intel: list[IntelItemOut]
