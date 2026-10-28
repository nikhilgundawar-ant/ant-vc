"""Meeting prep cards: who, history, open promises, deal state, what colleagues know, what to ask."""

from __future__ import annotations

import re
from datetime import timedelta
from typing import Any

from . import pipeline as pipeline_mod
from . import stages as stages_mod
from .graph import open_deal_for_company
from .pipeline import day_phrase, signal_phrase
from .thesis import pass_log_hit
from .util import clean_title, clip, fmt_short_date, fmt_time, money, norm_email, parse_date, plural, sid, tzinfo

STAGE_QUESTIONS = {
    "inbound": "What made them reach out to us now, and who else are they talking to?",
    "screening": "What is the one number that proves this is working?",
    "first_meeting": "Why this team, and what have they learned that others missed?",
    "second_meeting": "Which customer can we speak to this week?",
    "diligence": "Can they share cohort retention and two customer references this week?",
    "partner_meeting": "What would change the founder's mind about the round size or timing?",
    "term_sheet": "Which terms matter most to them, and what is their deadline?",
    "closing": "What is still open for closing, and who owns each item?",
    "portfolio": "What is the one thing we can unblock for them this month?",
}


def upcoming(ctx: dict[str, Any], min_minutes: int = 30, max_minutes: int = 150, user_only: bool = True) -> list[dict[str, Any]]:
    now = ctx["now"]
    user = ctx.get("user_person")
    out = []
    for m in ctx["meetings"]:
        if not m.get("external") or not m.get("start"):
            continue
        if user_only and user and user["id"] not in m["person_ids"]:
            continue
        delta = (m["start"] - now).total_seconds() / 60
        if min_minutes <= delta <= max_minutes:
            out.append(m)
    return out


def today_meetings(ctx: dict[str, Any]) -> list[dict[str, Any]]:
    now = ctx["now"]
    user = ctx.get("user_person")
    end = now.replace(hour=23, minute=59)
    return [m for m in ctx["meetings"] if m.get("external") and m.get("start") and now - timedelta(minutes=30) <= m["start"] <= end
            and (not user or user["id"] in m["person_ids"])]


def _sentence(text: str) -> str:
    """First letter up, the rest untouched (str.capitalize would turn "MIS" into "mis")."""
    t = (text or "").strip().rstrip(".")
    return t[:1].upper() + t[1:]


def last_touch_fact(h0: dict[str, Any], company: Any = None) -> str:
    """ "Last met 20 Oct: second meeting" for a meeting, "Last spoke 21 Oct: Re: Sable" for an email. The company the
    card is about is not said twice."""
    text = str(h0.get("text") or "").strip()
    if company and text.lower().startswith(str(company).lower()):
        text = text[len(str(company)):].strip(" :-\u2013")
    if h0.get("type") == "meeting":
        return f"Last met {h0.get('date')}" + (f": {text}" if text else "")
    return f"Last spoke {h0.get('date')}" + (f": {text}" if text else "")


def _after_colon(text: str) -> str:
    """Lower case after "You owe them:", the rest untouched; an acronym ("MIS pack") keeps its capitals."""
    t = (text or "").strip().rstrip(".")
    return t[:1].lower() + t[1:] if t[:2] != t[:2].upper() else t


