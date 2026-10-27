"""What each panel member sees, written out for the VC panel: Today at 07:00, the drafts waiting in Gmail, the partner
pack, every push from Thursday to Monday (hourly runs replayed through the real `due` scheduler) and each tab's hero.

    python3 evals/panel_pack.py [--out evals/runs/council/briefs-r4]

Members are the six people of the fictional Quillwater Ventures plus "solo": Aditi's world run as a solo GP (no partners,
every pitch in her inbox), so a Solo GP has a page of their own to judge. On Wednesday evening each deal owner tapped
Share on their competing funds, so the CRM holds those notes and every member's ant. reads them (demo.shared_notes).
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from datetime import datetime, timedelta

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
sys.path.insert(0, os.path.join(ROOT, "evals"))

import demo  # noqa: E402
import replay  # noqa: E402
from instinct import brief as brief_mod  # noqa: E402
from instinct import cli, schedules  # noqa: E402
from instinct.util import load, tzinfo  # noqa: E402

MEMBERS = ["aditi", "kabir", "meera", "rohan", "tara", "vikram", "solo"]
TABS = {"pipeline": "Pipeline", "people": "People", "portfolio": "Portfolio", "lps": "LPs"}


def solo_bundle() -> dict:
    return demo.solo_bundle()


def bundle_and_config(member: str) -> tuple[dict, dict]:
    if member == "solo":
        b = solo_bundle()
        cfg = replay._member_config("aditi")
        prof = replay.PROFILES["profiles"]["solo_gp"]
        cfg.update({"level": "solo_gp", "today_items": prof["today_items"], "brief_words": prof["brief_words"], "weights": dict(prof["weights"]),
                    "modules": dict(prof["modules"]), "pipeline_scope": prof["pipeline_scope"], "opens_on": prof["opens_on"],
                    "thesis": b.get("thesis"), "quota": prof.get("quota"),
                    "firm_members": [m for m in cfg.get("firm_members") or [] if m.get("email") == b["user"]["email"]]})
        return b, cfg
    b = replay._bundle(member)
    b.setdefault("crm", {}).setdefault("notes", []).extend(demo.shared_notes())  # Wednesday's shared competing funds
    cfg = replay._member_config(member)
    cfg["opens_on"] = replay.PROFILES["profiles"][cfg["level"]]["opens_on"]
    return b, cfg


def owed_drafts(member: str, owed: list[dict], now_iso: str, user_first: str | None = None) -> dict:
    """The drafts the morning brief writes before the brief time: the demo's hand-written ones where they exist, a
    sourced template for the rest. Kept in Home, as on a Gmail connector with no create-draft tool (this account's)."""
    return demo.demo_drafts("aditi" if member == "solo" else member, owed, now_iso, user_first)


def replay_week(member: str) -> dict:
    b, cfg = bundle_and_config(member)
    tz = tzinfo(b["tz"])
    home = {"snap": {}, "state": {}, "ratings": [], "versions": {}, "runs": []}
    extraction = replay.truth_extraction(b)
    inbound = demo.inbound_for(b)
    pushes, drafted, first = [], [], None
    partner_packs: dict[str, dict] = {}  # each partner meeting's pack as the last run before it saw it
    plan = schedules.plan(cfg)  # the user's own run minute and hours, as the two scheduled tasks fire them
    t = datetime(2026, 10, 22, plan["weekday_hours"][0], plan["minute"], tzinfo=tz)
    end = datetime(2026, 10, 26, 20, 0, tzinfo=tz)
    while t <= end:
        weekend = t.weekday() >= 5
        on = (t.hour in plan["weekend_hours"]) if weekend else (t.hour in plan["weekday_hours"])
        if not on:
            t += timedelta(hours=1)
            continue
        if first is None:
            mode, jobs = "setup", ["setup", "morning_brief"]
        else:
            due = schedules.due(cfg, home, t, weekend_prompt=weekend)
            mode, jobs = due["build_mode"], due["jobs"]
        bb = copy.deepcopy(b)
        bb["now"] = t.isoformat()
        reads = mode in ("setup", "daily", "week_ahead", "review", "digest")
        extras = {"asks": demo.ASKS} if mode == "setup" else {}
        res = cli.build_all(bb, cfg, home, extraction if reads else None, inbound if reads else None, None, mode, None, extras)
        if mode in ("setup", "daily"):
            d = owed_drafts(member, res["report"].get("owed") or [], t.isoformat(), str(b["user"]["name"]).split(" ")[0])
            if d:
                res["snaps"]["drafts"] = {"as_of": t.isoformat(), "items": {**(((home["snap"].get("drafts") or {}).get("items")) or {}), **d}}
                cli.link_drafts(res["snaps"]["brief"], res["snaps"]["drafts"]["items"], set(d))
                for doc_ in ("asks", "portfolio"):  # as the drafts command does
                    cli.ready_hero(res["snaps"].get(doc_), set(d), res["snaps"]["drafts"]["items"])
                nl_ = cli.push_after_drafts(res["report"]["push"], res["snaps"]["brief"], set(d))
                if nl_:
                    res["report"]["push"]["line"] = nl_
                    res["report"]["push_line"] = res["report"]["run_row"]["push_line"] = nl_
                drafted.append((t.strftime("%a %H:%M"), [f"{x.get('to_name')}: {x.get('subject')}" for x in d.values()]))
        replay.apply_build(home, res, t, jobs)
        for c in ((res["snaps"].get("prep") or {}).get("cards") or {}).values():
            if c.get("kind") == "partner" and (replay.parse_dt(c.get("start")) or t) >= t:
                partner_packs[c["meeting_id"]] = {"start": c.get("start"), "title": c.get("title"), "finding": c.get("finding"),
                                                  "decisions": [{"company": d["company"], "why": d["why"], "owner": d.get("owner")}
                                                                for d in c.get("decisions") or []]}
        p = res["report"]["push"]
        if p["send"]:
            pushes.append(f"{t.strftime('%a %H:%M')} ({mode}): {p['line']}")
        if first is None:
            first = json.loads(json.dumps(res, default=str))
        t += timedelta(hours=1)
    return {"first": first, "pushes": pushes, "drafted": drafted, "config": cfg, "bundle": b, "partner_packs": partner_packs}


def tab_hero(snaps: dict, key: str) -> str:
    h = (snaps.get(key) or {}).get("hero") or {}
    return f"{h.get('statement')} | {h.get('finding')}" if h else "(none)"


def write_pack(member: str, out_dir: str) -> str:
    rep = replay_week(member)
    res, cfg = rep["first"], rep["config"]
    snaps, b = res["snaps"], res["brief"]
    level = cfg["level"]
    label = replay.PROFILES["profiles"][level]["label"]
    mods = cfg.get("modules") or {}
    tabs = ["Today"] + [v for k, v in TABS.items() if mods.get({"lps": "lp"}.get(k, k), "on") != "off"]
    name = rep["bundle"]["user"]["name"] + (" (as a solo GP)" if member == "solo" else "")
    hero = b["hero"]
    urgent = bool(hero.get("breach")) or hero.get("status_word") == "overdue" or "overdue" in str(hero.get("kicker") or "").lower() or \
        str(hero.get("kicker") or "").startswith("In ")
    lines = [f"# {name}, {label}, at Quillwater Ventures (fictional)", "",
             f"Tabs shown: {', '.join(tabs)}. Opens on: {'Today (the top item is urgent)' if urgent else cfg.get('opens_on')}.", "",
             f"## Home: Today after the first run, Thursday {str(b.get('as_of') or '')[11:16]}", "",
             f"Hero: {hero.get('kicker')} | {hero.get('statement')} | {hero.get('finding')}" +
             (" | button: Open draft" if hero.get("draft") else f" | button: {hero.get('button')}" if hero.get("button") else ""), "",
             "Agenda:"]
    for m in b["meetings"]:
        lines.append(f"- {m['time']} {m['who']}" + (" (internal)" if m.get("internal") else "") + (" [Prep]" if m.get("prep_id") else ""))
        for n, d in zip(m.get("notes") or [], (m.get("note_drafts") or []) + [None] * 3):
            lines.append(f"  - {n}" + (" · draft ready" if d else ""))
    if b.get("tomorrow"):
        lines.append("Tomorrow: " + "; ".join(f"{m['time']} {m['who']}" for m in b["tomorrow"]))
    lines.append("")
    for sec in b["sections"]:
        lines.append(f"### {sec['label']}")
        for it in sec["items"]:
            lines.append(f"- [{it.get('status_word')}] {it['title']}: {it['detail']}" + (" · Draft ready" if it.get("draft") else "") +
                         f" [{(it.get('source') or {}).get('label')}]")
        lines.append("")
    drafts = ((snaps.get("drafts") or {}).get("items")) or {}
    props = ((snaps.get("proposals") or {}).get("items")) or {}
    if drafts or props:
        lines.append("### Ready for you (drafts ready to send, changes waiting for a tap)")
        for d in drafts.values():
            lines.append(f"- Draft to {d.get('to_name')}: {d.get('subject')}. {d.get('context') or ''}" +
                         (" (in Gmail drafts)" if d.get("in_gmail") else " (in Home: Open in Gmail fills a new message)"))
            lines.append("  > " + str(d.get("body") or "").replace("\n\n", " / ").replace("\n", " / ")[:400])
        for p in props.values():
            lines.append(f"- CRM change: {(p.get('record') or {}).get('name')}: {p.get('title')}")
        lines.append("")
    lines.append(b.get("evidence") or "")
    pack = next((c for c in snaps["prep"]["cards"].values() if c.get("kind") == "partner"), None)
    if pack:
        lines += ["", f"## Partner pack: {pack['time']} {pack['who']}", "", pack.get("finding") or ""]
        for r in pack.get("decisions") or []:
            # As Home shows each row, the same for every attendee: lead, sponsoring partner, round and size.
            first = lambda n: str(n).split(" ")[0] if n else None  # noqa: E731
            size = cli.money(r["raise_usd"]) if r.get("raise_usd") else None
            facts = " · ".join(x for x in [f"Lead: {first(r.get('owner'))}" if r.get("owner") else None,
                                           f"Partner: {first(r.get('partner'))}" if r.get("partner") and r.get("partner") != r.get("owner") else None,
                                           " ".join(x for x in (r.get("round"), size) if x) or None] if x)
            label = "Urgent: " if r.get("urgent") else "Stalled: " if r.get("kind") == "stalled" else ""
            lines.append(f"- {label}{r['company']}" + (f" ({r['stage']})" if r.get("stage") else "") +
                         f": {str(r['why']).rstrip('.')}." + (f" {facts}" if facts else ""))
        for q in (pack.get("question_seeds") or [])[:3]:
            lines.append(f"- Ask: {q}")
    lines += ["", "## Copy brief (plain text, quiet deals left out)", "", "```", res["brief"].get("shareable_text") or "", "```", "",
              "## Emails drafted into Gmail before the brief (each morning)", ""]
    for when, items in rep["drafted"]:
        lines.append(f"- {when}: " + ("; ".join(items) if items else "none"))
    if not rep["drafted"]:
        lines.append("- none: nothing owed was an email")
    lines += ["", "## Pushes from Thu 22 Oct to Mon 26 Oct (hourly runs replayed through the real scheduler)", ""]
    lines += [f"- {p}" for p in rep["pushes"]] or ["- none"]
    lines += ["", "## Tab heroes", ""]
    for key, title in (("pipeline", "Pipeline"), ("people", "People"), ("portfolio", "Portfolio"), ("lps", "LPs"), ("asks", "Founders need")):
        lines.append(f"- {title}: {tab_hero(snaps, key)}")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{member}.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "evals", "runs", "council", "briefs-r4"))
    ap.add_argument("--only")
    a = ap.parse_args()
    for m in (a.only.split(",") if a.only else MEMBERS):
        print(write_pack(m, a.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
