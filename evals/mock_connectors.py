#!/usr/bin/env python3
"""Mock connectors for eval mode. Answers like Gmail, Google Calendar, Granola, the CRM, Drive, market data,
Carta, scheduled tasks and the ant. Home database would, from the golden fund (all fictional).

  python3 evals/mock_connectors.py --as aditi status
  python3 evals/mock_connectors.py --as aditi gmail search --after 2026-10-15 [--query text] [--limit 50]
  python3 evals/mock_connectors.py --as aditi gmail thread --id th0012
  python3 evals/mock_connectors.py --as aditi calendar list --start 2026-10-22T00:00:00+05:30 --end 2026-10-23T23:59:00+05:30
  python3 evals/mock_connectors.py --as aditi granola list --after 2026-10-01
  python3 evals/mock_connectors.py --as aditi granola transcript --id tr02
  python3 evals/mock_connectors.py --as aditi crm deals|companies|people|notes|passes [--deal d_lumen] ; crm record --id d_gravity ; crm update --id d_gravity --json '{"next_step": "..."}'
  python3 evals/mock_connectors.py --as aditi gmail draft --json '{"to": "", "subject": "", "body": ""}'   (no create-draft tool unless INSTINCT_MOCK_DRAFTS=1, as on the real account; send, reply and forward always fail and are recorded)
  python3 evals/mock_connectors.py --as aditi calendar create --json '{"title": "", "start": "", "end": "", "attendees": []}'
  python3 evals/mock_connectors.py --as aditi drive search --query Lumen ; drive read --id dr_lumen_metrics
  python3 evals/mock_connectors.py --as aditi slack search --query Lumen     (the fictional fund has no Slack messages)
  python3 evals/mock_connectors.py --as tara world add --json '{"id": "...", "subject": "...", "messages": [...]}'
                                                                         (eval only, between runs: play the user or the world)
  python3 evals/mock_connectors.py --as aditi market enrich --domain lumenledger.com
  python3 evals/mock_connectors.py --as aditi carta lps
  python3 evals/mock_connectors.py --as aditi schedule create --json '{"name": "...", "cron_expression": "...", "prompt": "..."}'
  python3 evals/mock_connectors.py --as aditi artifact publish --file home/index.html
  python3 evals/mock_connectors.py --as aditi db list --collection snap --out-dir DIR
  python3 evals/mock_connectors.py --as aditi db batch --file batch.json
  python3 evals/mock_connectors.py --as aditi db set|update|get --collection runs --id r20261022T0651 [--json '{...}' | --file F]
  python3 evals/mock_connectors.py --as aditi bundle --out FILE          (eval shortcut: the whole connector view in one file)
  python3 evals/mock_connectors.py --as tara bundle --out FILE --now 2026-10-29T06:28:00+05:30 --mode daily --after 2026-10-28T19:28:00+05:30
                                                                         (as that run reads it: nothing after --now, and the
                                                                         windows of its row in shared/connectors.md from --after)

A seeded run can add to the golden world: evals/runs/<run>/world_extra.json ({"threads", "events", "transcripts",
"crm_notes"}) holds what happened after the golden snapshot that its Home depends on (a note the user marked sent, an
introduction that landed, notes the CRM gained). Every read serves it, as the real apps would. A draft marked sent in
the run's mock Home (Sent it, from the page or a seed) is in the user's sent mail from that moment.

Connector states for QA come from INSTINCT_MOCK_STATE, e.g. "granola=missing,affinity=revoked,gmail=rate_limited".
`status` lists each connector's tools; Gmail lists `create_draft` only with INSTINCT_MOCK_DRAFTS=1.
Every call is logged to evals/runs/<run>/mock_log.jsonl (run name from INSTINCT_RUN, default "default").
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GOLD = os.path.join(HERE, "golden")
CONNECTORS = ["gmail", "google calendar", "granola", "affinity", "google drive", "slack", "pitchbook", "carta", "notion"]


def run_dir() -> str:
    d = os.path.join(HERE, "runs", os.environ.get("INSTINCT_RUN", "default"))
    os.makedirs(d, exist_ok=True)
    return d


def log(entry: dict) -> None:
    with open(os.path.join(run_dir(), "mock_log.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"t": time.time(), **entry}) + "\n")


def states() -> dict:
    out = {c: "connected" for c in CONNECTORS}
    for part in filter(None, os.environ.get("INSTINCT_MOCK_STATE", "").split(",")):
        k, _, v = part.partition("=")
        out[k.strip()] = v.strip()
    return out


def _log_rows() -> list[dict]:
    path = os.path.join(run_dir(), "mock_log.jsonl")
    return [json.loads(l) for l in open(path) if l.strip()] if os.path.exists(path) else []


def guard(connector: str) -> None:
    st = states().get(connector, "missing")
    if st == "connected":
        return
    msg = {"missing": f"{connector} is not connected.", "revoked": f"{connector} access was revoked. Reconnect it in Settings.",
           "rate_limited": f"{connector} is rate limited. Try again in a few minutes."}.get(st, f"{connector}: {st}")
    log({"connector": connector, "error": st})
    print(json.dumps({"error": st, "message": msg}))
    sys.exit(3)


def emit(obj) -> None:
    print(json.dumps(obj, indent=1, ensure_ascii=False))


def _latest(th: dict) -> str:
    return max([str(m.get("date") or "") for m in th.get("messages") or []] + [str(th.get("date") or "")])


def _sent_from_home(b: dict) -> dict:
    """A draft the user marked sent in this run's mock Home is in their sent mail from that moment, as on a real account:
    in its own thread when the subject replies to one ("Re: Founder asks: ..."), else a thread of its own."""
    drafts = (_home_doc("drafts") or {}).get("items") or {}
    path = os.path.join(run_dir(), "db", "state", "items.json")
    if not drafts or not os.path.exists(path):
        return b
    raw = json.load(open(path, encoding="utf-8"))
    items = ((raw.get("data") if isinstance(raw, dict) and "data" in raw else raw) or {}).get("items") or {}
    me = {"name": (b.get("user") or {}).get("name"), "email": (b.get("user") or {}).get("email")}
    if not me["email"]:
        return b
    import re  # noqa: E402

    def base(subj: object) -> str:
        return re.sub(r"^((re|fwd?|fw):\s*)+", "", str(subj or ""), flags=re.I).strip().lower()
    threads = {t["id"]: t for t in b.get("threads") or []}
    for did, d in sorted(drafts.items()):
        st = items.get(did) or {}
        at = st.get("done_at")
        if not isinstance(d, dict) or not at or (st.get("closed_by") == "done" and not st.get("sent")):
            continue  # closed by Done on its row: nothing went
        tos = [x.strip() for x in str(d.get("to") or "").replace(";", ",").split(",") if x.strip()]
        msg = {"from": me, "to": [{"email": x} for x in tos], "date": at, "text": str(d.get("body") or "")[:1200], "sent_from_home": did}
        # Already in the mail (a seed put the sent note in world_extra.json): never twice.
        if any(base(t.get("subject")) == base(d.get("subject")) and any(
                str(((m.get("from") or {}) if isinstance(m.get("from"), dict) else {}).get("email") or "").lower() == str(me["email"]).lower() and
                str(m.get("date") or "")[:10] == str(at)[:10] and not m.get("sent_from_home") for m in t.get("messages") or [])
               for t in threads.values()):
            continue
        hit = next((t for t in threads.values() if str(d.get("subject") or "").lower().startswith("re:") and base(t.get("subject")) == base(d.get("subject"))), None)
        if hit:
            if not any(m.get("sent_from_home") == did for m in hit.get("messages") or []):
                hit["messages"] = sorted((hit.get("messages") or []) + [msg], key=lambda m: str(m.get("date") or ""))
                hit["date"] = max(_latest(hit), at)
            continue
        tid = f"sent_{did}"
        threads.setdefault(tid, {"id": tid, "subject": d.get("subject") or "(no subject)", "date": at, "labels": ["SENT"], "snippet": msg["text"][:80],
                                 "url": f"https://mail.google.com/mail/u/0/#sent/{tid}",
                                 "participants": [me] + [{"email": x} for x in tos], "messages": [msg]})
    b["threads"] = list(threads.values())
    return b


def with_extra(b: dict) -> dict:
    """The golden world plus this run's world_extra.json: new threads join the mailbox, a reply joins its thread. Drafts
    marked sent in the run's mock Home are in the sent mail too."""
    path = os.path.join(run_dir(), "world_extra.json")
    if not os.path.exists(path):
        return _sent_from_home(b)
    extra = json.load(open(path, encoding="utf-8"))
    if extra.get("now"):  # the eval run's own time: `status` reports it, and `bundle` reads as of it
        b["now"] = extra["now"]
    threads = {t["id"]: t for t in b.get("threads") or []}
    for t in extra.get("threads") or []:
        old = threads.get(t["id"])
        if old is None:
            threads[t["id"]] = t
            continue
        seen = {(m.get("date"), (m.get("from") or {}).get("email")) for m in old.get("messages") or []}
        msgs = (old.get("messages") or []) + [m for m in t.get("messages") or [] if (m.get("date"), (m.get("from") or {}).get("email")) not in seen]
        threads[t["id"]] = {**old, "messages": sorted(msgs, key=lambda m: str(m.get("date") or "")), "date": max(_latest(old), _latest(t))}
    b["threads"] = list(threads.values())
    for key in ("events", "transcripts"):
        have = {x.get("id") for x in b.get(key) or []}
        b[key] = (b.get(key) or []) + [x for x in extra.get(key) or [] if x.get("id") not in have]
    notes = b.setdefault("crm", {}).setdefault("notes", [])
    have = {n.get("id") for n in notes if n.get("id")}
    notes.extend(n for n in extra.get("crm_notes") or [] if not n.get("id") or n.get("id") not in have)
    return _sent_from_home(b)


