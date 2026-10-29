"""Stress checks for the 0.10 / 0.11 engine pieces: timelines, notes, reminders, people rows, prep note ids, the lint's
manifest exception, and the demo build. QA specialist 4 (data pipelines, fuzzing).

    python3 evals/stress/engine_fuzz.py

Each check PASSES when the engine behaves as promised, so a FAIL line is a bug. Exits 0 either way.
"""

from __future__ import annotations

import contextlib
import copy
import io
import json
import os
import random
import sys
import tempfile
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "engine"))
sys.path.insert(0, os.path.join(ROOT, "evals"))

import demo  # noqa: E402
from instinct import cli, homedb, safety, timeline  # noqa: E402
from instinct import graph as G  # noqa: E402
from instinct.resolve import resolve_people  # noqa: E402
from instinct.util import parse_dt  # noqa: E402

RESULTS: list[tuple[bool, str, str]] = []
NOW = parse_dt("2026-10-22T07:00:00+05:30")
GOLD = json.load(open(os.path.join(ROOT, "evals", "golden", "bundles", "aditi.json"), encoding="utf-8"))
LIMIT = homedb.MAX_DOC_BYTES


def check(name: str):
    def deco(fn):
        try:
            ok, why = fn()
        except Exception as e:  # a raise is a failure, with where it came from
            tb = traceback.extract_tb(e.__traceback__)[-1]
            ok, why = False, f"raised {e!r} at {os.path.basename(tb.filename)}:{tb.lineno} {tb.name}"
        RESULTS.append((bool(ok), name, why or ""))
        print(("PASS" if ok else "FAIL"), name, ("- " + why) if why and not ok else "")
        return fn
    return deco


def doc_bytes(doc) -> int:
    """Bytes as homedb measures and stores a document (compact JSON, UTF-8)."""
    return len(json.dumps(doc, ensure_ascii=False, default=str).encode())


def ctx_of(b):
    return G.build(b, resolve_people(b))


CTX = ctx_of(GOLD)
RAJ = "raj.malhotra@fablebank.in"
_CFG = None


def config():
    global _CFG
    if _CFG is None:
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "b.json")
            json.dump(GOLD, open(p, "w"))
            with contextlib.redirect_stdout(io.StringIO()):
                cli.main(["setup", "--bundle", p, "--out", tmp, "--level", "partner", "--home-url", "x"])
            _CFG = json.load(open(os.path.join(tmp, "config.json")))
    return _CFG


def build_all(b, home=None):
    home = home or {"snap": {}, "state": {}, "ratings": [], "versions": {}}
    return cli.build_all(b, config(), home, demo.truth_extraction(), demo.inbound_for(GOLD), None, "pulse", None, {})


def events(tl: dict):
    for i in range(timeline.SHARDS):
        for k, evs in ((tl.get(f"timeline_{i}") or {}).get("items") or {}).items():
            for e in evs:
                yield i, k, e


