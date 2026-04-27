import json
import os
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.deps import get_current_username

router = APIRouter(prefix="/api/supervision", tags=["supervision"])

AGENTS_MAP = {
    "marlene":     {"jobId": "fdfb0543-81a7-4eb7-86c7-9eaf7b1f5378", "name": "Marlène",  "role": "Head of Research",  "pole": "Recherche"},
    "gaston":      {"jobId": "TON_ID_GASTON",                         "name": "Gaston",   "role": "SEO Analyst",        "pole": "Recherche"},
    "marcel_x":    {"jobId": "5d4ed714-2ba8-40be-becb-fa4670b92f97", "name": "Marcel",   "role": "Veille X Ecom",      "pole": "Intelligence"},
    "marcel_yt":   {"jobId": "d415271f-e72c-4986-8b3c-f5d57615a8e6", "name": "Marcel",   "role": "Veille YouTube",     "pole": "Intelligence"},
    "edith_intel": {"jobId": "3e203c26-b452-47fc-b8fb-ff0c2df2bb41", "name": "Édith",    "role": "Synthèse Intel",     "pole": "Intelligence"},
    "edith_pod":   {"jobId": "5782f709-a956-4326-aa89-cf0f827b747b", "name": "Édith",    "role": "Veille POD X",       "pole": "Intelligence"},
    "yvon":        {"jobId": "2b2ba93c-032b-4ff1-aed7-e3f1593cd952", "name": "Yvon",     "role": "Chief of Staff",     "pole": "Orchestration"},
}


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


@router.get("/openclaw/agents")
async def openclaw_agents(_username: str = Depends(get_current_username)):
    settings = get_settings()
    openclaw_dir = getattr(settings, "openclaw_dir", "/openclaw-data")

    jobs = _read_jobs(openclaw_dir)
    jobs_by_id = {j["id"]: j for j in jobs}

    result = []
    for key, agent in AGENTS_MAP.items():
        job_id = agent["jobId"]
        job = jobs_by_id.get(job_id, {})
        state = job.get("state", {})
        runs = _read_last_runs(openclaw_dir, job_id, 5)
        last_run = runs[-1] if runs else None

        result.append({
            "key": key,
            "name": agent["name"],
            "role": agent["role"],
            "pole": agent["pole"],
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
        })

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
