"""Supervision OpenClaw : lecture des fichiers cron (volume monté), sans appel HTTP au gateway."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import get_settings
from app.deps import get_current_username
from app.services import openclaw_cron as oc

router = APIRouter(prefix="/api/supervision", tags=["supervision"])


@router.get("/openclaw")
def openclaw_status(_username: str = Depends(get_current_username)) -> dict[str, Any]:
    """Statut global issu de cron/jobs.json (compte jobs + dernier statut connu)."""
    root = oc.oc_root()
    settings = get_settings()
    if not root.exists() or not root.is_dir():
        return {
            "configured": False,
            "source": "filesystem",
            "message": "OPENCLAW_DIR absente ou non montée. Montez le répertoire host OpenClaw (ex. /home/ubuntu/.openclaw) en :ro.",
            "openclaw_dir": str(settings.openclaw_dir),
        }
    jobs = oc.load_jobs_list(root)
    by_last: dict[str, int] = {"ok": 0, "error": 0, "other": 0}
    for rec in jobs:
        lrs = rec.get("lastRunStatus") or rec.get("last_run_status")
        s = (str(lrs) if lrs is not None else "").lower()
        if s in ("ok", "success", "succeeded", "done"):
            by_last["ok"] = by_last.get("ok", 0) + 1
        elif s in ("error", "failed", "failure"):
            by_last["error"] = by_last.get("error", 0) + 1
        elif s:
            by_last["other"] = by_last.get("other", 0) + 1

    if not jobs:
        return {
            "configured": True,
            "source": "filesystem",
            "openclaw_dir": str(settings.openclaw_dir),
            "directory_exists": True,
            "jobs_file": False,
            "jobs_in_file": 0,
            "jobs_enabled": 0,
            "last_run_status_counts": by_last,
            "message": "Aucun cron dans cron/jobs.json (fichier absent ou vide).",
        }

    en_count = sum(1 for rec in jobs if oc.is_job_enabled(rec))
    return {
        "configured": True,
        "source": "filesystem",
        "openclaw_dir": str(settings.openclaw_dir),
        "directory_exists": True,
        "jobs_file": True,
        "jobs_in_file": len(jobs),
        "jobs_enabled": en_count,
        "last_run_status_counts": by_last,
    }


@router.get("/openclaw/agents")
def openclaw_agents(_username: str = Depends(get_current_username)) -> dict[str, Any]:
    """Statut + dernier rapport de chaque agent mappé."""
    root = oc.oc_root()
    if not root.exists() or not root.is_dir():
        return {
            "configured": False,
            "source": "filesystem",
            "message": "OPENCLAW_DIR absente ou non montée",
            "agents": [],
        }
    jobs = oc.load_jobs_list(root)
    agents = [oc.agent_entry(root, s, jobs) for s in oc.AGENTS_MAP]
    return {
        "configured": True,
        "source": "filesystem",
        "openclaw_dir": str(get_settings().openclaw_dir),
        "agents": agents,
    }


@router.get("/openclaw/agents/{job_id}/report")
def openclaw_agent_report(
    job_id: str, _username: str = Depends(get_current_username)
) -> dict[str, Any]:
    """Dernier rapport + historique des runs (fichier .jsonl)."""
    root = oc.oc_root()
    jid = oc.norm_uuid(job_id)
    if not jid:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="job_id invalide ou non configuré (Gaston : id à renseigner dans AGENTS_MAP)",
        )
    if not root.exists() or not root.is_dir():
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OPENCLAW_DIR absente",
        )
    spec = oc.spec_for_job_id(jid)
    path = root / "cron" / "runs" / f"{jid}.jsonl"
    if not path.is_file():
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Aucun fichier de runs pour ce job")
    if spec is None:
        spec = {
            "key": "unknown",
            "name": "OpenClaw",
            "label": f"Job {jid[:8]}…",
        }
    all_runs = oc.parse_jsonl(path)
    runs: list[dict[str, Any]] = []
    for r in reversed(all_runs):
        u = r.get("usage")
        if not isinstance(u, dict):
            u = {}
        runs.append(
            {
                "ts": r.get("ts") or r.get("time"),
                "status": oc.run_status(r),
                "summary": r.get("summary") or r.get("message") or "",
                "usage": u,
                "tokens": oc.usage_tokens(u),
                "model": r.get("model"),
                "durationMs": r.get("durationMs") or r.get("duration_ms"),
            }
        )
    latest = runs[0] if runs else None
    return {
        "jobId": jid,
        "key": spec.get("key"),
        "name": spec.get("name"),
        "label": spec.get("label"),
        "latest": latest,
        "runs": runs,
    }
