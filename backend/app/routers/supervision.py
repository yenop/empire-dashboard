import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import get_settings
from app.deps import get_current_username
from app.services import openclaw_cron as oc

router = APIRouter(prefix="/api/supervision", tags=["supervision"])


def _read_jobs(openclaw_dir: str) -> list[dict]:
    jobs_file = Path(openclaw_dir) / "cron/jobs.json"
    if not jobs_file.exists():
        return []
    try:
        return json.loads(jobs_file.read_text())["jobs"]
    except Exception:
        return []


def _read_last_runs(openclaw_dir: str, job_id: str, n: int = 5) -> list[dict]:
    runs_file = Path(openclaw_dir) / f"cron/runs/{job_id}.jsonl"
    if not runs_file.exists():
        return []
    lines = []
    try:
        for line in runs_file.read_text().splitlines():
            line = line.strip()
            if line:
                try:
                    lines.append(json.loads(line))
                except Exception:
                    pass
    except Exception:
        pass
    return lines[-n:]


def _supervision_rows_from_map() -> list[dict[str, str]]:
    """Une ligne par entrée `openclaw_cron.AGENTS_MAP` (source unique)."""
    rows: list[dict[str, str]] = []
    for spec in oc.AGENTS_MAP:
        key = str(spec.get("key", ""))
        rows.append(
            {
                "key": key,
                "jobId": str(spec.get("jobId", "") or ""),
                "name": str(spec.get("name", "")),
                "role": str(spec.get("label", "")),
                "pole": (str(spec.get("pole", "")).lower() or "orchestration"),
                "dashboard_agent_id": str(spec.get("dashboard_agent_id", key)),
            }
        )
    return rows


@router.get("/openclaw/agents")
async def openclaw_agents(_username: str = Depends(get_current_username)):
    settings = get_settings()
    openclaw_dir = getattr(settings, "openclaw_dir", "/openclaw-data")

    jobs = _read_jobs(openclaw_dir)
    jobs_by_id = {j["id"]: j for j in jobs}

    result = []
    for agent in _supervision_rows_from_map():
        job_id = agent["jobId"]
        job = jobs_by_id.get(job_id, {}) if job_id else {}
        state = job.get("state", {})
        runs = _read_last_runs(openclaw_dir, job_id, 5) if job_id else []
        last_run = runs[-1] if runs else None

        result.append(
            {
                "key": agent["key"],
                "name": agent["name"],
                "role": agent["role"],
                "label": agent["role"],
                "pole": agent["pole"],
                "dashboard_agent_id": agent["dashboard_agent_id"],
                "jobId": job_id,
                "enabled": job.get("enabled", False),
                "schedule": job.get("schedule", {}).get("expr"),
                "status": state.get("lastRunStatus", "idle"),
                "consecutiveErrors": state.get("consecutiveErrors", 0),
                "lastError": state.get("lastError"),
                "lastRunAt": state.get("lastRunAtMs"),
                "nextRunAt": state.get("nextRunAtMs"),
                "lastDurationMs": state.get("lastDurationMs"),
                "lastSummary": last_run.get("summary") if last_run else None,
                "lastModel": last_run.get("model") if last_run else None,
                "lastTokens": last_run.get("usage") if last_run else None,
                "recentRuns": [
                    {
                        "ts": r.get("ts"),
                        "status": r.get("status"),
                        "durationMs": r.get("durationMs"),
                        "tokens": r.get("usage", {}).get("total_tokens") if r.get("usage") else None,
                        "summaryPreview": (r.get("summary") or "")[:200],
                    }
                    for r in runs
                ],
            }
        )

    return {"ok": True, "agents": result}


@router.get("/openclaw/agents/{job_id}/report")
async def openclaw_agent_report(
    job_id: str,
    _username: str = Depends(get_current_username),
):
    settings = get_settings()
    openclaw_dir = getattr(settings, "openclaw_dir", "/openclaw-data")
    runs = _read_last_runs(openclaw_dir, job_id, 1)
    if not runs:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Aucun run trouvé")
    return {"ok": True, "report": runs[-1]}


@router.get("/openclaw")
async def openclaw_status(_username: str = Depends(get_current_username)):
    settings = get_settings()
    openclaw_dir = getattr(settings, "openclaw_dir", "/openclaw-data")
    jobs = _read_jobs(openclaw_dir)
    ok_count = sum(1 for j in jobs if j.get("state", {}).get("lastRunStatus") == "ok")
    error_count = sum(1 for j in jobs if j.get("state", {}).get("consecutiveErrors", 0) > 0)
    return {
        "configured": True,
        "source": "file",
        "openclaw_dir": openclaw_dir,
        "total_jobs": len(jobs),
        "ok": ok_count,
        "errors": error_count,
    }