def hostile_bundle():
    """The golden bundle plus every shape a connector or Claude might hand over that is odd but not malformed JSON."""
    b = copy.deepcopy(GOLD)
    uni = "Ünïcødé 名前 مرحبا 🚀 "
    th = b["threads"]
    th.append({"id": "fz_nomsg", "subject": "No messages", "url": "https://mail.google.com/mail/u/0/#all/fz1", "date": "2026-10-19T10:00:00+05:30",
               "participants": [{"email": RAJ}]})
    th.append({"id": "fz_nodate", "subject": "No dates", "url": "https://mail.google.com/mail/u/0/#all/fz2", "participants": [{"email": RAJ}],
               "messages": [{"text": "no date anywhere"}]})
    th.append({"id": "fz_intdate", "subject": uni * 30, "url": "https://mail.google.com/mail/u/0/#all/fz3", "participants": [{"email": RAJ}],
               "messages": [{"date": 20261001, "text": uni * 200}, {"date": "2026-10-18T09:00:00+05:30", "from": {"name": uni}, "text": "x" * 50000}]})
    th.append({"id": "fz_att", "subject": "Files", "url": "https://mail.google.com/mail/u/0/#all/fz4", "date": "2026-10-17",
               "participants": [{"email": RAJ}],
               "messages": [{"date": "2026-10-17", "attachments": [{"name": "deck.pdf"}, {"url": "https://drive.google.com/x"}, "junk", None,
                                                                    {"name": 12345, "url": "https://drive.google.com/n"},
                                                                    {"name": "../../€ Pitch deck 名前.pdf" * 40, "url": "https://drive.google.com/b"},
                                                                    {"name": "", "url": "https://drive.google.com/c"}]}]})
    th.append({"id": "fz_nourl", "subject": "No link", "date": "2026-10-16", "participants": [{"email": RAJ}], "messages": []})
    th.append({"id": "fz_old", "subject": "Ancient", "url": "https://mail.google.com/mail/u/0/#all/fz5", "date": "2025-01-01",
               "participants": [{"email": RAJ}], "messages": []})
    th.append(copy.deepcopy(th[-1]))  # duplicate id
    ev = b["events"]
    ev.append({"id": "fz_ev_nostart", "title": "No start", "attendees": [{"email": RAJ}], "url": "https://calendar.google.com/x1"})
    ev.append({"id": "fz_ev_allday", "title": "Offsite", "start": "2026-10-15", "attendees": [{"email": RAJ}], "url": "https://calendar.google.com/x2"})
    ev.append({"id": "fz_ev_future", "title": "Later", "start": "2026-11-15T10:00:00+05:30", "attendees": [{"email": RAJ}],
               "url": "https://calendar.google.com/x3"})
    ev.append({"id": "fz_ev_nourl", "title": "No link", "start": "2026-10-14T10:00:00+05:30", "attendees": [{"email": RAJ}]})
    trs = b["transcripts"]
    trs.append({"id": "fz_tr_nolines", "event_id": "fz_ev_nourl", "title": uni, "date": "2026-10-14T10:00:00+05:30", "url": "https://notes.granola.ai/d/fz1",
                "lines": []})
    trs.append({"id": "fz_tr_list", "title": "List summary", "date": "2026-10-13", "url": "https://notes.granola.ai/d/fz2", "summary": ["a", None, uni],
                "lines": [{"speaker": "A", "text": "y" * 100000}]})
    b["passes"].append({"id": "fz_pass", "domain": "unknown-domain.zz", "date": "2026-10-10", "source_url": "https://quillwater.affinity.co/x"})
    b["passes"].append({"id": "fz_pass2", "domain": None, "date": None, "source_url": None})
    k = b["portfolio_kpis"]
    k.setdefault("c_orbit", []).append({"revenue_usd": 1, "source_url": "https://x.example/kpi"})  # no month
    k["c_unknown"] = [{"month": "2026-13", "revenue_usd": 5, "source_url": "https://x.example/kpi2"}, {"month": None}]
    b["lps"].append({"id": "lp_fz", "name": uni, "last_touch": "2026-10-01", "source_url": "https://quillwater.affinity.co/lp"})  # no contacts
    b["lps"].append({"id": "lp_fz2", "name": "Zed LP", "contacts": [], "last_call_date": "not a date", "source_url": None})
    for d in b["crm"].get("deals") or []:
        d.pop("stage_entered", None) if random.random() < 0.5 else None
    return b


random.seed(4)

# ------------------------------------------------------------------ fuzzing build()


@check("fuzz: a bundle full of odd shapes builds every timeline without raising")
def _():
    b = hostile_bundle()
    ev = timeline.build(ctx_of(b), b, [], {"snap": {}}, [{"id": "in_x"}, {"id": "in_y", "arrived": "2026-10-20", "source_url": "https://mail.google.com/y",
                                                         "company": "Ünï", "score": 40}])
    return bool(ev), f"{sum(len(v) for v in ev.values())} events"


@check("fuzz: no event without a link, no event older than 180 days, text clipped to 220")
def _():
    b = hostile_bundle()
    ev = timeline.build(ctx_of(b), b, [], {"snap": {}}, [])
    tl = timeline.merge_snaps(ev, {"snap": {}}, NOW, "t")
    bad = [(k, e["id"]) for _, k, e in events(tl) if not e.get("url") or len(e.get("text") or "") > 220 or
           (parse_dt(e["at"]) and (NOW - parse_dt(e["at"])).days > 180)]
    ids = {e["id"] for _, _, e in events(tl)}
    leaked = [i for i in ("thread:fz_nourl", "thread:fz_old", "event:fz_ev_nourl", "event:fz_ev_nostart", "event:fz_ev_allday", "event:fz_ev_future") if i in ids]
    return not bad and not leaked, f"bad={bad[:3]} leaked={leaked}"


