import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AppStatus(str, enum.Enum):
    live = "live"
    beta = "beta"
    dev = "dev"


class AgentStatus(str, enum.Enum):
    active = "active"
    setup = "setup"
    recruit = "recruit"


class TaskStatus(str, enum.Enum):
    todo = "todo"
    inprogress = "inprogress"
    done = "done"


class TaskPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class IntelType(str, enum.Enum):
    skill = "skill"
    config = "config"
    update = "update"
    workflow = "workflow"
    model = "model"
    agent = "agent"
    pod = "pod"
    seo = "seo"
    api = "api"


class IntelStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    implemented = "implemented"
    borderline = "borderline"
    rejected = "rejected"


class AppModel(Base):
    __tablename__ = "apps"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    niche: Mapped[str] = mapped_column(String(200))
    icon: Mapped[str] = mapped_column(String(10))
    color: Mapped[str] = mapped_column(String(7))
    mrr: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    downloads: Mapped[int] = mapped_column(Integer, default=0)
    conversion_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"))
    churn_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"))
    aso_score: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[AppStatus] = mapped_column(
        Enum(AppStatus, native_enum=False, length=20), default=AppStatus.dev
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    tasks: Mapped[list["TaskModel"]] = relationship(back_populates="app")


class AgentModel(Base):
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(100))
    pole: Mapped[str] = mapped_column(String(50))
    emoji: Mapped[str] = mapped_column(String(10))
    color: Mapped[str] = mapped_column(String(7))
    status: Mapped[AgentStatus] = mapped_column(
        Enum(AgentStatus, native_enum=False, length=20), default=AgentStatus.recruit
    )
    xp: Mapped[int] = mapped_column(Integer, default=0)
    max_xp: Mapped[int] = mapped_column(Integer, default=50)
    rank_label: Mapped[str] = mapped_column(String(50), default="Recrue")
    tasks_count: Mapped[int] = mapped_column(Integer, default=0)
    messages_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    tasks: Mapped[list["TaskModel"]] = relationship(back_populates="agent")


class TaskModel(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200))
    agent_id: Mapped[str | None] = mapped_column(
        String(50), ForeignKey("agents.id"), nullable=True
    )
    app_id: Mapped[str | None] = mapped_column(
        String(50), ForeignKey("apps.id"), nullable=True
    )
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, native_enum=False, length=20), default=TaskStatus.todo
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority, native_enum=False, length=20), default=TaskPriority.medium
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    agent: Mapped["AgentModel | None"] = relationship(back_populates="tasks")
    app: Mapped["AppModel | None"] = relationship(back_populates="tasks")


class IntelModel(Base):
    __tablename__ = "intel"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(100))
    intel_type: Mapped[IntelType] = mapped_column(
        "type", Enum(IntelType, native_enum=False, length=20)
    )
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[IntelStatus] = mapped_column(
        Enum(IntelStatus, native_enum=False, length=20), default=IntelStatus.pending
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )


class WorkflowStateModel(Base):
    """Single-row coordination: current phase 1–10 (Timeline)."""

    __tablename__ = "workflow_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    phase: Mapped[int] = mapped_column(Integer, default=1)
    last_validated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class NerveFileModel(Base):
    """Per-agent Markdown nerve files (IDENTITY, SOUL, MEMORY, AGENTS, HEARTBEAT)."""

    __tablename__ = "nerve_files"

    agent_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    slug: Mapped[str] = mapped_column(String(32), primary_key=True)
    content: Mapped[str] = mapped_column(Text, default="")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )


class WireConversationModel(Base):
    __tablename__ = "wire_conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    messages: Mapped[list["WireMessageModel"]] = relationship(
        back_populates="conversation"
    )


class WireMessageModel(Base):
    __tablename__ = "wire_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("wire_conversations.id", ondelete="CASCADE")
    )
    from_agent_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    to_agent_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    conversation: Mapped["WireConversationModel"] = relationship(
        back_populates="messages"
    )


class NicheStatus(str, enum.Enum):
    draft = "draft"
    in_review = "in_review"
    validated = "validated"
    launched = "launched"
    rejected = "rejected"


class NicheCandidateModel(Base):
    __tablename__ = "niche_candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200))
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    score_seo: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[NicheStatus] = mapped_column(
        Enum(NicheStatus, native_enum=False, length=20), default=NicheStatus.draft
    )
    source_agents: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )


class ContentStage(str, enum.Enum):
    outline = "outline"
    draft = "draft"
    review = "review"
    published = "published"


class ContentPipelineModel(Base):
    __tablename__ = "content_pipeline"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200))
    agent_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    app_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    stage: Mapped[ContentStage] = mapped_column(
        Enum(ContentStage, native_enum=False, length=20), default=ContentStage.outline
    )
    excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )


class SeoRankModel(Base):
    __tablename__ = "seo_ranks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    keyword: Mapped[str] = mapped_column(String(200))
    app_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tracked_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )


class ApiKeyRequestStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    fulfilled = "fulfilled"
    rejected = "rejected"


class ApiKeyRequestModel(Base):
    __tablename__ = "api_key_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[str] = mapped_column(String(50))
    service_name: Mapped[str] = mapped_column(String(120))
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ApiKeyRequestStatus] = mapped_column(
        Enum(ApiKeyRequestStatus, native_enum=False, length=20),
        default=ApiKeyRequestStatus.pending,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
