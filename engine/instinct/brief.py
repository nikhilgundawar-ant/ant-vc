"""The morning brief: gather candidate items, rank them for the user's level, fit the word budget, pick the hero."""

from __future__ import annotations

import re
from datetime import timedelta
from typing import Any

from . import network as network_mod
from . import stages as stages_mod
from .pipeline import deadline_gap, signal_phrase, sponsor
from .pipeline import working_days_since as pipeline_working_days
from .util import (clip, draft_gaps, fit_sentences, join_sentences, fmt_date, fmt_short_date, fmt_time, money, norm_email, parse_date,
                   parse_dt, plural, sid, tzinfo, words)

KIND_GROUP = {
    "meeting": "meeting", "commitment": "commitment", "waiting": "commitment", "question": "commitment", "signal": "signal", "stale": "deal_move",
    "deal_move": "deal_move", "decision": "decision", "inbound": "inbound", "pass_returned": "inbound",
    "portfolio": "portfolio", "board": "portfolio", "ask": "ask", "lp": "lp", "relationship": "relationship",
    "review": "relationship",
}
SECTION_OF = {
    "commitment": "commitments", "waiting": "commitments", "question": "commitments", "signal": "signals", "portfolio": "signals", "lp": "signals",
    "board": "signals", "stale": "deals", "deal_move": "deals", "decision": "decide", "inbound": "inbound",
    "pass_returned": "inbound", "relationship": "people", "review": "people", "meeting": "meetings", "ask": "asks",
}
SECTION_LABEL = {
    "decide": "One thing to decide", "commitments": "Commitments due", "signals": "Signals", "deals": "Pipeline",
    "inbound": "Inbound worth a look", "people": "People", "meetings": "Meetings today", "asks": "Founders need",
    "team": "Waiting on your team",
}
SECTION_ORDER = ["decide", "commitments", "team", "signals", "asks", "deals", "inbound", "people"]
NEXT_UP = 4
INBOUND_CAP = 5
# The word shown beside every row. Breach is kept for a figure past its threshold; work uses Urgent, High, Medium, Low.
PRIORITY_WORD = {"urgent": "urgent", "high": "high", "medium": "medium", "low": "low"}
GLYPH = {"urgent": "breach", "high": "high", "medium": "medium", "low": "low"}


def item_id(kind: str, key: Any) -> str:
    """The id Home uses for a row's snooze, done mark and rating. Other views use it to mark the same thing."""
    return sid(kind, key, prefix="t")


# An ask's notes: the first one (to the warm path, the board partner or the team), then the taps that follow it in
# Home once that note went out: "Aditi said yes: draft the intro ask" (`_intro`) and "Ask the team instead" or "Aditi
# said yes: ask the team" (`_team`). A note with no reply in five working days gets one nudge, drafted by the morning
# run: `_nudge` for the first note, `_intro_nudge` for the intro ask, `_team_nudge` for the team note.
ASK_NOTE_SUFFIXES = ("", "_intro", "_team", "_nudge", "_intro_nudge", "_team_nudge")


FIRM_VIEW = re.compile(r"\b(feedback|view|views|thoughts|decision)\b", re.I)


def view_holder(ctx: dict[str, Any], what: Any, company_id: Any) -> str | None:
    """Who holds the firm's view a promise shares: the deal's sponsoring partner, when that is someone else."""
    if not company_id or not FIRM_VIEW.search(str(what or "")):
        return None
    deal_ = next((d_ for d_ in ctx.get("deals") or [] if d_.get("company_id") == company_id), None)
    sp_ = sponsor(ctx, deal_) if deal_ else None
    me_name = str((ctx.get("user_person") or {}).get("name") or "")
    return sp_ if sp_ and sp_.split(" ")[0].lower() != me_name.split(" ")[0].lower() else None


def gaps_line(n: int, holder: str | None = None) -> str:
    """What a draft with blanks needs before it goes: "Draft has 3 lines to fill: check the firm's view with Aditi"."""
    if not n:
        return ""
    return f"Draft has {plural(n, 'line')} to fill" + (f": check the firm's view with {str(holder).split(' ')[0]}" if holder else "")


def _answers(rep: Any, note: Any) -> bool:
    """A reply Home keeps answers this note: recorded against it (`tap`), or newer than when it was marked sent."""
    if not isinstance(rep, dict) or not isinstance(note, dict) or not rep.get("on"):
        return False
    return bool((rep.get("tap") and rep.get("tap") == note.get("tap")) or str(rep.get("on") or "") > str(note.get("at") or ""))


def _and(names: list[str]) -> str:
    names = [n for n in names if n]
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + f" and {names[-1]}" if names else ""


def ask_sent(sent_drafts: dict[str, Any] | None, aid: Any, first: bool = False) -> dict[str, Any] | None:
    """The latest note sent for an ask (or the first, when `first`), across its first note and the ones after it,
    with the tap it answered."""
    xs = []
    for suf in ASK_NOTE_SUFFIXES:
        s_ = (sent_drafts or {}).get(f"{aid}{suf}")
        if isinstance(s_, str):
            s_ = {"at": s_, "note_kind": "contact"}
        if s_:
            xs.append({**s_, "tap": f"{aid}{suf}"})
    xs.sort(key=lambda x: str(x.get("at") or ""))
    return (xs[0] if first else xs[-1]) if xs else None


def nudge_tap(sent: dict[str, Any] | None) -> str | None:
    """The tap of the one nudge a sent note can get: none once that note was itself a nudge."""
    tap = str((sent or {}).get("tap") or "")
    return f"{tap}_nudge" if tap and not tap.endswith("_nudge") else None


def ask_view(a: dict[str, Any], parts: dict[str, Any], today: Any) -> dict[str, Any]:
    """Where a founder ask stands, said the same on its row, the Portfolio hero, a push and the line under a meeting:
    the introduction made; a note of yours ready to send (the next one, after the board partner said yes or a colleague
    went quiet, or a nudge); a note out, and to whom; a nudge after five quiet working days; then, when the nudge too
    goes unanswered, the way round."""
    aid = a.get("item_id")
    by_action = parts.get("drafts_by_action") or {}
    sent_drafts = parts.get("sent_drafts") or {}
    sent = ask_sent(sent_drafts, aid)
    # A nudge counts only for the note it follows: once a later note went out, a nudge still waiting is moot.
    nudge_ = nudge_tap(sent)
    follow = (parts.get("ask_follow") or {}).get(aid) or []
    yes = next((f for f in follow if (f.get("after") or {}).get("kind") == "board"), None)
    # A next note the user tapped after the latest one went out ("Aditi said yes: ask the team", "Ask the team instead")
    # takes the ask out of any nudge: the nudge asks a question the user already answered.
    tap_now = str((sent or {}).get("tap") or "")
    chosen = [f for f in follow if f.get("id") not in sent_drafts and not tap_now.startswith(str(f.get("id")))]
    if chosen:
        nudge_ = None
    # The note the user chose after the first (the team, the intro ask) before a nudge written earlier: the later choice
    # leads, and Home picks by the same order.
    ready_tap = next((t for t in [f"{aid}{suf}" for suf in ("_team", "_intro")] + ([nudge_] if nudge_ else []) + [f"{aid}"]
                      if aid and t in by_action and t not in sent_drafts), None)
    ready = by_action.get(ready_tap) if ready_tap else None
    v: dict[str, Any] = {"word": "asked", "label": None, "lead": "", "short": None, "state": "", "draft": ready, "weight": 0, "rank": 2}
    if a.get("made_on"):  # the introduction went out: one tap on Done closes the ask
        made_ = fmt_short_date(parse_date(a["made_on"]))
        return {**v, "word": "made", "label": "Intro made", "lead": f"Intro made on {made_}. ", "draft": None,
                "short": f"intro made on {made_}", "state": f"Intro made on {made_}", "weight": -25, "rank": 4}
    at = parse_dt((sent or {}).get("at"))
    to_first = str((sent or {}).get("to_name") or "").split(" ")[0]
    kind = (sent or {}).get("note_kind")
    tap = str((sent or {}).get("tap") or "")
    # What a nudge followed: the board partner, a colleague, a contact or the team.
    base = (sent_drafts.get(tap[:-len("_nudge")]) if tap.endswith("_nudge") else sent) or {}
    base_kind = base.get("note_kind") if isinstance(base, dict) else "contact"
    # Asks that went out in one note wait on one reply: they are nudged together, in one note.
    group = [x for x in parts.get("asks") or [] if isinstance(x, dict) and x.get("status") != "done" and not x.get("made_on") and sent and
             sent.get("draft") and (ask_sent(sent_drafts, x.get("item_id")) or {}).get("draft") == sent.get("draft") and
             not _answers(x.get("replied"), sent)]
    v["group"] = sent.get("draft") if sent and len(group) > 1 else None
    many = f": one note for {len(group)} asks" if v["group"] else ""
    who_ = "the team" if base_kind == "team" else (to_first or "them")
    # A reply from whoever the note went to, after it went: no nudge. A next note the user asked for still leads.
    replied = a.get("replied") if isinstance(a.get("replied"), dict) else None
    answered = bool(sent and _answers(replied, sent))
    # A reply that put off its answer ("let me think and come back to you"): five quiet working days on, it is nudged.
    put_off = bool(answered and replied.get("defers") and parse_dt(replied.get("on")) and
                   pipeline_working_days(parse_dt(replied["on"]).date(), today) >= 5)
    # They answered the note's other asks, not this one: never "no reply", since a reply came.
    others = a.get("answered_others") if isinstance(a.get("answered_others"), dict) else None
    others = others if sent and not answered and _answers(others, sent) else None
    part_ = (f"{str(others.get('by') or to_first or 'They').split(' ')[0]} answered on {_and(others.get('named') or [])} on "
             f"{fmt_short_date(parse_dt(others.get('on')))}, not this one") if others else ""
    if ready and ready_tap == nudge_ and (not answered or put_off):
        if put_off:
            by_d = str(replied.get("by") or to_first or "They").split(" ")[0]
            return {**v, "word": "ready", "label": "Nudge ready", "nudge": True,
                    "lead": f"Nudge to {who_} ready: {by_d} wrote on {fmt_short_date(parse_dt(replied.get('on')))} that the answer would follow. ",
                    "short": f"nudge {who_}, the answer {by_d} promised has not come. Note ready", "state": "Nudge ready", "rank": 0}
        if part_:
            return {**v, "word": "ready", "label": "Nudge ready", "nudge": True, "lead": f"Nudge to {who_} ready: {part_}. ",
                    "short": f"nudge {who_}, no answer on this one yet. Note ready", "state": "Nudge ready", "rank": 0}
        return {**v, "word": "ready", "label": "Nudge ready", "nudge": True,
                "lead": f"Nudge to {who_} ready{many}, no reply since {fmt_short_date(at)}. ",
                "short": f"nudge {who_}, no reply since {fmt_short_date(at)}. Note ready", "state": "Nudge ready", "rank": 0}
    if ready and ready_tap not in (aid, nudge_) and sent:
        # The next note is yours to send: after the board partner's yes (said in the warning), or a quiet colleague.
        what = "Team note" if ready_tap.endswith("_team") else "Intro ask"
        yes_by = str(((yes or {}).get("after") or {}).get("to_name") or "").split(" ")[0]
        why = "" if yes or answered else f": {part_}" if part_ else f": no reply from {to_first or 'them'} since {fmt_short_date(at)}"
        return {**v, "word": "ready", "label": f"{yes_by} said yes" if yes and yes_by else f"{what} ready",
                "lead": f"{what} ready{why}. ", "short": f"{what.lower()} ready{why}", "state": f"{what} ready", "rank": 0}
    if chosen and sent:
        # Tapped, and the note is not written yet: it is on its way, and nothing nudges the person who already answered.
        what = "Team note" if str(chosen[-1].get("id")).endswith("_team") else "Intro ask"
        yes_by = str(((yes or {}).get("after") or {}).get("to_name") or "").split(" ")[0]
        return {**v, "word": "requested", "label": f"{yes_by} said yes" if yes and yes_by else f"{what} coming", "draft": None,
                "lead": f"{what} coming at the next check. ", "short": f"{what.lower()} coming", "state": f"{what} coming",
                "weight": -10, "rank": 2}
    if answered and replied.get("defers"):
        by_ = str(replied.get("by") or to_first or "They").split(" ")[0]
        on_ = fmt_short_date(parse_dt(replied.get("on")))
        if put_off:
            return {**v, "word": "nudge", "label": "Nudge", "draft": None, "nudge": True,
                    "lead": f"{by_} wrote on {on_} that the answer would follow, and it has not come: nudge {who_}. ",
                    "short": f"nudge {who_}, the answer {by_} promised on {on_} has not come", "state": f"{by_} replied on {on_}, no answer yet",
                    "weight": -5, "rank": 1}
        return {**v, "word": "replied", "label": f"{by_} replied", "draft": None, "replied": True,
                "lead": f"{by_} replied on {on_}: the answer is to follow. ", "short": f"{by_} replied on {on_}, answer to follow",
                "state": f"{by_} replied on {on_}", "weight": -10, "rank": 2}
    if answered:
        # They answered (a message from them after the note, in its thread or naming the company): no nudge. The user
        # reads the reply and taps what it says: the partner's yes, another way in, or Close ask.
        by_ = str(replied.get("by") or to_first or "They").split(" ")[0]
        on_ = fmt_short_date(parse_dt(replied.get("on")))
        return {**v, "word": "replied", "label": f"{by_} replied", "draft": None, "replied": True,
                "lead": f"{by_} replied on {on_}: read it, then answer here. ", "short": f"{by_} replied on {on_}",
                "state": f"{by_} replied on {on_}", "weight": -5, "rank": 1}
    if sent:  # the note went out: the ask waits on whoever it went to
        said = {"team": "Asked the team", "board": f"Asked {to_first or 'the board partner'}", "nudge": f"Nudged {who_}",
                "colleague": f"Asked {to_first} for the intro" if to_first else "Intro requested"}.get(kind, "Intro requested")
        quiet_days = pipeline_working_days(at.date(), today) if at else 0
        if quiet_days >= 5 and kind == "nudge":  # nudged and still quiet: another way in, never a third note
            way = {"board": f"raise it with {to_first or 'them'} directly", "team": "ask one colleague directly"}.get(base_kind, "ask the team instead")
            return {**v, "word": "nudge", "label": "No reply", "draft": None,
                    "lead": f"{said} on {fmt_short_date(at)}" + (f": {part_}. {way[:1].upper()}{way[1:]}. " if part_ else f", still no reply: {way}. "),
                    "short": f"no reply since the nudge on {fmt_short_date(at)}: {way}", "state": f"{said} on {fmt_short_date(at)}, no reply",
                    "weight": -5, "rank": 1}
        if quiet_days >= 5 and part_:  # they answered the rest of that note: a nudge on this one only
            return {**v, "word": "nudge", "label": "Nudge", "draft": None, "nudge": True,
                    "lead": f"{said} on {fmt_short_date(at)}: {part_}. Nudge {who_}. ",
                    "short": f"nudge {who_}, no answer on this one yet", "state": f"{said} on {fmt_short_date(at)}, no answer on this one",
                    "weight": -5, "rank": 1}
        if quiet_days >= 5:  # five working days and no reply: one nudge, for every ask that note carried
            return {**v, "word": "nudge", "label": "Nudge", "draft": None, "nudge": True,
                    "lead": f"{said} on {fmt_short_date(at)}{many}, no reply in {quiet_days} working days: nudge {who_}. ",
                    "short": f"nudge {who_}, no reply since {fmt_short_date(at)}", "state": f"{said} on {fmt_short_date(at)}, no reply yet",
                    "weight": -5, "rank": 1}
        return {**v, "word": "requested", "label": said, "lead": f"{said} on {fmt_short_date(at)}. ", "draft": None,
                "short": f"{said[:1].lower()}{said[1:]} on {fmt_short_date(at)}", "state": f"{said} on {fmt_short_date(at)}",
                "weight": -20, "rank": 3}
    if ready:  # the first note is written and waits for you
        to_ = (parts.get("draft_names") or {}).get(ready) or ""
        return {**v, "state": f"Note to {to_} ready" if to_ else "Note ready", "note_ready": True, "rank": 0}
    return v


