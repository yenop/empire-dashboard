"""Lecture des fichiers cron OpenClaw (jobs.json, runs/*.jsonl) — partagé supervision + wire."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from app.config import get_settings

# Liens fil OpenClaw (key) → agent dashboard (`agents.id`). Mettre à jour jobId "gaston" quand le cron existera.
AGENTS_MAP: list[dict[str, Any]] = [
    {
        "key": "marlene",
        "dashboard_agent_id": "marlene",
        "jobId": "fdfb0543-81a7-4eb7-86c7-9eaf7b1f5378",
        "name": "Marlène",
        "label": "Recherche niches",
        "pole": "recherche",
    },
    {
        "key": "gaston",
        "dashboard_agent_id": "gaston",
        "jobId": "5d62c3e8-cd0d-4dad-a768-227eee28c757",
        "name": "Gaston",
        "label": "Analyse SEO",
        "pole": "recherche",
    },
    {
        "key": "colette",
        "jobId": "2eef9fda-00e5-4223-80db-8bbadeab0a69",
        "name": "Colette",
        "label": "Brief UI/UX",
        "pole": "production",
    },
    {
        "key": "marcel_x",
        "dashboard_agent_id": "marcel",
        "jobId": "5d4ed714-2ba8-40be-becb-fa4670b92f97",
        "name": "Marcel",
        "label": "Veille X ecom",
        "pole": "intelligence",
    },
    {
        "key": "marcel_yt",
        "dashboard_agent_id": "marcel",
        "jobId": "d415271f-e72c-4986-8b3c-f5d57615a8e6",
        "name": "Marcel",
        "label": "Veille YouTube",
        "pole": "intelligence",
    },
    {
        "key": "edith_intel",
        "dashboard_agent_id": "edith",
        "jobId": "3e203c26-b452-47fc-b8fb-ff0c2df2bb41",
        "name": "Édith",
        "label": "Synthèse Intel",
        "pole": "intelligence",
    },
    {
        "key": "edith_pod",
        "dashboard_agent_id": "edith",
        "jobId": "5782f709-a956-4326-aa89-cf0f827b747b",
        "name": "Édith",
        "label": "Veille POD X",
        "pole": "intelligence",
    },
    {
        "key": "yvon",
        "dashboard_agent_id": "yvon",
        "jobId": "2b2ba93c-032b-4ff1-aed7-e3f1593cd952",
        "name": "Yvon",
        "label": "Carte blanche nuit",
        "pole": "expansion",
    },
]


def oc_root() -> Path:
    return Path(get_settings().openclaw_dir).resolve()


def norm_uuid(s: str) -> str:
    s = (s or "").strip()
    if not s:
        return ""
    try:
        return str(UUID(s))
    except ValueError:
        return s


def load_json_file(path: Path) -> Any | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return None


def load_jobs_list(root: Path) -> list[dict[str, Any]]:
    data = load_json_file(root / "cron" / "jobs.json")
    if data is None:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict) and "jobs" in data and isinstance(data["jobs"], list):
        return [x for x in data["jobs"] if isinstance(x, dict)]
    if isinstance(data, dict) and "crons" in data and isinstance(data["crons"], list):
        return [x for x in data["crons"] if isinstance(x, dict)]
    return []


def job_id_of(rec: dict[str, Any]) -> str:
    for k in ("id", "jobId", "job_id", "uuid"):
        v = rec.get(k)
        if isinstance(v, str) and v.strip():
            return norm_uuid(v.strip())
    return ""


def find_job_rec(jobs: list[dict[str, Any]], job_id: str) -> dict[str, Any] | None:
    if not job_id:
        return None
    for rec in jobs:
        if job_id_of(rec) and job_id_of(rec) == norm_uuid(job_id):
            return rec
    return None


def parse_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    out: list[dict[str, Any]] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(d, dict):
            out.append(d)
    return out


def run_status(r: dict[str, Any]) -> str:
    s = str(r.get("status", "") or r.get("lastStatus", "")).lower().strip()
    if s in ("ok", "success", "succeeded", "done"):
        return "ok"
    if s in ("error", "failed", "failure", "err"):
        return "error"
    if s in ("disabled", "skipped", "idle"):
        return "idle"
    if s:
        return s
    return "unknown"


def consecutive_errors(rec: dict[str, Any] | None) -> int:
    if not rec:
        return 0
    for k in ("consecutiveErrors", "consecutive_errors", "consecutiveError"):
        v = rec.get(k)
        if isinstance(v, int) and v >= 0:
            return v
        if isinstance(v, str) and v.isdigit():
            return int(v)
    return 0


def usage_tokens(usage: Any) -> int | None:
    if not isinstance(usage, dict):
        return None
    tot = usage.get("total_tokens") or usage.get("total")
    if isinstance(tot, int):
        return tot
    a = usage.get("input_tokens")
    b = usage.get("output_tokens")
    if isinstance(a, int) and isinstance(b, int):
        return a + b
    return None


def is_job_enabled(rec: dict[str, Any]) -> bool:
    e = rec.get("enabled", True)
    if e is False:
        return False
    if isinstance(e, str) and e.lower() in ("false", "0", "no", "off"):
        return False
    return True


def _run_ts(r: dict[str, Any]) -> str:
    return str(r.get("ts") or r.get("time") or r.get("at") or "")


def _parse_ts_sort_key(s: str) -> float:
    if not s:
        return 0.0
    s = (s or "").strip()
    try:
        t = s.replace("Z", "+00:00") if s.endswith("Z") else s
        return datetime.fromisoformat(t).timestamp()
    except (ValueError, OSError, TypeError):
        return 0.0


def spec_for_job_id(jid: str) -> dict[str, Any] | None:
    for s in AGENTS_MAP:
        if norm_uuid(str(s.get("jobId", ""))) == jid:
            return s
    return None


def dashboard_agent_id_for_job(jid: str) -> str | None:
    spec = spec_for_job_id(jid)
    if not spec:
        return None
    dash = spec.get("dashboard_agent_id")
    if isinstance(dash, str) and dash.strip():
        return dash.strip()
    key = spec.get("key")
    if isinstance(key, str) and key.strip():
        return key.strip()
    return None


def first_openclaw_job_id_for_dashboard_agent(dashboard_agent_id: str) -> str | None:
    """Premier job OpenClaw avec UUID non vide pour cet `agents.id` (ordre AGENTS_MAP)."""
    for s in AGENTS_MAP:
        if str(s.get("dashboard_agent_id", "")) != dashboard_agent_id:
            continue
        jid = norm_uuid(str(s.get("jobId", "")))
        if jid:
            return jid
    return None


def agent_entry(root: Path, spec: dict[str, Any], jobs: list[dict[str, Any]]) -> dict[str, Any]:
    jid = norm_uuid(str(spec.get("jobId", "")))
    if not jid:
        return {
            "key": spec.get("key"),
            "name": spec.get("name"),
            "label": spec.get("label"),
            "pole": spec.get("pole"),
            "jobId": None,
            "status": "not_configured",
            "consecutiveErrors": 0,
            "lastRun": None,
            "job": None,
        }
    jrec = find_job_rec(jobs, jid)
    runs_path = root / "cron" / "runs" / f"{jid}.jsonl"
    all_runs = parse_jsonl(runs_path)
    last: dict[str, Any] | None = all_runs[-1] if all_runs else None
    st = "idle"
    if jrec and not is_job_enabled(jrec):
        st = "disabled"
    elif last:
        st = run_status(last)
    elif jrec and jrec.get("lastRunStatus"):
        st = run_status({"status": str(jrec.get("lastRunStatus"))})
    ce = consecutive_errors(jrec) if jrec else 0
    last_out = None
    if last:
        last_out = {
            "ts": _run_ts(last),
            "status": run_status(last),
            "summary": last.get("summary") or last.get("message") or "",
            "usage": last.get("usage") if isinstance(last.get("usage"), dict) else {},
            "tokens": usage_tokens(last.get("usage")),
            "model": last.get("model"),
            "durationMs": last.get("durationMs") or last.get("duration_ms"),
        }
    job_out = None
    if jrec:
        job_out = {
            "id": job_id_of(jrec) or jid,
            "enabled": jrec.get("enabled", True),
            "schedule": jrec.get("schedule") or jrec.get("cron") or jrec.get("spec"),
            "lastRunStatus": jrec.get("lastRunStatus") or jrec.get("last_run_status"),
        }
    return {
        "key": spec.get("key"),
        "name": spec.get("name"),
        "label": spec.get("label"),
        "pole": spec.get("pole"),
        "jobId": jid,
        "status": st,
        "consecutiveErrors": ce,
        "lastRun": last_out,
        "job": job_out,
    }


def build_wire_conversations() -> list[dict[str, Any]] | None:
    """Fils = un fichier cron/runs/{jobId}.jsonl. Retourne None si répertoire OpenClaw indisponible."""
    root = oc_root()
    if not root.exists() or not root.is_dir():
        return None
    items: list[dict[str, Any]] = []
    known_ids: set[str] = set()
    for spec in AGENTS_MAP:
        jid = norm_uuid(str(spec.get("jobId", "")))
        if not jid:
            continue
        path = root / "cron" / "runs" / f"{jid}.jsonl"
        known_ids.add(jid)
        runs = parse_jsonl(path)
        last = runs[-1] if runs else None
        body = (last.get("summary") or last.get("message") or "") if last else ""
        preview = (body[:160] + "…") if len(body) > 160 else body
        last_ts = _run_ts(last) if last else ""
        ak = spec.get("key")
        items.append(
            {
                "id": jid,
                "title": f"{spec['name']} — {spec['label']}",
                "created_at": last_ts or None,
                "message_count": len(runs),
                "preview": preview,
                "source": "openclaw",
                "agent_key": ak,
                "last_message_at": last_ts or None,
                "last_is_broadcast": False,
                "last_pole": (spec.get("pole") or "orchestration"),
                "last_from_agent_id": ak,
                "last_to_agent_id": "dashboard",
            }
        )

    runs_dir = root / "cron" / "runs"
    if runs_dir.is_dir():
        for p in runs_dir.glob("*.jsonl"):
            nid = norm_uuid(p.stem)
            if not nid or nid in known_ids:
                continue
            runs = parse_jsonl(p)
            last = runs[-1] if runs else None
            body = (last.get("summary") or last.get("message") or "") if last else ""
            preview = (body[:160] + "…") if len(body) > 160 else body
            last_ts = _run_ts(last) if last else ""
            ex_spec = spec_for_job_id(nid)
            ex_pole = (ex_spec or {}).get("pole") or "orchestration"
            ex_key = (ex_spec or {}).get("key")
            items.append(
                {
                    "id": nid,
                    "title": f"OpenClaw job {nid[:8]}…",
                    "created_at": last_ts or None,
                    "message_count": len(runs),
                    "preview": preview,
                    "source": "openclaw",
                    "agent_key": None,
                    "last_message_at": last_ts or None,
                    "last_is_broadcast": False,
                    "last_pole": ex_pole,
                    "last_from_agent_id": ex_key,
                    "last_to_agent_id": "dashboard",
                }
            )
            known_ids.add(nid)

    items.sort(key=lambda it: _parse_ts_sort_key(it.get("created_at") or ""), reverse=True)
    return items


def wire_messages_for_job(job_id: str) -> list[dict[str, Any]] | None:
    """Messages = une ligne .jsonl = un « run ». None = volume OpenClaw indisponible (fallback DB)."""
    root = oc_root()
    if not root.exists() or not root.is_dir():
        return None
    jid = norm_uuid(job_id)
    if not jid:
        return None
    path = root / "cron" / "runs" / f"{jid}.jsonl"
    if not path.is_file():
        return []
    runs = parse_jsonl(path)
    spec = spec_for_job_id(jid)
    agent_key = (spec or {}).get("key") or "openclaw"
    out: list[dict[str, Any]] = []
    for i, r in enumerate(runs):
        body = (r.get("summary") or r.get("message") or "").strip() or f"[{run_status(r)}] (pas de texte)"
        ts = _run_ts(r)
        meta: dict[str, Any] = {
            "status": run_status(r),
            "model": r.get("model"),
        }
        tok = usage_tokens(r.get("usage"))
        if tok is not None:
            meta["tokens"] = tok
        ex = r.get("durationMs")
        if ex is None:
            ex = r.get("duration_ms")
        if ex is not None:
            meta["durationMs"] = ex
        out.append(
            {
                "id": f"{jid}-{i + 1}",
                "from_agent_id": agent_key,
                "to_agent_id": "dashboard",
                "body": body,
                "created_at": ts if ts else None,
                "source": "openclaw",
                "meta": meta,
            }
        )
    # Dernier run = fin du fichier = plus récent
    return list(reversed(out))
