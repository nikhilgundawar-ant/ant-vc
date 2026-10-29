"""Command line for the ant. engine. Skills call these commands; each reads JSON files and writes JSON files.

  python3 engine/instinct.py check
  python3 engine/instinct.py setup     --bundle B --out DIR [--tz TZ] [--brief-time 07:00] [--level auto] [--home-url URL]
  python3 engine/instinct.py build     --bundle B --config C --out DIR [--home HOMEDIR] [--extracted E] [--inbound I] [--kpis K] [--mode M]
  python3 engine/instinct.py validate-commitments --bundle B --extracted E [--out F]
  python3 engine/instinct.py triage    --inbound I --thesis T [--passes P] [--out F]
  python3 engine/instinct.py memo-check --memo M --sources S
  python3 engine/instinct.py intro     --bundle B --company-file FILE
  python3 engine/instinct.py actions   --home HOMEDIR
  python3 engine/instinct.py due       --home HOMEDIR [--config C] [--weekend]
  python3 engine/instinct.py questions --out DIR --questions Q
  python3 engine/instinct.py drafts    --out DIR --drafts D
  python3 engine/instinct.py schedules --config C
  python3 engine/instinct.py tune      --config C --home HOMEDIR [--out DIR]
  python3 engine/instinct.py lint      --root PLUGIN_ROOT
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
from datetime import timedelta
from typing import Any

from . import __version__
from . import brief as brief_mod
from . import commitments as commit_mod
from . import graph as graph_mod
from . import homedb, levels, lp, network, pipeline, portfolio, prep, safety, schedules, stages, thesis, timeline, tuning
from .resolve import resolve_people
from .util import clip, draft_gaps, dump, fit_line, fmt_short_date, fmt_time, join_sentences, load, money, norm_email, parse_date, parse_dt, plural, sid, tzinfo

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def _profiles() -> dict[str, Any]:
    return load(os.path.join(ROOT, "ontology", "profiles.json"))


def _emit(obj: Any) -> None:
    sys.stdout.write(json.dumps(obj, indent=2, ensure_ascii=False, default=str) + "\n")


# ---------------------------------------------------------------- setup


def cmd_setup(a: argparse.Namespace) -> int:
    bundle = load(a.bundle)
    if isinstance(bundle.get("passes"), dict):
        bundle["passes"] = list(bundle["passes"].get("passes") or [])
    if a.tz:
        bundle["tz"] = a.tz
    resolved = resolve_people(bundle)
    ctx = graph_mod.build(bundle, resolved)
    user_email = ctx["user_email"]
    guess = levels.infer(bundle, user_email)
    level = guess["level"] if a.level in (None, "", "auto") else a.level
    profile = _profiles()["profiles"][level]
    crm = bundle.get("crm") or {}
    portfolio_cos = [c for c in (crm.get("companies") or []) if c.get("status") == "portfolio"]
    suggestion = thesis.suggest_thesis(portfolio_cos, (bundle.get("passes") or []))
    open_deals = [d for d in ctx["deals"] if stages.is_active(d["stage_key"], ctx["stage_map"])]
    config = {
        "version": __version__, "level": level, "level_label": profile["label"], "level_guess": guess,
        "user_name": (bundle.get("user") or {}).get("name"), "user_email": (bundle.get("user") or {}).get("email"),
        "firm": (bundle.get("firm") or {}).get("name"), "firm_domain": ctx["firm_domain"], "tz": ctx["tz"],
        "fund": (bundle.get("firm") or {}).get("fund"), "fund_size_usd": (bundle.get("firm") or {}).get("fund_size_usd"),
        "firm_members": [{"name": m.get("name"), "email": m.get("email"), "title": m.get("title")} for m in ((bundle.get("firm") or {}).get("members") or [])],
        "brief_time": a.brief_time or "07:00", "home_url": a.home_url, "today_items": profile["today_items"],
        "brief_words": profile["brief_words"], "opens_on": profile["opens_on"], "weights": dict(profile["weights"]),
        "modules": dict(profile["modules"]), "pipeline_scope": profile["pipeline_scope"], "dwell_scale": 1.0,
        "delivery": {"home": True, "push": True}, "thesis": bundle.get("thesis"),
        "crm_system": crm.get("system"), "demo": bool(bundle.get("demo")),
    }
    summary = {
        "people": len([p for p in resolved["people"] if not p.get("colleague")]), "merges": len(resolved["merges"]),
        "needs_review": len(resolved["needs_review"]), "companies": len(ctx["companies"]), "open_deals": len(open_deals),
        "meetings_90d": sum(1 for m in ctx["meetings"] if m["start"] and m["start"] <= ctx["now"]),
        "meetings_upcoming": sum(1 for m in ctx["meetings"] if m["start"] and m["start"] > ctx["now"]),
        "threads": len((bundle.get("threads") or [])), "transcripts": len((bundle.get("transcripts") or [])),
    }
    out = {"config": config, "summary": summary, "level_guess": guess, "thesis_suggestion": suggestion,
           "confirm": [
               f"You look like {'an' if profile['label'][:1].lower() in 'aeiou' else 'a'} {profile['label'].lower()} "
               f"(confidence {guess['confidence']:.0%}). Right?",
               "Here is the thesis I drafted from what I could read: your investments, your passes and your firm's site. Right?",
               f"Morning brief at {config['brief_time']} your time?",
           ],
           "schedules": schedules.build(config)}
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        dump(config, os.path.join(a.out, "config.json"))
        dump(out, os.path.join(a.out, "setup.json"))
        dump(resolved, os.path.join(a.out, "people.json"))
    _emit({k: out[k] for k in ("summary", "level_guess", "confirm")} | {"config_file": os.path.join(a.out, "config.json") if a.out else None})
    return 0


# ---------------------------------------------------------------- build


CATEGORY_LABEL = {"email": "Email", "calendar": "Calendar", "notes": "Meeting notes", "crm": "Your CRM", "drive": "Drive", "lps": "LP data"}
STATUS_TEXT = {"revoked": "access was revoked", "rate_limited": "is busy (rate limited)", "missing": "is not connected", "error": "could not be read"}


def _lower_first(text: str) -> str:
    """"Invite Rahul" in mid-sentence reads "invite Rahul"; an acronym ("IC") stays."""
    t = str(text or "")
    return t if not t or (len(t) > 1 and t[:2].isupper()) else t[:1].lower() + t[1:]


# Words that make an LP's email outside the chase's own thread an answer about the money. Not a bare "fund": almost
# every LP email says it ("is the Fund II annual meeting in December?").
# "The call" and a bare "pay" are no answer about money ("thanks for the call yesterday", "pay a visit").
CALL_WORDS = re.compile(r"\b(wire|wired|transfer|transferred|payment|paid(?! a visit| attention| tribute)|remit|remittance|capital call|drawdown|draw-down|call notice|"
                        r"the amount|instal?ments?|contribution|pay (?:it|the|this|our|in)|will pay)\b", re.I)
# A reply that says the money already went ("we paid it last Friday"): check the account, never chase.
PAID_SAYS = re.compile(r"(?:\b(?:we|i|it|they|our bank)(?:'ve| have| has| was| had)?\s+(?:already\s+)?(?:been\s+)?(?:paid|wired|transferred|remitted|sent (?:it|the funds|the money|the wire|payment))\b"
                       r"|\b(?:payment|the wire|the transfer|the money|the funds)\s+(?:was made|was sent|were sent|has been made|has been sent|went out|has gone out|went through)\b)"
                       r"(?![^.]*\b(?:visit|a call|attention|tribute|respects)\b)", re.I)
# A reply that puts off its answer ("let me think about these and come back to you"), and one that gives it.
DEFER_WORDS = re.compile(r"\b(let me (?:think|check|come back)|come back to you|get back to you|circle back|will revert|revert by|"
                         r"think about (?:it|these|this|them)|need (?:more )?time|not sure yet|hold on (?:this|these|it))\b", re.I)
YES_WORDS = re.compile(r"\b(yes|let'?s|go ahead|happy to|agreed|ok to|okay to|please ask|no to|pass on|we pass|hold off)\b", re.I)
# A sentence about what happened, not what will: its day is never a promised one ("we paid it last Friday").
PAST_DAY = re.compile(r"\b(paid|sent|went|wired|transferred|released|did|was|were|had|last|yesterday|ago)\b", re.I)
AHEAD_DAY = re.compile(r"\b(will|shall|going to|plan|expect|next|tomorrow|by)\b", re.I)
WIRE_WORD = re.compile(r"\b(wire|transfer|payment|pay|remit|go(?:es)? out|send|release|clear|process)\b", re.I)
WEEKDAY_N = {d_: i for i, d_ in enumerate(("mon", "tue", "wed", "thu", "fri", "sat", "sun"))}


def _named_day(text: str, when) -> Any:
    """The day a reply names for what it promises ("goes out on Wednesday", "by 28 Oct", "tomorrow", "next week"), as a
    date after `when`; None when it names none or the reading is unsure. A sentence about the wire is read first; one
    about what happened ("we paid it last Friday", "thanks for Monday's call") never names the day."""
    t = str(text or "").lower()
    base = when.date() if hasattr(when, "date") else when

    def day_in(x: str) -> Any:
        # A date on or after the reply is a promise; one before it is what they answer ("the 5 Oct call").
        for m_ in re.finditer(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b", x):
            mon_ = MONTH_N[m_.group(2)[:3]]
            try:
                d_ = base.replace(month=mon_, day=int(m_.group(1)))
            except ValueError:
                continue
            if d_ < base - timedelta(days=60):
                d_ = d_.replace(year=d_.year + 1)
            if d_ >= base:
                return d_
        for m_ in re.finditer(r"\b(?:(on|by|next|this|until|last)\s+)?(mon|tue|wed|thu|fri)[a-z]*day\b('s)?", x):
            if m_.group(1) == "last" or m_.group(3):
                continue  # "last Friday", "Monday's call": a day gone by
            ahead_ = (WEEKDAY_N[m_.group(2)] - base.weekday()) % 7 or 7
            return base + timedelta(days=ahead_)
        if re.search(r"\btomorrow\b", x):
            return base + timedelta(days=1)
        if re.search(r"\b(end of (the|this) week|this week)\b", x):
            return base + timedelta(days=max(0, 4 - base.weekday()))
        if re.search(r"\bnext week\b", x):
            return base + timedelta(days=(7 - base.weekday()) + 4)  # the Friday of next week: anything in it is in time
        return None
    parts_ = [x.strip() for x in re.split(r"(?<=[.!?])\s+|\n+", t) if x.strip()]
    for x in [x for x in parts_ if WIRE_WORD.search(x)] + [x for x in parts_ if not WIRE_WORD.search(x)]:
        if PAST_DAY.search(x) and not AHEAD_DAY.search(x):
            continue
        d_ = day_in(x)
        if d_:
            return d_
    return None


def _went_at(bundle: dict[str, Any], me: str, subject: Any, tapped, known: Any = None):
    """When a note really went, for "since the note went": the user's own message in its thread, as a run finds it or
    an earlier run kept it (`known`). The note is the user's latest message there, from two weeks before the tap to
    twelve hours after it, that does not follow someone else's message: a thank-you after their reply is never the
    note, and a tap days late still finds it. Else the start of the day before the tap, since a note is often sent
    first and marked sent later, and a reply can land in between."""
    if known and parse_dt(known):
        return parse_dt(known)
    if not tapped:
        return None
    best = _note_in_thread(bundle, me, subject, tapped)
    if best:
        return best
    local_ = tapped.astimezone(tapped.tzinfo)
    return (local_ - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)


def _note_in_thread(bundle: dict[str, Any], me: str, subject: Any, tapped) -> Any:
    """The user's note in its thread (see `_went_at`), or None when this run's mail does not hold it."""
    if not tapped:
        return None
    base_ = re.sub(r"^((re|fwd?|fw):\s*)+", "", str(subject or ""), flags=re.I).strip().lower()
    best = None
    for th in (bundle or {}).get("threads") or []:
        if not base_ or re.sub(r"^((re|fwd?|fw):\s*)+", "", str(th.get("subject") or ""), flags=re.I).strip().lower() != base_:
            continue
        msgs = sorted(((parse_dt(m_.get("date")), m_) for m_ in th.get("messages") or [] if parse_dt(m_.get("date"))), key=lambda x: x[0])
        prev_me = True
        for w_, m_ in msgs:
            f_ = m_.get("from")
            mine = norm_email(f_.get("email") if isinstance(f_, dict) else f_) == me
            if mine and prev_me and tapped - timedelta(days=14) <= w_ <= tapped + timedelta(hours=12) and (not best or w_ > best):
                best = w_
            prev_me = mine
    return best


def _answers(rep: Any, note: Any) -> bool:
    """A reply Home keeps answers this note: recorded against it (`tap`), or newer than when it was marked sent."""
    if not isinstance(rep, dict) or not isinstance(note, dict) or not rep.get("on"):
        return False
    return bool((rep.get("tap") and rep.get("tap") == note.get("tap")) or str(rep.get("on") or "") > str(note.get("at") or ""))


def _was_sent(st: Any) -> bool:
    """A draft's mark in Home says it went: Sent it (`sent`), or an older mark with no word on how it closed. Done on a
    row (`closed_by: "done"`) settles that row only."""
    return bool(isinstance(st, dict) and st.get("done_at") and (st.get("sent") or st.get("closed_by") != "done"))


def _promise_ids(d: dict[str, Any]) -> list[str]:
    """Every promise a draft keeps: its own, and any promise to the same person a later morning folded into it."""
    return [x for x in dict.fromkeys([d.get("commitment_id")] + list(d.get("commitment_ids") or [])) if x]


def _local_iso(value: Any, tz_name: str | None) -> Any:
    """A UTC stamp from Home in the user's zone, same instant; anything else as it was."""
    if not isinstance(value, str) or not value or "T" not in value:
        return value
    dt = parse_dt(value)
    if not dt or not dt.tzinfo:
        return value
    return dt.astimezone(tzinfo(tz_name)).isoformat()


def _local_marks(state: dict[str, Any], tz_name: str | None) -> None:
    """Every tap time in Home's state (a done or snooze mark, an approval and what it followed) in the user's zone."""
    if not tz_name:
        return
    for row in (((state.get("items") or {}).get("items")) or {}).values():
        if isinstance(row, dict):
            for k in ("done_at", "snoozed_until"):
                if row.get(k):
                    row[k] = _local_iso(row[k], tz_name)
    for act in (((state.get("actions") or {}).get("items")) or {}).values():
        if isinstance(act, dict):
            if act.get("at"):
                act["at"] = _local_iso(act["at"], tz_name)
            after = (act.get("payload") or {}).get("after") if isinstance(act.get("payload"), dict) else None
            if isinstance(after, dict) and after.get("at"):
                after["at"] = _local_iso(after["at"], tz_name)


def _carry_forward(bundle: dict[str, Any], home: dict[str, Any], unavailable: dict[str, str]) -> dict[str, Any]:
    """Fill what this run could not read with what Home already knows. An hourly pulse reads a small window and
    a connector can fail; neither may blank a view or produce a false all-clear."""
    snap = home["snap"]
    pipe = (snap.get("pipeline") or {}).get("deals") or {}
    port = (snap.get("portfolio") or {}).get("companies") or {}
    stored_lps = (snap.get("lps") or {}).get("lps") or {}
    crm = dict(bundle.get("crm") or {})
    companies = [dict(c) for c in (crm.get("companies") or [])]
    have_c = {c.get("id") for c in companies}
    for cid, c in port.items():  # portfolio first: a portfolio company with a follow-on deal stays portfolio
        if cid not in have_c:
            companies.append({"id": cid, "name": c.get("name"), "domain": c.get("domain"), "status": "portfolio",
                              "url": c.get("source_url"), "from_home": True})
            have_c.add(cid)
    for d in pipe.values():
        cid = d.get("company_id")
        if cid and cid not in have_c:
            companies.append({"id": cid, "name": d.get("company"), "domain": d.get("domain"), "status": "pipeline", "from_home": True})
            have_c.add(cid)
    deals = [dict(d) for d in (crm.get("deals") or [])]
    # A field the read left out (a bundle written by hand can drop one) keeps what Home knew; only an explicit null
    # clears it. The run says when a read dropped a field Home holds on several deals.
    kept_fields: dict[str, int] = {}
    for d in deals:
        old_ = pipe.get(d.get("id")) or {}
        for k_ in ("round", "raise_usd", "stage_entered"):
            if k_ not in d and old_.get(k_) not in (None, "", []):
                d[k_] = old_[k_]
                kept_fields[k_] = kept_fields.get(k_, 0) + 1
    if any(n_ >= 3 for n_ in kept_fields.values()):
        crm["kept_fields"] = {k_: n_ for k_, n_ in kept_fields.items() if n_ >= 3}
    # A pulse may read only the deals changed since the last run (crm.partial): the rest come from Home. A deal is never
    # closed by being left out, even of a full read (a bundle written by hand can miss one): it stays as Home knew it
    # until a read sends it at a closed stage, and the run says which deals a full read did not list.
    have_d = {d.get("id") for d in deals}
    full_read = "crm" not in unavailable and bool(deals) and not crm.get("partial")
    smap = stages.load()
    unlisted = []
    for did, d in pipe.items():
        if did not in have_d:
            # The CRM's own stage label stays ("IC", "Due diligence"); the key Home mapped it to rides beside it.
            deals.append({"id": did, "company_id": d.get("company_id"), "company_name": d.get("company"),
                          "stage": d.get("stage") or d.get("stage_key"), "stage_key": d.get("stage_key"), "stage_entered": d.get("stage_entered"),
                          "next_step": d.get("next_step"), "next_step_due": d.get("next_step_due"), "owner": d.get("owner"),
                          "url": d.get("source_url"), "round": d.get("round"), "raise_usd": d.get("raise_usd"),
                          "last_contact": d.get("crm_last_contact") or d.get("last_contact"),
                          "quiet": d.get("quiet"), "team": d.get("team") or [], "from_home": True})
            if full_read and stages.is_active(stages.map_stage(d.get("stage_key") or d.get("stage"), smap), smap):
                unlisted.append({"id": did, "company": d.get("company")})
    if unlisted:
        crm["unlisted"] = unlisted
    for d in deals:  # a last contact Home has seen never goes backwards; the CRM's own date stays the CRM's
        prev = (pipe.get(d.get("id")) or {}).get("last_contact")
        if prev and (not d.get("last_contact") or str(prev) > str(d.get("last_contact"))[:10]):
            d["seen_contact"] = prev
    # People, other companies and the pass log: a pulse reads none of them, so the directory a wider read left in Home
    # stands in. A founder keeps their company, a quote keeps who wrote it, a fund administrator keeps its name.
    dirx = snap.get("directory") or {}
    for c in dirx.get("companies") or []:
        if isinstance(c, dict) and c.get("id") and c["id"] not in have_c:
            companies.append({**c, "from_home": True})
            have_c.add(c["id"])
    people = [dict(p) for p in (crm.get("people") or [])]
    if not people and dirx.get("people"):
        people = [{**p, "from_home": True} for p in dirx["people"] if isinstance(p, dict)]
    elif people and crm.get("people_partial") and dirx.get("people"):
        # A morning read of the people that matter today (open deals, the portfolio, today's meetings): everyone else
        # comes from the directory the last wide read left.
        seen_ = {p.get("id") for p in people if p.get("id")} | \
            {norm_email(e) for p in people for e in [p.get("email")] + list(p.get("emails") or []) if norm_email(e)}
        people += [{**p, "from_home": True} for p in dirx["people"] if isinstance(p, dict) and p.get("id") not in seen_ and
                   not ({norm_email(e) for e in [p.get("email")] + list(p.get("emails") or []) if norm_email(e)} & seen_)]
    if people:
        crm["people"] = people
    passes = bundle.get("passes")
    if passes is None and dirx.get("passes"):
        passes = [{**x, "from_home": True} for x in dirx["passes"] if isinstance(x, dict)]
    crm["companies"], crm["deals"] = companies, deals
    lps = list(bundle.get("lps") or [])
    if not lps and stored_lps:
        # A run that did not read LPs keeps every field Home holds: owner, fund and capital calls included.
        lps = [{"id": lid, "name": l.get("name"), "fund": l.get("fund"), "commitment_usd": l.get("commitment_usd"),
                "called_usd": l.get("called_usd"), "paid_in_usd": l.get("paid_in_usd"), "last_call_date": l.get("last_call_date"),
                "owner": l.get("owner"), "reup_window_start": l.get("reup_window_start"), "reup_window_end": l.get("reup_window_end"),
                "last_touch": l.get("last_touch"), "contacts": l.get("contacts") or [], "source_url": l.get("source_url"), "from_home": True}
               for lid, l in stored_lps.items()]
    return {**bundle, "crm": crm, "lps": lps, **({"passes": passes} if passes is not None else {})}


DIRECTORY_PERSON = ("id", "name", "email", "emails", "company_id", "title", "url", "strength_by_member", "tags")
DIRECTORY_COMPANY = ("id", "name", "domain", "status", "sectors", "hq", "url", "description")
DIRECTORY_PASS = ("id", "company", "domain", "date", "reason", "revisit_trigger", "by", "source_url")


def _directory(bundle: dict[str, Any], home: dict[str, Any], now_iso: str) -> dict[str, Any] | None:
    """Who and what the CRM holds, as the last wide read found it: people (with their company, title and how well each
    colleague knows them), every company and the pass log. Written only when this run read them; pulses read it back.
    People at the firm's own companies come first, so a very large CRM keeps the ones that matter if the list is cut."""
    crm = bundle.get("crm") or {}
    people = [p for p in crm.get("people") or [] if isinstance(p, dict) and not p.get("from_home")]
    companies = [c for c in crm.get("companies") or [] if isinstance(c, dict) and not c.get("from_home")]
    passes = [x for x in bundle.get("passes") or [] if isinstance(x, dict) and not x.get("from_home")]
    if not (people or companies or passes):
        return None
    old = dict((home.get("snap") or {}).get("directory") or {})
    out = {"as_of": now_iso, "people": old.get("people") or [], "companies": old.get("companies") or [], "passes": old.get("passes") or []}

    def merged(rows: list[dict[str, Any]], before: list[Any], fields: tuple[str, ...], key) -> list[dict[str, Any]]:
        """Each row read, laid over the row Home kept: a field this read did not send (a description, an id) stays."""
        prev = {key(r): r for r in before if isinstance(r, dict) and key(r)}
        return [{**{k: v for k, v in (prev.get(key(r)) or {}).items() if k in fields},
                 **{k: r[k] for k in fields if r.get(k) not in (None, "", [], {})}} for r in rows]
    if companies:
        rows_c = merged(companies, out["companies"], DIRECTORY_COMPANY, lambda c: c.get("id"))
        if crm.get("companies_partial"):  # a narrow read updates the rows it read and keeps the rest
            got = {c.get("id") for c in rows_c}
            rows_c += [c for c in out["companies"] if isinstance(c, dict) and c.get("id") not in got]
        # One order whatever was read, so a morning that changed nothing writes nothing.
        rows_c.sort(key=lambda c: (str(c.get("name") or "").lower(), str(c.get("id") or "")))
        out["companies"] = rows_c
    if people:
        ours = {c.get("id") for c in out["companies"] or companies if isinstance(c, dict) and c.get("status") in ("portfolio", "pipeline", "active")} | \
            {d.get("company_id") for d in crm.get("deals") or [] if isinstance(d, dict)}
        rows = merged(people, out["people"], DIRECTORY_PERSON, lambda p: p.get("id"))
        if crm.get("people_partial"):
            got_ = {p.get("id") for p in rows if p.get("id")}
            rows += [p for p in out["people"] if isinstance(p, dict) and p.get("id") not in got_]
        rows.sort(key=lambda p: (0 if p.get("company_id") in ours else 1 if p.get("strength_by_member") else 2, str(p.get("name") or ""),
                                 str(p.get("id") or "")))
        out["people"] = rows
    if passes:
        out["passes"] = merged(passes, out["passes"], DIRECTORY_PASS,  # a pass is its company and its date, with or without an id
                               lambda x: f"{str(x.get('domain') or x.get('company') or '').lower()}|{str(x.get('date') or '')[:10]}"
                               if (x.get("domain") or x.get("company")) else x.get("id"))
    return out


