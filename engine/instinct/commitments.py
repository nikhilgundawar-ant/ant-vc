"""Commitments: check what Claude extracted from meeting notes against the transcript.

Every commitment must quote the transcript word for word, name a meeting
participant as the owner, and carry a due date when one was said. Anything that
fails is rejected with a reason instead of reaching the brief.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from difflib import SequenceMatcher
from typing import Any

from .names import first_relation, normalize_name, split_name
from .pipeline import parse_deadline
from .util import fmt_short_date, norm_email, parse_date, parse_dt, sid, tzinfo

QUOTE_FLOOR = 0.86


def _clean(text: str) -> str:
    text = (text or "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", text).strip().lower()


def transcript_lines(tr: dict[str, Any]) -> list[dict[str, Any]]:
    lines = tr.get("lines")
    if lines:
        return [{"i": i, "speaker": (l.get("speaker") or ""), "text": (l.get("text") or "")} for i, l in enumerate(lines)]
    out = []
    for i, raw in enumerate((tr.get("text") or "").splitlines()):
        m = re.match(r"^\s*(?:\[[^\]]*\]\s*)?([^:]{2,60}):\s*(.*)$", raw)
        out.append({"i": i, "speaker": m.group(1).strip() if m else "", "text": m.group(2) if m else raw})
    return out


def locate_quote(quote: str, lines: list[dict[str, Any]]) -> tuple[int | None, float]:
    q = _clean(quote)
    if not q:
        return None, 0.0
    best_i, best = None, 0.0
    for line in lines:
        t = _clean(line["text"])
        if q in t:
            return line["i"], 1.0
        ratio = SequenceMatcher(None, q, t).find_longest_match(0, len(q), 0, len(t)).size / max(1, len(q))
        if ratio > best:
            best_i, best = line["i"], ratio
    return (best_i, best) if best >= QUOTE_FLOOR else (None, best)


WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def parse_due(value: Any, ref: datetime) -> date | None:
    """Relative dates, by the same table as the post-meeting skill. Weeks run Monday to Sunday."""
    if value is None or value == "":
        return None
    d = parse_date(value)
    if d and re.match(r"^\d{4}-\d{2}-\d{2}", str(value)):
        return d
    t = str(value).lower()
    base = ref.date()
    if re.search(r"\b(today|tonight|eod|end of day|by evening|after this call|after the call)\b", t):
        return base
    if re.search(r"\btomorrow\b", t):
        return base + timedelta(days=1)
    m = re.search(r"\bnext (" + "|".join(WEEKDAYS) + r")\b", t)
    if m:
        next_monday = base + timedelta(days=7 - base.weekday())
        return next_monday + timedelta(days=WEEKDAYS.index(m.group(1)))
    m = re.search(r"\b(" + "|".join(WEEKDAYS) + r")\b", t)
    if m:
        delta = (WEEKDAYS.index(m.group(1)) - base.weekday()) % 7
        return base + timedelta(days=delta or 7)
    if re.search(r"\b(this week|end of (the )?week|eow)\b", t):
        if base.weekday() >= 5:
            return base + timedelta(days=7 - base.weekday() + 4)
        return base + timedelta(days=4 - base.weekday())
    if re.search(r"\bnext week\b", t):
        return base + timedelta(days=7 - base.weekday() + 4)
    if re.search(r"\bend of (the )?month\b", t):
        first_next = (base.replace(day=1) + timedelta(days=32)).replace(day=1)
        return first_next - timedelta(days=1)
    m = re.search(r"\b(?:by|before|on|the)\s+(?:the\s+)?(\d{1,2})(?:st|nd|rd|th)\b", t)
    if m:
        day = int(m.group(1))
        try:
            cand = base.replace(day=day)
        except ValueError:
            cand = None
        if cand is None or cand < base:
            nxt = (base.replace(day=1) + timedelta(days=32)).replace(day=1)
            try:
                cand = nxt.replace(day=day)
            except ValueError:
                return None
        return cand
    m = re.search(r"\bin (\d+|two|three|a couple of) (days|weeks)\b", t)
    if m:
        n = {"two": 2, "three": 3, "a couple of": 2}.get(m.group(1), None) or int(m.group(1))
        return base + timedelta(days=n * (7 if m.group(2) == "weeks" else 1))
    return parse_deadline(t if t.startswith(("by", "before", "on", "this", "next")) else f"by {t}", ref)


def _match_participant(name: str, participants: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not name:
        return None
    if "@" in name:
        for p in participants:
            if norm_email(p.get("email")) == norm_email(name):
                return p
    target = normalize_name(name)
    for p in participants:
        if normalize_name(p.get("name")) == target:
            return p
    tf, tl = split_name(name)
    close = []
    for p in participants:
        pf, pl = split_name((p.get("name") or ""))
        if (tl and pl == tl and first_relation(pf, tf) in ("same", "nick")) or (not tl and first_relation(pf, tf) in ("same", "nick")):
            close.append(p)
    return close[0] if len(close) == 1 else None


def validate(extracted: list[dict[str, Any]], transcripts: list[dict[str, Any]], firm_domain: str = "") -> dict[str, Any]:
    by_id = {t.get("id"): t for t in transcripts}
    valid, rejected = [], []
    seen: set[tuple[str, int, str]] = set()
    for item in extracted:
        tr = by_id.get(item.get("transcript_id"))
        if not tr:
            rejected.append({**item, "why": "unknown transcript"})
            continue
        lines = transcript_lines(tr)
        line_i, ratio = locate_quote((item.get("quote") or ""), lines)
        if line_i is None:
            rejected.append({**item, "why": f"quote not found in the transcript (best match {ratio:.2f})"})
            continue
        participants = (tr.get("attendees") or [])
        owner = _match_participant((item.get("owed_by") or ""), participants)
        if not owner:
            rejected.append({**item, "why": "owner is not a meeting participant"})
            continue
        owed_to = _match_participant((item.get("owed_to") or ""), participants) if item.get("owed_to") else None
        meeting_dt = parse_dt(tr.get("date")) or datetime.now()
        due = parse_due(item.get("due"), meeting_dt)
        # Two promises on one line are kept apart when each quotes its own clause.
        qn = re.sub(r"\W+", " ", str(item.get("quote") or "").lower()).strip()
        ln = re.sub(r"\W+", " ", lines[line_i]["text"].lower()).strip()
        clause = qn if qn and qn != ln else ""
        key = (tr["id"], line_i, normalize_name(owner.get("name")), clause)
        if key in seen:
            rejected.append({**item, "why": "duplicate: already extracted from this line. For two promises on one line, quote each clause on its own"})
            continue
        seen.add(key)
        side = "us" if firm_domain and (owner.get("email") or "").lower().endswith("@" + firm_domain) else "them"
        valid.append({
            "id": sid("commitment", tr["id"], line_i, owner.get("email") or owner.get("name"), *([clause] if clause else []), prefix="k"),
            "transcript_id": tr["id"], "event_id": tr.get("event_id"), "line": line_i,
            "owed_by": owner.get("name"), "owed_by_email": owner.get("email"), "side": side,
            "owed_to": (owed_to or {}).get("name") or item.get("owed_to"), "owed_to_email": (owed_to or {}).get("email"),
            "attendee_emails": sorted({norm_email(p.get("email")) for p in participants if p.get("email")}),
            "internal": bool(firm_domain) and side == "us" and bool(owed_to) and str((owed_to or {}).get("email") or "").lower().endswith("@" + firm_domain),
            "what": (item.get("what") or "").strip(),
            "due": due.isoformat() if due else None, "quote": lines[line_i]["text"], "status": "open",
            "source_url": tr.get("url"), "meeting_title": tr.get("title"), "meeting_date": tr.get("date"),
        })
    return {"valid": valid, "rejected": rejected}


def merge(store: list[dict[str, Any]], new: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Add new commitments to the store without duplicates; keep status changes the user made."""
    by_id = {c["id"]: c for c in store}
    for c in new:
        if c["id"] in by_id:
            keep = by_id[c["id"]]
            # How it closed stays too: a promise closed by Sent it is remembered as sent (the CRM step it was is done).
            by_id[c["id"]] = {**c, "status": keep.get("status", c["status"]), "done_at": keep.get("done_at"),
                              **({"sent": True} if keep.get("sent") else {})}
        else:
            by_id[c["id"]] = c
    return list(by_id.values())


