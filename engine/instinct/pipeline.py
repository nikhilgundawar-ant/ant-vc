"""Pipeline watch: stale deals, competing-fund signals, weekly review, partner pre-read."""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from typing import Any

from . import stages as stages_mod
from .graph import deals_for_user, open_deal_for_company
from .util import clip, domain_of, fmt_short_date, norm_email, parse_date, parse_dt, plural, sid

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
MONTHS = {m: i + 1 for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"])}
MONTHS.update({k[:3]: v for k, v in list(MONTHS.items())})
MONTHS["sept"] = 9

# ---------------------------------------------------------------- stale deals


def sponsor(ctx: dict[str, Any], deal: dict[str, Any]) -> str | None:
    """The partner who sponsors a deal: its lead when a partner leads it, else a partner on its team, else the firm's
    only partner. None when the firm has several partners and none is on the deal."""
    titles = {norm_email(m.get("email")): str(m.get("title") or "") for m in ctx.get("members") or [] if isinstance(m, dict)}

    def is_partner(e: Any) -> bool:
        return bool(re.search(r"\b(partner|general partner|gp|managing director)\b", titles.get(norm_email(e), ""), re.I))

    def name(e: Any) -> str | None:
        return ((ctx.get("lookup") or {}).get(norm_email(e)) or {}).get("name") if e else None
    for e in [deal.get("owner_email")] + [t for t in deal.get("team") or [] if isinstance(t, str)]:
        if e and is_partner(e):
            return name(e)
    partners = [e for e in titles if is_partner(e)]
    return name(partners[0]) if len(partners) == 1 else None


def working_days_since(day: date, today: date) -> int:
    """Weekdays after `day`, up to and including `today`: Thursday to Monday is two."""
    n, d = 0, day
    while d < today:
        d += timedelta(days=1)
        if d.weekday() < 5:
            n += 1
    return n


def add_working_days(day: date, n: int) -> date:
    """The weekday `n` working days after `day`: Friday plus one is Monday."""
    d = day
    while n > 0:
        d += timedelta(days=1)
        if d.weekday() < 5:
            n -= 1
    return d


def met_recently(ctx: dict[str, Any], working_days: int = 5) -> dict[str, Any]:
    """{company id: when}: companies the user met (an external meeting that has started) in the last five working
    days. That meeting is the deal's latest step: the deal is not stale, and its next step may not be in the CRM yet."""
    now = ctx["now"]
    out: dict[str, Any] = {}
    for cid, st in (ctx.get("met_carried") or {}).items():  # what Home carried from a wider read
        if st <= now and working_days_since(st.date(), now.date()) <= working_days:
            out[cid] = st
    for m in ctx.get("meetings") or []:
        st = m.get("start")
        if not st or not m.get("external") or st > now or m.get("all_day"):
            continue
        if working_days_since(st.date(), now.date()) > working_days:
            continue
        for pid in m.get("external_ids") or []:
            cid = ((ctx.get("lookup") or {}).get(pid) or {}).get("company_id")
            if cid and (cid not in out or st > out[cid]):
                out[cid] = st
    return out


def stale_deals(ctx: dict[str, Any], deals: list[dict[str, Any]] | None = None, dwell_scale: float = 1.0,
                skip_contact: bool = False) -> list[dict[str, Any]]:
    """Deals past their stage's dwell time, with no next step, an overdue next step, or no contact in a week.
    With skip_contact (email could not be read this run) the no-contact rule is skipped rather than guessed."""
    stage_map = ctx["stage_map"]
    today = ctx["now"].date()
    no_contact_days = stage_map.get("no_contact_days", 7)
    out = []
    for d in deals if deals is not None else ctx["deals"]:
        key = d["stage_key"]
        st = stage_map["by_key"].get(key, {})
        if not st.get("active"):
            continue
        reasons = []
        entered = d.get("stage_entered_dt")
        days_in = (today - entered.date()).days if entered else None
        due_ = d.get("next_step_due_dt")
        if (d.get("next_step") or "").strip() and due_ and today <= due_.date() <= today + timedelta(days=1):
            continue  # the next step is due today or tomorrow: the deal is moving
        dw = stages_mod.dwell(key, stage_map, dwell_scale)
        if dw is not None and days_in is not None and days_in > dw:
            reasons.append({"code": "over_dwell", "text": f"{plural(days_in, 'day')} in {stages_mod.label(d['stage_name'], False)}, past the {dw}-day mark"})
        next_step = (d.get("next_step") or "").strip()
        if key != "inbound" and not next_step:
            reasons.append({"code": "no_next_step", "text": "No next step set"})
        due = d.get("next_step_due_dt")
        if next_step and due and due.date() < today:
            reasons.append({"code": "next_step_overdue", "text": f"Next step was due {fmt_short_date(due)}"})
        if st.get("contact_check") and not skip_contact:
            lc = d.get("last_contact_dt")
            gap = (today - lc.date()).days if lc else None
            if gap is None or gap > no_contact_days:
                reasons.append({"code": "no_contact", "text": "No contact on record" if gap is None else f"No contact in {plural(gap, 'day')}"})
        if reasons:
            out.append({"deal_id": d["id"], "company": d.get("company_name"), "stage": d["stage_name"], "stage_key": key,
                        "owner": d.get("owner_email"), "days_in_stage": days_in, "dwell": dw, "reasons": reasons,
                        "source_url": d.get("url")})
    out.sort(key=lambda s: (-stages_mod.order(s["stage_key"], stage_map), -(s["days_in_stage"] or 0)))
    return out


# ---------------------------------------------------------------- founders waiting on a reply

SMALL_TALK = re.compile(r"\b(how are you|how have you been|how's it going|how is it going|hope (you|all|this|your)|how was your)\b", re.I)


def question_in(text: Any) -> str | None:
    """The last real question in a message, word for word: a sentence of two words or more ("Any update?") that ends
    with a question mark, with no link in it and no small talk ("How are you?")."""
    found = None
    for sent in re.split(r"(?<=[.?!])\s+|\n+", str(text or "")):
        sent = sent.strip()
        if sent.endswith("?") and len(sent.split()) >= 2 and "http" not in sent.lower() and not SMALL_TALK.search(sent):
            found = sent
    return found


def firm_domains(ctx: dict[str, Any]) -> set[str]:
    """The firm's own mail domains: the user's, the firm's and every member's."""
    me = norm_email(ctx.get("user_email"))
    firm = (ctx.get("bundle") or {}).get("firm") or {}
    doms = {x for x in [me.split("@")[-1] if me else "", str(firm.get("domain") or "").lower()] if x}
    doms |= {norm_email(m.get("email")).split("@")[-1] for m in (firm.get("members") or []) + (ctx.get("members") or [])
             if isinstance(m, dict) and norm_email(m.get("email"))}
    return doms


def company_of(ctx: dict[str, Any], email: Any) -> Any:
    """The company an address belongs to: its person's company, else its domain's."""
    e = norm_email(email)
    if not e:
        return None
    return ((ctx.get("lookup") or {}).get(e) or {}).get("company_id") or (ctx.get("domain_to_company") or {}).get(e.split("@")[-1])


def answered_since(ctx: dict[str, Any], company_id: Any, since: date) -> bool:
    """The firm wrote to the company on or after `since` on a thread this run read, or someone met them since."""
    doms = firm_domains(ctx)
    for th in (ctx.get("bundle") or {}).get("threads") or []:
        if not any(company_of(ctx, (p_ or {}).get("email")) == company_id for p_ in th.get("participants") or []):
            continue
        for m in th.get("messages") or []:
            dt = parse_dt(m.get("date"), ctx.get("tz"))
            sender = norm_email((m.get("from") or {}).get("email"))
            if dt and dt.date() >= since and sender and sender.split("@")[-1] in doms:
                return True
    lookup = ctx.get("lookup") or {}
    for mt in ctx.get("meetings") or []:
        st = mt.get("start")
        if st and since <= st.date() and st <= ctx["now"] and not mt.get("all_day") and \
                any((lookup.get(pid) or {}).get("company_id") == company_id for pid in mt.get("external_ids") or []):
            return True
    met = (ctx.get("met_carried") or {}).get(company_id)
    return bool(met and met.date() >= since)


def unanswered(ctx: dict[str, Any], deals: list[dict[str, Any]] | None = None, skip_threads: Any = ()) -> list[dict[str, Any]]:
    """Founders waiting on the user. Their company has an open deal, and the latest message to or from that company,
    on any thread, is their question: two working days old or more and at most three weeks, with nothing from the
    firm since and no meeting with them since. One per deal, the question quoted word for word."""
    now = ctx["now"]
    today = now.date()
    firm_doms = firm_domains(ctx)
    by_key = ctx["stage_map"]["by_key"]
    by_company: dict[str, dict[str, Any]] = {}
    for d in deals if deals is not None else ctx["deals"]:
        if (by_key.get(d.get("stage_key")) or {}).get("active") and d.get("company_id"):
            by_company.setdefault(d["company_id"], d)
    lookup = ctx.get("lookup") or {}
    latest: dict[str, tuple] = {}  # company id: (when, sender, message, thread) of the latest word either way
    skip = {str(x) for x in skip_threads or ()}
    for th in (ctx.get("bundle") or {}).get("threads") or []:
        if str(th.get("id")) in skip:
            continue
        cids = set()
        for p_ in th.get("participants") or []:
            e = norm_email((p_ or {}).get("email"))
            if e and e.split("@")[-1] not in firm_doms and company_of(ctx, e) in by_company:
                cids.add(company_of(ctx, e))
        for m in th.get("messages") or []:
            dt = parse_dt(m.get("date"), ctx.get("tz"))
            if not dt or dt > now:
                continue
            sender = norm_email((m.get("from") or {}).get("email"))
            for cid in cids | ({company_of(ctx, sender)} & set(by_company) if sender else set()):
                if cid not in latest or dt > latest[cid][0]:
                    latest[cid] = (dt, sender, m, th)
    out = []
    for cid, (dt, sender, m, th) in latest.items():
        if not sender or sender.split("@")[-1] in firm_doms or company_of(ctx, sender) != cid:
            continue  # the firm wrote last, or someone else did (a co-investor, a lawyer)
        if working_days_since(dt.date(), today) < 2 or (today - dt.date()).days > 21:
            continue
        q = question_in(m.get("text"))
        if not q:
            continue
        met = any(mt.get("start") and dt <= mt["start"] <= now and not mt.get("all_day") and
                  any((lookup.get(pid) or {}).get("company_id") == cid for pid in mt.get("external_ids") or [])
                  for mt in ctx.get("meetings") or []) or bool((ctx.get("met_carried") or {}).get(cid) and ctx["met_carried"][cid] >= dt)
        if met:
            continue  # you met them since: the question was likely answered in the room
        deal = by_company[cid]
        name = (lookup.get(sender) or {}).get("name") or (m.get("from") or {}).get("name") or sender
        out.append({"id": sid("asked", th.get("id"), m.get("date")), "deal_id": deal["id"], "company": deal.get("company_name"),
                    "company_id": cid, "person": name, "email": sender, "asked_on": dt.date().isoformat(),
                    "question": q if len(q) <= 160 else None, "subject": th.get("subject"), "thread_id": th.get("id"),
                    "source_url": th.get("url")})
    out.sort(key=lambda r: r["asked_on"])
    return out


# ---------------------------------------------------------------- competing-fund signals

POSITIVE = [
    (re.compile(r"\bterm[\s-]?sheet\b", re.I), 3, "term sheet"),
    (re.compile(r"\bTS\b"), 2, "term sheet"),
    (re.compile(r"\b(wants to|offered to|has offered to|agreed to|has agreed to|is going to|plans to|is set to|will)\s+(lead|anchor|co-lead)\b", re.I), 3, "another fund leading"),
    (re.compile(r"\b(is|are)\s+(leading|anchoring)\b[^.?!]{0,30}\b(round|seed|series|raise)\b", re.I), 3, "another fund leading"),
    (re.compile(r"\b(round|allocation)\b[^.?!]{0,30}\b(filling|closing|almost full|oversubscribed|full)\b", re.I), 3, "round filling"),
    (re.compile(r"\boversubscribed\b", re.I), 3, "round filling"),
    (re.compile(r"\bclos(e|ing)\b[^.?!]{0,20}\bthe round\b", re.I), 2, "closing the round"),
    (re.compile(r"\b(other|another|two|three|several|a few)\b[^.?!]{0,12}\b(funds?|investors|vcs|firms)\b[^.?!]{0,50}\b(interested|keen|moving|committed|diligence|offer|offers|term)\b", re.I), 3, "other funds moving"),
    (re.compile(r"\b(deadline|decide by|decision by|need (a|an)? ?answer by|commit by|exploding)\b", re.I), 2, "deadline"),
    (re.compile(r"\b(offer|terms)\b[^.?!]{0,20}\bfrom\b", re.I), 2, "offer from another fund"),
]
NEGATIVE = [
    re.compile(r"\b(no|not yet|haven't|have not|don't have|do not have|without)\b[^.?!]{0,25}\bterm[\s-]?sheet", re.I),
    re.compile(r"\bterm[\s-]?sheet\b[^.?!]{0,25}\b(template|templates|explained|101|guide|primer|webinar)\b", re.I),
    re.compile(r"\b(our|we'll send|we will send|we can send|send you our)\b[^.?!]{0,20}\bterm[\s-]?sheet", re.I),
    re.compile(r"\b(when|if)\b[^.?!]{0,20}\b(we|you)\b[^.?!]{0,20}\bterm[\s-]?sheet", re.I),
    re.compile(r"\bnot (closing|raising)\b", re.I),
    re.compile(r"\b(led|lead)\b[^.?!]{0,30}\b(by you|our seed|their seed in 20)", re.I),
]


def _own_names(ctx: dict[str, Any]) -> list[str]:
    """The firm's own name and domain stem, so our own fund never reads as "another fund"."""
    firm = (ctx.get("bundle") or {}).get("firm") or {}
    names = []
    if firm.get("name"):
        names.append(str(firm["name"]).split()[0].lower())
    if ctx.get("firm_domain"):
        names.append(ctx["firm_domain"].split(".")[0].lower())
    return [n for n in dict.fromkeys(names) if len(n) >= 3]
FUND_RE = re.compile(r"\b((?:[A-Z][A-Za-z&]+\s){0,3}(?:Capital|Ventures|Partners|VC|Fund|Investments|Growth))\b")
SENT_RE = re.compile(r"(?<=[.!?])\s+|\n+")


def _is_negated(sentence: str) -> bool:
    return any(n.search(sentence) for n in NEGATIVE)


def parse_deadline(text: str, ref: datetime) -> date | None:
    """'by Friday', 'by 5 Nov', 'by November 5th', 'end of the week', 'end of month'."""
    t = text.lower()
    base = ref.date()
    m = re.search(r"\b(?:by|before|until|on|this|next)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", t)
    if m:
        target = WEEKDAYS.index(m.group(1))
        delta = (target - base.weekday()) % 7 or 7
        if "next " + m.group(1) in t:
            delta += 7 if delta < 7 else 0
        return base + timedelta(days=delta)
    month_rx = r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*"
    m = re.search(rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+(?:of\s+)?{month_rx}\b", t)
    if m:
        return _safe_date(base, MONTHS.get(m.group(2), 0), int(m.group(1)))
    m = re.search(rf"\b{month_rx}\s+(\d{{1,2}})(?:st|nd|rd|th)?\b", t)
    if m:
        return _safe_date(base, MONTHS.get(m.group(1), 0), int(m.group(2)))
    if re.search(r"\bend of (the )?week\b", t):
        return base + timedelta(days=(4 - base.weekday()) % 7)
    if re.search(r"\bend of (the )?month\b", t):
        nxt = (base.replace(day=28) + timedelta(days=4))
        return nxt - timedelta(days=nxt.day)
    if re.search(r"\btomorrow\b", t):
        return base + timedelta(days=1)
    return None


def _safe_date(base: date, month: int, day: int) -> date | None:
    if not month:
        return None
    year = base.year if month >= base.month - 1 else base.year + 1
    try:
        return date(year, month, day)
    except ValueError:
        return None


SHARED_NOTE = re.compile(r"^\s*Competing fund:\s*(?P<what>.+?)\s*(?:\(from (?P<who>[\w\- ]+?)'s email(?:, (?P<on>[^)]+))?\))?\s*$", re.I | re.S)


def signal_phrase(sig: dict[str, Any]) -> str:
    """The fact in a few words: "term sheet from Bluepeak", "Bluepeak wants to lead", or "another fund is moving"."""
    fund = next((f for f in (sig.get("funds") or []) if f), None)
    labels = sig.get("labels") or []
    if fund and "term sheet" in labels:
        return f"term sheet from {fund}"
    if fund and any("lead" in l for l in labels):
        return f"{fund} wants to lead"
    if "term sheet" in labels:
        return "another fund has a term sheet out"
    if fund:
        return f"{fund} is moving"
    ev = str(sig.get("evidence") or "")
    m = re.search(r"\b(two|three|four|five|several|multiple|\d+) other (funds|investors|vcs)\b[^.]{0,40}?\b(in diligence|term sheets?|offers?)", ev, re.I)
    if m:
        what = m.group(3).lower()
        return f"{m.group(1).lower()} other funds " + ("in diligence" if what == "in diligence" else f"with {what}")
    if re.search(r"\boversubscribed\b", ev, re.I):
        return "the round is oversubscribed"
    if re.search(r"\b(round is (almost |nearly |now )?full|almost full|filling (up|fast)|nearly full)\b", ev, re.I):
        return "the round is filling up"
    if re.search(r"\b(competing|another) offer\b", ev, re.I):
        return "a competing offer is in"
    return "another fund is moving"


GREETING = re.compile(r"^\s*(?i:hi|hello|hey|dear)\s+[\w.-]+\s*[,:!]?\s*")
LEAD_IN = re.compile(r"^\s*(?i:(?:just\s+)?(?:wanted|writing)\s+to\s+(?:flag|let you know|say|share)\s+(?:that\s+)?)")


def _unaddress(sentence: str, names: set[str] | None = None) -> str:
    """The fact without the greeting: "Hi Kabir, wanted to flag that Tamarind..." becomes "Tamarind...",
    and "Rohan, our seed is..." becomes "Our seed is..." when Rohan is someone at the firm."""
    out = GREETING.sub("", sentence, count=1)
    m = re.match(r"^\s*([A-Z][a-z]+)\s*,\s*", out)
    if m and names and m.group(1).lower() in names:
        out = out[m.end():]
    out = LEAD_IN.sub("", out, count=1).strip()
    return (out[:1].upper() + out[1:]) if out else sentence


def deadline_gap(deal: dict[str, Any], deadline: Any, today: Any = None) -> str | None:
    """A founder's deadline that falls before our next step: the one fact that turns a calm row red. Once the date
    has gone, it says so instead of comparing it with the next step."""
    dl = parse_date(deadline) if deadline else None
    if not dl:
        return None
    if today and dl < today:
        return f"Their deadline {fmt_short_date(dl)} has passed"
    nxt = deal.get("next_step_due_dt") or parse_dt(deal.get("next_step_due"))
    if nxt and nxt.date() > dl:
        return f"Their deadline {fmt_short_date(dl)} is before your next step {fmt_short_date(nxt)}"
    if not (deal.get("next_step") or "").strip():
        return f"Their deadline is {fmt_short_date(dl)} and no next step is set"
    return None


def day_phrase(stage: str, days: int | None, dwell: int | None) -> str:
    """ "Term sheet, day 4 of 10", or past the mark: "Partner meeting for 9 days, usually 7"."""
    if days is None:
        return stage
    if dwell and days > dwell:
        return f"{stage} for {plural(days, 'day')}, usually {dwell}"
    return f"{stage}, day {days}" + (f" of {dwell}" if dwell else "")


def competing_signals(ctx: dict[str, Any], threshold: int = 3) -> list[dict[str, Any]]:
    firm_domain = ctx["firm_domain"]
    tz = ctx["tz"]
    own = _own_names(ctx)
    own_led = re.compile(r"\b(led|lead)\b[^.?!]{0,30}\bby (" + "|".join(map(re.escape, own)) + r")\b", re.I) if own else None
    first_names = {str(m.get("name") or "").split(" ")[0].lower() for m in ctx.get("members") or []} | \
        {str((ctx.get("user") or {}).get("name") or "").split(" ")[0].lower()}
    out = []
    for th in (ctx["bundle"].get("threads") or []):
        ext_domains = {domain_of(p.get("email")) for p in (th.get("participants") or []) if domain_of(p.get("email")) != firm_domain}
        deal = None
        for dom in ext_domains:
            cid = ctx["domain_to_company"].get(dom)
            deal = open_deal_for_company(ctx, cid)
            if deal:
                break
        if not deal:
            # personal addresses: match through the resolved person's company
            for p in (th.get("participants") or []):
                hit = ctx["lookup"].get(norm_email(p.get("email")))
                if hit and hit.get("company_id"):
                    deal = open_deal_for_company(ctx, hit["company_id"])
                    if deal:
                        break
        if not deal:
            continue
        messages = th.get("messages") or [{"from": {}, "date": th.get("date"), "text": (th.get("snippet") or "")}]
        best = None
        for msg in messages:
            sender = domain_of((msg.get("from") or {}).get("email"))
            if sender == firm_domain:
                continue  # our own words are not a signal about the round
            when = parse_dt(msg.get("date") or th.get("date"), tz) or ctx["now"]
            for sentence in SENT_RE.split(msg.get("text") or ""):
                s = sentence.strip()
                if not s or _is_negated(s) or (own_led and own_led.search(s)):
                    continue
                hits = [(w, label) for rx, w, label in POSITIVE if rx.search(s)]
                score = sum(w for w, _ in hits)
                if score >= threshold and (best is None or score > best["score"]):
                    funds = [f.strip() for f in FUND_RE.findall(s) if not any(o in f.lower() for o in own)]
                    best = {"score": score, "evidence": clip(_unaddress(s, first_names), 180), "labels": sorted({lbl for _, lbl in hits}),
                            "deadline": parse_deadline(s, when), "date": when, "funds": funds,
                            "said_by": str((msg.get("from") or {}).get("name") or "").split(" ")[0] or None}
        if best:
            out.append({
                "id": sid("signal", "competing", th.get("id"), prefix="s"), "kind": "round_moving",
                "deal_id": deal["id"], "company": deal.get("company_name"), "stage": deal["stage_name"], "stage_key": deal["stage_key"],
                "round": deal.get("round"), "company_id": deal.get("company_id"),
                "owner": deal.get("owner_email"), "thread_id": th.get("id"), "source_url": th.get("url"),
                "evidence": best["evidence"], "labels": best["labels"], "funds": best["funds"], "said_by": best.get("said_by"),
                "deadline": best["deadline"].isoformat() if best["deadline"] else None,
                "date": best["date"].isoformat(), "breach": True, "confidence": min(1.0, best["score"] / 6),
            })
    # What a colleague shared to the CRM: "Competing fund: ..." notes ant. wrote on the deal owner's approval. The
    # whole team reads the same fact, so every attendee's partner pack carries it.
    deal_by_id = {d["id"]: d for d in ctx["deals"]}
    for n in ((ctx["bundle"].get("crm") or {}).get("notes") or []):
        text = str(n.get("text") or "")
        m = SHARED_NOTE.match(text)
        deal = deal_by_id.get(n.get("deal_id"))
        if not m or not deal or not stages_mod.is_active(deal["stage_key"], ctx["stage_map"]):
            continue
        body, said, on = m.group("what").strip().rstrip("."), (m.group("who") or "").strip() or None, m.group("on")
        when = parse_dt(n.get("date") or on, tz) or ctx["now"]
        dl = re.search(r"decide by (\d{1,2} \w{3}(?: \d{4})?)", body, re.I)
        deadline = parse_deadline("by " + dl.group(1), when) if dl else None
        funds = [f.strip() for f in FUND_RE.findall(body) if not any(o in f.lower() for o in own)]
        labels = ["term sheet"] if re.search(r"term sheet", body, re.I) else ["lead"] if re.search(r"\blead\b", body, re.I) else []
        out.append({
            "id": sid("signal", "shared", n.get("id"), prefix="s"), "kind": "round_moving", "deal_id": deal["id"],
            "company": deal.get("company_name"), "stage": deal["stage_name"], "stage_key": deal["stage_key"], "round": deal.get("round"),
            "company_id": deal.get("company_id"), "owner": deal.get("owner_email"), "thread_id": None, "source_url": n.get("url"),
            "evidence": re.sub(r",?\s*decide by \d{1,2} \w{3}(?: \d{4})?", "", body), "labels": labels, "funds": funds, "said_by": said,
            "deadline": deadline.isoformat() if deadline else None, "date": when.isoformat(), "breach": True, "confidence": 0.8,
            "shared": True})
    # One signal per deal. The founder's own words from your mail beat a colleague's shared summary of them: the
    # shared note then only says the team already has it (and fills a deadline or fund the thread lacked).
    by_deal: dict[str, dict[str, Any]] = {}
    for s in sorted(out, key=lambda s: s["date"]):
        old = by_deal.get(s["deal_id"])
        if old and s.get("shared") and not old.get("shared"):
            old["in_crm"] = True
            old["deadline"] = old.get("deadline") or s.get("deadline")
            old["funds"] = old.get("funds") or s.get("funds")
            continue
        if old and old.get("shared") and not s.get("shared"):
            s = {**s, "in_crm": True, "deadline": s.get("deadline") or old.get("deadline"), "funds": s.get("funds") or old.get("funds")}
        by_deal[s["deal_id"]] = s
    return sorted(by_deal.values(), key=lambda s: s["date"], reverse=True)


def shared_note(sig: dict[str, Any]) -> str:
    """The CRM note that shares a competing fund with the team, in the one shape every ant. reads back."""
    dl = parse_date(sig.get("deadline"))
    who = f" (from {sig['said_by']}'s email" + (f", {fmt_short_date(parse_dt(sig.get('date')))})" if sig.get("date") else ")") if sig.get("said_by") else ""
    return f"Competing fund: {signal_phrase(sig)}" + (f", decide by {fmt_short_date(dl)}" if dl else "") + f".{who}"


# ---------------------------------------------------------------- review and pre-read


def moves(ctx: dict[str, Any], days: int = 7, deals: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    since = ctx["now"] - timedelta(days=days)
    out = []
    for d in deals if deals is not None else ctx["deals"]:
        entered = d.get("stage_entered_dt")
        if entered and entered >= since and d["stage_key"] not in ("inbound",):
            out.append({"deal_id": d["id"], "company": d.get("company_name"), "stage": d["stage_name"], "stage_key": d["stage_key"],
                        "entered": entered.date().isoformat(), "owner": d.get("owner_email"), "source_url": d.get("url")})
    out.sort(key=lambda m: -stages_mod.order(m["stage_key"], ctx["stage_map"]))
    return out


def _step_key(text: Any) -> str:
    return " ".join(w for w in re.findall(r"[a-z0-9]+", str(text or "").lower()) if w not in ("the", "a", "an", "our", "your", "to"))


def _sent_step(ctx: dict[str, Any], step: Any, company_id: Any = None) -> Any:
    """The day a promise with this step's words, to this company, was sent (Sent it on its draft), or None."""
    k = _step_key(step)
    if not k:
        return None
    for key, on in sorted((ctx.get("sent_steps") or {}).items(), key=lambda kv: str(kv[1]), reverse=True):
        co_, _, what = str(key).partition("|")
        if co_ and company_id and co_ != company_id:
            continue
        if what and (what == k or (len(k) >= 12 and (k in what or what in k))):
            return parse_date(on)
    return None


def decisions(ctx: dict[str, Any], signals: list[dict[str, Any]], deals: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    pool = deals if deals is not None else ctx["deals"]
    out: dict[str, dict[str, Any]] = {}
    met = met_recently(ctx)
    for d in pool:
        if d["stage_key"] in ("partner_meeting", "term_sheet"):
            days = (ctx["now"].date() - d["stage_entered_dt"].date()).days if d.get("stage_entered_dt") else None
            dw = stages_mod.dwell(d["stage_key"], ctx["stage_map"])
            name_ = stages_mod.label(d.get("stage_name"), False)
            at = ("At partner meeting" if re.search(r"partner|\bIC\b|committee", name_, re.I) or not name_ else
                  f"{name_[:1].upper()}{name_[1:]} stage") if d["stage_key"] == "partner_meeting" else "Term sheet out"
            why = day_phrase(at, days, dw)
            seen = met.get(d.get("company_id"))
            # A step you already did (its promise's email marked sent) is old news in the CRM: say so once, never as next.
            done_on = _sent_step(ctx, d.get("next_step"), d.get("company_id"))
            why += (f". The CRM's step, {d['next_step'].rstrip('.').lower()}, went on {fmt_short_date(done_on)}: update it" if d.get("next_step") and done_on else
                    f". Next step: {d['next_step'].rstrip('.')}" if d.get("next_step") else
                    f". Met {fmt_short_date(seen)}" if seen else ". No next step set")
            out[d["id"]] = {"deal_id": d["id"], "company": d.get("company_name"), "stage": d["stage_name"], "why": why,
                            "deadline": None, "source_url": d.get("url"), "owner": d.get("owner_email")}
    pool_ids = {d["id"] for d in pool}
    for s in signals:
        if s["deal_id"] not in pool_ids:
            continue
        row = out.get(s["deal_id"]) or {"deal_id": s["deal_id"], "company": s["company"], "stage": s["stage"],
                                        "source_url": s["source_url"], "owner": s.get("owner")}
        phrase = signal_phrase(s)
        dl = date.fromisoformat(s["deadline"]) if s.get("deadline") else None
        passed = bool(dl and dl < ctx["now"].date())
        row["why"] = phrase[:1].upper() + phrase[1:] + ((f", their deadline passed {fmt_short_date(dl)}" if passed else
                                                         f", decide by {fmt_short_date(dl)}") if dl else "")
        deal = next((d for d in pool if d["id"] == s["deal_id"]), None)
        gap = None if passed else (deadline_gap(deal, s.get("deadline"), ctx["now"].date()) if deal else None)
        if gap:
            row["why"] += f". {gap}"
            row["gap"] = gap
        row["passed"] = passed
        row["deadline"] = s.get("deadline")
        row["source_url"] = s["source_url"]
        row["breach"] = True
        out[s["deal_id"]] = row
    return sorted(out.values(), key=lambda r: (r.get("deadline") or "9999", r["company"] or ""))


def weekly_review(ctx: dict[str, Any], scope: str = "full", dwell_scale: float = 1.0) -> dict[str, Any]:
    pool = deals_for_user(ctx, scope)
    active = [d for d in pool if stages_mod.is_active(d["stage_key"], ctx["stage_map"])]
    stale = stale_deals(ctx, active, dwell_scale)
    signals = competing_signals(ctx)
    no_next = [s for s in stale if any(r["code"] == "no_next_step" for r in s["reasons"])]
    by_stage = {}
    for st in ctx["stage_map"]["stages"]:
        if st["active"]:
            by_stage[st["name"]] = sum(1 for d in active if d["stage_key"] == st["key"])
    return {
        "as_of": ctx["now"].isoformat(), "scope": scope, "active": len(active), "by_stage": by_stage,
        "moves": moves(ctx, 7, pool), "stale": stale, "decisions": decisions(ctx, signals, pool),
        "signals": [s for s in signals if s["deal_id"] in {d["id"] for d in pool}],
        "no_next_step_share": round(len(no_next) / len(active), 3) if active else 0.0,
    }


def partner_preread(ctx: dict[str, Any], inbound: list[dict[str, Any]] | None = None,
                    portfolio_flags: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    signals = competing_signals(ctx)
    return {
        "as_of": ctx["now"].isoformat(),
        "moves": moves(ctx, 7),
        "decisions": decisions(ctx, signals),
        "portfolio_flags": sorted(portfolio_flags or [], key=lambda f: (not f.get("breach"), (f.get("company") or ""))),
        "inbound": [i for i in (inbound or []) if (i.get("score") or 0) >= 70][:5],
        "sections": ["Moves this week", "Decisions needed", "Portfolio flags", "Inbound of note"],
    }
