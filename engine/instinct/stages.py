"""Pipeline stages: defaults, CRM name mapping, dwell times."""

from __future__ import annotations

import os
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))


def ontology_path(name: str) -> str:
    return os.path.join(ROOT, "ontology", name)


def load(path: str | None = None) -> dict[str, Any]:
    from .util import load as _load
    data = _load(path or ontology_path("stages.json"))
    data["by_key"] = {s["key"]: s for s in data["stages"]}
    data["order"] = {s["key"]: i for i, s in enumerate(data["stages"])}
    return data


def map_stage(label: Any, stage_map: dict[str, Any], overrides: dict[str, str] | None = None) -> str:
    """Map a CRM stage label onto a stage key. Unknown labels fall back to screening."""
    if label is None:
        return "screening"
    text = str(label).strip().lower()
    if overrides and text in overrides:
        return overrides[text]
    if text in stage_map["by_key"]:
        return text
    for key, aliases in (stage_map.get("crm_aliases") or {}).items():
        if text == key.replace("_", " ") or text in aliases:
            return key
    for key, aliases in (stage_map.get("crm_aliases") or {}).items():
        if any(a in text for a in aliases if len(a) > 3):
            return key
    return "screening"


def stage_name(key: str, stage_map: dict[str, Any], crm_label: Any = None) -> str:
    if crm_label:
        return str(crm_label)
    return stage_map["by_key"].get(key, {}).get("name", key)


def is_active(key: str, stage_map: dict[str, Any]) -> bool:
    return bool(stage_map["by_key"].get(key, {}).get("active"))


def order(key: str, stage_map: dict[str, Any]) -> int:
    return stage_map["order"].get(key, 0)


def dwell(key: str, stage_map: dict[str, Any], scale: float = 1.0) -> int | None:
    d = stage_map["by_key"].get(key, {}).get("dwell_days")
    return None if d is None else int(round(d * scale))


def label(name: str | None, start: bool = True) -> str:
    """A CRM stage name in a sentence: "Term Sheet" reads "Term sheet" (or "term sheet" mid-sentence); "IC" stays "IC"."""
    words = str(name or "").split()
    out = [w if (w.isupper() and len(w) > 1) else w.lower() for w in words]
    if out and start and not (words[0].isupper() and len(words[0]) > 1):
        out[0] = out[0][:1].upper() + out[0][1:]
    return " ".join(out)
