"""Per-entity timelines for Home's side panels.

Every company, person and LP Home shows gets a short history, newest first. Each event names the tool it came from
and carries the link that opens it, so every line in the panel can be checked:

    {"id": "thread:t1", "at": "2026-10-20T10:12:00+05:30", "src": "Gmail", "url": "https://...", "kind": "email",
     "text": "Email from Maya Chen: Q3 numbers attached"}

Keys: "c:<company id>", "p:<person id>", "lp:<lp id>", "in:<inbound id>". Events merge across runs (a pulse reads only
recent mail, so older events stay as Home had them), last 180 days, at most 14 per entity. The result is split into
shards (snap/timeline_0 .. timeline_3) so no Home document passes its size limit.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import timedelta
from typing import Any

from .util import clip, norm_email, parse_dt

SHARDS = 4
PER_ENTITY = 14
KEEP_DAYS = 180
SHARD_BUDGET = 220_000  # characters per shard, under the 240 KB a Home document can hold
NOTE_APPS = (("granola", "Granola"), ("fireflies", "Fireflies"), ("otter", "Otter"), ("fathom", "Fathom"), ("notion", "Notion"),
             ("zoom", "Zoom"), ("tldv", "tl;dv"))


def _app(url: Any, default: str) -> str:
    u = str(url or "").lower()
    if "mail.google" in u:
        return "Gmail"
    if "calendar.google" in u:
        return "Calendar"
    if "drive.google" in u or "docs.google" in u:
        return "Drive"
    for key, label in NOTE_APPS:
        if key in u:
            return label
    for crm in ("affinity", "attio", "hubspot", "salesforce", "pipedrive", "notion"):
        if crm in u:
            return crm.capitalize() if crm != "hubspot" else "HubSpot"
    return default


def _link(url: Any) -> str | None:
    """Only a plain web link is written: a line without one is never shown."""
    u = str(url or "").strip()
    return u if re.match(r"^https?://\S", u) else None


def _money(v: Any) -> str | None:
    return f"${v:,.0f}" if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def _summary_text(summ: Any) -> str:
    """A notes app's summary as one readable line: a string, a list of strings or of {text}, or a dict of those."""
    if isinstance(summ, dict):
        summ = [v for v in summ.values()]
    if isinstance(summ, list):
        parts = []
        for x in summ:
            if isinstance(x, dict):
                x = x.get("text") or x.get("summary") or ""
            elif isinstance(x, list):
                x = "; ".join(str(y) for y in x if isinstance(y, (str, int, float)))
            if isinstance(x, (str, int, float)) and str(x).strip():
                parts.append(str(x).strip())
        return "; ".join(parts)
    return str(summ) if isinstance(summ, (str, int, float)) else ""


def _when(e: dict[str, Any]):
    return parse_dt(e.get("at"))


def shard_of(key: str) -> int:
    return int(hashlib.sha1(key.encode()).hexdigest(), 16) % SHARDS