def _carried_asked(ctx: dict[str, Any], home: dict[str, Any], fresh: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """A founder's question stays open until the firm writes to them, someone meets them, the deal closes or three weeks
    pass. A narrow read (an hourly pulse, a mail outage) keeps what Home last knew."""
    pipe = ((home["snap"].get("pipeline") or {}).get("deals")) or {}
    today = ctx["now"].date()
    by_id = {d["id"]: d for d in ctx["deals"]}
    have = {q["deal_id"] for q in fresh}
    out = list(fresh)
    for did, d in pipe.items():
        a = d.get("asked")
        deal = by_id.get(did)
        if not isinstance(a, dict) or did in have or not deal:
            continue
        if not (ctx["stage_map"]["by_key"].get(deal["stage_key"]) or {}).get("active"):
            continue
        on = parse_date(a.get("on"))
        if not on or (today - on).days > 21 or pipeline.answered_since(ctx, deal.get("company_id"), on):
            continue
        out.append({"id": a.get("id"), "deal_id": did, "company": deal.get("company_name"), "company_id": deal.get("company_id"),
                    "person": a.get("person"), "email": a.get("email"), "asked_on": a.get("on"), "question": a.get("question"),
                    "subject": a.get("subject"), "thread_id": a.get("thread_id"), "source_url": a.get("source_url"), "carried": True})
    return [q for q in out if q.get("id")]


def _carried_signals(ctx: dict[str, Any], home: dict[str, Any], fresh: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep "another fund is moving" until it is resolved: deal closed or passed, or a week past its deadline
    (three weeks after it was first seen when there is no deadline)."""
    pipe = ((home["snap"].get("pipeline") or {}).get("deals")) or {}
    today = ctx["now"].date()
    by_id = {d["id"]: d for d in ctx["deals"]}
    have = {s["deal_id"] for s in fresh}
    out = list(fresh)
    for s in out:
        d = pipe.get(s["deal_id"]) or {}
        if not d.get("competing"):
            continue
        # The same race keeps its row, its push key and its ratings when the founder's email leaves the read and only the
        # team's CRM note still says it: never pushed again as news. A new email is news, and keeps its own id.
        if d.get("competing_id") and d["competing_id"] != s["id"] and s.get("shared"):
            s["id"] = d["competing_id"]
        if s.get("shared") and not d.get("competing_summary") and d.get("competing_evidence"):
            # The founder's own words, read while their email was in the window, beat the team's summary of them.
            s.update({"evidence": d["competing_evidence"], "said_by": d.get("competing_said_by") or s.get("said_by"),
                      "source_url": d.get("competing_source_url") or s.get("source_url"), "shared": False, "in_crm": True,
                      "date": d.get("competing_since") or s.get("date")})
    for did, d in pipe.items():
        if not d.get("competing") or did in have or did not in by_id:
            continue
        deal = by_id[did]
        if not ctx["stage_map"]["by_key"].get(deal["stage_key"], {}).get("active"):
            continue
        since = parse_date(d.get("competing_since")) or today
        deadline = parse_date(d.get("deadline"))
        if (deadline and (today - deadline).days > 7) or (not deadline and (today - since).days > 21):
            continue
        out.append({"id": d.get("competing_id") or sid("signal", "carried", did, prefix="s"), "kind": "round_moving", "deal_id": did,
                    "company": deal.get("company_name"), "stage": deal["stage_name"], "stage_key": deal["stage_key"], "round": deal.get("round"),
                    "company_id": deal.get("company_id"), "owner": deal.get("owner_email"), "thread_id": None,
                    "source_url": d.get("competing_source_url") or deal.get("url"), "evidence": d.get("competing_evidence") or "Another fund is moving",
                    "labels": d.get("competing_labels") or [], "funds": d.get("competing_funds") or [], "deadline": d.get("deadline"),
                    "date": since.isoformat(), "breach": True, "confidence": 0.5, "carried": True,
                    # A summary the team shared reads as one (where the deal stands, where the news came from), never as
                    # the founder's quote.
                    **({"shared": True} if d.get("competing_summary") else {}),
                    **({"said_by": d["competing_said_by"]} if d.get("competing_said_by") else {})})
    return out


def _merge_card(card: dict[str, Any], old: dict[str, Any], known: dict[str, int]) -> None:
    """A prep card rebuilt from an hour's reading keeps what an earlier, wider read found: titles, strength,
    older history, the empathy map, colleagues and context. Questions already written stay."""
    if old.get("questions"):
        card["questions"] = old["questions"]
    olds = {}
    for a in old.get("attendees") or []:
        for k in (a.get("email"), a.get("name")):
            if k:
                olds[str(k).lower()] = a
    for a in card.get("attendees") or []:
        o = olds.get(str(a.get("email") or "").lower()) or olds.get(str(a.get("name") or "").lower()) or {}
        for k in ("title", "company", "last_touch", "source_url"):
            if not a.get(k) and o.get(k):
                a[k] = o[k]
        a["strength"] = max(int(a.get("strength") or 0), int(o.get("strength") or 0), known.get(str(a.get("name") or "").lower(), 0))
    have = {(h.get("date"), h.get("text")) for h in card.get("history") or []}
    merged = (card.get("history") or []) + [h for h in old.get("history") or [] if (h.get("date"), h.get("text")) not in have]
    merged.sort(key=lambda h: str(h.get("iso") or ""), reverse=True)  # newest first, whichever read found it
    card["history"] = merged[:3]
    for k in ("empathy_map_url", "colleagues", "context"):
        if not card.get(k) and old.get(k):
            card[k] = old[k]
    if card["history"]:
        h0 = card["history"][0]
        key = f"history:{card.get('meeting_id')}"
        text = prep.last_touch_fact(h0, next((a_.get("company") for a_ in card.get("attendees") or [] if a_.get("company")), None))
        facts = [f for f in card.get("facts") or [] if f.get("key") != key]
        if len(facts) < 5:
            facts.append({"text": text, "key": key})
        card["facts"] = facts
        if not card.get("finding") and facts:
            card["finding"] = facts[0]["text"]
        if not card.get("second") and len(facts) > 1:
            card["second"] = facts[1]["text"]


def _merge_review(resolved: dict[str, Any], home: dict[str, Any], overrides: dict[str, list[list[str]]]) -> list[dict[str, Any]]:
    """Possible duplicates stay until the user answers, even when this hour's reading is too narrow to see them."""
    answered = {frozenset(e.lower() for e in pair) for pair in overrides["merge"] + overrides["apart"]}
    same = {}
    for p in resolved["people"]:
        for e in p.get("emails") or []:
            same[e.lower()] = p["id"]
    out, seen = [], set()
    for r in list(resolved["needs_review"]) + list(((home["snap"].get("review") or {}).get("items")) or []):
        a, b = [str((r.get(k) or [None])[0] or "").lower() for k in ("a_emails", "b_emails")]
        key = frozenset((a, b))
        if not a or not b or key in seen or key in answered or (a in same and same.get(a) == same.get(b)):
            continue
        seen.add(key)
        out.append(r)
    return out


def _quiet_set(ctx: dict[str, Any]) -> dict[str, set[str]]:
    deals = [d for d in ctx.get("deals") or [] if isinstance(d, dict) and d.get("quiet")]
    cids = {d.get("company_id") for d in deals if d.get("company_id")}
    names = {str(d.get("company_name") or "").lower() for d in deals} | \
        {str(((ctx.get("companies") or {}).get(c) or {}).get("name") or "").lower() for c in cids}
    return {"deals": {d["id"] for d in deals}, "companies": cids, "names": {n for n in names if len(n) >= 3}}


def _touches_quiet(obj: Any, quiet: dict[str, set[str]]) -> bool:
    if not quiet["deals"] and not quiet["companies"]:
        return False
    blob = json.dumps(obj, default=str).lower()
    return any(d.lower() in blob for d in quiet["deals"]) or any(c.lower() in blob for c in quiet["companies"]) or \
        any(n in blob for n in quiet["names"])


def build_all(bundle: dict[str, Any], config: dict[str, Any], home: dict[str, Any], extracted: list[dict[str, Any]] | None,
              inbound: list[dict[str, Any]] | None, kpis: dict[str, Any] | None, mode: str,
              applied: dict[str, Any] | None = None, extras: dict[str, Any] | None = None) -> dict[str, Any]:
    """One build: everything Home shows, from this run's reading plus what Home already holds.
    extras: {"asks": [founder asks], "digest": {"kind", "markdown"}, "run": {"id", "started", "jobs"}}."""
    extras = extras or {}
    # The build reads Home and never changes it in place: the write plan compares what was built with Home as it was,
    # so a changed warning, booked mark or looks-done mark is always written.
    home = {**home, "snap": copy.deepcopy(home.get("snap") or {}), "state": copy.deepcopy(home.get("state") or {})}
    # A run's bundle may leave out who the user is, the firm and the thesis: they come from the config.
    bundle = dict(bundle)
    if isinstance(bundle.get("passes"), dict):  # the CRM's own shape, {"passes": [...]}, works as well as a bare list
        bundle["passes"] = list(bundle["passes"].get("passes") or [])
    bundle.setdefault("tz", config.get("tz"))
    # Home stamps taps in UTC ("2026-10-23T01:35:00.000Z"): read in the user's own zone, a 01:30 tap in Mumbai counts
    # as that day, so "Asked the team on 23 Oct" and the five working days to a nudge start on the right date.
    _local_marks(home["state"], bundle.get("tz") or config.get("tz"))
    if not (bundle.get("user") or {}).get("email") and config.get("user_email"):
        bundle["user"] = {"name": config.get("user_name"), "email": config.get("user_email")}
    if not (bundle.get("firm") or {}).get("domain") and config.get("firm_domain"):
        bundle["firm"] = {"name": config.get("firm"), "domain": config.get("firm_domain"), "members": config.get("firm_members") or [],
                          "fund": config.get("fund"), "fund_size_usd": config.get("fund_size_usd")}
    elif not (bundle.get("firm") or {}).get("members") and config.get("firm_members"):
        bundle["firm"] = {**bundle["firm"], "members": config["firm_members"]}
    if not bundle.get("thesis") and config.get("thesis"):
        bundle["thesis"] = config["thesis"]
    profiles = _profiles()
    level = config.get("level", "partner")
    profile = {**profiles["profiles"][level], "level": level}
    profile["modules"] = {**profile["modules"], **(config.get("modules") or {})}
    profile["pipeline_scope"] = config.get("pipeline_scope") or profile["pipeline_scope"]
    home.setdefault("snap", {})
    home.setdefault("state", {})
    unavailable = {k: v for k, v in (bundle.get("unavailable") or {}).items() if v}
    # What this run itself read, before Home fills the gaps: each connector's window moves only when it was read.
    read_now = [k for k, field in (("email", "threads"), ("calendar", "events"), ("notes", "transcripts"), ("crm", "crm"),
                                   ("lps", "lps"), ("drive", "empathy_maps")) if bundle.get(field) is not None and k not in unavailable]
    bundle = _carry_forward(bundle, home, unavailable)
    # Taps in Home that the engine applies itself: same person, different people, quiet deal.
    approved = {k: v for k, v in (((home["state"].get("actions") or {}).get("items")) or {}).items()
                if isinstance(v, dict) and v.get("status") == "approved"}
    overrides: dict[str, list[list[str]]] = {"merge": [], "apart": []}
    quiet_deals: set[str] = {did for did, d in (((home["snap"].get("pipeline") or {}).get("deals")) or {}).items() if d.get("quiet")}
    for act in approved.values():
        pay = act.get("payload") or {}
        if act.get("type") in ("merge", "keep_apart") and pay.get("a_email") and pay.get("b_email"):
            overrides["merge" if act["type"] == "merge" else "apart"].append([pay["a_email"], pay["b_email"]])
        elif act.get("type") == "quiet" and pay.get("deal_id"):
            quiet_deals.add(pay["deal_id"])
    resolved = resolve_people(bundle, overrides)
    if mode not in ("setup", "digest"):
        resolved["needs_review"] = _merge_review(resolved, home, overrides)
    ctx = graph_mod.build(bundle, resolved)
    for d in ctx["deals"]:
        if d["id"] in quiet_deals:
            d["quiet"] = True
    # A stage moved from Home's met log entered that stage the day it was applied, even when the CRM keeps no stage
    # date or did not move it: Halo moved to Second meeting today is day 0, not day 13.
    moved_here = _applied_stage_moves(home, applied, ctx["now"], ctx["stage_map"], ctx["tz"])
    for did, (key_, when_) in moved_here.items():
        d = next((x for x in ctx["deals"] if x["id"] == did), None)
        if d and d["stage_key"] == key_ and (not d.get("stage_entered_dt") or d["stage_entered_dt"] < when_):
            d["stage_entered_dt"] = when_
            d["stage_entered"] = when_.date().isoformat()
    _date_stage_moves(ctx, home, set(moved_here))
    now = ctx["now"]
    warnings: list[str] = []
    # People read only at today's companies, on a Home with no directory yet (the first morning after an update): warm
    # paths through everyone else are missing until a wide read. connectors.md says to read wide this once.
    if ((bundle.get("crm") or {}).get("people_partial") and not (((home.get("snap") or {}).get("directory") or {}).get("people"))):
        warnings.append("People were read only at today's companies, and Home has no directory yet: warm paths through anyone else "
                        "are missing until a wide read. Read people and companies wide on the next run.")
    kept_f = (bundle.get("crm") or {}).get("kept_fields") or {}
    if kept_f:
        warnings.append("This run's CRM read left out " + ", ".join(f"{k_} on {n_} deals" for k_, n_ in kept_f.items()) +
                        ": Home kept what it knew. Send every field on the next read.")
    unlisted = (bundle.get("crm") or {}).get("unlisted") or []
    if unlisted:
        names_ = [str(u.get("company") or u.get("id")) for u in unlisted[:5]]
        warnings.append(f"{plural(len(unlisted), 'open deal')} in Home not in this CRM read ({', '.join(names_)}"
                        f"{', and more' if len(unlisted) > 5 else ''}): kept as Home knew {'it' if len(unlisted) == 1 else 'them'}. "
                        "Read each record and send it with its stage if it closed.")
    # Meetings an earlier, wider read saw: an hourly pulse reads only today and tomorrow, and a deal met on Thursday
    # must not turn stale again on Friday's pulses.
    ctx["met_carried"] = {}
    for d in (((home["snap"].get("pipeline") or {}).get("deals")) or {}).values():
        met_dt = parse_dt(d.get("last_met"))
        if d.get("company_id") and met_dt:
            ctx["met_carried"][d["company_id"]] = met_dt

    # Commitments: stored + newly extracted, checked against the transcripts; old ones pruned.
    store = list(((home["snap"].get("commitments") or {}).get("items") or {}).values())
    rejected: list[dict[str, Any]] = []
    if extracted:
        res = commit_mod.validate(extracted, (bundle.get("transcripts") or []), ctx["firm_domain"])
        store = commit_mod.merge(store, res["valid"])
        rejected = res["rejected"]
    item_state = ((home["state"].get("items") or {}).get("items")) or {}
    # A promise's draft marked sent keeps the promise: it closes then, and stays closed after Home prunes the draft. A draft
    # closed by Done on one row was not sent: the other promises it carries stay open.
    sent_promise = {cid_: (item_state.get(did) or {}).get("done_at")
                    for did, d in ((((home["snap"].get("drafts") or {}).get("items")) or {})).items()
                    if isinstance(d, dict) and _was_sent(item_state.get(did))
                    for cid_ in _promise_ids(d)}
    for c in store:
        st = item_state.get(c["id"])
        if st and st.get("done_at"):
            c["status"] = "done"
            c["done_at"] = st["done_at"]
            # Sent it on the page marks the promise itself sent too: it stays a sent promise, never a plain done one.
            if (st.get("sent") or sent_promise.get(c["id"])) and st.get("closed_by") != "done":
                c["sent"] = True
        elif sent_promise.get(c["id"]) and c.get("status") != "done":
            c["status"], c["done_at"], c["sent"] = "done", sent_promise[c["id"]], True
        hint = commit_mod.looks_done(c, bundle.get("threads") or [], ctx["user_email"]) or commit_mod.done_by_calendar(c, ctx)
        if hint:
            c["looks_done"] = hint
    # What Sent it closed, by company and words: the CRM step it was is done. Home keeps it 90 days, past the promise's
    # own 30, so an old step the CRM still holds never reads as the next one.
    steps_ = {k_: v_ for k_, v_ in ((((home["snap"].get("commitments") or {}).get("sent_steps")) or {})).items()
              if isinstance(k_, str) and "|" in k_ and parse_date(v_) and 0 <= (now.date() - parse_date(v_)).days <= 90}
    for c in store:
        if c.get("sent") and c.get("what") and c.get("done_at"):
            co_s = (ctx.get("domain_to_company") or {}).get(str(c.get("owed_to_email") or "").rpartition("@")[2].lower()) or ""
            steps_[f"{co_s}|{pipeline._step_key(c.get('what'))}"] = str(c.get("done_at"))[:10]
    ctx["sent_steps"] = dict(sorted(steps_.items(), key=lambda kv: kv[1])[-200:])
    store = commit_mod.prune(store, now.date())
    commitments_due = commit_mod.due_view(store, now.date(), ctx["user_email"])
    ctx["promise_what"] = {c["id"]: c.get("what") for c in store if c.get("id")}
    # Meeting notes by calendar event: what earlier runs read (kept in Home), each promise's own meeting, then this run's
    # read. A later morning finds a meeting's notes after the run that read them; the newest 200 are kept.
    notes_ev = {str(k): v for k, v in (((home["snap"].get("commitments") or {}).get("notes")) or {}).items() if k and v}
    notes_ev.update({str(c["event_id"]): c["source_url"] for c in store if c.get("event_id") and c.get("source_url")})
    notes_ev.update({str(t.get("event_id")): t.get("url") for t in bundle.get("transcripts") or [] if t.get("event_id") and t.get("url")})
    ctx["notes_by_event"] = dict(list(notes_ev.items())[-200:])

    scope = profile["pipeline_scope"]
    pool = graph_mod.deals_for_user(ctx, scope if scope != "needs_call" else "full")
    signals = _carried_signals(ctx, home, pipeline.competing_signals(ctx))
    stale = _meeting_day_stale(ctx, pipeline.stale_deals(ctx, pool, float(config.get("dwell_scale") or 1.0), skip_contact="email" in unavailable))
    moves_24h = pipeline.moves(ctx, 1, pool)
    decisions = pipeline.decisions(ctx, signals, pool)

    # Inbound: new triage results merged with recent ones.
    inbound_rows = list(((home["snap"].get("inbound") or {}).get("items") or {}).values())
    if inbound is not None:
        th = config.get("thesis") or bundle.get("thesis") or {}
        fresh = thesis.triage(inbound, th, (bundle.get("passes") or []))
        by_id = {r["id"]: r for r in inbound_rows}
        # When each pitch's email came: a pitch's age is its own, never when Home first saw it (a wide read finds old ones).
        th_first = {str(th.get("id")): min(str(m_.get("date")) for m_ in th.get("messages") or [] if m_.get("date"))
                    for th in bundle.get("threads") or [] if any(m_.get("date") for m_ in th.get("messages") or [])}
        for r in fresh:  # a pitch read again keeps the day it was first seen, and whether you answered it
            old_r = by_id.get(r["id"]) or {}
            arrived_ = old_r.get("arrived") or th_first.get(str(r.get("thread_id")))
            if not old_r and arrived_ and parse_dt(arrived_) and (now - parse_dt(arrived_)).days > 14:
                continue  # a wide read (the Monday digest) never brings back a pitch older than the list's two weeks
            by_id[r["id"]] = {**r, "seen_at": old_r.get("seen_at") or now.isoformat(), **({"answered": old_r["answered"]} if old_r.get("answered") else {}),
                              **({"in_touch": True} if old_r.get("in_touch") else {}),
                              **({"drafted": old_r["drafted"]} if old_r.get("drafted") else {}),
                              **({"arrived": arrived_} if arrived_ else {})}
        inbound_rows = [r for r in by_id.values() if (now - (parse_dt(r.get("seen_at")) or now)).days <= 14]
    # A pitch whose reply was written once keeps that: a reply that left Home unsent after a week is never written again.
    for d_ in ((((home["snap"].get("drafts") or {}).get("items")) or {})).values():
        if isinstance(d_, dict) and d_.get("inbound_id"):
            for r_ in inbound_rows:
                if r_.get("id") == d_["inbound_id"] and not r_.get("drafted"):
                    r_["drafted"] = str(d_.get("first_made_at") or d_.get("made_at") or now.isoformat())[:10]

    # Founders waiting on a reply: their question, with nothing from the firm since. That deal is waiting on you, not
    # "no contact": they wrote. An hourly pulse reads only the newest mail, so Home keeps what a wider read found.
    read_mail = bundle.get("threads") is not None and "email" not in unavailable
    fresh_asked = pipeline.unanswered(ctx, pool, {str(r.get("thread_id")) for r in inbound_rows if r.get("thread_id")}) if read_mail else []
    asked = _carried_asked(ctx, home, fresh_asked)
    asked_deals = {q["deal_id"] for q in asked}
    for st_ in stale:
        if st_["deal_id"] in asked_deals:
            st_["reasons"] = [r for r in st_["reasons"] if r["code"] != "no_contact"]
    stale = [st_ for st_ in stale if st_["reasons"]]

    # Portfolio and LPs. KPI history carries forward: Home's series, then the bundle's, then this run's reading.
    crm = bundle.get("crm") or {}
    port_cos = [c for c in (crm.get("companies") or []) if c.get("status") == "portfolio"]
    layers = [((home["snap"].get("portfolio") or {}).get("kpis") or {}), (bundle.get("portfolio_kpis") or {}), (kpis or {})]
    kpi_map = {}
    for cid in set().union(*[set(x) for x in layers]):
        by_month = {}
        for layer in layers:
            for r in layer.get(cid, []) or []:
                if r.get("month"):
                    by_month[r["month"]] = r
        kpi_map[cid] = [by_month[k] for k in sorted(by_month)][-6:]
    flags = portfolio.portfolio_flags(port_cos, kpi_map)
    boards = portfolio.board_prep(ctx)
    stored_lps = ((home["snap"].get("lps") or {}).get("lps") or {})
    # A note to an LP's contact that you marked sent is a touch on that day, in mail or not: a chased call, once paid,
    # never reads "no touch in 110 days".
    sent_to_: dict[str, str] = {}
    for did_, d_ in ((((home["snap"].get("drafts") or {}).get("items")) or {})).items():
        on_ = str((item_state.get(did_) or {}).get("done_at") or "")[:10] if _was_sent(item_state.get(did_)) else ""
        if isinstance(d_, dict) and on_:
            for x_ in str(d_.get("to") or "").replace(";", ",").split(","):
                if norm_email(x_):
                    sent_to_[norm_email(x_)] = max(sent_to_.get(norm_email(x_), ""), on_)
    lps_in = []
    for l in (bundle.get("lps") or []):
        prev = (stored_lps.get(l.get("id")) or {}).get("last_touch")
        cur = l.get("last_touch")
        chased_ = [str(c_.get("at") or "")[:10] for c_ in (((stored_lps.get(l.get("id")) or {}).get("alert") or {}).get("chases") or [])
                   if isinstance(c_, dict) and c_.get("at")]
        sent_ = [sent_to_.get(norm_email(x_)) for x_ in l.get("contacts") or []]
        lps_in.append({**l, "last_touch": max([x for x in [prev, cur] + chased_ + sent_ if x], default=None)})
    # Money first (a capital call not yet paid), then touches. Each LP has one owner: a colleague's LP shows on the LPs tab
    # with their name, and only its owner gets the line, the push and the draft.
    lp_by_id = {l.get("id"): l for l in lps_in}
    me_lp = norm_email(ctx.get("user_email"))
    if config.get("firm_members"):  # colleagues by the config, so a run that read no people still knows who owns what
        ctx["colleagues"] = {norm_email(m.get("email")): m.get("name") for m in config["firm_members"]
                             if isinstance(m, dict) and norm_email(m.get("email")) and norm_email(m.get("email")) != me_lp}
    lp_alerts, team_lp_alerts = [], []
    one_each: dict[str, dict[str, Any]] = {}  # one line per LP: a touch that is also due rides on the call
    for a in lp.call_alerts(ctx, lps_in) + lp.alerts(ctx, lps_in):
        if a["lp_id"] in one_each:
            one_each[a["lp_id"]]["text"] += f"; {a['text'][:1].lower() + a['text'][1:]}"
            continue
        one_each[a["lp_id"]] = dict(a)
    for a in one_each.values():
        owner_email, owner_name = lp.owner_of(ctx, lp_by_id.get(a["lp_id"]) or {})
        if owner_email:
            team_lp_alerts.append({**a, "owner": owner_email, "owner_name": owner_name})
        else:
            lp_alerts.append(a)
    bundle = {**bundle, "lps": lps_in, "portfolio_kpis": kpi_map}
    # Relationship decay needs months of history; small hourly windows reuse the last weekly result.
    stored_people = home["snap"].get("people") or {}
    if mode in ("setup", "digest") or not stored_people:
        decay = network.decay(ctx)
        people_top = None
    else:
        # The stored lists keep their order, but every day count is today's: a last touch this run saw moves forward, and
        # someone you wrote to since leaves "going cold".
        seen_touch = ((ctx.get("last_touch") or {}).get((ctx.get("user_person") or {}).get("id")) or {}) if ctx.get("user_person") else {}

        def fresh_days(rows: Any, key: str) -> list[dict[str, Any]]:
            out_ = []
            for r_ in rows or []:
                if not isinstance(r_, dict):
                    continue
                r_ = dict(r_)
                s_ = seen_touch.get(r_.get(key))
                if s_ and (not r_.get("last_touch") or s_.date().isoformat() > str(r_["last_touch"])[:10]):
                    r_["last_touch"] = s_.date().isoformat()
                lt_ = parse_date(r_.get("last_touch"))
                if lt_:
                    r_["days_since"] = (now.date() - lt_).days
                out_.append(r_)
            return out_
        decay = [r_ for r_ in fresh_days(stored_people.get("decay"), "person_id") if (r_.get("days_since") or 0) > 60]
        people_top = fresh_days(stored_people.get("top"), "id") if stored_people.get("top") is not None else None

    # Prep cards for today's meetings and the next working day's (Friday reaches Monday), and at least the next 36 hours.
    today = prep.today_meetings(ctx)
    reach_ = max(now + timedelta(hours=36), prep.prep_end(now))  # on a Friday, Monday's meetings too
    upcoming = [m for m in ctx["meetings"] if m.get("external") and m.get("start") and now <= m["start"] <= reach_
                and (not ctx.get("user_person") or ctx["user_person"]["id"] in m["person_ids"])]
    empathy = {k.lower(): v for k, v in (bundle.get("empathy_maps") or {}).items()}
    prep_by_meeting = {}
    verdicts = {str(r.get("domain") or "").lower(): brief_mod.revisit_verdict(r) for r in inbound_rows
                if r.get("pass_log") and (r.get("revisit_check") or {}).get("met") in (True, False)}
    # Founder asks, merged and given their warm paths before any card names them, so the dinner's prep card and the
    # ask's own row tell the same story. A run that read no CRM people keeps the paths Home found on a wider read.
    asks = _merge_asks(home, extras.get("asks"), now, item_state) if (extras.get("asks") is not None or home["snap"].get("asks")) else None
    people_read = any(not p.get("from_home") for p in ((bundle.get("crm") or {}).get("people")) or [] if isinstance(p, dict))
    for a_ in (asks or {}).values():
        if a_.get("status") != "done" and (people_read or "paths" not in a_):
            a_["paths"] = network.ask_paths(ctx, str(a_.get("ask") or ""), a_.get("company_id")) or None
    open_asks = [a for a in (asks or {}).values() if a.get("status") != "done"] if asks is not None else \
        [a for a in (extras.get("asks") or []) if isinstance(a, dict)]
    # Drafts Home already holds, by the promise they keep: the row shows "Draft ready" instead of "Draft a note".
    all_drafts = {**((((home["snap"].get("drafts") or {}).get("items")) or {})), **{k: v for k, v in (extras.get("drafts") or {}).items()
                                                                                       if isinstance(v, dict)}}
    holder_follow: list[dict[str, Any]] = []
    for did_h, d_h in all_drafts.items():
        st_h = item_state.get(did_h) or {}
        if not (isinstance(d_h, dict) and d_h.get("kind") == "holder" and _was_sent(st_h)):
            continue
        at_h = parse_dt(st_h.get("done_at"))
        who_h = norm_email(d_h.get("to"))
        base_h = re.sub(r"^((re|fwd?|fw):\s*)+", "", str(d_h.get("subject") or ""), flags=re.I).strip().lower()
        went_h = _went_at(bundle, norm_email(ctx.get("user_email")), d_h.get("subject"), at_h, d_h.get("went_at")) if at_h else None
        read_h = False  # this run read the note's thread, so "no reply" is a fact, not a gap in the read
        if at_h and not d_h.get("replied"):
            for th in bundle.get("threads") or []:
                if re.sub(r"^((re|fwd?|fw):\s*)+", "", str(th.get("subject") or ""), flags=re.I).strip().lower() != base_h:
                    continue
                # Read only when the thread holds the note itself: a thread trimmed to a later message is no read.
                read_h = read_h or bool(went_h and any(parse_dt(m_.get("date")) and abs((parse_dt(m_.get("date")) - went_h).total_seconds()) < 60
                                                     and norm_email((m_.get("from") or {}).get("email") if isinstance(m_.get("from"), dict) else m_.get("from"))
                                                     == norm_email(ctx.get("user_email")) and len(str(m_.get("text") or "").split()) >= 8
                                                     for m_ in th.get("messages") or []))  # a note, not a two-word thank-you
                for m_ in th.get("messages") or []:
                    f_ = m_.get("from")
                    w_ = parse_dt(m_.get("date"))
                    if norm_email(f_.get("email") if isinstance(f_, dict) else f_) == who_h and w_ and went_h and w_ > went_h:
                        d_h["replied"] = {"on": w_.isoformat(), "url": th.get("url")}  # kept on the note in Home
                        break
        # The deadline-day push follows any sent note with no answer, never one this run could not check.
        if d_h.get("replied") or not at_h or not read_h or now.hour < 14:
            continue
        first_h = str(d_h.get("to_name") or "them").split(" ")[0]
        for x_ in d_h.get("decisions") or []:
            if str(x_.get("deadline") or "")[:10] == now.date().isoformat():
                holder_follow.append({"key": f"holder:{did_h}:{x_.get('deal_id')}", "line": f"{x_.get('company')}: no word from {first_h} yet, decide today",
                                      "subjects": [f"deal:{x_.get('deal_id')}"] if x_.get("deal_id") else []})
    ctx["holder_follow"] = holder_follow[:1]
    drafts_by_commitment = {cid_: did for did, d in all_drafts.items()
                            if isinstance(d, dict) and not (item_state.get(did) or {}).get("done_at") for cid_ in _promise_ids(d)}
    drafts_by_action = {a_: did for did, d in all_drafts.items() if isinstance(d, dict) and not (item_state.get(did) or {}).get("done_at")
                        for a_ in [d.get("action_id")] + list(d.get("action_ids") or []) if a_}
    drafts_by_question = {d["question_id"]: did for did, d in all_drafts.items()
                          if isinstance(d, dict) and d.get("question_id") and not (item_state.get(did) or {}).get("done_at")}
    # A pitch whose pass reply is drafted: its Inbound-stage deal says so instead of "book a first meeting or pass".
    in_by_id = {r["id"]: r for r in inbound_rows}
    # A pitch you answered stays answered: the reply's sent mark is kept on the pitch after Home prunes the draft.
    for did_, d_ in all_drafts.items():
        if isinstance(d_, dict) and d_.get("inbound_id") in in_by_id and (item_state.get(did_) or {}).get("done_at") and \
                not in_by_id[d_["inbound_id"]].get("answered"):
            in_by_id[d_["inbound_id"]]["answered"] = item_state[did_]["done_at"]
    pass_drafted = {}
    for d in all_drafts.values():
        r_ = in_by_id.get(d.get("inbound_id")) if isinstance(d, dict) else None
        if r_ and r_.get("decision") == "pass":
            cid_ = ctx["domain_to_company"].get(str(r_.get("domain") or "").lower())
            if cid_:
                pass_drafted[cid_] = d.get("made_at") or now.isoformat()
    # A draft written for an ask that the user marked sent: the ask now waits on whoever the note went to.
    member_emails = {norm_email(m_.get("email")) for m_ in ctx.get("members") or [] if norm_email(m_.get("email"))}
    sent_drafts = {}
    for did, d in all_drafts.items():
        if not isinstance(d, dict) or not (d.get("action_id") or d.get("action_ids")) or not _was_sent(item_state.get(did)):
            continue
        tos = [norm_email(x) for x in str(d.get("to") or "").replace(";", ",").split(",") if norm_email(x)]
        for aid_ in list(d.get("action_ids") or []) or [d["action_id"]]:
            kind_ = (d.get("note_kinds") or {}).get(aid_) or (d.get("note_kind") if d.get("note_kind") != "several" else None) or \
                ("team" if len(tos) > 1 else "colleague" if tos and tos[0] in member_emails else "contact")
            sent_drafts[aid_] = {"at": (item_state.get(did) or {})["done_at"], "note_kind": kind_, "to_name": d.get("to_name"), "to": tos,
                                 "draft": did, "subject": d.get("subject")}
    # An ask remembers each note that went out for it, so a sent draft pruned from Home (two weeks after Sent it)
    # never makes the ask forget who was asked, or draft its first note again.
    for a_ in (asks or {}).values():
        aid_ = a_.get("item_id")
        if not aid_:
            continue
        notes_ = {n.get("tap"): n for n in a_.get("notes") or [] if isinstance(n, dict) and n.get("tap")}
        for suf in brief_mod.ASK_NOTE_SUFFIXES:
            s_ = sent_drafts.get(f"{aid_}{suf}")
            if s_ and f"{aid_}{suf}" not in notes_:
                notes_[f"{aid_}{suf}"] = {"tap": f"{aid_}{suf}", "at": s_.get("at"), "note_kind": s_.get("note_kind"),
                                         "to_name": s_.get("to_name"), "to": s_.get("to") or [], "draft": s_.get("draft"),
                                         **({"subject": s_["subject"]} if s_.get("subject") else {})}
        for tap_, n_ in notes_.items():
            sent_drafts.setdefault(tap_, {"at": n_.get("at"), "note_kind": n_.get("note_kind"), "to_name": n_.get("to_name"),
                                          "to": n_.get("to") or [], "draft": n_.get("draft"), "subject": n_.get("subject")})
        # A nudge, once written, is written once: Home prunes an unsent draft after 30 days, and the ask remembers it.
        drafted_n = {str(t_) for d_ in all_drafts.values() if isinstance(d_, dict) for t_ in [d_.get("action_id")] + list(d_.get("action_ids") or [])
                     if t_ and str(t_).startswith(f"{aid_}_") and str(t_).endswith("_nudge")}
        if drafted_n:
            a_["nudges_drafted"] = sorted(set(a_.get("nudges_drafted") or []) | drafted_n)
        if notes_:
            a_["notes"] = sorted(notes_.values(), key=lambda n: str(n.get("at") or ""))
            # Where each note sits in the user's mail, once a read finds it: a nudge says "reply in that thread", and
            # the row links to it.
            me_ = norm_email(ctx.get("user_email"))
            for n_ in a_["notes"]:
                if n_.get("url") or not n_.get("subject"):
                    continue
                subj_n = re.sub(r"^((re|fwd?|fw):\s*)+", "", str(n_["subject"]), flags=re.I).strip().lower()
                at_n = parse_dt(n_.get("at"))
                for th in bundle.get("threads") or []:
                    th_s = re.sub(r"^((re|fwd?|fw):\s*)+", "", str(th.get("subject") or ""), flags=re.I).strip().lower()
                    if th_s == subj_n and th.get("url") and any(
                            norm_email((m_.get("from") or {}).get("email") if isinstance(m_.get("from"), dict) else m_.get("from")) == me_ and
                            (not at_n or (parse_dt(m_.get("date")) or at_n) >= at_n - timedelta(days=1)) for m_ in th.get("messages") or []):
                        n_["url"] = th["url"]
                        break
            for n_ in a_["notes"]:  # when it really went: the user's own message in that thread
                if not n_.get("went_at") and n_.get("subject") and n_.get("at"):
                    w_ = _went_at(bundle, me_, n_["subject"], parse_dt(n_["at"]))
                    if w_ and _note_in_thread(bundle, me_, n_["subject"], parse_dt(n_["at"])):
                        n_["went_at"] = w_.isoformat()
    # A reply to an ask's latest note: a message from whoever it went to, after it went, in that note's own thread. A
    # reply that names some of the note's companies answers those asks only; one that names none answers them all. An
    # email elsewhere that only names the company is not a reply (the board pack is not an answer). The ask then waits
    # on the user, not on them, and is never nudged.
    note_cos_: dict[str, set] = {}
    co_names_ = {str(a_.get("company")).strip().lower(): str(a_.get("company")).strip() for a_ in (asks or {}).values() if a_.get("company")}
    for a_ in (asks or {}).values():
        for n_ in a_.get("notes") or []:
            if isinstance(n_, dict) and n_.get("draft") and a_.get("company"):
                note_cos_.setdefault(str(n_["draft"]), set()).add(str(a_["company"]).strip().lower())
    for a_ in (asks or {}).values():
        notes_ = [n for n in a_.get("notes") or [] if isinstance(n, dict) and n.get("at")]
        if not notes_ or a_.get("made_on") or a_.get("status") == "done":
            continue
        last_ = max(notes_, key=lambda n: str(n.get("at")))
        since_ = _went_at(bundle, norm_email(ctx.get("user_email")), last_.get("subject"), parse_dt(last_.get("at")), last_.get("went_at"))
        who_ = {norm_email(x) for x in last_.get("to") or [] if norm_email(x)}
        subj_ = re.sub(r"^((re|fwd?|fw):\s*)+", "", str(last_.get("subject") or ""), flags=re.I).strip().lower()
        co_ = str(a_.get("company") or "").strip().lower()
        # The companies one note carried: the first note's, when the latest is its nudge (a nudge answers in the same thread).
        first_n = next((n for n in notes_ if not str(n.get("tap") or "").endswith("_nudge")), last_)
        cos_ = note_cos_.get(str(last_.get("draft"))) or note_cos_.get(str(first_n.get("draft"))) or ({co_} if co_ else set())
        subjs_ = {x for x in (subj_, re.sub(r"^((re|fwd?|fw):\s*)+", "", str(first_n.get("subject") or ""), flags=re.I).strip().lower()) if x}
        hit_, part_ = None, None
        # A company by its full name, or by its first word when no other ask on the note shares it ("Yes on Orbit").
        firsts_: dict[str, list[str]] = {}
        for c_ in cos_:
            if c_ and len(c_.split(" ")[0]) >= 4:
                firsts_.setdefault(c_.split(" ")[0], []).append(c_)

        def named_in(text_: str) -> set:
            got_ = {c_ for c_ in cos_ if c_ and c_ in text_}
            return got_ | {cs_[0] for f_, cs_ in firsts_.items() if len(cs_) == 1 and re.search(rf"\b{re.escape(f_)}\b", text_)}
        for th in bundle.get("threads") or []:
            th_subj = re.sub(r"^((re|fwd?|fw):\s*)+", "", str(th.get("subject") or ""), flags=re.I).strip().lower()
            if not subjs_ or th_subj not in subjs_:
                continue
            for m_ in th.get("messages") or []:
                frm_ = m_.get("from")
                frm_ = norm_email(frm_.get("email") if isinstance(frm_, dict) else frm_)
                when_ = parse_dt(m_.get("date"))
                text_ = str(m_.get("text") or "").lower()
                named_ = named_in(text_)
                if not (frm_ in who_ and when_ and since_ and when_ > since_):
                    continue
                name_ = (m_.get("from") or {}).get("name") if isinstance(m_.get("from"), dict) else None
                if (not named_ or co_ in named_) and (not hit_ or when_ > parse_dt(hit_["on"])):
                    # "Let me think about these and come back to you" answers nothing yet: kept as a reply that defers, so
                    # five quiet working days on, one nudge follows.
                    defers_ = bool(DEFER_WORDS.search(text_)) and not (named_ and co_ in named_ and YES_WORDS.search(text_))
                    hit_ = {"on": when_.isoformat(), "by": name_ or last_.get("to_name"), "tap": last_.get("tap"), "url": th.get("url"),
                            **({"defers": True} if defers_ else {})}
                elif named_ and co_ not in named_ and (not part_ or when_ > parse_dt(part_["on"])):
                    part_ = {"on": when_.isoformat(), "by": name_ or last_.get("to_name"), "url": th.get("url"), "tap": last_.get("tap"),
                             "named": sorted(co_names_.get(c_, c_) for c_ in named_)}
        if hit_:
            a_["replied"] = hit_
            a_.pop("answered_others", None)
        elif part_:
            a_["answered_others"] = part_  # "Aditi answered on Orbit Treasury and Kestrel Pay on 26 Oct, not this one"
    # A capital call you chased: the note you marked sent is the touch. The line says when and to whom, and after five
    # quiet working days that a second note is coming (the morning run writes it, once). The LP remembers each chase
    # for the life of the call: Home prunes a sent draft two weeks after Sent it, and a first note must never be
    # drafted again, nor a third.
    stored_lp_rows = ((home["snap"].get("lps") or {}).get("lps") or {})
    for a_ in lp_alerts + team_lp_alerts:
        if a_.get("kind") != "call":
            continue
        tid_ = brief_mod.item_id("lp", a_["id"])
        old_ = stored_lp_rows.get(a_["lp_id"]) or {}
        rec_ = [dict(c) for c in ((old_.get("alert") or {}).get("chases") or []) if isinstance(c, dict) and c.get("at") and c.get("tap")
                and str(c.get("call_date") or "") == str(a_.get("call_date") or "")]
        for key_, tap_ in ((a_["id"], a_["id"]), (tid_, a_["id"]), (f"{a_['id']}_2", f"{a_['id']}_2")):
            s_ = sent_drafts.get(key_)
            if s_ and s_.get("at") and not any(c.get("tap") == tap_ for c in rec_):
                rec_.append({"tap": tap_, "at": s_.get("at"), "to_name": s_.get("to_name"), "draft": s_.get("draft"),
                             "call_date": a_.get("call_date"), **({"subject": s_["subject"]} if s_.get("subject") else {})})
        rec_.sort(key=lambda c: str(c.get("at")))
        if rec_:
            a_["chases"] = rec_
        first_ = next((c for c in rec_ if c.get("tap") == a_["id"]), None)
        again_ = next((c for c in rec_ if c.get("tap") == f"{a_['id']}_2"), None)
        last_ = again_ or first_
        if not last_:
            continue
        at_ = parse_dt(last_.get("at"))
        to_ = str(last_.get("to_name") or "").split(" ")[0] or "them"
        quiet_ = pipeline.working_days_since(at_.date(), now.date()) if at_ else 0
        # A reply from the LP's contacts since the chase went: no "no reply", and no second note. Kept on the record, so a
        # later run that reads less mail still knows.
        contacts_ = {norm_email(x) for x in (lp_by_id.get(a_["lp_id"]) or {}).get("contacts") or [] if norm_email(x)}
        me_c = norm_email(ctx.get("user_email"))
        went_ = _went_at(bundle, me_c, last_.get("subject"), at_, last_.get("went_at")) if at_ else None
        if went_ and not last_.get("went_at") and _note_in_thread(bundle, me_c, last_.get("subject"), at_):
            last_["went_at"] = went_.isoformat()  # found in mail: kept with the chase
        rep_ = (old_.get("alert") or {}).get("replied") if isinstance((old_.get("alert") or {}).get("replied"), dict) else None
        rep_ = rep_ if rep_ and at_ and ((rep_.get("tap") and rep_.get("tap") == last_.get("tap")) or (parse_dt(rep_.get("on")) or at_) > at_) else None
        chase_subjs = {re.sub(r"^((re|fwd?|fw):\s*)+", "", str(c_.get("subject") or ""), flags=re.I).strip().lower()
                       for c_ in rec_ if c_.get("subject")}
        for th in bundle.get("threads") or []:
            th_subj = re.sub(r"^((re|fwd?|fw):\s*)+", "", str(th.get("subject") or ""), flags=re.I).strip().lower()
            for m_ in th.get("messages") or []:
                f_ = m_.get("from")
                when_ = parse_dt(m_.get("date"))
                # In the chase's own thread, or about the call ("the wire goes out on Wednesday"): an email about the
                # AGM is not an answer.
                about_ = (chase_subjs and th_subj in chase_subjs) or CALL_WORDS.search(f"{th_subj} {m_.get('text') or ''}")
                if norm_email(f_.get("email") if isinstance(f_, dict) else f_) in contacts_ and when_ and went_ and when_ > went_ and about_ and \
                        (not rep_ or when_ > parse_dt(rep_["on"])):
                    name_ = (f_.get("name") if isinstance(f_, dict) else None) or to_
                    said_ = _named_day(str(m_.get("text") or ""), when_)
                    paid_ = bool(PAID_SAYS.search(str(m_.get("text") or "")))
                    rep_ = {"on": when_.isoformat(), "by": str(name_).split(" ")[0] or to_, "url": th.get("url"), "tap": last_.get("tap"),
                            **({"promised": said_.isoformat()} if said_ and not paid_ else {}), **({"says_paid": True} if paid_ else {})}
        # A reply is not payment: while the call is unpaid, the follow-up comes the working day after the date they
        # named ("the wire goes out on Wednesday"), or five working days after a reply that names none.
        follow_ = False
        if rep_:
            rep_on = parse_dt(rep_["on"])
            prom_ = parse_date(rep_.get("promised")) if rep_.get("promised") else None
            # "We paid it": the bank gets a week and a half to show it before a note asks.
            due_ = pipeline.add_working_days(prom_, 1) if prom_ else pipeline.add_working_days(rep_on.date(), 8 if rep_.get("says_paid") else 5)
            follow_ = now.date() >= due_
            rep_["follow_on"] = due_.isoformat()
        a_["chased"] = {"at": last_.get("at"), "to": to_, "quiet": quiet_, "again": bool(again_),
                        **({"replied": True, "reply_on": rep_["on"], "follow": follow_} if rep_ else {}),
                        **({"promised": rep_["promised"]} if rep_ and rep_.get("promised") else {})}
        if rep_:
            a_["replied"] = rep_
        who_r = (rep_ or {}).get("by") or to_
        a_["text"] = str(a_.get("text") or "").split("; ")[0] + f"; chased {to_}{' again' if again_ else ''} on {fmt_short_date(at_)}" + \
            ((f", {who_r} said on {fmt_short_date(parse_dt(rep_['on']))} it was paid, and it has not shown: check with {who_r}" if rep_.get("says_paid") else
              f", {who_r} said it would go on {fmt_short_date(parse_date(rep_['promised']))}, still unpaid" if rep_.get("promised") else
              f", {who_r} replied on {fmt_short_date(parse_dt(rep_['on']))}, still unpaid") + (f": call {to_}" if again_ else "")
             if rep_ and follow_ else
             f", {who_r} says it was paid ({fmt_short_date(parse_dt(rep_['on']))}): check the account" if rep_ and rep_.get("says_paid") else
             f", {who_r} replied on {fmt_short_date(parse_dt(rep_['on']))}" +
             (f", saying it goes on {fmt_short_date(parse_date(rep_['promised']))}" if rep_.get("promised") else "") if rep_ else
             f", no reply in {quiet_} working days: call {to_}" if quiet_ >= 5 and again_ else  # two notes is the most: then a call
             f", no reply in {quiet_} working days" if quiet_ >= 5 else "")
    # An introduction made: after the note went out, a thread holds both the founder's company and the contact.
    for a_ in (asks or {}).values():
        sent_ = brief_mod.ask_sent(sent_drafts, a_.get("item_id"), first=True)
        p0_ = (a_.get("paths") or [None])[0] or {}
        if a_.get("made_on") or not sent_ or not norm_email(p0_.get("email")):
            continue
        since_ = parse_dt(sent_["at"])
        for th in bundle.get("threads") or []:
            people_ = {norm_email((x or {}).get("email")) for x in th.get("participants") or []}
            if norm_email(p0_["email"]) in people_ and any(pipeline.company_of(ctx, e_) == a_.get("company_id") for e_ in people_ if e_):
                when_ = max((parse_dt(m_.get("date")) for m_ in th.get("messages") or [] if parse_dt(m_.get("date"))), default=None) or \
                    parse_dt(th.get("date") or th.get("last_date"))
                if when_ and since_ and when_ >= since_:
                    a_["made_on"] = when_.date().isoformat()
                    break
    # Taps that follow an ask's sent note ("Yes, ask the team", "Yes, draft the intro ask", "Ask the team instead"), by
    # the ask's row id: the row then says the board partner agreed, or that the next note is ready.
    ask_follow: dict[str, list[dict[str, Any]]] = {}
    for k_, a_ in ((((home["state"].get("actions") or {}).get("items")) or {})).items():
        pay_ = (a_ or {}).get("payload") or {}
        if isinstance(a_, dict) and a_.get("status") == "approved" and a_.get("type") == "draft" and pay_.get("next_of") and \
                re.search(r"_(team|intro)$", str(k_)):
            ask_follow.setdefault(str(pay_["next_of"]), []).append({"id": k_, "at": a_.get("at"), "note_kind": pay_.get("note_kind"),
                                                                    "after": pay_.get("after") or {}})
    # Who each waiting note is for, in a word: "Aditi", or "the team" for a note to several colleagues.
    draft_names = {}
    for did_, d_ in all_drafts.items():
        if isinstance(d_, dict):
            tos_ = [x for x in str(d_.get("to") or "").replace(";", ",").split(",") if x.strip()]
            draft_names[did_] = "the team" if d_.get("note_kind") == "team" or len(tos_) > 1 else str(d_.get("to_name") or "").split(" ")[0]
    # The prep card says where each ask stands, as its row does: a note ready, a note out and to whom, a nudge, or the
    # introduction made.
    note_states: dict[str, Any] = {}
    view_parts = {"drafts_by_action": drafts_by_action, "sent_drafts": sent_drafts, "ask_follow": ask_follow,
                  "draft_names": draft_names, "asks": list((asks or {}).values())}
    for a_ in open_asks:
        aid_ = a_.get("item_id")
        if not aid_:
            continue
        v_ = brief_mod.ask_view(a_, view_parts, now.date())
        sent_ = brief_mod.ask_sent(sent_drafts, aid_)
        if v_["word"] == "made":
            note_states[aid_] = {"state": "made", "on": a_["made_on"]}
        elif v_.get("draft"):
            d_ = all_drafts.get(v_["draft"]) or {}
            tos_ = [x for x in str(d_.get("to") or "").replace(";", ",").split(",") if x.strip()]
            kind_ = (d_.get("note_kinds") or {}).get(aid_) or d_.get("note_kind")
            note_states[aid_] = {"state": "ready", "nudge": bool(v_.get("nudge")),
                                 "to": "the team" if kind_ == "team" or len(tos_) > 1 else (str(d_.get("to_name") or "").split(" ")[0] or None)}
        elif sent_:
            to_first_ = str(sent_.get("to_name") or "").split(" ")[0]
            said_ = {"team": "asked the team", "board": f"asked {to_first_ or 'the board partner'}", "nudge": f"nudged {to_first_ or 'them'}",
                     "colleague": f"asked {to_first_} for the intro" if to_first_ else "intro requested"}.get(sent_.get("note_kind"), "intro requested")
            note_states[aid_] = {"state": "sent", "label": said_, "on": str(sent_.get("at") or "")[:10], "quiet": v_["word"] == "nudge",
                                 "short_label": "asked the team" if sent_.get("note_kind") == "team" else
                                 f"nudged {to_first_}" if sent_.get("note_kind") == "nudge" and to_first_ else
                                 f"asked {to_first_}" if to_first_ else "intro requested"}
    asks_for_prep = [{**a_, "note_state": note_states.get(a_.get("item_id"))} for a_ in open_asks]
    for m in {mm["id"]: mm for mm in today + upcoming}.values():
        prep_by_meeting[m["id"]] = prep.card(ctx, m, store, signals, stale, empathy, flags, lp_alerts, lps_in, verdicts, asks_for_prep)
    old_prep = (home["snap"].get("prep") or {}).get("cards") or {}
    known = {}  # strength Home last computed from the full history, by name: a narrow pulse read never lowers it
    for r in (stored_people.get("top") or []) + (stored_people.get("decay") or []):
        nm = str(r.get("name") or "").lower()
        known[nm] = max(known.get(nm, 0), int(r.get("strength") or 0))
    for mid, card in prep_by_meeting.items():
        old = old_prep.get(mid) or {}
        _merge_card(card, old, known)
    # Partner syncs and ICs get a decision pack: every deal to decide across the firm, with why now.
    # A partner pack needs partners: a solo GP's own review is the pipeline itself.
    partner_mtgs = prep.partner_meetings(ctx) if not _off(profile, "pipeline") and profile.get("level") != "solo_gp" else []
    if partner_mtgs:
        # The pack is the same for everyone in the room: it reads the CRM and shared notes only, never one person's
        # own mail or calendar (Sterling AA is "no contact in 10 days" for every attendee, or for none).
        tz_ = ctx["tz"]
        crm_deals = [{**d, "last_contact_dt": parse_dt(d.get("last_contact"), tz_)} for d in ctx["deals"]]
        pack_ctx = {**ctx, "deals": crm_deals, "meetings": [], "sent_steps": {}}  # one pack for the room: nothing from one person's mail
        firm_stale = _meeting_day_stale(pack_ctx, pipeline.stale_deals(pack_ctx, None, float(config.get("dwell_scale") or 1.0),
                                                                       skip_contact="crm" in unavailable))
        firm_decisions = pipeline.decisions(pack_ctx, signals, crm_deals)
        for m in partner_mtgs:
            ctx["level"] = profile.get("level")
            pcard_ = prep.partner_card(ctx, m, firm_decisions, firm_stale, store)
            # The questions a morning wrote stay through the day's pulses, as on every other card: a Friday's
            # questions for Monday's meeting are still there on Monday.
            if (old_prep.get(m["id"]) or {}).get("questions") and not pcard_.get("questions"):
                pcard_["questions"] = old_prep[m["id"]]["questions"]
            prep_by_meeting[m["id"]] = pcard_
    if "calendar" in unavailable:  # keep the cards for meetings still ahead
        for mid, old in old_prep.items():
            if mid not in prep_by_meeting and (parse_dt(old.get("start")) or now) >= now:
                prep_by_meeting[mid] = old

    parts = {"meetings_today": today, "prep_by_meeting": prep_by_meeting, "commitments_due": commitments_due, "signals": signals,
             "asks": list((asks or {}).values()),
             "stale": stale, "moves_24h": moves_24h, "decisions": decisions, "inbound": inbound_rows, "portfolio_flags": flags,
             "boards": boards, "lp_alerts": lp_alerts, "lps_raw": (bundle.get("lps") or []), "decay": decay, "needs_review": resolved["needs_review"],
             "internal_today": prep.internal_today(ctx), "tomorrow": prep.tomorrow_meetings(ctx),
             "partner_meetings": [m for m in partner_mtgs if m["start"] >= now], "drafts_by_commitment": drafts_by_commitment,
             "unanswered": asked, "drafts_by_question": drafts_by_question, "sent_drafts": sent_drafts, "pass_drafted": pass_drafted,
             "drafts_by_action": drafts_by_action, "ask_follow": ask_follow, "draft_names": draft_names,
             "draft_gaps": {did_: draft_gaps(d_.get("body")) for did_, d_ in all_drafts.items() if isinstance(d_, dict) and draft_gaps(d_.get("body"))},
             "decision_meetings": [m for m in prep.partner_meetings(ctx) if m["start"] >= now],
             "found_at": now, "next_check": _next_check(now, config), "next_check_at": schedules.next_run(config, now).isoformat()}
    # A pitch from a founder you already write to says so in the brief and on the Pitches list: no cold reply on top.
    talking_now = _talking(ctx, inbound_rows, now)
    for r in inbound_rows:
        # Once a read saw you write to them, the pitch stays "in touch" for its life on the list (14 days): a read
        # that missed the thread never turns it back into "book a call".
        if str(r.get("domain") or "").lower() in talking_now or norm_email(r.get("from")).split("@")[-1] in talking_now:
            r["in_touch"] = True
    # What a push named earlier today stays on Today until it is done or the day ends.
    today_iso = now.date().isoformat()
    # Deals a sync already covered today stay off a colleague's Today for the rest of the day.
    prev_brief = home["snap"].get("brief") or {}
    covered = set(prev_brief.get("covered_today") or []) if prev_brief.get("covered_date") == today_iso else set()
    for c in list(old_prep.values()) + list(prep_by_meeting.values()):
        if c.get("kind") == "partner" and str(c.get("start") or "")[:10] == today_iso and (parse_dt(c.get("start")) or now) <= now:
            covered |= {r.get("deal_id") for r in c.get("decisions") or [] if r.get("kind") != "stalled" and r.get("deal_id")}
    parts["covered_today"] = sorted(covered)
    parts["pinned_ids"] = list(dict.fromkeys(
        r["push_item"] for r in home.get("runs") or [] if isinstance(r, dict) and r.get("push_item") and
        (r.get("pushed") or r.get("shown_in_chat")) and str(r.get("started") or "")[:10] == today_iso and
        not (item_state.get(r["push_item"]) or {}).get("done_at")))
    state = home["state"].get("items") or {}
    the_brief = brief_mod.build(ctx, profile, config, parts, state, mode)
    for pid in parts["pinned_ids"]:
        brief_mod.show_pushed(the_brief, pid)
    if "calendar" in unavailable and not the_brief["meetings"]:
        old_brief = home["snap"].get("brief") or {}
        the_brief["meetings"] = [m for m in (old_brief.get("meetings") or []) if str(m.get("start") or "")[:10] == now.date().isoformat()]

    # Safety: drop anything without a source.
    dropped = []
    for sec in the_brief["sections"]:
        keep = [it for it in sec["items"] if (it.get("source") or {}).get("url")]
        dropped.extend(it for it in sec["items"] if not (it.get("source") or {}).get("url"))
        sec["items"] = keep
    the_brief["sections"] = [s for s in the_brief["sections"] if s["items"]]
    if dropped:
        warnings.append(f"Dropped {len(dropped)} line(s) with no source link.")
    # Connectors this run could not use: said plainly in Home and in the run report.
    old_unavail = {u["source"]: u for u in ((home["snap"].get("brief") or {}).get("unavailable") or [])}
    the_brief["unavailable"] = [{"source": k, "status": v, "label": CATEGORY_LABEL.get(k, k),
                                 "since": (old_unavail.get(k) or {}).get("since") or now.isoformat()} for k, v in unavailable.items()]
    for k, v in unavailable.items():
        warnings.append(f"{CATEGORY_LABEL.get(k, k)} {STATUS_TEXT.get(v, v)}. Home keeps what it last knew.")
    # Quiet deals stay in the user's own Home: the copyable brief and the push line leave them out.
    quiet = _quiet_set(ctx)
    shareable = json.loads(json.dumps(the_brief, default=str))
    for sec in shareable["sections"]:
        sec["items"] = [it for it in sec["items"] if not _touches_quiet(it, quiet)]
    shareable["sections"] = [s for s in shareable["sections"] if s["items"]]
    shareable["meetings"] = [m for m in shareable.get("meetings") or [] if not _touches_quiet(m, quiet)]
    if _touches_quiet(shareable.get("hero"), quiet):
        shareable["hero"] = {"kind": "quiet", "kicker": "Private", "statement": "A quiet deal needs you. Open ant. Home."}
    the_brief["text"] = brief_mod.render_text(the_brief)
    the_brief["shareable_text"] = brief_mod.render_text(shareable, links=False)

    # A pitch you met or have booked says so on the Pitches list, so it never reads "book a call" after the call.
    by_domain: dict[str, tuple[str, Any]] = {}
    for m in ctx["meetings"]:
        st = m.get("start")
        if not st or not m.get("external") or not (now - timedelta(days=14) <= st <= now + timedelta(days=14)):
            continue
        for pid in m.get("external_ids") or []:
            dom = str((ctx["lookup"].get(pid) or {}).get("company_domain") or "").lower()
            if dom:
                kind_ = "booked_on" if st >= now else "met_on"
                if kind_ == "booked_on" or dom not in by_domain or by_domain[dom][0] != "booked_on":
                    by_domain[dom] = (kind_, st)
    # Only a run that read the calendar wide can say a meeting is not there: an hourly pulse reads today and the next
    # working day, so it keeps what a wider read found ("you met them on 20 Oct"), and the line never flips by the hour.
    wide_cal = mode in ("setup", "daily", "review", "week_ahead", "digest")
    for r in inbound_rows:
        if wide_cal:
            r.pop("met_on", None)
            r.pop("booked_on", None)
        hit = by_domain.get(str(r.get("domain") or "").lower())
        if hit:
            r[hit[0]] = hit[1].isoformat()
        if r.get("met_on") or r.get("booked_on"):
            r.pop("in_touch", None)  # met or booked says more than "in touch"
    snaps = _snapshots(ctx, config, profile, the_brief, prep_by_meeting, store, signals, stale, decisions, inbound_rows, flags, boards,
                       lp_alerts, decay, resolved, home, port_cos, kpi_map, bundle, people_top, applied or {}, mode,
                       unavailable, asks, extras.get("digest"), extras.get("proposals"), extras.get("drafts"), warnings, team_lp_alerts,
                       asked=asked, ask_parts=parts)
    # The day's count includes the meetings still to log, and apart from them the steps still to add after a log:
    # a meeting you logged is never counted as one to log. The text forms of the brief say the same count as Home.
    mp_ = (snaps.get("pipeline") or {}).get("met_prompts") or []
    n_log, n_step = sum(1 for p_ in mp_ if not p_.get("step_only")), sum(1 for p_ in mp_ if p_.get("step_only"))
    extra_ = " and ".join(x for x in (f"{plural(n_log, 'meeting')} to log" if n_log else "",
                                      f"{plural(n_step, 'next step')} to add" if n_step else "") if x)
    if extra_ and the_brief.get("headline"):
        h_ = str(the_brief["headline"])
        the_brief["headline"] = extra_ if h_ == "nothing needs you" else f"{h_}, {extra_}"
        the_brief["text"] = brief_mod.render_text(the_brief)
        shareable["headline"] = the_brief["headline"]
        the_brief["shareable_text"] = brief_mod.render_text(shareable, links=False)
    pa = pending_actions(home, ctx["now"])
    if pa["refused"]:
        # Said once: each refused tap becomes a "Not done" row in Home with the reason, and later runs skip it.
        props_doc = snaps.setdefault("proposals", {"as_of": now.isoformat(), "items": {}})
        props_doc.setdefault("items", {})
        acts = ((home["state"].get("actions") or {}).get("items") or {})
        for r in pa["refused"]:
            name, title = _tap_label(acts.get(r["id"]) or {}, ctx)
            props_doc["items"][r["id"]] = {"type": r.get("type"), "status": "refused", "title": title,
                                           "record": {"name": name} if name else None,
                                           "reason": r["why"], "applied_at": now.isoformat(), "source_label": "ant. Home", "source_url": None}
        warnings.append(f"Refused {len(pa['refused'])} approval(s): " + "; ".join(f"{r['id']} ({r['why']})" for r in pa["refused"][:5]) + ".")
    if pa["check_by_hand"]:
        warnings.append("A stopped run may have applied " + ", ".join(r["id"] for r in pa["check_by_hand"][:5]) + ". Check the record.")
    digest = extras.get("digest") or {}
    if digest.get("markdown") and digest.get("kind") in ("preread", "review"):
        named = sorted(n for n in quiet["names"] if n and n in str(digest["markdown"]).lower())
        if named:
            warnings.append("The " + DIGEST_TITLE.get(digest["kind"], "digest").lower() + " names a quiet deal (" + ", ".join(named) +
                            "). Take it out before anyone else reads it.")
    started = parse_dt((extras.get("run") or {}).get("started")) or now  # bands are measured from when the run began
    eve = _board_eve(ctx, boards, store, started)
    # A board-eve line still to come this evening keeps its place in the day's four pushes.
    eve_later = _board_eve(ctx, boards, store, started.replace(hour=17, minute=0)) if started.hour < 17 else []
    push = _push(the_brief, home, started, mode, unavailable, old_unavail, quiet, prep_by_meeting, snaps, extras.get("packs"), eve,
                 schedules.next_run(config, started), ctx, eve_later, schedules.day_runs(config, started))
    push["subjects"] = _named_subjects(push.get("line"), push.get("subjects") or [], ctx)
    if push.get("send") and brief_mod.show_pushed(the_brief, push.get("item")):
        shareable_now = json.loads(json.dumps(the_brief, default=str))
        for sec in shareable_now["sections"]:
            sec["items"] = [it for it in sec["items"] if not _touches_quiet(it, quiet)]
        shareable_now["sections"] = [s_ for s_ in shareable_now["sections"] if s_["items"]]
        shareable_now["meetings"] = [m for m in shareable_now.get("meetings") or [] if not _touches_quiet(m, quiet)]
        if _touches_quiet(shareable_now.get("hero"), quiet):
            shareable_now["hero"] = shareable["hero"]
        the_brief["shareable_text"] = brief_mod.render_text(shareable_now, links=False)
    # A hero that a push named today opens Home on Today, whatever tab the person starts on: they tapped through to it.
    pushed_today = set(parts.get("pinned_ids") or []) | ({push.get("item")} if push.get("send") and push.get("item") else set())
    if (the_brief.get("hero") or {}).get("item_id") in pushed_today - {None}:
        the_brief["hero"]["pushed"] = True
    elif push.get("send") and push.get("item"):
        # The push named a row, not the hero: Home opens on Today with that row open, so the tap lands on what it said.
        if any(it.get("id") == push["item"] for sec in the_brief.get("sections") or [] for it in sec.get("items") or []):
            the_brief["pushed_item"] = push["item"]
    report = {
        "as_of": now.isoformat(), "mode": mode, "level": level, "hero": the_brief["hero"], "items": _things(the_brief),
        "words": the_brief["words"], "signals": len(signals), "stale": len(stale), "decisions": len(decisions),
        "commitments_open": sum(1 for c in store if c.get("status") == "open"),
        "commitments_rejected": rejected, "inbound": len(inbound_rows), "portfolio_flags": len(flags), "lp_alerts": len(lp_alerts),
        "flags": [{"company": f["company"], "headline": f["headline"], "detail": f["detail"], "priority": f["priority"],
                   "source_url": f.get("source_url")} for f in flags[:10]],
        "decay": len(decay), "needs_review": len(resolved["needs_review"]), "dropped_without_source": len(dropped),
        "warnings": warnings, "unavailable": unavailable, "push": push, "push_line": push["line"],
        "next_brief": schedules.next_brief(config, now),
        "new_breaches": _new_breaches(the_brief, home),
        # Emails the user owes, for the morning brief to draft into Gmail before the brief time. Never sent.
        # (Another run gets only the nudges whose asks moved on since they were written: pulse step 5 rewrites those.)
        "owed": [o_ for o_ in _owed(commitments_due, inbound_rows, all_drafts, item_state, profile, now, ctx, _drafting(home, now), asked,
                      _letter_inputs(snaps, ctx), (snaps.get("asks") or {}).get("items") or asks,
                      [{**a, "contacts": (lp_by_id.get(a["lp_id"]) or {}).get("contacts") or [], "fund": (lp_by_id.get(a["lp_id"]) or {}).get("fund")}
                       for a in lp_alerts if a.get("kind") == "call" and (a.get("days_since") or 0) >= 14],
                      {k_ for k_, a_ in ((((home["state"].get("actions") or {}).get("items")) or {})).items()
                       if isinstance(a_, dict) and a_.get("status") == "approved" and a_.get("type") == "draft" and
                       (now - (parse_dt(a_.get("at")) or now)).days <= TAP_DAYS}, signals)
                 if mode in ("daily", "setup") or o_.get("kind") == "narrow" or (o_.get("kind") == "holder" and o_.get("rebuild"))],
    }
    run = extras.get("run") or {}
    report["run_row"] = {"started": run.get("started") or now.isoformat(), "finished": now.isoformat(), "mode": mode,
                         "jobs": run.get("jobs") or BY_HAND_JOBS.get(mode, [mode]), "items": _things(the_brief), "words": the_brief["words"],
                         "warnings": warnings[:10], "unavailable": unavailable, "push_line": push["line"], "push_key": push["key"],
                         "push_keys": push.get("keys") or [], "push_item": push.get("item"), "push_subjects": push.get("subjects") or [],
                         "deferred": push.get("deferred"), "deferred_more": push.get("deferred_more") or [],
                         # Setup speaks in chat: its line is shown there, never pushed, yet a later run must not repeat it.
                         "pushed": bool(push["send"]) and not extras.get("by_hand") and mode != "setup",
                         "shown_in_chat": bool(push["send"]) and mode == "setup",
                         "read": read_now,
                         "next_check_at": parts["next_check_at"]}
    return {"brief": the_brief, "snaps": snaps, "report": report, "ctx": ctx, "parts": parts}


def _tap_label(act: dict[str, Any], ctx: dict[str, Any]) -> tuple[str | None, str]:
    """(name, what) for a tap's row in Home: "Atlas Settlement" and "Stage to Passed", never a bare type or a name
    said twice."""
    pay = act.get("payload") or {}
    kind = act.get("type")
    rec = pay.get("record") or {}
    ent = pay.get("entity") or {}
    rid = rec.get("id") or pay.get("deal_id") or ent.get("id")
    name = rec.get("name") or ent.get("name") or pay.get("company")
    if not name and rid:
        deal = next((d for d in ctx.get("deals") or [] if d.get("id") == rid), None)
        name = (deal or {}).get("company_name") or ((ctx.get("companies") or {}).get(rid) or {}).get("name")
    if kind == "crm_update" and isinstance(pay.get("fields"), list) and pay["fields"]:
        change = ", ".join(f"{str(f.get('field') or '').replace('_', ' ')} to {f.get('proposed')}" for f in pay["fields"] if isinstance(f, dict))
        return name, change[:1].upper() + change[1:]
    if kind == "next_step":
        step_ = str(pay.get("text") or pay.get("next_step") or "").strip().rstrip(".")
        if step_:
            return name, "Next step: " + step_ + (f", stage to {pay['stage']}" if pay.get("stage") else "")
        met_ = parse_date(str(pay.get("met") or "")[:10])
        # A met log with no step names what it did: "Met 22 Oct, stage to Second meeting".
        return name, (f"Met {fmt_short_date(met_)}" if met_ else "Logged") + (f", stage to {pay['stage']}" if pay.get("stage") else "")
    if kind == "calendar_hold":
        return name, "Calendar hold"
    title = str(pay.get("title") or ("Draft a note" if kind == "draft" else "A tap ant. did not apply"))
    if name and title.lower().startswith(str(name).lower()):
        rest = title[len(str(name)):].strip(" :")
        title = ("Draft a note: " if kind == "draft" else "") + (rest[:1].lower() + rest[1:] if rest else "note")
    return name, title[:1].upper() + title[1:]


def _named_subjects(line: Any, subjects: list[str], ctx: dict[str, Any]) -> list[str]:
    """A push records only what its line names: a deal or a company stays a subject only when the line says its name
    ("Sable, Rivulet and Trellis" names Sable Fraud AI). Promises, meetings and LPs stay: the line is about them."""
    names: dict[str, str] = {f"deal:{d['id']}": str(d.get("company_name") or "") for d in ctx.get("deals") or [] if d.get("id")}
    names.update({f"company:{cid}": str(c.get("name") or "") for cid, c in (ctx.get("companies") or {}).items()})
    low = str(line or "").lower()
    out = []
    for s_ in subjects:
        n = names.get(s_)
        first_ = n.split(" ")[0].lower() if n else ""
        if n is None or not n or n.lower() in low or (len(first_) >= 4 and re.search(rf"\b{re.escape(first_)}\b", low)):
            out.append(s_)
    return out


def _subjects(it: dict[str, Any] | None) -> list[str]:
    """What a push is about: the deal, company, promise, LP or meeting it names. Repeats are judged on these."""
    if not it:
        return []
    ent = it.get("entity") or {}
    out = []
    if it.get("deal_id"):
        out.append(f"deal:{it['deal_id']}")
    if ent.get("company_id"):
        out.append(f"company:{ent['company_id']}")
    if ent.get("type") == "deal" and ent.get("id"):
        out.append(f"deal:{ent['id']}")
    if ent.get("type") == "company" and ent.get("id"):
        out.append(f"company:{ent['id']}")
    if ent.get("type") == "lp" and ent.get("id"):
        out.append(f"lp:{ent['id']}")
    if it.get("commitment_id"):
        out.append(f"commitment:{it['commitment_id']}")
    if ent.get("type") == "meeting" and ent.get("id"):
        out.append(f"meeting:{ent['id']}")
    if ent.get("type") == "ask" and ent.get("id"):
        out.append(f"ask:{ent['id']}")
    if it.get("note_group"):  # asks that went out in one note: a push naming one names that note's nudge
        out.append(f"note:{it['note_group']}")
    if ent.get("type") == "note":
        out += [f"company:{c}" for c in ent.get("company_ids") or [] if c] + [f"ask:{x}" for x in ent.get("ask_ids") or [] if x]
    if it.get("kind") == "portfolio" and ent.get("company_id"):
        out.append(f"flag:{ent['company_id']}")
    if it.get("kind") in ("inbound", "pass_returned") and ent.get("company_id"):
        out.append(f"pass:{ent['company_id']}")
    return list(dict.fromkeys(out))


def _promise_line(it: dict[str, Any], repeat: bool = False, lead: str = "") -> str | None:
    """A promise as a push: the action, who it is for and when, never cut at the name. "Still open" when it was
    pushed before, with how late it is now. `lead` opens the line ("Week ahead: ")."""
    if it.get("kind") != "commitment" or not it.get("to_name"):
        return None
    what = str(it.get("statement") or it.get("title") or "").rstrip(".")
    who = str(it["to_name"]).split(" ")[0]
    if re.search(rf"\b{re.escape(who)}\b", what) and it.get("to_company"):
        who = it["to_company"]  # "Answer Helen's question": the line names her company, not Helen twice
        who_full = who
    elif it.get("to_company"):
        who_full = f"{who} ({it['to_company']})"
    else:
        who_full = who
    late = it.get("days_late")
    due = parse_date(it.get("due"))
    when = f"{plural(late, 'day')} late" if late else ("due today" if it.get("status_word") == "due_today" else
                                                       f"due {fmt_short_date(due)}" if due else "no date set")
    # A draft with blanks says what is left ("3 lines to fill"), never just "Draft ready".
    tail = (f". {plural(it['draft_gaps'], 'line')} to fill" if it.get("draft_gaps") else ". Draft ready") if it.get("draft") else ""
    head = lead + ("Still open: " if repeat else "")
    riv = it.get("rival") if isinstance(it.get("rival"), str) else ""
    riv = f". {riv[:1].upper()}{riv[1:]}" if riv else ""  # why it leads: "Term sheet from Bluepeak Partners"
    for who_txt, t in ((who_full, tail + riv), (who, tail + riv), (who_full, tail), (who, tail), (who, "")):
        line = f"{head}{what}: {who_txt}, {when}{t}"
        if len(line) <= 89:
            return line
    room = 89 - len(f"{head}: {who}, {when}")
    return f"{head}{clip(what, max(20, room))}: {who}, {when}"


DAILY_PUSHES = 4


def _push(brief: dict[str, Any], home: dict[str, Any], now, mode: str, unavailable: dict[str, str],
          old_unavail: dict[str, Any], quiet: dict[str, set[str]], prep_by_meeting: dict[str, Any],
          snaps: dict[str, Any] | None = None, packs: list[dict[str, Any]] | None = None,
          eve: list[dict[str, Any]] | None = None, next_at=None, ctx: dict[str, Any] | None = None,
          eve_later: list[dict[str, Any]] | None = None, day_runs: list[Any] | None = None) -> dict[str, Any]:
    """What reaches the phone, one line per run.
    - Nothing lands inside a meeting or in the 15 minutes before one: a line that can wait goes at the next free run.
    - Every meeting with a prep card gets one heads-up, from the last free run that starts at least 45 minutes before
      it. When every such run falls inside another meeting, the heads-up folds into an earlier free run; failing that,
      the first free run still 10 minutes ahead sends it. Nothing displaces it: on a run that also owes the morning
      line, the Thursday review or the week ahead, the heads-up goes out and that line follows next run. Meetings due
      in one run share one line that names each. A heads-up adds a fact the morning line lacked.
    - At most four pushes a day. The morning line, heads-ups, the board-eve line and a reconnect always go; a review,
      week ahead, follow-up or new breach goes only while the day has room, counting the heads-ups still due today.
    - The morning line leads with your own work: a deadline today, then a late promise no push named in 72 hours, then
      anything due today, then the most urgent item not named lately; when everything was named lately, the top item
      as "Still open", with how late it is now. Two of your own promises due today share one line. Whatever it names
      is put on Today.
    - The week ahead sums up the week: meetings, the decisions with their dates, and promises already late.
    - Other runs push only something new: prep, a board meeting tomorrow with a promise still open (evenings), a
      breach no earlier run had seen, a displaced scheduled line, a post-meeting pack, a connector to reconnect.
    - Lines keep the person or company and the date; the action is what gets shortened. Nothing is pushed twice in a
      week."""
    today = now.date().isoformat()
    runs = home.get("runs") or []
    recent = [r for r in runs if (parse_dt(r.get("started")) or now) >= now - timedelta(days=7)]
    pushed: set[str] = set()
    for r in recent:
        if r.get("pushed", True) or r.get("shown_in_chat"):
            pushed.update(k for k in [r.get("push_key"), *(r.get("push_keys") or [])] if k)
    named_72h: set[str] = set()
    named_7d: set[str] = set()
    named_6d: set[str] = set()  # by calendar day: pushed today or on the five days before
    for r in runs:
        when = parse_dt(r.get("started")) or now
        if not (r.get("pushed") or r.get("shown_in_chat")):
            continue
        subj = set(r.get("push_subjects") or []) | ({f"item:{r['push_item']}"} if r.get("push_item") else set())
        if when >= now - timedelta(hours=72):
            named_72h |= subj
        if when >= now - timedelta(days=7):
            named_7d |= subj
        if when.astimezone(now.tzinfo).date() >= now.date() - timedelta(days=5):
            named_6d |= subj

    def item_line(title: str, detail: str | None, room: int = 89) -> str:
        """The title and the detail's first sentence when they fit in `room`; a parenthesis and a "Next: " go before
        the date the detail ends on ("Screening memo, was due 23 Oct"); else the title alone."""
        first = str(detail or "").split(". ")[0].rstrip(".")
        bare = re.sub(r"\s*\([^()]{1,40}\)", "", title)
        for cand in (f"{title}. {first}", f"{bare}. {first}", f"{bare}. {re.sub(r'^Next: ', '', first)}"):
            if first and len(cand) <= room:
                return cand
        return title

    def line_for(h: dict[str, Any], repeat: bool = False) -> str:
        if _touches_quiet(h, quiet):
            return "A quiet deal needs you. Open ant. Home."
        if h.get("kind") == "meeting":
            who = str(h.get("kicker", "")).split(" · ")[-1].split(", ")[-1]
            time = str(h.get("kicker", "")).split(" · ")[1] if " · " in str(h.get("kicker", "")) else ""
            fact = str(h.get("statement") or "").strip()  # names keep their capitals
            short_who = who.split(": ")[0]  # "Founder community: November dinner" reads as "Founder community"
            fact = re.sub(rf"\s+at {re.escape(short_who)}(?=[.,]|$)", "", fact)  # the line already names the company
            first = fact.split(". ")[0].rstrip(".")

            def tight(t: str) -> str:
                for a, b in (("Revisit condition met: ", "Met our bar: "), ("You owe them: ", "You owe: ")):
                    t = t.replace(a, b)
                return t
            # The whole fact, then shorter words, then the first sentence alone, then its first whole clauses: anything
            # reads better than a cut one.
            for f_ in (fact, tight(fact), first, tight(first), re.sub(r", due \d{1,2} [A-Z][a-z]{2}$", "", tight(first))):
                for w_ in (who, short_who):
                    line = f"{time} {w_}: {f_}".strip()
                    if len(line) <= 89:
                        return line
            head_ = f"{time} {short_who}: ".lstrip()
            toks = re.split(r"((?<=[a-z]):\s|,\s|;\s|\s(?=\())", tight(first))  # clause, separator, clause, ...
            for k in range((len(toks) + 1) // 2 - 1, 0, -1):
                cand = head_ + "".join(toks[:2 * k - 1])
                if len(cand) <= 89:
                    return cand
            return f"{time} {short_who}".strip()
        promise = _promise_line(h, repeat)
        if promise:
            return promise
        prefix = "Still open: " if repeat else ""
        for pl_ in [h.get("push_line")] + list(h.get("push_lines") or []):
            if pl_ and len(prefix + str(pl_)) <= 89:
                return prefix + str(pl_)  # a row that names several things says them its own way, the longest that fits
        if h.get("short") and (h.get("entity") or {}).get("name"):
            # The whole short line, else its first sentence, else its first whole clauses: never a cut name.
            head_, sh = f"{prefix}{h['entity']['name']}: ", str(h["short"])
            first_ = sh.split(". ")[0]
            cuts = [sh, first_] + [first_[:m_.start()] for m_ in reversed(list(re.finditer(r"[,;:] ", first_)))]
            for cand in cuts:
                if cand and len(head_ + cand) <= 89:
                    return head_ + cand
        return prefix + item_line(str(h.get("statement") or "Nothing new"), h.get("finding"), 89 - len(prefix))

    def out(text: str, key: str | None, subjects: list[str] | None = None, **more: Any) -> dict[str, Any]:
        return {"line": fit_line(brief_mod.clean(text), 89), "key": key, "send": key is not None, "subjects": subjects or [], **more}

    def subjects_of_card(card: dict[str, Any]) -> list[str]:
        subj = [f"meeting:{card.get('meeting_id')}"] + [f"company:{c}" for c in card.get("company_ids") or []]
        if (card.get("deal") or {}).get("id"):
            subj.append(f"deal:{card['deal']['id']}")
        if card.get("kind") == "partner" and card.get("decisions"):
            subj.append(f"deal:{card['decisions'][0]['deal_id']}")
        return subj

    # Time-bound first, whatever kind of run this is. A meeting gets its heads-up from the last run that still lands
    # 45 minutes ahead: the next run would be too late. The first run of the day also covers meetings sooner than that.
    next_run = next_at or now + timedelta(hours=1)
    meetings_all = [m for m in ((ctx or {}).get("meetings") or []) if m.get("start") and not m.get("all_day")]

    def busy_at(t) -> bool:
        """A meeting is under way at t, or starts within 15 minutes of it."""
        for m in meetings_all:
            st, en = m["start"], m.get("end") or m["start"] + timedelta(minutes=30)
            if st - timedelta(minutes=15) <= t < en:
                return True
        return False

    # Today's scheduled runs, past and future, so every run of the day plans the heads-ups the same way.
    slots = sorted(day_runs or []) or [now] + [next_run + timedelta(hours=k) for k in range(0, 12)]
    near = min(slots, key=lambda t: abs((t - now).total_seconds()))
    this_slot = near if abs((near - now).total_seconds()) <= 30 * 60 else now

    def own_run(start):
        """A meeting's own heads-up run: the last free run 45 minutes to 8 hours ahead, else the first free run
        still 10 minutes ahead."""
        free = [t for t in slots if timedelta(minutes=45) <= start - t <= timedelta(hours=8) and not busy_at(t)]
        if free:
            return free[-1]
        soon = [t for t in slots if timedelta(minutes=10) <= start - t < timedelta(minutes=45) and not busy_at(t)]
        return soon[0] if soon else None

    prep_sent = sum(1 for r in runs if str(r.get("started") or "")[:10] == today and r.get("pushed") and
                    str(r.get("push_key") or "").startswith("prep:"))

    def heads_up_plan() -> dict[str, Any]:
        """{meeting id: run} for the heads-ups still to send today, in at most as many runs as the day's four pushes
        leave after the morning line, the board-eve line and the heads-ups already sent. With more, the two closest
        runs merge into the earlier one, so a later heads-up folds into an earlier push. A meeting whose run went by
        (it was booked late, or that run was missed) moves to the next free run still 10 minutes ahead."""
        own = {}
        for card in prep_by_meeting.values():
            st = parse_dt(card.get("start"))
            if not st or st <= now or f"prep:{card['meeting_id']}" in pushed:
                continue
            r = own_run(st)
            if r is not None and r < this_slot - timedelta(seconds=90):
                r = next((t for t in [this_slot] + [x for x in slots if x > this_slot]
                          if st - t >= timedelta(minutes=10) and not busy_at(t)), None)
            if r is not None and r.date() == now.date():
                own[card["meeting_id"]] = r
        reserved = (1 if now.weekday() < 5 else 0) + (1 if (eve or eve_later) else 0)
        groups = [[r] for r in sorted(set(own.values()))]
        while len(groups) > max(1, DAILY_PUSHES - reserved - prep_sent):
            i = min(range(len(groups) - 1), key=lambda k: (groups[k + 1][0] - groups[k][0], k))
            groups[i] += groups.pop(i + 1)
        to = {r: g[0] for g in groups for r in g}
        return {mid: to[r] for mid, r in own.items()}

    plan_ = heads_up_plan()

    def push_run_for(start, mid=None):
        return plan_.get(mid) if mid in plan_ else own_run(start)

    def is_now(t) -> bool:
        return t is not None and abs((t - this_slot).total_seconds()) < 90
    named_today: set[str] = set()  # what a push named since this time yesterday: the board-eve line counts for the morning after
    for r in runs:
        if (r.get("pushed") or r.get("shown_in_chat")) and (parse_dt(r.get("started")) or now) >= now - timedelta(hours=24):
            named_today |= set(r.get("push_subjects") or [])
    prep_due = []
    for card in prep_by_meeting.values():
        start = parse_dt(card.get("start"))
        if not start or f"prep:{card['meeting_id']}" in pushed:
            continue
        if start <= now or not is_now(push_run_for(start, card["meeting_id"])):
            continue
        # What you owe the people you are about to meet leads, even when this morning's push named it: walking in
        # without it costs the most. Otherwise the heads-up adds news: the card's first fact no push named today.
        fact = card.get("finding") or "First meeting. Prep is ready"
        facts_ = card.get("facts") or []
        owe = next((f for f in facts_ if f.get("kind") == "owe"), None)
        # News first; with no news, the meeting's purpose (the deal's step) before when you last met.
        fresh = next((f for f in facts_ if f.get("key") not in named_today and f is not owe and
                      not str(f.get("key")).startswith("history:")), None) or \
            next((f for f in facts_ if f is not owe and str(f.get("key")).startswith("deal:")), None) or \
            next((f for f in facts_ if f.get("key") not in named_today and f is not owe), None)
        if owe:
            fact = owe["text"]
            if fresh:  # and the room's news after it, when both fit on the line
                both = join_sentences(fact, fresh["text"])
                if len(f"{card.get('time')} {card.get('who')}: {both}") <= 89 or \
                        len(f"{card.get('time')} {str(card.get('who') or '').split(', ')[-1]}: {both}") <= 89:
                    fact = both
        elif fresh:
            fact = fresh["text"]
            short_who_ = str(card.get("who") or "").split(", ")[-1].split(": ")[0]
            if fresh.get("short") and len(f"{card.get('time')} {short_who_}: {fact}") > 89:
                fact = fresh["short"]  # "Divya needs two banks as customers: Aditi knows Raj Malhotra"
        yours = [y for y in card.get("yours") or [] if y not in str(fact)]
        level_ = ((((snaps or {}).get("config")) or ((home.get("snap") or {}).get("config")) or {}).get("level"))
        if card.get("kind") == "partner" and yours and level_ not in ("partner", "solo_gp"):  # a partner leads the room's list
            # A sync heads-up names the user's own deals in the room's list: "11 to decide, yours: Kite Pay and Lumen Ledger".
            n_dec = sum(1 for r in card.get("decisions") or [] if r.get("kind") != "stalled")
            short_ = [y.split(" ")[0] for y in yours]  # "Sable, Rivulet and Trellis" when the full names do not fit
            done_ = False
            for names_ in (yours, short_):
                for k in range(len(names_), 0, -1):
                    named = names_[0] if k == 1 else ", ".join(names_[:k - 1]) + f" and {names_[k - 1]}"
                    more = f" and {len(names_) - k} more" if k < len(names_) else ""
                    cand = f"{n_dec} to decide, yours: {named}{more}"
                    if len(f"{card.get('time')} {card.get('who')}: {cand}") <= 89 and (k == len(names_) or names_ is short_):
                        fact, done_ = cand, True
                        break
                if done_:
                    break
        prep_due.append((start, card, line_for({"kind": "meeting", "kicker": f"Next · {card.get('time')} · {card.get('who')}",
                                                "statement": fact, "entity": card})))
    prep_due.sort(key=lambda x: x[0])

    def prep_push() -> tuple[str, str, list[str], list[str]] | None:
        """(line, key, extra keys, subjects) for the prep push due now. Meetings that share this run's band share
        one line: the first with its fact, the others by time and name, so none goes without a heads-up."""
        if not prep_due:
            return None
        _, card, text = prep_due[0]
        keys, subj = [], subjects_of_card(card)
        if len(prep_due) > 1:
            later = [f"{c.get('time')} {str(c.get('who') or '').split(', ')[-1]}" for _, c, _ in prep_due[1:]]
            tail = " · then " + ", ".join(later)
            first = text.split(": ", 1)
            # The first meeting's fact whole, or its first sentence, or its first clause; never a cut one.
            fact = first[1] if len(first) > 1 else ""
            options = [fact, fact.split(". ")[0], re.split(r"[,;] ", fact.split(". ")[0])[0], ""]
            text = next((f"{first[0]}: {f_.rstrip('.')}{tail}" if f_ else f"{first[0]}{tail}" for f_ in options
                         if len(f"{first[0]}: {f_.rstrip('.')}{tail}" if f_ else f"{first[0]}{tail}") <= 89), f"{first[0]}{tail}")
            for _, c, _ in prep_due[1:]:
                keys.append(f"prep:{c['meeting_id']}")
                subj += subjects_of_card(c)
        return text, f"prep:{card['meeting_id']}", keys, subj

    def review_held(day: str) -> bool:
        """Home holds that day's pipeline review, so a push that says "Review ready" leads to it."""
        rv_ = (((home.get("snap") or {}).get("digests") or {}).get("items") or {}).get("review") or {}
        return bool(rv_.get("markdown")) and str(rv_.get("as_of") or "")[:10] >= str(day)[:10]

    def pending_deferred() -> list[dict[str, Any]]:
        out_: list[dict[str, Any]] = []
        seen_: set[str] = set()
        for r in sorted(runs, key=lambda r: str(r.get("started") or ""), reverse=True):
            for d in [r.get("deferred") or {}] + [x for x in r.get("deferred_more") or [] if isinstance(x, dict)]:
                if not d.get("key") or not d.get("line") or d["key"] in seen_ or d["key"] in pushed:
                    continue
                seen_.add(d["key"])
                kind_, _, day = str(d["key"]).partition(":")
                started_ = parse_dt(r.get("started")) or now
                # A held line waits for a free run with room the same day; tomorrow it is old news, and Home has it.
                # The pipeline review is the exception: held all Thursday, it goes on the next working day, after the
                # morning line.
                nxt_ = started_.date() + timedelta(days=1)
                while nxt_.weekday() >= 5:
                    nxt_ += timedelta(days=1)
                if (kind_ == "daily" and day == today) or (kind_ in ("review", "week_ahead", "pack", "item") and started_.date() == now.date()):
                    out_.append(d)
                elif kind_ == "review" and nxt_ == now.date() and review_held(day):
                    out_.append({**d, "carried": True})
        return out_

    def busy() -> bool:
        return busy_at(now)

    sent_today = sum(1 for r in runs if str(r.get("started") or "")[:10] == today and (r.get("pushed") or r.get("shown_in_chat"))
                     and r.get("push_key"))  # setup's line in chat counts: the user heard from ant.

    def reserved_later() -> int:
        """Pushes still owed today: heads-ups at later runs, and the board-eve line."""
        later: set = set()
        for card in prep_by_meeting.values():
            st = parse_dt(card.get("start"))
            if not st or f"prep:{card['meeting_id']}" in pushed:
                continue
            r = push_run_for(st, card["meeting_id"])
            if r is not None and not is_now(r) and r > this_slot and r.date() == now.date():
                later.add(r.replace(second=0, microsecond=0))
        eve_n = 1 if any(f"board:{e['meeting_id']}" not in pushed for e in eve_later or []) else 0
        return len(later) + eve_n

    def room() -> bool:
        return sent_today + 1 + reserved_later() <= DAILY_PUSHES

    def eve_push() -> tuple[str, str, list[str], list[str]] | None:
        for e in eve or []:
            if f"board:{e['meeting_id']}" not in pushed:
                return e["line"], f"board:{e['meeting_id']}", [], [f"company:{e.get('company_id')}"] + \
                    [f"commitment:{cid}" for cid in e.get("commitment_ids") or []]
        return None

    def week_line() -> str | None:
        """ "Week ahead: 14 meetings, decide Gravity Payouts by 31 Oct and Atlas by 05 Nov, 2 promises late". """
        end = now + timedelta(days=7)
        n_meet = sum(1 for m in meetings_all if now <= m["start"] <= end)
        dec = []
        for it in order:
            dl = parse_date(it.get("due"))
            if it.get("kind") in ("signal", "decision") and dl and now.date() <= dl <= end.date() and not _touches_quiet(it, quiet):
                name = str((it.get("entity") or {}).get("name") or str(it.get("title") or "").split(":")[0])
                if name and name not in [d_[0] for d_ in dec]:
                    dec.append((name, dl))
        late = sum(1 for it in order if it.get("kind") in ("commitment", "question") and
                   (it.get("days_late") or it.get("status_word") == "overdue") and not _touches_quiet(it, quiet))
        parts_ = [plural(n_meet, "meeting") if n_meet else "no meetings booked"]
        if dec:
            parts_.append("decide " + " and ".join(f"{n} by {fmt_short_date(d_)}" for n, d_ in dec[:2]))
        if late:
            parts_.append(plural(late, "promise") + " late")
        owed = next((it for it in order if it.get("kind") == "lp" and str(it.get("short") or "").startswith("owes ")), None)
        if owed and len(parts_) < 3:  # money an LP still owes on a call: the week's money fact for finance
            parts_.append(f"{(owed.get('entity') or {}).get('name') or 'an LP'} {owed['short']}")
        for k in range(len(parts_), 1, -1):
            text = "Week ahead: " + ", ".join(parts_[:k])
            if len(text) <= 89:
                return text
        return None

    hero = brief.get("hero") or {}
    order = []
    if hero.get("item_id") and hero.get("kind") != "meeting":
        order.append({**hero, "id": hero["item_id"], "statement": hero.get("statement"), "finding": hero.get("finding")})
    for sec in brief.get("sections") or []:
        for it in sec["items"]:
            order.append({**it, "statement": it.get("title"), "finding": it.get("detail")})

    def work_day(it: dict[str, Any]) -> str:
        """The day a promise is worked on: due at a weekend means due by Friday."""
        d = parse_date(it.get("due"))
        if d and it.get("kind") == "commitment" and d.weekday() >= 5:
            d = d - timedelta(days=d.weekday() - 4)
        return d.isoformat() if d else str(it.get("due") or "")[:10]

    def fresh_pick() -> tuple[dict[str, Any] | None, bool]:
        """Your own work first, in Today's order (a promise or a deadline; not what others owe you): what is due today,
        then what is late that no push named in 72 hours. Then anything due today, shown on Today or not; then the most
        urgent item no push named in 72 hours; else the top item, as a repeat."""
        pool = order + [{**x, "statement": x.get("title"), "finding": x.get("detail")} for x in brief.get("due_today") or []]

        def waits(it: dict[str, Any]) -> bool:
            """An ask whose note is out, or whose introduction was made, waits on someone else: no push names it."""
            return it.get("kind") == "ask" and it.get("ask_state") in ("requested", "made", "replied")

        def ok(it: dict[str, Any]) -> bool:
            return it.get("kind") != "meeting" and not _touches_quiet(it, quiet) and it.get("status_word") != "looks_done" and \
                not it.get("fyi") and not it.get("decide_first") and not (it.get("after") and (parse_dt(it["after"]) or now) > now) and \
                not waits(it)
        # A promise to a founder three or more days late while another fund is moving costs the most to miss: it beats
        # anything due today except a deadline on a deal that is also contested.
        # Not on two of three mornings: one a push named in the last two days gives way to the next.
        named_day: set[str] = set()
        for r_ in runs:
            if (r_.get("pushed") or r_.get("shown_in_chat")) and (parse_dt(r_.get("started")) or now) >= now - timedelta(hours=50):
                named_day |= set(r_.get("push_subjects") or []) | ({f"item:{r_['push_item']}"} if r_.get("push_item") else set())
        rival = next((it for it in pool if it.get("kind") == "commitment" and it.get("rival") and ok(it) and
                      not ((set(_subjects(it)) | {f"item:{it.get('id')}"}) & named_day)), None)
        for it in pool:  # a deadline day always wins, even when an earlier push named it
            if it.get("kind") != "waiting" and work_day(it) == today and ok(it):
                if rival and not it.get("rival") and not it.get("contested") and it.get("kind") not in ("signal", "decision"):
                    return rival, False
                return it, False
        if rival:
            return rival, False
        # Money owed to the fund that leads Today reaches the phone at least once a week: a week of late promises
        # winning every morning never hides an unpaid capital call. Mid-week, so Monday stays your own work's.
        # The call need not lead Today: a solo GP's call under a busy hero is money owed all the same.
        if now.weekday() >= 2:
            money_ = next((it for it in pool if it.get("kind") == "lp" and it.get("call") and ok(it) and
                           not ((set(_subjects(it)) | {f"item:{it.get('id')}"}) & named_6d)), None)
            if money_:
                return money_, False
        for it in pool:  # your own late work: a promise, or a founder waiting on your reply
            late = it.get("status_word") == "overdue" or bool(it.get("days_late"))
            if it.get("kind") in ("commitment", "question") and late and ok(it) and \
                    not ((set(_subjects(it)) | {f"item:{it.get('id')}"}) & named_72h):
                return it, False
        for it in pool:
            if str(it.get("due") or "")[:10] == today and ok(it):
                return it, False
        for it in order:
            subj = set(_subjects(it)) | {f"item:{it.get('id')}"}
            if not (subj & named_72h) and not waits(it):
                # A race Home has shown for two days or more is not news: it goes out as "Still open".
                old_race = it.get("kind") == "signal" and parse_dt(it.get("since")) and (now - parse_dt(it["since"])).days >= 2
                return it, bool(subj & named_7d) or bool(old_race)
        rest_ = [it for it in order if not waits(it)]
        # Everything was named lately: the repeat is the top line no push named yesterday, so the same "Still open" line
        # never lands two mornings running.
        named_30h: set[str] = set()
        for r_ in runs:
            if (r_.get("pushed") or r_.get("shown_in_chat")) and (parse_dt(r_.get("started")) or now) >= now - timedelta(hours=30):
                named_30h |= set(r_.get("push_subjects") or []) | ({f"item:{r_['push_item']}"} if r_.get("push_item") else set())
        not_yday = [it for it in rest_ if not ((set(_subjects(it)) | {f"item:{it.get('id')}"}) & named_30h)]
        return ((not_yday or rest_)[0], True) if rest_ else (None, False)

    if mode in ("daily", "setup"):
        pick, repeat = fresh_pick()
        head = str(brief.get("headline") or "nothing needs you")
        line = line_for(pick, repeat) if pick else f"{head[:1].upper()}{head[1:]}"
        second = None
        # Two of your own promises due today: one line names both, so neither is news at noon.
        if pick and pick.get("kind") == "commitment" and work_day(pick) == today and not repeat:
            second = next((it for it in order if it is not pick and it.get("id") != pick.get("id") and it.get("kind") == "commitment"
                           and work_day(it) == today and it.get("status_word") != "looks_done" and not _touches_quiet(it, quiet)), None)
            if second:
                def what_(it: dict[str, Any]) -> str:
                    return brief_mod._lower_first(str(it.get("statement") or it.get("title") or "").rstrip("."))
                for both in (f"Due today: {what_(pick)} ({str(pick.get('to_name') or '').split(' ')[0]}) and {what_(second)} "
                             f"({str(second.get('to_name') or '').split(' ')[0]})", f"Due today: {what_(pick)} and {what_(second)}"):
                    if len(both) <= 89 and "()" not in both:
                        line = both
                        break
        subj = _subjects(pick)
        if pick and line.startswith("Due today: ") and second:
            subj += [x for x in _subjects(second) if x not in subj]  # the line names both promises
        morning = {"line": fit_line(brief_mod.clean(line), 89), "key": f"daily:{today}", "item": (pick or {}).get("id"), "subjects": subj}
        # A follow-up the morning run wrote from last night's notes goes out on the next run: one line a run.
        more = [{"line": fit_line(brief_mod.clean(str(p_["line"])), 89), "key": f"pack:{p_['meeting_id']}", "subjects": []}
                for p_ in (packs or []) if isinstance(p_, dict) and p_.get("meeting_id") and p_.get("line") and
                not _touches_quiet(p_, quiet) and f"pack:{p_['meeting_id']}" not in pushed][:2]
        extra_ = {"deferred_more": more} if more else {}
        timed = prep_push() or eve_push()
        if timed:  # a heads-up goes first; the morning line follows on the next run
            text, key, keys, psubj = timed
            return out(text, key, psubj, keys=keys, deferred=morning, **extra_)
        if busy():  # never as a meeting starts: the morning line goes at the next free run
            return {"line": "Nothing new", "key": None, "send": False, "subjects": [], "deferred": morning, **extra_}
        # Yesterday evening's week ahead or review, pushed back by a board-eve line, goes first; the morning line next.
        late = next((d for d in pending_deferred() if not str(d["key"]).startswith("daily:") and not d.get("carried")), None)
        if late:
            return out(late["line"], late["key"], late.get("subjects") or [], item=late.get("item"), deferred=morning, **extra_)
        return out(line, f"{mode}:{today}", subj, item=(pick or {}).get("id"), **extra_)
    def review_line() -> tuple[str, list[str]]:
        """The pipeline review's line from today's figures: a review carried to the next day says "day 5 of 10", not
        the day before's count."""
        ph = ((snaps or {}).get("pipeline") or {}).get("hero") or {}
        deals_needing = ph.get("count")
        if _touches_quiet(ph, quiet):
            return "Review ready: a quiet deal needs a call", []
        if ph.get("deal_id") and f"deal:{ph['deal_id']}" in named_72h:
            # Already pushed this week: the review names the next deal that was not, or the same one with the count.
            fresh = next((it for it in order if it.get("deal_id") and it.get("kind") in ("decision", "signal", "stale") and
                          f"deal:{it['deal_id']}" not in named_72h and not _touches_quiet(it, quiet)), None)
            if fresh and fresh.get("kind") == "signal" and "passed" in str(fresh.get("short") or ""):
                # A race whose date has gone is said as passed, never as a fund still moving.
                return "Review ready: " + str(fresh.get("statement")).split(". ")[0] + ", their deadline passed", [f"deal:{fresh['deal_id']}"]
            if fresh:
                return "Review ready: " + item_line(str(fresh.get("statement")), fresh.get("finding"), 89 - len("Review ready: ")), \
                    [f"deal:{fresh['deal_id']}"]
            name = str(ph.get("statement") or "").split(":")[0]
            more = (deals_needing or 1) - 1
            return f"Review ready: {name}" + (f" and {plural(more, 'more deal')} need you this week" if more else " needs you this week"), []
        # A race whose date has gone is said as passed, never as a fund still moving.
        passed_ = next((it for it in order if it.get("kind") == "signal" and ph.get("deal_id") and it.get("deal_id") == ph.get("deal_id") and
                        "passed" in str(it.get("short") or "")), None)
        return ("Review ready: " + str(ph.get("statement")).split(". ")[0] + (", their deadline passed" if passed_ else ""),
                [f"deal:{ph['deal_id']}"] if ph.get("deal_id") else [])

    if mode in ("week_ahead", "review"):
        pick, subj = None, []
        if mode == "week_ahead":
            pick, _ = fresh_pick()
            summary = week_line()
            line = summary or _promise_line(pick or {}, lead="Week ahead: ") or "Week ahead: " + line_for(pick or hero)
            # A push records only what its line names: "3 promises late" names none of them, so Monday can still push one.
            subj = [] if summary else _subjects(pick or hero)
            if summary:
                pick = None
        else:
            line, subj = review_line()
        timed = prep_push() or eve_push()
        scheduled = {"line": fit_line(brief_mod.clean(line), 89), "key": f"{mode}:{today}", "item": (pick or {}).get("id"), "subjects": subj}
        if timed:  # a meeting soon, or a board tomorrow with a promise open, goes first; this line follows next run
            text, key, keys, psubj = timed
            return out(text, key, psubj, keys=keys, deferred=scheduled)
        if busy():  # it waits for the next free run
            return {"line": "Nothing new", "key": None, "send": False, "subjects": [], "deferred": scheduled}
        if not room():  # the day's pushes are spoken for: the review waits in Home
            return {"line": "Nothing new", "key": None, "send": False, "subjects": []}
        return out(line, f"{mode}:{today}", subj, item=(pick or {}).get("id"))
    candidates: list[tuple[str, str, list[str], list[str]]] = []  # (key, text, extra keys, subjects)
    for timed in (prep_push(), eve_push()):
        if timed:
            text, key, keys, psubj = timed
            candidates.append((key, text, keys, psubj))
    old = home["snap"].get("brief") or {}
    seen = set(old.get("ranked_ids") or []) | {it["id"] for sec in old.get("sections", []) for it in sec.get("items", [])}
    if (old.get("hero") or {}).get("item_id"):
        seen.add(old["hero"]["item_id"])
    for it in order:
        # A new breach is news; a race from an email two days old or more is not, even when a wide read (the Monday
        # digest) brings it back after a narrow one dropped it.
        old_race = it.get("kind") == "signal" and ((parse_dt(it.get("since")) and (now - parse_dt(it["since"])).days >= 2) or
                                                   "passed" in str(it.get("short") or ""))
        if it.get("breach") and it["id"] not in seen and not old_race:
            candidates.append((f"item:{it['id']}", line_for(it), [], _subjects(it)))
    for hf_ in (ctx or {}).get("holder_follow") or []:
        candidates.append((hf_["key"], hf_["line"], [], hf_.get("subjects") or []))
    # A morning, review or week-ahead line that a heads-up displaced goes out now: the morning line the same day, the
    # review or week ahead within a day (a Sunday board-eve moves the week ahead to Monday's first run).
    deferred_item: dict[str, Any] = {}
    for d in pending_deferred():
        if d.get("carried"):  # yesterday's review, said with today's figures
            line_, subj_ = review_line()
            candidates.append((d["key"], line_, [], subj_))
        else:
            candidates.append((d["key"], d["line"], [], d.get("subjects") or []))
        deferred_item[d["key"]] = d.get("item")
    for pack in (packs or []):
        if isinstance(pack, dict) and pack.get("meeting_id") and pack.get("line") and not _touches_quiet(pack, quiet):
            candidates.append((f"pack:{pack['meeting_id']}", str(pack["line"]), [], []))
    # A connector the user must fix pushes once; one that is only busy says so in Home and catches up on its own.
    for k, v in unavailable.items():
        if v in ("revoked", "missing"):
            text = (f"{CATEGORY_LABEL.get(k, k)} access was revoked: reconnect it in Claude. Home shows what it last knew" if v == "revoked"
                    else f"{CATEGORY_LABEL.get(k, k)} is not connected: Home shows what it last knew")
            candidates.append((f"conn:{k}:{v}", text, [], []))
    held = None
    for key, text, keys, subj in candidates:
        if key in pushed:
            continue
        # Four a day: a review, week ahead, follow-up or new breach goes only while the day has room for the
        # heads-ups and board-eve line still due. The morning line, heads-ups, board eve and a reconnect always go.
        if key.startswith(("review:", "week_ahead:", "pack:", "item:", "holder:")) and not room():
            continue
        # A line that can wait never lands in a meeting or as one starts: it waits for the next free run.
        if busy() and key.startswith(("daily:", "review:", "week_ahead:", "pack:", "item:", "board:", "conn:", "holder:")):
            if held is None:
                held = {"line": text, "key": key, "item": deferred_item.get(key), "subjects": subj}
            continue
        return out(text, key, subj, keys=keys, item=deferred_item.get(key), **({"deferred": held} if held else {}))
    return {"line": "Nothing new", "key": None, "send": False, "subjects": [], **({"deferred": held} if held else {})}


def _board_eve(ctx: dict[str, Any], boards: list[dict[str, Any]], store: list[dict[str, Any]], now) -> list[dict[str, Any]]:
    """From 17:00, a board meeting tomorrow with a promise to that company still open: one push the evening before."""
    if now.hour < 17:
        return []
    tomorrow = (now + timedelta(days=1)).date()
    me = norm_email(ctx["user_email"])
    out = []
    for b in boards:
        start = parse_dt(b.get("start"))
        if not start or start.date() != tomorrow:
            continue
        owed = []
        for c in store:
            if c.get("status") != "open" or c.get("looks_done") or norm_email(c.get("owed_by_email")) != me:
                continue
            to = ctx["lookup"].get(norm_email(c.get("owed_to_email"))) if c.get("owed_to_email") else None
            if (to or {}).get("company_id") == b["company_id"]:
                owed.append(c)
        if not owed:
            continue
        owed.sort(key=lambda c: c.get("due") or "9999")
        what = str(owed[0]["what"]).rstrip(".")
        due = parse_date(owed[0].get("due"))
        line = f"{b['company']} board tomorrow {fmt_time(start, ctx['tz'])}. You promised to {what[:1].lower() + what[1:]}"
        line += (f" by {fmt_short_date(due)}" if due else "") + (f", plus {plural(len(owed) - 1, 'more promise')}" if len(owed) > 1 else "")
        out.append({"meeting_id": b["meeting_id"], "company_id": b["company_id"], "line": line,
                    "commitment_ids": [c["id"] for c in owed]})
    return out


def _met_soon(ctx: dict[str, Any]) -> set[str]:
    """Companies the user met in the last twelve hours or meets in the next 36: contact is not their problem."""
    now = ctx["now"]
    out: set[str] = set()
    for m in ctx["meetings"]:
        if m.get("external") and m.get("start") and now - timedelta(hours=12) <= m["start"] <= now + timedelta(hours=36):
            for pid in m.get("external_ids") or []:
                cid = (ctx["lookup"].get(pid) or {}).get("company_id")
                if cid:
                    out.add(cid)
    return out


def _meeting_day_stale(ctx: dict[str, Any], stale: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """A deal is never stale while a meeting with the company is booked in the next seven days or happened in the
    last five working days (a Thursday call still counts on Monday): the meeting is the next step, or just was.
    Otherwise "no contact" drops on the day you meet them."""
    met = _met_soon(ctx)
    near = _meeting_window(ctx, 0, 7) | set(pipeline.met_recently(ctx))
    # A contact the CRM logged in the last five working days counts like a meeting in every Home: a colleague's
    # "met" log clears the deal for the whole team, not only for whoever was in the room.
    now_ = ctx["now"]
    for d in ctx["deals"]:
        lc = parse_date(str(d.get("last_contact") or "")[:10])
        if d.get("company_id") and lc and lc <= now_.date() and pipeline.working_days_since(lc, now_.date()) <= 5:
            near.add(d["company_id"])
    comp = {d["id"]: d.get("company_id") for d in ctx["deals"]}
    out = []
    for st in stale:
        cid = comp.get(st["deal_id"])
        if cid in near:
            continue
        if cid in met:
            reasons = [r for r in st["reasons"] if r["code"] != "no_contact"]
            if not reasons:
                continue
            st = {**st, "reasons": reasons}
        out.append(st)
    return out


def _meeting_window(ctx: dict[str, Any], back_days: int, ahead_days: int) -> set[str]:
    """Companies with an external meeting from back_days ago to ahead_days ahead."""
    now = ctx["now"]
    out: set[str] = set()
    for m in ctx["meetings"]:
        if m.get("external") and m.get("start") and now - timedelta(days=back_days) <= m["start"] <= now + timedelta(days=ahead_days):
            for pid in m.get("external_ids") or []:
                cid = (ctx["lookup"].get(pid) or {}).get("company_id")
                if cid:
                    out.add(cid)
    return out


EMAILABLE = re.compile(r"^\s*(send|share|intro|introduce|forward|reply|respond|answer|follow up|follow-up|confirm|email|write to|get back|invite|"
                       r"circle back|loop in|connect|set up a call|schedule|book|propose|put [\w\s]{1,40} in touch)\b", re.I)


def _drafting(home: dict[str, Any], now) -> set[str]:
    """Owed emails a run started drafting in the last two days (it marks each on its run row before the Gmail call).
    One a stopped run left unrecorded is never drafted again: Gmail may already hold it."""
    out: set[str] = set()
    for r in home.get("runs") or []:
        if (parse_dt(r.get("started")) or now) >= now - timedelta(days=2):
            out.update((r.get("drafting") or {}).keys())
    return out


def _owed(commitments_due: dict[str, Any], inbound_rows: list[dict[str, Any]], drafts: dict[str, Any], item_state: dict[str, Any],
          profile: dict[str, Any], now, ctx: dict[str, Any] | None = None, drafting: set[str] | None = None,
          asked: list[dict[str, Any]] | None = None, letter_inputs: dict[str, Any] | None = None,
          asks: dict[str, Any] | None = None, lp_calls: list[dict[str, Any]] | None = None,
          taps: set[str] | None = None, races: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Emails the user owes, for Claude to draft into Gmail drafts before the brief time. Promises due within two days
    or overdue that are an email by nature come first. Levels that triage every pitch also get a reply to each new
    pitch: returning companies that met their bar first, then calls, asks for more and kind passes. Never one already
    drafted, never a promise that looks done, never a flagged pitch, never a founder you already talk to, and one
    email per person: a reply to someone you also owe a promise joins that draft."""
    have_c = {cid_ for did_, d in drafts.items() if isinstance(d, dict) and not (item_state.get(did_) or {}).get("done_at")
              for cid_ in _promise_ids(d)}
    have_i = {d.get("inbound_id") for d in drafts.values() if isinstance(d, dict)}
    have_to = {norm_email(d.get("to")) for d in drafts.values() if isinstance(d, dict) and d.get("to")}
    # Drafts still waiting for this person: a new email to them joins the one in Home instead of making a second.
    open_to: dict[str, tuple[str, dict[str, Any]]] = {}
    for did, d in drafts.items():
        if isinstance(d, dict) and d.get("to") and not (item_state.get(did) or {}).get("done_at"):
            made = parse_dt(d.get("made_at"))
            if not made or now - made <= timedelta(days=3):
                for addr in [d["to"]] + [x for x in str(d.get("cc") or "").replace(";", ",").split(",") if x.strip()]:
                    open_to.setdefault(norm_email(addr), (did, d))  # an intro's second person counts as addressed too
    later_sync = any(prep.is_partner_meeting(m) and m.get("start") and now <= m["start"] <= now + timedelta(days=4)
                     for m in (ctx or {}).get("meetings") or [])
    out: list[dict[str, Any]] = []
    drafting = drafting or set()
    letters: list[dict[str, Any]] = []
    for c in commitments_due.get("mine") or []:
        if c.get("looks_done") or c["id"] in have_c or (item_state.get(c["id"]) or {}).get("done_at") or f"dr_{c['id']}" in drafting:
            continue
        if brief_mod.LETTER.search(str(c.get("what") or "")):
            # The quarterly letter is work ant. finishes: drafted from the KPIs and the LP list, gaps marked.
            q_ = re.search(r"\bQ([1-4])\b", str(c.get("what") or ""))
            qn = int(q_.group(1)) if q_ else ((now.month - 1) // 3 or 4)  # the quarter just ended, unless the promise names one
            qy = now.year - (1 if not q_ and now.month <= 3 else 0)
            letters.append({"id": f"dr_{c['id']}", "kind": "letter", "commitment_id": c["id"], "to": norm_email(c.get("owed_to_email")) or None,
                            "quarter": f"Q{qn} {qy}",
                            "to_name": c.get("owed_to"), "what": c["what"], "due": c.get("due"), "overdue": bool(c.get("overdue")),
                            "inputs": letter_inputs or {}, "context": "Drafted from the KPI history and the LP list: add your commentary",
                            "source_label": "Meeting notes", "source_url": c.get("source_url")})
            continue
        if not c.get("owed_to_email") or not EMAILABLE.search(str(c.get("what") or "")):
            continue
        if OUTCOME.search(str(c.get("what") or "")) and (later_sync or profile.get("level") == "solo_gp"):
            continue  # an outcome cannot be shared before the meeting (or a solo GP's own call) that decides it
        to = norm_email(c["owed_to_email"])
        joined = open_to.get(to)
        if joined and joined[1].get("in_gmail"):
            joined = None  # a draft already in Gmail is never edited: this one stays its own email
        made = parse_date(c.get("meeting_date"))
        # "Set up a call with Kabir": the colleague's calendar and drafts are theirs, so the email copies them in and asks
        # the founder for times, rather than offering hours that may already be offered to someone else.
        with_ = [m_ for m_ in (ctx or {}).get("members") or [] if norm_email(m_.get("email")) and
                 norm_email(m_.get("email")) != norm_email((ctx or {}).get("user_email")) and
                 str(m_.get("name") or "").split(" ")[0] and
                 re.search(rf"\b{re.escape(str(m_.get('name') or '').split(' ')[0])}\b", str(c.get("what") or ""))] \
            if commit_mod.is_scheduling(str(c.get("what") or "")) else []
        # An introduction goes to both people: the second one, named in the promise, is copied in.
        intro_cc = None
        if re.match(r"^(intro|introduce|connect)\b", str(c.get("what") or ""), re.I):
            hit = next((p_ for p_ in (ctx or {}).get("people") or [] if p_.get("name") and len(str(p_["name"]).split()) > 1 and
                        re.search(rf"\b{re.escape(str(p_['name']))}\b", str(c.get("what") or "")) and
                        to not in [norm_email(e_) for e_ in p_.get("emails") or []] and (p_.get("emails") or [])), None)
            intro_cc = norm_email((hit.get("emails") or [None])[0]) if hit else None
        # The recipient's company names the email in their words ("Rivulet Payments: our feedback").
        cid_to = (((ctx or {}).get("lookup") or {}).get(to) or {}).get("company_id")
        to_co = (((ctx or {}).get("companies") or {}).get(cid_to or "") or {}).get("name")
        # The firm's view is the sponsoring partner's to give: feedback from a meeting with no notes names who holds it.
        holder = brief_mod.view_holder(ctx or {}, c.get("what"), cid_to)
        out.append({"id": joined[0] if joined else f"dr_{c['id']}", "kind": "promise", "commitment_id": c["id"], "to": to,
                    **({"company": to_co} if to_co and not c.get("internal") else {}),
                    **({"with": [{"name": m_.get("name"), "email": norm_email(m_.get("email"))} for m_ in with_],
                        "cc": ", ".join(norm_email(m_.get("email")) for m_ in with_)} if with_ else {}),
                    **({"cc": intro_cc} if intro_cc and not with_ else {}),
                    **({"holder": holder} if holder else {}),
                    **({"join": {"subject": joined[1].get("subject"), "body": joined[1].get("body")}} if joined else {}),
                    "to_name": c.get("owed_to"), "what": c["what"], "due": c.get("due"), "overdue": bool(c.get("overdue")),
                    "internal": bool(c.get("internal")), "made_on": c.get("meeting_date"), "quote": c.get("quote"),
                    # What they owe you, late or due: the email asks for it in one line. Never in an email that copies
                    # someone else (an introduction): what the founder owes you is not for the banker to read.
                    **({"they_owe": owes_} if not (intro_cc or with_) and
                       (owes_ := [{"commitment_id": t_.get("id"), "what": t_.get("what"), "due": t_.get("due"), "overdue": bool(t_.get("overdue"))}
                                  for t_ in (commitments_due.get("theirs") or [])
                                  if norm_email(t_.get("owed_by_email")) == to][:2]) else {}),
                    "context": "You promised this" + (f" on {fmt_short_date(made)}" if made else "") +
                               (f", due {fmt_short_date(parse_date(c.get('due')))}" if c.get("due") else ""),
                    "source_label": "Meeting notes", "source_url": c.get("source_url")})
    out = out[:5] + letters[:1]
    # Money an LP still owes on a capital call, two weeks on: the person who owns the LP gets the chase note drafted.
    if (profile.get("modules") or {}).get("lp") == "full":
        drafted_ = {a_ for d in drafts.values() if isinstance(d, dict) for a_ in [d.get("action_id")] + list(d.get("action_ids") or []) if a_}
        for a_ in (lp_calls or [])[:2]:
            tid = brief_mod.item_id("lp", a_["id"])
            to_ = next((norm_email(c_) for c_ in a_.get("contacts") or [] if norm_email(c_)), None)
            chased_ = a_.get("chased") or {}
            # A second, shorter note once the first went five working days with no reply; never a third, and never once
            # they answered.
            again = bool(chased_) and not chased_.get("again") and \
                ((chased_.get("quiet", 0) >= 5 and not chased_.get("replied")) or bool(chased_.get("follow")))
            aid2 = f"{a_['id']}_2"
            if not to_ or (item_state.get(tid) or {}).get("done_at"):
                continue
            if chased_.get("again") or (chased_ and not again):
                continue  # two notes went out: never a third; one went out: the second waits for five quiet working days
            if again:
                if aid2 in drafted_ or f"dr_{aid2}" in drafting:
                    continue
            elif a_["id"] in drafted_ or tid in drafted_ or f"dr_{a_['id']}" in drafting:
                continue
            who_ = (((ctx or {}).get("lookup") or {}).get(to_) or {}).get("name")
            out.append({"id": f"dr_{aid2}" if again else f"dr_{a_['id']}", "kind": "lp_call", "action_id": aid2 if again else a_["id"],
                        "action_ids": [aid2] if again else [a_["id"], tid], "lp": a_.get("name"), "lp_id": a_.get("lp_id"), "chase_tap": a_["id"],
                        "fund": a_.get("fund"), "to": to_, "to_name": who_ or a_.get("name"), "outstanding_usd": a_.get("outstanding_usd"),
                        "call_date": a_.get("call_date"), "days_since": a_.get("days_since"),
                        **({"again": True, "chased_on": str(chased_.get("at") or "")[:10]} if again else {}),
                        **({"replied_on": str(chased_.get("reply_on") or "")[:10]} if again and chased_.get("replied") else {}),
                        **({"promised": chased_["promised"]} if again and chased_.get("promised") else {}),
                        "context": (("They said the money would go on " + fmt_short_date(parse_date(chased_["promised"])) + " and it has not come: a short follow-up"
                                     if chased_.get("promised") else
                                     f"They replied on {fmt_short_date(parse_date(str(chased_.get('reply_on'))[:10]))} and the money has not come: a short follow-up")
                                    if again and chased_.get("replied") else
                                    f"No reply since you wrote on {fmt_short_date(parse_date(str(chased_.get('at'))[:10]))}: a second, shorter note"
                                    if again else f"{a_.get('name')} still owes {money(a_.get('outstanding_usd'))} on the capital call" +
                                    (f" of {fmt_short_date(parse_date(a_['call_date']))}" if a_.get("call_date") else "")),
                        "source_label": "LP list", "source_url": a_.get("source_url")})
    # A founder's ask is finished without a tap at the level that owns asks: a note to the warm path, or to the team.
    if (profile.get("modules") or {}).get("portfolio") == "asks" or profile.get("level") == "solo_gp":
        by_action = {a_ for d in drafts.values() if isinstance(d, dict) for a_ in [d.get("action_id")] + list(d.get("action_ids") or []) if a_}
        n_ask = 0
        for a_ in sorted((asks or {}).values(), key=lambda x: str(x.get("date") or ""), reverse=True):
            aid = a_.get("item_id")
            if a_.get("status") == "done" or not aid or aid in by_action or a_.get("notes") or f"dr_{aid}" in drafting or n_ask >= 3 or \
                    (item_state.get(aid) or {}).get("done_at") or (parse_date(a_.get("date")) and (now.date() - parse_date(a_.get("date"))).days > 21):
                continue
            p0 = (a_.get("paths") or [None])[0]
            solo = profile.get("level") == "solo_gp"
            me_a = norm_email((ctx or {}).get("user_email"))
            team = [m_ for m_ in (ctx or {}).get("members") or [] if norm_email(m_.get("email")) and norm_email(m_.get("email")) != me_a]
            warn_to = a_.get("warning_to") or {}
            if a_.get("warning") and not solo and norm_email(warn_to.get("email")) and norm_email(warn_to.get("email")) != me_a:
                # Cash is tight: the board partner hears it first, and decides whether the firm sources at all.
                to_, to_name_, note_kind = warn_to.get("email"), warn_to.get("name"), "board"
            elif p0 and p0.get("colleague") == "You":
                to_, to_name_, note_kind = p0.get("email"), p0.get("person"), "contact"  # you know the contact: ask them yourself
            elif p0:
                col = ((ctx or {}).get("lookup") or {}).get(p0.get("colleague_id")) or {}
                to_, to_name_, note_kind = (col.get("emails") or [None])[0], p0.get("colleague"), "colleague"  # they make the intro
            elif solo or not team:
                continue  # no one to ask: the row says no one in your network fits yet
            else:
                # First names, unless one is also the founder's ("Vikram" the colleague and Vikram Rao the founder).
                founder_first = str(a_.get("who") or "").split(" ")[0].lower()
                firsts = [str(m_.get("name") or m_.get("email")) if str(m_.get("name") or "").split(" ")[0].lower() == founder_first
                          else str(m_.get("name") or m_.get("email")).split(" ")[0] for m_ in team]
                to_ = ", ".join(norm_email(m_.get("email")) for m_ in team)
                to_name_ = firsts[0] if len(firsts) == 1 else ", ".join(firsts[:-1]) + f" and {firsts[-1]}"
                note_kind = "team"
            out.append({"id": f"dr_{aid}", "kind": "ask", "action_id": aid, "ask_id": a_.get("id"), "company": a_.get("company"),
                        "ask": a_.get("ask"), "who": a_.get("who"), "path": p0, "warning": a_.get("warning"), "note_kind": note_kind,
                        "to": (to_ if note_kind == "team" else norm_email(to_)) or None, "to_name": to_name_,
                        "context": ({"board": f"Cash is tight: {to_name_} hears it first and decides whether we source",
                                     "team": "No warm path found: a note to your team"}.get(note_kind) or
                                    f"Warm path: {p0['colleague']} {'know' if p0['colleague'] == 'You' else 'knows'} {p0['person']}"),
                        "source_label": a_.get("source_label") or "Founder update", "source_url": a_.get("source_url")})
            n_ask += 1
        # A note out five working days with no reply gets one short nudge: one per note, naming every ask it carried
        # that still waits. Never a nudge of a nudge, never when you already chose another way in (a tap such as
        # "Ask the team instead" not yet answered by a sent note), and never twice.
        nudges: dict[str, list[tuple[dict[str, Any], dict[str, Any], str]]] = {}
        for a_ in (asks or {}).values():
            aid = a_.get("item_id")
            notes_ = [n for n in a_.get("notes") or [] if isinstance(n, dict) and n.get("at") and n.get("tap")]
            if a_.get("status") == "done" or a_.get("made_on") or not aid or not notes_ or (item_state.get(aid) or {}).get("done_at"):
                continue
            last_ = max(notes_, key=lambda n: str(n.get("at")))
            tap_ = str(last_["tap"])
            sent_taps = {str(n.get("tap")) for n in notes_}
            if tap_.endswith("_nudge") or any(t_ for t_ in (taps or set()) if t_.startswith(f"{aid}_") and not t_.endswith("_nudge")
                                              and t_ not in sent_taps and t_ != tap_):
                continue
            ntap = f"{tap_}_nudge"
            at_ = parse_dt(last_.get("at"))
            replied_ = a_.get("replied") if isinstance(a_.get("replied"), dict) else {}
            put_off = bool(replied_.get("defers")) and _answers(replied_, last_) and parse_dt(replied_.get("on")) and \
                pipeline.working_days_since(parse_dt(replied_["on"]).date(), now.date()) >= 5
            if ntap in by_action or ntap in sent_taps or ntap in (a_.get("nudges_drafted") or []) or f"dr_{ntap}" in drafting or not at_ or \
                    pipeline.working_days_since(at_.date(), now.date()) < 5 or (_answers(replied_, last_) and not put_off):
                continue  # too soon, already nudged, or they answered
            nudges.setdefault(str(last_.get("draft") or ntap), []).append((a_, last_, ntap))
        for note_id, group in sorted(nudges.items(), key=lambda kv: str(kv[1][0][1].get("at")))[:3]:
            # In the note's own order, so the nudge reads like the note it follows.
            order_ = [str(x) for x in ((drafts.get(note_id) or {}).get("action_ids") or [])]
            group.sort(key=lambda g: (order_.index(str(g[1].get("tap"))) if str(g[1].get("tap")) in order_ else len(order_),
                                      str(g[0].get("company") or "")))
            a0, last0, _ = group[0]
            base_kind = last0.get("note_kind") or "contact"
            tos_ = [norm_email(x) for x in last0.get("to") or [] if norm_email(x)]
            names_ = [str(g[0].get("company") or "a founder") for g in group]
            on_ = fmt_short_date(at_) if (at_ := parse_dt(last0.get("at"))) else "your note"
            taps_ = [g[2] for g in group]
            # They answered the note's other asks: the nudge thanks them for those and asks only about these.
            oth_ = next((g[0]["answered_others"] for g in group if _answers(g[0].get("answered_others"), last0)), None)
            if not oth_ and last0.get("draft"):
                # Or they made the intro for another ask on that note since: the nudge thanks them for it first.
                made_ = [a_ for a_ in (asks or {}).values() if isinstance(a_, dict) and a_.get("made_on") and a_.get("company") and
                         str(a_["made_on"])[:10] >= str(last0.get("at") or "")[:10] and
                         any(isinstance(n_, dict) and n_.get("draft") == last0["draft"] for n_ in a_.get("notes") or [])]
                if made_:
                    oth_ = {"on": max(str(a_["made_on"]) for a_ in made_), "named": sorted(str(a_["company"]) for a_ in made_), "kind": "made"}
            oth_by = str((oth_ or {}).get("by") or last0.get("to_name") or "They").split(" ")[0]
            # They wrote that the answer would follow, and it has not: the nudge says so.
            def_ = next((g[0]["replied"] for g in group if isinstance(g[0].get("replied"), dict) and g[0]["replied"].get("defers") and
                         _answers(g[0]["replied"], last0)), None)
            out.append({"id": f"dr_{taps_[0]}", "kind": "ask_nudge", "action_id": taps_[0], "action_ids": taps_,
                        **({"answered": {"on": str(oth_.get("on") or "")[:10], "companies": oth_.get("named") or [], "url": oth_.get("url"),
                                         **({"kind": "made"} if oth_.get("kind") == "made" else {})}} if oth_ else {}),
                        "note_kind": "nudge", "nudge_of": base_kind, "to": ", ".join(tos_) or None, "to_name": last0.get("to_name"),
                        "sent_on": str(last0.get("at") or "")[:10], "company": ", ".join(names_),
                        "re": (drafts.get(str(last0.get("draft") or "")) or {}).get("subject") or last0.get("subject"),
                        **({"note_draft": last0["draft"]} if last0.get("draft") else {}),
                        "items": [{"action_id": g[2], "company": g[0].get("company"), "ask": g[0].get("ask"), "who": g[0].get("who"),
                                   "source_url": g[0].get("source_url")} for g in group],
                        "context": (f"{str(def_.get('by') or last0.get('to_name') or 'They').split(' ')[0]} wrote on "
                                    f"{fmt_short_date(parse_dt(def_.get('on')))} that the answer would follow, and it has not come: one short nudge"
                                    if def_ else
                                    f"{oth_by} {'made the intro for' if oth_.get('kind') == 'made' else 'answered on'} "
                                    f"{brief_mod._and(oth_.get('named') or [])} on {fmt_short_date(parse_dt(oth_.get('on')) or parse_date(oth_.get('on')))}, "
                                    f"not on {brief_mod._and(names_)}: one short nudge on {'that' if len(group) == 1 else 'those'} only" if oth_ else
                                    f"No reply since you wrote on {on_}: one short nudge" + (f" on {brief_mod._and(names_)}" if len(group) > 1 else "")) +
                                   f". Send it as a reply to your {on_} note, so the asks stay in view",
                        "source_label": a0.get("source_label") or "Founder update", "source_url": a0.get("source_url")})
        # A nudge still waiting follows its asks: when one moved on (another way in was tapped or sent, they answered, the
        # intro was made or the ask closed), it is rewritten for the asks still waiting on that note.
        by_item_ = {a_.get("item_id"): a_ for a_ in (asks or {}).values() if isinstance(a_, dict) and a_.get("item_id")}

        def moved_on(a_: dict[str, Any], tap: str) -> bool:
            notes_ = [n for n in a_.get("notes") or [] if isinstance(n, dict) and n.get("at") and n.get("tap")]
            last_ = max(notes_, key=lambda n: str(n.get("at")), default=None)
            rep_ = a_.get("replied") if isinstance(a_.get("replied"), dict) else {}
            aid_ = str(a_.get("item_id"))
            sent_ = {str(n.get("tap")) for n in notes_}
            return bool(a_.get("status") == "done" or a_.get("made_on") or (item_state.get(aid_) or {}).get("done_at") or not last_ or
                        f"{last_['tap']}_nudge" != tap or _answers(rep_, last_) or
                        any(t_ for t_ in (taps or set()) if t_.startswith(f"{aid_}_") and not t_.endswith("_nudge") and t_ not in sent_))
        for did, d in sorted(drafts.items()):
            if not isinstance(d, dict) or d.get("note_kind") != "nudge" or d.get("in_gmail") or did in drafting or \
                    (item_state.get(did) or {}).get("done_at"):
                continue
            keep_, gone_ = [], []
            for tap in [str(t) for t in (list(d.get("action_ids") or []) or [d.get("action_id")]) if t]:
                m_ = re.match(r"^(t_[0-9a-f]+)", tap)
                a_ = by_item_.get(m_.group(1)) if m_ else None
                if a_:
                    (gone_ if moved_on(a_, tap) else keep_).append((a_, tap))
            if gone_ and keep_:
                kept_names = [str(a_.get("company") or "a founder") for a_, _ in keep_]
                gone_names = [str(a_.get("company") or "a founder") for a_, _ in gone_]
                note0 = max((n for n in keep_[0][0].get("notes") or [] if isinstance(n, dict) and n.get("at")),
                            key=lambda n: str(n.get("at")), default={})
                out.append({"id": did, "kind": "narrow", "action_id": keep_[0][1], "action_ids": [t for _, t in keep_], "note_kind": "nudge",
                            "sent_on": str(note0.get("at") or "")[:10] or None,
                            "to": d.get("to"), "to_name": d.get("to_name"), "subject": d.get("subject"), "body": d.get("body"),
                            "items": [{"action_id": t, "company": a_.get("company"), "ask": a_.get("ask"), "who": a_.get("who")} for a_, t in keep_],
                            "dropped": gone_names, **({"old_context": d.get("context")} if d.get("context") else {}),
                            "context": f"{brief_mod._and(gone_names)} moved on since this nudge was written: it now asks about "
                                       f"{brief_mod._and(kept_names)} only",
                            "source_label": d.get("source_label"), "source_url": d.get("source_url")})
    # One note per person: several founder asks for the same colleague (two cash warnings and an intro, all to Aditi)
    # go in one email, a paragraph each, and the note keeps every ask's tap so each row still shows "Draft ready".
    groups_: dict[str, list[dict[str, Any]]] = {}
    for o_ in out:
        if o_.get("kind") == "ask" and o_.get("note_kind") in ("board", "colleague", "contact") and o_.get("to"):
            groups_.setdefault(str(o_["to"]), []).append(o_)
    for to_, group in groups_.items():
        if len(group) < 2:
            continue
        group.sort(key=lambda g: (g.get("note_kind") != "board", str(g.get("company") or "")))  # the partner's call first
        first_ = str(group[0].get("to_name") or "").split(" ")[0] or "them"
        merged = {**group[0], "action_ids": [g["action_id"] for g in group], "note_kinds": {g["action_id"]: g["note_kind"] for g in group},
                  "items": [{k: g.get(k) for k in ("action_id", "company", "ask", "who", "path", "warning", "note_kind", "source_url")} for g in group],
                  "note_kind": "several", "company": ", ".join(str(g.get("company")) for g in group),
                  "context": f"{len(group)} founder asks for {first_} in one note: " + ", ".join(str(g.get("company")) for g in group)}
        at = min(out.index(g) for g in group)
        out = [o_ for o_ in out if o_ not in group]
        out.insert(at, merged)
    # Two of today's emails reaching one person (an introduction copies Raj in, and a founder's ask writes to him): both
    # stay, and the note says the other is on its way.
    reach: dict[str, dict[str, Any]] = {}
    for o_ in out:
        if o_.get("kind") == "promise":
            for e_ in [o_.get("to")] + [x.strip() for x in str(o_.get("cc") or "").split(",") if x.strip()]:
                if norm_email(e_):
                    reach.setdefault(norm_email(e_), o_)
    for did_, d_ in drafts.items():
        if isinstance(d_, dict) and d_.get("commitment_id") and not (item_state.get(did_) or {}).get("done_at"):
            for e_ in [d_.get("to")] + [x.strip() for x in str(d_.get("cc") or "").split(",") if x.strip()]:
                if norm_email(e_):
                    reach.setdefault(norm_email(e_), {"id": did_, "to_name": d_.get("to_name"), "what": d_.get("subject")})
    for o_ in out:
        other = reach.get(norm_email(o_.get("to"))) if o_.get("kind") == "ask" else None
        if other and other.get("id") != o_["id"]:
            o_["also"] = {"id": other.get("id"), "what": other.get("what"), "to_name": other.get("to_name")}
    # Times already offered in drafts still waiting: never offered to a second person.
    held: set[str] = set()
    fixes: list[dict[str, Any]] = []
    # A rewrite keeps the promise it serves in view: what it is, when it is due, and who holds the firm's view.
    by_c = {c_["id"]: c_ for lst in (commitments_due or {}).values() if isinstance(lst, list) for c_ in lst if isinstance(c_, dict) and c_.get("id")}
    listed_ = {o_.get("id") for o_ in out}
    # Meeting notes by calendar event: this run's read, then what earlier runs read (Home keeps each meeting's notes link),
    # so a draft written before a meeting finds its notes on any later morning, not only the run that read them.
    notes_by_event = {**((ctx or {}).get("notes_by_event") or {}),
                      **{t_.get("event_id"): t_.get("url") for t_ in (((ctx or {}).get("bundle") or {}).get("transcripts") or [])
                         if t_.get("event_id") and t_.get("url")}}
    waits_on: dict[str, list[dict[str, Any]]] = {}  # the partner whose view each waiting draft needs
    theirs_by_ = {}
    for t_ in (commitments_due or {}).get("theirs") or []:
        if isinstance(t_, dict) and norm_email(t_.get("owed_by_email")):
            theirs_by_.setdefault(norm_email(t_.get("owed_by_email")), []).append(
                {"commitment_id": t_.get("id"), "what": t_.get("what"), "due": t_.get("due"), "overdue": bool(t_.get("overdue"))})
    for did, d in sorted(drafts.items()):
        if not isinstance(d, dict) or (item_state.get(did) or {}).get("done_at") or did in drafting or did in listed_ or d.get("kind") == "holder":
            continue
        first_d = parse_dt(d.get("first_made_at") or d.get("made_at"))
        if d.get("inbound_id") and not d.get("in_gmail") and first_d and (now - first_d).days > 7:
            continue  # Home drops it this morning: nothing to rewrite
        slots = [x for x in (parse_dt(v) for v in d.get("slots") or []) if x]
        made = parse_dt(d.get("made_at"))
        keep_links = {k: d.get(k) for k in ("commitment_id", "inbound_id", "question_id", "action_id", "action_ids", "note_kind", "note_kinds", "cc")
                      if d.get(k)}
        c_ = by_c.get(d.get("commitment_id")) or {}
        cid_d = (((ctx or {}).get("lookup") or {}).get(norm_email(d.get("to"))) or {}).get("company_id")
        holder_d = brief_mod.view_holder(ctx or {}, c_.get("what"), cid_d) if c_ else None
        if holder_d and c_:
            co_d = (((ctx or {}).get("companies") or {}).get(cid_d or "") or {}).get("name")
            waits_on.setdefault(holder_d, []).append({"draft": did, "commitment_id": c_.get("id"), "what": c_.get("what"), "to_name": d.get("to_name"), "company": co_d,
                                                      "due": c_.get("due"), "overdue": bool(c_.get("overdue")),
                                                      "source_url": d.get("source_url") or c_.get("source_url")})
        promise_d = {**({"what": c_.get("what"), "due": c_.get("due"), "overdue": bool(c_.get("overdue"))} if c_ else {}),
                     **({"holder": holder_d} if holder_d else {}), **({"old_context": d.get("context")} if d.get("context") else {})}
        # What they owe you, late or due: the rewrite asks for it in one line ("Could you also share the benchmarks?").
        owes_d = [] if d.get("cc") else (theirs_by_.get(norm_email(d.get("to"))) or [])[:2]
        stale_w = _stale_words(d.get("body"), made, now)
        base_fix = {"id": did, "to": norm_email(d.get("to")) or d.get("to"), "to_name": d.get("to_name"), "subject": d.get("subject"),
                    "body": d.get("body"), **keep_links, **promise_d, **({"they_owe": owes_d} if owes_d else {}),
                    **({"commitment_ids": d["commitment_ids"]} if d.get("commitment_ids") else {}),
                    **({"words": stale_w} if stale_w else {}),
                    "source_label": d.get("source_label"), "source_url": d.get("source_url")}
        hold_line = f". Check the firm's view with {holder_d.split(' ')[0]} before you send" if holder_d else ""
        # One email that keeps several promises, one of them closed since by Done on its row: it is rewritten for the
        # promises still open, at the next check, so Sent it never repeats what was settled another way.
        cids_d = _promise_ids(d)
        closed_d = [x_ for x_ in cids_d if (item_state.get(x_) or {}).get("done_at")]
        open_d = [x_ for x_ in cids_d if x_ not in closed_d]
        received_d = [x_ for x_ in d.get("asks_for") or [] if (item_state.get(x_) or {}).get("done_at")]
        if ((len(cids_d) > 1 and closed_d and open_d) or (received_d and open_d)) and not d.get("in_gmail"):
            what_ = lambda x_: str(((ctx or {}).get("promise_what") or {}).get(x_) or "a promise").rstrip(".")
            said_n = ([f"{brief_mod._and([what_(x_) for x_ in closed_d])} {'is' if len(closed_d) == 1 else 'are'} marked done"] if closed_d else []) + \
                ([f"{brief_mod._and([re.sub(r'^(share|send|give|forward)\s+', '', what_(x_), flags=re.I) for x_ in received_d])} came in"]
                 if received_d else [])
            fixes.append({**base_fix, "kind": "narrow", "commitment_id": open_d[0], "commitment_ids": open_d,
                          "promises": [{"commitment_id": x_, "what": what_(x_)} for x_ in open_d],
                          "dropped": [{"commitment_id": x_, "what": what_(x_)} for x_ in closed_d],
                          **({"received": [{"commitment_id": x_, "what": what_(x_)} for x_ in received_d]} if received_d else {}),
                          "context": "; ".join(said_n) + ": this email keeps " +
                                     brief_mod._and([_lower_first(what_(x_)) for x_ in open_d]) + (" only" if closed_d else "") +
                                     (", without asking for what came in" if received_d else "") + hold_line})
            continue
        if d.get("in_gmail"):
            held |= {x.isoformat() for x in slots if x >= now}
            continue  # a draft already in Gmail is never edited
        # A time today or earlier is no use in a draft not yet sent: the founder needs notice.
        stale_times = bool(slots) and min(slots).date() <= now.date()
        met_m = _met_meeting(ctx or {}, d.get("to"), made, now) if made else None
        met = met_m["start"] if met_m else None
        if met and d.get("inbound_id"):
            continue  # moot: Home drops a cold reply once you have met the founder
        if met:
            # Who was in the room and where the notes are: the rewrite greets only them and reads what was said.
            me_e = norm_email((ctx or {}).get("user_email"))
            met_with = list(dict.fromkeys(str(a_.get("name") or a_.get("email")) for a_ in met_m.get("attendees") or []
                                          if isinstance(a_, dict) and norm_email(a_.get("email")) != me_e and (a_.get("name") or a_.get("email"))))
            notes = notes_by_event.get(met_m.get("id"))
            fixes.append({**base_fix, "kind": "refresh", "met_on": met.date().isoformat(), "met_title": met_m.get("title"),
                          "met_with": met_with, "notes_url": notes, "has_notes": bool(notes),
                          **({"old_slots": [x.isoformat() for x in slots]} if stale_times else {"slots": [x.isoformat() for x in slots]} if slots else {}),
                          # With no notes there is nothing to bring it up to date from: the user checks it still stands.
                          "context": (f"Written before your {fmt_short_date(met)} meeting with them: brought up to date from the notes"
                                      if notes else f"Written before your {fmt_short_date(met)} meeting, which has no notes: check it still stands, "
                                                  "or tap Done if it was settled in the room") +
                                     (", with two new times" if stale_times else "") + hold_line})
            if not stale_times:
                held |= {x.isoformat() for x in slots if x >= now}
            continue
        if stale_times:
            fixes.append({**base_fix, "kind": "reslot", "old_slots": [x.isoformat() for x in slots],
                          "context": "The times this draft offered are today or earlier, too short notice: two new ones from your calendar" + hold_line})
            continue
        held |= {x.isoformat() for x in slots if x >= now}
        # Written before you met people it names (a guest list, an introduction): checked against that meeting.
        # (Since it was last written or checked: a rewrite that kept every line still counts as checked.)
        named_m = _named_meeting(ctx or {}, d.get("body"), d.get("to"), parse_dt(d.get("updated_at")) or made, now) \
            if made and not d.get("inbound_id") else None
        if named_m:
            m_, named_ = named_m
            notes = notes_by_event.get(m_.get("id"))
            firsts_ = [n_.split(" ")[0] for n_ in named_]
            fixes.append({**base_fix, "kind": "refresh", "named_only": True, "met_on": m_["start"].date().isoformat(), "met_title": m_.get("title"),
                          "met_with": named_, "notes_url": notes, "has_notes": bool(notes),
                          **({"slots": [x.isoformat() for x in slots]} if slots else {}),
                          "context": f"Written before your {fmt_short_date(m_['start'])} meeting with {brief_mod._and(firsts_)}, whom it names: " +
                                     ("brought up to date from the notes" if notes else "check it still stands") + hold_line})
            continue
        # A day it named has come or gone ("this week", written last week; "by Tue 27 Oct" on Thu 29): a date goes in its place.
        if stale_w:
            past_ = next((w_ for w_ in stale_w if re.search(r"\d", w_)), None)
            # Who set the date decides the rewrite: ant.'s own suggestion moves; one the user or a source set stays,
            # with a line that owns the delay.
            ours_ = d.get("date_set_by") == "instinct" or bool(re.search(r"(Instinct|ant\.)'s suggestion\b", str(d.get("context") or "")))
            fixes.append({**base_fix, "kind": "redate", "words": stale_w, "made_on": made.date().isoformat(), "set_by": "instinct" if ours_ else "you",
                          **({"slots": [x.isoformat() for x in slots]} if slots else {}),
                          "context": (((f"It said \"{past_}\", which no longer holds: a date two working days out is in its place, as ant.'s "
                                        "suggestion: change it if you like") if ours_ else
                                       f"It said \"{past_}\", which has passed: a date two working days out is in its place, with one line that owns the delay, as ant.'s suggestion. Change it if you like")
                                      if past_ else f"Written on {fmt_short_date(made)}, it said \"{stale_w[0]}\": a date is in its place now") + hold_line})
    fixes = fixes[:10]
    for f_ in fixes:
        if f_.get("old_slots"):
            f_["avoid_slots"] = sorted(held)
    for o in out:
        if commit_mod.is_scheduling(str(o.get("what") or "")):
            o["avoid_slots"] = sorted(held)
    out = out + fixes
    # Two or more of your drafts wait on one partner's view (the feedback after their meeting, a pricing view): one short
    # internal note asks for it, each draft in one line, once a morning. Never when the view is yours.
    today_ = now.date().isoformat()
    me_h = norm_email((ctx or {}).get("user_email"))
    for o_ in out:  # this morning's new drafts that share a partner's view wait on it too
        if o_.get("kind") == "promise" and o_.get("holder") and o_.get("commitment_id") not in {w_.get("commitment_id") for w_ in waits_on.get(o_["holder"]) or []}:
            waits_on.setdefault(o_["holder"], []).append({"draft": o_["id"], "commitment_id": o_.get("commitment_id"), "what": o_.get("what"),
                                                          "to_name": o_.get("to_name"), "company": o_.get("company"), "due": o_.get("due"),
                                                          "overdue": bool(o_.get("overdue")), "source_url": o_.get("source_url")})
    # A decision due within two working days on a deal that partner sponsors, and that you work on: the note names it too.
    decide_by: dict[str, list[dict[str, Any]]] = {}
    deals_h = {d_.get("id"): d_ for d_ in (ctx or {}).get("deals") or [] if isinstance(d_, dict) and d_.get("id")}
    for s_ in races or []:
        dl_ = parse_date(s_.get("deadline"))
        deal_ = deals_h.get(s_.get("deal_id")) or {}
        on_deal = me_h and me_h in {norm_email(deal_.get("owner_email"))} | {norm_email(t_) for t_ in deal_.get("team") or [] if isinstance(t_, str)}
        if not dl_ or dl_ < now.date() or pipeline.working_days_since(now.date(), dl_) > 2 or not on_deal:
            continue
        sp_ = pipeline.sponsor(ctx or {}, deal_)
        if sp_ and sp_ in waits_on and not any(x_.get("deal_id") == s_.get("deal_id") for x_ in decide_by.get(sp_) or []):
            decide_by.setdefault(sp_, []).append({"deal_id": s_.get("deal_id"), "company": s_.get("company"), "deadline": dl_.isoformat(),
                                                  "what": pipeline.signal_phrase(s_), "source_url": s_.get("source_url")})
    # Quiet deals stay out of every draft to a colleague (safety rule 6): no line, and no decision, names one.
    quiet_h = _quiet_set(ctx or {}) if ctx else {"deals": set(), "companies": set(), "names": set()}
    for holder_, waiting_all in sorted(waits_on.items()):
        slug_ = re.sub(r'[^a-z0-9]+', '_', holder_.lower()).strip('_')
        mem_ = next((m_ for m_ in (ctx or {}).get("members") or [] if str(m_.get("name") or "").lower() == holder_.lower() and norm_email(m_.get("email"))), None)
        if not mem_ or norm_email(mem_.get("email")) == me_h:
            continue
        waiting_ = [w_ for w_ in waiting_all if not _touches_quiet(w_, quiet_h)]
        decide_ = sorted([x_ for x_ in decide_by.get(holder_) or [] if not _touches_quiet(x_, quiet_h)], key=lambda x_: x_["deadline"])
        # One note per partner, under one id, rebuilt in place while it waits. Once sent, none while it waits on their
        # answer: after they reply (in the note's thread), or in the three working days after it went, no other note;
        # then a second note only for drafts the first did not name.
        prior_ = sorted(((did_, d_) for did_, d_ in drafts.items() if isinstance(d_, dict) and d_.get("kind") == "holder" and
                         norm_email(d_.get("to")) == norm_email(mem_["email"])), key=lambda kv: str(kv[1].get("first_made_at") or kv[1].get("made_at") or ""))
        waiting_prior = [(did_, d_) for did_, d_ in prior_ if not (item_state.get(did_) or {}).get("done_at")]
        sent_prior = [(did_, d_) for did_, d_ in prior_ if _was_sent(item_state.get(did_))]
        named_before = {h_ for _, d_ in sent_prior for h_ in d_.get("holds") or []} | \
            {x_.get("deal_id") for _, d_ in sent_prior for x_ in d_.get("decisions") or []}
        if sent_prior and not waiting_prior:
            last_did, last_ = sent_prior[-1]
            sent_at_ = parse_dt((item_state.get(last_did) or {}).get("done_at"))
            if not last_.get("replied") and sent_at_ and pipeline.working_days_since(sent_at_.date(), now.date()) < 3:
                continue  # it just went: no other note while it waits on her answer
            # Answered or not, what a sent note named is never asked again: her answer covers it, or a nudge would.
            waiting_ = [w_ for w_ in waiting_ if w_.get("draft") not in named_before]
            decide_ = [x_ for x_ in decide_ if x_.get("deal_id") not in named_before]
        # A new note needs two things to ask about; one already waiting is rebuilt down to the one left, never left
        # asking about a draft already sent. A note saved in Gmail is never rewritten: Home says which line to take out.
        if not waiting_ or (len(waiting_) + len(decide_) < 2 and not waiting_prior):
            continue
        if waiting_prior and waiting_prior[-1][1].get("in_gmail"):
            continue
        waiting_.sort(key=lambda w_: (not w_.get("overdue"), str(w_.get("due") or "9999")))
        if waiting_prior:
            hid_ = waiting_prior[-1][0]
        else:  # a new note never reuses the id of one already sent, even one Home no longer keeps
            n_h = len(sent_prior) + 1
            hid_ = f"dr_hold_{slug_}" if n_h == 1 else f"dr_hold_{slug_}_{n_h}"
            while (item_state.get(hid_) or {}).get("done_at"):
                n_h += 1
                hid_ = f"dr_hold_{slug_}_{n_h}"
        if hid_ in drafting:
            continue
        if waiting_prior:
            # Waiting in Home already: rebuilt only when what it asks about changed (a held draft was sent, a new one waits).
            old_ = waiting_prior[-1][1]
            if set(old_.get("holds") or []) == {w_.get("draft") for w_ in waiting_[:5]} and \
                    {x_.get("deal_id") for x_ in old_.get("decisions") or []} == {x_.get("deal_id") for x_ in decide_[:3]}:
                continue
        first_h = holder_.split(" ")[0]
        out.append({"id": hid_, "kind": "holder", "to": norm_email(mem_["email"]), "to_name": holder_, "items": waiting_[:5],
                    **({"decisions": decide_[:3]} if decide_ else {}), **({"rebuild": True} if waiting_prior else {}),
                    "context": f"{plural(len(waiting_), 'draft')} wait on {first_h}'s view" +
                               (f", and {plural(len(decide_), 'decision')} {'is' if len(decide_) == 1 else 'are'} due" if decide_ else "") +
                               f": one short note asks {first_h} for it. The drafts stay as they are until you have it",
                    "source_label": "Meeting notes", "source_url": waiting_[0].get("source_url") or (decide_[0].get("source_url") if decide_ else None)})
    # A promise with no date that is an email by nature ("Invite Rahul to the founders dinner") is never its own email,
    # but it rides in the draft already waiting for that person, as one line: one email per person. When that draft is
    # being rewritten anyway (after a meeting, a stale day), the rewrite carries it; otherwise the draft is listed to join.
    waiting_to: dict[str, tuple[str, dict[str, Any]]] = {}
    for did, d in drafts.items():
        if isinstance(d, dict) and d.get("to") and not d.get("in_gmail") and not (item_state.get(did) or {}).get("done_at") and \
                did not in drafting and d.get("commitment_id"):
            waiting_to.setdefault(norm_email(d["to"]), (did, d))
    by_id_out = {o.get("id"): o for o in out}
    for c in (commitments_due.get("undated") or [])[:4]:
        if c.get("looks_done") or c["id"] in have_c or (item_state.get(c["id"]) or {}).get("done_at") or \
                not c.get("owed_to_email") or not EMAILABLE.search(str(c.get("what") or "")):
            continue
        hit_ = waiting_to.get(norm_email(c["owed_to_email"]))
        if not hit_:
            continue
        did_, d_ = hit_
        made_u = parse_date(c.get("meeting_date"))
        line_ = "Also carries your promise" + (f" of {fmt_short_date(made_u)}" if made_u else "") + \
            f" to {_lower_first(str(c['what']).rstrip('.'))}, which has no date"
        also_ = {"commitment_id": c["id"], "what": c["what"], "made_on": c.get("meeting_date"), "quote": c.get("quote")}
        o_ = by_id_out.get(did_)
        if o_ is not None:
            if o_.get("kind") in ("promise", "question", "inbound_reply", "letter", "lp_call"):
                continue  # that email is new this morning: the promise waits for its next rewrite
            o_.setdefault("also_promises", []).append(also_)
            o_["commitment_ids"] = list(dict.fromkeys(list(o_.get("commitment_ids") or []) + _promise_ids(d_) + [c["id"]]))
            o_["context"] = (str(o_.get("context") or "").rstrip(".") + ". " if o_.get("context") else "") + line_
            continue
        entry_ = {"id": did_, "kind": "promise", "commitment_id": d_.get("commitment_id"), "commitment_ids": _promise_ids(d_) + [c["id"]],
                  "to": norm_email(c["owed_to_email"]), "to_name": c.get("owed_to"), "what": c["what"], "due": None, "overdue": False,
                  "undated": True, "also_promises": [also_], "join": {"subject": d_.get("subject"), "body": d_.get("body")},
                  "internal": bool(c.get("internal")), "made_on": c.get("meeting_date"), "quote": c.get("quote"),
                  "context": (d_.get("context") + ". " if d_.get("context") else "") + line_,
                  "source_label": d_.get("source_label") or "Meeting notes", "source_url": d_.get("source_url") or c.get("source_url")}
        out.append(entry_)
        by_id_out[did_] = entry_
    # A founder's question on your own deal with nothing from the firm since: the answer is drafted like a promise.
    me_ = norm_email((ctx or {}).get("user_email"))
    own = {d["id"] for d in (ctx or {}).get("deals") or [] if d.get("owner_email") == me_ or
           me_ in {norm_email(t) for t in (d.get("team") or []) if isinstance(t, str)}}
    have_q = {d.get("question_id") for d in drafts.values() if isinstance(d, dict)}
    by_to_q = {o["to"]: o for o in out}
    n_q = 0
    for q in asked or []:
        to = norm_email(q.get("email"))
        if q["deal_id"] not in own or not to or q["id"] in have_q or f"dr_{q['id']}" in drafting or n_q >= 3 or \
                (item_state.get(brief_mod.item_id("question", q["id"])) or {}).get("done_at"):
            continue
        if to in by_to_q:
            by_to_q[to]["question_id"] = q["id"]  # one email to one person: the promise's draft answers the question too
            by_to_q[to]["question"] = q.get("question")
            continue
        joined = open_to.get(to)
        if joined and joined[1].get("in_gmail"):
            joined = None
        first = str(q.get("person") or "They").split(" ")[0]
        out.append({"id": joined[0] if joined else f"dr_{q['id']}", "kind": "question", "question_id": q["id"], "deal_id": q["deal_id"],
                    **({"join": {"subject": joined[1].get("subject"), "body": joined[1].get("body")}} if joined else {}),
                    "to": to, "to_name": q.get("person"), "company": q.get("company"), "question": q.get("question"),
                    "asked_on": q.get("asked_on"), "subject": q.get("subject"),
                    "context": f"{first} asked on {fmt_short_date(parse_date(q.get('asked_on')))}, no reply yet",
                    "source_label": "Email", "source_url": q.get("source_url")})
        n_q += 1
    triage = (profile.get("modules") or {}).get("triage")
    if triage not in ("all", "own"):
        return out
    talking = _talking(ctx or {}, inbound_rows, now)
    by_to = {o["to"]: o for o in out}
    rank = {"call": 1, "more_info": 2, "pass": 3}

    sent_on: dict[str, str] = {}  # when each pitch arrived, from its thread
    for th in (((ctx or {}).get("bundle") or {}).get("threads") or []):
        dates = [str(m.get("date") or "") for m in th.get("messages") or [] if m.get("date")]
        if dates:
            sent_on[str(th.get("id"))] = min(dates)

    def order(r: dict[str, Any]) -> tuple:
        # Companies back with what we asked for first, then the oldest pitch first: no founder waits days for an answer.
        met = (r.get("revisit_check") or {}).get("met") is True
        return (0 if met else 1, sent_on.get(str(r.get("thread_id"))) or str(r.get("seen_at") or "9999"), rank.get(r.get("decision"), 4))

    replies: list[dict[str, Any]] = []
    for r in sorted(inbound_rows, key=order):
        to = norm_email(r.get("from"))
        if r["id"] in have_i or r.get("drafted") or r.get("injection_flag") or not to or r.get("answered") or (item_state.get(f"in_{r['id']}") or {}).get("done_at") or \
                f"dr_{r['id']}" in drafting:
            continue
        seen = parse_dt(r.get("seen_at"))
        arrived = parse_dt(r.get("arrived")) or (parse_dt(sent_on.get(str(r.get("thread_id")))) if r.get("thread_id") else None)
        if (seen and (now - seen).days > 2) or (arrived and (now - arrived).days > 5):
            continue  # a reply drafted days late reads worse than none; a pitch's age is its email's, not when Home saw it
        if triage == "own" and r.get("decision") != "call" and (r.get("revisit_check") or {}).get("met") is not True:
            continue  # a level that triages its own pitches gets replies drafted for the strong ones only
        if str(r.get("domain") or "").lower() in talking or to.split("@")[-1] in talking or to in have_to:
            continue  # you already talk to this founder: no cold reply on top
        if to in by_to:
            by_to[to]["inbound_id"] = r["id"]  # one email to one person
            continue
        founder = ((ctx or {}).get("lookup", {}).get(to) or {}).get("name")
        replies.append({"id": f"dr_{r['id']}", "kind": "inbound_reply", "inbound_id": r["id"], "to": to, "to_name": founder,
                        **({"avoid_slots": sorted(held)} if r["decision"] == "call" or (r.get("revisit_check") or {}).get("met") is True else {}),
                        "company": r.get("company"), "decision": r["decision"], "score": r.get("score"),
                        "missing": [x["text"] for x in r.get("reasons") or [] if not x.get("ok")][:3], "ask_for": _ask_for(r),
                        "pass_reason": r.get("pass_reason"), "revisit_check": r.get("revisit_check"),
                        **({"why_pass": _why_pass(r, ((ctx or {}).get("bundle") or {}).get("thesis") or {})} if r["decision"] == "pass" else {}),
                        "context": f"Inbound pitch, score {r.get('score')}: {r['decision'].replace('_', ' ')}",
                        "source_label": "Email", "source_url": r.get("source_url")})
    # Every new pitch gets its reply the first morning, oldest first, up to twenty: passes included, since a kind
    # no is most of an analyst's inbox.
    return out + replies[:20]


def _named_meeting(ctx: dict[str, Any], body: Any, to: Any, after, now) -> tuple[dict[str, Any], list[str]] | None:
    """The last meeting since `after` with people the draft names in full, other than its recipient (a guest list
    written before you met the guests), with their names; else None."""
    text = str(body or "")
    if not text or not after:
        return None
    me, to_e = norm_email(ctx.get("user_email")), norm_email(to)
    best = None
    for m in ctx.get("meetings") or []:
        st = m.get("start")
        if not st or not (after < st <= now):
            continue
        named = []
        for a_ in m.get("attendees") or []:
            nm = str((a_ or {}).get("name") or "").strip() if isinstance(a_, dict) else ""
            if norm_email((a_ or {}).get("email")) in (me, to_e) or len(nm.split()) < 2:
                continue
            if re.search(rf"\b{re.escape(nm)}\b", text):
                named.append(nm)
        if named and (not best or st > best[0]["start"]):
            best = (m, named)
    return best


# Words that fix a day relative to when a draft was written: wrong once that day or week has gone. "Today" counts only
# as a time ("later today", "when we meet today"), never as "now" ("one sponsor bank today").
STALE_DAY = ("tonight", "this morning", "this afternoon", "this evening", "tomorrow", "yesterday")
TODAY_TIME = re.compile(r"\b(?:later|by|until|before|from|end of|on) today\b|\btoday at \d|\b(?:meet|speak|talk|call|see you|catch up)\w* today\b"
                        r"|\btoday'?s (?:call|meeting|session)\b", re.I)
STALE_WEEK = ("this week", "next week", "end of the week", "end of this week")


# A date a draft promises to meet ("I will introduce you by Tue 27 Oct", "before 30 October"): stale once it has passed.
# A date the draft looks back on ("good to see you on 22 Oct") is never one.
PROMISED_DATE = re.compile(r"\b(?:by|before|until|till|no later than|on or before)\s+(?:(?:mon|tue|wed|thu|fri|sat|sun)[a-z]*,?\s+)?"
                           r"(\d{1,2})(?:st|nd|rd|th)?\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b", re.I)
MONTH_N = {m_: i + 1 for i, m_ in enumerate(("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"))}
# A date with no lead word ("I will introduce you Thu 29 Oct"): a promise when its sentence looks ahead, never when the
# words just before it look back ("Good to see you on 22 Oct").
BARE_DATE = re.compile(r"\b(?:(?:mon|tue|wed|thu|fri|sat|sun)[a-z]*,?\s+)?(\d{1,2})(?:st|nd|rd|th)?\s+"
                       r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b", re.I)
AHEAD_CUE = re.compile(r"\b(will|i'll|we'll|shall|going to|plan to|aim to|expect to|let's|can we|could we|happy to)\b", re.I)
BACK_CUE = re.compile(r"\b(see you|saw|met|meet(?:ing)? on|spoke|talked|wrote|sent|thanks? (?:you )?for|since|last|was|were|had)\b[^.!?\n]{0,24}$", re.I)
# Words that ask the reader first ("Tell me who you would like to meet, and I will introduce you ..."): a date that is
# today cannot hold once they have to answer first.
ASK_FIRST = re.compile(r"\b(tell me|let me know|once you|when you|after you|as soon as you)\b", re.I)


def _stale_words(body: Any, made, now) -> list[str]:
    """Days in a waiting draft that no longer hold: "tomorrow" or "later today" from an earlier day, "this week" or
    "next week" from an earlier week (and "this week" on a Friday, when only today is left of it), and a date it
    promised to meet that has passed ("by Tue 27 Oct", read on Thu 29 Oct)."""
    if not made:
        return []
    text = str(body or "")
    same_day = made.date() == now.date()
    same_week = made.isocalendar()[:2] == now.isocalendar()[:2]
    out = (["today"] if not same_day and TODAY_TIME.search(text) else []) + \
        [w for w in STALE_DAY if not same_day and re.search(rf"\b{w}\b", text, re.I)]
    out += [w for w in STALE_WEEK if re.search(rf"\b{w}\b", text, re.I) and
            (not same_week or (w in ("this week", "end of the week", "end of this week") and now.weekday() >= 4 and not same_day))]
    def when_of(m_):
        day_, mon_ = int(m_.group(1)), MONTH_N[m_.group(2)[:3].lower()]
        year_ = made.year + (1 if mon_ < made.month - 6 else 0)  # a December draft naming "by 5 Jan" means next year
        try:
            return made.replace(year=year_, month=mon_, day=day_).date()
        except ValueError:
            return None
    taken = []
    for m_ in PROMISED_DATE.finditer(text):
        taken.append(m_.span())
        when_ = when_of(m_)
        # Only a date that was still ahead when the draft was written: "the data room was closed until 20 Oct", in a
        # draft of 22 Oct, is a fact, not a promise.
        if when_ and made.date() <= when_ < now.date():
            out.append(m_.group(0).strip())
    for m_ in BARE_DATE.finditer(text):
        if any(a_ <= m_.start() < b_ for a_, b_ in taken):
            continue
        start_ = max(text.rfind(c_, 0, m_.start()) for c_ in ".!?\n") + 1
        end_ = min([i_ for i_ in (text.find(c_, m_.end()) for c_ in ".!?\n") if i_ >= 0] or [len(text)])
        before_, sentence_ = text[start_:m_.start()], text[start_:end_]
        when_ = when_of(m_)
        if not when_ or BACK_CUE.search(before_) or not AHEAD_CUE.search(sentence_):
            continue
        if when_ < made.date():
            continue
        if when_ < now.date() or (when_ == now.date() and ASK_FIRST.search(before_)):
            out.append(m_.group(0).strip())
    return out


def _met_meeting(ctx: dict[str, Any], email: Any, after, now) -> dict[str, Any] | None:
    """The last meeting with this person (or anyone at their company) after `after`, up to now; else None."""
    e = norm_email(email)
    if not e or not after:
        return None
    lookup = ctx.get("lookup") or {}
    person = lookup.get(e) or {}
    pid, cid = person.get("id"), person.get("company_id")
    best = None
    for m in ctx.get("meetings") or []:
        st = m.get("start")
        if not st or not m.get("external") or m.get("all_day") or not (after < st <= now):
            continue
        ids = m.get("external_ids") or []
        if (pid and pid in ids) or (cid and any((lookup.get(x) or {}).get("company_id") == cid for x in ids)):
            best = m if not best or st > best["start"] else best
    return best


def _met_since(ctx: dict[str, Any], email: Any, after, now):
    """When the user last met this person (or anyone at their company) after `after`, up to now; else None."""
    m = _met_meeting(ctx, email, after, now)
    return m["start"] if m else None


def _talking(ctx: dict[str, Any], inbound_rows: list[dict[str, Any]], now) -> set[str]:
    """Domains you met in the last week, have a meeting booked with, or wrote to in the last 14 days (on another thread
    or in the pitch's own thread)."""
    talking: set[str] = set()
    for m in ctx.get("meetings") or []:
        if m.get("start") and now - timedelta(days=7) <= m["start"] <= now + timedelta(days=14):
            for pid in m.get("external_ids") or []:
                for e in (ctx.get("lookup", {}).get(pid) or {}).get("emails") or []:
                    talking.add(str(e).split("@")[-1].lower())
    me_ = norm_email(ctx.get("user_email"))
    firm_dom = me_.split("@")[-1] if me_ else ""
    for th in ((ctx.get("bundle") or {}).get("threads") or []):
        mine = [m for m in th.get("messages") or [] if norm_email((m.get("from") or {}).get("email")) == me_ and
                (parse_dt(m.get("date")) or now) >= now - timedelta(days=14)]
        if mine:  # you already write to them, on another thread or in the pitch itself: no cold reply on top
            for p_ in th.get("participants") or []:
                dom = str((p_ or {}).get("email") or "").split("@")[-1].lower()
                if dom and dom != firm_dom:
                    talking.add(dom)
    return talking


def _things(the_brief: dict[str, Any]) -> int:
    """What the headline counts: Today's rows and the hero, so "12 things for today" and the run row agree."""
    h_ = the_brief.get("hero") or {}
    return int(the_brief.get("count") or 0) + (1 if h_.get("item_id") and h_.get("kind") != "meeting" else 0)


def _applied_stage_moves(home: dict[str, Any], applied: dict[str, Any] | None, now, stage_map: dict[str, Any],
                         tz: str | None = None) -> dict[str, Any]:
    """{deal id: (stage key, when)} for the stage changes Home's met log asked for and a run applied: this run's
    results first, then earlier runs' (kept 30 days in snap/proposals). A stage the CRM already held is no move. The
    deal entered the stage on the day of the meeting that moved it, when the log names one."""
    acts = (((home.get("state") or {}).get("actions") or {}).get("items")) or {}
    props = (((home.get("snap") or {}).get("proposals") or {}).get("items")) or {}
    out: dict[str, Any] = {}
    for aid, act in acts.items():
        pay = (act or {}).get("payload") or {}
        if (act or {}).get("type") != "next_step" or not pay.get("stage") or not pay.get("deal_id"):
            continue
        res = (applied or {}).get(aid)
        if res is not None:
            if res.get("status", "applied") != "applied" or "stage" in (res.get("skipped") or []) or "stage" in (res.get("already") or []):
                continue
            when = now
        else:
            p = props.get(aid) or {}
            when = parse_dt(p.get("applied_at"))
            if p.get("status") != "applied" or not when or "stage" in (p.get("skipped") or []) or "stage" in (p.get("already") or []):
                continue
        key = stages.map_stage(str(pay["stage"]), stage_map)
        met_ = parse_dt(str(pay.get("met") or "")[:10], tz) if pay.get("met") else None
        when = met_ if met_ and met_ <= when else when
        if pay["deal_id"] not in out or when > out[pay["deal_id"]][1]:
            out[pay["deal_id"]] = (key, when)
    return out


def _ask_hero(open_asks: list[dict[str, Any]], parts: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    """The founder ask that needs the user now, said where it stands: a note of theirs ready to send first, then a nudge
    due, then the oldest ask with no note out; when every ask waits on someone else, the newest, with who has it."""
    if not open_asks:
        return {}
    today = ctx["now"].date()
    views = [(a, brief_mod.ask_view(a, parts, today)) for a in open_asks]
    views.sort(key=lambda x: (x[1]["rank"], str(x[0].get("date") or "") if x[1]["rank"] == 2 else "",
                              "" if x[1]["rank"] == 2 else str(x[0].get("date") or "")))
    if all(v["rank"] >= 3 for _, v in views):
        views.sort(key=lambda x: str(x[0].get("date") or ""), reverse=True)
    a0, v0 = views[0]
    if v0.get("group") and v0.get("nudge"):  # asks that went out in one note: one nudge, said once
        members = [a for a, v in views if v.get("group") == v0["group"] and v.get("nudge")]
        if len(members) > 1:
            g = brief_mod.ask_group_row(members, {a["id"]: v for a, v in views}, parts, today)
            rest = len(open_asks) - len(members)
            return {"statement": g["title"], "finding": g["detail"] + (f". {rest} more open" if rest else ""), "ask_id": a0.get("id"),
                    "company_id": a0.get("company_id"), "item_id": a0.get("item_id"), "state": v0["word"], "group_asks": g["group_asks"],
                    **({"draft": g["draft"]} if g.get("draft") else {}), **({"ready_form": g["ready_form"]} if g.get("ready_form") else {}),
                    "source_url": a0.get("source_url"), "source_label": a0.get("source_label") or "Founder update"}
    who = a0.get("who") if a0.get("who") and str(a0.get("who")).lower() not in ("the founder", "founder") else \
        (_founder(ctx, a0.get("company_id")) or "The founder")
    asked_on = parse_date(a0.get("date"))
    more = len(open_asks) - 1
    finding = (v0["lead"] if v0["lead"] else (f"{v0['state']}. " if v0.get("note_ready") else "")) + \
        (f"{a0['warning']}. " if a0.get("warning") else "") + f"{who} asked" + (f" on {fmt_short_date(asked_on)}" if asked_on else "") + \
        (f". {more} more open" if more else "")
    return {"statement": f"{a0.get('company')}: {_lower(a0['ask'])}", "finding": finding, "ask_id": a0.get("id"),
            "company_id": a0.get("company_id"), "item_id": a0.get("item_id"), "state": v0["word"],
            **({"draft": v0["draft"]} if v0.get("draft") else {}),
            "source_url": a0.get("source_url"), "source_label": a0.get("source_label") or "Founder update"}


def _date_stage_moves(ctx: dict[str, Any], home: dict[str, Any], dated: set[str] | None = None) -> None:
    """Every Home dates a stage move, not only the Home that made it. When the CRM moved a deal on since this Home last
    looked but kept the old stage's date (many CRMs keep none), the deal entered its new stage on the CRM's last contact
    when that came after Home's last look (the meeting that moved it), else now. Home keeps the later of its own date
    and the CRM's while the stage holds."""
    pipe = (home.get("snap") or {}).get("pipeline") or {}
    old = pipe.get("deals") or {}
    seen = parse_dt(pipe.get("as_of"))
    now = ctx["now"]
    for d in ctx["deals"]:
        prev = old.get(d["id"]) or {}
        if not prev.get("stage_key") or not seen or d["id"] in (dated or set()):
            continue  # a move this Home's own met log made is dated from its meeting already
        crm_in = d.get("stage_entered_dt")
        same = prev["stage_key"] == d["stage_key"] or (prev.get("stage") and prev.get("stage") == stages.label(d.get("stage_name") or ""))
        if same:
            mine = parse_dt(str(prev.get("stage_entered") or "")[:10], ctx.get("tz")) if prev.get("stage_entered") else None
            if mine and mine <= now and (not crm_in or mine > crm_in):
                d["stage_entered_dt"], d["stage_entered"] = mine, mine.date().isoformat()
            continue
        if crm_in and crm_in > seen:
            continue  # the CRM dated the move itself
        lc = parse_dt(str(d.get("last_contact") or "")[:10], ctx.get("tz")) if d.get("last_contact") else None
        when = lc if lc and lc.date() >= seen.date() and lc <= now else now
        d["stage_entered_dt"], d["stage_entered"] = when, when.date().isoformat()


def _met_prompts(ctx: dict[str, Any], deals: dict[str, Any], home: dict[str, Any],
                 props: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """After a founder meeting on your own deal, one tap logs it: the next step, the stage and the date you met. Shown
    while the CRM's last contact is older than the meeting, newest meeting first. A log saved with no step asks once
    more, for the step alone, after a run applied it."""
    me = norm_email(ctx.get("user_email"))
    actions = (((home.get("state") or {}).get("actions") or {}).get("items")) or {}
    props = props if props is not None else ((((home.get("snap") or {}).get("proposals") or {}).get("items")) or {})
    active = [s_ for s_ in ctx["stage_map"]["stages"] if s_["active"]]
    out = []
    for did, d in deals.items():
        if not d.get("active") or norm_email(d.get("owner")) != me:
            continue
        # Logged with no step, where none was left standing (the CRM had none, or it was this meeting): once a run
        # applied the log, the owner's Today asks for the step alone until one is set, however long ago the meeting was.
        step_only = None
        for lid_, act_ in actions.items():
            if not isinstance(act_, dict) or not (lid_ == f"ns_{did}" or lid_.startswith(f"ns_{did}_")):
                continue
            pay = act_.get("payload") or {}
            met_ = str(pay.get("met") or "")[:10] or lid_[len(f"ns_{did}_"):]
            no_step = not str(pay.get("text") or "").strip() and (pay.get("clear_step") or not str(pay.get("current") or "").strip())
            if met_ and no_step and (props.get(lid_) or {}).get("status") == "applied" and f"nss_{did}_{met_}" not in actions and \
                    not str(d.get("next_step") or "").strip() and (not step_only or met_ > step_only):
                step_only = met_
        # The deal remembers the request (Home drops the log's applied row after a month): it stays until a step is set.
        old_need = str(((((home.get("snap") or {}).get("pipeline") or {}).get("deals") or {}).get(did) or {}).get("needs_step") or "")
        if not step_only and old_need and not str(d.get("next_step") or "").strip() and f"nss_{did}_{old_need}" not in actions:
            step_only = old_need
        if step_only and not str(d.get("next_step") or "").strip():
            d["needs_step"] = step_only
        if step_only and (not d.get("last_met") or str(d["last_met"])[:10] <= step_only):
            out.append({"deal_id": did, "company": d.get("company"), "met_on": step_only, "step_only": True, "aid": f"nss_{did}_{step_only}",
                        "next_step": d.get("next_step"), "next_step_due": d.get("next_step_due"), "stage": d.get("stage"),
                        "stage_key": d.get("stage_key"), "source_url": d.get("source_url")})
            continue
        if not d.get("last_met"):
            continue
        met = str(d["last_met"])[:10]
        # One log per meeting: the tap's id names the meeting, so next week's meeting with the same founder asks again.
        lid = f"ns_{did}_{met}" if f"ns_{did}_{met}" in actions else f"ns_{did}"
        logged = actions.get(lid) if lid != f"ns_{did}" or ((actions.get(lid) or {}).get("payload") or {}).get("met") in (met, None) else None
        if logged:
            continue
        if d.get("crm_last_contact") and str(d["crm_last_contact"])[:10] >= met:
            continue  # the CRM already knows about this meeting
        idx = next((i for i, s_ in enumerate(active) if s_["key"] == d.get("stage_key")), None)
        nxt = active[idx + 1] if idx is not None and idx + 1 < len(active) else None
        # The meeting says where the deal is now: an invite titled "second meeting" moves a first-meeting deal on.
        title = str(d.get("last_met_title") or "").lower()
        implied = None
        for s_ in (active[idx + 1:] if idx is not None else []):
            names = [s_["name"].lower(), s_["key"].replace("_", " ")] + [a for a in (ctx["stage_map"].get("crm_aliases") or {}).get(s_["key"], [])
                                                                         if len(a) > 3]
            if any(re.search(rf"\b{re.escape(n)}\b", title) for n in names):
                implied = s_
                break
        # The CRM's step stays in the form only when it is still ahead: a step due by the meeting, or one that names
        # the meeting itself ("Second meeting"), was that meeting.
        step = str(d.get("next_step") or "").strip()
        step_due = str(d.get("next_step_due") or "")[:10]
        was_meeting = bool(step) and (bool(step_due) and step_due <= met or bool(implied) and
                                      re.search(rf"\b{re.escape(implied['name'].lower())}\b", step.lower()) is not None or
                                      re.search(r"\b(meeting|call|catch[- ]?up|intro)\b", step.lower()) is not None and bool(title) and
                                      any(w in title for w in re.findall(r"[a-z]{5,}", step.lower())))
        out.append({"deal_id": did, "company": d.get("company"), "met_on": met, "next_step": d.get("next_step"),
                    "next_step_due": d.get("next_step_due"), "stage": d.get("stage"), "stage_key": d.get("stage_key"),
                    "next_stage": {"key": nxt["key"], "name": nxt["name"]} if nxt else None,
                    "implied_stage": {"key": implied["key"], "name": implied["name"]} if implied else None,
                    "meeting": d.get("last_met_title"), "aid": f"ns_{did}_{met}", "step_was_meeting": was_meeting,
                    # A date already gone is never offered again: the form asks for a new one.
                    "prefill": "" if was_meeting else step,
                    "prefill_due": "" if was_meeting or not step_due or step_due <= met or step_due < ctx["now"].date().isoformat() else step_due,
                    "source_url": d.get("source_url")})
    out.sort(key=lambda r: r["met_on"], reverse=True)
    return out[:5]


def _letter_inputs(snaps: dict[str, Any], ctx: dict[str, Any] | None = None) -> dict[str, Any]:
    """What the quarterly letter is drafted from: the fund's figures, each portfolio company's latest month against
    plan, the flags with their figures, the deals that became investments this quarter and the live pipeline by stage,
    each with its source. Quiet deals never reach it."""
    lps = snaps.get("lps") or {}
    port = snaps.get("portfolio") or {}
    kpis = port.get("kpis") or {}
    rows = []
    for cid, c in (port.get("companies") or {}).items():
        last = (kpis.get(cid) or [{}])[-1] if kpis.get(cid) else {}
        if last:
            rows.append({"company": c.get("name"), "month": last.get("month"), "revenue_usd": last.get("revenue_usd"),
                         "plan_revenue_usd": last.get("plan_revenue_usd"), "cash_usd": last.get("cash_usd"), "burn_usd": last.get("burn_usd"),
                         "source_url": last.get("source_url") or c.get("source_url")})
    lp_link = next((l.get("source_url") for l in (lps.get("lps") or {}).values() if isinstance(l, dict) and l.get("source_url")), None)
    # Committed and called only: a paid-in figure would tell every LP that someone has not paid.
    out = {"funds": [{**{k_: v_ for k_, v_ in f.items() if "paid" not in k_}, "source_label": "LP list", "source_url": f.get("source_url") or lp_link}
                     for f in lps.get("funds") or []],
           "portfolio": rows[:15],
           "flags": [{"company": f.get("company"), "headline": f.get("headline"), "detail": f.get("detail"), "source_url": f.get("source_url")}
                     for f in port.get("flags") or []][:8]}
    if ctx:
        now_ = ctx["now"]
        q_start = now_.date().replace(month=((now_.month - 1) // 3) * 3 + 1, day=1)
        prev_start = (q_start.replace(year=q_start.year - 1, month=10) if q_start.month == 1 else q_start.replace(month=q_start.month - 3))
        out["new_investments"] = [{"company": d.get("company_name"), "entered": d["stage_entered_dt"].date().isoformat(), "round": d.get("round"),
                                   "round_size_usd": d.get("raise_usd"), "source_url": d.get("url")}
                                  for d in ctx["deals"] if d.get("stage_key") == "portfolio" and d.get("stage_entered_dt") and not d.get("quiet")
                                  and prev_start <= d["stage_entered_dt"].date() < q_start + timedelta(days=92)][:6]
        stages_ = {}
        for d in ctx["deals"]:
            st_ = ctx["stage_map"]["by_key"].get(d.get("stage_key"), {})
            if st_.get("active") and not d.get("quiet"):
                stages_[st_.get("name")] = stages_.get(st_.get("name"), 0) + 1
        out["pipeline"] = {"open_deals": sum(stages_.values()), "by_stage": stages_, "source_label": "CRM"}
    return out


def _why_pass(r: dict[str, Any], thesis_: dict[str, Any]) -> str | None:
    """The one reason that decided a pass, in words a founder can take: what we never back, then where, then the round,
    then the sector. Never a score."""
    texts = [str(x.get("text") or "") for x in r.get("reasons") or [] if not x.get("ok")]
    for t in texts:
        if t.startswith("Anti-pattern:"):
            return f"we do not invest in {t.split(':', 1)[1].strip()}"
    for t in texts:
        if t.startswith("Outside our geographies"):
            where = thesis.where_we_invest(thesis_.get("geographies") or [])
            return "it is outside where we invest" + (f": we back {where}" if where else "")
    for t in texts:
        if t.startswith(("Later stage", "Later than our stage")):
            return "the round is later and larger than the ones we lead"
    for t in texts:
        if t.startswith(("Outside thesis sectors", "Adjacent to thesis")):
            return "it sits outside the sectors we invest in"
    for t in texts:
        if "check size" in t:
            return "the round does not fit our check size"
    return None


def _ask_for(r: dict[str, Any]) -> list[str]:
    """The facts an "ask for more" reply asks for: what the score lacked, in plain words, never a reason we hold."""
    texts = [str(x.get("text") or "") for x in r.get("reasons") or []]
    out = []
    if any(t.startswith("Stage unknown") for t in texts):
        out.append("which stage you are at")
    if any(t.startswith("Round size not stated") for t in texts):
        out.append("how much you are raising, and from whom")
    if any(t.startswith("Adjacent to thesis") for t in texts):
        out.append("which banks, lenders or other financial firms use it today")
    if not any(t.startswith("Signals:") for t in texts):
        out.append("who pays for it today, and roughly how much")
    return out[:3]


def _next_check(now, config) -> str:
    """The next scheduled run in words: "10:22", "tomorrow 06:22" or "Mon 06:22"."""
    nxt = schedules.next_run(config, now)
    if nxt.date() == now.date():
        return nxt.strftime("%H:%M")
    if nxt.date() == now.date() + timedelta(days=1):
        return "tomorrow " + nxt.strftime("%H:%M")
    return nxt.strftime("%a %H:%M")


def _new_breaches(brief: dict[str, Any], home: dict[str, Any]) -> list[str]:
    before = set()
    old = home["snap"].get("brief") or {}
    if (old.get("hero") or {}).get("item_id"):
        before.add(old["hero"]["item_id"])  # the hero Home showed is not news an hour later
    for sec in (old.get("sections") or []):
        for it in (sec.get("items") or []):
            if it.get("breach"):
                before.add(it["id"])
    now = [it["id"] for sec in brief["sections"] for it in sec["items"] if it.get("breach")]
    return [i for i in now if i not in before]


# A build run by hand records the job it did, so the scheduled run that day does not do it again.
BY_HAND_JOBS = {"daily": ["morning_brief"], "setup": ["setup", "morning_brief"], "week_ahead": ["week_ahead"],
                "review": ["pipeline_review"], "digest": ["monday_digest"], "weekend": ["weekend_pulse"]}
OUTCOME = brief_mod.OUTCOME

DIGEST_TITLE = {"review": "Weekly pipeline review", "preread": "Partner meeting pre-read", "week_ahead": "Your week ahead",
                "digest": "Monday digest"}
ALLOWED_CRM_FIELDS = {"stage", "next_step", "next_step_due", "note", "notes", "round", "amount", "last_contact"}
NO_PROPOSAL_TYPES = ("draft", "next_step")  # typed or tapped by the user in Home itself


def _plain_ask(text: str) -> str:
    """ "Intro to two banks" reads "An introduction to two banks"; "intros to" reads "introductions to"."""
    t = re.sub(r"\bintros to\b", "introductions to", text, flags=re.I)
    t = re.sub(r"\b(an )?intro to\b", "an introduction to", t, flags=re.I)
    return t[:1].upper() + t[1:] if text[:1].isupper() else t


def _merge_asks(home: dict[str, Any], new: list[dict[str, Any]] | None, now, item_state: dict[str, Any]) -> dict[str, Any]:
    """Founder asks live in their own document, so a build never wipes them. Each needs a source link."""
    stored = dict((((home["snap"].get("asks") or {}).get("items")) or {}))
    for a in new or []:
        if not isinstance(a, dict) or not str(a.get("ask") or "").strip() or not a.get("source_url"):
            continue
        key = sid("ask", a.get("company_id") or a.get("company"), str(a["ask"]).strip().lower()[:60], prefix="a")
        prev = stored.get(key) or {}
        stored[key] = {"company": a.get("company"), "company_id": a.get("company_id"), "ask": clip(_plain_ask(str(a["ask"]).strip()), 140),
                       "who": a.get("who"), "kind": a.get("kind") or "other", "date": a.get("date") or now.date().isoformat(),
                       "source_label": a.get("source_label") or "Founder update", "source_url": a.get("source_url"),
                       "id": key, "item_id": brief_mod.item_id("ask", key), "status": prev.get("status", "open"),
                       "seen_at": prev.get("seen_at") or now.isoformat(),
                       **{k_: prev[k_] for k_ in ("made_on", "paths", "warning_to", "notes", "replied") if prev.get(k_)}}
    today = now.date()
    out = {}
    for key, a in stored.items():
        if a.get("ask"):
            a = {**a, "ask": _plain_ask(str(a["ask"]))}
        st = item_state.get(a.get("item_id")) or {}
        if st.get("done_at"):
            a = {**a, "status": "done", "done_at": st["done_at"]}
        asked = parse_date(a.get("date"))
        done = parse_date(a.get("done_at"))
        last_note = max((parse_date(str(n.get("at") or "")[:10]) for n in a.get("notes") or [] if isinstance(n, dict)
                         and parse_date(str(n.get("at") or "")[:10])), default=None)
        if (done and (today - done).days > 14) or (asked and (today - asked).days > 60 and not (last_note and (today - last_note).days <= 30)):
            continue  # an old ask leaves, unless a note for it went out in the last month
        out[key] = a
    return out


def _nudge_moot(d: dict[str, Any], asks: dict[str, Any] | None, taps: set[str] | None = None) -> bool:
    """A nudge waiting to be sent chases nothing once every ask it names was made or closed, got a later note, was
    answered (a reply from whoever the note went to, after it went), or got a next note the user tapped (`taps`)."""
    if asks is None:
        return False
    by_item = {a_.get("item_id"): a_ for a_ in asks.values() if isinstance(a_, dict)}
    for tap in list(d.get("action_ids") or []) or [d.get("action_id")]:
        m_ = re.match(r"^(t_[0-9a-f]+)", str(tap or ""))
        a_ = by_item.get(m_.group(1)) if m_ else None
        if not a_ or a_.get("status") == "done" or a_.get("made_on"):
            continue
        notes_ = [n for n in a_.get("notes") or [] if isinstance(n, dict) and n.get("at") and n.get("tap")]
        last_ = max(notes_, key=lambda n: str(n.get("at")), default=None)
        rep_ = a_.get("replied") if isinstance(a_.get("replied"), dict) else {}
        sent_ = {str(n.get("tap")) for n in notes_}
        chose_ = any(t_ for t_ in (taps or set()) if t_.startswith(f"{m_.group(1)}_") and not t_.endswith("_nudge") and t_ not in sent_)
        # A reply that only put off its answer is no answer: the nudge it waits for stays until sent or answered.
        answered_ = _answers(rep_, last_) and not (rep_.get("defers") and str(rep_.get("on") or "") < str(d.get("made_at") or ""))
        if last_ and f"{last_['tap']}_nudge" == tap and not answered_ and not chose_:
            return False
    return True


def _founder(ctx: dict[str, Any], company_id: Any) -> str | None:
    for p in ctx.get("people") or []:
        if company_id and p.get("company_id") == company_id and re.search(r"\b(ceo|founder|co-founder)\b", str(p.get("title") or ""), re.I):
            return p.get("name")
    return None


def _uncertain_actions(home: dict[str, Any]) -> set[str]:
    """Actions a run marked as applying but never recorded: the tool may or may not have acted. Never retried."""
    out: set[str] = set()
    props = ((home["snap"].get("proposals") or {}).get("items") or {})
    for r in home.get("runs") or []:
        for aid in (r.get("applying") or {}):
            if (props.get(aid) or {}).get("status") not in ("applied", "failed"):
                out.add(aid)
    return out


def _off(profile: dict[str, Any], module: str) -> bool:
    return (profile.get("modules") or {}).get(module) in (None, "off")


def _snapshots(ctx, config, profile, the_brief, prep_by_meeting, store, signals, stale, decisions, inbound_rows, flags, boards,
               lp_alerts, decay, resolved, home, port_cos, kpi_map, bundle, people_top=None, applied=None, mode="daily",
               unavailable=None, asks=None, digest=None, new_props=None, new_drafts=None, warnings=None,
               team_lp_alerts=None, asked=None, ask_parts=None) -> dict[str, dict[str, Any]]:
    now_iso = ctx["now"].isoformat()
    team_lp_alerts = team_lp_alerts or []
    unavailable = unavailable or {}
    stale_by = {s["deal_id"]: s for s in stale}
    sig_by = {s["deal_id"]: s for s in signals}
    asked_by = {q["deal_id"]: {"id": q["id"], "person": q.get("person"), "email": q.get("email"), "on": q.get("asked_on"),
                               "question": q.get("question"), "subject": q.get("subject"), "thread_id": q.get("thread_id"),
                               "source_url": q.get("source_url")} for q in asked or []}
    old_deals = ((home["snap"].get("pipeline") or {}).get("deals")) or {}
    # A booked meeting is a next step: the row says so instead of "No next step set".
    next_meet: dict[str, Any] = {}
    for m in ctx["meetings"]:
        st_ = m.get("start")
        if st_ and m.get("external") and ctx["now"] <= st_ <= ctx["now"] + timedelta(days=14):
            for pid in m.get("external_ids") or []:
                cid = (ctx["lookup"].get(pid) or {}).get("company_id")
                if cid and (cid not in next_meet or st_ < next_meet[cid]):
                    next_meet[cid] = st_
    met_lately = pipeline.met_recently(ctx)  # includes what Home carried (ctx["met_carried"])
    met_title: dict[str, str] = {}  # the title of that meeting ("Halo Reconcile: second meeting"): the met log reads its stage from it
    for m in ctx["meetings"]:
        for pid in m.get("external_ids") or []:
            cid = (ctx["lookup"].get(pid) or {}).get("company_id")
            if cid and m.get("start") and met_lately.get(cid) == m["start"] and m.get("title"):
                met_title[cid] = str(m["title"])
    deals = {}
    for d in ctx["deals"]:
        st = ctx["stage_map"]["by_key"].get(d["stage_key"], {})
        if not st.get("active") and not d.get("quiet"):
            continue  # passed, closed and portfolio deals live in the CRM; Home keeps the live pipeline small
        days_in = (ctx["now"].date() - d["stage_entered_dt"].date()).days if d.get("stage_entered_dt") else None
        lc = d.get("last_contact_dt")
        sig = sig_by.get(d["id"]) or {}
        old = old_deals.get(d["id"]) or {}
        deals[d["id"]] = {
            "company": d.get("company_name"), "company_id": d.get("company_id"), "domain": d.get("domain"),
            "stage": stages.label(d["stage_name"]), "stage_key": d["stage_key"], "stage_entered": d.get("stage_entered"), "active": bool(st.get("active")),
            "days_in_stage": days_in, "dwell": stages.dwell(d["stage_key"], ctx["stage_map"], float(config.get("dwell_scale") or 1.0)),
            "owner": d.get("owner_email"), "team": d.get("team") or [], "next_step": d.get("next_step"), "next_step_due": d.get("next_step_due"),
            # The CRM's step is a promise you marked sent: the row says it went, never that it is next.
            "step_went": (lambda w_: w_.isoformat() if w_ else None)(pipeline._sent_step(ctx, d.get("next_step"), d.get("company_id"))),
            "next_meeting": next_meet[d["company_id"]].isoformat() if d.get("company_id") in next_meet else None,
            "last_met": met_lately[d["company_id"]].isoformat() if d.get("company_id") in met_lately else None,
            "last_met_title": met_title.get(d.get("company_id")) or
                              (old.get("last_met_title") if d.get("company_id") in met_lately and
                               old.get("last_met") == met_lately[d["company_id"]].isoformat() else None),
            "last_contact": lc.date().isoformat() if lc else None, "last_contact_days": (ctx["now"] - lc).days if lc else None,
            "crm_last_contact": str(d.get("last_contact"))[:10] if d.get("last_contact") else None, "raise_usd": d.get("raise_usd"),
            "partner": pipeline.sponsor(ctx, d),
            "stale": d["id"] in stale_by, "stale_reasons": [r["text"] for r in stale_by.get(d["id"], {}).get("reasons", [])],
            "competing": bool(sig), "competing_evidence": sig.get("evidence"), "competing_source_url": sig.get("source_url"),
            # A colleague's shared note summarises the founder; only words from the founder's own email go in quotes.
            "competing_summary": bool(old.get("competing_summary")) if sig.get("carried") else bool(sig.get("shared")),
            "competing_said_by": sig.get("said_by") or (old.get("competing_said_by") if old.get("competing") else None),
            "competing_phrase": pipeline.signal_phrase(sig) if sig else None,
            "competing_id": sig.get("id"), "competing_labels": sig.get("labels") or [], "competing_funds": sig.get("funds") or [],
            # Shared to the CRM once stays shared: a run that reads no CRM notes never offers to share it again.
            "competing_shared": bool(sig) and bool(sig.get("shared") or sig.get("in_crm") or old.get("competing_shared")),
            "competing_since": (old.get("competing_since") if old.get("competing") else None) or (sig.get("date") if sig else None),
            "deadline": sig.get("deadline"), "deadline_gap": pipeline.deadline_gap(d, sig.get("deadline"), ctx["now"].date()) if sig else None,
            "quiet": bool(d.get("quiet")), "round": d.get("round"),
            # A founder's question with nothing from the firm since: the row says who waits on you, and since when.
            "asked": asked_by.get(d["id"]),
            "source_url": d.get("url"), "from_home": bool(d.get("from_home")),
        }
        # Empty fields are left out: a large pipeline stays well under the document cap.
        deals[d["id"]] = {k: v for k, v in deals[d["id"]].items() if v not in (None, "", [], False) or k in ("days_in_stage",)}
    stale_ids = {x["deal_id"] for x in decisions}
    needs_call = list(decisions) + [{"deal_id": s["deal_id"], "company": s["company"], "why": ", ".join(r["text"] for r in s["reasons"][:1])}
                                    for s in stale if s["deal_id"] not in stale_ids and
                                    s["stage_key"] in ("diligence", "partner_meeting", "term_sheet", "closing")]
    active = [d for d in deals.values() if d.get("active")]
    if profile.get("level") == "analyst":
        # An analyst's week is their own deals and the inbound queue, not the partners' decisions.
        me = ctx["user_email"]
        mine = {did for did, d in deals.items() if d.get("active") and (d.get("owner") == me or me in (d.get("team") or []))}
        own_needs = [{"deal_id": s_["deal_id"], "company": s_["company"], "breach": True, "deadline": s_.get("deadline"),
                      "why": pipeline.signal_phrase(s_) + (f", decide by {fmt_short_date(parse_date(s_['deadline']))}" if s_.get("deadline") else "")}
                     for s_ in signals if s_["deal_id"] in mine] + \
                    [{"deal_id": s_["deal_id"], "company": s_["company"], "why": s_["reasons"][0]["text"]} for s_ in stale
                     if s_["deal_id"] in mine and s_["deal_id"] not in {x["deal_id"] for x in signals}]
        calls = [r for r in inbound_rows if r.get("decision") == "call" and not r.get("pass_log")]
        if own_needs:
            needs_call = own_needs
        elif calls:
            needs_call = [{"deal_id": None, "company": calls[0]["company"], "why": f"book a call, score {calls[0]['score']}"}]
    if _off(profile, "pipeline"):
        pipe_hero = {"statement": "Pipeline is not part of your setup", "finding": "Turn it on in Settings if you want it here.",
                     "deal_id": None, "breach": False, "off": True}
    elif not active and "crm" in unavailable:
        pipe_hero = {"statement": "Your CRM could not be read", "finding": "Reconnect it in Settings. ant. will try again next hour.",
                     "deal_id": None, "breach": False, "unavailable": True}
    elif needs_call:
        # The same order as Today: the deal Today ranks highest leads here too.
        rank_of = {did: i for i, did in enumerate(the_brief.get("ranked_deal_ids") or [])}
        needs_call = sorted(needs_call, key=lambda x: (rank_of.get(x.get("deal_id"), 999), 0 if x.get("breach") else 1))
        top = needs_call[0]
        more = len(needs_call) - 1
        if profile.get("level") == "analyst":
            finding = f"{more} more of your deals {'needs' if more == 1 else 'need'} a look" if more else "The one deal of yours that needs a look"
        else:
            finding = f"{more} more {'deal needs' if more == 1 else 'deals need'} you this week" if more else "The one deal that needs you this week"
        # Hero grammar: the statement is the company and its first fact; the deadline gap and the count go below it.
        first, _, rest = str(top.get("why") or "needs a decision").partition(". ")
        if rest:
            finding = f"{rest.rstrip('.')}. {finding}"
        if top.get("deadline"):
            first = re.sub(r",\s*decide by \d{1,2} \w{3}\.?$", "", first.rstrip("."))  # the kicker carries the date
        names_ = {f_ for s_ in signals for f_ in s_.get("funds") or []} | {str(c_.get("name") or "") for c_ in (ctx.get("companies") or {}).values()} | \
            {str(p_.get("name") or "").split(" ")[0] for p_ in ctx.get("people") or []}
        pipe_hero = {"statement": f"{top['company']}: {_lower(first.rstrip('.'), names_)}", "finding": finding,
                     "deal_id": top["deal_id"], "breach": bool(top.get("breach")), "count": len(needs_call),
                     "deadline": top.get("deadline")}
    elif active:
        pipe_hero = {"statement": "Every active deal has a next step", "finding": "ant. checks again within the hour.", "deal_id": None,
                     "breach": False}
    else:
        pipe_hero = {"statement": "No active deals yet", "finding": "Deals appear here from your CRM.", "deal_id": None, "breach": False}
    if "crm" in unavailable and active:
        pipe_hero["finding"] += ". Your CRM could not be read this hour, so this is what ant. last saw"
    top = people_top if people_top is not None else network.top_people(ctx, 150)
    if decay:
        r0 = decay[0]
        tag = " (portfolio)" if r0.get("company_status") == "portfolio" else ""
        people_hero = {"statement": f"Reconnect with {r0['name']}", "finding": f"{plural(r0['days_since'], 'day')} since you spoke" +
                       (f", {r0['company']}{tag}" if r0.get("company") else "") + f". Strength down from {r0.get('strength_was', r0['strength'])} to {r0['strength']}",
                       "person_id": r0["person_id"], "name": r0["name"], "source_url": r0.get("source_url")}
    elif top:
        people_hero = {"statement": "Your top relationships are warm", "finding": "No one in your top 50 has gone quiet for 60 days.", "person_id": None}
    else:
        people_hero = {"statement": "No relationships yet", "finding": "People appear once ant. has read your mail and calendar.", "person_id": None}
    kpi = portfolio.kpi_table(port_cos, kpi_map)
    companies = {}
    for c in port_cos:
        cflags = [f for f in flags if f["company_id"] == c["id"]]
        companies[c["id"]] = {**kpi.get(c["id"], {"name": c.get("name")}), "domain": c.get("domain"), "flags": cflags,
                              "board": next((b for b in boards if b["company_id"] == c["id"]), None), "source_url": c.get("url")}
    first_board = next((b for b in boards if flags and b["company_id"] == flags[0]["company_id"]), None)
    has_kpis = any(kpi_map.get(c["id"]) for c in port_cos)
    if _off(profile, "portfolio"):
        port_hero = {"statement": "Portfolio is not part of your setup", "finding": "Turn it on in Settings if you want it here.",
                     "company_id": None, "breach": False, "off": True}
    elif flags:
        port_hero = {"statement": f"{flags[0]['company']}: {flags[0]['headline']}",
                     "finding": flags[0]["detail"] + (f". Board meeting {fmt_short_date(parse_dt(first_board['start']))}" if first_board else ""),
                     "company_id": flags[0]["company_id"], "breach": flags[0].get("breach", False),
                     "source_url": flags[0].get("source_url"), "source_label": "Founder update"}
    elif not port_cos:
        port_hero = {"statement": "No portfolio companies found", "finding": "Mark companies as portfolio in your CRM and they appear here.",
                     "company_id": None, "breach": False}
    elif not has_kpis:
        port_hero = {"statement": "No founder updates read yet", "finding": "ant. reads them as they arrive, and on Monday mornings.",
                     "company_id": None, "breach": False}
    else:
        port_hero = {"statement": "No portfolio flags this week", "finding": "Updates read and checked.", "company_id": None, "breach": False}
    open_asks_ = sorted((a for a in (asks or {}).values() if a.get("status") != "done"), key=lambda a: str(a.get("date") or ""), reverse=True)
    ask_hero = _ask_hero(open_asks_, ask_parts or {}, ctx)
    if (profile.get("modules") or {}).get("portfolio") == "asks" and open_asks_:
        # Platform's Portfolio leads with the ask that needs the user now, and says where it stands; finance flags stay
        # below for the board owner.
        port_hero = {**ask_hero, "company_id": ask_hero.get("company_id"), "breach": False}
    lps_map = {}
    every_alert = lp_alerts + team_lp_alerts
    for l in (bundle.get("lps") or []):
        last = lp.last_touch(ctx, l)
        called = l.get("called_usd") if isinstance(l.get("called_usd"), (int, float)) else None
        paid = l.get("paid_in_usd") if isinstance(l.get("paid_in_usd"), (int, float)) else called
        _, owner_name = lp.owner_of(ctx, l)
        lps_map[l["id"]] = {"name": l.get("name"), "fund": l.get("fund"), "commitment_usd": l.get("commitment_usd"),
                            "called_usd": called, "paid_in_usd": paid, "last_call_date": l.get("last_call_date"),
                            "owner": norm_email(l.get("owner")) or None,
                            "unfunded_usd": (l.get("commitment_usd") or 0) - called if called is not None else None,
                            "outstanding_usd": called - paid if called is not None and paid is not None and called - paid >= 1 else None,
                            "owner_name": owner_name, "reup_window_start": l.get("reup_window_start"),
                            "reup_window_end": l.get("reup_window_end"), "last_touch": last.isoformat() if last else None,
                            "days_since": (ctx["now"].date() - last).days if last else None, "contacts": l.get("contacts") or [],
                            "alert": next((a for a in every_alert if a["lp_id"] == l["id"]), None), "source_url": l.get("source_url")}
    if _off(profile, "lp"):
        lp_hero = {"statement": "LPs are not part of your setup", "finding": "Turn them on in Settings if you want them here.",
                   "lp_id": None, "breach": False, "off": True}
    elif lp_alerts:
        a0 = lp_alerts[0]
        if a0.get("kind") == "call":
            lp_hero = {"kicker": "Capital call", "statement": f"{a0['name']} owes {money(a0['outstanding_usd'])} on a capital call",
                       "finding": a0["text"][:1].upper() + a0["text"][1:]}
        else:
            lp_hero = {"statement": f"{a0['name']} is due a touch", "finding": a0["text"]}
        lp_hero.update({"lp_id": a0["lp_id"], "alert_id": a0["id"], "name": a0["name"], "breach": a0["breach"],
                        "source_url": a0.get("source_url")})
    elif not lps_map:
        lp_hero = {"statement": "LP data could not be read" if "lps" in unavailable else "No LP list connected",
                   "finding": "Add your LP list in Settings: a sheet in Drive or your CRM.", "lp_id": None, "breach": False}
    elif team_lp_alerts:
        owners = sorted({a["owner_name"] for a in team_lp_alerts})
        call = next((a for a in team_lp_alerts if a.get("kind") == "call"), None)
        if call:
            # Money the fund is owed leads, even when a colleague owns the LP: never "all in touch" above it.
            lp_hero = {"kicker": "Capital call · with " + str(call["owner_name"]).split(" ")[0],
                       "statement": f"{call['name']} owes {money(call['outstanding_usd'])} on a capital call",
                       "finding": f"{call['owner_name']} owns this LP, so the note is theirs to write. Every LP you own is in touch.",
                       "lp_id": None, "breach": True, "source_url": call.get("source_url")}
        else:
            lp_hero = {"statement": "Every LP you own is in touch",
                       "finding": " and ".join(owners) + (" owns" if len(owners) == 1 else " own") +
                                  f" the {plural(len(team_lp_alerts), 'LP')} that need something: " +
                                  ", ".join(a["name"] for a in team_lp_alerts), "lp_id": None, "breach": False}
    else:
        lp_hero = {"statement": "Every LP is in touch", "finding": "No LP is past its touch window.", "lp_id": None, "breach": False}
    # Proposals: approvals and what this run applied with a tool. Resolved ones older than 30 days drop off, oldest first.
    old_props = (home["snap"].get("proposals") or {}).get("items") or {}
    actions = ((home["state"].get("actions") or {}).get("items") or {})
    uncertain = _uncertain_actions(home)
    props = {}
    for pid_, p in old_props.items():
        p = dict(p)
        act = actions.get(pid_)
        if act and act.get("status") == "approved" and p.get("status") == "proposed":
            p["status"] = "approved"
        if act and act.get("status") == "withdrawn" and p.get("status") == "approved":
            p["status"] = "proposed"
        if pid_ in uncertain and p.get("status") == "approved":
            p.update({"status": "check", "reason": "A run stopped while applying this. Check the record before you approve it again."})
        resolved_at = parse_dt(p.get("applied_at"))
        if p.get("status") in ("applied", "failed", "dismissed") and resolved_at and (ctx["now"] - resolved_at).days > 30:
            continue
        props[pid_] = p
    # A competing fund on a deal you own or work on: offer to share it to the CRM deal, so every partner's ant.
    # reads the same fact and the sync pack is the same for everyone. One tap; never shared without it.
    me = norm_email(ctx["user_email"])
    shared_deals = {n.get("deal_id") for n in ((bundle.get("crm") or {}).get("notes") or []) if pipeline.SHARED_NOTE.match(str(n.get("text") or ""))}
    shared_deals |= {did for did, d in old_deals.items() if d.get("competing_shared")}
    shared_deals |= {(p.get("record") or {}).get("id") for k, p in old_props.items() if k.startswith("share_") and isinstance(p, dict)}
    deal_by = {d["id"]: d for d in ctx["deals"]}
    if not _off(profile, "pipeline") and profile.get("level") != "solo_gp":
        for sig in signals:
            d = deal_by.get(sig["deal_id"]) or {}
            mine_ = d.get("owner_email") == me or me in {norm_email(t) for t in d.get("team") or [] if isinstance(t, str)}
            pid_ = f"share_{sig['id']}"
            if not mine_ or sig.get("shared") or sig.get("in_crm") or sig.get("carried") or d.get("quiet") or sig["deal_id"] in shared_deals or pid_ in old_props:
                continue
            new_props = {**(new_props or {}), pid_: {
                "type": "crm_update", "title": "share the competing fund with your partners",
                "record": {"type": "deal", "id": sig["deal_id"], "name": sig.get("company")},
                "fields": [{"field": "note", "current": None, "proposed": pipeline.shared_note(sig)}],
                "source_label": "Email", "source_url": sig.get("source_url")}}
    # Proposals written this run (post-meeting CRM changes, next steps, holds): shown in Home for the user's tap.
    for pid_, p in (new_props or {}).items():
        if not isinstance(p, dict) or p.get("type") not in ("crm_update", "calendar_hold") or not p.get("source_url"):
            (warnings if warnings is not None else []).append(f"Proposal {pid_} left out: it needs a type and a source link.")
            continue
        bad = [f.get("field") for f in p.get("fields") or [] if isinstance(f, dict) and f.get("field") not in ALLOWED_CRM_FIELDS]
        if p["type"] == "crm_update" and (bad or not p.get("fields")):
            (warnings if warnings is not None else []).append(f"Proposal {pid_} left out: fields ant. does not change ({', '.join(map(str, bad)) or 'none'}).")
            continue
        if (props.get(pid_) or {}).get("status") not in (None, "proposed"):
            continue  # already decided or applied: never reopen it
        if p["type"] == "crm_update" and (p.get("record") or {}).get("type") == "deal":
            # A change the CRM already holds is not a proposal: Beacon already at Term Sheet asks for no tap.
            deal = next((d for d in ctx["deals"] if d["id"] == (p.get("record") or {}).get("id")), None)
            if deal:
                def holds(f: dict[str, Any]) -> bool:
                    name, want = f.get("field"), f.get("proposed")
                    if name == "stage":
                        return stages.map_stage(str(want or ""), ctx["stage_map"]) == deal.get("stage_key")
                    if name in ("next_step", "next_step_due", "last_contact"):
                        return str(deal.get(name) or "").strip().lower()[:200] == str(want or "").strip().lower()[:200]
                    return False
                kept = [f for f in p.get("fields") or [] if isinstance(f, dict) and not holds(f)]
                if not kept:
                    continue
                p = {**p, "fields": kept}
        props[pid_] = {**p, "status": "proposed", "proposed_at": now_iso}
    # A Google Sheet as the CRM: scheduled checks cannot write to it, so a CRM change is a suggestion the user pastes in.
    if str(config.get("crm_system") or "").lower() == "sheet":
        for p in props.values():
            if p.get("type") == "crm_update" and p.get("status") == "proposed":
                p["by_hand"] = True
    for aid, res in (applied or {}).items():
        act = actions.get(aid) or {}
        name_, title_ = _tap_label(act, ctx)
        row = dict(props.get(aid) or {"type": act.get("type"), "title": title_, "record": {"name": name_} if name_ else None})
        row.update({"status": res.get("status", "applied"), "reason": res.get("reason"), "skipped": res.get("skipped") or [],
                    "already": res.get("already") or [], "applied_at": now_iso})
        props[aid] = row
    # The CRM is read after taps are applied, so a deal it sends still holding a step this run just replaced means the
    # read came first, or the write did not land: say so once, so nobody trusts either side blindly.
    read_deals = {d.get("id"): d for d in ((bundle.get("crm") or {}).get("deals") or []) if isinstance(d, dict) and not d.get("from_home")}
    for aid, res in (applied or {}).items():
        act = actions.get(aid) or {}
        pay = act.get("payload") or {}
        d_ = read_deals.get(pay.get("deal_id")) if act.get("type") == "next_step" and (res or {}).get("status", "applied") == "applied" else None
        new_ = str(pay.get("text") or "").strip()
        old_ = str(pay.get("current") or "").strip()
        if not d_ or warnings is None:
            continue
        name_w = d_.get("company_name") or pay.get("company") or "A deal"
        held_ = str(d_.get("next_step") or "").strip()
        # Each part of the tap the read contradicts: a step it replaced or cleared, a stage it moved, a meeting it logged.
        said_ = []
        if old_ and held_ == old_ and ((new_ and new_ != old_) or (not new_ and pay.get("clear_step"))):
            said_.append(f"the old next step (\"{old_}\")")
        st_new = stages.map_stage(str(pay.get("stage") or ""), ctx["stage_map"]) if pay.get("stage") else None
        st_read = stages.map_stage(str(d_.get("stage") or d_.get("stage_name") or ""), ctx["stage_map"]) if (d_.get("stage") or d_.get("stage_name")) else None
        if st_new and st_read and st_new != st_read:
            said_.append(f"the old stage ({d_.get('stage') or d_.get('stage_name')})")
        met_ = parse_date(pay.get("met"))
        lc_ = parse_date(d_.get("last_contact"))
        if met_ and lc_ and lc_ < met_:
            said_.append(f"a last contact of {fmt_short_date(lc_)}, before the {fmt_short_date(met_)} meeting you logged")
        if said_:
            warnings.append(f"{name_w}: this run's CRM read still shows {brief_mod._and(said_)} after ant. applied yours. Check the record.")
    snaps = {
        "brief": the_brief,
        "prep": {"as_of": now_iso, "cards": prep_by_meeting},
        "pipeline": {"as_of": now_iso, "scope": profile["pipeline_scope"], "deals": deals, "hero": pipe_hero,
                     "stages": [{"key": s["key"], "name": s["name"]} for s in ctx["stage_map"]["stages"] if s["active"]],
                     "met_prompts": _met_prompts(ctx, deals, home, props)},
        "people": {"as_of": now_iso, "top": top, "decay": decay, "hero": people_hero},
        "portfolio": {"as_of": now_iso, "companies": companies, "flags": flags, "boards": boards, "hero": port_hero, "kpis": kpi_map},
        # LP commitments and calls stay out of the Home of a role without the LP view: an associate's page holds none.
        "lps": ({"as_of": now_iso, "lps": {}, "alerts": [], "team_alerts": [], "hero": None, "funds": [], "off": True} if _off(profile, "lp") else
                {"as_of": now_iso, "lps": lps_map, "alerts": lp_alerts, "team_alerts": team_lp_alerts, "hero": lp_hero,
                 "funds": lp.fund_summary(bundle.get("lps") or [], bundle.get("firm"), ctx["now"].date(),
                                          ((home["snap"].get("lps") or {}).get("funds")) or [])}),
        "commitments": {"as_of": now_iso, "items": {c["id"]: c for c in store}, "notes": ctx.get("notes_by_event") or {},
                        "sent_steps": ctx.get("sent_steps") or {}},
        "inbound": {"as_of": now_iso, "items": {r["id"]: r for r in inbound_rows}},
        "review": {"as_of": now_iso, "items": resolved["needs_review"][:20]},
        "proposals": {"as_of": now_iso, "items": props},
    }
    directory = _directory(bundle, home, now_iso)
    if directory:
        snaps["directory"] = directory
    # Drafts: kept until the user marks one sent (then 14 days) or for 30 days; a draft saved again replaces its row.
    stored_drafts = dict((((home["snap"].get("drafts") or {}).get("items")) or {}))
    item_state = ((home["state"].get("items") or {}).get("items")) or {}
    for did, d in (new_drafts or {}).items():
        if not isinstance(d, dict) or not d.get("body") or not d.get("source_url"):
            (warnings if warnings is not None else []).append(f"Draft {did} left out: it needs a body and a source link.")
            continue
        prev_ = stored_drafts.get(did) or {}
        same_ = prev_.get("body") == d.get("body") and prev_.get("made_at")
        stored_drafts[did] = {**d, "made_at": prev_.get("made_at") if same_ else now_iso, "updated_at": now_iso}
    kept = {}
    draft_taps = {k_ for k_, a_ in ((((home["state"].get("actions") or {}).get("items")) or {})).items()
                  if isinstance(a_, dict) and a_.get("status") == "approved" and a_.get("type") == "draft" and
                  (ctx["now"] - (parse_dt(a_.get("at")) or ctx["now"])).days <= TAP_DAYS}
    # A second chase still waiting is moot once the LP answered after it was written.
    lp_replied = {f"{a_['id']}_2": parse_dt((a_.get("replied") or {}).get("on")) for a_ in lp_alerts + (team_lp_alerts or [])
                  if isinstance(a_.get("replied"), dict)}
    for did, d in stored_drafts.items():
        done = parse_dt((item_state.get(did) or {}).get("done_at"))
        made = parse_dt(d.get("made_at"))
        rep_on = lp_replied.get(str(d.get("action_id") or ""))
        if rep_on and not done and made and rep_on > made:
            continue
        if d.get("kind") == "holder" and done and (ctx["now"] - done).days <= 45 and \
                any(h_ in stored_drafts and not (item_state.get(h_) or {}).get("done_at") for h_ in d.get("holds") or []):
            kept[did] = d  # a sent note to a partner is the record of the ask and her answer while a draft it named waits
            continue
        if (done and (ctx["now"] - done).days > 14) or (made and (ctx["now"] - made).days > 30):
            continue
        if d.get("inbound_id") and not done and not d.get("in_gmail") and _met_since(ctx, d.get("to"), made, ctx["now"]):
            continue  # a cold reply to a founder you have since met is moot: the follow-up comes from that meeting
        first_ = parse_dt(d.get("first_made_at") or d.get("made_at"))
        if d.get("inbound_id") and not done and not d.get("in_gmail") and first_ and (ctx["now"] - first_).days > 7:
            continue  # a cold reply a week unsent would read late: it leaves, and the pitch stays on the Pitches list
        if d.get("kind") == "holder" and not done and d.get("holds") and \
                all((item_state.get(h_) or {}).get("done_at") or h_ not in stored_drafts for h_ in d["holds"]):
            continue  # every draft it asked about went out: nothing left to ask
        if d.get("note_kind") == "nudge" and not done and _nudge_moot(d, asks, draft_taps):
            continue  # a later note went out or was tapped for its asks, or they were made, closed or answered: nothing to chase
        kept[did] = d
    if kept or home["snap"].get("drafts"):
        snaps["drafts"] = {"as_of": now_iso, "items": kept}
    # Settings belong to setup, tuning and the settings skill. A build writes config only when Home has none.
    if mode == "setup" or not home["snap"].get("config"):
        snaps["config"] = {**config, "updated_at": now_iso}
    for a_ in (asks or {}).values():
        if not a_.get("who") or str(a_.get("who")).lower() in ("the founder", "founder"):
            a_["who"] = _founder(ctx, a_.get("company_id")) or a_.get("who") or "The founder"
    if asks is not None:
        open_asks = sorted((a for a in asks.values() if a.get("status") != "done"), key=lambda a: str(a.get("date") or ""), reverse=True)
        snaps["asks"] = {"as_of": now_iso, "items": asks,
                         "hero": ({k_: v_ for k_, v_ in _ask_hero(open_asks, ask_parts or {}, ctx).items() if k_ != "company_id"} if open_asks else
                                  {"statement": "No open founder asks", "finding": "Asks from updates and mail appear here.", "ask_id": None})}
    if digest and str(digest.get("markdown") or "").strip():
        items = dict((((home["snap"].get("digests") or {}).get("items")) or {}))
        kind = digest.get("kind") or "review"
        items[kind] = {"kind": kind, "title": DIGEST_TITLE.get(kind, "ant. digest"), "markdown": clip(str(digest["markdown"]), 12000),
                       "as_of": now_iso}
        snaps["digests"] = {"as_of": now_iso, "items": items}
    notes_doc = _notes_snap(bundle, store, home, ctx, now_iso)
    if notes_doc:
        snaps["notes"] = notes_doc
    # Timelines for the side panels: every company, person and LP, each event with its link.
    snaps.update(timeline.merge_snaps(timeline.build(ctx, bundle, store, home, inbound_rows), home, ctx["now"], now_iso, ctx))
    rem = timeline.reminders(home, ctx, snaps, bundle, now_iso)
    if rem:
        snaps["reminders"] = rem
    return snaps


NOTE_HOSTS = (("granola", "Granola"), ("fireflies", "Fireflies"), ("otter", "Otter"), ("fathom", "Fathom"), ("notion", "Notion"),
              ("zoom", "Zoom"), ("meet.google", "Google Meet"), ("docs.google", "Google Docs"), ("tldv", "tl;dv"), ("avoma", "Avoma"))
NOTES_KEEP_DAYS = 30
NOTES_MAX = 40
NOTES_BUDGET = 150_000  # characters across every note, well under the 256 KB a Home doc can hold


def _note_source(url: Any) -> str:
    u = str(url or "").lower()
    return next((label for key, label in NOTE_HOSTS if key in u), "your notes app")


def _notes_snap(bundle, store, home, ctx, now_iso) -> dict[str, Any] | None:
    """Meeting notes for Home's side panel: a TL;DR when the notes app gave one, the promises, and the lines, trimmed.

    Notes are merged across runs (a check that reads no transcripts keeps what Home has) and kept 30 days."""
    old = dict((((home["snap"].get("notes") or {}).get("items")) or {}))
    promises: dict[str, list[dict[str, Any]]] = {}
    for c in store or []:
        tid = c.get("transcript_id")
        if tid and c.get("what"):
            promises.setdefault(str(tid), []).append({"what": clip(str(c["what"]), 200), "by": c.get("owed_by"), "side": c.get("side"),
                                                       "due": c.get("due"), "status": c.get("status") or "open"})
    for tr in bundle.get("transcripts") or []:
        tid = str(tr.get("id") or "")
        if not tid:
            continue
        lines, raw = commit_mod.transcript_lines(tr), tr.get("lines") or []
        summary = tr.get("summary") or tr.get("tldr") or tr.get("notes")
        if isinstance(summary, list):
            summary = "\n".join(f"- {s}" for s in summary if s)
        old[tid] = {
            "id": tid, "event_id": tr.get("event_id"), "title": clip(str(tr.get("title") or "Meeting"), 120), "date": tr.get("date"),
            "url": tr.get("url"), "source": _note_source(tr.get("url")),
            "attendees": [a.get("name") for a in tr.get("attendees") or [] if isinstance(a, dict) and a.get("name")][:12],
            "summary": clip(str(summary), 1500) if summary else (old.get(tid) or {}).get("summary"),
            "lines": [{"t": (raw[i] if i < len(raw) and isinstance(raw[i], dict) else {}).get("t"),
                       "who": l["speaker"], "text": clip(str(l["text"]), 400)} for i, l in enumerate(lines[:160]) if str(l.get("text") or "").strip()],
            "more": max(0, len(lines) - 160),
        }
    if not old:
        return None
    for tid, n in old.items():
        n["promises"] = promises.get(tid, n.get("promises") or [])[:8]
    fresh = [n for n in old.values() if not (parse_dt(n.get("date")) and (ctx["now"] - parse_dt(n["date"])).days > NOTES_KEEP_DAYS)]
    fresh.sort(key=lambda n: str(n.get("date") or ""), reverse=True)
    items, used = {}, 0
    for n in fresh[:NOTES_MAX]:
        size = len(json.dumps(n, default=str))
        if used + size > NOTES_BUDGET:
            n = {**n, "lines": n["lines"][:40], "more": n.get("more", 0) + max(0, len(n["lines"]) - 40)}
            size = len(json.dumps(n, default=str))
            if used + size > NOTES_BUDGET:
                break
        items[n["id"]] = n
        used += size
    return {"as_of": now_iso, "items": items}


def _lower(text: str, names: Any = ()) -> str:
    """A fragment's first letter, lowered to sit after "Company: ", never a name's: "Saffron Peak Capital wants to
    lead", "Bluepeak is moving" and "IC" stay as written."""
    t = str(text or "").strip()
    if not t or t[:2] == t[:2].upper():
        return t
    w = t.split()
    if len(w) > 1 and w[0][:1].isupper() and w[1][:1].isupper():
        return t  # two capitalised words open a name
    if any(n and len(n) > 2 and t.startswith(n) and (len(t) == len(n) or not t[len(n)].isalnum()) for n in names):
        return t
    return t[:1].lower() + t[1:]


def cmd_build(a: argparse.Namespace) -> int:
    bundle = load(a.bundle)
    config = load(a.config)
    home = homedb.read_home(a.home, a.versions)
    extracted = _rows(load(a.extracted), "commitments", "--extracted") if a.extracted else None
    inbound = _rows(load(a.inbound), "pitches", "--inbound") if a.inbound else None
    kpis = load(a.kpis) if a.kpis else None
    applied = load(a.applied) if a.applied else None
    extras: dict[str, Any] = {}
    if a.asks:
        extras["asks"] = _rows(load(a.asks), "asks", "--asks")
    if a.packs:
        extras["packs"] = _rows(load(a.packs), "packs", "--packs")
    for name in ("proposals", "drafts"):
        path = getattr(a, name)
        if path:
            obj = load(path)
            obj = obj.get("items", obj) if isinstance(obj, dict) else {str(x.get("id")): x for x in obj if isinstance(x, dict) and x.get("id")}
            extras[name] = obj
    if a.digest:
        with open(a.digest, encoding="utf-8") as fh:
            extras["digest"] = {"kind": a.digest_kind or "review", "markdown": fh.read()}
    if a.run_id or a.started or a.jobs:
        extras["run"] = {"id": a.run_id, "started": a.started, "jobs": [j for j in (a.jobs or "").split(",") if j]}
    else:
        extras["by_hand"] = True  # a run the user asked for in chat: nothing reaches the phone
    if isinstance(config, dict) and "data" in config and isinstance(config["data"], dict) and "level" not in config:
        config = config["data"]
    res = build_all(bundle, config, home, extracted, inbound, kpis, a.mode, applied, extras)
    os.makedirs(a.out, exist_ok=True)
    plan = homedb.write_plan(res["snaps"], home, a.out)
    dump(res["report"], os.path.join(a.out, "report.json"))
    with open(os.path.join(a.out, "brief.md"), "w", encoding="utf-8") as fh:
        fh.write(res["brief"]["text"] + "\n")
    with open(os.path.join(a.out, "brief-shareable.md"), "w", encoding="utf-8") as fh:
        fh.write(res["brief"]["shareable_text"] + "\n")
    run_file = dump(res["report"]["run_row"], os.path.join(a.out, "home", "run.json"))
    owed_file = dump(res["report"].get("owed") or [], os.path.join(a.out, "owed.json"))
    _emit({"report": {k: v for k, v in res["report"].items() if k not in ("run_row", "owed")},
           "batch_file": os.path.join(os.path.abspath(a.out), "home", "batch.json"), "documents": plan["documents"],
           "skipped_unchanged": plan.get("skipped", []), "run_row_file": run_file,
           "owed_file": owed_file, "owed": len(res["report"].get("owed") or [])})
    return 0


# ---------------------------------------------------------------- single-purpose commands


def _rows(obj: Any, key: str, what: str) -> list[dict[str, Any]]:
    """Accept a bare list or {"<key>": [...]}; anything else is a clear error, not a traceback."""
    if isinstance(obj, dict) and isinstance(obj.get(key), list):
        obj = obj[key]
    if not isinstance(obj, list) or not all(isinstance(x, dict) for x in obj):
        raise SystemExit(f"{what} must be a JSON list of objects (or {{\"{key}\": [...]}}).")
    return obj


def cmd_validate(a: argparse.Namespace) -> int:
    bundle = load(a.bundle)
    firm_domain = ((bundle.get("firm") or {}).get("domain") or "").lower()
    res = commit_mod.validate(_rows(load(a.extracted), "commitments", "--extracted"), (bundle.get("transcripts") or []), firm_domain)
    if a.out:
        dump(res, a.out)
    _emit({"valid": len(res["valid"]), "rejected": res["rejected"]})
    return 0


def cmd_triage(a: argparse.Namespace) -> int:
    rows = thesis.triage(_rows(load(a.inbound), "pitches", "--inbound"), load(a.thesis),
                         _rows(load(a.passes), "passes", "--passes") if a.passes else [])
    if a.out:
        dump(rows, a.out)
    _emit(rows)
    return 0


def cmd_check_injection(a: argparse.Namespace) -> int:
    """Second opinion on embedded instructions: the engine's patterns over each pitch, or over a text file."""
    out = []
    if a.inbound:
        for r in _rows(load(a.inbound), "pitches", "--inbound"):
            blob = " ".join(str(r.get(k) or "") for k in ("body", "text", "sector", "traction", "team", "injection_quote"))
            hits = safety.detect_injection(blob)
            out.append({"company": r.get("name"), "flagged_by_you": bool(r.get("injection_flag")), "engine_hits": hits,
                        "agree": bool(hits) == bool(r.get("injection_flag")) or bool(r.get("injection_flag"))})
    if a.text_file:
        with open(a.text_file, encoding="utf-8") as fh:
            out.append({"file": a.text_file, "engine_hits": safety.detect_injection(fh.read())})
    _emit({"results": out})
    return 0


def cmd_memo(a: argparse.Namespace) -> int:
    _emit(safety.check_memo(load(a.memo), load(a.sources)))
    return 0


def cmd_letter_check(a: argparse.Namespace) -> int:
    """The quarterly letter's sections, checked: which of the template's sections a draft (markdown) still lacks."""
    with open(a.letter, encoding="utf-8") as fh:
        _emit(lp.letter_check(fh.read()))
    return 0


def cmd_intro(a: argparse.Namespace) -> int:
    """The company name comes from a file, never the command line: names read from email can carry shell text."""
    if a.company_file:
        with open(a.company_file, encoding="utf-8") as fh:
            raw = fh.read().strip()
        try:
            obj = json.loads(raw)
            company = obj.get("company") if isinstance(obj, dict) else str(obj)
        except ValueError:
            company = raw
    else:
        company = a.company
    if not company:
        raise SystemExit("Give the company in --company-file (a text or JSON file).")
    ctx = graph_mod.build(load(a.bundle))
    _emit(network.intro_paths(ctx, str(company)[:120]))
    return 0


ENGINE_APPLIED = ("merge", "keep_apart", "quiet", "skip")


def cmd_actions(a: argparse.Namespace) -> int:
    """Approved taps that need a tool call (CRM, calendar, drafts). The engine applies the rest on build."""
    _emit(pending_actions(homedb.read_home(a.home), parse_dt(a.now) if getattr(a, "now", None) else None))
    return 0


TAP_DAYS = 30  # as long as Home keeps what a run did with a tap (its row in snap/proposals)


def pending_actions(home: dict[str, Any], now=None) -> dict[str, Any]:
    """Approved taps for the pulse to apply with a tool. A CRM change or calendar hold is applied only when it
    matches a proposal Home showed, with the proposal's own fields; anything else is refused and said so. A tap older
    than Home's record of what was done with it is never offered again: it was applied a month ago, or let lapse."""
    from datetime import datetime as _dt, timezone as _tz
    raw = (home["state"].get("actions") or {}).get("items") or {}
    # Without a time given (the pulse passes its run's start): the clock, never a guess from Home's own records, which
    # can be old.
    now = now or _dt.now(_tz.utc)
    actions = {k: v for k, v in raw.items()
               if not (isinstance(v, dict) and parse_dt(v.get("at")) and (now - parse_dt(v.get("at"))).days > TAP_DAYS)}
    props = ((home["snap"].get("proposals") or {}).get("items") or {})
    user_email = str(((home["snap"].get("config") or {}).get("user_email")) or "").lower()
    lps_now = (((home["snap"].get("lps") or {}).get("lps")) or {})
    sheet_crm = str(((home["snap"].get("config") or {}).get("crm_system")) or "").lower() == "sheet"
    uncertain = _uncertain_actions(home)
    # Automatic mode (state/settings, set in Home's Help or at setup): a CRM change or calendar hold a run proposed
    # from your own notes applies without a tap, unless you skipped or withdrew it. Each still goes through every check
    # below, and Activity offers Undo.
    settings = ((home["state"].get("settings") or {}).get("items")) or {}
    if settings.get("auto_apply") is True:
        for pid, prop in props.items():
            if pid in actions or not isinstance(prop, dict) or prop.get("status") != "proposed" or prop.get("by_hand"):
                continue
            if prop.get("type") in ("crm_update", "calendar_hold"):
                actions = {**actions, pid: {"type": prop["type"], "status": "approved", "auto": True,
                                            "payload": {"fields": prop.get("fields"), "record": prop.get("record")}}}
    # What the user lets ant. do with each kind of tool (Home, Settings): a CRM or calendar set to read only takes no change.
    access = settings.get("access") if isinstance(settings.get("access"), dict) else {}
    todo, engine, refused, check = [], [], [], []
    for aid, act in actions.items():
        if not isinstance(act, dict) or act.get("status") != "approved":
            continue
        kind = act.get("type")
        if kind in ENGINE_APPLIED:
            engine.append(aid)
            continue
        prop = props.get(aid) or {}
        # A step saved again after its last one was applied is new: it is applied at this run, whatever came before.
        resaved = kind == "next_step" and parse_dt(act.get("at")) and parse_dt(prop.get("applied_at")) and \
            parse_dt(act["at"]) > parse_dt(prop["applied_at"])
        if prop.get("status") in ("applied", "failed", "check", "dismissed", "refused") and not resaved:
            continue
        if kind in ("crm_update", "next_step", "revert") and access.get("crm") in ("read", "off"):
            refused.append({"id": aid, "type": kind, "why": "Your CRM is set to read only in ant. Home's Settings. Change it there to let ant. update it."})
            continue
        if kind == "calendar_hold" and access.get("calendar") in ("read", "off"):
            refused.append({"id": aid, "type": kind, "why": "Your calendar is set to read only in ant. Home's Settings."})
            continue
        if sheet_crm and kind in ("crm_update", "next_step", "revert"):
            refused.append({"id": aid, "type": kind, "why": "Your CRM is a Google Sheet, which ant. cannot write to. Copy the change from Home and paste it in."})
            continue
        if aid in uncertain:
            check.append({"id": aid, "type": kind, "why": "A run stopped while applying this. Check the record; do not apply it again."})
            continue
        if kind == "revert":
            # Undo from Activity: a CRM change ant. applied, put back. Each field goes from what ant. wrote to what was
            # there before, under the same rule (only while the record still holds what ant. wrote). Notes stay: a note
            # added is never deleted.
            of = str((act.get("payload") or {}).get("of") or "")
            orig, orig_act = props.get(of) or {}, actions.get(of) or {}
            if orig.get("type") != "crm_update" or orig.get("status") != "applied":
                refused.append({"id": aid, "type": kind, "why": "Only a CRM change ant. applied can be put back."})
                continue
            back = [{"field": f.get("field"), "current": f.get("proposed"), "proposed": f.get("current")}
                    for f in (orig.get("fields") or []) if isinstance(f, dict) and f.get("field") in ALLOWED_CRM_FIELDS
                    and f.get("field") not in ("note", "notes")]
            if not back:
                refused.append({"id": aid, "type": kind, "why": "A note cannot be taken back. Delete it in the CRM if you need to."})
                continue
            todo.append({"id": aid, "type": "crm_update", "reverts": of, "record": orig.get("record") or (orig_act.get("payload") or {}).get("record"),
                         "fields": back, "rule": "Re-read the record first. Apply a field only if its value still equals `current`; otherwise skip it and say so."})
            continue
        if kind in NO_PROPOSAL_TYPES:
            pay = act.get("payload") or {}
            if kind == "next_step" and not (pay.get("deal_id") and (str(pay.get("text") or pay.get("next_step") or "").strip() or
                                                                    parse_date(pay.get("met")) or str(pay.get("stage") or "").strip())):
                refused.append({"id": aid, "type": kind, "why": "A met log needs a deal and a step, a stage or the date you met."})
                continue
            if kind == "next_step" and pay.get("stage") and re.search(r"\b(pass|passed|closed|lost|won|dead|portfolio)\b", str(pay["stage"]), re.I):
                refused.append({"id": aid, "type": kind, "why": "A next step moves a deal forward, never to passed, lost, won or the portfolio."})
                continue
            ent = pay.get("entity") or {}
            if kind == "draft" and ent.get("type") == "lp":
                # One owner per LP: Home offers a draft only on your own LPs, and a tap from before the owner changed waits.
                owner = norm_email((lps_now.get(ent.get("id")) or {}).get("owner"))
                if owner and owner != user_email:
                    who = str((lps_now.get(ent.get("id")) or {}).get("owner_name") or owner.split("@")[0]).split(" ")[0]
                    refused.append({"id": aid, "type": kind, "why": f"{ent.get('name') or 'This LP'} is {who.capitalize()}'s LP: "
                                                                   f"the note is theirs to write."})
                    continue
            todo.append({"id": aid, "type": kind, "payload": pay, "proposal": prop or None})
            continue
        if kind not in ("crm_update", "calendar_hold"):
            refused.append({"id": aid, "type": kind, "why": "Not an action ant. applies."})
            continue
        if not prop or prop.get("type") != kind or prop.get("status") not in ("proposed", "approved"):
            refused.append({"id": aid, "type": kind, "why": "No matching proposal in Home. ant. applies only what it showed you."})
            continue
        if kind == "crm_update":
            fields = [f for f in (prop.get("fields") or []) if isinstance(f, dict)]
            bad = [f.get("field") for f in fields if f.get("field") not in ALLOWED_CRM_FIELDS]
            if not fields or bad:
                refused.append({"id": aid, "type": kind, "why": "Fields ant. does not change: " + ", ".join(str(b) for b in bad) if bad else
                                "The proposal lists no fields."})
                continue
            todo.append({"id": aid, "type": kind, "record": prop.get("record"), "fields": fields, **({"auto": True} if act.get("auto") else {}),
                         "rule": "Re-read the record first. Apply a field only if its value still equals `current`; otherwise skip it and say so."})
        else:
            others = [e for e in (prop.get("attendees") or []) if str(e).lower() not in ("", user_email)]
            if others:
                refused.append({"id": aid, "type": kind, "why": "A hold may have only you on it."})
                continue
            todo.append({"id": aid, "type": kind, "event": prop.get("event") or {}, "proposal": prop,
                         "rule": "Create it on the user's own calendar with no attendees: an invite would email someone."})
    return {"pending": todo, "applied_by_engine": engine, "refused": refused, "check_by_hand": check,
            "rule": "Before each tool call, mark the action as applying on this run's row. Record every result in applied.json."}


def cmd_questions(a: argparse.Namespace) -> int:
    """Put the three questions you wrote into their prep cards and make sure snap/prep is in the batch."""
    path = os.path.join(os.path.abspath(a.out), "home", "snap__prep.json")
    doc = load(path)
    given = load(a.questions)
    done, refused = [], []
    for mid, qs in (given or {}).items():
        card = (doc.get("cards") or {}).get(mid)
        qs = [str(q).strip() for q in (qs or []) if str(q).strip()]
        if not card:
            refused.append({"meeting_id": mid, "why": "no prep card for this meeting"})
        elif len(qs) != 3 or not all(q.endswith("?") for q in qs):
            refused.append({"meeting_id": mid, "why": "needs exactly three questions, each ending with a question mark"})
        else:
            card["questions"] = qs
            done.append(mid)
    if done:
        dump(doc, path)
        homedb.add_to_plan(a.out, "prep")
    _emit({"written": done, "refused": refused})
    return 0 if not refused else 1


def link_drafts(brief: dict[str, Any], drafts: dict[str, Any], fresh: set[str] | None = None) -> None:
    """Each promise row, the hero and the "You owe" lines under a meeting point at the draft that keeps the promise;
    a founder's waiting question points at the reply that answers it. Drafts written this run (`fresh`) also reach the
    rows the build wrote before them: the letter's row and a capital call's say "Draft ready", a draft with blanks
    says how many lines are left, and asks that went out in one note point at their nudge."""
    by_promise = {cid_: did for did, r in drafts.items() if isinstance(r, dict) for cid_ in _promise_ids(r)}
    by_question = {r["question_id"]: did for did, r in drafts.items() if isinstance(r, dict) and r.get("question_id")}
    hero = brief.get("hero") or {}
    rows = [it for sec in brief.get("sections") or [] for it in sec.get("items") or []]
    for it in rows:
        if it.get("commitment_id") in by_promise:
            it["draft"] = by_promise[it["commitment_id"]]
        elif it.get("question_id") in by_question:
            it["draft"] = by_question[it["question_id"]]
    if hero.get("commitment_id") in by_promise:
        hero["draft"] = by_promise[hero["commitment_id"]]
    elif hero.get("question_id") in by_question:
        hero["draft"] = by_question[hero["question_id"]]
    pool = {k: v for k, v in drafts.items() if isinstance(v, dict) and (fresh is None or k in fresh)}
    new_by_action = {a_: did for did, r in sorted(pool.items(), key=lambda kv: str(kv[1].get("made_at") or ""))
                     for a_ in [r.get("action_id")] + list(r.get("action_ids") or []) if a_}

    def add(it: dict[str, Any], key: str, line: str) -> None:
        if line and line not in str(it.get(key) or ""):
            it[key] = str(it.get(key) or "").rstrip(".") + f". {line}"
    # Rows say it in their detail, the hero in its finding.
    for it, key in [(r_, "detail") for r_ in rows] + ([(hero, "finding")] if hero.get("item_id") else []):
        did = it.get("draft")
        if did in pool and it.get("commitment_id"):
            gaps = draft_gaps(pool[did].get("body"))
            if brief_mod.LETTER.search(str(it.get("title") or it.get("statement") or "")):
                if gaps:
                    it["draft_gaps"] = gaps
                it[key] = str(it.get(key) or "").replace(
                    ". ant. drafts it from the KPI history and the LP list",
                    f". Draft ready: {'fill in ' + plural(gaps, 'line') + ', ' if gaps else ''}check the figures, then send it")
            elif gaps:
                it["draft_gaps"] = gaps
                add(it, key, brief_mod.gaps_line(gaps, it.get("holder")))
        if it.get("kind") == "lp" and it.get("call") and not it.get("draft"):
            hit = new_by_action.get(f"{it.get('alert_id')}_2") or new_by_action.get(it.get("alert_id")) or \
                new_by_action.get(it.get("id") if key == "detail" else it.get("item_id"))
            if hit:
                it["draft"] = hit
                # Written now: the line says it is ready, not that the morning will write it.
                it[key] = str(it.get(key) or "").replace(". The morning brief drafts a second note", "")
                add(it, key, ("Second note ready" if it.get("chased") else "Draft ready") + ": check the amount, then send it")
        if it.get("group_asks") and not it.get("draft"):  # asks that went out in one note: their nudge
            hit = next((new_by_action[f"{g.get('item_id')}{suf}"] for g in it["group_asks"] for suf in ("_nudge", "_intro_nudge", "_team_nudge")
                        if f"{g.get('item_id')}{suf}" in new_by_action), None)
            if hit:
                it["draft"] = hit
                # The row, the hero and the push say the nudge is written from this run on, not an hour later.
                rf = it.get("ready_form") if isinstance(it.get("ready_form"), dict) else {}
                for k_ in ("push_line", "push_lines", "status_word", "ask_state", "state_label"):
                    if rf.get(k_):
                        it[k_] = rf[k_]
                if rf.get("detail"):
                    old_ = str(it.get(key) or "")
                    it[key] = rf["detail"]
                    for tk in ("text", "shareable_text"):  # the copyable brief says the same
                        if old_ and old_ in str(brief.get(tk) or ""):
                            brief[tk] = str(brief[tk]).replace(old_, rf["detail"])
        if it.get("kind") == "ask" and not it.get("group_asks") and not it.get("draft") and it.get("id"):
            # One ask's own nudge, written this run: its row (and the hero) say it is ready from this run on.
            hit = next((new_by_action[f"{it['id']}{suf}"] for suf in ("_nudge", "_intro_nudge", "_team_nudge")
                        if f"{it['id']}{suf}" in new_by_action), None)
            if hit:
                it["draft"] = hit
                it["status_word"], it["state_label"], it["ask_state"] = "ready", "Nudge ready", "ready"
                add(it, key, "Nudge ready")
    by_action = {a_: did for did, r in sorted(drafts.items(), key=lambda kv: str((kv[1] or {}).get("made_at") or "") if isinstance(kv[1], dict) else "")
                 if isinstance(r, dict) for a_ in [r.get("action_id")] + list(r.get("action_ids") or []) if a_}
    for m in brief.get("meetings") or []:  # Home shows "draft ready" beside the line; the brief's own text is unchanged
        ids = m.get("note_ids") or []
        m["note_drafts"] = [(by_action.get(cid[7:]) if str(cid).startswith("action:") else by_promise.get(cid)) if cid else None for cid in ids]


def cmd_drafts(a: argparse.Namespace) -> int:
    """Put the drafts you saved to Gmail this run into Home: snap/drafts gains them, and each promise row (and the
    hero) links to its draft, so Home shows "Draft ready" with Open in Gmail and Copy. Both documents join the batch."""
    out = os.path.abspath(a.out)
    folder = os.path.join(out, "home")
    given = load(a.drafts)
    if isinstance(given, dict):
        given = given.get("items", given)
    else:
        given = {str(x.get("id")): x for x in (given or []) if isinstance(x, dict) and x.get("id")}
    owed_path = os.path.join(out, "owed.json")
    owed = {o["id"]: o for o in (load(owed_path) if os.path.exists(owed_path) else []) if isinstance(o, dict) and o.get("id")}
    bpath = os.path.join(folder, "snap__brief.json")
    brief = load(bpath)
    now_iso = brief.get("as_of")
    dpath = os.path.join(folder, "snap__drafts.json")
    doc = load(dpath) if os.path.exists(dpath) else {"as_of": now_iso, "items": {}}
    doc.setdefault("items", {})
    done, refused = [], []
    # The morning's own mail search found an answer the build missed (owed-kinds: write no nudge or second note): the
    # rows, the heroes and the push say they replied, and Home keeps the reply on the ask or the LP.
    found = {did: d["replied"] for did, d in given.items() if isinstance(d, dict) and isinstance(d.get("replied"), dict) and
             d["replied"].get("on") and not str(d.get("body") or "").strip()}
    answered_docs = _apply_found_replies(out, folder, brief, owed, found) if found else []
    done, refused_rows = draft_rows({k: v for k, v in given.items() if k not in found}, owed, doc["items"], now_iso)
    refused += refused_rows
    link_drafts(brief, doc["items"], set(done))
    push_line = _redo_push_line(out, folder, brief, set(done)) if done else None
    for name_ in answered_docs:
        if not name_.startswith("push:"):
            homedb.add_to_plan(a.out, name_)
    if found and not done:
        dump(brief, bpath)
        homedb.add_to_plan(a.out, "brief")
    if done:
        doc["as_of"] = now_iso
        dump(doc, dpath)
        dump(brief, bpath)
        homedb.add_to_plan(a.out, "drafts")
        homedb.add_to_plan(a.out, "brief")
        for name_ in ("asks", "portfolio"):  # the ask heroes name the nudge as ready too
            if _ready_heroes(os.path.join(folder, f"snap__{name_}.json"), set(done), doc["items"]):
                homedb.add_to_plan(a.out, name_)
    push_line = push_line or (next((x_ for x_ in answered_docs if x_.startswith("push:")), "")[5:] or None)
    _emit({"written": done, "refused": refused, **({"replied": sorted(found)} if found else {}), **({"push_line": push_line} if push_line else {})})
    return 0 if not refused else 1


def draft_rows(given: dict[str, Any], owed: dict[str, Any], items: dict[str, Any], now_iso: str) -> tuple[list[str], list[dict[str, Any]]]:
    """The drafts command's own rows: each draft Claude wrote, laid over Home's row for it (`items`, changed in place)
    with what its owed entry carries (the ids it keeps, a note to a partner's lists, a rewrite's ids). Returns the ids
    written and the ones refused, with why. The replay harness writes its drafts with this too."""
    done, refused = [], []
    doc = {"items": items}
    for did, d in given.items():
        if not isinstance(d, dict) or not str(d.get("body") or "").strip() or not d.get("source_url"):
            refused.append({"id": did, "why": "a draft needs a body and a source link"})
            continue
        if not (d.get("to") or d.get("to_name")):
            refused.append({"id": did, "why": "a draft needs a recipient"})
            continue
        o = owed.get(did) or {}
        prev = doc["items"].get(did) or {}
        row = {**d, "commitment_id": d.get("commitment_id") or o.get("commitment_id"), "inbound_id": d.get("inbound_id") or o.get("inbound_id"),
               "question_id": d.get("question_id") or o.get("question_id"), "action_id": d.get("action_id") or o.get("action_id"),
               "note_kind": d.get("note_kind") or o.get("note_kind"), "action_ids": d.get("action_ids") or o.get("action_ids"),
               "note_kinds": d.get("note_kinds") or o.get("note_kinds")}
        asks_ = [t_.get("commitment_id") for t_ in o.get("they_owe") or [] if isinstance(t_, dict) and t_.get("commitment_id")]
        if o.get("kind") == "narrow" and o.get("received"):
            asks_ = [x_ for x_ in (prev.get("asks_for") or []) if x_ not in {r_.get("commitment_id") for r_ in o["received"]}]
        elif not asks_:
            asks_ = list(prev.get("asks_for") or [])
        if asks_:
            row["asks_for"] = list(dict.fromkeys(asks_))
        elif o.get("kind") == "narrow" and o.get("received"):
            row["asks_for"] = None
        if o.get("kind") == "holder":  # what the note asks about, as this run's entry says (a rebuild can drop some)
            row.update({"kind": "holder", "holds": [w_.get("draft") for w_ in o.get("items") or [] if w_.get("draft")],
                        "decisions": [{k_: x_.get(k_) for k_ in ("deal_id", "company", "deadline", "what")} for x_ in o.get("decisions") or []]})
        elif prev.get("kind") == "holder":
            row.update({"kind": "holder", "holds": prev.get("holds"), "decisions": prev.get("decisions"), "replied": prev.get("replied")})
        # A draft that took in another promise to the same person keeps every promise it carries: each row shows it,
        # and Sent it closes them all. The promise it was first written for stays its own.
        if o.get("kind") == "narrow" and o.get("commitment_ids"):  # a promise in it was closed: only the open ones stay
            prev = {k_: v_ for k_, v_ in prev.items() if k_ not in ("commitment_id", "commitment_ids")}
            row.update({"commitment_id": o.get("commitment_id"), "commitment_ids": list(o["commitment_ids"])})
        cids_ = [x for x in dict.fromkeys(([prev.get("commitment_id")] if (o.get("join") or o.get("commitment_ids")) else []) +
                                          list(prev.get("commitment_ids") or []) + [row.get("commitment_id")] +
                                          list(o.get("commitment_ids") or []) + list(d.get("commitment_ids") or [])) if x]
        if o.get("kind") == "narrow" and o.get("commitment_ids"):
            cids_ = [x for x in cids_ if x in o["commitment_ids"]]
        if len(cids_) > 1:
            row["commitment_ids"] = cids_
            row["commitment_id"] = prev.get("commitment_id") or row.get("commitment_id") or cids_[0]
        if row.get("in_gmail") and not row.get("gmail_url"):
            row["gmail_url"] = "https://mail.google.com/mail/u/0/#drafts"
        # Who set the dates in it, stored, never read from prose: a rewrite that put dates in place (a redate, or a
        # refresh with stale words) chose them, so a later run moves them again rather than keeping a passed one.
        if o.get("kind") in ("redate", "refresh", "reslot") and o.get("words"):
            row["date_set_by"] = "instinct"
        elif prev.get("date_set_by"):
            row["date_set_by"] = prev.get("date_set_by")
        # A draft rewritten (new times, or brought up to date after a meeting) counts as written now.
        same = prev.get("body") == row.get("body") and prev.get("made_at")
        row.update({"made_at": prev.get("made_at") if same else now_iso, "updated_at": now_iso,
                    "first_made_at": prev.get("first_made_at") or prev.get("made_at") or now_iso,
                    "decision": d.get("decision") or o.get("decision") or prev.get("decision")})
        doc["items"][did] = {k: v for k, v in row.items() if v is not None}
        done.append(did)
    return done, refused


def _apply_found_replies(out: str, folder: str, brief: dict[str, Any], owed: dict[str, Any], found: dict[str, Any]) -> list[str]:
    """Replies the morning found for an `ask_nudge` or a second chase (`lp_call` with `again`): kept on each ask or LP
    (against the note they answer), and the rows, heroes and push of this run say so. Returns the documents changed,
    and "push:<line>" when the push line changed."""
    changed: list[str] = []
    item_ids: dict[str, dict[str, Any]] = {}
    lp_ids: dict[str, dict[str, Any]] = {}
    for oid, rep_ in found.items():
        o = owed.get(oid) or {}
        by_ = str(rep_.get("by") or o.get("to_name") or "They").split(" ")[0]
        # A reply that only says the answer will follow ("let me think and come back to you") keeps `defers`: the ask is
        # followed up five working days later, never closed by it.
        defers_ = bool(rep_.get("defers")) or bool(DEFER_WORDS.search(str(rep_.get("text") or "")) and not YES_WORDS.search(str(rep_.get("text") or "")))
        rec_ = {"on": str(rep_.get("on")), "by": by_, **({"url": rep_["url"]} if rep_.get("url") else {}), **({"defers": True} if defers_ else {})}
        if o.get("kind") == "ask_nudge":
            for t_ in [o.get("action_id")] + list(o.get("action_ids") or []):
                if t_ and str(t_).endswith("_nudge"):
                    note_tap = str(t_)[:-len("_nudge")]
                    item_ids[re.sub(r"_(team|intro)$", "", note_tap)] = {**rec_, "tap": note_tap}
        elif o.get("kind") == "lp_call" and o.get("lp_id"):
            lp_ids[o["lp_id"]] = {**rec_, "tap": o.get("chase_tap") or (o.get("action_ids") or [None])[0]}
    apath = os.path.join(folder, "snap__asks.json")
    if item_ids and os.path.exists(apath):
        adoc = load(apath)
        for a_ in ((adoc.get("items") or {}).values()):
            if isinstance(a_, dict) and a_.get("item_id") in item_ids:
                was_ = a_.get("replied") if isinstance(a_.get("replied"), dict) else {}
                a_["replied"] = {**item_ids[a_["item_id"]], **({"defers": True} if was_.get("defers") and was_.get("on") == item_ids[a_["item_id"]].get("on") else {})}
        dump(adoc, apath)
        changed.append("asks")
    lpath = os.path.join(folder, "snap__lps.json")
    if lp_ids and os.path.exists(lpath):
        ldoc = load(lpath)
        for lid_, row_ in ((ldoc.get("lps") or {}).items()):
            if lid_ in lp_ids and isinstance(row_, dict) and isinstance(row_.get("alert"), dict):
                row_["alert"]["replied"] = lp_ids[lid_]
        dump(ldoc, lpath)
        changed.append("lps")

    def said(r_: dict[str, Any]) -> str:
        return f"{r_['by']} replied on {fmt_short_date(parse_dt(r_['on']))}"
    lines_: dict[str, str] = {}
    rows_ = [it for sec in brief.get("sections") or [] for it in sec.get("items") or []]
    for it in rows_ + ([brief["hero"]] if isinstance(brief.get("hero"), dict) else []):
        key_ = it.get("id") or it.get("item_id")
        ids_ = [g_.get("item_id") for g_ in it.get("group_asks") or []] or [key_]
        hits_ = [item_ids[i_] for i_ in ids_ if i_ in item_ids]
        if hits_ and len(hits_) == len(ids_):
            text_ = said(hits_[0]) + (": the answer is to follow" if hits_[0].get("defers") else ": read it, then answer here")
            for k_ in ("detail", "finding"):
                if k_ in it:
                    it[k_] = text_
            it.update({"draft": None, "status_word": "replied", "ask_state": "replied", "state_label": f"{hits_[0]['by']} replied"})
            it.pop("push_line", None)
            it.pop("push_lines", None)
            lines_[str(key_)] = (str(it.get("title") or it.get("statement") or "").split(":")[0] + ": " + said(hits_[0]))[:89]
        lid_ = ((it.get("entity") or {}).get("id") if (it.get("entity") or {}).get("type") == "lp" else None) or it.get("lp_id")
        if lid_ in lp_ids:
            for k_ in ("detail", "finding"):
                if k_ in it:
                    it[k_] = str(it[k_]).split("; ")[0] + f"; {said(lp_ids[lid_])}: read it before you chase again"
            it["draft"] = None
            lines_[str(key_)] = (str((it.get("entity") or {}).get("name") or it.get("statement") or "An LP") + ": " + said(lp_ids[lid_]))[:89]
    rpath = os.path.join(out, "report.json")
    if lines_ and os.path.exists(rpath):
        report = load(rpath)
        push_ = report.get("push") if isinstance(report.get("push"), dict) else {}
        new_ = lines_.get(str(push_.get("item") or ""))
        if new_ and new_ != push_.get("line"):
            push_["line"] = new_
            report.update({"push": push_, "push_line": new_})
            dump(report, rpath)
            runpath = os.path.join(folder, "run.json")
            if os.path.exists(runpath):
                run_ = load(runpath)
                if isinstance(run_, dict):
                    run_["push_line"] = new_
                    dump(run_, runpath)
            changed.append(f"push:{new_}")
    return changed


def push_after_drafts(push: dict[str, Any], brief: dict[str, Any], fresh: set[str]) -> str | None:
    """The morning push was worded at the build, before morning-brief step 6 wrote the drafts. When it names a promise,
    a grouped nudge or a capital call whose draft was written just now, the line says it is ready, so the phone, Today
    and the run's last line agree. The new line, or None when nothing changes."""
    item_, line_ = (push or {}).get("item"), str((push or {}).get("line") or "")
    if not item_ or not line_ or not (push or {}).get("send"):
        return None
    hero_ = brief.get("hero") or {}
    rows_ = [it for sec in brief.get("sections") or [] for it in sec.get("items") or []]
    hit = hero_ if hero_.get("item_id") == item_ else next((r for r in rows_ if r.get("id") == item_), None)
    if not hit or hit.get("draft") not in fresh:
        return None
    repeat = line_.startswith("Still open: ")
    new_ = None
    if hit.get("kind") == "commitment":
        new_ = _promise_line({**hit, "statement": hit.get("statement") or hit.get("title")}, repeat)
    elif hit.get("group_asks") and hit.get("push_line"):
        pre_ = "Still open: " if repeat else ""
        new_ = next((pre_ + str(c_) for c_ in [hit["push_line"]] + list(hit.get("push_lines") or []) if c_ and len(pre_ + str(c_)) <= 89),
                    str(hit["push_line"]))
    elif hit.get("kind") == "lp" and hit.get("call") and "ready" not in line_.lower():
        cand = line_.rstrip(".") + (". Second note ready" if hit.get("chased") else ". Draft ready")
        new_ = cand if len(cand) <= 89 else None
    elif hit.get("kind") == "ask" and "ready" not in line_.lower():
        cand = line_.rstrip(".") + ". Note ready"  # one ask's nudge, or its next note, written this morning
        new_ = cand if len(cand) <= 89 else None
    return new_ if new_ and new_ != line_ else None


def _redo_push_line(out: str, folder: str, brief: dict[str, Any], fresh: set[str]) -> str | None:
    """push_after_drafts on the run's files: the report and the run row take the new line. Returns it, or None."""
    rpath, runpath = os.path.join(out, "report.json"), os.path.join(folder, "run.json")
    if not os.path.exists(rpath):
        return None
    report = load(rpath)
    push_ = report.get("push") if isinstance(report.get("push"), dict) else {}
    new_ = push_after_drafts(push_, brief, fresh)
    if not new_:
        return None
    push_["line"] = new_
    report.update({"push": push_, "push_line": new_})
    dump(report, rpath)
    if os.path.exists(runpath):
        run_ = load(runpath)
        if isinstance(run_, dict):
            run_["push_line"] = new_
            dump(run_, runpath)
    return new_


def ready_hero(doc: dict[str, Any] | None, fresh: set[str], drafts: dict[str, Any]) -> bool:
    """An ask hero (snap/asks or snap/portfolio) for asks that went out in one note: once this run wrote their nudge, it
    says "Nudge ready" and opens the draft. True when it changed."""
    hero_ = (doc or {}).get("hero") if isinstance(doc, dict) else None
    if not isinstance(hero_, dict) or not hero_.get("group_asks") or hero_.get("draft"):
        return False
    taps = {f"{g.get('item_id')}{suf}" for g in hero_["group_asks"] for suf in ("_nudge", "_intro_nudge", "_team_nudge")}
    hit = next((did for did in sorted(fresh) if isinstance(drafts.get(did), dict) and
                ({drafts[did].get("action_id")} | set(drafts[did].get("action_ids") or [])) & taps), None)
    if not hit:
        return False
    hero_["draft"] = hit
    rf = hero_.get("ready_form") if isinstance(hero_.get("ready_form"), dict) else {}
    if rf.get("detail"):
        more = re.search(r"\. (\d+ more open)$", str(hero_.get("finding") or ""))
        hero_["finding"] = rf["detail"] + (f". {more.group(1)}" if more else "")
        hero_["state"] = "ready"
    return True


def _ready_heroes(path: str, fresh: set[str], drafts: dict[str, Any]) -> bool:
    """ready_hero on a snapshot file in the run folder."""
    if not os.path.exists(path):
        return False
    doc = load(path)
    if not ready_hero(doc, fresh, drafts):
        return False
    dump(doc, path)
    return True


def cmd_due(a: argparse.Namespace) -> int:
    config = load(a.config) if a.config and os.path.exists(a.config) else {}
    if isinstance(config, dict) and "data" in config and isinstance(config["data"], dict):
        config = config["data"]
    home = homedb.read_home(a.home)
    if not config:
        config = home["snap"].get("config") or {}
    now = parse_dt(a.now, config.get("tz")) if a.now else None
    _emit(schedules.due(config, home, now, weekend_prompt=bool(a.weekend)))
    return 0


def cmd_schedules(a: argparse.Namespace) -> int:
    config = load(a.config)
    if isinstance(config, dict) and "data" in config and isinstance(config["data"], dict) and "level" not in config:
        config = config["data"]
    _emit(schedules.build(config))
    return 0


def cmd_tune(a: argparse.Namespace) -> int:
    config = load(a.config)
    home = homedb.read_home(a.home)
    ratings = (home.get("ratings") or [])
    if isinstance(config, dict) and "data" in config and isinstance(config["data"], dict) and "level" not in config:
        config = config["data"]
    tz = config.get("tz") or "UTC"
    from .util import tzinfo
    from datetime import datetime as _dt
    now = parse_dt(a.now, tz) if getattr(a, "now", None) else _dt.now(tzinfo(tz))
    res = tuning.tune(config, ratings, _profiles().get("limits"), now.isoformat())
    scores = sorted((r for r in ratings if r.get("kind") == "weekly_score"), key=lambda r: r.get("at") or "")
    res["weekly_score"] = int(scores[-1]["value"]) if scores and str(scores[-1].get("value", "")).isdigit() else None
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        dump(res["config"], os.path.join(a.out, "config.json"))
        # What a scheduled run may write back: the tuned fields only, merged into snap/config (the guard holds it to these).
        dump({k: res["config"][k] for k in ("weights", "today_items", "dwell_scale", "tuned_at") if k in res["config"]},
             os.path.join(a.out, "config-update.json"))
        dump(res, os.path.join(a.out, "tuning.json"))
    _emit({"changes": res["changes"], "note": res["note"], "counts": res["counts"], "weekly_score": res["weekly_score"]})
    return 0


def cmd_lint(a: argparse.Namespace) -> int:
    v = safety.lint_skills(a.root)
    _emit({"violations": v, "ok": not v})
    return 0 if not v else 1


def cmd_check(a: argparse.Namespace) -> int:
    ok = sys.version_info >= (3, 9)
    files = ["ontology/stages.json", "ontology/profiles.json", "schedules.json"]
    missing = [f for f in files if not os.path.exists(os.path.join(ROOT, f))]
    # The page is copied only by setup, which publishes it; a scheduled run never needs it.
    _emit({"engine": __version__, "python": sys.version.split()[0], "python_ok": ok, "plugin_root": ROOT, "missing": missing,
           "home_page": os.path.exists(os.path.join(ROOT, "home", "index.html")), "ok": ok and not missing})
    return 0 if ok and not missing else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="instinct", description="ant. for VCs engine")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("check")
    s.set_defaults(fn=cmd_check)
    s = sub.add_parser("setup")
    s.add_argument("--bundle", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--tz")
    s.add_argument("--brief-time", dest="brief_time")
    s.add_argument("--level", default="auto")
    s.add_argument("--home-url", dest="home_url")
    s.set_defaults(fn=cmd_setup)
    s = sub.add_parser("build")
    s.add_argument("--bundle", required=True)
    s.add_argument("--config", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--home")
    s.add_argument("--versions")
    s.add_argument("--extracted")
    s.add_argument("--inbound")
    s.add_argument("--kpis")
    s.add_argument("--applied", help="JSON map of action id to {status: applied|failed, reason}")
    s.add_argument("--asks", help="Founder asks read this run: [{company, company_id, ask, who, kind, date, source_url}]")
    s.add_argument("--packs", help="Post-meeting packs written this run: [{meeting_id, company, line}]")
    s.add_argument("--proposals", help="Proposals written this run: {id: proposal} (shape in shared/home.md)")
    s.add_argument("--drafts", help="Drafts written or saved this run: {id: draft} (shape in shared/home.md)")
    s.add_argument("--digest", help="Markdown of the review, pre-read, week ahead or digest written this run")
    s.add_argument("--digest-kind", dest="digest_kind", choices=["review", "preread", "week_ahead", "digest"])
    s.add_argument("--run-id", dest="run_id")
    s.add_argument("--started")
    s.add_argument("--jobs", help="Comma-separated jobs from the due command")
    s.add_argument("--mode", default="daily", choices=["setup", "daily", "pulse", "week_ahead", "review", "digest", "weekend"])
    s.set_defaults(fn=cmd_build)
    s = sub.add_parser("validate-commitments")
    s.add_argument("--bundle", required=True)
    s.add_argument("--extracted", required=True)
    s.add_argument("--out")
    s.set_defaults(fn=cmd_validate)
    s = sub.add_parser("triage")
    s.add_argument("--inbound", required=True)
    s.add_argument("--thesis", required=True)
    s.add_argument("--passes")
    s.add_argument("--out")
    s.set_defaults(fn=cmd_triage)
    s = sub.add_parser("check-injection")
    s.add_argument("--inbound")
    s.add_argument("--text-file", dest="text_file")
    s.set_defaults(fn=cmd_check_injection)
    s = sub.add_parser("memo-check")
    s.add_argument("--memo", required=True)
    s.add_argument("--sources", required=True)
    s.set_defaults(fn=cmd_memo)
    s = sub.add_parser("letter-check")
    s.add_argument("--letter", required=True)
    s.set_defaults(fn=cmd_letter_check)
    s = sub.add_parser("intro")
    s.add_argument("--bundle", required=True)
    s.add_argument("--company-file", dest="company_file", help="A file holding the company name (preferred)")
    s.add_argument("--company", help="Only for names you typed yourself")
    s.set_defaults(fn=cmd_intro)
    s = sub.add_parser("actions")
    s.add_argument("--home", required=True)
    s.add_argument("--now", help="ISO time of this run; taps older than 30 days are never offered again")
    s.set_defaults(fn=cmd_actions)
    s = sub.add_parser("questions")
    s.add_argument("--out", required=True, help="The build's --out folder")
    s.add_argument("--questions", required=True, help="{meeting_id: [three questions]}")
    s.set_defaults(fn=cmd_questions)
    s = sub.add_parser("drafts")
    s.add_argument("--out", required=True, help="The build's --out folder")
    s.add_argument("--drafts", required=True, help="{draft id: draft} for the drafts saved to Gmail this run (shape in shared/home.md)")
    s.set_defaults(fn=cmd_drafts)
    s = sub.add_parser("due")
    s.add_argument("--config")
    s.add_argument("--home")
    s.add_argument("--now")
    s.add_argument("--weekend", action="store_true")
    s.set_defaults(fn=cmd_due)
    s = sub.add_parser("schedules")
    s.add_argument("--config", required=True)
    s.set_defaults(fn=cmd_schedules)
    s = sub.add_parser("tune")
    s.add_argument("--config", required=True)
    s.add_argument("--home", required=True)
    s.add_argument("--out")
    s.add_argument("--now")
    s.set_defaults(fn=cmd_tune)
    s = sub.add_parser("lint")
    s.add_argument("--root", required=True)
    s.set_defaults(fn=cmd_lint)
    args = p.parse_args(argv)
    return args.fn(args)