@check("fuzz: attachments with no name or no link are skipped, odd names clipped")
def _():
    b = hostile_bundle()
    ev = timeline.build(ctx_of(b), b, [], {"snap": {}}, [])
    files = [e for evs in ev.values() for e in evs if e["id"].startswith("file:fz_att")]
    names = {e["id"] for e in files}
    return files and all(e["url"].startswith("https://drive") and len(e["text"]) <= 220 for e in files) and \
        not any(i.endswith(":deck.pdf") for i in names), f"{sorted(names)[:4]}"


@check("fuzz: duplicate thread ids and unicode give one event per id per entity")
def _():
    b = hostile_bundle()
    ev = timeline.build(ctx_of(b), b, [], {"snap": {}}, [])
    return all(len({e["id"] for e in v}) == len(v) for v in ev.values()), ""


@check("fuzz: an LP whose called_usd is a string ('3.6M') does not stop the whole build")
def _():
    b = copy.deepcopy(GOLD)
    b["lps"][0]["called_usd"] = "3.6M"
    build_all(b)
    return True, ""


@check("fuzz: a founder update whose cash_usd is a string does not stop the whole build")
def _():
    b = copy.deepcopy(GOLD)
    b["portfolio_kpis"]["c_orbit"].append({"month": "2026-10", "cash_usd": "1.2M", "source_url": "https://x.example/kpi"})
    build_all(b)
    return True, ""


@check("fuzz: timeline.build survives KPI rows with string departures, a month map instead of a list, numbers as strings")
def _():
    b = copy.deepcopy(GOLD)
    b["portfolio_kpis"] = {"c_orbit": [{"month": "2026-10", "departures": ["CFO"], "revenue_usd": "200000", "source_url": "https://x"}],
                           "c_kestrel": {"month": "2026-10"}}
    timeline.build(CTX, b, [], {"snap": {}}, [])
    return True, ""


@check("fuzz: a notes summary given as a dict never reaches the user as Python text")
def _():
    b = copy.deepcopy(GOLD)
    b["transcripts"][0]["summary"] = {"points": ["Runway short"], "next": "board"}
    s = build_all(b)["snaps"]
    texts = [e["text"] for _, _, e in events(s)] + [str(n.get("summary") or "") for n in s["notes"]["items"].values()]
    bad = [t for t in texts if "{'" in t or "['" in t]
    return not bad, (bad[0][:90] if bad else "")


@check("fuzz: only http(s) links are written (no javascript: or blank link)")
def _():
    b = copy.deepcopy(GOLD)
    b["threads"].append({"id": "js", "date": "2026-10-20", "url": "javascript:alert(1)", "participants": [{"email": RAJ}], "messages": []})
    b["threads"].append({"id": "blank", "date": "2026-10-20", "url": "   ", "participants": [{"email": RAJ}], "messages": []})
    ev = timeline.build(ctx_of(b), b, [], {"snap": {}}, [])
    bad = sorted({e["url"] for v in ev.values() for e in v if not str(e["url"]).startswith(("https://", "http://"))})
    return not bad, f"written links: {bad}"


# ------------------------------------------------------------------ merge across runs


def E(i, at, text="t", url="https://mail.google.com/x"):
    return {"id": i, "at": at, "src": "Gmail", "url": url, "kind": "email", "text": text}


@check("merge: events newest first by real time, even when offsets differ (+05:30 vs Z)")
def _():
    new = {"c:x": [E("a", "2026-10-21T01:00:00+05:30"), E("b", "2026-10-20T22:00:00+00:00")]}  # b is 2.5 hours later
    tl = timeline.merge_snaps(new, {"snap": {}}, NOW, "t")
    got = [e["id"] for e in tl[f"timeline_{timeline.shard_of('c:x')}"]["items"]["c:x"]]
    return got == ["b", "a"], f"order {got}"