def ask_group_row(rows: list[dict[str, Any]], views: dict[str, dict[str, Any]], parts: dict[str, Any], today: Any) -> dict[str, Any] | None:
    """One row for asks that went out in one note and now wait on its nudge: "2 founder asks wait on Aditi", with the
    nudge's draft. Each ask keeps its own row on the Portfolio tab, where it is answered or closed. `ready_form` is what
    the row says once the morning's nudge is written, so the run that writes it can say so at once."""
    first_ = rows[0]
    v0 = views[first_["id"]]
    rows = sorted(rows, key=lambda r: str(r.get("company") or ""))  # one order wherever the note's asks are named
    sent = ask_sent(parts.get("sent_drafts"), first_.get("item_id")) or {}
    at = parse_dt(sent.get("at"))
    to_first = str(sent.get("to_name") or "").split(" ")[0] or "them"
    kind = sent.get("note_kind")
    who_ = "the team" if kind == "team" else to_first
    names = [str(r.get("company") or "a founder") for r in rows]
    shorts = [n.split(" ")[0] for n in names]
    quiet_days = pipeline_working_days(at.date(), today) if at else 0

    # They answered the note's other asks: every line says so, never "no reply".
    oth_ = next((r.get("answered_others") for r in rows if _answers(r.get("answered_others"), sent)), None)

    def says(ready: bool) -> dict[str, Any]:
        tail = "Nudge ready" if ready else f"Nudge {who_}"
        if oth_:
            by_o = str(oth_.get("by") or to_first).split(" ")[0]
            on_o = fmt_short_date(parse_dt(oth_.get("on")))
            named_o = [str(x) for x in oth_.get("named") or []]
            lines = [c for c in (f"{by_o} answered on {_and(named_o)}; {_and(names)} still wait" + (". Note ready" if ready else ""),
                                 f"{by_o} answered on {_and([n.split(' ')[0] for n in named_o])}; {_and(shorts)} still wait" + (". Note ready" if ready else ""),
                                 f"{by_o} answered on {_and([n.split(' ')[0] for n in named_o])}; {_and(shorts)} still wait",
                                 f"{len(rows)} founder asks still wait on {who_}") if len(c) <= 89]
            return {"detail": f"Your {fmt_short_date(at)} note to {who_}: {by_o} answered on {_and(named_o)} on {on_o}, not on {_and(names)}. {tail}",
                    "push_line": lines[0] if lines else f"{len(rows)} founder asks still wait on {who_}", "push_lines": lines,
                    "status_word": "ready" if ready else "nudge", "ask_state": "ready" if ready else "nudge",
                    "state_label": "Nudge ready" if ready else "Nudge"}
        # Longest first: a push takes the first that fits, "Still open: " included, so a repeat still names the nudge.
        lines = [c for c in (f"Nudge {who_} on {_and(names)}: no reply since {fmt_short_date(at)}" + (". Note ready" if ready else ""),
                             f"Nudge {who_} on {_and(shorts)}: no reply since {fmt_short_date(at)}" + (". Note ready" if ready else ""),
                             f"Nudge {who_} on {_and(shorts)}: no reply since {fmt_short_date(at)}",
                             f"Nudge {who_} on {len(rows)} founder asks: no reply since {fmt_short_date(at)}",
                             f"Nudge {who_} on {len(rows)} founder asks") if len(c) <= 89]
        return {"detail": f"Your {fmt_short_date(at)} note to {who_}: no answer yet on {_and(names)}, {plural(quiet_days, 'working day')}. {tail}",
                "push_line": lines[0] if lines else f"Nudge {who_} on {len(rows)} founder asks", "push_lines": lines,
                "status_word": "ready" if ready else "nudge", "ask_state": "ready" if ready else "nudge",
                "state_label": "Nudge ready" if ready else "Nudge"}
    ready = v0.get("word") == "ready"
    # The note itself, in the user's mail: the nudge goes as a reply to it.
    note_url = next((n.get("url") for n in reversed(first_.get("notes") or []) if isinstance(n, dict) and n.get("url") and
                     not str(n.get("tap") or "").endswith("_nudge")), None)
    return {"title": f"{len(rows)} founder asks wait on {who_}", **says(ready), "ready_form": says(True),
            **({"note_url": note_url} if note_url else {}),
            "short": f"{len(rows)} asks still wait on {who_}" if oth_ else f"{len(rows)} asks, no reply since {fmt_short_date(at)}", "draft": v0.get("draft"),
            "group_asks": [{"item_id": r.get("item_id"), "company": r.get("company"), "company_id": r.get("company_id"), "ask": r.get("ask")}
                           for r in rows]}