def due_view(store: list[dict[str, Any]], today: date, user_email: str, horizon_days: int = 2) -> dict[str, list[dict[str, Any]]]:
    """Open promises by side: yours due within `horizon_days` working days (on a Friday that reaches Monday and Tuesday)
    or late, a colleague's to you from its due day, and yours with no date a week or more after the meeting."""
    mine, theirs, undated = [], [], []
    horizon = today
    left = horizon_days
    while left > 0:
        horizon += timedelta(days=1)
        if horizon.weekday() < 5:
            left -= 1
    for c in store:
        if c.get("status") != "open":
            continue
        due = parse_date(c.get("due")) if c.get("due") else None
        overdue = bool(due and due < today)
        soon = bool(due and today <= due <= horizon)
        row = {**c, "overdue": overdue, "due_soon": soon, "due_today": bool(due and due == today)}
        me = norm_email(user_email)
        if norm_email(c.get("owed_by_email")) == me:
            if overdue or soon:
                mine.append(row)
            elif not due:
                made = parse_date(c.get("meeting_date"))
                if made and 5 <= (today - made).days <= 45:
                    undated.append(row)
        elif (overdue or (c.get("internal") and soon and norm_email(c.get("owed_to_email")) == me)) and \
                (norm_email(c.get("owed_to_email")) == me or me in (c.get("attendee_emails") or [])):
            theirs.append(row)  # a colleague's promise to you shows from the day it is due: "waiting on your team"
    mine.sort(key=lambda c: (not c["overdue"], c.get("due") or "9999"))
    theirs.sort(key=lambda c: c.get("due") or "9999")
    undated.sort(key=lambda c: c.get("meeting_date") or "")
    return {"mine": mine, "theirs": theirs, "undated": undated}


