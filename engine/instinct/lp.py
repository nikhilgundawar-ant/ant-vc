"""LP watch: who is due a touch before the re-up decision, and the quarterly letter checklist."""

from __future__ import annotations

import re
from datetime import timedelta
from typing import Any

from .util import fmt_short_date, money, norm_email, parse_date, sid

LETTER_SECTIONS = ["Fund summary", "Portfolio highlights", "New investments", "Follow-ons and markdowns", "Exits",
                   "Pipeline and market", "Asks"]
WINDOW_TOUCH_DAYS = 45
DEFAULT_TOUCH_DAYS = 90
WINDOW_LEAD_DAYS = 90
WINDOW_URGENT_DAYS = 30


def last_touch(ctx: dict[str, Any], lp: dict[str, Any]):
    """Latest interaction with any of the LP's contacts, or the stored last_touch, whichever is newer."""
    stored = parse_date(lp.get("last_touch"))
    contact_ids = set()
    for e in (lp.get("contacts") or []):
        p = ctx["lookup"].get(norm_email(e))
        if p:
            contact_ids.add(p["id"])
    seen = None
    for it in ctx["interactions"]:
        if it["date"] and contact_ids & set(it["person_ids"]) and any(m in it["person_ids"] for m in ctx["member_ids"]):
            d = it["date"].date()
            if seen is None or d > seen:
                seen = d
    dates = [d for d in (stored, seen) if d]
    return max(dates) if dates else None


def met_today(ctx: dict[str, Any], lp: dict[str, Any]) -> bool:
    """The user meets one of this LP's contacts today."""
    ids = {ctx["lookup"][norm_email(e)]["id"] for e in (lp.get("contacts") or []) if norm_email(e) in ctx["lookup"]}
    now = ctx["now"]
    return any(m.get("start") and m["start"].date() == now.date() and ids & set(m.get("person_ids") or []) for m in ctx["meetings"])


def owner_of(ctx: dict[str, Any], lp: dict[str, Any]) -> tuple[str | None, str | None]:
    """(email, first name) of the colleague who owns this LP relationship, or (None, None) when it is the user's or
    unassigned. An owner ant. cannot place in the firm counts as unassigned, so nothing goes unwatched."""
    email = norm_email(lp.get("owner"))
    if not email or email == norm_email(ctx.get("user_email")):
        return None, None
    colleagues = ctx.get("colleagues")
    if colleagues is not None:  # the firm's members from the config: known even on a run that read no people
        if email not in colleagues:
            return None, None
        return email, str(colleagues[email] or email.split("@")[0]).split(" ")[0].capitalize()
    person = ctx["lookup"].get(email)
    if not person or not person.get("is_member"):
        return None, None
    return email, str(person.get("name") or email).split(" ")[0]