def _item(kind: str, key: Any, title: str, detail: str, base: float, priority: str, source_label: str, source_url: str | None,
          breach: bool = False, entity: dict[str, Any] | None = None, due: str | None = None, actions: list[str] | None = None,
          deal_id: str | None = None, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    row = {"id": item_id(kind, key), "kind": kind, "group": KIND_GROUP[kind], "section": SECTION_OF[kind],
           "title": clip(title, 90), "detail": fit_sentences(detail, 160), "base": base, "priority": priority, "breach": breach,
           "source": {"label": source_label, "url": source_url}, "entity": entity or {}, "due": due,
           "actions": actions or ["open"], "deal_id": deal_id, **(extra or {})}
    row.setdefault("status_word", PRIORITY_WORD.get(priority, "medium"))
    return row


def candidates(ctx: dict[str, Any], profile: dict[str, Any], parts: dict[str, Any]) -> list[dict[str, Any]]:
    """Every item that could earn a place in today's brief, with a base score. Scores rise when the item
    touches someone you meet today, a board this week, or a deal at a later stage."""
    mods = profile["modules"]
    scope = profile.get("pipeline_scope", "own")
    tz = ctx["tz"]
    now = ctx["now"]
    user_email = ctx["user_email"]
    lookup = ctx["lookup"]
    stage_map = ctx["stage_map"]
    diligence_order = stages_mod.order("diligence", stage_map)
    out: list[dict[str, Any]] = []
    own_deal_ids = {d["id"] for d in ctx["deals"] if d.get("owner_email") == user_email or
                    user_email in {norm_email(t) for t in (d.get("team") or []) if isinstance(t, str)}}
    deal_pool = {d["id"] for d in ctx["deals"]} if scope in ("full", "needs_call") else own_deal_ids
    deal_by_id = {d["id"]: d for d in ctx["deals"]}

    meet_ids: set[str] = set()
    for m in (parts.get("meetings_today") or []):
        meet_ids.update((m.get("external_ids") or []))
    meet_companies = {lookup[pid].get("company_id") for pid in meet_ids if pid in lookup and lookup[pid].get("company_id")}
    board_companies = {b["company_id"] for b in (parts.get("boards") or [])}
    soon_ids: set[str] = set()  # people the user meets in the next 36 hours
    for m in ctx["meetings"]:
        if m.get("start") and now <= m["start"] <= now + timedelta(hours=36):
            soon_ids.update(m.get("external_ids") or [])
    upcoming_by_domain: dict[str, Any] = {}
    met_by_domain: dict[str, Any] = {}  # pitches you have already met in the last two weeks
    for m in ctx["meetings"]:
        if m.get("start") and now <= m["start"] <= now + timedelta(days=14):
            for pid in m.get("external_ids") or []:
                dom = (lookup.get(pid) or {}).get("company_domain")
                if dom and dom not in upcoming_by_domain:
                    upcoming_by_domain[dom] = m["start"]
        elif m.get("start") and now - timedelta(days=14) <= m["start"] < now:
            for pid in m.get("external_ids") or []:
                dom = (lookup.get(pid) or {}).get("company_domain")
                if dom and (dom not in met_by_domain or m["start"] > met_by_domain[dom]):
                    met_by_domain[dom] = m["start"]
    # A meeting an earlier, wider read saw counts too: a pulse reads only today's calendar.
    for cid_, st_ in (ctx.get("met_carried") or {}).items():
        dom = str(((ctx.get("companies") or {}).get(cid_) or {}).get("domain") or "").lower()
        if dom and st_ and now - timedelta(days=14) <= st_ < now and (dom not in met_by_domain or st_ > met_by_domain[dom]):
            met_by_domain[dom] = st_

    def pid_of(email: str | None) -> str | None:
        hit = lookup.get(norm_email(email)) if email else None
        return hit["id"] if hit else None

    def order_of(key: str | None) -> int:
        return stages_mod.order(key or "screening", stage_map)

    def founder_of(company_id: str | None) -> str | None:
        for p in ctx.get("people") or []:
            if company_id and p.get("company_id") == company_id and re.search(r"\b(ceo|founder|co-founder)\b", str(p.get("title") or ""), re.I):
                return p.get("name")
        return None

    def firm_lead_person(company_id: str | None, mine: bool = False) -> dict[str, Any] | None:
        """The colleague closest to a company's people: who to check with before acting for it. With `mine`, the user
        counts too, so a partner who is herself closest to the company is told the call is hers."""
        people = [p for p in ctx.get("people") or [] if company_id and p.get("company_id") == company_id and not p.get("is_member")]
        me = (ctx.get("user_person") or {}).get("id")
        best, score = None, 0
        for mid in ctx.get("member_ids") or []:
            if mid == me and not mine:
                continue
            total = sum((ctx.get("strengths") or {}).get(mid, {}).get(p["id"], 0) for p in people)
            if total > score or (mid == me and total and total >= score):
                best, score = mid, total
        return next((p for p in ctx.get("people") or [] if p.get("id") == best), None) if best else None

    def firm_lead(company_id: str | None) -> str | None:
        person = firm_lead_person(company_id)
        return str(person.get("name") or "").split(" ")[0] or None if person else None

    def company_name(company_id: str | None) -> str | None:
        return (ctx["companies"].get(company_id or "") or {}).get("name") if company_id else None

    def when_label(dt, title: Any = None) -> str:
        """ "10:00" today, "Mon 10:00" another day; "10:00" when the title already names the day ("Monday partner meeting")."""
        local = dt.astimezone(tzinfo(tz))
        if local.date() == now.astimezone(tzinfo(tz)).date() or local.strftime("%A").lower() in str(title or "").lower():
            return fmt_time(dt, tz)
        return f"{local.strftime('%a')} {fmt_time(dt, tz)}"

    for m in (parts.get("meetings_today") or []):
        prep = (parts.get("prep_by_meeting") or {}).get(m["id"]) or {}
        mins = (m["start"] - now).total_seconds() / 60
        soon = 0 <= mins <= 240
        deal = prep.get("deal") or {}
        late_stage = bool(deal and deal.get("stage") and order_of(_stage_key(deal["stage"], ctx)) >= diligence_order)
        base = 55 + (25 if soon else 0) + (10 if late_stage else 0)
        out.append(_item("meeting", m["id"], f"{fmt_time(m['start'], tz)} \u00b7 {prep.get('who') or m.get('title')}",
                         prep.get("finding") or (m.get("title") or ""), base, "high" if soon else "medium", "Calendar", m.get("url"),
                         entity={"type": "meeting", "id": m["id"], "name": m.get("title")}, due=m["start"].isoformat(),
                         actions=["prep", "open"], extra={"prep_id": prep.get("id"), "time": fmt_time(m["start"], tz)}))

    cv = parts.get("commitments_due", {"mine": [], "theirs": []})
    # Finance and IR deliver to their own partners: the LP letter is core work, ranked like a promise to a founder.
    internal_counts = profile.get("level") == "finance"
    # Companies where another fund is moving: a promise to them that is days late can cost the deal.
    rivals: dict[str, str] = {}
    for s in parts.get("signals") or []:
        dl_ = parse_date(s.get("deadline"))
        if s.get("company_id") and not (dl_ and dl_ < now.date()):
            # The race and its date: "two other funds with offers, decide by 31 Oct".
            rivals.setdefault(s["company_id"], signal_phrase(s) + (f", decide by {fmt_short_date(dl_)}" if dl_ else ""))
    for c in (cv.get("mine") or []):
        due = parse_date(c.get("due"))
        overdue = c.get("overdue")
        meeting_today = pid_of(c.get("owed_to_email")) in meet_ids
        internal = c.get("internal") and not internal_counts
        to_company = (lookup.get(norm_email(c.get("owed_to_email"))) or {}).get("company_id") if c.get("owed_to_email") else None
        # Due at a weekend means due by Friday: on Friday it is the day's work.
        work_due = due - timedelta(days=due.weekday() - 4) if due and due.weekday() >= 5 else due
        contested = rivals.get(to_company or "") if not c.get("internal") else None  # another fund is moving on this company
        rival = contested if overdue and due and (now.date() - due).days >= 3 else None
        if rival:
            base = 82  # three days late to a founder while another fund is moving: it leads over any chore due today
        elif overdue:
            base = 56 if internal else 75  # your own late work ranks above what a colleague owes you
        elif c.get("due_today") or (work_due and work_due == now.date()):
            base = 60 if internal else 70  # a promise to a founder due today outranks a decision with no date
        elif work_due and work_due == now.date() + timedelta(days=1) and internal_counts:
            base = 64  # tomorrow's deliverable is today's work
        else:
            base = 50
        meeting_soon = not meeting_today and pid_of(c.get("owed_to_email")) in soon_ids
        if meeting_today:
            base += 10 if (overdue or c.get("due_today")) else 5
        elif meeting_soon:
            base += 6
        if to_company and to_company in board_companies:
            base += 15  # a promise to a company whose board meets in the next three days
        title = c["what"].rstrip(".")
        to_name = c.get("owed_to") or "them"
        cname = company_name(to_company)
        if cname and cname.lower() not in to_name.lower() and not c.get("internal"):
            to_name += f" ({cname})"
        when = ("today" if due == now.date() else "tomorrow" if due == now.date() + timedelta(days=1) else fmt_short_date(due)) if due else None
        if due and work_due == now.date() and due != now.date():
            when = f"{due.strftime('%a')} {fmt_short_date(due)}, so today"  # the push and the row agree: a Saturday deadline is Friday's work
        detail = f"Promised to {to_name}" + (f", due {when}" if when else "") + \
            (f", {plural((now.date() - due).days, 'day')} late" if due and overdue else "")
        if rival:
            detail += f". {rival[:1].upper()}{rival[1:]}"  # why it leads: "Term sheet from Bluepeak Partners"
        if meeting_today:
            detail += ". You meet them today"
        elif meeting_soon:
            detail += ". You meet them tomorrow"
        drafted_ = (parts.get("drafts_by_commitment") or {}).get(c["id"])
        gaps_ = (parts.get("draft_gaps") or {}).get(drafted_) or 0 if drafted_ else 0
        holder_ = view_holder(ctx, c.get("what"), to_company) if gaps_ and not c.get("internal") else None
        if LETTER.search(str(c.get("what") or "")):
            detail += (f". Draft ready: {'fill in ' + plural(gaps_, 'line') + ', ' if gaps_ else ''}check the figures, then send it" if drafted_ else
                       ". ant. drafts it from the KPI history and the LP list")
        elif gaps_:  # a draft with blanks is never just "Draft ready": it says what is left, and who holds it
            detail += f". {gaps_line(gaps_, holder_)}"
        word = "overdue" if overdue else "due_today" if c.get("due_today") else "due"
        after = None  # an outcome is shared after the meeting that decides it, never before
        decide_first = None
        if OUTCOME.search(str(c.get("what") or "")):
            pm = next((m for m in parts.get("decision_meetings") or parts.get("partner_meetings") or []
                       if m["start"] >= now and (not due or m["start"].date() <= due)), None)
            if pm:
                after = pm["start"].isoformat()
                detail += f". Share it after the {when_label(pm['start'], pm.get('title'))} {pm.get('title') or 'partner meeting'}"
                base -= 15  # nothing to do until the room decides: it never leads the morning
            elif profile.get("level") == "solo_gp":
                decide_first = True  # a solo GP's own call: no draft or push until they make it
                detail += ". Share it once you decide"
                base -= 15
        if c.get("looks_done"):
            base *= 0.5  # sent mail suggests it is done: one tap closes it, and it never pushes
            detail = f"Looks done: {c['looks_done']}"
            word = "looks_done"
        out.append(_item("commitment", c["id"], title[:1].upper() + title[1:], detail, base,
                         "urgent" if overdue and not c.get("looks_done") else "high", "Meeting notes", c.get("source_url"),
                         breach=bool(overdue) and not c.get("looks_done"),
                         entity={"type": "commitment", "id": c["id"], "name": title, "company_id": to_company}, due=c.get("due"),
                         actions=["done", "snooze", "open"],
                         extra={"commitment_id": c["id"], "status_word": word, "to_email": norm_email(c.get("owed_to_email")) or None,
                                "draft": drafted_, "after": after, "decide_first": decide_first,
                                **({"draft_gaps": gaps_} if gaps_ else {}), **({"holder": holder_} if holder_ else {}),
                                "to_name": c.get("owed_to"), "to_company": cname if not c.get("internal") else None,
                                "days_late": (now.date() - due).days if due and overdue else None, "rival": rival,
                                "contested": bool(contested), "internal": bool(c.get("internal"))}))
    for c in (cv.get("undated") or [])[:2]:
        title = c["what"].rstrip(".")
        made = parse_date(c.get("meeting_date"))
        u_company = (lookup.get(norm_email(c.get("owed_to_email"))) or {}).get("company_id") if c.get("owed_to_email") else None
        out.append(_item("commitment", c["id"], title[:1].upper() + title[1:],
                         f"Promised to {c.get('owed_to') or 'them'}" + (f" on {fmt_short_date(made)}" if made else "") + ", no date set",
                         40, "medium", "Meeting notes", c.get("source_url"),
                         entity={"type": "commitment", "id": c["id"], "name": title, "company_id": u_company}, due=None,
                         actions=["done", "snooze", "open"],
                         extra={"commitment_id": c["id"], "status_word": "undated", "to_email": norm_email(c.get("owed_to_email")) or None,
                                "to_name": c.get("owed_to"), "draft": (parts.get("drafts_by_commitment") or {}).get(c["id"])}))
    for c in (cv.get("theirs") or []):
        due = parse_date(c.get("due"))
        meeting_today = pid_of(c.get("owed_by_email")) in meet_ids
        by_company = (lookup.get(norm_email(c.get("owed_by_email"))) or {}).get("company_id") if c.get("owed_by_email") else None
        late = (now.date() - due).days if due and due < now.date() else 0
        when_txt = (f"Promised for {fmt_short_date(due)}" + (f", {plural(late, 'day')} late" if late else ", due today" if due == now.date() else "")
                    if due else "Promised in a meeting")
        extra_w = {"commitment_id": c["id"], "status_word": "waiting", "from_email": norm_email(c.get("owed_by_email")) or None,
                   "days_late": late or None, "to_you": norm_email(c.get("owed_to_email")) == norm_email(user_email)}
        if c.get("internal"):
            extra_w["section"] = "team"  # a colleague's promise to you
        # Owed to you, or to someone else in a meeting you were in: the line says who it is owed to.
        to_you = norm_email(c.get("owed_to_email")) == norm_email(user_email) or not c.get("owed_to")
        owed_whom = "you" if to_you else str(c.get("owed_to")).split(" ")[0]
        held_ = None
        if c.get("internal") and to_you:
            held_ = next((m_ for m_ in (cv.get("mine") or []) if m_.get("overdue") and
                          norm_email(m_.get("owed_to_email")) == norm_email(c.get("owed_by_email"))), None)
        held_txt = ""
        if held_:
            late_h = (now.date() - parse_date(held_["due"])).days if parse_date(held_.get("due")) else 0
            held_txt = f". It may wait on yours: {_lower_first(str(held_['what']).rstrip('.'))}" + (f", {plural(late_h, 'day')} late" if late_h else "")
        out.append(_item("waiting", c["id"], f"{c.get('owed_by')} owes {owed_whom}: {_lower_first(c['what'].rstrip('.'))}",
                         when_txt + (". You meet them today" if meeting_today else "") + held_txt,
                         (48 if due == now.date() else 35) if c.get("internal") else 45, "medium", "Meeting notes", c.get("source_url"),
                         entity={"type": "commitment", "id": c["id"], "name": c["what"], "company_id": by_company}, due=c.get("due"),
                         actions=["done", "snooze", "open"], extra=extra_w))
    # A founder on your own deal asked a question and nothing from the firm went back: the reply is your work.
    for q in (parts.get("unanswered") or []):
        if q["deal_id"] not in own_deal_ids:
            continue
        asked = parse_date(q.get("asked_on"))
        if not asked:
            continue
        first = str(q.get("person") or "They").split(" ")[0]
        wait = (now.date() - asked).days
        base = 60 + min(wait, 10) + (5 if q.get("company_id") in meet_companies else 0)
        said = f'"{q["question"]}"' if q.get("question") else (f'In "{q["subject"]}". Reply in that thread' if q.get("subject") else "Reply in your thread")
        out.append(_item("question", q["id"], f"{q['company']}: {first} asked on {fmt_short_date(asked)}, no reply yet", said, base, "high",
                         "Email", q.get("source_url"), entity={"type": "deal", "id": q["deal_id"], "name": q["company"], "company_id": q.get("company_id")},
                         deal_id=q["deal_id"], actions=["draft", "done", "snooze", "open"],
                         extra={"status_word": "waiting_you", "question_id": q["id"], "to_email": norm_email(q.get("email")) or None,
                                "to_name": q.get("person"), "to_company": q.get("company"),
                                "draft": (parts.get("drafts_by_question") or {}).get(q["id"]),
                                "short": f"{first} asked on {fmt_short_date(asked)}, no reply yet"}))

    if mods.get("pipeline") != "off":
        for s in (parts.get("signals") or []):
            key = s.get("stage_key")
            owned = s["deal_id"] in own_deal_ids
            if scope == "needs_call":
                if not owned and order_of(key) < diligence_order:
                    continue
            elif s["deal_id"] not in deal_pool:
                continue
            later_round = str(s.get("round") or "").lower().startswith("series")
            base = 60 + 4 * order_of(key) + (2 if later_round else 0) + (5 if s.get("company_id") in meet_companies else 0)
            dl = parse_date(s.get("deadline"))
            # The founder's own words say when ("by 5 Nov", "end of the month"): only add a date when they do not.
            said = bool(dl and (re.search(rf"\b0?{dl.day}\s*{dl.strftime('%b')}", s["evidence"], re.I) or
                                re.search(r"\b(end of (the )?(month|week|quarter)|next week|this week|tomorrow|today|monday|tuesday|"
                                          r"wednesday|thursday|friday|saturday|sunday|jan(uary)?|feb(ruary)?|mar(ch)?|apr(il)?|june?|"
                                          r"july?|aug(ust)?|sept?(ember)?|oct(ober)?|nov(ember)?|dec(ember)?)\b", s["evidence"], re.I)))
            ev = clip(s["evidence"], 100)
            if s.get("shared"):
                # Where the deal stands, then where the news came from: a row never says only its source. A step whose
                # date has gone says "was due", and on your own deal the news is in your CRM, not "shared" with you.
                d_ = deal_by_id.get(s["deal_id"]) or {}
                stand = stages_mod.label(d_["stage_name"]) if d_.get("stage_name") else ""
                if (d_.get("next_step") or "").strip():
                    due_ = d_.get("next_step_due_dt")
                    stand += (", next: " if stand else "Next: ") + _lower_first(str(d_["next_step"]).strip().rstrip(".")) + \
                        ((f", was due {fmt_short_date(due_)}" if due_.date() < now.date() else f" by {fmt_short_date(due_)}") if due_ else "")
                where_ = "in your CRM" if owned else "shared by the deal team"
                ev = (f"{stand}. " if stand else "") + (f"From {s['said_by']}'s email, {where_}." if s.get("said_by") else
                                                        "In your CRM." if owned else "Shared to the CRM by the deal team.")
            elif re.search(r"\b(we|we've|we're|we'd|our|us)\b", ev, re.I):
                # Their words, never read as ours; a cut quote ends on its ellipsis, never "and…." A quote two days old
                # or more says when it was written, so "until next week" keeps its meaning.
                said_on = parse_dt(s.get("date"))
                verb = f"wrote on {fmt_short_date(said_on)}" if said_on and (now.date() - said_on.date()).days >= 2 else "says"
                ev = f'{s.get("said_by") or "They"} {verb}: "{ev}"' if ev.endswith(("…", "?", "!")) else \
                    f'{s.get("said_by") or "They"} {verb}: "{ev.rstrip(".")}."'
            ev = ev[:1].upper() + ev[1:]  # a row's detail starts a sentence, whatever the note it came from
            gap = deadline_gap(deal_by_id.get(s["deal_id"]) or {}, s.get("deadline"), now.date())
            # The date once, as a sentence of its own: never after a deadline already said to have passed.
            detail = join_sentences(ev, f"Decision by {fmt_short_date(dl)}.") if dl and not said and dl >= now.date() else ev
            if dl and 0 <= (dl - now.date()).days <= 1:
                base += 25  # an answer due today or tomorrow outranks an overdue email
            if gap:
                detail = f"{gap}. " + detail  # the date that turns a calm row red goes first
                base += 6
            if profile.get("level") != "solo_gp":
                pm = next((m for m in parts.get("partner_meetings") or [] if m["start"] >= now and (not dl or m["start"].date() <= dl)), None)
                if pm:  # after the founder's words, so a short row keeps the words and loses the reminder
                    detail = join_sentences(detail, f"Raise it at the {when_label(pm['start'], pm.get('title'))} {pm.get('title') or 'partner meeting'}.")
            phrase = signal_phrase(s)
            passed = bool(dl and dl < now.date())
            short = phrase + ((f", their deadline passed {fmt_short_date(dl)}" if passed else
                               ", decide today" if dl == now.date() else ", decide by tomorrow" if dl == now.date() + timedelta(days=1)
                               else f", decide by {fmt_short_date(dl)}") if dl else "")
            if passed:
                base -= 10  # still worth a look, no longer a countdown
            # An analyst sees a colleague's race for context; Today and the morning push lead with their own deals and pitches.
            fyi = profile.get("level") == "analyst" and not owned
            if fyi:
                base = min(base, 45)
            lead = None
            if s.get("owner") and norm_email(s["owner"]) != norm_email(user_email):
                lead = str((lookup.get(norm_email(s["owner"])) or {}).get("name") or s["owner"].split("@")[0]).split(" ")[0]
                lead = lead[:1].upper() + lead[1:]
            out.append(_item("signal", s["id"], f"{s['company']}: {phrase}" + (f" ({lead} leads)" if lead else ""), detail, base, "urgent", "Email", s.get("source_url"),
                             breach=True, entity={"type": "deal", "id": s["deal_id"], "name": s["company"]}, due=None if passed else s.get("deadline"),
                             deal_id=s["deal_id"], actions=["open", "snooze"],
                             extra={"status_word": "urgent", "short": short, "gap": gap, "fyi": fyi or None, "since": s.get("date")}))
        if scope != "needs_call":
            for st in (parts.get("stale") or []):
                if st["deal_id"] not in own_deal_ids:
                    continue  # stale nudges go to the deal owner; the Pipeline tab shows the rest
                comp_id = (deal_by_id.get(st["deal_id"]) or {}).get("company_id")
                base = 50 + 4 * order_of(st.get("stage_key")) + 6 * (len(st["reasons"]) - 1) + (5 if comp_id in meet_companies else 0)
                top = st["reasons"][0]
                headline = {"over_dwell": f"{plural(st.get('days_in_stage') or 0, 'day')} in {stages_mod.label(st['stage'], False)}" +
                                          (f" (usually {st['dwell']})" if st.get("dwell") else ""),
                            "no_next_step": "no next step set", "next_step_overdue": _lower_first(top["text"]),
                            "no_contact": _lower_first(top["text"])}.get(top["code"], _lower_first(top["text"]))
                d_row = deal_by_id.get(st["deal_id"]) or {}
                nxt = (d_row.get("next_step") or "").strip()
                rest = [r["text"] for r in st["reasons"][1:2] if r["code"] != "next_step_overdue"]
                late_step = any(r["code"] == "next_step_overdue" for r in st["reasons"])
                due_s = fmt_short_date(d_row["next_step_due_dt"]) if d_row.get("next_step_due_dt") else None
                reasons = (f"Next: {nxt}" + ((f", was due {due_s}" if late_step else f" by {due_s}") if due_s else "") if nxt else "") or ""
                reasons = ". ".join(x for x in [reasons] + rest if x)
                if not reasons:  # never an empty line: say since when, and what would move it
                    since = d_row.get("stage_entered_dt")
                    lc = d_row.get("last_contact_dt")
                    passed_on = (parts.get("pass_drafted") or {}).get(comp_id)
                    if st.get("stage_key") == "inbound" and passed_on:
                        reasons = f"Pass reply drafted {fmt_short_date(parse_dt(passed_on))}: send it, then move the deal to Passed"
                    elif st.get("stage_key") == "inbound":
                        reasons = (f"In Inbound since {fmt_short_date(since)}: " if since else "") + "book a first meeting or pass"
                    else:
                        reasons = (f"In {stages_mod.label(st['stage'], False)} since {fmt_short_date(since)}" if since else "") + \
                            (f"{'. ' if since else ''}Last contact {fmt_short_date(lc)}" if lc else "")
                        reasons = reasons or "Add the next step"
                    reasons = reasons[:1].upper() + reasons[1:]
                out.append(_item("stale", st["deal_id"], f"{st['company']}: {headline}", reasons, base, "medium",
                                 "CRM", st.get("source_url"), entity={"type": "deal", "id": st["deal_id"], "name": st["company"]},
                                 deal_id=st["deal_id"], actions=["next_step", "snooze", "open"], extra={"status_word": "stale"}))
            for mv in parts.get("moves_24h", []):
                if mv["deal_id"] not in deal_pool:
                    continue
                out.append(_item("deal_move", mv["deal_id"] + mv["entered"], f"{mv['company']}: moved to {stages_mod.label(mv['stage'])}",
                                 f"Since {fmt_short_date(parse_date(mv['entered']))}", 30, "low", "CRM", mv.get("source_url"),
                                 entity={"type": "deal", "id": mv["deal_id"], "name": mv["company"]}, deal_id=mv["deal_id"],
                                 extra={"status_word": "moved"}))
        for d in (parts.get("decisions") or []):
            if scope != "needs_call" and profile.get("level") != "solo_gp" and d["deal_id"] not in own_deal_ids:
                continue  # a vote on someone else's deal is not this person's line
            if d.get("breach"):
                continue  # already a signal item
            stale_ids = {s["deal_id"] for s in (parts.get("stale") or [])}
            dbase = 66 + (4 if (deal_by_id.get(d["deal_id"]) or {}).get("stage_key") == "term_sheet" else 0) + (6 if d["deal_id"] in stale_ids else 0)
            out.append(_item("decision", d["deal_id"], f"Decide on {d['company']}", d["why"], dbase, "high",
                             "CRM", d.get("source_url"), entity={"type": "deal", "id": d["deal_id"], "name": d["company"]},
                             deal_id=d["deal_id"], actions=["open"]))

    if mods.get("triage") not in (None, "off"):
        for r in (parts.get("inbound") or []):
            if r["decision"] == "pass" and not r.get("pass_log") and not r.get("injection_flag"):
                continue  # a kind pass needs no line; one that hid instructions for AI tools always gets one
            if r.get("answered") and not r.get("injection_flag"):
                continue  # you replied (Sent it on its draft): the pitch waits on them now, on the Pitches list
            label = {"call": "book a call", "more_info": "ask for more", "pass": "pass"}[r["decision"]]
            booked = upcoming_by_domain.get((r.get("domain") or "").lower())
            seen_them = met_by_domain.get((r.get("domain") or "").lower())
            if booked and r["decision"] != "pass":
                label = f"call booked for {fmt_short_date(booked)} {fmt_time(booked, tz)}"
            elif seen_them:
                label = f"you met them on {fmt_short_date(seen_them)}"  # the call happened: no "book a call" after it
            elif r.get("in_touch") and r["decision"] != "pass":
                label = "you already write to them: answer in your thread"
            comp_id = ctx["domain_to_company"].get((r.get("domain") or "").lower())
            met = comp_id in meet_companies
            if seen_them and not r.get("injection_flag") and any(
                    d.get("company_id") == comp_id and (ctx["stage_map"]["by_key"].get(d.get("stage_key")) or {}).get("active")
                    for d in ctx["deals"] if comp_id):
                continue  # met, and an open deal in the CRM (a returning pass too): the met log and the Pipeline carry it now
            if r.get("pass_log"):
                kind, base = "pass_returned", 45 + r["score"] / 5 + (5 if met else 0)
            elif r["decision"] == "call":
                kind, base = "inbound", 40 + r["score"] / 5
            else:
                kind, base = "inbound", 25 + r["score"] / 10
            title = f"{r['company']} is back" if r.get("pass_log") else f"Inbound: {r['company']}"
            extra = {"score": r["score"], "status_word": "call" if r["decision"] == "call" else r["decision"], "seen_at": r.get("seen_at")}
            if booked and r["decision"] != "pass":
                extra["status_word"] = "booked"
            elif seen_them:
                extra["status_word"] = "met"
                base -= 15  # met already: the follow-up lives under promises, not in the inbound queue
            elif r.get("in_touch") and r["decision"] != "pass":
                extra["status_word"] = "in_touch"
                base -= 10  # the conversation is already going: no cold reply on top
            if r.get("pass_log"):
                # The one question that matters on a return: did they meet the bar we set when we passed?
                verdict = revisit_verdict(r)
                when = parse_date(r.get("pass_date"))
                passed = f"Passed {fmt_short_date(when)}" if when else "Passed before"
                passed += f": {_lower_first(str(r.get('pass_reason') or '').rstrip('.'))}" if r.get("pass_reason") else ""
                detail = ". ".join(x for x in (verdict, f"Score {r['score']}: {label}", passed) if x)
                chk = r.get("revisit_check") or {}
                ev_ = clip(str(chk.get("evidence") or "").rstrip("."), 70)
                extra["short"] = ("back and met our bar" + (f": {_lower_first(ev_)}" if ev_ else "") if chk.get("met") is True else
                                  "back, our bar not met yet" + (f": {_lower_first(ev_)}" if ev_ else "") if chk.get("met") is False else
                                  "back from the pass log")
            else:
                # The decision first, so a clipped line never loses it.
                detail = f"Score {r['score']}: {label}. " + (r["facts"] if r.get("facts") else "")
            detail = detail.strip()
            if r.get("injection_flag"):
                # Never repeat the hidden words: they would travel on in the copied brief, perhaps into another AI tool.
                # The warning goes first, so a long line never loses it.
                detail = "The email hides instructions for AI tools; ant. ignored them. Read it yourself before you reply. " + detail
                extra["status_word"] = "flagged"
                base = max(base, 45)  # the user hears about it once, whatever the score
            out.append(_item(kind, r["id"], title, detail, round(base, 1), "medium" if r["decision"] == "call" else "low",
                             "Email", r.get("source_url"), entity={"type": "inbound", "id": r["id"], "name": r["company"], "company_id": comp_id},
                             actions=["open", "snooze"], extra=extra))

    if mods.get("portfolio") not in (None, "off"):
        flag_base = {"runway": 80, "key_departure": 60, "burn": 58, "revenue": 58, "churn": 50}
        level = profile.get("level")
        for f in (parts.get("portfolio_flags") or []):
            # Routed by role: Platform sees people moves, not finance alarms; principals and associates see a flag
            # only for a company they meet or whose board meets this week. Everyone keeps them all on Portfolio.
            if level == "platform" and f["kind"] != "key_departure":
                continue
            if level in ("principal", "associate", "analyst") and f["company_id"] not in board_companies | meet_companies:
                continue
            fb = flag_base.get(f["kind"], 50)
            if level == "finance" and f["kind"] != "runway" and f["company_id"] not in board_companies:
                fb = min(fb, 45)  # the CFO watches cash; a revenue miss or a departure is the letter's, not the morning's
            base = fb + (15 if f["company_id"] in board_companies else 0) + \
                (5 if f["company_id"] in meet_companies else 0)
            head = f.get("headline") or f["text"].partition(":")[0]
            board = next((b for b in (parts.get("boards") or []) if b["company_id"] == f["company_id"]), None)
            detail = f.get("detail") or f["text"]
            detail = detail[:1].upper() + detail[1:]
            if board:
                detail += f". Board meeting {fmt_short_date(parse_dt(board['start']))}"
            out.append(_item("portfolio", f["id"], f"{f['company']}: {head}", detail, base, f["priority"],
                             "Founder update", f.get("source_url"), breach=f.get("breach", False),
                             entity={"type": "company", "id": f["company_id"], "name": f["company"], "company_id": f["company_id"]},
                             extra={"status_word": "breach" if f.get("breach") else f["priority"]}))
        for b in (parts.get("boards") or []):
            out.append(_item("board", b["meeting_id"], f"Board prep: {b['company']}", f"Board meeting {fmt_short_date(parse_dt(b['start']))}",
                             50, "high", "Calendar", b.get("source_url"), entity={"type": "company", "id": b["company_id"], "name": b["company"]},
                             actions=["prep", "open"]))

        today = now.date()
        ask_rows: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]] = []  # (ask, view, row)
        for a in (parts.get("asks") or []):
            before = str(a.pop("warning", None) or "")  # recomputed every build, so a cleared flag clears its warning
            if a.get("status") == "done":
                continue
            # The cash warning travels with the ask everywhere it shows, Today or the Portfolio tab, for every level.
            tight = next((f for f in (parts.get("portfolio_flags") or []) if f["company_id"] == a.get("company_id") and f["kind"] in ("runway", "burn")), None)
            prev_to = a.pop("warning_to", None)  # kept when this run read no CRM people to find the board partner again
            if tight and (a.get("kind") == "hiring" or re.search(r"\b(hire|hiring|engineers?|recruit)", str(a.get("ask") or ""), re.I)):
                if profile.get("level") == "solo_gp":  # she is the board: the call is hers, made before anyone sources
                    a["warning"] = (f"{tight.get('headline') or 'Cash is tight'}: weigh the hires against the "
                                    f"{'burn' if tight.get('kind') == 'burn' else 'runway'} before sourcing")
                elif profile.get("level") == "partner" and (firm_lead_person(a.get("company_id"), mine=True) or {}).get("id") == \
                        (ctx.get("user_person") or {}).get("id") and (ctx.get("user_person") or {}).get("id"):
                    # A partner closest to the company is its board partner: the call is hers, made before anyone sources.
                    a["warning"] = f"{tight.get('headline') or 'Cash is tight'}: your call before anyone sources"
                else:
                    prev = re.search(r"check with ([A-Z][\w-]+(?: [A-Z][\w-]+)?) before|(?:^|: )([A-Z][\w-]+(?: [A-Z][\w-]+)?) said yes", before)
                    lead_p = firm_lead_person(a.get("company_id"))
                    # After the board partner's yes (the user's "Aditi said yes" tap), the warning carries the answer.
                    yes = next((f for f in ((parts.get("ask_follow") or {}).get(a.get("item_id")) or [])
                                if (f.get("after") or {}).get("kind") == "board"), None)
                    lead = (str(lead_p.get("name") or "").split(" ")[0] if lead_p else None) or \
                        (str(((yes or {}).get("after") or {}).get("to_name") or "").split(" ")[0] or None) or \
                        (prev.group(1) or prev.group(2) if prev else None)
                    if lead and lead_p and lead.lower() == str(a.get("who") or "").split(" ")[0].lower():
                        lead = str(lead_p.get("name") or lead)  # "Vikram Nair", never a "Vikram" the founder could be
                    board_out = ((parts.get("sent_drafts") or {}).get(a.get("item_id")) or {}).get("note_kind") == "board"
                    head_ = tight.get('headline') or 'Cash is tight'
                    # Once the board note went out, the row says who was asked and when; the flag alone stays.
                    # The answer leads, then the flag it answered: "Aditi said yes on 22 Oct. Runway under 9 months".
                    a["warning"] = (f"{lead or 'The board partner'} said yes on {fmt_short_date(parse_dt(yes.get('at')))}. {head_}" if yes else
                                    head_ if board_out else f"{head_}: check with {lead or 'the board partner'} before sourcing")
                    if lead_p and (lead_p.get("emails") or []):
                        a["warning_to"] = {"name": lead_p.get("name"), "email": (lead_p.get("emails") or [None])[0]}
                    elif isinstance(prev_to, dict) and lead and str(prev_to.get("name") or "").split(" ")[0] == lead.split(" ")[0]:
                        a["warning_to"] = prev_to
            # Who in the firm's network answers the ask, and the colleague who knows them best (the build found them
            # before the prep cards; a direct caller of this function may not have).
            if "paths" not in a:
                a["paths"] = network_mod.ask_paths(ctx, str(a.get("ask") or ""), a.get("company_id")) or None
            if mods.get("portfolio") != "asks" and profile.get("level") != "solo_gp" and \
                    a.get("company_id") not in board_companies | meet_companies:
                continue  # founder asks are Platform's queue; others see one only when they meet that company
            asked = parse_date(a.get("date"))
            age = (today - asked).days if asked else 30
            sent = ask_sent(parts.get("sent_drafts"), a.get("item_id"))
            if age > 21 and not sent and not a.get("made_on"):
                continue  # an old ask leaves Today; one with a note out stays until the intro is made or you close it
            base = (58 if mods.get("portfolio") == "asks" else 36) + (6 if age <= 2 else 0) + \
                (5 if a.get("company_id") in meet_companies or a.get("company_id") in board_companies else 0)
            who = a.get("who") if a.get("who") and str(a.get("who")).lower() not in ("the founder", "founder") else \
                (founder_of(a.get("company_id")) or "The founder")
            ask_detail = f"{who} asked" + (f" on {fmt_short_date(asked)}" if asked else "")
            if a.get("warning"):
                ask_detail += f". {a['warning']}"
            # Once the team is asked (a team note ready or sent), "no warm path" is old news.
            sd_ = parts.get("sent_drafts") or {}
            team_way = f"{a.get('item_id')}_team" in (parts.get("drafts_by_action") or {}) or \
                any(isinstance(sd_.get(f"{a.get('item_id')}{x}"), dict) and sd_[f"{a.get('item_id')}{x}"].get("note_kind") == "team" for x in ("", "_team")) or \
                any(str(f_.get("id")).endswith("_team") for f_ in ((parts.get("ask_follow") or {}).get(a.get("item_id")) or []))
            if a.get("paths"):
                p0 = a["paths"][0]
                ask_detail += f". Warm path: {p0['colleague']} {'know' if p0['colleague'] == 'You' else 'knows'} {p0['person']}" + \
                    (f" at {p0['company']}" if p0.get("company") else "")
            elif team_way:
                pass
            else:  # with a cash warning the board partner is asked first, never the team
                ask_detail += ". No one in your network fits yet" if profile.get("level") == "solo_gp" else \
                    ". No warm path found yet" if a.get("warning") else ". No warm path found: ask your team"
            if a.get("company_id") in meet_companies:
                ask_detail += ". You meet them today"
            ask_text = _lower_first(str(a.get("ask") or "").strip().rstrip("."))
            path_txt = (f"Path: {a['paths'][0]['colleague']} {'know' if a['paths'][0]['colleague'] == 'You' else 'knows'} "
                        f"{a['paths'][0]['person']}") if a.get("paths") else ""
            view = ask_view(a, parts, today)
            word, label = view["word"], view["label"]
            ask_detail = view["lead"] + ask_detail + (f". {view['state']}" if view.get("note_ready") else "")
            short_ = view["short"] or ask_text + (f". {path_txt}" if path_txt else "") + (". Note ready" if view.get("note_ready") else "")
            state_ = view["state"]  # where the ask stands, for the line under a meeting with them
            base += view["weight"]
            ask_rows.append((a, view, _item("ask", a["id"], f"{a.get('company') or 'A founder'}: {_lower_first(a.get('ask') or '')}",
                             ask_detail, base,
                             "high" if mods.get("portfolio") == "asks" else "medium", a.get("source_label") or "Founder update", a.get("source_url"),
                             entity={"type": "ask", "id": a["id"], "name": a.get("company"), "company_id": a.get("company_id"),
                                     "paths": a.get("paths")},
                             actions=["draft", "done", "snooze", "open"],
                             extra={"status_word": word, "asked_days": age if asked else None, "ask_state": word, "state_label": label,
                                    "short": short_, "meet_line": f"They asked: {ask_text}" + (f". {state_ or path_txt}" if state_ or path_txt else ""),
                                    **({"draft": view["draft"]} if view.get("draft") else {}),
                                    # "Aditi replied on 26 Oct: read it" links to the reply on Today too, as on Portfolio.
                                    **({"reply_url": (a.get("replied") or {}).get("url")} if view.get("replied") and (a.get("replied") or {}).get("url") else {}),
                                    **({"note_group": view["group"]} if view.get("group") else {})})))
        # Asks that went out in one note and wait on its nudge: one row on Today, one push, one draft.
        groups_: dict[str, list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]]] = {}
        for a, view, row in ask_rows:
            if view.get("group") and view.get("nudge"):
                groups_.setdefault(view["group"], []).append((a, view, row))
        folded: set[str] = set()
        for g_id, members in groups_.items():
            if len(members) < 2:
                continue
            members.sort(key=lambda m: -m[2]["base"])
            g = ask_group_row([m[0] for m in members], {m[0]["id"]: m[1] for m in members}, parts, today)
            if not g:
                continue
            a0 = members[0][0]
            row = _item("ask", f"note:{g_id}", g["title"], g["detail"], max(m[2]["base"] for m in members),
                        members[0][2]["priority"], "Founder updates", a0.get("source_url"),
                        entity={"type": "note", "id": g_id, "name": g["title"].split(" wait on ")[-1],
                                "ask_ids": [m[0]["id"] for m in members], "company_ids": [m[0].get("company_id") for m in members]},
                        actions=["asks", "snooze", "open"],
                        extra={**{k_: g[k_] for k_ in ("status_word", "ask_state", "state_label", "short", "push_line", "push_lines", "group_asks",
                                                      "draft", "ready_form", "note_url") if g.get(k_)}, "note_group": g_id})
            out.append(row)
            folded |= {m[2]["id"] for m in members}
        out.extend(r for _, _, r in ask_rows if r["id"] not in folded)

    if mods.get("lp") not in (None, "off"):
        lp_contacts, lp_emails = {}, {}
        for l in (parts.get("lps_raw") or []):
            lp_contacts[l.get("id")] = {pid_of(e) for e in (l.get("contacts") or [])}
            lp_emails[l.get("id")] = [norm_email(e) for e in (l.get("contacts") or []) if e]
        for a in (parts.get("lp_alerts") or []):
            met = bool(lp_contacts.get(a["lp_id"], set()) & meet_ids)
            # Money owed on a capital call outranks a touch; the push names the LP and the amount.
            call = a.get("kind") == "call"
            short = (f"owes {money(a.get('outstanding_usd'))} on a capital call" if call else _lower_first(str(a["text"]).split("; ")[0]))
            title = f"{a['name']} owes {money(a.get('outstanding_usd'))} on a capital call" if call else f"LP: {a['name']}"
            text = a["text"]
            if call and a.get("call_date"):  # the title has the amount; the line says when it was called
                rest = text.split("; ", 1)[1] if "; " in text else ""
                text = f"Called on {fmt_short_date(parse_date(a['call_date']))}" + \
                    (f", {plural(a['days_since'], 'day')} ago" if a.get("days_since") is not None else "") + (f"; {rest}" if rest else "")
            # The chase note drafted before the brief: the row says so, as a promise's row does. Once you sent it, the line
            # says when you chased; a second note comes after five quiet working days.
            by_action_ = parts.get("drafts_by_action") or {}
            drafted = by_action_.get(f"{a['id']}_2") or by_action_.get(a["id"]) or by_action_.get(item_id("lp", a["id"]))
            chased = a.get("chased") or {}
            if call and drafted:
                text += ". " + ("Second note ready" if chased else "Draft ready") + ": check the amount, then send it"
                short += ". " + ("Second note ready" if chased else "Draft ready")
            elif call and chased:
                short += f", chased {chased.get('to')}" + (", replied" if chased.get("replied") else "")
                if chased.get("quiet", 0) >= 5 and not chased.get("again") and not chased.get("replied"):
                    text += ". The morning brief drafts a second note"
            # Finance owns the LPs: a touch is the day's work there, above the portfolio flags it does not act on.
            touch_base = 54 if profile.get("level") == "finance" else 40
            waiting_on_them = call and chased and not drafted and (chased.get("quiet", 0) < 5 or chased.get("replied"))
            out.append(_item("lp", a["id"], title, text + (". You meet them today" if met else ""),
                             (52 if waiting_on_them else 72 if call else 70 if a["breach"] else touch_base) + (5 if met else 0), a["priority"], "CRM",
                             a.get("source_url"), breach=a["breach"], entity={"type": "lp", "id": a["lp_id"], "name": a["name"]},
                             actions=["draft", "snooze", "open"], extra={"status_word": "overdue" if a["breach"] else "due", "short": short,
                                                                         "to_email": next(iter(lp_emails.get(a["lp_id"]) or []), None),
                                                                         "alert_id": a["id"], **({"call": True, "chased": bool(chased)} if call else {}),
                                                                         **({"draft": drafted} if drafted else {})}))

    for r in (parts.get("decay") or [])[:5]:
        port = r.get("company_status") == "portfolio"
        out.append(_item("relationship", r["person_id"], f"Reconnect with {r['name']}", f"{plural(r['days_since'], 'day')} since you spoke" +
                         (f" ({r['company']}{', in our portfolio' if port else ''})" if r.get("company") else ""), 25, "low", "Email", r.get("source_url"),
                         entity={"type": "person", "id": r["person_id"], "name": r["name"]}, actions=["draft", "snooze"],
                         extra={"status_word": "cold"}))
    for r in (parts.get("needs_review") or [])[:2]:
        out.append(_item("review", f"{r.get('a_id')}-{r.get('b_id')}", f"Same person? {r['a']} and {r['b']}", r["rule"], 20, "low",
                         "ant.", "instinct://review", entity={"type": "review", "id": f"{r.get('a_id')}-{r.get('b_id')}", "name": r["a"]},
                         actions=["merge", "keep_apart"],
                         extra={"status_word": "check", "pair": {"a": r["a"], "b": r["b"], "a_email": (r.get("a_emails") or [None])[0],
                                         "b_email": (r.get("b_emails") or [None])[0]}}))
    return out


