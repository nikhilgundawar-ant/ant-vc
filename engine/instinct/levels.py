"""Infer the user's level from what their calendar and inbox look like. Setup shows it back for one tap."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

PATTERNS = {
    "board": re.compile(r"\bboard (meeting|call|prep|deck|pack)\b|\bboard\b", re.I),
    "lp": re.compile(r"\b(lp|limited partner|capital call|quarterly (letter|report)|fund (iii|ii|iv|3|2)|re-?up|annual meeting|agm|nav)\b", re.I),
    "finance": re.compile(r"\b(capital call|nav|audit|fund admin|k-?1|distribution|valuation|waterfall|management fee|carried interest|tax)\b", re.I),
    "first_meeting": re.compile(r"\b(intro|first call|first meeting|catch up|chat|<>|\bx\b)\b", re.I),
    "pitch": re.compile(r"\b(pitch|deck|raising|fundraise|our round|pre-seed|seed round|series a)\b", re.I),
    "platform": re.compile(r"\b(hiring|intro request|talent|recruit|event|community|customer intro|founder ask|portfolio ask|office hours)\b", re.I),
    "screening": re.compile(r"\b(market map|landscape|sourcing|screening|research|cohort|thesis)\b", re.I),
    "partner_meeting": re.compile(r"\b(partner meeting|ic|investment committee|monday meeting)\b", re.I),
}


def infer(bundle: dict[str, Any], user_email: str) -> dict[str, Any]:
    user_email = (user_email or "").lower()
    c: Counter[str] = Counter()
    for ev in (bundle.get("events") or []):
        emails = [(a.get("email") or "").lower() for a in (ev.get("attendees") or [])]
        if user_email and user_email not in emails:
            continue
        title = ev.get("title") or ""
        for key, rx in PATTERNS.items():
            if rx.search(title):
                c[f"event_{key}"] += 1
    for th in (bundle.get("threads") or []):
        emails = [(p.get("email") or "").lower() for p in (th.get("participants") or [])]
        if user_email and user_email not in emails:
            continue
        subject = th.get("subject") or ""
        for key, rx in PATTERNS.items():
            if rx.search(subject):
                c[f"mail_{key}"] += 1
    title = " ".join((m.get("title") or "") for m in ((bundle.get("firm") or {}).get("members") or [])
                     if (m.get("email") or "").lower() == user_email).lower()
    scores = {
        # Everyone on the deal team sits in the Monday partner meeting, so it counts the same for all three.
        "partner": 3 * c["event_board"] + c["event_partner_meeting"] + 2 * c["mail_lp"] + c["event_lp"] + 0.5 * c["mail_pitch"],
        "principal": 2 * c["event_board"] + c["event_partner_meeting"] + 1.5 * c["event_first_meeting"] + c["mail_pitch"],
        "associate": c["event_partner_meeting"] + 2.5 * c["event_first_meeting"] + 1.2 * c["mail_pitch"] + c["event_screening"],
        "analyst": 1.5 * c["mail_pitch"] + 3 * c["mail_screening"] + 2 * c["event_screening"] + 0.3 * c["event_first_meeting"],
        "platform": 3 * c["mail_platform"] + 2 * c["event_platform"],
        "finance": 3 * c["mail_finance"] + 2 * c["event_lp"] + 2 * c["mail_lp"] + c["event_board"] * 0.5,
    }
    hints = {"partner": r"\b(partner|gp|general partner|managing)\b", "principal": r"\b(principal|vp|vice president|director)\b",
             "associate": r"\bassociate\b", "analyst": r"\banalyst\b", "platform": r"\b(platform|community|talent)\b",
             "finance": r"\b(cfo|finance|controller|ir|investor relations|coo)\b"}
    for level, rx in hints.items():
        if re.search(rx, title):
            scores[level] += 10
    members = [m for m in ((bundle.get("firm") or {}).get("members") or []) if m.get("email")]
    if len(members) == 1 and str(members[0].get("email")).lower() == user_email:
        # Nobody else at the firm: whatever the calendar looks like, this person does every job.
        return {"level": "solo_gp", "confidence": 0.9, "scores": {k: round(v, 1) for k, v in scores.items()},
                "evidence": dict(c.most_common(8)), "options": ["solo_gp", "partner", "principal"], "recommend": True}
    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    best, runner = ranked[0], ranked[1]
    confidence = 0.5 if best[1] == 0 else min(0.95, 0.5 + (best[1] - runner[1]) / (best[1] + 1) / 2)
    return {"level": best[0], "confidence": round(confidence, 2), "scores": {k: round(v, 1) for k, v in ranked},
            # Options are the levels the mail and calendar give evidence for (at least two, so there is a choice);
            # a level that scored nothing is never offered as if it were a guess.
            "evidence": dict(c.most_common(8)),
            "options": [k for i, (k, v) in enumerate(ranked[:3]) if i < 2 or (v > 0 and v >= 0.1 * (best[1] or 1))],
            "recommend": confidence >= 0.7}