def as_run_reads(b: dict, now: str, mode: str | None, after: str | None) -> dict:
    """What a run at `now` reads: nothing that has not happened yet, and with `mode`, the windows of its row in
    shared/connectors.md (`after` is the run's window start; a pulse without one reads the last hour)."""
    sys.path.insert(0, HERE)
    import replay  # noqa: E402  (its windows are the ones the multi-run suites check)
    from datetime import timedelta
    from instinct.util import parse_dt, tzinfo  # noqa: E402
    tz = tzinfo(b["tz"])
    t = parse_dt(now, b["tz"])
    cut = []
    for th in b.get("threads") or []:
        msgs = [m for m in th.get("messages") or [] if (parse_dt(m.get("date"), b["tz"]) or t) <= t]
        if msgs:
            cut.append({**th, "messages": msgs, "date": max(str(m.get("date") or "") for m in msgs)})
    b = {**b, "now": t.isoformat(), "threads": cut,
         "transcripts": [x for x in b.get("transcripts") or [] if (parse_dt(x.get("date"), b["tz"]) or t) <= t]}
    if not mode:
        return b
    since = parse_dt(after, b["tz"]) if after and "T" in after else (t - timedelta(days=60) if mode == "setup" else t - timedelta(hours=1))
    out = replay._window_bundle(b, mode, t.astimezone(tz), since, mode == "weekend")
    return shape_as_documented(out, mode, t)