def revisit_verdict(r: dict[str, Any]) -> str:
    """What Claude found when it read the returning pitch against the revisit condition, or the condition to check."""
    chk = r.get("revisit_check") or {}
    trig = str(r.get("revisit_trigger") or "").rstrip(".")
    ev = clip(str(chk.get("evidence") or "").rstrip("."), 70)
    if chk.get("met") is True:
        return "Revisit condition met" + (f": {ev}" if ev else "")
    if chk.get("met") is False:
        return "Revisit condition not met yet" + (f": {ev}" if ev else "")
    return f"Check the revisit condition: {_lower_first(trig)}" if trig else ""


def _lower_first(text: str) -> str:
    t = (text or "").strip()
    return t[:1].lower() + t[1:] if t[:2] != t[:2].upper() else t


def _stage_key(stage_name: str, ctx: dict[str, Any]) -> str:
    return stages_mod.map_stage(stage_name, ctx["stage_map"])


def rank(items: list[dict[str, Any]], weights: dict[str, float], state: dict[str, Any], now) -> list[dict[str, Any]]:
    hidden = set()
    for item_id, st in (state.get("items") or {}).items():
        if st.get("done_at"):
            hidden.add(item_id)
        until = parse_dt(st.get("snoozed_until"))
        if until and until > now:
            hidden.add(item_id)
    ranked = []
    for it in items:
        if it["id"] in hidden or (it.get("commitment_id") and it["commitment_id"] in hidden):
            continue
        w = weights.get(it["group"], 1.0)
        if w <= 0:
            continue
        due = parse_dt(it.get("due"))
        urgency = 1.0
        if due:
            hours = (due - now).total_seconds() / 3600
            work = due.date()
            if it["kind"] == "commitment" and work.weekday() >= 5 and work > now.date():
                work -= timedelta(days=work.weekday() - 4)  # a promise due at the weekend is Friday's work
            if work == now.date() and it["kind"] != "meeting":
                urgency = 1.3  # deadline day wins
            elif hours < 0:
                urgency = 1.15
            elif hours <= 48:
                urgency = 1.1
        ranked.append({**it, "score": round(it["base"] * w * urgency, 1)})
    ranked.sort(key=lambda it: (-it["score"], it.get("due") or "9999"))
    return ranked


