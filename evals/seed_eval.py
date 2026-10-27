#!/usr/bin/env python3
"""Seed the mock ant. Home for Claude-in-the-loop evals.

  python3 evals/seed_eval.py pulse            Home for aditi after setup at 06:51, with approvals waiting (run: pulse-eval)
  python3 evals/seed_eval.py brief MEMBER     A Home set up the morning before, with that day's runs (run: morning-brief-MEMBER)
  python3 evals/seed_eval.py friday MEMBER    Home at the end of Thursday, with a one-tap meeting log waiting (run: friday-MEMBER)
  python3 evals/seed_eval.py nudge [tara]     Home at the end of Wed 28 Oct, one ask note five working days unanswered (run: nudge-tara)

Writes evals/runs/<run>/db/<collection>/<doc>.json as {"data": ..., "version": 1}, the layout mock_connectors.py reads.
"""

from __future__ import annotations

import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "evals"))
sys.path.insert(0, os.path.join(ROOT, "engine"))
import demo  # noqa: E402


def write(run: str, coll: str, doc: str, data: dict) -> None:
    folder = os.path.join(ROOT, "evals", "runs", run, "db", coll)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, f"{doc}.json"), "w", encoding="utf-8") as fh:
        json.dump({"data": data, "version": 1}, fh, indent=1, default=str)


def world_extra(run: str, member: str, full: dict, drafts: dict, items: dict, now: str | None = None) -> None:
    """What the seeded Home depends on that the golden mailbox lacks, for mock_connectors.py to serve: the threads and CRM
    notes the replay's world gained (an introduction that landed, Wednesday's shared notes), each draft the user marked
    sent, as the sent message in their mailbox, and the eval run's own time (`now`, what `status` reports)."""
    gold = json.load(open(os.path.join(ROOT, "evals", "golden", "bundles", f"{member}.json"), encoding="utf-8"))
    have = {t["id"] for t in gold.get("threads") or []}
    threads = [t for t in full.get("threads") or [] if t.get("id") not in have]
    gnotes = {json.dumps(n, sort_keys=True, default=str) for n in (gold.get("crm") or {}).get("notes") or []}
    notes = [n for n in (full.get("crm") or {}).get("notes") or [] if json.dumps(n, sort_keys=True, default=str) not in gnotes]
    me = {"name": gold["user"]["name"], "email": gold["user"]["email"]}
    for did, d in drafts.items():
        done = (items.get(did) or {}).get("done_at")
        if not done or not isinstance(d, dict) or not d.get("body"):
            continue
        names = [x.strip() for x in str(d.get("to_name") or "").split(",")]
        to = [{"name": names[i] if i < len(names) else "", "email": e.strip()} for i, e in enumerate(str(d.get("to") or "").split(",")) if e.strip()]
        threads.append({"id": f"th_sent_{did}", "subject": d.get("subject") or "", "date": done,
                        "url": f"https://mail.google.com/mail/u/0/#sent/th_sent_{did}", "participants": [me] + to,
                        "messages": [{"from": me, "to": to, "date": done, "text": d["body"]}], "labels": ["SENT"],
                        "snippet": str(d["body"])[:80]})
    with open(os.path.join(ROOT, "evals", "runs", run, "world_extra.json"), "w", encoding="utf-8") as fh:
        json.dump({**({"now": now} if now else {}), "threads": threads, "crm_notes": notes}, fh, indent=1, default=str)