def build(ctx: dict[str, Any], bundle: dict[str, Any], store: list[dict[str, Any]], home: dict[str, Any],
          inbound_rows: list[dict[str, Any]] | None = None) -> dict[str, list[dict[str, Any]]]:
    """The events this run can see, per entity key."""
    tz = ctx.get("tz")
    lookup = ctx.get("lookup") or {}
    members = set(ctx.get("member_ids") or [])
    out: dict[str, dict[str, dict[str, Any]]] = {}

    def add(key: str | None, ev: dict[str, Any]) -> None:
        link = _link(ev.get("url"))
        if not key or not ev.get("at") or not link:
            return  # a line without its link is never shown
        out.setdefault(key, {})[ev["id"]] = {**ev, "url": link}

    def keys_for(pids: list[str]) -> list[str]:
        ks: list[str] = []
        for pid in pids:
            p = lookup.get(pid) or {}
            if pid in members or p.get("colleague") or p.get("is_member"):
                continue
            ks.append("p:" + pid)
            if p.get("company_id"):
                ks.append("c:" + str(p["company_id"]))
        return list(dict.fromkeys(ks))

    me = norm_email(ctx.get("user_email"))
    lp_by_email: dict[str, str] = {}
    for lp_ in bundle.get("lps") or []:
        for e in lp_.get("contacts") or []:
            if e:
                lp_by_email[norm_email(e)] = str(lp_.get("id"))

    # Mail: who wrote last and what they said, in one line.
    for th in bundle.get("threads") or []:
        msgs = [m for m in th.get("messages") or [] if isinstance(m, dict)]
        dated = [(parse_dt(m.get("date"), tz), m) for m in msgs]
        last = max((x for x in dated if x[0]), key=lambda x: x[0], default=(None, {}))[1] if any(x[0] for x in dated) else (msgs[-1] if msgs else {})
        when = parse_dt(last.get("date") or th.get("date"), tz)
        if not when:
            continue
        frm = last.get("from") or {}
        who = "you" if me and norm_email(frm.get("email")) == me else (frm.get("name") or frm.get("email") or "").strip()
        said = " ".join(str(last.get("text") or "").split())
        text = f"Email{' from ' + who if who else ''}: {th.get('subject') or '(no subject)'}" + (f". {said}" if said else "")
        ev = {"id": f"thread:{th.get('id')}", "at": when.isoformat(), "src": "Gmail", "url": th.get("url"), "kind": "email", "text": clip(text, 220)}
        pids = [(lookup.get(norm_email(p.get("email"))) or {}).get("id") for p in th.get("participants") or [] if p.get("email")]
        for k in keys_for([p for p in pids if p]):
            add(k, ev)
        for p in th.get("participants") or []:
            lpid = lp_by_email.get(norm_email(p.get("email")))
            if lpid:
                add("lp:" + lpid, ev)
        # Files shared in the thread (a deck, a financial model): their own events, with the link the email gives.
        for m in msgs:
            for att in m.get("attachments") or []:
                if not isinstance(att, dict) or not att.get("url") or not att.get("name"):
                    continue
                nm = str(att["name"])
                kind_ = "Deck" if re.search(r"deck|pitch|teaser|memo", nm, re.I) else "Model" if re.search(r"model|financial|projection|\.xlsx?$", nm, re.I) else "File"
                when_ = parse_dt(m.get("date"), tz) or when
                fev = {"id": f"file:{th.get('id')}:{nm}", "at": when_.isoformat(), "src": _app(att["url"], "Gmail"), "url": att["url"], "kind": "doc",
                       "doc": kind_.lower(), "text": clip(f"{kind_} shared: {nm}", 220)}
                for k in keys_for([p for p in pids if p]):
                    add(k, fev)

    # Meetings, and the notes taken in them.
    notes_by_event = {tr.get("event_id"): tr for tr in bundle.get("transcripts") or [] if tr.get("event_id")}
    for m in ctx.get("meetings") or []:
        st = m.get("start")
        if not st or st > ctx["now"] or m.get("all_day"):
            continue
        ks = keys_for(m.get("person_ids") or [])
        for a in m.get("attendees") or []:
            lpid = lp_by_email.get(norm_email((a or {}).get("email")))
            if lpid:
                ks.append("lp:" + lpid)
        add_ev = {"id": f"event:{m.get('id')}", "at": st.isoformat(), "src": _app(m.get("url"), "Calendar"), "url": m.get("url"), "kind": "meeting",
                  "text": clip(f"Meeting: {m.get('title') or 'Meeting'}", 220)}
        tr = notes_by_event.get(m.get("id"))
        note_ev = None
        if tr and tr.get("url"):
            first = " ".join(_summary_text(tr.get("summary")).replace("- ", "").split())
            note_ev = {"id": f"notes:{tr.get('id')}", "at": st.isoformat(), "src": _app(tr.get("url"), "Notes"), "url": tr.get("url"), "kind": "notes",
                       "note_id": tr.get("id"), "text": clip("Notes: " + (first or (tr.get("title") or "meeting notes")), 220)}
        for k in dict.fromkeys(ks):
            add(k, add_ev)
            if note_ev:
                add(k, note_ev)

    # Promises from meetings, both ways.
    for c in store or []:
        when = parse_dt(c.get("meeting_date"), tz)
        if not when or not c.get("source_url"):
            continue
        pids = [(lookup.get(norm_email(e)) or {}).get("id") for e in c.get("attendee_emails") or []]
        ev = {"id": f"promise:{c.get('id')}", "at": when.isoformat(), "src": _app(c.get("source_url"), "Notes"), "url": c.get("source_url"), "kind": "promise",
              "text": clip(f"{c.get('owed_by') or 'Someone'} promised: {c.get('what')}" + (f" (due {str(c.get('due'))[:10]})" if c.get("due") else "") +
                           (" · done" if c.get("status") == "done" else ""), 220)}
        for k in keys_for([p for p in pids if p]):
            add(k, ev)

    # The CRM: stage moves and the last step.
    for d in ctx.get("deals") or []:
        cid = d.get("company_id")
        if not cid:
            continue
        if d.get("stage_entered_dt") and d.get("url"):
            add("c:" + str(cid), {"id": f"stage:{d.get('id')}:{d.get('stage_key')}", "at": d["stage_entered_dt"].isoformat(), "src": _app(d.get("url"), "CRM"),
                                  "url": d.get("url"), "kind": "crm", "text": clip(f"Moved to {d.get('stage_name') or d.get('stage')}" +
                                                                               (f". Next step: {d.get('next_step')}" if d.get("next_step") else ""), 220)})
    for p_ in bundle.get("passes") or []:
        when = parse_dt(p_.get("date"), tz)
        dom = str(p_.get("domain") or "").lower()
        cid = (ctx.get("domain_to_company") or {}).get(dom)
        if when and cid and p_.get("source_url"):
            add("c:" + str(cid), {"id": f"pass:{p_.get('id')}", "at": when.isoformat(), "src": "Pass log", "url": p_.get("source_url"), "kind": "pass",
                                  "text": clip(f"Passed{' by ' + str(p_.get('by')) if p_.get('by') else ''}: {p_.get('reason') or ''}", 220)})

    # Founder updates: the month's numbers, against plan.
    kpis = bundle.get("portfolio_kpis") if isinstance(bundle.get("portfolio_kpis"), dict) else {}
    for cid, months in kpis.items():
        months = months if isinstance(months, list) else [months] if isinstance(months, dict) else []
        for k in months:
            if not isinstance(k, dict):
                continue
            when = parse_dt(str(k.get("month") or "") + "-28", tz) if k.get("month") else None
            if not when or not k.get("source_url"):
                continue
            bits = []
            if _money(k.get("revenue_usd")):
                bits.append(f"revenue {_money(k['revenue_usd'])}" + (f" vs plan {_money(k.get('plan_revenue_usd'))}" if _money(k.get("plan_revenue_usd")) else ""))
            if _money(k.get("burn_usd")):
                bits.append(f"burn {_money(k['burn_usd'])}")
            if _money(k.get("cash_usd")):
                bits.append(f"cash {_money(k['cash_usd'])}")
            for dep in k.get("departures") if isinstance(k.get("departures"), list) else []:
                if isinstance(dep, dict) and dep.get("name"):
                    bits.append(f"{dep.get('name')}" + (f" ({dep.get('role')})" if dep.get("role") else "") + " leaving")
            add("c:" + str(cid), {"id": f"kpi:{cid}:{k.get('month')}", "at": when.isoformat(), "src": _app(k.get("source_url"), "Founder update"),
                                  "url": k.get("source_url"), "kind": "update", "text": clip(f"{k.get('month')} update: " + ", ".join(bits), 220)})

    # LPs: calls and touches.
    for lp_ in bundle.get("lps") or []:
        url = lp_.get("source_url")
        for field, label in (("last_call_date", "Capital call"), ("last_touch", "Last touch")):
            when = parse_dt(lp_.get(field), tz)
            if when and url:
                add("lp:" + str(lp_.get("id")), {"id": f"lp:{lp_.get('id')}:{field}", "at": when.isoformat(), "src": _app(url, "LP list"), "url": url,
                                                 "kind": "lp", "text": label + (f": {_money(lp_.get('called_usd'))} called" if field == "last_call_date" and _money(lp_.get("called_usd")) else "")})

    # Pitches: when it came in and what ant. made of it.
    for r in inbound_rows or []:
        when = parse_dt(r.get("arrived") or r.get("date") or r.get("seen_at"), tz)
        if when and r.get("source_url"):
            add("in:" + str(r.get("id")), {"id": f"pitch:{r.get('id')}", "at": when.isoformat(), "src": "Gmail", "url": r.get("source_url"), "kind": "pitch",
                                           "text": clip(f"Pitch from {r.get('from') or r.get('company')}: fit {r.get('score')} of 100", 220)})
    return {k: list(v.values()) for k, v in out.items()}


