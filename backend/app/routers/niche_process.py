from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_username
from app.models import NicheProcessStateModel
from app.niche_process_catalog import (
    RED_FLAG_DEFS,
    SCORE_BUSINESS_KEYS,
    SCORE_SEO_KEYS,
    all_catalog_item_keys,
    catalog_payload,
    default_state_payload,
)
from app.services.wire_messages import (
    WireConversationNotFound,
    fetch_messages_for_conversation,
    wire_timeline_sort_key,
)
from app.services.wire_resolve import resolve_conversation_id_for_agent

router = APIRouter(prefix="/api/niche-process", tags=["niche-process"])

VALID_ITEM_KEYS = frozenset(all_catalog_item_keys())
_WIRE_ID_KEYS = frozenset({"marlene_conversation_id", "gaston_conversation_id"})
_MAX_WIRE_CONV_ID_LEN = 120


def _deep_merge(base: dict, patch: dict) -> dict:
    out = dict(base)
    for k, v in patch.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _get_row(db: Session) -> NicheProcessStateModel:
    row = db.get(NicheProcessStateModel, 1)
    if not row:
        row = NicheProcessStateModel(id=1, payload=default_state_payload())
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


def _normalize_wire_conv_id(val: Any) -> str | None:
    if val is None:
        return None
    if isinstance(val, str):
        s = " ".join(val.split())
        if not s:
            return None
        if len(s) > _MAX_WIRE_CONV_ID_LEN:
            return s[:_MAX_WIRE_CONV_ID_LEN]
        return s
    return None


def _sanitize_wire_block(merged: dict[str, Any]) -> None:
    w = merged.get("wire") if isinstance(merged.get("wire"), dict) else {}
    merged["wire"] = {
        "marlene_conversation_id": _normalize_wire_conv_id(
            w.get("marlene_conversation_id")
        ),
        "gaston_conversation_id": _normalize_wire_conv_id(
            w.get("gaston_conversation_id")
        ),
    }


def _ensure_payload_shape(p: dict[str, Any]) -> dict[str, Any]:
    d = default_state_payload()
    merged = _deep_merge(d, p)
    # Prune items_checked to valid keys only
    ic = merged.get("items_checked") or {}
    merged["items_checked"] = {k: bool(v) for k, v in ic.items() if k in VALID_ITEM_KEYS}
    _sanitize_wire_block(merged)
    return merged


def _avg(nums: list[float | None]) -> float | None:
    vals = [n for n in nums if n is not None and isinstance(n, (int, float))]
    if len(vals) != len(nums):
        return None
    return sum(vals) / len(nums)


def _compute(state: dict[str, Any]) -> dict[str, Any]:
    sb = state.get("scores_business") or {}
    ss = state.get("scores_seo") or {}
    b_list = [sb.get(k) for k in SCORE_BUSINESS_KEYS]
    s_list = [ss.get(k) for k in SCORE_SEO_KEYS]
    for i, v in enumerate(b_list):
        if v is not None:
            b_list[i] = float(v)
    for i, v in enumerate(s_list):
        if v is not None:
            s_list[i] = float(v)
    score_marlene = _avg(b_list)  # type: ignore[arg-type]
    score_gaston = _avg(s_list)  # type: ignore[arg-type]
    score_final: float | None = None
    if score_marlene is not None and score_gaston is not None:
        score_final = score_marlene * 0.6 + score_gaston * 0.4
    verdict: Literal["pending", "go", "borderline", "nogo"] = "pending"
    if score_final is not None:
        if score_final >= 8.0:
            verdict = "go"
        elif score_final >= 6.0:
            verdict = "borderline"
        else:
            verdict = "nogo"
    return {
        "score_marlene": score_marlene,
        "score_gaston": score_gaston,
        "score_final": score_final,
        "verdict": verdict,
    }


class WireIdsPatch(BaseModel):
    marlene_conversation_id: str | None = None
    gaston_conversation_id: str | None = None


class NicheProcessPatch(BaseModel):
    items_checked: dict[str, bool] | None = None
    handoff: dict[str, str] | None = None
    scores_business: dict[str, float | None] | None = None
    scores_seo: dict[str, float | None] | None = None
    red_flags: dict[str, bool] | None = None
    notes: dict[str, str] | None = None
    wire: WireIdsPatch | None = None


@router.get("")
def get_niche_process(
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    row = _get_row(db)
    state = _ensure_payload_shape(row.payload or {})
    return {
        **catalog_payload(),
        "state": state,
        "computed": _compute(state),
    }


@router.patch("")
def patch_niche_process(
    body: NicheProcessPatch,
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    row = _get_row(db)
    state = _ensure_payload_shape(row.payload or {})
    patch: dict[str, Any] = body.model_dump(exclude_none=True)
    if "items_checked" in patch and patch["items_checked"]:
        merged_ic = dict(state.get("items_checked") or {})
        for k, v in patch["items_checked"].items():
            if k in VALID_ITEM_KEYS:
                merged_ic[k] = bool(v)
        patch["items_checked"] = merged_ic
    if "scores_business" in patch and patch["scores_business"]:
        for k in list(patch["scores_business"].keys()):
            if k not in SCORE_BUSINESS_KEYS:
                del patch["scores_business"][k]
    if "scores_seo" in patch and patch["scores_seo"]:
        for k in list(patch["scores_seo"].keys()):
            if k not in SCORE_SEO_KEYS:
                del patch["scores_seo"][k]
    if "red_flags" in patch and patch["red_flags"]:
        allowed = {d["key"] for d in RED_FLAG_DEFS}
        for k in list(patch["red_flags"].keys()):
            if k not in allowed:
                del patch["red_flags"][k]
    if "wire" in patch and patch["wire"] is not None:
        cur = dict(state.get("wire") or {})
        raw = patch["wire"] if isinstance(patch["wire"], dict) else {}
        for k in _WIRE_ID_KEYS:
            if k in raw:
                cur[k] = _normalize_wire_conv_id(raw.get(k))
        patch["wire"] = cur
    state = _deep_merge(state, patch)
    state = _ensure_payload_shape(state)
    row.payload = state
    db.add(row)
    db.commit()
    db.refresh(row)
    cat = catalog_payload()
    return {
        **cat,
        "state": state,
        "computed": _compute(state),
    }


@router.get("/wire-feed")
def get_niche_process_wire_feed(
    _username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    row = _get_row(db)
    state = _ensure_payload_shape(row.payload or {})
    wire = state.get("wire") or {}
    ml = (wire.get("marlene_conversation_id") or "").strip() or (
        resolve_conversation_id_for_agent(db, "marlene") or ""
    )
    ga = (wire.get("gaston_conversation_id") or "").strip() or (
        resolve_conversation_id_for_agent(db, "gaston") or ""
    )
    items: list[dict[str, Any]] = []
    warnings: list[str] = []

    for lane, cid in (("marlene", ml), ("gaston", ga)):
        if not cid:
            continue
        try:
            msgs = fetch_messages_for_conversation(db, cid)
            for m in msgs:
                row_item = dict(m)
                row_item["lane"] = lane
                row_item["wire_conversation_id"] = cid
                items.append(row_item)
        except WireConversationNotFound as e:
            warnings.append(f"{lane}: {e.detail}")

    items.sort(key=wire_timeline_sort_key)
    return {
        "items": items,
        "configured": {"marlene": bool(ml), "gaston": bool(ga)},
        "warnings": warnings,
    }