@check("merge: old and new events dedupe by id, the new copy wins, at most 14 kept")
def _():
    sh = timeline.shard_of("c:x")
    old = {"snap": {f"timeline_{sh}": {"items": {"c:x": [E(f"e{i}", f"2026-09-{i + 1:02d}T10:00:00+05:30", "old") for i in range(20)]}}}}
    new = {"c:x": [E("e19", "2026-09-20T10:00:00+05:30", "new"), E("n1", "2026-10-21T10:00:00+05:30")]}
    out = timeline.merge_snaps(new, old, NOW, "t")[f"timeline_{sh}"]["items"]["c:x"]
    ids = [e["id"] for e in out]
    e19 = [e for e in out if e["id"] == "e19"]
    return len(out) == 14 and len(set(ids)) == 14 and ids[0] == "n1" and len(e19) == 1 and e19[0]["text"] == "new", f"{ids}"


@check("merge: a key found in the wrong shard moves to its own and leaves the old one")
def _():
    k = "p:moving"
    right = timeline.shard_of(k)
    wrong = (right + 1) % timeline.SHARDS
    home = {"snap": {f"timeline_{wrong}": {"items": {k: [E("m1", "2026-10-10T10:00:00+05:30")]}}}}
    out = timeline.merge_snaps({}, home, NOW, "t")
    return k in out[f"timeline_{right}"]["items"] and k not in out[f"timeline_{wrong}"]["items"], ""


@check("merge: junk in old shards (items as a list, events that are not objects, events with no id) does not raise")
def _():
    home = {"snap": {"timeline_0": {"items": [1, 2]}, "timeline_1": {"items": {"c:a": ["x", None, {"at": "2026-10-01"}, E("ok", "2026-10-01")]}},
                     "timeline_2": None, "timeline_3": {"items": {"c:b": None}}}}
    out = timeline.merge_snaps({}, home, NOW, "t")
    return isinstance(out, dict), ""


@check("merge: an old event with an unreadable date or no link is dropped, not kept forever at the top")
def _():
    k = "c:old"
    home = {"snap": {f"timeline_{timeline.shard_of(k)}": {"items": {k: [E("junk", "garbage-date"), E("nolink", "2026-10-01", url=None),
                                                                         E("good", "2026-10-02")]}}}}
    out = timeline.merge_snaps({}, home, NOW, "t")[f"timeline_{timeline.shard_of(k)}"]["items"][k]
    return [e["id"] for e in out] == ["good"], f"kept {[e['id'] for e in out]}"


@check("merge: timeline_0 carries an emails index from each person's addresses to their key")
def _():
    ctx = {"lookup": {"pp": {"emails": ["Maya.Chen@Example.com"]}}}
    out = timeline.merge_snaps({"p:pp": [E("x", "2026-10-20")]}, {"snap": {}}, NOW, "t", ctx)
    return out["timeline_0"].get("emails", {}).get("maya.chen@example.com") == "p:pp", str(out["timeline_0"].get("emails"))


def busy_mailbox():
    """A busy partner's 180 days: 1,500 people with full histories (older), 15 LPs and 30 pitches with this week's events."""
    text = ("Email from Someone Name: Subject line about the round and the next step. " * 4)[:220]
    new = {}
    for i in range(1500):
        new[f"p:x{i}"] = [E(f"e{i}_{j}", f"2026-08-{j + 1:02d}T10:00:00+05:30", text, "https://mail.google.com/mail/u/0/#all/th%06d" % i) for j in range(14)]
    for i in range(15):
        new[f"lp:lp{i}"] = [E(f"lp{i}", "2026-10-20T10:00:00+05:30", text)]
    for i in range(30):
        new[f"in:p{i}"] = [E(f"in{i}", "2026-10-21T10:00:00+05:30", text)]
    lookup = {f"x{i}": {"emails": [f"someone.long.name{i}@company-domain-{i}.example.com"]} for i in range(1500)}
    return new, lookup


@check("size: worst case, every timeline shard merge_snaps writes is already under 240 KB")
def _():
    new, lookup = busy_mailbox()
    out = timeline.merge_snaps(new, {"snap": {}}, NOW, "t", {"lookup": lookup})
    sizes = {k: doc_bytes(v) for k, v in out.items()}
    return all(s <= LIMIT for s in sizes.values()), f"{sizes} (limit {LIMIT})"