def _two(detail: Any) -> str:
    """A hero's finding: its first sentence, plus when you meet them. Two facts at most; the rest is one tap away."""
    parts_ = [p_ for p_ in re.split(r'(?<=[.!?…"])\s+(?=[A-Z])', str(detail or "").strip()) if p_]
    if len(parts_) <= 2:
        return " ".join(parts_)
    meet = next((p_ for p_ in parts_[1:] if p_.startswith("You meet them")), None)
    return " ".join([parts_[0]] + ([meet] if meet else [parts_[1]]))


# A promise to share what a meeting decides: never drafted or pushed before that meeting.
OUTCOME = re.compile(r"\b(outcome|result|results|verdict|decision|feedback from)\b", re.I)

LETTER = re.compile(r"\b(LP|investor|quarterly)\b[^.]{0,20}\b(letter|update|report)\b", re.I)
TITLE_STOP = {"meeting", "catch", "check", "update", "weekly", "partner", "partners", "review", "intro", "introduction", "founder",
              "founders", "community", "session", "follow", "sync", "monday", "tuesday", "wednesday", "thursday", "friday",
              "quarterly", "annual", "planning", "discussion", "board"}


HERO_KICKER = {"signal": "Another fund is moving", "commitment": "You promised", "question": "A founder is waiting", "decision": "Decide",
               "portfolio": "Portfolio",
               "ask": "A founder asks", "review": "Same person?",
               "lp": "LP due a touch", "inbound": "Inbound", "pass_returned": "Back from the pass log", "stale": "Pipeline",
               "waiting": "Waiting on them", "board": "Board prep", "relationship": "Relationships", "deal_move": "Pipeline"}