def _home_doc(doc: str) -> dict:
    """A snapshot in this run's mock Home (evals/runs/<run>/db/snap/<doc>.json), or {}."""
    path = os.path.join(run_dir(), "db", "snap", f"{doc}.json")
    if not os.path.exists(path):
        return {}
    raw = json.load(open(path, encoding="utf-8"))
    return raw.get("data") if isinstance(raw, dict) and "data" in raw else raw


def shape_as_documented(b: dict, mode: str, now) -> dict:
    """The bundle as shared/connectors.md says a run writes it, not the whole connector view: CRM changes this run made
    stay made; a morning reads the people and companies that matter today (partial flags), the LP list only with LP
    watch on, and each thread's latest message (and the user's own latest, after it), each up to 600 characters; a
    pulse sends only the deals that differ from Home's pipeline (crm.partial)."""
    from datetime import timedelta
    from instinct.util import parse_dt  # noqa: E402
    b = json.loads(json.dumps(b))
    crm = b.get("crm") or {}
    changes_path = os.path.join(run_dir(), "crm_changes.json")
    changes = json.load(open(changes_path)) if os.path.exists(changes_path) else {}
    if changes:
        crm["deals"] = [{**d, **changes.get(d.get("id"), {})} for d in crm.get("deals") or []]
    cfg = _home_doc("config")
    if (cfg.get("modules") or {}).get("lp") in (None, "off") and mode != "setup":
        b.pop("lps", None)
    if mode not in ("setup", "digest"):
        b.pop("portfolio_kpis", None)
        b.pop("empathy_maps", None)
    me = str((b.get("user") or {}).get("email") or "").lower()
    for th in b.get("threads") or []:
        msgs = sorted(th.get("messages") or [], key=lambda m: str(m.get("date") or ""))
        if not msgs:
            continue
        keep = [msgs[-1]]
        mine = [m for m in msgs if str(((m.get("from") or {}).get("email") if isinstance(m.get("from"), dict) else m.get("from")) or "").lower() == me]
        if mine and mine[-1] is not msgs[-1]:
            keep = [mine[-1], msgs[-1]]
        th["messages"] = [{**m, "text": str(m.get("text") or "")[:600]} for m in keep]
    if mode == "daily":
        open_ = [d for d in crm.get("deals") or [] if str(d.get("stage") or "").lower() not in ("passed", "lost", "declined", "portfolio", "won")]
        cids = {d.get("company_id") for d in open_} | {c.get("id") for c in crm.get("companies") or [] if c.get("status") == "portfolio"}
        day_end = now + timedelta(days=4)
        meet_emails = {str(a.get("email") or "").lower() for e in b.get("events") or [] for a in e.get("attendees") or []
                       if isinstance(a, dict) and now <= (parse_dt(e.get("start"), b.get("tz")) or now - timedelta(days=1)) <= day_end}
        crm["deals"] = open_
        crm["companies"] = [c for c in crm.get("companies") or [] if c.get("id") in cids]
        crm["people"] = [p for p in crm.get("people") or [] if p.get("company_id") in cids or
                         {str(e).lower() for e in [p.get("email")] + list(p.get("emails") or []) if e} & meet_emails]
        crm["companies_partial"] = crm["people_partial"] = True
    if mode in ("pulse", "weekend"):
        pipe = (_home_doc("pipeline").get("deals") or {})
        def differs(d: dict) -> bool:
            h = pipe.get(d.get("id"))
            if not h:
                return True
            return (str(h.get("stage") or "").lower() != str(d.get("stage") or "").lower() or
                    str(h.get("next_step") or "") != str(d.get("next_step") or "") or
                    str(h.get("next_step_due") or "")[:10] != str(d.get("next_step_due") or "")[:10] or
                    str(h.get("crm_last_contact") or "")[:10] != str(d.get("last_contact") or "")[:10])
        crm["deals"] = [d for d in crm.get("deals") or [] if differs(d)]
        crm["partial"] = True
    b["crm"] = crm
    return b


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--as", dest="member", required=True)
    ap.add_argument("connector")
    ap.add_argument("action", nargs="?")
    ap.add_argument("--after")
    ap.add_argument("--before")
    ap.add_argument("--query")
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--id")
    ap.add_argument("--start")
    ap.add_argument("--end")
    ap.add_argument("--deal")
    ap.add_argument("--domain")
    ap.add_argument("--json")
    ap.add_argument("--file")
    ap.add_argument("--collection")
    ap.add_argument("--out-dir", dest="out_dir")
    ap.add_argument("--out")
    ap.add_argument("--if-version", dest="if_version", type=int)
    ap.add_argument("--now")
    ap.add_argument("--mode", choices=["setup", "daily", "pulse", "weekend", "review", "week_ahead", "digest"])
    a = ap.parse_args()
    b = with_extra(json.load(open(os.path.join(GOLD, "bundles", f"{a.member}.json"), encoding="utf-8")))
    world = json.load(open(os.path.join(GOLD, "world.json"), encoding="utf-8"))
    log({"member": a.member, "connector": a.connector, "action": a.action, "id": a.id, "query": a.query})

    if a.connector == "status":
        gmail_tools = ["search_threads", "get_thread", "list_drafts", "get_draft", "update_draft", "send_message", "reply", "forward"]
        if os.environ.get("INSTINCT_MOCK_DRAFTS") == "1":
            gmail_tools.insert(2, "create_draft")
        emit({"now": b["now"], "tz": b["tz"], "user": b["user"], "connectors": states(), "tools": {"gmail": gmail_tools}})
        return 0
    if a.connector == "bundle":
        out = dict(b)
        if a.now or a.mode or os.path.exists(os.path.join(run_dir(), "world_extra.json")):
            out = as_run_reads(out, a.now or b["now"], a.mode, a.after)
        st = states()
        out["unavailable"] = {}
        # A connector that cannot be read is named in `unavailable`, and its data is left out (never an empty list).
        for name, key, label in (("granola", "transcripts", "notes"), ("affinity", "crm", "crm"), ("gmail", "threads", "email"),
                                 ("google calendar", "events", "calendar"), ("carta", "lps", "lps")):
            if st.get(name) != "connected":
                out.pop(key, None)
                out["unavailable"][label] = "missing" if st.get(name) == "missing" else st.get(name)
        if not out["unavailable"]:
            out.pop("unavailable")
        json.dump(out, open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        emit({"written": a.out, "threads": len(out.get("threads") or []), "events": len(out.get("events") or []),
              "transcripts": len(out.get("transcripts") or []), "unavailable": out.get("unavailable") or {}})
        return 0
    if a.connector == "gmail":
        guard("gmail")
        if a.action == "search":
            rows = []
            for t in sorted(b["threads"], key=lambda t: t["date"], reverse=True):
                if a.after and t["date"][:10] < a.after:
                    continue
                if a.before and t["date"][:10] > a.before:
                    continue
                blob = (t["subject"] + " " + " ".join(m["text"] for m in t["messages"])).lower()
                # As Gmail reads a query: from: and to: name a sender or recipient; other words match the subject, the
                # text or a participant's name or address.
                q_ = str(a.query or "").lower()
                froms_ = {str((m.get("from") or {}).get("email") or "").lower() for m in t["messages"] if isinstance(m.get("from"), dict)}
                people_ = " ".join(f"{str(x.get('name') or '').lower()} {str(x.get('email') or '').lower()}" for x in t.get("participants") or [])
                want_from = [w_[5:] for w_ in q_.split() if w_.startswith("from:")]
                want_to = [w_[3:] for w_ in q_.split() if w_.startswith("to:")]
                rest_q = " ".join(w_ for w_ in q_.split() if not w_.startswith(("from:", "to:")))
                if want_from and not any(any(f_ in fe_ for fe_ in froms_) for f_ in want_from):
                    continue
                if want_to and not any(w_ in people_ for w_ in want_to):
                    continue
                if rest_q and rest_q not in blob and rest_q not in people_:
                    continue
                rows.append({"id": t["id"], "subject": t["subject"], "date": t["date"], "participants": t["participants"],
                             "snippet": t["snippet"], "url": t["url"], "labels": t.get("labels", [])})
            emit({"threads": rows[: a.limit], "total": len(rows)})
            return 0
        if a.action == "thread":
            t = next((t for t in b["threads"] if t["id"] == a.id), None)
            emit(t or {"error": "not_found"})
            return 0
        if a.action == "draft":
            # Like the real account's Gmail connector, which has no create-draft tool. INSTINCT_MOCK_DRAFTS=1 adds one.
            if os.environ.get("INSTINCT_MOCK_DRAFTS") != "1":
                log({"write": "gmail_draft_unavailable", "data": a.json})
                emit({"error": "unknown_tool", "message": "This Gmail connector has no create-draft tool. Keep the draft in Home."})
                return 4
            body = json.loads(a.json or "{}")
            n = sum(1 for _ in open(os.path.join(run_dir(), "mock_log.jsonl")))
            log({"write": "gmail_draft", "data": body})
            emit({"draft_id": f"dr{n}", "url": f"https://mail.google.com/mail/u/0/#drafts/dr{n}"})
            return 0
        if a.action in ("send", "reply", "forward"):
            log({"write": "gmail_SEND_ATTEMPT", "action": a.action, "data": a.json})
            emit({"error": "forbidden", "message": "ant. never sends. This attempt is recorded and fails the eval."})
            return 3
    if a.connector == "calendar":
        guard("google calendar")
        if a.action == "create":
            body = json.loads(a.json or "{}")
            log({"write": "calendar_create", "data": body})
            emit({"event_id": "ev_new", "url": "https://calendar.google.com/event?eid=ev_new"})
            return 0
        rows = [e for e in b["events"] if (not a.start or e["start"] >= a.start) and (not a.end or e["start"] <= a.end)]
        emit({"events": sorted(rows, key=lambda e: e["start"])})
        return 0
    if a.connector == "granola":
        guard("granola")
        if a.action == "list":
            rows = [{"id": t["id"], "title": t["title"], "date": t["date"], "attendees": t["attendees"], "url": t["url"], "event_id": t["event_id"]}
                    for t in b["transcripts"] if not a.after or t["date"][:10] >= a.after]
            emit({"meetings": sorted(rows, key=lambda r: r["date"], reverse=True)})
            return 0
        if a.action == "transcript":
            t = next((t for t in b["transcripts"] if t["id"] == a.id), None)
            emit(t or {"error": "not_found"})
            return 0
    if a.connector == "crm":
        guard("affinity")
        crm = b["crm"]
        # Changes this run made to CRM records stay changed: a re-read sees them, as the real CRM would.
        changes_path = os.path.join(run_dir(), "crm_changes.json")
        changes = json.load(open(changes_path)) if os.path.exists(changes_path) else {}
        if a.action == "update":
            data = json.loads(a.json or "{}")
            if not any(d.get("id") == a.id for d in crm.get("deals", []) + crm.get("companies", []) + crm.get("people", [])):
                emit({"error": "not_found"})
                return 3
            changes.setdefault(a.id, {}).update(data)
            json.dump(changes, open(changes_path, "w"), indent=1)
            log({"write": "crm_update", "record": a.id, "data": data})
            emit({"updated": a.id, "fields": sorted(data)})
            return 0
        if a.action == "record":
            rec = next((d for d in crm.get("deals", []) + crm.get("companies", []) + crm.get("people", []) if d.get("id") == a.id), None)
            emit({**rec, **changes.get(a.id, {})} if rec else {"error": "not_found"})
            return 0
        if changes and a.action == "deals":
            crm = {**crm, "deals": [{**d, **changes.get(d.get("id"), {})} for d in crm.get("deals", [])]}
        if a.action == "notes":
            emit({"notes": [n for n in crm.get("notes", []) if not a.deal or n["deal_id"] == a.deal]})
        elif a.action == "passes":  # the pass log: passed deals with the reason and the revisit trigger
            emit({"passes": b.get("passes", []), "system": crm.get("system")})
        else:
            emit({a.action: crm.get(a.action, []), "system": crm.get("system")})
        return 0
    if a.connector == "slack":
        guard("slack")
        emit({"messages": [], "total": 0, "note": "No Slack messages in the fictional fund's workspace."})
        return 0
    if a.connector == "world":
        # Eval only, never inside a run: play the user or the world between runs ("Tara sent the nudge from Gmail",
        # "Aditi replied"). The thread joins this run's world_extra.json, so the next run's reads see it.
        path = os.path.join(run_dir(), "world_extra.json")
        extra = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {"threads": []}
        th = json.loads(a.json or "{}")
        if not th.get("id") or not th.get("messages"):
            emit({"error": "a thread needs an id and messages"})
            return 2
        extra.setdefault("threads", []).append(th)
        json.dump(extra, open(path, "w", encoding="utf-8"), indent=1)
        log({"world": "thread_added", "id": th["id"]})
        emit({"added": th["id"]})
        return 0
    if a.connector == "drive":
        guard("google drive")
        if a.action == "search":
            q = (a.query or "").lower()
            emit({"files": [{"id": d["id"], "name": d["name"], "url": d["url"]} for d in world["drive"] if q in d["name"].lower()]})
        else:
            d = next((d for d in world["drive"] if d["id"] == a.id), None)
            emit(d or {"error": "not_found"})
        return 0
    if a.connector == "market":
        guard("pitchbook")
        comp = next((c for c in world["crm"]["companies"] if c.get("domain") == a.domain), None)
        emit({"domain": a.domain, "found": bool(comp), "name": (comp or {}).get("name"), "hq": (comp or {}).get("hq"),
              "sectors": (comp or {}).get("sectors"), "source_url": f"https://pitchbook.example/profile/{a.domain}"})
        return 0
    if a.connector == "carta":
        guard("carta")
        emit({"lps": b["lps"]})
        return 0
    if a.connector == "schedule":
        if a.action == "list":  # the scheduled tasks this account already has (the resume check)
            made = [e["schedule_created"] for e in _log_rows() if e.get("schedule_created")]
            seeded = json.load(open(os.path.join(run_dir(), "schedules_seeded.json"))) if os.path.exists(os.path.join(run_dir(), "schedules_seeded.json")) else []
            emit({"triggers": [{"name": t.get("name"), "cron_expression": t.get("cron_expression")} for t in seeded + made]})
            return 0
        task = json.loads(a.json or "{}")
        log({"schedule_created": task})
        emit({"trigger_id": f"trig_mock_{abs(hash(task.get('name', ''))) % 10000}", "derived_state": {"permission_mode": "auto"}})
        return 0
    if a.connector == "artifact":
        if a.action == "list":  # the user's artifacts, as the Artifact tool's list action returns them
            have = any(e.get("artifact_published") for e in _log_rows()) or os.path.isdir(os.path.join(run_dir(), "db", "snap"))
            emit({"artifacts": [{"title": "ant. Home", "url": "https://claude.ai/artifact/mock-instinct-home"}] if have else []})
            return 0
        log({"artifact_published": a.file})
        emit({"url": "https://claude.ai/artifact/mock-instinct-home", "subscription": "watching"})
        return 0
    if a.connector == "db":
        db_dir = os.path.join(run_dir(), "db")
        if a.action == "list":
            src = os.path.join(db_dir, a.collection)
            dst = os.path.join(a.out_dir, a.collection)
            os.makedirs(dst, exist_ok=True)
            files, lines = [], []
            if os.path.isdir(src):
                for f in sorted(os.listdir(src)):
                    data = json.load(open(os.path.join(src, f)))
                    json.dump(data, open(os.path.join(dst, f), "w"), indent=1)
                    files.append(os.path.join(dst, f))
                    # The same result line ArtifactData's list prints: paste these into versions.txt.
                    size = len(json.dumps(data.get("data") if isinstance(data, dict) else data))
                    lines.append(f'- "{f[:-5]}"  {size} bytes  version {data.get("version", 1) if isinstance(data, dict) else 1}  "{os.path.join(dst, f)}"')
            emit({"files": files, "lines": lines})
            return 0
        if a.action in ("set", "update", "get"):
            folder = os.path.join(db_dir, a.collection)
            os.makedirs(folder, exist_ok=True)
            path = os.path.join(folder, f"{a.id}.json")
            current = json.load(open(path)) if os.path.exists(path) else None
            if a.action == "get":
                emit(current or {"error": "not_found"})
                return 0 if current else 3
            body = json.load(open(a.file)) if a.file else json.loads(a.json or "{}")
            # As ArtifactData does: a write to a document that exists needs its current version.
            if current and a.if_version != current["version"]:
                emit({"error": "version_conflict", "doc": a.id, "current_version": current["version"],
                      "hint": "read the document again and write once more with its version"})
                return 4
            if a.action == "update":
                if not current:
                    emit({"error": "not_found"})
                    return 3
                merged = dict(current["data"])
                for k, v in body.items():
                    if isinstance(v, dict) and isinstance(merged.get(k), dict):
                        merged[k] = {**merged[k], **v}
                    else:
                        merged[k] = v
                body = merged
            version = (current["version"] + 1) if current else 1
            json.dump({"data": body, "version": version}, open(path, "w"), indent=1)
            emit({"doc_id": a.id, "version": version})
            return 0
        if a.action == "batch":
            plan = json.load(open(a.file))
            writes = plan.get("writes") or [w for bt in plan.get("batches", []) for w in bt["writes"]]
            done = []
            for w in writes:
                folder = os.path.join(db_dir, w["collection"])
                os.makedirs(folder, exist_ok=True)
                path = os.path.join(folder, f"{w['doc_id']}.json")
                current = json.load(open(path)) if os.path.exists(path) else None
                if current and w.get("if_version") != current["version"]:
                    emit({"error": "version_conflict", "doc": w["doc_id"], "current_version": current["version"]})
                    return 4
                body = json.load(open(w["file_path"])) if w.get("file_path") else w.get("data")
                version = (current["version"] + 1) if current else 1
                json.dump({"data": body, "version": version}, open(path, "w"), indent=1)
                done.append({"doc_id": w["doc_id"], "version": version})
            emit({"written": done})
            return 0
    emit({"error": "unknown command"})
    return 2


if __name__ == "__main__":
    sys.exit(main())