@check("size: worst case, after homedb's own trim every timeline document is under 240 KB")
def _():
    new, lookup = busy_mailbox()
    out = timeline.merge_snaps(new, {"snap": {}}, NOW, "t", {"lookup": lookup})
    sizes = {k: doc_bytes(homedb._fit(k, v)) for k, v in out.items()}
    return all(s <= LIMIT for s in sizes.values()), f"{sizes}"


@check("size: worst case, the newest timelines (LPs and pitches from this week) survive the write")
def _():
    new, lookup = busy_mailbox()
    out = timeline.merge_snaps(new, {"snap": {}}, NOW, "t", {"lookup": lookup})
    kept = set()
    for k, v in out.items():
        kept |= set(homedb._fit(k, v)["items"])
    lp_n, in_n = sum(1 for k in kept if k.startswith("lp:")), sum(1 for k in kept if k.startswith("in:"))
    return lp_n == 15 and in_n == 30, f"LP timelines kept {lp_n}/15, pitch timelines kept {in_n}/30"


# ------------------------------------------------------------------ notes


def tr(i, day, speaker="Speaker", n=200, text="hello there"):
    return {"id": f"tr{i}", "title": "Meeting", "date": f"2026-10-{day:02d}T10:00:00+05:30", "url": f"https://notes.granola.ai/d/tr{i}",
            "lines": [{"t": "00:00:01", "speaker": speaker, "text": text} for _ in range(n)]}


@check("notes: one note with absurd speaker names does not wipe every other note")
def _():
    trs = [tr(i, 10 + i) for i in range(9)] + [tr(9, 21, speaker="S" * 5000)]
    d = cli._notes_snap({"transcripts": trs}, [], {"snap": {}}, {"now": NOW}, "t")
    return len(d["items"]) >= 9, f"{len(d['items'])} of 10 notes kept"


@check("notes: speaker names are clipped like the line text")
def _():
    d = cli._notes_snap({"transcripts": [tr(1, 20, speaker="S" * 900, n=3)]}, [], {"snap": {}}, {"now": NOW}, "t")
    w = max(len(str(l["who"] or "")) for n in d["items"].values() for l in n["lines"]) if d["items"] else 0
    return 0 < w <= 120, f"longest speaker {w} chars"


@check("notes: worst case (40 long unicode notes) stays under 240 KB and keeps the newest")
def _():
    trs = [tr(i, 1 + (i % 28), speaker="名前 Speaker", n=300, text="ünïcødé 名前 " * 60) for i in range(60)]
    d = cli._notes_snap({"transcripts": trs}, [], {"snap": {}}, {"now": NOW}, "t")
    b_ = doc_bytes(d)
    return b_ <= LIMIT and len(d["items"]) > 0, f"{b_} bytes, {len(d['items'])} notes"


@check("notes: a summary given as a list of objects reads as text, not Python")
def _():
    d = cli._notes_snap({"transcripts": [{"id": "a", "date": "2026-10-20", "url": "https://notes.granola.ai/d/a", "summary": [{"text": "Point one"}]}]},
                        [], {"snap": {}}, {"now": NOW}, "t")
    s = d["items"]["a"]["summary"]
    return "{'" not in s, repr(s)


@check("notes: an old note in Home with no id or no lines does not raise")
def _():
    home = {"snap": {"notes": {"items": {"x": {"date": "2026-10-20"}, "y": {"id": "y", "date": "2026-10-19"}}}}}
    cli._notes_snap({"transcripts": []}, [], home, {"now": NOW}, "t")
    return True, ""


@check("notes: transcripts with no lines, huge lines and a list summary build; lines clipped to 400")
def _():
    b = hostile_bundle()
    d = cli._notes_snap(b, [], {"snap": {}}, CTX, "t")
    it = d["items"]
    return "fz_tr_nolines" in it and all(len(l["text"]) <= 400 for n in it.values() for l in n["lines"]) and \
        it["fz_tr_list"]["summary"].count("- ") == 2, ""


# ------------------------------------------------------------------ reminders