def prune(store: list[dict[str, Any]], today: date) -> list[dict[str, Any]]:
    """Keep the store small and true: done items go after 30 days, open items 120 days after they were due
    (or made, when undated)."""
    out = []
    for c in store:
        if c.get("status") == "done":
            done = parse_date(c.get("done_at"))
            if done and (today - done).days > 30:
                continue
        else:
            ref = parse_date(c.get("due")) or parse_date(c.get("meeting_date"))
            if ref and (today - ref).days > 120:
                continue
        out.append(c)
    return out


SCHEDULING = re.compile(r"\b(confirm|schedule|book|set up|setup|find|propose|arrange|fix)\b((?:\s+[\w'-]+){0,4}?)\s+(meeting|call|slot|time|times|"
                        r"session|catch[- ]?up|dinner|lunch|coffee|visit)\b", re.I)
SEND_TIMES = re.compile(r"\bsend\b(?:\s+[\w'-]+){0,3}?\s+(invites?|calendar invites?|times|slots|time options)\b", re.I)
NOT_ABOUT = {"after", "before", "from", "at", "in", "during", "following", "about", "of", "on"}


def is_scheduling(what: str) -> bool:
    """A promise to arrange a meeting ("confirm the second meeting slot", "set up a call with Kabir"), never one that
    only mentions a meeting ("send feedback after the Monday partner meeting")."""
    text = str(what or "")
    if SEND_TIMES.search(text):
        return True
    for m in SCHEDULING.finditer(text):
        if not set(m.group(2).lower().split()) & NOT_ABOUT:
            return True
    return False