def call_alerts(ctx: dict[str, Any], lps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """An LP that has not paid all the capital called from it: the amount outstanding and since when."""
    today = ctx["now"].date()
    out = []
    for lp in lps:
        called, paid = lp.get("called_usd"), lp.get("paid_in_usd")
        if not isinstance(called, (int, float)) or not isinstance(paid, (int, float)) or called - paid < 1:
            continue
        since = parse_date(lp.get("last_call_date"))
        days = (today - since).days if since else None
        out.append({"lp_id": lp.get("id"), "name": lp.get("name"), "id": sid("lp", lp.get("id"), "call", prefix="l"),
                    "priority": "urgent", "breach": bool(days is None or days > 10), "kind": "call", "outstanding_usd": called - paid,
                    "call_date": since.isoformat() if since else None,
                    "days_since": days, "last_touch": None, "in_window": False, "window": None, "source_url": lp.get("source_url"),
                    "text": f"{money(called - paid)} still due on the capital call" + (f" of {fmt_short_date(since)}" if since else "") +
                            (f", {days} days ago" if days is not None else "")})
    return out


def fund_summary(lps: list[dict[str, Any]], firm: dict[str, Any] | None, today,
                 before: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Each fund at a glance: committed, called, paid in and unfunded, LP count and the next re-up window. Called and
    unfunded appear only when the LP list carries what was called. A fund's target size comes from the firm, else
    from what Home showed before (a pulse reads no LP list or firm page)."""
    known_size = {str(f.get("name")): f.get("size_usd") for f in before or [] if f.get("size_usd")}
    funds: dict[str, dict[str, Any]] = {}
    for lp in lps:
        name = str(lp.get("fund") or (firm or {}).get("fund") or "Fund")
        f = funds.setdefault(name, {"name": name, "committed_usd": 0, "called_usd": 0, "paid_in_usd": 0, "lps": 0, "known_called": 0,
                                    "next_window": None})
        f["lps"] += 1
        f["committed_usd"] += lp.get("commitment_usd") or 0
        if isinstance(lp.get("called_usd"), (int, float)):
            f["known_called"] += 1
            f["called_usd"] += lp["called_usd"]
            f["paid_in_usd"] += lp.get("paid_in_usd") if isinstance(lp.get("paid_in_usd"), (int, float)) else lp["called_usd"]
        start = parse_date(lp.get("reup_window_start"))
        if start and start >= today and (not f["next_window"] or start.isoformat() < f["next_window"]):
            f["next_window"] = start.isoformat()
    out = []
    for f in funds.values():
        whole = f["known_called"] == f["lps"] and f["lps"] > 0
        size = ((firm or {}).get("fund_size_usd") if (firm or {}).get("fund") == f["name"] else None) or known_size.get(f["name"])
        out.append({"name": f["name"], "size_usd": size, "committed_usd": f["committed_usd"], "lps": f["lps"], "next_window": f["next_window"],
                    "called_usd": f["called_usd"] if whole else None, "paid_in_usd": f["paid_in_usd"] if whole else None,
                    "unfunded_usd": f["committed_usd"] - f["called_usd"] if whole else None,
                    "called_pct": round(100 * f["called_usd"] / f["committed_usd"]) if whole and f["committed_usd"] else None})
    return out


def alerts(ctx: dict[str, Any], lps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    today = ctx["now"].date()
    out = []
    for lp in lps:
        last = last_touch(ctx, lp)
        gap = (today - last).days if last else None
        if met_today(ctx, lp):
            continue  # you meet them today: the meeting is the touch, and its prep card carries the LP's facts
        start, end = parse_date(lp.get("reup_window_start")), parse_date(lp.get("reup_window_end"))
        in_window = bool(start and end and start - timedelta(days=WINDOW_LEAD_DAYS) <= today <= end)
        base = {"lp_id": lp.get("id"), "name": lp.get("name"), "commitment": money(lp.get("commitment_usd")),
                "last_touch": last.isoformat() if last else None, "days_since": gap, "in_window": in_window,
                "window": f"{fmt_short_date(start)} to {fmt_short_date(end)}" if start and end else None,
                "source_url": lp.get("source_url")}
        if in_window and (gap is None or gap > WINDOW_TOUCH_DAYS):
            # Overdue only once the window is a month away or open: ten weeks out it is a touch to plan, not a breach.
            soon = start - today <= timedelta(days=WINDOW_URGENT_DAYS)
            out.append({**base, "id": sid("lp", lp.get("id"), "window", prefix="l"), "priority": "urgent" if soon else "high", "breach": soon,
                        "text": f"Re-up window opens {fmt_short_date(start)}; no touch in {gap if gap is not None else 'any'} days"})
        elif gap is None or gap > DEFAULT_TOUCH_DAYS:
            out.append({**base, "id": sid("lp", lp.get("id"), "decay", prefix="l"), "priority": "high", "breach": False,
                        "text": f"No touch in {gap if gap is not None else 'any'} days"})
    out.sort(key=lambda a: (not a["breach"], -(a["days_since"] or 999)))
    return out


# A paid-in figure beside a called one tells every LP that someone has not paid: it never goes in the letter.
# Paid-in capital by any of its names: "paid in", "contributed", "funded so far", "capital received".
PAID_IN = re.compile(r"\bpaid[\s-]*in\b|\b(?:contributed|contributions?)\b|\bfunded so far\b|\bcapital received\b|\breceived from LPs\b", re.I)


def letter_check(markdown: str) -> dict[str, Any]:
    """Which of the template's sections a draft letter lacks, and any line that names paid-in capital."""
    heads = [h.strip().lower() for h in re.findall(r"^#{1,4}\s+(.+)$", markdown or "", re.M)]
    missing = [s for s in LETTER_SECTIONS if not any(s.lower() in h for h in heads)]
    paid = [ln.strip() for ln in (markdown or "").splitlines() if PAID_IN.search(ln)]
    return {"sections": LETTER_SECTIONS, "missing": missing, "paid_in_lines": paid[:5],
            "complete": not missing and not paid,
            **({"fix": "Take out every paid-in figure: the letter gives committed and called only."} if paid else {})}