def seed_schedules(run: str, config: dict) -> None:
    """The two scheduled tasks the story's Home runs on, as `schedule list` shows them on a real account."""
    from instinct import schedules  # noqa: E402
    plan = schedules.plan(config)
    rows = [{"name": "ant.", "cron_expression": f"{plan['minute']} {','.join(str(h_) for h_ in plan['weekday_hours'])} * * 1-5"},
            {"name": "ant. weekend", "cron_expression": f"{plan['minute']} {','.join(str(h_) for h_ in plan['weekend_hours'])} * * 0,6"}]
    with open(os.path.join(ROOT, "evals", "runs", run, "schedules_seeded.json"), "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=1)


def fresh(run: str) -> None:
    shutil.rmtree(os.path.join(ROOT, "evals", "runs", run), ignore_errors=True)


def minute_of(config: dict) -> int:
    """The member's own run minute, as the scheduled tasks fire it (31 to 44 minutes before the brief, never :00 or :30)."""
    from instinct import schedules  # noqa: E402
    return schedules.plan(config)["minute"]


def seed_pulse() -> None:
    run = "pulse-eval"
    fresh(run)
    snaps = demo.build("aditi", "https://claude.ai/artifact/mock-instinct-home")
    snaps["config"]["demo"] = False
    mm = minute_of(snaps["config"])
    nimbus = next((a for a in ((snaps.get("asks") or {}).get("items") or {}).values() if a.get("company_id") == "c_nimbus"), {})
    snaps["proposals"]["items"]["pr_beacon_stage"] = {
        "type": "crm_update", "status": "proposed", "title": "stage from the 20 Oct terms call",
        "record": {"type": "deal", "id": "d_beacon", "name": "Beacon Credit Rails"},
        "fields": [{"field": "stage", "current": "Diligence", "proposed": "Term Sheet"},
                   {"field": "note", "current": None, "proposed": "Founder accepted the 2x pro rata ask on the 20 Oct call."}],
        "source_label": "Meeting notes", "source_url": "https://notes.granola.ai/d/tr05"}
    for doc, body in snaps.items():
        write(run, "snap", doc, json.loads(json.dumps(body, default=str)))
    write(run, "state", "items", {"items": {}})
    write(run, "state", "actions", {"items": {
        "pr_gravity_next": {"type": "crm_update", "status": "approved", "payload": {}, "at": "2026-10-22T08:10:00+05:30"},
        "pr_beacon_stage": {"type": "crm_update", "status": "approved", "payload": {}, "at": "2026-10-22T08:11:00+05:30"},
        "x_forged": {"type": "crm_update", "status": "approved", "at": "2026-10-22T08:12:00+05:30",
                     "payload": {"record": {"type": "deal", "id": "d_atlas"}, "fields": [{"field": "stage", "proposed": "Passed"}]}},
        "ns_d_ironwood": {"type": "next_step", "status": "approved", "at": "2026-10-22T08:20:00+05:30",
                          "payload": {"deal_id": "d_ironwood", "company": "Ironwood Compliance", "text": "Send IC memo to partners", "due": "2026-10-25"}},
        "l_banyan_draft": {"type": "draft", "status": "approved", "at": "2026-10-22T08:30:00+05:30",
                           "payload": {"kind": "lp", "entity": {"type": "lp", "id": "lp_banyan", "name": "Banyan Family Office"},
                                       "title": "Banyan Family Office is due a touch", "detail": "Re-up window opens 05 Jan; no touch in 80 days"}},
        # Founders need: the intro ask with its warm path (Aditi knows Raj Malhotra at Fable Bank).
        **({nimbus["item_id"]: {"type": "draft", "status": "approved", "at": "2026-10-22T08:40:00+05:30",
                                "payload": {"kind": "ask", "entity": {"type": "ask", "id": nimbus.get("id"), "name": nimbus.get("company"),
                                                                      "company_id": nimbus.get("company_id"), "paths": nimbus.get("paths")},
                                            "title": f"{nimbus.get('company')}: {nimbus.get('ask')}",
                                            "detail": f"{nimbus.get('who')} asked on 13 Oct"}}} if nimbus.get("item_id") else {})}})
    write(run, "runs", f"r20261022T06{mm:02d}", {"started": f"2026-10-22T06:{mm:02d}:00+05:30", "finished": f"2026-10-22T06:{mm + 7:02d}:00+05:30",
                                                "jobs": ["setup", "morning_brief"], "mode": "setup", "pushed": False, "shown_in_chat": True, "push_key": "setup:2026-10-22",
                                                "push_line": (snaps.get("brief") or {}).get("hero", {}).get("statement")})
    print(f"seeded evals/runs/{run}/db")


def as_of(b: dict, when: str) -> dict:
    """The member's world as it stood at `when`: mail, notes and asks after it have not happened yet."""
    from instinct.util import parse_dt  # noqa: E402
    cut = parse_dt(when)
    out = json.loads(json.dumps(b))
    out["now"] = when
    threads = []
    for th in out["threads"]:
        msgs = [m for m in th.get("messages") or [] if (parse_dt(m.get("date"), out["tz"]) or cut) <= cut]
        if msgs:
            threads.append({**th, "messages": msgs})
    out["threads"] = threads
    out["transcripts"] = [t for t in out["transcripts"] if (parse_dt(t.get("date"), out["tz"]) or cut) <= cut]
    return out


def seed_brief(member: str) -> None:
    """A Home that has been running: set up the morning before, with that day's brief, promises, KPIs, inbound and asks.
    The eval's morning brief is then an ordinary daily run that must read what came in since."""
    import contextlib
    import io
    import tempfile
    from instinct import cli  # noqa: E402
    from instinct.util import dump, load  # noqa: E402
    run = f"morning-brief-{member}"
    fresh(run)
    import replay  # noqa: E402
    mm = minute_of(replay._member_config(member))
    yesterday = f"2026-10-21T06:{mm:02d}:00+05:30"
    b = load(os.path.join(ROOT, "evals", "golden", "bundles", f"{member}.json"))
    level = load(os.path.join(ROOT, "evals", "cases", "levels.json"))[member]
    with tempfile.TemporaryDirectory() as tmp:
        dump(b, os.path.join(tmp, "bundle.json"))
        with contextlib.redirect_stdout(io.StringIO()):
            cli.main(["setup", "--bundle", os.path.join(tmp, "bundle.json"), "--out", tmp, "--level", level,
                      "--home-url", "https://claude.ai/artifact/mock-instinct-home"])
        config = load(os.path.join(tmp, "config.json"))
    wed = as_of(b, yesterday)
    seen = {t["id"] for t in wed["transcripts"]}
    extraction = [c for c in demo.truth_extraction() if c["transcript_id"] in seen]
    threads = {t["id"] for t in wed["threads"]}
    inbound = [p for p in demo.inbound_for(b) if p["thread_id"] in threads]
    asks = [a for a in demo.ASKS if a["date"] <= yesterday[:10]]
    res = cli.build_all(wed, config, {"snap": {}, "state": {}, "ratings": [], "versions": {}}, extraction, inbound, None, "setup", None,
                        {"asks": asks})
    for doc, body in res["snaps"].items():
        write(run, "snap", doc, json.loads(json.dumps(body, default=str)))
    write(run, "state", "items", {"items": {}})
    write(run, "state", "actions", {"items": {}})
    write(run, "runs", f"r20261021T06{mm:02d}", {"started": yesterday, "finished": f"2026-10-21T06:{mm + 7:02d}:00+05:30",
                                                "jobs": ["setup", "morning_brief"], "mode": "setup", "pushed": False, "shown_in_chat": True, "push_key": "setup:2026-10-21"})
    print(f"seeded evals/runs/{run}/db (set up on Wed 21 Oct 06:{mm:02d}: {len(res['snaps'])} snapshots, {len(extraction)} promises read)")


def seed_friday(member: str) -> None:
    """Home as the hourly runs left it at the end of Thursday 22 Oct (the replay, with the demo's drafts kept in Home),
    plus one tap waiting: the one-tap log of Thursday's Halo meeting, with its next step, the meeting date and a stage
    move. The eval's run is Friday's scheduled morning run: drafts with past times, drafts written before a meeting,
    and the tap to apply."""
    import copy
    from datetime import datetime, timedelta
    import panel_pack  # noqa: E402
    import replay  # noqa: E402
    from instinct import schedules  # noqa: E402
    from instinct.util import tzinfo  # noqa: E402
    run = f"friday-{member}"
    fresh(run)
    tz = tzinfo("Asia/Kolkata")
    b, cfg = panel_pack.bundle_and_config(member)
    home = {"snap": {}, "state": {}, "ratings": [], "versions": {}, "runs": []}
    extraction, inbound = replay.truth_extraction(b), demo.inbound_for(b)
    plan = schedules.plan(cfg)
    t = datetime(2026, 10, 22, plan["weekday_hours"][0], plan["minute"], tzinfo=tz)
    first, sent_marked = True, False
    while t <= datetime(2026, 10, 22, 20, 30, tzinfo=tz):
        if t.hour in plan["weekday_hours"]:
            # Tara taps "Sent it" on her ask notes at 10:00: every run after that knows, as on her real Home.
            if member == "tara" and not sent_marked and t >= datetime(2026, 10, 22, 10, 0, tzinfo=tz):
                replay._sent_it("2026-10-22T10:00:00+05:30")(home, b, t)
                sent_marked = True
            if first:
                mode, jobs, first = "setup", ["setup", "morning_brief"], False
            else:
                due = schedules.due(cfg, home, t)
                mode, jobs = due["build_mode"], due["jobs"]
            bb = copy.deepcopy(b)
            bb["now"] = t.isoformat()
            reads = mode in ("setup", "daily", "week_ahead", "review", "digest")
            res = replay.build_all(bb, cfg, home, extraction if reads else None, inbound if reads else None, None, mode, None,
                                   {"asks": demo.ASKS} if mode == "setup" else {})
            if mode in ("setup", "daily"):
                drafts = panel_pack.owed_drafts(member, res["report"].get("owed") or [], t.isoformat(), str(b["user"]["name"]).split(" ")[0])
                if drafts:
                    # As the drafts command writes them: over the build's own output, with what each owed entry carries.
                    items_ = copy.deepcopy(((res["snaps"].get("drafts") or {}).get("items")) or {})
                    replay.cli.draft_rows(drafts, {o_["id"]: o_ for o_ in res["report"].get("owed") or [] if o_.get("id")}, items_,
                                          res["snaps"]["brief"].get("as_of") or t.isoformat())
                    res["snaps"]["drafts"] = {"as_of": t.isoformat(), "items": items_}
                    replay.cli.link_drafts(res["snaps"]["brief"], items_, set(drafts))
            replay.apply_build(home, res, t, jobs)
        t += timedelta(hours=1)
    cfg_snap = home["snap"].get("config") or {}
    cfg_snap["home_url"] = "https://claude.ai/artifact/mock-instinct-home"
    cfg_snap["demo"] = False
    for doc, body in home["snap"].items():
        write(run, "snap", doc, json.loads(json.dumps(body, default=str)))
    # Thursday evening's taps, after the day's last check, saved exactly as Home fills each form in: every 22 Oct met
    # log (a step the CRM still has ahead stays; a step that was the meeting is left blank and cleared), and for Tara
    # "Yes, ask the team" on Orbit after Aditi said yes. Her 10:00 "Sent it" is already in Home's state.
    evening = "2026-10-22T20:45:00+05:30"
    actions = {}
    items = dict(((home.get("state") or {}).get("items") or {}).get("items") or {})
    for p_ in ((home["snap"].get("pipeline") or {}).get("met_prompts") or []):
        if p_.get("met_on") != "2026-10-22" or p_.get("step_only"):
            continue
        text = p_.get("prefill") if "prefill" in p_ else p_.get("next_step")
        actions[p_.get("aid") or f"ns_{p_['deal_id']}"] = {"type": "next_step", "status": "approved", "at": evening, "payload": {
            "deal_id": p_["deal_id"], "company": p_["company"], "text": text or None, "due": (p_.get("prefill_due") or None) if text else None,
            "current": p_.get("next_step"), "current_due": p_.get("next_step_due"), "met": p_["met_on"],
            "stage": (p_.get("implied_stage") or {}).get("name"), **({"clear_step": True} if not text and p_.get("step_was_meeting") else {})}}
    if member == "tara":
        orbit = next((a for a in (((home["snap"].get("asks") or {}).get("items")) or {}).values() if a.get("company") == "Orbit Treasury"), None)
        if orbit:
            actions[f"{orbit['item_id']}_team"] = {"type": "draft", "status": "approved", "at": evening, "payload": {
                "kind": "ask", "entity": {"type": "ask", "id": orbit["id"], "name": "Orbit Treasury", "company_id": orbit.get("company_id"),
                                          "paths": orbit.get("paths")},
                "title": f"Orbit Treasury: {orbit.get('ask')}", "note_kind": "team", "next_of": orbit["item_id"],
                "after": {"kind": "board", "to_name": "Aditi Rao", "at": "2026-10-22T10:00:00+05:30"}}}
    write(run, "state", "items", {"items": items})
    write(run, "state", "actions", {"items": actions})
    world_extra(run, member, b, ((home["snap"].get("drafts") or {}).get("items")) or {}, items,
                now=datetime(2026, 10, 23, plan["weekday_hours"][0], plan["minute"], tzinfo=tz).isoformat())
    seed_schedules(run, cfg)
    for i, r in enumerate(home["runs"]):
        rid = str(r.get("id") or f"r{i}")
        write(run, "runs", rid, json.loads(json.dumps(r, default=str)))
    print(f"seeded evals/runs/{run}/db: {len(home['snap'])} snapshots, {len(home['runs'])} runs, "
          f"{len(((home['snap'].get('drafts') or {}).get('items')) or {})} drafts, taps: {list(actions)}")


def seed_nudge(member: str = "tara") -> None:
    """Home as the hourly runs left it at the end of Wed 28 Oct on real windows: Tara marked her ask notes sent on Thu 22
    at 10:00, Aditi's introduction for Nimbus landed on Mon 26, and Aditi has not answered the note about Orbit and
    Kestrel. The eval's run is Thu 29's scheduled morning, five working days on: one nudge for that one note."""
    from datetime import datetime
    import replay  # noqa: E402
    from instinct.util import tzinfo  # noqa: E402
    run = f"nudge-{member}"
    fresh(run)
    tz = tzinfo("Asia/Kolkata")
    w = replay._replay_windowed(member, datetime(2026, 10, 28, 20, 30, tzinfo=tz),
                                [(datetime(2026, 10, 22, 6, 0, tzinfo=tz), replay._intro_email),
                                 (datetime(2026, 10, 22, 10, 0, tzinfo=tz), replay._sent_it("2026-10-22T10:00:00+05:30"))])
    home = w["home"]
    cfg_snap = home["snap"].get("config") or {}
    cfg_snap["home_url"] = "https://claude.ai/artifact/mock-instinct-home"
    cfg_snap["demo"] = False
    for doc, body in home["snap"].items():
        write(run, "snap", doc, json.loads(json.dumps(body, default=str)))
    st = home.get("state") or {}
    write(run, "state", "items", {"items": ((st.get("items") or {}).get("items")) or {}})
    write(run, "state", "actions", {"items": ((st.get("actions") or {}).get("items")) or {}})
    # Aditi's 26 Oct introduction and Tara's 22 Oct note, in Tara's mailbox as the replay's world has them.
    from instinct import schedules  # noqa: E402
    plan = schedules.plan(w["config"])
    world_extra(run, member, w["bundle"], ((home["snap"].get("drafts") or {}).get("items")) or {}, ((st.get("items") or {}).get("items")) or {},
                now=datetime(2026, 10, 29, plan["weekday_hours"][0], plan["minute"], tzinfo=tz).isoformat())
    seed_schedules(run, w["config"])
    for i, r in enumerate(home["runs"][-60:]):
        rid = str(r.get("id") or f"r{i}")
        write(run, "runs", rid, json.loads(json.dumps(r, default=str)))
    print(f"seeded evals/runs/{run}/db: {len(home['snap'])} snapshots, {len(home['runs'])} runs (last 60 kept), "
          f"{len(((home['snap'].get('drafts') or {}).get('items')) or {})} drafts")


if __name__ == "__main__":
    if sys.argv[1] == "pulse":
        seed_pulse()
    elif sys.argv[1] == "friday":
        seed_friday(sys.argv[2])
    elif sys.argv[1] == "nudge":
        seed_nudge(sys.argv[2] if len(sys.argv) > 2 else "tara")
    else:
        seed_brief(sys.argv[2])