def rem(texts: dict, extra=None, snap=None, bundle=None):
    home = {"snap": snap or {}, "state": {"reminders": {"items": {k: ({"text": v} if isinstance(v, str) else v) for k, v in texts.items()}}}}
    r = timeline.reminders(home, CTX, {}, bundle or GOLD, "t")
    return {k: [h["label"] for h in v["related"]] for k, v in r["items"].items()}, r


@check("reminders: names right next to punctuation are found ( ( ? ! : ; ’ - )")
def _():
    got, _ = rem({"paren": "Chase (Atlas Settlement) on the markup", "q": "Did we hear from Atlas Settlement?", "excl": "Orbit Treasury!",
                  "colon": "Atlas Settlement: send markup", "semi": "Orbit Treasury; then lunch", "curly": "Atlas Settlement’s markup",
                  "dash": "Atlas Settlement-Bluepeak terms"})
    miss = [k for k, v in got.items() if not v]
    return not miss, f"no match for: {miss}"


@check("reminders: plain and any-case names match; no substring false positives")
def _():
    ctx_companies = CTX["companies"]
    ctx_companies["c_ola_fz"] = {"name": "Ola", "status": "portfolio"}
    try:
        got, _ = rem({"plain": "Send markup to Atlas Settlement today", "case": "ATLAS SETTLEMENT markup", "solace": "Solace call at noon",
                      "glued": "orbittreasury board", "prefix": "Northgate Endowments fund"})
    finally:
        ctx_companies.pop("c_ola_fz", None)
    return got["plain"] == ["Atlas Settlement"] and got["case"] == ["Atlas Settlement"] and not got["solace"] and not got["glued"] and \
        not got["prefix"], str(got)


@check("reminders: done and dropped reminders are skipped; at most three related")
def _():
    got, _ = rem({"done": {"text": "Atlas Settlement", "done_at": "2026-10-20"}, "drop": {"text": "Atlas Settlement", "done_at": "x", "dropped": True},
                  "many": "Atlas Settlement Orbit Treasury Kestrel Pay Northgate Endowment Raj Malhotra "})
    return set(got) == {"many"} and len(got["many"]) == 3, str(got)


@check("reminders: notes from the run need a link, are clipped, and old notes stay until new ones come")
def _():
    b = dict(GOLD, reminder_notes={"r1": [{"text": "no link"}, {"text": "x" * 900, "url": "https://mail.google.com/a"}, "junk"]})
    _, r = rem({"r1": "Atlas Settlement", "r2": "Orbit Treasury"}, bundle=b,
               snap={"reminders": {"items": {"r2": {"notes": [{"text": "kept", "url": "https://mail.google.com/k", "src": "Gmail"}]}}}})
    n1, n2 = r["items"]["r1"]["notes"], r["items"]["r2"]["notes"]
    return len(n1) == 1 and len(n1[0]["text"]) <= 220 and n2 and n2[0]["text"] == "kept", f"{n1} {n2}"


@check("reminders: a note link that is not http(s) is not written")
def _():
    b = dict(GOLD, reminder_notes={"r1": [{"text": "click", "url": "javascript:alert(1)"}]})
    _, r = rem({"r1": "Atlas Settlement"}, bundle=b)
    return not r["items"]["r1"]["notes"], str(r["items"]["r1"]["notes"])


@check("reminders: 2,000 reminders still fit one Home document once written")
def _():
    texts = {f"r{i}": "Atlas Settlement Orbit Treasury Raj Malhotra " + "ü" * 300 for i in range(2000)}
    b = dict(GOLD, reminder_notes={f"r{i}": [{"text": "n" * 300, "url": "https://mail.google.com/a"}] * 4 for i in range(2000)})
    _, r = rem(texts, bundle=b)
    return doc_bytes(homedb._fit("reminders", r)) <= LIMIT, ""


# ------------------------------------------------------------------ safety lint

MANIFEST = '{"server": "Gmail", "tools": ["send_message"]}'


