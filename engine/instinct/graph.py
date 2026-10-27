"""The context graph: people, companies, deals, meetings and interactions in one place.

Built from a bundle (what the skills gathered from connectors) plus the resolved
people. Every skill starts here.
"""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from . import stages as stages_mod
from .resolve import person_lookup, resolve_people
from .util import domain_of, is_freemail, local_now, norm_email, parse_dt, sid


def build(bundle: dict[str, Any], resolved: dict[str, Any] | None = None) -> dict[str, Any]:
    tz = bundle.get("tz") or "UTC"
    now = local_now(bundle.get("now"), tz)
    resolved = resolved or resolve_people(bundle)
    people = resolved["people"]
    lookup = person_lookup(people)
    firm = bundle.get("firm") or {}
    firm_domain = (firm.get("domain") or "").lower()
    user = bundle.get("user") or {}
    user_email = norm_email(user.get("email"))
    user_person = lookup.get(user_email)
    members = []
    for m in (firm.get("members") or []):
        p = lookup.get(norm_email(m.get("email")))
        members.append({**m, "person_id": p["id"] if p else None})
    member_ids = {m["person_id"] for m in members if m.get("person_id")}
    if user_person:
        member_ids.add(user_person["id"])

    crm = bundle.get("crm") or {}
    stage_map = stages_mod.load()
    companies: dict[str, dict[str, Any]] = {}
    domain_to_company: dict[str, str] = {}
    for c in (crm.get("companies") or []):
        cid = c.get("id") or sid("company", c.get("domain") or c.get("name"), prefix="c")
        companies[cid] = {**c, "id": cid}
        if c.get("domain"):
            domain_to_company[c["domain"].lower()] = cid
    for p in people:
        dom = p.get("company_domain")
        if dom and dom != firm_domain and dom not in domain_to_company and not is_freemail(dom):
            cid = sid("company", dom, prefix="c")
            companies[cid] = {"id": cid, "name": _name_from_domain(dom), "domain": dom, "status": "other", "inferred": True}
            domain_to_company[dom] = cid
    crm_person_company = {cp.get("id"): cp.get("company_id") for cp in (crm.get("people") or [])}
    for p in people:
        cid = crm_person_company.get(p.get("crm_id")) if p.get("crm_id") else None
        p["company_id"] = cid or domain_to_company.get(p.get("company_domain") or "")
        p["is_member"] = p["id"] in member_ids

    # Interactions from threads, events and transcripts.
    interactions: list[dict[str, Any]] = []
    for th in (bundle.get("threads") or []):
        pids = _pids((th.get("participants") or []), lookup)
        dates = [parse_dt(m.get("date"), tz) for m in (th.get("messages") or []) if m.get("date")]
        dt = max([d for d in dates if d], default=None) or parse_dt(th.get("date"), tz)
        senders = {norm_email((m.get("from") or {}).get("email")) for m in (th.get("messages") or [])}
        interactions.append({"id": f"thread:{th.get('id')}", "type": "email", "date": dt, "person_ids": pids,
                             "url": th.get("url"), "subject": th.get("subject"), "senders": senders,
                             "labels": (th.get("labels") or [])})
    transcript_by_event = {tr.get("event_id"): tr for tr in (bundle.get("transcripts") or []) if tr.get("event_id")}
    meetings = []
    for ev in (bundle.get("events") or []):
        start, end = parse_dt(ev.get("start"), tz), parse_dt(ev.get("end"), tz)
        pids = _pids((ev.get("attendees") or []), lookup)
        external = [pid for pid in pids if not lookup[pid].get("colleague") and pid not in member_ids]
        tr = transcript_by_event.get(ev.get("id"))
        # An all-day event (a date with no time, or a day long) is not a meeting the user sits in.
        all_day = (bool(ev.get("start")) and "T" not in str(ev.get("start"))) or bool(start and end and end - start >= timedelta(hours=20))
        meeting = {"id": ev.get("id"), "title": ev.get("title"), "start": start, "end": end, "person_ids": pids, "all_day": all_day,
                   "external_ids": external, "external": bool(external), "url": ev.get("url"),
                   # The addresses on the invite: a card names the one the meeting uses, not an alias merged in later.
                   "attendees": [{"name": a.get("name"), "email": a.get("email")} for a in (ev.get("attendees") or []) if isinstance(a, dict)],
                   "description": ev.get("description"), "transcript_id": tr.get("id") if tr else None,
                   "transcript_url": tr.get("url") if tr else None}
        meetings.append(meeting)
        if start and start <= now:
            interactions.append({"id": f"event:{ev.get('id')}", "type": "meeting", "date": start, "person_ids": pids,
                                 "url": ev.get("url"), "subject": ev.get("title"), "senders": set(), "labels": []})
    meetings.sort(key=lambda m: m["start"] or now)

    # Last contact and strength per person, from the user's point of view and per firm member.
    per_person: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for it in interactions:
        for pid in it["person_ids"]:
            per_person[pid].append(it)
    strengths: dict[str, dict[str, int]] = defaultdict(dict)
    lifetime: dict[str, dict[str, int]] = defaultdict(dict)
    last_touch: dict[str, dict[str, datetime]] = defaultdict(dict)
    # A thread counts toward a relationship only when the member wrote in it too: a cold sender who mails often is not
    # a warm path.
    member_emails: dict[str, set[str]] = defaultdict(set)
    for p_ in people:
        if p_["id"] in member_ids:
            member_emails[p_["id"]] |= {norm_email(e) for e in p_.get("emails") or [] if e}
    for pid, its in per_person.items():
        if pid in member_ids:
            continue
        for mid in member_ids:
            shared = [it for it in its if mid in it["person_ids"] and it["date"] and
                      (it["type"] != "email" or not member_emails.get(mid) or (it.get("senders") or set()) & member_emails[mid])]
            if not shared:
                continue
            meet_90 = sum(1 for it in shared if it["type"] == "meeting" and (now - it["date"]).days <= 90)
            mail_90 = sum(1 for it in shared if it["type"] == "email" and (now - it["date"]).days <= 90)
            meet_all = sum(1 for it in shared if it["type"] == "meeting")
            mail_all = sum(1 for it in shared if it["type"] == "email")
            last = max(it["date"] for it in shared)
            days = max(0, (now - last).days)
            recency = math.exp(-days / 60)
            raw = min(100, 12 * meet_90 + 3 * mail_90 + 4 * (meet_all - meet_90) + 1 * (mail_all - mail_90))
            strengths[mid][pid] = int(round(raw * (0.5 + 0.5 * recency)))
            lifetime[mid][pid] = int(min(100, 12 * meet_all + 3 * mail_all))
            last_touch[mid][pid] = last
    # Firm-wide relationship scores from the CRM (Affinity-style), so colleagues' relationships count too.
    member_by_email = {norm_email(m.get("email")): m.get("person_id") for m in members if m.get("person_id")}
    for cp in (crm.get("people") or []):
        hit = lookup.get(norm_email(cp.get("email"))) if cp.get("email") else None
        if not hit:
            continue
        for memail, score in (cp.get("strength_by_member") or {}).items():
            mid = member_by_email.get(norm_email(memail))
            if mid and mid != hit["id"] and isinstance(score, (int, float)):
                strengths[mid][hit["id"]] = max(strengths[mid].get(hit["id"], 0), int(score))
                lifetime[mid][hit["id"]] = max(lifetime[mid].get(hit["id"], 0), int(score))
    for p in people:
        its = [it for it in per_person.get(p["id"], []) if it["date"] and it["date"] <= now]
        p["last_contact"] = max((it["date"] for it in its), default=None)
        p["interaction_count"] = len(its)
        if user_person:
            p["strength"] = strengths.get(user_person["id"], {}).get(p["id"], 0)
            p["last_touch_user"] = last_touch.get(user_person["id"], {}).get(p["id"])

    # Company last contact (anyone at the firm with anyone at the company).
    company_last: dict[str, datetime] = {}
    for p in people:
        cid = p.get("company_id")
        if cid and p.get("last_contact"):
            if cid not in company_last or p["last_contact"] > company_last[cid]:
                company_last[cid] = p["last_contact"]

    deals = []
    for d in (crm.get("deals") or []):
        if not d.get("id"):
            d = {**d, "id": sid("deal", d.get("company_id") or d.get("company_name") or d.get("name") or str(sorted(d.items())), prefix="d")}
        # A deal carried from Home keeps the key it was mapped to when the CRM sent it; its label stays the CRM's.
        key = d["stage_key"] if d.get("from_home") and d.get("stage_key") in stage_map["by_key"] else stages_mod.map_stage(d.get("stage"), stage_map)
        comp = companies.get(d.get("company_id")) or {}
        crm_last = parse_dt(d.get("last_contact"), tz)
        seen_last = company_last.get(d.get("company_id"))
        kept = parse_dt(d.get("seen_contact"), tz)  # what an earlier run saw in your mail and calendar
        last_contact = max([x for x in (crm_last, seen_last, kept) if x], default=None)
        owner_email = norm_email(d.get("owner"))
        deals.append({**d, "stage_key": key, "stage_name": stages_mod.stage_name(key, stage_map, d.get("stage")),
                      "company_name": comp.get("name") or d.get("company_name"), "domain": comp.get("domain"),
                      "stage_entered_dt": parse_dt(d.get("stage_entered"), tz),
                      "next_step_due_dt": parse_dt(d.get("next_step_due"), tz),
                      "last_contact_dt": last_contact, "owner_email": owner_email,
                      "owner_person": (lookup.get(owner_email) or {}).get("id")})

    return {
        "tz": tz, "now": now, "bundle": bundle, "people": people, "lookup": lookup, "resolved": resolved,
        "user": user, "user_email": user_email, "user_person": user_person, "members": members,
        "member_ids": member_ids, "firm_domain": firm_domain, "companies": companies,
        "domain_to_company": domain_to_company, "interactions": interactions, "meetings": meetings,
        "strengths": strengths, "lifetime": lifetime, "last_touch": last_touch, "deals": deals,
        "stage_map": stage_map, "company_last": company_last,
    }


