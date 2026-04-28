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


def _run_ignore(conn, sql: str) -> None:
    try:
        conn.execute(text(sql))
    except Exception:
        pass


def ensure_intel_pipeline_schema() -> None:
    """Intel decision pipeline: extra columns, status vocabulary, task.intel_item_id."""
    insp = inspect(engine)
    if not insp.has_table("intel"):
        return

    intel_cols = {c["name"] for c in insp.get_columns("intel")}

    with engine.begin() as conn:
        if "agent_id" not in intel_cols:
            _run_ignore(conn, "ALTER TABLE intel ADD COLUMN agent_id VARCHAR(50)")
        if "decision_note" not in intel_cols:
            _run_ignore(conn, "ALTER TABLE intel ADD COLUMN decision_note TEXT")
        if "decision_at" not in intel_cols:
            _run_ignore(conn, "ALTER TABLE intel ADD COLUMN decision_at DATETIME")
        if "task_id" not in intel_cols:
            _run_ignore(conn, "ALTER TABLE intel ADD COLUMN task_id INTEGER")
        if "implemented_at" not in intel_cols:
            _run_ignore(conn, "ALTER TABLE intel ADD COLUMN implemented_at DATETIME")
        if "verified_at" not in intel_cols:
            _run_ignore(conn, "ALTER TABLE intel ADD COLUMN verified_at DATETIME")
        if "priority" not in intel_cols:
            _run_ignore(
                conn,
                "ALTER TABLE intel ADD COLUMN priority VARCHAR(20) NOT NULL DEFAULT 'normal'",
            )
        if "updated_at" not in intel_cols:
            _run_ignore(
                conn,
                "ALTER TABLE intel ADD COLUMN updated_at DATETIME "
                "DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
            )

        conn.execute(
            text(
                "UPDATE intel SET status = 'pending_decision' "
                "WHERE status IN ('pending', 'borderline')"
            )
        )

        _run_ignore(conn, "ALTER TABLE intel MODIFY COLUMN status VARCHAR(32) NOT NULL")

        if insp.has_table("tasks"):
            tasks_cols = {c["name"] for c in insp.get_columns("tasks")}
            if "intel_item_id" not in tasks_cols:
                _run_ignore(conn, "ALTER TABLE tasks ADD COLUMN intel_item_id INTEGER")

        _run_ignore(
            conn,
            "ALTER TABLE intel ADD CONSTRAINT fk_intel_agent "
            "FOREIGN KEY (agent_id) REFERENCES agents(id)",
        )
        _run_ignore(
            conn,
            "ALTER TABLE intel ADD CONSTRAINT fk_intel_task "
            "FOREIGN KEY (task_id) REFERENCES tasks(id)",
        )
        _run_ignore(
            conn,
            "ALTER TABLE tasks ADD CONSTRAINT fk_tasks_intel_item "
            "FOREIGN KEY (intel_item_id) REFERENCES intel(id)",
        )
