import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app import models  # noqa: F401
from app.database import Base, SessionLocal, engine
from app.db_schema import (
    ensure_intel_pipeline_schema,
    ensure_wire_conversations_openclaw_column,
    ensure_wire_message_status_columns,
)
from app.limiter import limiter
from app.routers import (
    agents,
    apps,
    auth,
    dashboard,
    internal_tasks,
    intel,
    mrr,
    nerve,
    niche_process,
    ops,
    supervision,
    tasks,
    wire,
    workflow,
)
from app.niche_process_catalog import default_state_payload
from app.services.minio_client import ensure_bucket
from app.services.deliverable_checker import auto_check_deliverables
from app.services.seed import seed_empire_extensions, seed_if_empty

logger = logging.getLogger(__name__)


async def _deliverable_checker_loop() -> None:
    await asyncio.sleep(300)
    while True:
        try:
            from app.models import WorkflowStateModel

            db = SessionLocal()
            try:
                st = db.get(WorkflowStateModel, 1)
                if st:
                    auto_check_deliverables(db, max(1, min(10, st.phase)))
            finally:
                db.close()
        except Exception:
            logger.exception("deliverable_checker loop failed")
        await asyncio.sleep(300)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    ensure_wire_conversations_openclaw_column()
    ensure_wire_message_status_columns()
    ensure_intel_pipeline_schema()
    with SessionLocal() as db:
        seed_if_empty(db)
        seed_empire_extensions(db)
        if not db.get(models.NicheProcessStateModel, 1):
            db.add(
                models.NicheProcessStateModel(
                    id=1,
                    payload=default_state_payload(),
                )
            )
            db.commit()
        st = db.get(models.WorkflowStateModel, 1)
        if st:
            auto_check_deliverables(db, max(1, min(10, st.phase)))
    ensure_bucket()
    checker_task = asyncio.create_task(_deliverable_checker_loop())
    yield
    checker_task.cancel()
    try:
        await checker_task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="App Empire API", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3080",
        "http://127.0.0.1:3080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(internal_tasks.router)
app.include_router(dashboard.router)
app.include_router(agents.router)
app.include_router(apps.router)
app.include_router(tasks.router)
app.include_router(intel.router)
app.include_router(mrr.router)
app.include_router(supervision.router)
app.include_router(workflow.router)
app.include_router(niche_process.router)
app.include_router(nerve.router)
app.include_router(wire.router)
app.include_router(ops.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