def merge_snaps(new: dict[str, list[dict[str, Any]]], home: dict[str, Any], now, as_of: str,
                ctx: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    """Merge this run's events into Home's, trim, and split into shards. timeline_0 also carries `emails`, each address of a
    person with a timeline to their key, so a draft's recipient or a CRM contact finds its person."""
    merged: dict[str, dict[str, dict[str, Any]]] = {}
    for i in range(SHARDS):
        old_items = (((home.get("snap") or {}).get(f"timeline_{i}") or {}).get("items"))
        if not isinstance(old_items, dict):
            continue
        for k, evs in old_items.items():
            for ev in evs if isinstance(evs, list) else []:
                # Old events meet the same rules as new ones: a readable date and a web link.
                if isinstance(ev, dict) and ev.get("id") and _when(ev) and _link(ev.get("url")):
                    merged.setdefault(str(k), {})[ev["id"]] = ev
    for k, evs in new.items():
        for ev in evs:
            merged.setdefault(k, {})[ev["id"]] = ev
    floor = now - timedelta(days=KEEP_DAYS)
    shards: list[dict[str, list[dict[str, Any]]]] = [{} for _ in range(SHARDS)]
    for k, evs in merged.items():
        keep = [e for e in evs.values() if _when(e) and _when(e) >= floor]
        keep.sort(key=lambda e: _when(e), reverse=True)  # by real time, whatever the offset
        if keep:
            shards[shard_of(k)][k] = keep[:PER_ENTITY]
    emails: dict[str, str] = {}
    if ctx:
        old_e = (((home.get("snap") or {}).get("timeline_0") or {}).get("emails"))
        emails = dict(old_e) if isinstance(old_e, dict) else {}
        lookup = ctx.get("lookup") or {}
        for k in merged:
            if k.startswith("p:"):
                for e in (lookup.get(k[2:]) or {}).get("emails") or []:
                    if e:
                        emails[norm_email(e)] = k
    size = lambda d: len(json.dumps(d, default=str, ensure_ascii=False).encode("utf-8"))
    out = {}
    for i, items in enumerate(shards):
        extra = {}
        if i == 0 and ctx:
            live = {k for sh in shards for k in sh}
            extra = {"emails": dict([kv for kv in emails.items() if kv[1] in live][-1500:])}
        cap = PER_ENTITY
        while size({"items": items, **extra}) > SHARD_BUDGET and cap > 1:
            cap -= 1
            items = {k: v[:cap] for k, v in items.items()}
        # Still too big: the entities whose latest event is oldest go first, never the newest LP, pitch or deal.
        if size({"items": items, **extra}) > SHARD_BUDGET:
            order = sorted(items, key=lambda k: _when(items[k][0]), reverse=True)
            kept: dict[str, list[dict[str, Any]]] = {}
            for k in order:
                kept[k] = items[k]
                if size({"items": kept, **extra}) > SHARD_BUDGET:
                    del kept[k]
                    break
            items = kept
            if extra:
                extra["emails"] = {e: k for e, k in extra["emails"].items() if k in items or any(k in sh for j, sh in enumerate(shards) if j)}
        if items or (home.get("snap") or {}).get(f"timeline_{i}"):
            out[f"timeline_{i}"] = {"as_of": as_of, "items": items, **extra}
    return out


def reminders(home: dict[str, Any], ctx: dict[str, Any], snaps: dict[str, Any], bundle: dict[str, Any], as_of: str) -> dict[str, Any] | None:
    """Context for the user's own reminders (state/reminders, written by Home).

    For each open reminder: the companies, people and LPs it names, each with its latest three events, and the notes
    Claude found for it this run (`bundle.reminder_notes`, each with a link), kept until the reminder is done."""
    items = (((home.get("state") or {}).get("reminders") or {}).get("items")) or {}
    if not items and not (home.get("snap") or {}).get("reminders"):
        return None
    old = ((((home.get("snap") or {}).get("reminders") or {}).get("items")) or {})
    names: list[tuple[str, str, str]] = []  # (lowercase name, key, label)
    for d in ctx.get("deals") or []:
        if d.get("company_name") and d.get("company_id"):
            names.append((str(d["company_name"]).lower(), "c:" + str(d["company_id"]), str(d["company_name"])))
    for cid, comp in (ctx.get("companies") or {}).items():
        if comp.get("name") and comp.get("status") == "portfolio":
            names.append((str(comp["name"]).lower(), "c:" + str(cid), str(comp["name"])))
    for lp_ in bundle.get("lps") or []:
        if lp_.get("name"):
            names.append((str(lp_["name"]).lower(), "lp:" + str(lp_.get("id")), str(lp_["name"])))
    members = set(ctx.get("member_ids") or [])
    for p in ctx.get("people") or []:
        if p.get("name") and len(str(p["name"]).split()) >= 2 and p.get("id") not in members and not p.get("colleague"):
            names.append((str(p["name"]).lower(), "p:" + str(p["id"]), str(p["name"])))
    timelines: dict[str, list[dict[str, Any]]] = {}
    for i in range(SHARDS):
        timelines.update(((snaps.get(f"timeline_{i}") or (home.get("snap") or {}).get(f"timeline_{i}") or {}).get("items")) or {})
    notes_in = bundle.get("reminder_notes") or {}
    out: dict[str, Any] = {}
    for rid, r in items.items():
        if not isinstance(r, dict) or r.get("done_at") or not r.get("text"):
            continue
        text = " " + " ".join(str(r["text"]).lower().split()) + " "
        hits, seen = [], set()
        for low, key, label in sorted(names, key=lambda x: -len(x[0])):
            if len(low) >= 4 and key not in seen and re.search(r"(?<![\w])" + re.escape(low) + r"(?![\w])", text):
                seen.add(key)
                hits.append({"key": key, "label": label, "events": (timelines.get(key) or [])[:3]})
            if len(hits) >= 3:
                break
        notes = [n for n in (notes_in.get(rid) if isinstance(notes_in.get(rid), list) else []) if isinstance(n, dict) and n.get("text") and _link(n.get("url"))][:4] or \
            ((old.get(rid) or {}).get("notes") or [])
        out[rid] = {"related": hits, "notes": [{"text": clip(str(n["text"]), 220), "url": _link(n.get("url")), "src": n.get("src") or _app(n.get("url"), "Source")} for n in notes if isinstance(n, dict) and _link(n.get("url"))],
                    "checked_at": as_of}
    return {"as_of": as_of, "items": out}
