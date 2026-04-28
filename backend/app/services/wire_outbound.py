"""Append dashboard Wire notes to Nerve (HEARTBEAT) so crons can read them."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.models import NerveFileModel
from app.services import nerve_files as nf


def nerve_storage_mode() -> str:
    s = get_settings()
    st = (s.nerve_storage or "database").lower()
    if st not in ("database", "filesystem"):
        return "database"
    return st


def append_nerve_note(
    db: Session,
    agent_id: str,
    note: str,
    *,
    message_id: int | None = None,
    human_status: str = "sent",
    settings: Settings | None = None,
) -> tuple[bool, str | None]:
    """
    Append a dated block to HEARTBEAT. Returns (ok, error_detail).
    If workspace path is missing in filesystem mode, returns (False, reason) without raising.

    Uses FEEDBACK:* lines so OpenClaw crons can parse status without changing file layout.
    """
    s = settings or get_settings()
    slug = "heartbeat"
    status_prefix = {
        "approved": "FEEDBACK:APPROVED",
        "rework": "FEEDBACK:REWORK",
        "sent": "FEEDBACK:INFO",
    }.get(human_status, "FEEDBACK:INFO")
    timestamp = datetime.now(timezone.utc).isoformat()
    block = f"""

--- {timestamp} ---
{status_prefix}
message_id: {message_id if message_id is not None else "n/a"}
{note.strip()}
---
"""
    if nerve_storage_mode() == "filesystem":
        try:
            cur = nf.read_nerve_file(agent_id, slug, s)
        except nf.NervePathError as e:
            return False, str(e)
        try:
            nf.write_nerve_file(agent_id, slug, (cur or "") + block, s)
        except OSError as e:
            return False, str(e)
        return True, None
    row = db.get(NerveFileModel, (agent_id, slug))
    cur = row.content if row else ""
    if not row:
        row = NerveFileModel(agent_id=agent_id, slug=slug, content=cur + block)
        db.add(row)
    else:
        row.content = cur + block
    db.commit()
    return True, None
