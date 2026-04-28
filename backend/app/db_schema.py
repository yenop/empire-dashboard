"""Idempotent schema patches (add columns) for existing DBs — create_all does not alter tables."""

from sqlalchemy import inspect, text

from app.database import engine


def ensure_wire_conversations_openclaw_column() -> None:
    """Add openclaw_job_id to wire_conversations if missing."""
    insp = inspect(engine)
    if not insp.has_table("wire_conversations"):
        return
    cols = {c["name"] for c in insp.get_columns("wire_conversations")}
    if "openclaw_job_id" in cols:
        return
    with engine.begin() as conn:
        conn.execute(
            text(
                "ALTER TABLE wire_conversations ADD COLUMN openclaw_job_id VARCHAR(40)"
            )
        )
