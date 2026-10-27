"""Weekly tuning: move ranking weights, brief length and thresholds in the direction the ratings point."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .util import clamp, parse_dt

STEP = 0.15


def _group(r: dict[str, Any]) -> str:
    """Weights are per group (meeting, commitment, signal, deal_move, ...). Home sends both the item's kind and its group."""
    from .brief import KIND_GROUP
    return r.get("group") or KIND_GROUP.get(r.get("kind") or "", r.get("kind") or "other")


def tally(ratings: list[dict[str, Any]], key=lambda r: r.get("kind") or "other") -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = defaultdict(lambda: {"useful": 0, "not_useful": 0, "wrong": 0})
    for r in ratings:
        val = r.get("value")
        if val in ("useful", "not_useful", "wrong"):
            out[key(r)][val] += 1
    return dict(out)


def tune(config: dict[str, Any], ratings: list[dict[str, Any]], limits: dict[str, Any] | None = None,
         now: str | None = None) -> dict[str, Any]:
    """Each rating counts once: only ratings since the last tuning are read, and a weight never moves against what
    the ratings say (a weight below the floor is not raised by "not useful" taps)."""
    limits = limits or {"weight_min": 0.3, "weight_max": 2.0, "today_items_min": 3, "today_items_max": 25}
    since = parse_dt(config.get("tuned_at"))
    fresh = [r for r in ratings if r.get("kind") != "weekly_score" and
             (since is None or (parse_dt(r.get("at")) is not None and parse_dt(r.get("at")) > since))]
    weights = dict((config.get("weights") or {}))
    counts = tally(fresh, _group)
    changes: list[dict[str, Any]] = []
    for group, c in counts.items():
        n = c["useful"] + c["not_useful"] + c["wrong"]
        if n < 3 or group not in weights:
            continue
        net = (c["useful"] - c["not_useful"] - 2 * c["wrong"]) / n
        if abs(net) < 0.2:
            continue
        old = weights[group]
        new = round(clamp(old * (1 + STEP * (1 if net > 0 else -1) * min(1.0, abs(net) * 1.5)), limits["weight_min"], limits["weight_max"]), 2)
        if (net > 0 and new <= old) or (net < 0 and new >= old):
            continue  # at a limit, or a default below the floor: never move against the ratings
        weights[group] = new
        changes.append({"what": f"{group} weight", "from": old, "to": new,
                        "why": f"{c['useful']} useful, {c['not_useful']} not useful, {c['wrong']} wrong"})
    total = sum(c["useful"] + c["not_useful"] + c["wrong"] for c in counts.values())
    noise = sum(c["not_useful"] + c["wrong"] for c in counts.values())
    items = config.get("today_items", 8)
    if total >= 10 and noise / total > 0.30 and items > limits["today_items_min"]:
        changes.append({"what": "items in Today", "from": items, "to": items - 1, "why": f"{noise} of {total} items rated not useful or wrong"})
        items -= 1
    elif total >= 10 and noise / total < 0.08 and items < limits["today_items_max"]:
        useful_share = 1 - noise / total
        changes.append({"what": "items in Today", "from": items, "to": items + 1, "why": f"{useful_share:.0%} of items rated useful"})
        items += 1
    stale = tally(fresh).get("stale", {"useful": 0, "not_useful": 0, "wrong": 0})
    scale = config.get("dwell_scale", 1.0)
    sn = sum(stale.values())
    if sn >= 5 and (stale["not_useful"] + stale["wrong"]) / sn > 0.4:
        changes.append({"what": "stale-deal threshold", "from": scale, "to": round(min(2.0, scale * 1.2), 2), "why": "stale nudges came too early"})
        scale = round(min(2.0, scale * 1.2), 2)
    new_config = {**config, "weights": weights, "today_items": items, "dwell_scale": scale}
    if now:
        new_config["tuned_at"] = now
    note = _note(changes)
    return {"config": new_config, "changes": changes, "note": note, "counts": counts, "ratings_read": len(fresh)}


def _note(changes: list[dict[str, Any]]) -> str:
    if not changes:
        return "No changes this week."
    top = changes[0]
    direction = "more" if (isinstance(top["to"], (int, float)) and isinstance(top["from"], (int, float)) and top["to"] > top["from"]) else "fewer"
    thing = top["what"].replace(" weight", "")
    if top["what"].endswith("weight"):
        line = f"ant. now shows {direction} {thing.replace('_', ' ')} items because you rated them: {top['why']}."
    else:
        line = f"I changed {top['what']} from {top['from']} to {top['to']} because {top['why']}."
    if len(changes) > 1:
        line += f" Plus {len(changes) - 1} smaller change{'s' if len(changes) > 2 else ''}."
    return line