def hero(ranked: list[dict[str, Any]], prep_by_meeting: dict[str, Any], now, tz: str | None = None) -> dict[str, Any]:
    """The one thing. A meeting inside 90 minutes leads with the fact that matters in the room; otherwise the
    highest-scored item leads, stated as a fact, with today's agenda beside it."""
    meetings = sorted([r for r in ranked if r["kind"] == "meeting"], key=lambda r: r["due"])
    meet = next((it for it in meetings if 0 <= (parse_dt(it["due"]) - now).total_seconds() / 60 <= 90), None)
    if meet:
        prep = next((p for p in prep_by_meeting.values() if p.get("id") == meet.get("prep_id")), {})
        mins = int((parse_dt(meet["due"]) - now).total_seconds() // 60)
        fact = prep.get("finding") or meet["detail"] or meet.get("title")
        return {"kind": "meeting", "item_id": meet["id"], "prep_id": meet.get("prep_id"),
                "kicker": f"In {mins} min · {meet.get('time')} · {prep.get('who') or meet['title']}",
                "statement": fit_sentences(fact, 110), "finding": fit_sentences(prep.get("second") or "Prep is ready: last contact, open promises and questions.", 140),
                "button": "Prep me", "source": meet["source"], "entity": meet.get("entity")}
    top = next((it for it in ranked if it["kind"] != "meeting"), None)
    if top and top["kind"] == "signal":
        # A late promise to the company in the race leads instead: it names the race, and it is the thing to do now.
        co_ = (top.get("entity") or {}).get("name")
        top = next((it for it in ranked if it["kind"] == "commitment" and it.get("rival") and it.get("status_word") == "overdue" and
                    co_ and it.get("to_company") == co_), top)
    if top:
        # Hero grammar: the kicker names the kind and at most one fact the statement and finding do not already say.
        kicker = HERO_KICKER.get(top["kind"], "Needs you")
        if top["kind"] == "lp" and top.get("short", "").startswith("owes "):
            kicker = "Capital call"
        if top.get("group_asks"):
            kicker = "Founder asks · one note"
        if top["kind"] == "signal" and "passed" in str(top.get("short") or ""):
            kicker = "Their deadline passed"  # a race whose date has gone is not a fund moving: still worth a call, not news
        finding = _two(top["detail"])
        if top["kind"] == "commitment" and top.get("status_word") == "overdue":
            late = top.get("days_late")
            kicker = f"You promised · {plural(late, 'day')} late" if late else "You promised · overdue"
            finding = re.sub(r", \d+ days? late\b", "", finding)  # the kicker already says how late
        gl_ = gaps_line(top.get("draft_gaps") or 0, top.get("holder"))
        if gl_ and gl_ not in finding:  # what the draft still needs is never cut from the hero
            finding = finding.rstrip(".") + f". {gl_}"
        return {"kind": top["kind"], "item_id": top["id"], "kicker": kicker, "statement": top["title"], "finding": finding,
                "short": top.get("short"),
                "button": "Open", "source": top["source"], "breach": top.get("breach", False), "entity": top.get("entity"),
                "deal_id": top.get("deal_id"), "commitment_id": top.get("commitment_id"), "question_id": top.get("question_id"),
                "draft": top.get("draft"),
                **{k: top.get(k) for k in ("to_name", "to_company", "days_late", "due", "status_word", "rival", "contested", "internal",
                                           "after", "decide_first", "fyi")},
                **{k: top[k] for k in ("group_asks", "push_line", "push_lines", "note_group", "ask_state", "state_label", "draft_gaps", "holder",
                                       "alert_id", "call", "chased", "ready_form") if top.get(k)}}
    return {"kind": "calm", "item_id": None, "kicker": "All clear", "statement": "Nothing needs you",
            "finding": "ant. keeps watching your inbox, calendar and pipeline.", "button": None, "source": None}


def fit_budget(ranked: list[dict[str, Any]], max_items: int, max_words: int) -> list[dict[str, Any]]:
    chosen: list[dict[str, Any]] = []
    total = 0
    for it in ranked:
        if len(chosen) >= max_items:
            break
        cost = words(it["title"]) + words(it["detail"]) + 2
        if chosen and total + cost > max_words:
            # Over the budget: the sentence that matters if it fits (another fund's race when the row has one, else the
            # first), else the shortest; a row never goes out as a title with nothing under it.
            sents = [x.strip() for x in re.split(r"(?<=[.!?])\s+", str(it.get("detail") or "")) if x.strip()]
            race = next((x for x in sents if RACE_WORDS.search(x)), None) if it.get("rival") else None
            picks = [x for x in [race, sents[0] if sents else None] + sorted(sents, key=len) if x]
            first = next((fit_sentences(x, 90) for x in picks if total + words(it["title"]) + words(fit_sentences(x, 90)) + 2 <= max_words), "")
            if not first:
                continue
            trimmed = {**it, "detail": first}
            cost = words(it["title"]) + words(trimmed["detail"]) + 2
            chosen.append(trimmed)
        else:
            chosen.append(it)
        total += cost
    return chosen


RACE_WORDS = re.compile(r"\b(other funds?|term sheet|wants to lead|offers?|decides? by|decide by|deadline|is moving)\b", re.I)
LINKISH = re.compile(r"<[^<>|]{0,300}\|([^<>]{0,200})>|<(https?://[^>\s]+)>|\[([^\]]{0,200})\]\((?:https?://)?[^)\s]+\)|https?://\S+", re.I)


def clean(text: Any) -> str:
    """Text that came from email or notes, made inert for chat and copy: no live links, no markup."""
    t = LINKISH.sub(lambda m: m.group(1) or m.group(3) or "(link removed)", str(text or ""))
    return t.replace("<", "(").replace(">", ")").replace("*", "").replace("_", " ").replace("`", "'")


def render_text(brief: dict[str, Any], links: bool = True) -> str:
    """The brief as text for chat or for the user to copy. Only ant.'s own source links are live."""
    lines = [f"*{brief['date_label']} · {brief['headline']}*" if links else f"{brief['date_label']} · {brief['headline']}"]
    def link_for(src: dict[str, Any] | None) -> str:
        src = src or {}
        if not src.get("label"):
            return ""
        if links and src.get("url") and str(src["url"]).startswith("http"):
            return f" [{src['label']}]({src['url']})"
        return f" ({src['label']})"

    h = brief.get("hero") or {}
    if h.get("statement") and h.get("kind") != "calm":
        lines.append(f"{clean(h.get('kicker'))}: {clean(h['statement'])}" + (f". {clean(h['finding'])}" if h.get("finding") else "") +
                     link_for(h.get("source")))
    if brief.get("meetings"):
        lines.append("Meetings:")
        for m in brief["meetings"][:8]:
            note = "; ".join(clean(n) for n in m.get("notes") or [])
            lines.append(f"- {m['time']} {clean(m['who'])}" + (" (internal)" if m.get("internal") else "") + (f": {note}" if note else "") +
                         link_for(m.get("source")))
    for sec in brief["sections"]:
        lines.append(f"_{sec['label']}_" if links else sec["label"])
        for it in sec["items"]:
            lines.append(f"- {clean(it['title'])}" + (f": {clean(it['detail'])}" if it.get("detail") else "") + link_for(it["source"]))
    lines.append(brief["evidence"])
    return "\n".join(lines)


def build(ctx: dict[str, Any], profile: dict[str, Any], config: dict[str, Any], parts: dict[str, Any], state: dict[str, Any],
          mode: str = "daily") -> dict[str, Any]:
    now = ctx["now"]
    weights = {**profile["weights"], **(config.get("weights") or {})}
    items = candidates(ctx, profile, parts)
    ranked = rank(items, weights, state, now)
    max_items = int(config.get("today_items") or profile["today_items"])
    max_words = int(config.get("brief_words") or profile["brief_words"])
    meeting_items = [it for it in ranked if it["kind"] == "meeting"]
    the_hero = hero(ranked, (parts.get("prep_by_meeting") or {}), now, ctx["tz"])
    # One line per company: the hero's company, and inbound or stale repeats of the same company, are not listed twice.
    hero_names = set()
    if the_hero.get("kind") == "meeting":
        card = next((c for c in (parts.get("prep_by_meeting") or {}).values() if c.get("id") == the_hero.get("prep_id")), {})
        hero_names = {str((card.get("deal") or {}).get("company") or "").lower(), str(card.get("who") or "").split(", ")[-1].lower()} - {""}
    # Each company once: what concerns a company you meet today sits under that meeting on the agenda.
    lookup = ctx["lookup"]
    meet_of_company: dict[str, str] = {}
    meet_of_person: dict[str, str] = {}
    title_words: dict[str, set[str]] = {}
    # The first distinctive word of each company's name: "orbit" for Orbit Treasury.
    company_words = {w[0] for w in (re.findall(r"[a-z]{4,}", str(c.get("name") or "").lower()) for c in (ctx.get("companies") or {}).values())
                     if w and w[0] not in TITLE_STOP}
    for m in parts.get("meetings_today") or []:
        for pid in m.get("external_ids") or []:
            p = lookup.get(pid) or {}
            for e in p.get("emails") or []:
                meet_of_person[str(e).lower()] = m["id"]
            if p.get("company_id"):
                meet_of_company[p["company_id"]] = m["id"]
        title_words[m["id"]] = {w for w in re.findall(r"[a-z]{4,}", str(m.get("title") or "").lower()) if w in company_words}
    notes: dict[str, list[tuple[str, str | None]]] = {}
    # A deal in today's sync pack is on the agenda under that meeting, with the room's facts: a colleague's deal stays
    # off Today for the rest of the day once the sync has covered it; your own votes are named in the sync's line.
    packs_today = [((parts.get("prep_by_meeting") or {}).get(m["id"]) or {}) for m in parts.get("internal_today") or [] if m.get("start")]
    in_pack = {r.get("deal_id") for pk in packs_today for r in pk.get("decisions") or [] if r.get("kind") != "stalled"} | \
        set(parts.get("covered_today") or [])
    upcoming_pack = {r.get("deal_id") for m in parts.get("internal_today") or [] if m.get("start") and m["start"] >= now
                     for r in (((parts.get("prep_by_meeting") or {}).get(m["id"]) or {}).get("decisions") or []) if r.get("kind") != "stalled"}
    me_ = norm_email(ctx.get("user_email"))
    own_in_pack = {d["id"] for d in ctx["deals"] if d.get("owner_email") == me_}  # your own races stay in Next up too
    seen_company: set[str] = set()
    rest = []
    inbound_shown = 0
    for it in ranked:
        if it["kind"] == "meeting":
            continue
        ent = it.get("entity") or {}
        cid = ent.get("company_id") or (ctx["companies"].get(ent.get("id")) or {}).get("id") or \
            (next((d.get("company_id") for d in ctx["deals"] if d["id"] == it.get("deal_id")), None) if it.get("deal_id") else None)
        mid = meet_of_company.get(cid) if cid else None
        mid = mid or meet_of_person.get(str(it.get("to_email") or it.get("from_email") or "").lower())
        if not mid and it["kind"] in ("commitment", "waiting"):
            # Only a company's name ties a promise to a meeting by words: "diligence" in two titles is not a link.
            said = {w for w in re.findall(r"[a-z]{4,}", str(it.get("title") or "").lower()) if w in company_words}
            mid = next((k for k, ws in title_words.items() if ws & said), None)
        if mid and it["kind"] in ("signal", "commitment", "waiting", "question", "stale", "deal_move", "decision", "portfolio", "ask", "inbound",
                                  "pass_returned", "lp"):
            line = it.get("short") or it["title"]
            if it["kind"] == "commitment":
                line = (f"Looks done: {_lower_first(it['title'])}" if it.get("status_word") == "looks_done" else
                        f"You owe: {_lower_first(it['title'])}" + (" (overdue)" if it.get("status_word") == "overdue" else ""))
            elif it["kind"] == "waiting":
                line = f"They owe: {_lower_first(str(ent.get('name') or it['title'].split(': ', 1)[-1]).rstrip('.'))}" + \
                    (f" ({plural(it['days_late'], 'day')} late)" if it.get("days_late") else "")
            elif it["kind"] == "signal":
                line = "Watch: " + (it.get("short") or it["title"].split(": ", 1)[-1])
            elif it["kind"] == "pass_returned":
                line = (it.get("short") or "back from the pass log")
                line = line[:1].upper() + line[1:]
            elif it["kind"] == "lp":
                line = "LP: " + str(it.get("detail") or "").split(". You meet", 1)[0]
            elif it["kind"] == "ask":
                line = it.get("meet_line") or "They asked: " + _lower_first(it.get("short") or it["title"].split(": ", 1)[-1])
            elif it["kind"] == "portfolio":
                line = it["title"].split(": ", 1)[-1] + (f": {it['detail'].split('. Board')[0]}" if it.get("detail") else "")
            notes.setdefault(mid, []).append((line, it.get("commitment_id") if it["kind"] == "commitment" else
                                              f"action:{it['id']}" if it["kind"] == "ask" else None))
            if it["id"] != the_hero.get("item_id"):
                continue
        if it["id"] == the_hero.get("item_id"):
            continue
        if it["kind"] in ("decision", "signal") and it.get("deal_id") in in_pack and it.get("deal_id") not in own_in_pack:
            continue  # a colleague's deal to decide is on the agenda under the partner sync, with its pack
        if it["kind"] == "decision" and it.get("deal_id") in in_pack and it["id"] != the_hero.get("item_id"):
            continue  # your own vote went to today's sync: it does not come back as a row after the room decided
        if it["kind"] == "decision" and it.get("deal_id") in upcoming_pack and it["id"] != the_hero.get("item_id"):
            continue  # your own vote is named in the sync's agenda line ("with yours: ..."), not repeated in Next up
        name = str(ent.get("name") or "").lower()
        if it["kind"] in ("inbound", "pass_returned", "stale", "deal_move") and name:
            if name in hero_names or name in seen_company:
                continue
            seen_company.add(name)
        if it["kind"] in ("inbound", "pass_returned") and it.get("status_word") == "flagged":
            seen = parse_dt(it.get("seen_at"))
            if seen and now - seen > timedelta(hours=20):
                continue  # the warning had its morning on Today; it stays on the Pitches list
        if it["kind"] in ("inbound", "pass_returned") and it.get("status_word") != "flagged":
            inbound_shown += 1  # a pitch that hid instructions for AI tools is shown its first morning, whatever the cap
            if inbound_shown > INBOUND_CAP:
                continue  # the rest wait in the Pipeline tab's Inbound list
        rest.append(it)
    # One row per company: a stale or moved deal folds into the company's other row (a promise, a signal, an ask) as
    # one more sentence, so "Cobalt AA" is not two lines.
    names = {c.get("id"): str(c.get("name") or "") for c in (ctx.get("companies") or {}).values() if c.get("name")}
    deal_co = {d["id"]: d.get("company_id") for d in ctx["deals"]}

    def company_of(it: dict[str, Any]) -> str | None:
        ent = it.get("entity") or {}
        cid = ent.get("company_id") or (deal_co.get(it.get("deal_id")) if it.get("deal_id") else None)
        if cid:
            return cid
        title = str(it.get("title") or "")
        return next((k for k, n in names.items() if len(n) > 3 and re.search(rf"\b{re.escape(n)}\b", title, re.I)), None)
    folded: set[str] = set()
    for it in rest:
        if it["kind"] not in ("stale", "deal_move"):
            continue
        cid = company_of(it)
        host = next((x for x in rest if x is not it and x["kind"] not in ("stale", "deal_move") and x["id"] not in folded
                     and cid and company_of(x) == cid), None)
        if host:
            # "Deal: moved to Second meeting." The company is the host row's own, so the fact never repeats its name.
            fact = it["title"].split(": ", 1)[-1] if ": " in it["title"] else it["title"]
            name_ = str((it.get("entity") or {}).get("name") or "")
            label_ = name_ or "Deal"  # the deal by name, even when the row's title mentions it: "Cobalt AA: next step was due 15 Oct"
            host["detail"] = fit_sentences(join_sentences(str(host.get("detail") or ""), f"{label_}: {_lower_first(fact)}."), 160)
            folded.add(it["id"])
    rest = [it for it in rest if it["id"] not in folded]
    # An analyst's colleagues' races are context, not their work: one grey line after their own, never urgent rows.
    team = sorted((it for it in rest if it.get("fyi")), key=lambda it: (-round(float(it.get("score") or 0), 3), str(it.get("title"))))
    if team:
        rest = [it for it in rest if not it.get("fyi")]
        named = []
        for it in team:
            lead = re.search(r"\((\w+) leads\)", it["title"])
            named.append(f"{(it.get('entity') or {}).get('name') or it['title'].split(':')[0]}" + (f" ({lead.group(1)})" if lead else ""))
        shown, tail = [], ""
        for k, n in enumerate(named):
            more = len(named) - k - 1
            tail_ = f", and {more} more" if more else ""
            if len(", ".join(shown + [n]) + tail_) > 120 and shown:
                tail = f", and {len(named) - k} more"
                break
            shown.append(n)
        detail = ", ".join(shown) + tail + ". Each is on the Pipeline tab."
        rest.append(_item("signal", "team_races", f"{plural(len(team), 'deal')} your colleagues lead "
                          f"{'has' if len(team) == 1 else 'have'} a competing fund", detail, 20, "low", "CRM",
                          (team[0].get("source") or {}).get("url"), entity={"type": "team", "id": "team_races"},
                          actions=["open"], extra={"status_word": "team", "fyi": True, "score": 0}))
    slots = max(1, max_items - (1 if the_hero.get("item_id") and the_hero["kind"] != "meeting" else 0))
    fixed = words(f"{the_hero.get('kicker') or ''} {the_hero.get('statement') or ''} {the_hero.get('finding') or ''}")
    for mid, lines in notes.items():
        fixed += sum(words(l) for l, _ in lines[:3]) + 4
    max_words = max(60, max_words - fixed)
    # A level can reserve places: a solo GP is also their own analyst, so the best pitches always reach Today.
    for group, n in (profile.get("quota") or {}).items():
        best = [it for it in rest if it["group"] == group][:n]
        missing = [it for it in best if rest.index(it) >= slots - len(best)]
        for it in missing:
            rest.remove(it)
        for k, it in enumerate(missing):
            rest.insert(max(0, slots - len(missing) + k), it)
    # The colleagues' line closes Today, after the pitches too: context, never the first thing to do, and it never
    # takes the place of the user's own work.
    team_line = [it for it in rest if it.get("status_word") == "team"][:1]
    if team_line:
        slots = max(1, slots - 1)
    chosen = fit_budget([it for it in rest if it.get("status_word") != "team"], slots, max_words)
    # One fact, one line: a late promise leads because another fund is moving, and says so, unless the race has its own
    # row on Today or is the hero; then the race says it once, there.
    hero_it = next((x for x in ranked if x["id"] == the_hero.get("item_id")), None) if the_hero.get("item_id") else None
    race_cos = {company_of(x) for x in chosen + ([hero_it] if hero_it else []) if x and x["kind"] == "signal"} - {None}
    for i_, it in enumerate(chosen):
        if it["kind"] == "commitment" and it.get("rival") and company_of(it) in race_cos:
            phrase = f". {it['rival'][:1].upper()}{it['rival'][1:]}"
            if phrase in str(it.get("detail") or ""):
                chosen[i_] = {**it, "detail": str(it["detail"]).replace(phrase, "", 1), "rival_cut": it["detail"]}
    if hero_it and hero_it["kind"] == "commitment" and hero_it.get("rival") and company_of(hero_it):
        # The hero is the late promise and names the race: the race's own row would only say it again.
        chosen = [x for x in chosen if not (x["kind"] == "signal" and company_of(x) == company_of(hero_it))]
    # The next four, in order of what matters most to this person, read as one list under the hero. The rest
    # group by kind, the groups ordered by their best line.
    pitches = [it for it in chosen if it["kind"] in ("inbound", "pass_returned")]
    if len(pitches) >= 2:  # pitches read as one list, never split between Next up and the inbound section
        others = [it for it in chosen if it not in pitches]
        top, later = others[:NEXT_UP], others[NEXT_UP:] + pitches
    else:
        top, later = chosen[:NEXT_UP], chosen[NEXT_UP:]
    sections = [{"key": "top", "label": "Next up", "items": top}] if top else []
    best: dict[str, float] = {}
    for it in later:
        best[it["section"]] = max(best.get(it["section"], 0), it.get("score", 0))
    for key in sorted(best, key=lambda k: (-best[k], SECTION_ORDER.index(k) if k in SECTION_ORDER else 99)):
        its = [it for it in later if it["section"] == key]
        label = SECTION_LABEL[key] if not (key == "decide" and len(its) > 1) else "Decisions"
        sections.append({"key": key, "label": label, "items": its})
    if team_line:
        sections.append({"key": "team", "label": "Your team's deals", "items": team_line})
        chosen = chosen + team_line
    def top_notes(mid: str) -> list[tuple[str, str | None]]:
        seen_lines, out_ = set(), []
        for line, cid in notes.get(mid) or []:
            if line not in seen_lines:
                seen_lines.add(line)
                out_.append((line, cid))
        return out_[:3]
    meetings = [{"id": it["entity"]["id"], "time": it.get("time"), "start": it.get("due"), "who": it["title"].split(" · ", 1)[-1],
                 "prep_id": it.get("prep_id"), "item_id": it["id"], "source": it["source"],
                 "notes": [n for n, _ in top_notes(it["entity"]["id"])], "note_ids": [c for _, c in top_notes(it["entity"]["id"])],
                 "note_drafts": [((parts.get("drafts_by_action") or {}).get(c[7:]) if str(c).startswith("action:") else
                                  (parts.get("drafts_by_commitment") or {}).get(c)) if c else None for _, c in top_notes(it["entity"]["id"])]}
                for it in sorted(meeting_items, key=lambda it: it["due"])]
    tz = ctx["tz"]
    own_deals = {d["id"] for d in ctx["deals"] if d.get("owner_email") == me_}
    for m in parts.get("internal_today") or []:
        pcard = (parts.get("prep_by_meeting") or {}).get(m["id"]) or {}  # a partner sync or IC has its decision pack
        meetings.append({"id": m["id"], "time": fmt_time(m["start"], tz), "start": m["start"].isoformat(), "who": m.get("title") or "Internal",
                         "internal": True, "prep_id": pcard.get("id"), "item_id": None, "source": {"label": "Calendar", "url": m.get("url")},
                         "notes": agenda_for(pcard, own_deals)})
    meetings.sort(key=lambda m: m.get("start") or "")
    # The next working day's meetings, each opening its prep: on a Friday, "Monday" rather than an empty tomorrow.
    day_after = (ctx["now"] + timedelta(days=1)).date()
    tomorrow = [{"id": m["id"], "time": fmt_time(m["start"], tz), "start": m["start"].isoformat(),
                 "who": ((parts.get("prep_by_meeting") or {}).get(m["id"]) or {}).get("who") or m.get("title"),
                 **({"day": m["start"].astimezone(tzinfo(tz)).strftime("%A")} if m["start"].astimezone(tzinfo(tz)).date() != day_after else {}),
                 "prep_id": ((parts.get("prep_by_meeting") or {}).get(m["id"]) or {}).get("id")} for m in parts.get("tomorrow") or []]
    # A hero about someone you meet today says so, and opens that meeting's prep.
    if the_hero.get("item_id") and the_hero.get("kind") != "meeting":
        hit = next((it for it in ranked if it["id"] == the_hero["item_id"]), None)
        for m in meetings:
            if hit and any((n == (hit.get("short") and "Watch: " + hit["short"])) or (hit["title"].lower() in n.lower()) or
                           (n.startswith("You owe: ") and _lower_first(hit["title"]) in n) for n in m.get("notes") or []):
                if m.get("start") and parse_dt(m["start"]) and parse_dt(m["start"]) >= now:
                    # The meeting goes in the finding, not the kicker: one kicker fact is enough.
                    fnd, at = str(the_hero.get("finding") or ""), f"You meet them at {m['time']}"
                    if "You meet them today" in fnd:
                        the_hero["finding"] = fnd.replace("You meet them today", at)
                    elif at not in fnd:
                        the_hero["finding"] = join_sentences(fnd, at)
                    # A board with cash tight and a hiring ask: the board's question goes with you into the room.
                    bq = ((parts.get("prep_by_meeting") or {}).get(m["id"]) or {}).get("board_question")
                    if bq and bq not in str(the_hero.get("finding") or ""):
                        the_hero["finding"] = join_sentences(str(the_hero.get("finding") or ""), bq)
                    the_hero["meeting_time"] = m["time"]
                    if m.get("prep_id"):
                        the_hero.update({"button": "Prep me", "prep_id": m["prep_id"]})
                break
    sources = {it["source"]["label"] for it in chosen + meeting_items if it.get("source")}
    total = len(chosen) + (1 if the_hero.get("item_id") and the_hero.get("kind") != "meeting" else 0)
    urgent = sum(1 for it in chosen if it["priority"] == "urgent") + (1 if the_hero.get("breach") else 0)
    headline = ("nothing needs you" if not total and the_hero["kind"] == "calm" else
                f"{total} thing{'s' if total != 1 else ''} for today" + (f", {urgent} urgent" if urgent else ""))
    found = parts.get("found_at") or now
    brief = {
        "as_of": now.isoformat(), "mode": mode, "date_label": f"{now.strftime('%a')} {fmt_short_date(now)}", "headline": headline,
        "hero": the_hero, "meetings": meetings, "tomorrow": tomorrow[:4], "sections": sections, "count": len(chosen),
        "evidence": f"ant. · {len(sources)} source{'s' if len(sources) != 1 else ''} · found at {fmt_time(found, ctx['tz'])}",
        # Everything due today, shown or not, so the morning push can name it even when Today has no room; and what an
        # earlier push today named, so it stays on Today until it is done.
        "due_today": [dict(it) for it in ranked if it["kind"] != "meeting" and (str(it.get("due") or "")[:10] == now.date().isoformat() or
                                                                                it["id"] in set(parts.get("pinned_ids") or []))][:10],
        "next_check": parts.get("next_check"), "next_check_at": parts.get("next_check_at"), "ranked_ids": [it["id"] for it in ranked],
        "covered_today": list(parts.get("covered_today") or []), "covered_date": now.date().isoformat(),
        "ranked_deal_ids": list(dict.fromkeys(it["deal_id"] for it in ranked if it.get("deal_id"))),
    }
    brief["text"] = render_text(brief)
    brief["words"] = words(render_text(brief, links=False))  # what the user reads, not link addresses
    # The budget counts everything the user reads: header, meeting names, labels and sources too. Over it, the last
    # line of the last section goes first; the hero, the agenda and the first three lines always stay.
    budget = int(config.get("brief_words") or profile["brief_words"])
    hero_counts = 1 if the_hero.get("item_id") and the_hero.get("kind") != "meeting" else 0
    def over() -> bool:
        return brief["words"] > budget
    # First the third line under a busy meeting (what they owe us comes last), then the last line of the last section.
    for m in sorted(brief["meetings"], key=lambda m: -len(m.get("notes") or [])):
        if not over():
            break
        if len(m.get("notes") or []) > 2 and not (m.get("internal") and "with yours" in str(m["notes"][2])):  # your own votes stay
            for k in ("notes", "note_ids", "note_drafts"):
                if isinstance(m.get(k), list):
                    m[k] = m[k][:2]
            brief["text"] = render_text(brief)
            brief["words"] = words(render_text(brief, links=False))
    today_iso = now.date().isoformat()
    # Lines due today stay: the morning push names one, and every pushed line must be on Today.
    pinned = set(parts.get("pinned_ids") or [])

    def keep(it: dict[str, Any]) -> bool:
        return ((str(it.get("due") or "")[:10] == today_iso or it["id"] in pinned) and it.get("kind") != "meeting" and
                it.get("status_word") != "looks_done") or bool(it.get("late_fold"))
    while over() and sum(len(sec["items"]) for sec in brief["sections"]) > 3:
        spot = next(((si, ii) for si in range(len(brief["sections"]) - 1, -1, -1)
                     for ii in range(len(brief["sections"][si]["items"]) - 1, -1, -1)
                     if not keep(brief["sections"][si]["items"][ii])), None)
        if not spot:
            break
        brief["sections"][spot[0]]["items"].pop(spot[1])
        brief["sections"] = [sec for sec in brief["sections"] if sec["items"]]
        refresh(brief)
    # Your own promise due today or late this past week, money owed to the fund, and a colleague's work for you that is
    # late (one line) never leave Today. A late promise another fund's race hangs on, or one a colleague waits on, stays
    # until it is done, however late. When the cap or the budget cut one, it takes the place of the last line that can
    # wait, at the end of Next up.
    def must(it: dict[str, Any]) -> bool:
        if it.get("status_word") == "looks_done" or it.get("decide_first") or (it.get("after") and (parse_dt(it["after"]) or now) > now):
            return False
        late_ = it.get("days_late") or 0
        return (it["kind"] == "commitment" and (str(it.get("due") or "")[:10] == today_iso or
                                                (it.get("status_word") == "overdue" and 0 < late_ and
                                                 (late_ <= 7 or it.get("rival") or it.get("internal"))))) or \
            (it["kind"] == "lp" and str(it.get("short") or "").startswith("owes ")) or \
            (it["kind"] == "waiting" and it.get("section") == "team" and it.get("to_you") and 0 < late_)
    waiting_kept = 0
    for it in ranked:
        if it["kind"] == "meeting" or not must(it) or _on_today(brief, it):
            continue
        if it["kind"] == "waiting":
            if waiting_kept >= 1:
                continue
            waiting_kept += 1
        rows_ = [(si, ii) for si in range(len(brief["sections"]) - 1, -1, -1) for ii in range(len(brief["sections"][si]["items"]) - 1, -1, -1)]
        if brief["count"] + (1 if the_hero.get("item_id") and the_hero.get("kind") != "meeting" else 0) >= max_items:
            spot = next(((si, ii) for si, ii in rows_ if not must(brief["sections"][si]["items"][ii]) and
                         not keep(brief["sections"][si]["items"][ii])), None)
            if spot is None:
                continue
            brief["sections"][spot[0]]["items"].pop(spot[1])
            brief["sections"] = [sec for sec in brief["sections"] if sec["items"]]
        top = next((sec for sec in brief["sections"] if sec.get("key") == "top"), None)
        if top is None:
            top = {"key": "top", "label": "Next up", "items": []}
            brief["sections"].insert(0, top)
        top["items"].append({**it, "section": "top"})
        refresh(brief)
    # Your own promises more than a week late that no race holds up and the cap left off: one line, with how late
    # each is, never silence. Their drafts stay under Ready for you.
    late_left = [it for it in ranked if it["kind"] == "commitment" and it.get("status_word") == "overdue" and
                 (it.get("days_late") or 0) > 7 and not _on_today(brief, it) and not it.get("decide_first")]
    spot_f = None
    if late_left and brief["count"] + hero_counts >= max_items:
        # The line counts against Today's items: at the cap, the last line that can wait goes to make room. When no
        # line can wait, the week-late promise on Today that matters least joins the line instead (one with no race
        # first), so Today stays at its cap and that promise is still named, with how late it is.
        rows_f = [(si, ii) for si in range(len(brief["sections"]) - 1, -1, -1) for ii in range(len(brief["sections"][si]["items"]) - 1, -1, -1)]
        spot_f = next(((si, ii) for si, ii in rows_f if not must(brief["sections"][si]["items"][ii]) and
                       not keep(brief["sections"][si]["items"][ii])), None)
        if spot_f is None:
            joins_ = [(si, ii) for si, ii in rows_f if (lambda x: x["kind"] == "commitment" and x.get("status_word") == "overdue" and
                                                         (x.get("days_late") or 0) > 7 and not keep(x) and not x.get("decide_first"))(brief["sections"][si]["items"][ii])]
            joins_.sort(key=lambda p_: bool(brief["sections"][p_[0]]["items"][p_[1]].get("rival")))
            if joins_:
                spot_f = joins_[0]
                late_left = [brief["sections"][spot_f[0]]["items"][spot_f[1]]] + late_left
    # When every line on Today must stay and none is a week-late promise, the line waits for room.
    if late_left and (spot_f is not None or brief["count"] + hero_counts < max_items):
        fold = late_fold(late_left)
        if spot_f is not None:
            brief["sections"][spot_f[0]]["items"].pop(spot_f[1])
            brief["sections"] = [sec for sec in brief["sections"] if sec["items"]]
        top = next((sec for sec in brief["sections"] if sec.get("key") == "top"), None)
        if top is None:
            top = {"key": "top", "label": "Next up", "items": []}
            brief["sections"].insert(0, top)
        top["items"].append(fold)
        refresh(brief)
    # A line put back never takes Today over its words: the last line that can wait goes instead.
    while over() and sum(len(sec["items"]) for sec in brief["sections"]) > 3:
        spot = next(((si, ii) for si in range(len(brief["sections"]) - 1, -1, -1)
                     for ii in range(len(brief["sections"][si]["items"]) - 1, -1, -1)
                     if not keep(brief["sections"][si]["items"][ii]) and not must(brief["sections"][si]["items"][ii])), None)
        if not spot:
            break
        brief["sections"][spot[0]]["items"].pop(spot[1])
        brief["sections"] = [sec for sec in brief["sections"] if sec["items"]]
        refresh(brief)
    # One fact, one line, still true at the end: a late promise that left its race to the race's own row says it again
    # when that row has since left Today (the cap or the budget took it).
    races_on = {company_of(x) for sec in brief["sections"] for x in sec["items"] if x["kind"] == "signal"} | \
        ({company_of(hero_it)} if hero_it and hero_it["kind"] == "signal" else set())
    for sec in brief["sections"]:
        sec["items"] = [({**{k_: v_ for k_, v_ in x.items() if k_ != "rival_cut"}, "detail": x["rival_cut"]}
                         if company_of(x) not in races_on else {k_: v_ for k_, v_ in x.items() if k_ != "rival_cut"})
                        if x.get("rival_cut") else x for x in sec["items"]]
    refresh(brief)
    # For a pushed line put on Today after the build (show_pushed): the cap, and the lines that may give way to it.
    brief["cap"] = max_items
    brief["can_wait"] = [it["id"] for sec in brief["sections"] for it in sec["items"] if not keep(it) and not must(it)]
    return brief


def late_fold(late_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """One line for your own promises more than a week late that Today has no room for, with how late each is."""
    parts_ = [{"id": it["id"], "title": it.get("title"), "days_late": it.get("days_late") or 0, "draft": it.get("draft"),
               "source": it.get("source") or {}} for it in late_rows]
    named_ = [f"{_lower_first(str(it['title']).rstrip('.'))} ({plural(it['days_late'], 'day')} late)" for it in parts_[:3]]
    return _item("commitment", "late_fold", f"{plural(len(parts_), 'promise')} more than a week late",
                 "; ".join(named_) + (f"; and {len(parts_) - 3} more" if len(parts_) > 3 else "") +
                 (". Drafts are under Ready for you" if all(it.get("draft") for it in parts_) else
                  f". {plural(sum(1 for it in parts_ if it.get('draft')), 'draft')} under Ready for you" if any(it.get("draft") for it in parts_) else ""),
                 30, "medium", (parts_[0].get("source") or {}).get("label") or "Meeting notes",
                 (parts_[0].get("source") or {}).get("url"), actions=["snooze"],
                 extra={"status_word": "overdue", "fold_of": [it["id"] for it in parts_], "fold_rows": parts_, "section": "top", "late_fold": True})


def _on_today(brief: dict[str, Any], it: dict[str, Any]) -> bool:
    """Is this item on Today: the hero, a row, or a line under one of today's meetings?"""
    hero = brief.get("hero") or {}
    if it["id"] == hero.get("item_id") or any(it["id"] == x["id"] for sec in brief.get("sections") or [] for x in sec["items"]):
        return True
    notes = {c for m in brief.get("meetings") or [] for c in m.get("note_ids") or [] if c}
    return bool((it.get("commitment_id") and it["commitment_id"] in notes) or f"action:{it['id']}" in notes)


def agenda_for(pcard: dict[str, Any], own_deals: set[str]) -> list[str]:
    """The sync's three agenda lines as this person needs them: the room's first two decisions, then the rest with the
    user's own deals named ("And 9 more, with yours: Beacon Credit Rails and Ironwood Compliance")."""
    notes = list(pcard.get("agenda_notes") or [])[:3]
    rows = [r for r in pcard.get("decisions") or [] if r.get("kind") != "stalled"]
    if len(rows) <= 3 or len(notes) < 3:
        return notes
    mine = [r["company"] for r in rows[2:] if r.get("deal_id") in own_deals]
    if not mine:
        return notes
    named = mine[0] if len(mine) == 1 else ", ".join(mine[:-1]) + f" and {mine[-1]}"
    line = f"And {len(rows) - 2} more, with yours: {named}"
    if len(line) > 90 and len(mine) > 2:
        line = f"And {len(rows) - 2} more, with yours: {', '.join(mine[:2])} and {len(mine) - 2} more"
    return notes[:2] + [line]


def refresh(brief: dict[str, Any]) -> None:
    """Count, headline, text and words again after Today's lines changed."""
    the_hero = brief.get("hero") or {}
    kept = [it for sec in brief["sections"] for it in sec["items"]]
    brief["count"] = len(kept)
    n = len(kept) + (1 if the_hero.get("item_id") and the_hero.get("kind") != "meeting" else 0)
    u = sum(1 for it in kept if it.get("priority") == "urgent") + (1 if the_hero.get("breach") else 0)
    if n or the_hero.get("kind") != "calm":
        brief["headline"] = f"{n} thing{'s' if n != 1 else ''} for today" + (f", {u} urgent" if u else "")
    brief["text"] = render_text(brief)
    brief["words"] = words(render_text(brief, links=False))


def show_pushed(brief: dict[str, Any], item_id: str | None) -> bool:
    """The item a push names is always on Today: a line due today that had no room goes to the end of Next up."""
    if not item_id:
        return False
    hero = brief.get("hero") or {}
    seen = {hero.get("item_id")} | {it["id"] for sec in brief.get("sections") or [] for it in sec["items"]}
    if item_id in seen:
        return False
    row = next((dict(x) for x in brief.get("due_today") or [] if x.get("id") == item_id), None)
    if not row:
        return False
    notes = {c for m in brief.get("meetings") or [] for c in m.get("note_ids") or [] if c}
    if row.get("commitment_id") and row["commitment_id"] in notes:
        return False  # already a line under today's meeting
    top = next((sec for sec in brief["sections"] if sec.get("key") == "top"), None)
    if top is None:
        top = {"key": "top", "label": "Next up", "items": []}
        brief["sections"].insert(0, top)
    row.setdefault("priority", "high")
    row.setdefault("section", "top")
    top["items"].append(row)
    # Today keeps its cap. A week-late promise that can wait joins the line for promises more than a week late, so it
    # is still named (two such promises become that line); otherwise the last line that can wait gives way.
    hero_n = 1 if hero.get("item_id") and hero.get("kind") != "meeting" else 0
    if brief.get("cap") and sum(len(sec["items"]) for sec in brief["sections"]) + hero_n > int(brief["cap"]):
        wait_ = set(brief.get("can_wait") or []) - {item_id}
        week_late = lambda x: x.get("kind") == "commitment" and x.get("status_word") == "overdue" and (x.get("days_late") or 0) > 7 \
            and not x.get("late_fold") and not x.get("decide_first")
        fold_ = next((x for sec in brief["sections"] for x in sec["items"] if x.get("late_fold")), None)
        rows_w = [x for sec in reversed(brief["sections"]) for x in reversed(sec["items"]) if x["id"] in wait_]
        late_w = [x for x in rows_w if week_late(x)]
        joined = late_w[:1] if fold_ is not None else (late_w[:2] if len(late_w) >= 2 else [])
        gone_ids = {x["id"] for x in joined} or {next((x["id"] for x in rows_w if not week_late(x)), None)} - {None}
        if gone_ids:
            if joined:
                new_ = late_fold(joined + list((fold_ or {}).get("fold_rows") or []))
                if fold_ is None:
                    top["items"].insert(max(0, len(top["items"]) - 1), new_)
                for sec in brief["sections"]:
                    sec["items"] = [new_ if x.get("late_fold") else x for x in sec["items"]]
            for sec in brief["sections"]:
                sec["items"] = [x for x in sec["items"] if x["id"] not in gone_ids]
            brief["sections"] = [sec for sec in brief["sections"] if sec["items"]]
    refresh(brief)
    return True