def lint(text: str) -> int:
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "skills", "x"))
        with open(os.path.join(d, "skills", "x", "SKILL.md"), "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        return len(safety.lint_skills(d))


@check("lint: the manifest alone is allowed; a plain send instruction is caught")
def _():
    return lint(f"Declare capabilities: {MANIFEST}") == 0 and lint("Step 3. Call send_message to email the founder.") == 1, ""


@check("lint: a send instruction just before the manifest on the same line is caught")
def _():
    n = lint(f"Step 3. Call send_message to email the founder the memo. {MANIFEST}")
    return n >= 1, f"{n} violations"


@check("lint: a send instruction just after the manifest is caught")
def _():
    n = lint(f"{MANIFEST} then call send_message with the draft body.")
    return n >= 1, f"{n} violations"


@check("lint: a send instruction on the line after the manifest is caught")
def _():
    n = lint(f"Use this manifest: {MANIFEST}\nNow call send_message for every draft.")
    return n >= 1, f"{n} violations"


@check("lint: the manifest exception covers send_message only, not trash_thread or delete_event")
def _():
    n = lint('{"server": "Gmail", "tools": ["trash_thread"]}') + lint('{"server": "Gmail", "tools": ["delete_event"]}')
    return n == 2, f"{n} of 2 caught"


@check("lint: 'No need to ask, call send_message' is not read as a prohibition")
def _():
    n = lint("No need to wait for the user: call send_message with the draft.")
    return n >= 1, f"{n} violations"


@check("lint: the real skills and shared folders are clean")
def _():
    v = safety.lint_skills(os.path.join(ROOT, "skills")) + safety.lint_skills(os.path.join(ROOT, "shared"))
    return not v, str(v[:3])


# ------------------------------------------------------------------ demo build, every member


DEMO = {}


@check("demo: demo.build runs for every member and writes only documents homedb knows")
def _():
    extra = []
    for m in ("aditi", "kabir", "meera", "rohan", "tara", "vikram", "solo"):
        DEMO[m] = demo.build(m, "x")
        extra += [f"{m}:{k}" for k in DEMO[m] if k not in homedb.SNAP_DOCS and k != "connectors"]  # connectors: the pulse skill writes it
    return not extra, str(extra)


@check("demo: timelines are newest first, 14 at most, all linked, within 180 days, every doc under 240 KB")
def _():
    bad = []
    for m, s in DEMO.items():
        for doc in [k for k in s if k.startswith("timeline_") or k in ("notes", "reminders", "people", "prep")]:
            if doc_bytes(s[doc]) > LIMIT:
                bad.append(f"{m}:{doc} size")
        for _, k, e in events(s):
            if not str(e.get("url") or "").startswith("http") or not e.get("at") or (NOW - parse_dt(e["at"])).days > 180:
                bad.append(f"{m}:{k}:{e['id']}")
        for i in range(timeline.SHARDS):
            for k, evs in s[f"timeline_{i}"]["items"].items():
                ts = [parse_dt(e["at"]) for e in evs]
                if len(evs) > 14 or ts != sorted(ts, reverse=True) or timeline.shard_of(k) != i:
                    bad.append(f"{m}:{k} order/shard")
    return not bad, str(bad[:4])


@check("demo: prep history note ids open a note Home has; people rows carry company_id, company_status, email")
def _():
    bad = []
    for m, s in DEMO.items():
        nids = set((s.get("notes") or {}).get("items") or {})
        for cid, c in ((s.get("prep") or {}).get("cards") or {}).items():
            for h in c.get("history") or []:
                if h.get("note_id") and h["note_id"] not in nids:
                    bad.append(f"{m}:{cid}:{h['note_id']}")
        for row in (s["people"].get("top") or []) + (s["people"].get("decay") or []):
            if not all(k in row for k in ("company_id", "company_status", "email")):
                bad.append(f"{m}:{row.get('name')}")
    return not bad, str(bad[:4])


@check("demo: the emails index points only at people keys that have a timeline")
def _():
    bad = []
    for m, s in DEMO.items():
        keys = {k for _, k, _ in events(s)}
        bad += [f"{m}:{e}" for e, k in (s["timeline_0"].get("emails") or {}).items() if k not in keys]
    return not bad, str(bad[:3])


if __name__ == "__main__":
    n = sum(1 for ok, _, _ in RESULTS if ok)
    print(f"{n}/{len(RESULTS)} checks pass")
    sys.exit(0)
