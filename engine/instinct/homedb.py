"""ant. Home's database: read what the page and earlier runs stored, write fresh snapshots.

Layout (all private to the owner):
  snap/<doc>      written by ant. runs: config, brief, prep, pipeline, people, portfolio, lps,
                  drafts, proposals, commitments, inbound, scorecard, review
  state/items     written by the page: snoozes, done marks
  state/actions   written by the page: approvals and next steps for runs to apply
  ratings/<id>    written by the page, one per tap
  runs/<id>       written by ant. runs, one per run
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

from .util import dump, load

SNAP_DOCS = ["config", "brief", "prep", "pipeline", "people", "portfolio", "lps", "drafts", "proposals", "commitments",
             "inbound", "scorecard", "review", "asks", "digests", "directory", "notes"]
VOLATILE = ("as_of", "updated_at")
MAX_DOC_BYTES = 240 * 1024
BATCH_SIZE = 50


def _unwrap(raw: Any) -> tuple[dict[str, Any], int | None]:
    """ArtifactData saves documents as JSON files; accept both the bare body and a {data, version} wrapper."""
    if isinstance(raw, dict) and "data" in raw and isinstance(raw.get("data"), dict) and ("version" in raw or "id" in raw):
        return raw["data"], raw.get("version")
    if isinstance(raw, dict) and "__version" in raw:
        body = {k: v for k, v in raw.items() if k != "__version"}
        return body, raw.get("__version")
    return (raw if isinstance(raw, dict) else {}), None


def read_versions(path: str) -> dict[str, int]:
    """Versions of the documents a read saved. ArtifactData writes each document's body to a file and names its version
    only in the read's result ("brief  8810 bytes  version 3  .../snap/brief.json"). Accept a JSON map
    {"snap/brief": 3} or that result text pasted as is."""
    text = open(path, encoding="utf-8").read()
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return {str(k): int(v) for k, v in data.items() if isinstance(v, (int, float)) or str(v).isdigit()}
    except ValueError:
        pass
    out: dict[str, int] = {}
    for m in re.finditer(r'"([^"]+)"\s+\d+\s+bytes\s+version\s+(\d+)\s+"([^"]+)"', text):
        doc_id, version, file_path = m.group(1), int(m.group(2)), m.group(3)
        coll = os.path.basename(os.path.dirname(file_path))
        out[f"{coll}/{doc_id}"] = version
    return out


def read_home(folder: str | None, versions_path: str | None = None) -> dict[str, Any]:
    home: dict[str, Any] = {"snap": {}, "state": {}, "ratings": [], "versions": {}}
    if not versions_path and folder:
        for name in ("versions.txt", "versions.json"):
            if os.path.exists(os.path.join(folder, name)):
                versions_path = os.path.join(folder, name)  # the read step saves them here
                break
    if versions_path and os.path.exists(versions_path):
        home["versions"] = read_versions(versions_path)
    if not folder or not os.path.isdir(folder):
        return home
    for coll in ("snap", "state", "ratings", "runs"):
        cdir = os.path.join(folder, coll)
        if not os.path.isdir(cdir):
            continue
        for f in sorted(os.listdir(cdir)):
            if not f.endswith(".json"):
                continue
            body, version = _unwrap(load(os.path.join(cdir, f)))
            doc_id = f[:-5]
            if version is not None:
                home["versions"][f"{coll}/{doc_id}"] = version
            if coll == "ratings":
                home["ratings"].append({"id": doc_id, **body})
            elif coll == "runs":
                home.setdefault("runs", []).append({"id": doc_id, **body})
            else:
                home[coll][doc_id] = body
    return home


RECENCY_KEYS = ("applied_at", "at", "seen_at", "meeting_date", "due", "start", "last_touch", "last_contact", "stage_entered", "as_of")


def _recency(row: Any) -> str:
    if isinstance(row, dict):
        for k in RECENCY_KEYS:
            if row.get(k):
                return str(row[k])
    return ""


def _fit(doc_id: str, body: dict[str, Any]) -> dict[str, Any]:
    """Keep every document under the store's 256 KiB cap. Lists lose their tail (they are ranked); maps of items
    lose their OLDEST entries first, so a new promise or a new approval is never the one cut."""
    data = json.dumps(body, ensure_ascii=False, default=str)
    if len(data.encode()) <= MAX_DOC_BYTES:
        return body
    trimmed = dict(body)
    for key in ("people", "top", "history", "kpis", "deals", "companies", "items", "drafts", "lps", "cards", "passes"):
        val = trimmed.get(key)
        while val and len(json.dumps(trimmed, default=str).encode()) > MAX_DOC_BYTES:
            if isinstance(val, list):
                val = val[: max(1, int(len(val) * 0.8))]
            elif isinstance(val, dict):
                newest_first = sorted(val.items(), key=lambda kv: _recency(kv[1]), reverse=True)
                val = dict(newest_first[: max(1, int(len(val) * 0.8))])
            trimmed[key] = val
            if len(val) <= 1:
                break
    trimmed["trimmed"] = True
    return trimmed


def _same(a: Any, b: Any) -> bool:
    """True when two snapshots differ only in their timestamps, so the write can be skipped."""
    if not isinstance(a, dict) or not isinstance(b, dict):
        return False
    strip = lambda d: json.dumps({k: v for k, v in d.items() if k not in VOLATILE}, sort_keys=True, default=str)
    return strip(a) == strip(b)


def write_plan(snaps: dict[str, dict[str, Any]], home: dict[str, Any], out_dir: str) -> dict[str, Any]:
    folder = os.path.join(os.path.abspath(out_dir), "home")
    os.makedirs(folder, exist_ok=True)
    writes, skipped = [], []
    for doc_id, body in snaps.items():
        body = _fit(doc_id, body)
        path = dump(body, os.path.join(folder, f"snap__{doc_id}.json"))  # every snapshot is on disk, written or not
        if doc_id != "brief" and _same(json.loads(json.dumps(body, default=str)), (home.get("snap") or {}).get(doc_id)):
            skipped.append(doc_id)
            continue
        entry: dict[str, Any] = {"op": "set", "collection": "snap", "doc_id": doc_id, "file_path": path}
        version = (home.get("versions") or {}).get(f"snap/{doc_id}")
        if version is not None:
            entry["if_version"] = version
        writes.append(entry)
    batches = [writes[i:i + BATCH_SIZE] for i in range(0, len(writes), BATCH_SIZE)]
    plan = {"batches": [{"writes": b} for b in batches], "documents": len(writes), "skipped": skipped,
            "versions": {k[5:]: v for k, v in (home.get("versions") or {}).items() if k.startswith("snap/")},
            "note": "Call ArtifactData once per batch with action 'batch' and these writes. Entries without if_version create new documents."}
    dump(plan, os.path.join(folder, "batch.json"))
    return plan


def merge_map(old: dict[str, Any] | None, new: dict[str, Any], keep_keys: tuple[str, ...] = ("status", "applied_at", "done_at")) -> dict[str, Any]:
    out = dict(old or {})
    for k, v in new.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            kept = {kk: out[k][kk] for kk in keep_keys if kk in out[k] and out[k][kk] is not None}
            out[k] = {**v, **kept}
        else:
            out[k] = v
    return out


def add_to_plan(out_dir: str, doc_id: str) -> dict[str, Any]:
    """Put one snapshot (already on disk) into the batch, for a document the skill changed after the build."""
    folder = os.path.join(os.path.abspath(out_dir), "home")
    plan = load(os.path.join(folder, "batch.json"))
    path = os.path.join(folder, f"snap__{doc_id}.json")
    writes = [w for b in plan["batches"] for w in b["writes"] if not (w["collection"] == "snap" and w["doc_id"] == doc_id)]
    entry: dict[str, Any] = {"op": "set", "collection": "snap", "doc_id": doc_id, "file_path": path}
    if (plan.get("versions") or {}).get(doc_id) is not None:
        entry["if_version"] = plan["versions"][doc_id]
    writes.append(entry)
    plan["batches"] = [{"writes": writes[i:i + BATCH_SIZE]} for i in range(0, len(writes), BATCH_SIZE)]
    plan["documents"] = len(writes)
    plan["skipped"] = [d for d in plan.get("skipped") or [] if d != doc_id]
    dump(plan, os.path.join(folder, "batch.json"))
    return plan
