"""Read/write Nerve .md files under OPENCLAW_DIR (filesystem mode)."""

from __future__ import annotations

import json
from pathlib import Path

from app.config import Settings, get_settings
from app.workflow_phases import NERVE_LABELS


class NervePathError(Exception):
    """Invalid or unsafe path configuration."""


def _parse_agent_paths(raw: str) -> dict[str, str]:
    if not (raw or "").strip():
        return {}
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as e:
        raise NervePathError(f"OPENCLAW_NERVE_AGENT_PATHS is not valid JSON: {e}") from e
    if not isinstance(obj, dict):
        raise NervePathError("OPENCLAW_NERVE_AGENT_PATHS must be a JSON object")
    out: dict[str, str] = {}
    for k, v in obj.items():
        if isinstance(k, str) and isinstance(v, str) and k.strip():
            rel = v.strip().replace("\\", "/").strip("/")
            if ".." in rel.split("/"):
                raise NervePathError(f"Path for agent {k!r} must not contain '..'")
            out[k.strip()] = rel
    return out


def _openclaw_root(settings: Settings) -> Path:
    return Path(settings.openclaw_dir).resolve()


def _is_under(root: Path, p: Path) -> bool:
    try:
        p.relative_to(root)
        return True
    except ValueError:
        return False


def agent_workspace_rel(settings: Settings, agent_id: str) -> str | None:
    paths = _parse_agent_paths(settings.openclaw_nerve_agent_paths)
    if agent_id in paths:
        return paths[agent_id]
    tmpl = (settings.openclaw_nerve_path_template or "").strip()
    if tmpl:
        try:
            rel = tmpl.format(agent_id=agent_id).strip().replace("\\", "/").strip("/")
        except KeyError as e:
            raise NervePathError(
                "OPENCLAW_NERVE_PATH_TEMPLATE may only use {agent_id} as placeholder"
            ) from e
        if ".." in rel.split("/"):
            raise NervePathError("OPENCLAW_NERVE_PATH_TEMPLATE must not contain '..'")
        return rel
    return None


def resolve_nerve_file(settings: Settings, agent_id: str, slug: str) -> Path:
    if slug not in NERVE_LABELS:
        raise NervePathError(f"Unknown slug: {slug}")
    rel = agent_workspace_rel(settings, agent_id)
    if rel is None:
        raise NervePathError(
            "No workspace path for this agent: set OPENCLAW_NERVE_AGENT_PATHS "
            "or OPENCLAW_NERVE_PATH_TEMPLATE"
        )
    root = _openclaw_root(settings)
    agent_dir = (root / rel).resolve()
    if not _is_under(root, agent_dir):
        raise NervePathError("Resolved agent directory escapes OPENCLAW_DIR")
    filename = NERVE_LABELS[slug]
    file_path = (agent_dir / filename).resolve()
    if not _is_under(root, file_path):
        raise NervePathError("Resolved file path escapes OPENCLAW_DIR")
    return file_path


def read_nerve_file(agent_id: str, slug: str, settings: Settings | None = None) -> str:
    s = settings or get_settings()
    path = resolve_nerve_file(s, agent_id, slug)
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def write_nerve_file(agent_id: str, slug: str, content: str, settings: Settings | None = None) -> None:
    s = settings or get_settings()
    path = resolve_nerve_file(s, agent_id, slug)
    root = _openclaw_root(s)
    parent = path.parent.resolve()
    if not _is_under(root, parent):
        raise NervePathError("Parent directory escapes OPENCLAW_DIR")
    if not parent.is_dir():
        parent.mkdir(parents=True, exist_ok=True)
        parent_resolved = parent.resolve()
        if not _is_under(root, parent_resolved):
            raise NervePathError("Created parent directory escapes OPENCLAW_DIR")
    path.write_text(content, encoding="utf-8", newline="\n")