def _pids(parts: list[dict[str, Any]], lookup: dict[str, dict[str, Any]]) -> list[str]:
    out = []
    for p in parts:
        hit = lookup.get(norm_email(p.get("email"))) if p.get("email") else None
        if hit and hit["id"] not in out:
            out.append(hit["id"])
    return out


def _name_from_domain(domain: str) -> str:
    base = domain.split(".")[0]
    return base.replace("-", " ").title()


def company_of_person(ctx: dict[str, Any], pid: str) -> dict[str, Any] | None:
    p = ctx["lookup"].get(pid)
    if not p or not p.get("company_id"):
        return None
    return ctx["companies"].get(p["company_id"])


def open_deal_for_company(ctx: dict[str, Any], company_id: str | None) -> dict[str, Any] | None:
    if not company_id:
        return None
    active = [d for d in ctx["deals"] if d.get("company_id") == company_id and stages_mod.is_active(d["stage_key"], ctx["stage_map"])]
    return max(active, key=lambda d: stages_mod.order(d["stage_key"], ctx["stage_map"]), default=None)


def deals_for_user(ctx: dict[str, Any], scope: str) -> list[dict[str, Any]]:
    if scope in ("full", "needs_call"):
        return list(ctx["deals"])
    if scope == "off":
        return []
    me = ctx["user_email"]
    return [d for d in ctx["deals"] if d.get("owner_email") == me or me in {norm_email(t) for t in (d.get("team") or []) if isinstance(t, str)}]


def recent_window(ctx: dict[str, Any], days: int) -> datetime:
    return ctx["now"] - timedelta(days=days)