def internal_today(ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """Internal meetings the user attends today (partner meeting, IC): on the agenda, no prep card."""
    now = ctx["now"]
    user = ctx.get("user_person")
    end = now.replace(hour=23, minute=59)
    return [m for m in ctx["meetings"] if not m.get("external") and m.get("start") and now - timedelta(minutes=30) <= m["start"] <= end
            and (not user or user["id"] in m["person_ids"]) and len(m.get("person_ids") or []) >= 2]


def tomorrow_meetings(ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """The next working day's meetings with founders, and the partner meetings, that have prep: on a Friday, Monday's."""
    now = ctx["now"]
    user = ctx.get("user_person")
    end = prep_end(now)
    start = end.replace(hour=0, minute=0)
    return [m for m in ctx["meetings"] if (m.get("external") or is_partner_meeting(m)) and m.get("start") and start <= m["start"] <= end
            and (not user or user["id"] in (m.get("person_ids") or []))]


def card(ctx: dict[str, Any], meeting: dict[str, Any], commitments: list[dict[str, Any]], signals: list[dict[str, Any]],
         stale: list[dict[str, Any]], empathy_maps: dict[str, str] | None = None, flags: list[dict[str, Any]] | None = None,
         lp_alerts: list[dict[str, Any]] | None = None, lps: list[dict[str, Any]] | None = None,
         verdicts: dict[str, str] | None = None, asks: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    tz = ctx["tz"]
    lookup = ctx["lookup"]
    today = ctx["now"].date()
    ext = [lookup[pid] for pid in (meeting.get("external_ids") or []) if pid in lookup]
    user = ctx.get("user_person")
    user_emails = {norm_email(e) for e in (user or {}).get("emails", [])} | {norm_email(ctx.get("user_email"))}
    invited = {norm_email(a.get("email")) for a in (meeting.get("attendees") or []) if isinstance(a, dict)}
    attendees = []
    for p in ext:
        comp = ctx["companies"].get(p.get("company_id") or "", {})
        last = ctx["last_touch"].get(user["id"], {}).get(p["id"]) if user else None
        email = next((e for e in (p.get("emails") or []) if norm_email(e) in invited), (p.get("emails") or [None])[0])
        attendees.append({"id": p["id"], "name": p["name"], "email": email, "title": p.get("title"), "company": comp.get("name"),
                          "strength": (ctx["strengths"].get(user["id"], {}).get(p["id"], 0) if user else 0),
                          "last_touch": fmt_short_date(last) if last else None, "source_url": p.get("source_url")})
    ext_ids = {p["id"] for p in ext}
    history = sorted([it for it in ctx["interactions"] if ext_ids & set(it["person_ids"]) and it["date"] and it["date"] < meeting["start"]],
                     key=lambda it: it["date"], reverse=True)[:3]
    firm_name = ((ctx.get("bundle") or {}).get("firm") or {}).get("name")
    hist_rows = [{"date": fmt_short_date(it["date"]), "iso": it["date"].isoformat(), "type": it["type"],
                  "text": clip(clean_title(it.get("subject"), firm_name) if it["type"] == "meeting" else (it.get("subject") or ""), 90),
                  "source_url": it.get("url"), **({"note_id": it["transcript_id"]} if it.get("transcript_id") else {})}
                 for it in history]
    # Promises with anyone at their companies, not only the people in the room.
    comp_ids = {p.get("company_id") for p in ext if p.get("company_id")}
    comp_domains = {(ctx["companies"].get(cid) or {}).get("domain") for cid in comp_ids} - {None, ""}
    ext_emails = {norm_email(e) for p in ext for e in (p.get("emails") or [])}
    ext_names = {p["name"].lower() for p in ext}

    def at_their_company(email: Any) -> bool:
        e = norm_email(email)
        return bool(e) and (e in ext_emails or e.split("@")[-1] in comp_domains)

    open_c = []
    for c in commitments:
        if c.get("status") != "open":
            continue
        theirs = at_their_company(c.get("owed_by_email")) or (c.get("owed_to") or "").lower() in ext_names and \
            norm_email(c.get("owed_by_email")) not in user_emails
        ours = norm_email(c.get("owed_by_email")) in user_emails and (at_their_company(c.get("owed_to_email")) or (c.get("owed_to") or "").lower() in ext_names)
        if theirs or ours:
            open_c.append(c)
    deal = next((open_deal_for_company(ctx, cid) for cid in comp_ids if open_deal_for_company(ctx, cid)), None)
    deal_row = None
    seeds: list[str] = []
    watch = None
    if deal:
        days_in = (ctx["now"].date() - deal["stage_entered_dt"].date()).days if deal.get("stage_entered_dt") else None
        dw = stages_mod.dwell(deal["stage_key"], ctx["stage_map"])
        deal_row = {"id": deal["id"], "company": deal.get("company_name"), "stage": stages_mod.label(deal["stage_name"]), "days_in_stage": days_in,
                    "dwell": dw, "next_step": deal.get("next_step"), "source_url": deal.get("url"),
                    "step_went": (lambda w_: w_.isoformat() if w_ else None)(pipeline_mod._sent_step(ctx, deal.get("next_step"), deal.get("company_id")))}
        if STAGE_QUESTIONS.get(deal["stage_key"]):
            seeds.append(STAGE_QUESTIONS[deal["stage_key"]])
        sig = next((s for s in signals if s["deal_id"] == deal["id"]), None)
        if sig:
            what = signal_phrase(sig)
            what = what[:1].upper() + what[1:]
            dl = parse_date(sig.get("deadline"))
            watch = what + (f". Decide by {fmt_short_date(dl)}" if dl else "")
            seeds.insert(0, "Another fund is moving: ask where their process stands" + (f" and confirm the {fmt_short_date(dl)} deadline" if dl else ""))
        st = next((s for s in stale if s["deal_id"] == deal["id"]), None)
        if st and any(r["code"] in ("no_next_step", "next_step_overdue") for r in st["reasons"]):
            seeds.append("Leave with a dated next step")
    rows = []
    for c in open_c:
        due = parse_date(c.get("due"))
        what = _sentence(c["what"])
        mine = norm_email(c.get("owed_by_email")) in user_emails
        overdue = bool(due and due < today)
        done = c.get("looks_done")  # sent mail or a booked meeting says it is done: listed, never raised
        rows.append({"id": c.get("id"), "what": c["what"], "owed_by": c["owed_by"], "due": c.get("due"), "side": "us" if mine else "them",
                     "overdue": overdue and not done, "looks_done": done or None, "source_url": c.get("source_url")})
        if done:
            continue
        if not mine:
            seeds.insert(0, f"Follow up: {what}" + (f" (promised for {fmt_short_date(due)})" if due else ""))
        else:
            seeds.insert(0, f"You owe them: {_after_colon(what)}" + (f" (due {fmt_short_date(due)})" if due else ""))
    colleagues = []
    for mid in ctx["member_ids"]:
        if user and mid == user["id"]:
            continue
        for p in ext:
            last = ctx["last_touch"].get(mid, {}).get(p["id"])
            strength = ctx["strengths"].get(mid, {}).get(p["id"], 0)
            if last or strength >= 30:
                colleagues.append({"colleague": lookup[mid]["name"], "person": p["name"],
                                   "last_touch": fmt_short_date(last) if last else None, "strength": strength})
    colleagues.sort(key=lambda c: -(c.get("strength") or 0))
    empathy = None
    if empathy_maps:
        for p in ext:
            empathy = empathy_maps.get(p["name"].lower()) or empathy
    # A company we passed on before: the pass reason and the revisit trigger matter in the room.
    pass_note = None
    pass_verdict = False
    passes = (ctx.get("bundle") or {}).get("passes") or []
    for cid in comp_ids:
        comp = ctx["companies"].get(cid) or {}
        hit = pass_log_hit({"name": comp.get("name") or "", "domain": comp.get("domain")}, passes) if comp else None
        if hit:
            when = parse_date(hit.get("date"))
            verdict = (verdicts or {}).get(str(comp.get("domain") or "").lower())
            passed = f"we passed on {fmt_short_date(when)}: {(hit.get('reason') or '').strip().rstrip('.').lower()}"
            # What they have done since comes first: the bar we set when we passed, met or not.
            pass_note = f"{verdict}. {_sentence(passed)}" if verdict else f"We passed on {fmt_short_date(when)}: {_sentence(hit.get('reason') or '')}" + \
                (f". Revisit if: {_sentence(hit['revisit_trigger'])}" if hit.get("revisit_trigger") else "")
            pass_verdict = bool(verdict)
            if hit.get("revisit_trigger") and not verdict:
                seeds.insert(0, f"Has the revisit trigger happened: {_sentence(hit['revisit_trigger'])}?")
            break
    # Portfolio and LP context for meetings with no open deal.
    flag_note = None
    flag_cid = None
    cash_flag = None
    board_q = None
    for f in flags or []:
        if f.get("company_id") in comp_ids:
            flag_cid = f.get("company_id")
            flag_note = f"{f.get('headline')}: {f.get('detail')}"
            seeds.insert(0, f"{f.get('headline')} ({f.get('detail')}): what is the plan?")
            cash_flag = f if f.get("kind") in ("runway", "burn") else None
            break
    lp_note = None
    lp_id = None
    for l in lps or []:
        if {norm_email(e) for e in (l.get("contacts") or [])} & ext_emails:
            lp_id = l.get("id")
            start = parse_date(l.get("reup_window_start"))
            called, paid = l.get("called_usd"), l.get("paid_in_usd")
            owed = called - paid if isinstance(called, (int, float)) and isinstance(paid, (int, float)) and called - paid >= 1 else 0
            parts = [f"{money(l['commitment_usd'])} committed" if l.get("commitment_usd") else None,
                     f"{money(owed)} still due on a capital call" if owed else f"{money(called)} called" if isinstance(called, (int, float)) else None,
                     f"re-up window opens {fmt_short_date(start)}" if start else None]
            lp_note = "LP: " + ", ".join(x for x in parts if x) if any(parts) else None
            seeds.append("What will your committee need from us before the re-up decision?")
            break
    ours_overdue = [r for r in rows if r["side"] == "us" and r["overdue"]]
    theirs_overdue = [r for r in rows if r["side"] == "them" and r["overdue"]]
    live = [r for r in rows if not r.get("looks_done")]
    # Most important first: the watch line, what we owe, what they owe, the pass, a flag, an LP, the stage. Each fact
    # carries the subject it is about, so a heads-up skips what that morning's push already named.
    facts: list[tuple[str, ...]] = []  # (text, key) or (text, key, kind)
    deal_key = f"deal:{deal['id']}" if deal else "deal:-"
    if watch:
        facts.append((watch, deal_key))
    if ours_overdue:
        r = ours_overdue[0]
        late = (today - parse_date(r["due"])).days if parse_date(r.get("due")) else 0
        facts.append((f"You owe them: {_after_colon(r['what'])}, " + (f"{plural(late, 'day')} late" if late > 0 else f"due {fmt_short_date(parse_date(r['due']))}"),
                      f"commitment:{r.get('id')}", "owe" if late > 0 else "owe_soon"))
    if pass_note and pass_verdict:
        facts.append((pass_note, f"pass:{sorted(comp_ids)[0] if comp_ids else '-'}"))  # whether a returning company met our bar
    ask = next((a for a in asks or [] if a.get("company_id") in comp_ids and a.get("status") != "done"), None)
    if ask:  # a founder's open ask is the thing to solve in the room
        who = str(ask.get("who") or "").split(" ")[0] if ask.get("who") and str(ask.get("who")).lower() != "the founder" else "They"
        asked = parse_date(ask.get("date"))
        text_ = str(ask.get('ask') or '').strip().rstrip('.')
        hiring = bool(re.search(r"\b(hire|hiring|engineers?|recruit)", text_, re.I))
        if cash_flag and hiring:
            # Cash first: whether to help them hire at all is the board's question, so the runway leads the card.
            facts.append((flag_note, f"flag:{flag_cid}"))
        p0 = (ask.get("paths") or [None])[0] or {}
        path = f"{p0['colleague']} {'know' if p0['colleague'] == 'You' else 'knows'} {p0['person']}" if p0.get("colleague") and p0.get("person") else None
        # What the push says when the full line does not fit: "Divya needs two banks as customers: Aditi knows Raj Malhotra".
        core = re.sub(r"^(an? )?(introductions?|intros?) to ", "", text_, flags=re.I)
        # Where the ask stands, as a promise's line says "Draft ready": the note is ready, out, or the intro was made.
        ns = ask.get("note_state") or {}
        on_ = parse_date(ns.get("on"))
        quiet_ = ", no reply yet" if ns.get("quiet") else ""
        what_ = "nudge" if ns.get("nudge") else "note"
        state = (f"intro made on {fmt_short_date(on_)}" if ns.get("state") == "made" and on_ else
                 f"{ns.get('label')} on {fmt_short_date(on_)}{quiet_}" if ns.get("state") == "sent" and on_ else
                 f"{what_} to {ns['to']} ready" if ns.get("state") == "ready" and ns.get("to") else
                 f"{what_} ready" if ns.get("state") == "ready" else "")
        tail = f". {state[:1].upper()}{state[1:]}" if state else ""
        needs = f"{who} needs {core[:1].lower()}{core[1:]}"
        if ns.get("state") in ("made", "sent") and state:
            # "Divya needs two banks as customers: asked Aditi on 22 Oct"
            short = f"{needs}: " + (f"{ns.get('short_label')} on {fmt_short_date(on_)}{quiet_}" if ns.get("state") == "sent" and ns.get("short_label") else state)
        elif path:
            short = f"{needs}: {path}{tail}"  # "...: Aditi knows Raj Malhotra. Note to Aditi ready"
        else:
            short = f"{needs}: {state}" if state else None
        facts.append((f"{who} asked: {text_[:1].lower()}{text_[1:]}" + (f" ({fmt_short_date(asked)})" if asked else "") +
                      (f". {path}" if path and ns.get("state") not in ("made", "sent") else "") + tail,
                      f"ask:{ask.get('id') or ask.get('company_id')}",
                      {"kind": "ask", **({"short": short} if short else {})}))
        if cash_flag and hiring:
            # The board's question, as the partner's own decision; the plain runway seed would only say it twice.
            board_q = f"With {cash_flag.get('detail')}, do we help them hire now, or wait?"
            seeds[:] = [x for x in seeds if not x.endswith("): what is the plan?") or not x.startswith(str(cash_flag.get("headline")))]
            seeds.insert(0, board_q)
        else:
            seeds.insert(0, f"What would help most with {text_[:1].lower()}{text_[1:]}?" if text_ else "What would help most with your ask?")
    ours_soon = [r for r in live if r["side"] == "us" and not r["overdue"] and r.get("due") and parse_date(r["due"]) and
                 (parse_date(r["due"]) - today).days <= 2]
    if ours_soon and not ours_overdue:
        r = ours_soon[0]
        facts.append((f"You owe them: {_after_colon(r['what'])}, due {fmt_short_date(parse_date(r['due']))}", f"commitment:{r.get('id')}",
                      "owe_soon"))  # due, not late: it leads a heads-up only as news
    if theirs_overdue:
        r = theirs_overdue[0]
        what = _sentence(r["what"])
        late = (today - parse_date(r["due"])).days if parse_date(r.get("due")) else 0
        facts.append((f"{(r.get('owed_by') or 'They').split()[0]} owes you: {what[:1].lower() + what[1:]}, " +
                      (f"{late} day{'s' if late != 1 else ''} late" if late > 0 else f"due {fmt_short_date(parse_date(r['due']))}"),
                      f"commitment:{r.get('id')}"))
    for note, key in ((None if pass_verdict else pass_note, f"pass:{sorted(comp_ids)[0] if comp_ids else '-'}"),
                      (flag_note, f"flag:{flag_cid}"), (lp_note, f"lp:{lp_id}")):
        if note and not any(f_[1] == key for f_ in facts):
            facts.append((note, key))
    if deal_row and deal_row["days_in_stage"] is not None:
        nstep = str(deal_row.get("next_step") or "").strip().rstrip(".")
        went_ = parse_date(deal_row.get("step_went"))
        if nstep and went_:
            facts.append((day_phrase(stages_mod.label(deal_row["stage"]), deal_row["days_in_stage"], deal_row.get("dwell")) +
                          f". The CRM's step, {nstep[:1].lower() + nstep[1:]}, went on {fmt_short_date(went_)}: set the next one after this meeting", deal_key))
        elif nstep and _is_next_step(nstep, meeting, deal, tz):
            # This meeting is the next step: say so, never "12 days in first meeting" an hour before the second one.
            facts.append((f"Next step today: {nstep[:1].lower() + nstep[1:]}, after {plural(deal_row['days_in_stage'], 'day')} in "
                          f"{stages_mod.label(deal_row['stage'], False)}", deal_key))
        else:
            facts.append((day_phrase(stages_mod.label(deal_row["stage"]), deal_row["days_in_stage"], deal_row.get("dwell")) +
                          (f". Next step: {nstep}" if nstep else ". Set a next step after this meeting"), deal_key))
    if hist_rows:
        facts.append((last_touch_fact(hist_rows[0], next((p_.get("company") for p_ in attendees if p_.get("company")), None)),
                      f"history:{meeting['id']}"))
    lead = ext[0] if ext else None
    lead_comp = ctx["companies"].get((lead or {}).get("company_id") or "", {})
    if not facts and lead:  # someone new: the heads-up still says who, so no meeting goes without one
        title_ = (attendees[0].get("title") if attendees else None) or None
        facts.append((f"First meeting with {lead['name']}" + (f", {title_}" if title_ else "") + (f" at {lead_comp['name']}" if lead_comp.get("name") else ""),
                      f"meeting:{meeting['id']}"))
    finding = facts[0][0] if facts else None
    second = facts[1][0] if len(facts) > 1 else None
    if board_q and finding and not finding.startswith(str((cash_flag or {}).get("headline") or "")):
        second = board_q  # the room's question, under what you owe them: runway and the hiring ask together, yours to call
    sections = sum(1 for x in (hist_rows, rows, deal_row, colleagues, watch or flag_note or lp_note or pass_note) if x)
    # A group event (several companies around one table) goes by its own title, not by whoever is listed first.
    group = len({p.get("company_id") for p in ext if p.get("company_id")}) > 1
    return {
        "id": sid("prep", meeting["id"], prefix="m"), "meeting_id": meeting["id"], "title": meeting.get("title"),
        "start": meeting["start"].isoformat(), "time": fmt_time(meeting["start"], tz), "attendees": attendees,
        "who": meeting.get("title") if group and meeting.get("title") else
               f"{lead['name']}, {lead_comp.get('name')}" if lead and lead_comp.get("name") else (lead["name"] if lead else meeting.get("title")),
        "history": hist_rows, "open_commitments": rows, "watch": watch, "context": flag_note or lp_note or pass_note,
        "deal": deal_row, "colleagues": colleagues[:4], "question_seeds": list(dict.fromkeys(seeds))[:6], "questions": [],
        **({"board_question": board_q} if board_q else {}),
        "empathy_map_url": empathy, "finding": finding, "second": second, "prepared_count": max(1, sections),
        "facts": [{"text": f_[0], "key": f_[1], **((f_[2] if isinstance(f_[2], dict) else {"kind": f_[2]}) if len(f_) > 2 else {})}
                  for f_ in facts[:5]],
        "source_url": meeting.get("url"), "company_ids": sorted(c for c in comp_ids if c),
    }


STEP_STOP = {"call", "meeting", "with", "the", "and", "on", "for", "a", "an", "to", "of", "set", "up", "book", "schedule", "next"}


def _is_next_step(step: str, meeting: dict[str, Any], deal: dict[str, Any] | None, tz: str | None) -> bool:
    """The meeting is the deal's next step: its title holds every word of the step ("Second meeting" and "Halo
    Reconcile: second meeting"), or the step is due the day of the meeting."""
    words_ = {w for w in re.findall(r"[a-z0-9]+", step.lower()) if w not in STEP_STOP}
    title = set(re.findall(r"[a-z0-9]+", str(meeting.get("title") or "").lower()))
    if words_ and words_ <= title:
        return True
    due = (deal or {}).get("next_step_due_dt")
    start = meeting.get("start")
    if due and start:
        local = start.astimezone(tzinfo(tz)) if tz else start
        return due.date() == local.date() if hasattr(due, "date") else False
    return False


PARTNER_RE = re.compile(r"\b(partners?'?\s*(meeting|sync|call|review)|ic|investment committee|deal review|pipeline (review|meeting)|"
                        r"monday meeting)\b", re.I)
LATE = ("diligence", "partner_meeting", "term_sheet", "closing")


def is_partner_meeting(meeting: dict[str, Any]) -> bool:
    return not meeting.get("external") and bool(PARTNER_RE.search(str(meeting.get("title") or "")))


def partner_card(ctx: dict[str, Any], meeting: dict[str, Any], decisions: list[dict[str, Any]], stale: list[dict[str, Any]],
                 commitments: list[dict[str, Any]]) -> dict[str, Any]:
    """A partner sync or IC on the calendar: each deal to decide with why now, and the promises inside the team.
    Quiet deals stay out: this list is what the user brings into the room."""
    tz = ctx["tz"]
    today = ctx["now"].date()
    lookup = ctx["lookup"]
    deal_by_id = {d["id"]: d for d in ctx["deals"]}
    user_emails = {norm_email(e) for e in ((ctx.get("user_person") or {}).get("emails") or [])} | {norm_email(ctx.get("user_email"))}
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    quiet_left = 0

    members = {norm_email(m.get("email")): m.get("name") for m in ctx.get("members") or [] if isinstance(m, dict) and m.get("email")}
    members.update({k: v for k, v in (ctx.get("colleagues") or {}).items() if v})

    def owner_name(email: Any) -> str | None:
        hit = lookup.get(norm_email(email)) if email else None
        return (hit or {}).get("name") or (members.get(norm_email(email)) if email else None)

    def sponsor(d: dict[str, Any]) -> str | None:
        return pipeline_mod.sponsor(ctx, d)

    def add(deal_id: str, company: str, why: str, url: Any, urgent: bool = False, deadline: Any = None, passed: bool = False,
            stalled: bool = False) -> None:
        nonlocal quiet_left
        d = deal_by_id.get(deal_id) or {}
        if deal_id in seen:
            return
        seen.add(deal_id)
        if d.get("quiet"):
            quiet_left += 1
            return
        stage = stages_mod.label(d["stage_name"]) if d.get("stage_name") else None
        if stage and re.match(r"^(term sheet out|at partner meeting)\b", str(why), re.I):
            stage = None  # "Term sheet out, day 4 of 10" already says the stage; another fund's term sheet does not
        vote = d.get("stage_key") in ("partner_meeting", "term_sheet")
        rows.append({"deal_id": deal_id, "company": company, "stage": stage, "why": why,
                     "owner": owner_name(d.get("owner_email")), "partner": sponsor(d), "round": d.get("round"),
                     "raise_usd": d.get("raise_usd"), "deadline": deadline, "urgent": urgent,
                     "kind": "rival" if urgent else "vote" if vote and not stalled else "stalled",
                     "vote": vote, "passed": passed, "source_url": url or d.get("url")})

    mday = meeting["start"].date() if meeting.get("start") else today
    for x in decisions:  # ordered by deadline: the competitor and the date come with each
        add(x["deal_id"], x["company"], x["why"], x.get("source_url"), bool(x.get("breach")), x.get("deadline"), bool(x.get("passed")))
    # A card for a later day (Friday's for Monday): another fund's date that passes before the room meets is decided
    # before then, by whoever sponsors it. The card says so, keeps it at the end, and leads with what the room decides.
    for r_ in rows:
        dl_ = parse_date(r_.get("deadline")) if not r_.get("passed") else None
        if mday > today and dl_ and dl_ < mday:
            r_["before"] = True
            who_ = str(r_.get("partner") or r_.get("owner") or "").split(" ")[0]
            if who_ and who_ == str((ctx.get("user_person") or {}).get("name") or "").split(" ")[0]:
                who_ = ""  # your own deal: you decide it
            # The date once: the rest of the line keeps what is happening, not the deadline again.
            rest_ = re.sub(r",?\s*decide by \d{1,2} [A-Z][a-z]{2}\b", "", str(r_["why"]))
            rest_ = re.sub(r"\.?\s*Their deadline \d{1,2} [A-Z][a-z]{2} is before your next step[^.]*\.?", "", rest_).strip().rstrip(".")
            r_["why"] = f"Deadline {fmt_short_date(dl_)} passes before this meeting: decide by then" + (f" with {who_}" if who_ else "") + \
                (f". {rest_}" if rest_ else "")
    for st in stale:
        if st["stage_key"] in LATE:
            add(st["deal_id"], st["company"], st["reasons"][0]["text"], st.get("source_url"), stalled=True)
    # Each row says who leads it, which partner sponsors it, and the round: the room reads one list.

    def rank(r: dict[str, Any]) -> tuple:
        # Another fund's date first, then rivals racing with no date, then the votes and term sheets this room exists
        # for; late-stage deals that stalled come last, as their own list, not as decisions. A date that passes before
        # the meeting comes after the room's own decisions.
        if r.get("before"):
            return (2.5, r.get("deadline") or "")
        if r["kind"] == "rival" and r.get("deadline") and not r.get("passed"):
            return (0, r["deadline"])
        if r["kind"] == "rival":
            return (1, "")
        if r["kind"] == "vote":
            return (2, "")
        return (3, "")
    rows.sort(key=rank)
    rows = rows[:12]  # every deal up for a vote or racing a rival; the rest waits for the pipeline review
    to_decide = [r for r in rows if r["kind"] != "stalled" and not r.get("before")] + [r for r in rows if r.get("before")]
    promises = []
    for c in commitments:
        if c.get("status") != "open" or not c.get("internal"):
            continue
        mine = norm_email(c.get("owed_by_email")) in user_emails
        to_me = norm_email(c.get("owed_to_email")) in user_emails
        if not (mine or to_me):
            continue
        due = parse_date(c.get("due"))
        promises.append({"what": c["what"], "owed_by": c.get("owed_by"), "due": c.get("due"), "side": "us" if mine else "them",
                         "overdue": bool(due and due < today), "source_url": c.get("source_url")})
    promises.sort(key=lambda r: (not r["overdue"], r.get("due") or "9999"))

    def short(r: dict[str, Any]) -> str:
        dl = parse_date(r.get("deadline"))
        if r.get("before"):
            return r["company"] + (f", deadline {fmt_short_date(dl)} before this meeting" if dl else "")
        return r["company"] + (f", by {fmt_short_date(dl)}" if dl else "")

    if to_decide:
        dl0 = parse_date(to_decide[0].get("deadline")) if not to_decide[0].get("passed") and not to_decide[0].get("before") else None
        finding = f"Decide on {to_decide[0]['company']}" + (f" by {fmt_short_date(dl0)}" if dl0 else "") + \
            (f", and {len(to_decide) - 1} more" if len(to_decide) > 1 else "")
        second = f"{to_decide[0]['company']}: {to_decide[0]['why']}"
        # The heads-up after a morning that named the first deal: the rest of the list, by name, in one short line.
        names = [r["company"] for r in to_decide[1:]]
        shown: list[str] = []
        for n in names:
            if len(", ".join(shown + [n])) > 30:
                break
            shown.append(n)
        rest = len(names) - len(shown)
        also = (f"{to_decide[0]['company']} first, then " + ", ".join(shown) + (f" and {rest} more" if rest else "")) if shown else None
        if also and not rest and len(shown) > 1:
            also = f"{to_decide[0]['company']} first, then " + ", ".join(shown[:-1]) + f" and {shown[-1]}"
    else:
        finding = "No deal needs a decision this week"
        second = None
        also = None
    def question(r: dict[str, Any]) -> str:
        """One question per deal, from its own facts: the rival, the date, the round, our next step."""
        dl = parse_date(r.get("deadline"))
        why = str(r.get("why") or "")
        low = why.lower()
        co = r["company"]
        rnd = " ".join(x for x in (r.get("round"), money(r["raise_usd"]) if r.get("raise_usd") else None) if x)
        lead = str(r.get("owner") or "").split(" ")[0] or "the lead"
        fund = re.search(r"^\s*([A-Z][\w&.' ]+?)\s+(?:wants to lead|is moving)", why) or \
            re.search(r"(?i:term sheet from) ([A-Z][\w&.' ]+?)(?:,|\.|$)", why)
        fund_name = fund.group(1).strip() if fund else None
        when = f" by {fmt_short_date(dl)}" if dl and not r.get("passed") else ""
        if r.get("passed"):
            return f"{co}: their date has passed. Is the round gone, or does {lead} call the founder today?"
        if r.get("before"):
            return f"{co}: the founder wanted our answer by {fmt_short_date(dl)}, before this meeting. Did we give one, and are we still in?"
        if "term sheet from" in low:
            return (f"{co}: {fund_name or 'another fund'} has a term sheet out" + (f" and the founder decides{when}" if when else "") +
                    ". Do we move first, or step back?")
        if "wants to lead" in low:
            return f"{co}: {fund_name or 'another fund'} wants to lead" + (f" the {rnd}" if rnd else "") + ". Do we offer to co-lead, or follow?"
        if "offers" in low or "other funds" in low:
            return f"{co}: other funds are moving" + (f" and the founder decides{when}" if when else "") + ". What would make ours the offer they take?"
        if "filling" in low or "oversubscribed" in low:
            return f"{co}: the round is filling up. Do we hold an allocation this week, and does {lead} make the call?"
        if "term sheet out" in low:
            return f"{co}: our term sheet is out" + (f" ({rnd})" if rnd else "") + ". What is still open before they sign?"
        if "partner meeting" in low or "vote" in low or " ic" in f" {low}":
            return f"{co}: what is missing for a yes" + (f" on the {rnd}" if rnd else "") + ", and who votes?"
        return f"{co}: {low[:1] + why[1:] if why else 'it has stalled'}. Push it this week, or pass?"
    # Below partner, the user's own deals in the room's list come first: those are the ones they must raise.
    mine_ = [r for r in rows if norm_email((deal_by_id.get(r.get("deal_id")) or {}).get("owner_email")) in user_emails]
    ranked_ = mine_ + [r for r in rows if r not in mine_] if ctx.get("level") not in (None, "partner", "solo_gp") else rows
    seeds = [question(r) for r in ranked_[:3]]
    others = [lookup[pid] for pid in (meeting.get("person_ids") or []) if pid in lookup and
              not ({norm_email(e) for e in (lookup[pid].get("emails") or [])} & user_emails)]
    return {
        "id": sid("prep", meeting["id"], prefix="m"), "meeting_id": meeting["id"], "kind": "partner", "title": meeting.get("title"),
        "start": meeting["start"].isoformat(), "time": fmt_time(meeting["start"], tz), "who": meeting.get("title") or "Partner meeting",
        "attendees": [{"id": p["id"], "name": p["name"], "title": p.get("title"), "company": None, "strength": None} for p in others][:8],
        "decisions": rows, "open_commitments": promises[:6], "history": [], "watch": None, "context": None, "deal": None,
        "colleagues": [], "question_seeds": seeds, "questions": [], "empathy_map_url": None, "finding": finding, "second": second,
        "facts": [{"text": t, "key": k} for t, k in ((finding, f"deal:{to_decide[0]['deal_id']}" if to_decide else f"meeting:{meeting['id']}"),
                                                      (also, f"meeting:{meeting['id']}:also")) if t],
        "prepared_count": max(1, len(rows)), "quiet_left_out": quiet_left, "source_url": meeting.get("url"),
        # This user's own deals in the room's list: their heads-up and agenda line name them.
        "yours": [r["company"] for r in to_decide if norm_email((deal_by_id.get(r["deal_id"]) or {}).get("owner_email")) in user_emails],
        "agenda_notes": ([f"Decide: {short(r)}" for r in to_decide[:3]] if len(to_decide) <= 3 else
                         [f"Decide: {short(r)}" for r in to_decide[:2]] + [f"And {len(to_decide) - 2} more to decide"]) or ["No deal needs a decision"],
    }


def prep_end(now):
    """How far prep reaches: the end of the next working day, so a Friday preps Monday's meetings before the weekend."""
    d = now.date() + timedelta(days=1)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return now.replace(year=d.year, month=d.month, day=d.day, hour=23, minute=59, second=0, microsecond=0)


def partner_meetings(ctx: dict[str, Any], hours: int = 36) -> list[dict[str, Any]]:
    """Partner syncs and ICs the user attends from now to the end of the next working day."""
    now = ctx["now"]
    user = ctx.get("user_person")
    end = prep_end(now)
    return [m for m in ctx["meetings"] if is_partner_meeting(m) and m.get("start") and now - timedelta(minutes=30) <= m["start"] <= end
            and (not user or user["id"] in (m.get("person_ids") or []))]
