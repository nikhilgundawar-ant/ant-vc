"""Build the shareable demo of ant. Home: the real page with the fictional fund's data inside it, one view per person.

    python3 evals/build_demo_page.py --out <folder>

Writes <folder>/index.html. The page runs in static demo mode (no database): taps stay in memory and "View as" switches
between the six Quillwater members and a solo GP. Publish it as an artifact with no capabilities.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "evals"))
import demo  # noqa: E402

DEMO_NOW = "2026-10-22T07:05:00+05:30"  # the moment in the fictional fund's week the demo shows
PEOPLE = [("aditi", "Aditi Rao, Partner"), ("kabir", "Kabir Shah, Principal"), ("meera", "Meera Iyer, Associate"),
          ("rohan", "Rohan Das, Analyst"), ("tara", "Tara Menon, Head of Platform"), ("vikram", "Vikram Nair, CFO and IR"),
          ("solo", "A solo GP (Aditi's week, run alone)")]


# A few taps from the evening before, so Activity has something to show. Their ids match no line, so Today is unchanged.
SAMPLE_STATE = {
    "items": {
        "demo_sent_1": {"done_at": "2026-10-21T18:10:00+05:30", "sent": True, "t": "Thanks for the call, and the cap table ask", "g": "demo_sent_1",
                        "at": "2026-10-21T18:10:00+05:30"},
        "demo_done_1": {"done_at": "2026-10-21T17:40:00+05:30", "closed_by": "done", "t": "Share the Q3 KPI pack with the partners", "g": "demo_done_1",
                        "at": "2026-10-21T17:40:00+05:30"},
        "demo_snz_1": {"snoozed_until": "2026-10-22T08:00:00+05:30", "t": "Ledgerline: reference call notes", "g": "demo_snz_1", "at": "2026-10-21T16:05:00+05:30"},
    },
    "reminders": {
        "rdemo1": {"text": "Chase Atlas Settlement for legal counsel's contact", "due": "2026-10-22T11:00:00+05:30", "at": "2026-10-21T19:00:00+05:30"},
        "rdemo2": {"text": "Call Vikram Rao about the Orbit Treasury runway plan before the board", "due": "2026-10-22T08:30:00+05:30", "at": "2026-10-21T19:05:00+05:30"},
        "rdemo3": {"text": "Send the Q3 LP letter outline to Tara", "due": "2026-10-26T09:00:00+05:30", "at": "2026-10-21T19:10:00+05:30"},
    },
    "actions": {
        "demo_ns_1": {"type": "next_step", "status": "approved", "at": "2026-10-22T06:50:00+05:30", "t": "Halo Reconcile: next step Diligence plan with the CFO",
                      "payload": {"deal_id": "demo_halo", "company": "Halo Reconcile", "text": "Diligence plan with the CFO", "current": "Partner meeting"}},
    },
}


def build(out_dir: str) -> str:
    page = open(os.path.join(ROOT, "home", "index.html"), encoding="utf-8").read()
    members = {}
    for key, label in PEOPLE:
        snaps = json.loads(json.dumps(demo.build(key, "https://claude.ai/artifact/demo"), default=str))
        snaps["config"]["demo"] = True
        demo.sample_research(snaps)
        members[key] = {"label": label, "snaps": snaps, "state": SAMPLE_STATE}
    data = json.dumps({"order": [k for k, _ in PEOPLE], "members": members}, ensure_ascii=False, separators=(",", ":"))
    data = data.replace("</", "<\\/")  # never closes the script tag early
    page = page.replace("<title>ant. Home</title>", "<title>ant. Home Demo</title>", 1)
    marker = "<script>\n(function () {"
    assert marker in page, "page script not found"
    # The page's clock reads Thursday 22 Oct, 07:05 in Mumbai, so the next meeting, the last check and every "today"
    # match the data. Only this demo build sets the clock; the product page never does.
    clock = ("<script>(function () { var shift = Date.parse(" + json.dumps(DEMO_NOW) + ") - Date.now(), Real = Date;"
             " function D() { if (!(this instanceof D)) return new Real(Real.now() + shift).toString();"
             " if (!arguments.length) return new Real(Real.now() + shift);"
             " return new (Function.prototype.bind.apply(Real, [null].concat(Array.prototype.slice.call(arguments))))(); }"
             " D.now = function () { return Real.now() + shift; }; D.parse = Real.parse; D.UTC = Real.UTC; D.prototype = Real.prototype;"
             " window.Date = D; })();</script>\n")
    page = page.replace(marker, clock + f'<script type="application/json" id="instinct-demo">{data}</script>\n' + marker, 1)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "index.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(page)
    return path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    path = build(a.out)
    print(path, f"{os.path.getsize(path) / 1024:.0f} KiB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