def _named_on(what: str, meeting: dict[str, Any], ctx: dict[str, Any], skip: set[Any]) -> bool:
    """Everyone a promise names besides the person it is owed to (a colleague by first name, anyone by full name) is on
    the meeting. True when it names nobody else."""
    lookup = ctx.get("lookup") or {}
    me = (ctx.get("user_person") or {}).get("id")
    people = {p["id"]: p for p in lookup.values() if isinstance(p, dict) and p.get("id")}
    named = set()
    for pid, p in people.items():
        if pid in skip or pid == me:
            continue
        name = str(p.get("name") or "").strip()
        first = name.split(" ")[0]
        if name and re.search(rf"\b{re.escape(name)}\b", what, re.I):
            named.add(pid)
        elif p.get("is_member") and len(first) > 2 and re.search(rf"\b{re.escape(first)}\b", what):
            named.add(pid)
    return named <= set(meeting.get("person_ids") or [])


def done_by_calendar(c: dict[str, Any], ctx: dict[str, Any]) -> str | None:
    """What the calendar already shows done: a meeting booked with the person a "set up a meeting" promise was made
    to, or a board that has met since a promise to prepare for it. Asked, never assumed: the row offers Done."""
    if c.get("status") != "open":
        return None
    now = ctx["now"]
    made = parse_date(c.get("meeting_date"))
    lookup = ctx.get("lookup") or {}
    to = lookup.get(norm_email(c.get("owed_to_email"))) if c.get("owed_to_email") else None
    if to and to.get("is_member"):  # a founder's promise to us: the company is theirs
        to = lookup.get(norm_email(c.get("owed_by_email"))) if c.get("owed_by_email") else None
    if not to:
        return None
    company = to.get("company_id")
    what = str(c.get("what") or "")
    for m in ctx.get("meetings") or []:
        st = m.get("start")
        if not st or (made and st.date() <= made):
            continue
        ids = set(m.get("external_ids") or [])
        with_them = to.get("id") in ids or (company and any((lookup.get(i) or {}).get("company_id") == company for i in ids))
        if not with_them:
            continue
        if is_scheduling(what) and st <= now + timedelta(days=14):
            # Any meeting with them since the promise keeps it, however long ago: "confirm the slot" is done once they met.
            # "Set up a call with Kabir": a meeting with them alone does not keep it; Kabir has to be on it too.
            if not _named_on(what, m, ctx, {to.get("id")}):
                continue
            local = st.astimezone(tzinfo(ctx.get("tz") or "UTC"))
            if st <= now:
                return f"you met them on {local.strftime('%a')} {fmt_short_date(local)}"
            return f"a meeting with them is on the calendar for {local.strftime('%a')} {fmt_short_date(local)} {local.strftime('%H:%M')}"
        if re.search(r"\bboard\b", what, re.I) and re.search(r"\bboard\b", str(m.get("title") or ""), re.I) and \
                now - timedelta(days=7) <= (m.get("end") or st) <= now:
            return f"the board met on {fmt_short_date(st)}"
    return None


def looks_done(c: dict[str, Any], threads: list[dict[str, Any]], user_email: str) -> str | None:
    """A sent email from the user to the person owed, after the meeting, that mentions the promise: one-tap confirm."""
    if c.get("status") != "open" or norm_email(c.get("owed_by_email")) != norm_email(user_email) or not c.get("owed_to_email"):
        return None
    made = parse_date(c.get("meeting_date"))
    words = {w for w in re.findall(r"[a-z]{4,}", (c.get("what") or "").lower())} - {"send", "share", "with", "their", "them", "from", "over", "your", "will"}
    for th in threads or []:
        for m in th.get("messages") or []:
            frm = norm_email((m.get("from") or {}).get("email"))
            to = {norm_email(x.get("email")) for x in (m.get("to") or th.get("participants") or [])}
            when = parse_date(m.get("date") or th.get("date"))
            if frm != norm_email(user_email) or norm_email(c.get("owed_to_email")) not in to or (made and when and when < made):
                continue
            text = ((th.get("subject") or "") + " " + (m.get("text") or "")).lower()
            if words and sum(1 for w in words if w in text) >= max(1, min(2, len(words))):
                return f"you emailed them on {fmt_short_date(when)}" if when else "you emailed them"
    return None
