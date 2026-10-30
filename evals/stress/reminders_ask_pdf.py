"""Stress checks for ant. Home: reminders and time parsing, Ask, PDF export and Settings.

    python3 evals/stress/reminders_ask_pdf.py

Each check passes when the page behaves as it should, so a FAIL line is a live bug. Prints one PASS/FAIL line per
check and a summary "N/M checks pass". Exit code 0 always (the summary carries the verdict); pass --strict to exit 1
on any failure.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import sys
from zoneinfo import ZoneInfo

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import home_qa as Q  # noqa: E402
import demo  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

OUT = os.environ.get("STRESS_OUT") or "/tmp/claude-0/-home-claude/f41ebfd9-0635-5201-96ea-278169523f82/scratchpad/stress-reminders"
IST = ZoneInfo("Asia/Kolkata")
NY = ZoneInfo("America/New_York")
LON = ZoneInfo("Europe/London")
RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  [" + str(detail)[:300] + "]"), flush=True)


def deep(x):
    return json.loads(json.dumps(x, default=str))


# The mock db has no doc().delete() and downloads always resolve: a thin wrapper adds both, so Remove and save
# failures can be watched. It changes nothing else the harness records.
WRAP = r"""
(function () {
  var C = window.__QA__ || {}, u = window.claude && window.claude.use; window.__deletes = [];
  if (!u) return;
  window.claude.use = function (n) {
    return u(n).then(function (x) {
      if (n === "db" && x) { var d0 = x.doc; return Object.assign({}, x, { doc: function (p) { var r = d0(p); if (!r.delete) r.delete = function () { window.__deletes.push(p); return Promise.resolve(); }; return r; } }); }
      if (n === "sample" && C.stream) {
        var f = function (input, opts) { window.__sampleOpts.push({ model: null, effort: null, modelTier: (opts && opts.modelTier) || null });
          return new Promise(function (res) { window.__push = function (t, end) { if (opts && opts.onText) opts.onText({ text: t, delta: "" }); if (end) res({ text: t, truncated: false }); }; }); };
        f.json = function () { return Promise.resolve({}); };
        return f;
      }
      if (n === "downloads") {
        if (C.dlNull) return null;
        if (C.dlFail) return { save: function (req) { window.__downloads.push({ filename: req.filename, failed: C.dlFail }); return Promise.reject({ code: C.dlFail, message: "mock" }); } };
      }
      return x;
    });
  };
})();
"""


class QA2(Q.QA):
    """The harness's open, with a browser time zone and an extra init script (the wrapper above)."""

    def open2(self, browser, viewport=Q.DESK, when=Q.T0, member="aditi", tz="Asia/Kolkata", page_file=None, **cfg):
        ctx = browser.new_context(viewport=viewport, timezone_id=tz, color_scheme="light")
        page = ctx.new_page()
        page.route("**/fonts.googleapis.com/**", lambda r: r.abort())
        page.route("**/fonts.gstatic.com/**", lambda r: r.abort())
        page.route("**/cdnjs.cloudflare.com/**", lambda r: r.abort())
        qa = {"snap": cfg.pop("snap") if "snap" in cfg else self.snaps[member], "open_all": cfg.pop("open_all", False), "inline": cfg.pop("inline", False), **cfg}
        page.add_init_script("window.__QA__ = " + json.dumps(qa, default=str) + ";" + Q.MOCK + WRAP)
        errors: list[str] = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.clock.set_fixed_time(when)
        page.goto("file://" + (page_file or self.wrapper))
        page.wait_for_timeout(250)
        page._qa_errors = errors  # type: ignore[attr-defined]
        return ctx, page


def errs(page) -> list[str]:
    return [e for e in page._qa_errors if "fonts.g" not in e and "ERR_FAILED" not in e and "cdnjs" not in e and "net::" not in e]


def snap_tz(qa, tz: str) -> dict:
    s = deep(qa.snaps["aditi"])
    s["config"]["tz"] = tz
    return s


def to_reminders(page) -> None:
    page.locator('#rail-tabs [title="Your reminders"]').click()
    page.wait_for_timeout(60)


def add_via_form(page, text: str, scope: str = "#view") -> str | None:
    """Types a reminder into the form and returns the due time the page wrote for it (ISO, or None)."""
    n = len(page.evaluate("window.__writes"))
    box = page.locator(scope + " input[name=remind]").first
    box.fill(text)
    box.press("Enter")
    page.wait_for_timeout(80)
    ws = page.evaluate("window.__writes")[n:]
    for w in reversed(ws):
        if w.get("path") == "state/reminders":
            items = (w.get("data") or {}).get("items") or {}
            for v in items.values():
                if v.get("text") == text.strip()[:280]:
                    return v.get("due") or None
    return "NO-WRITE"


def same_instant(iso: str | None, want: dt.datetime | None) -> bool:
    if want is None:
        return iso is None
    if not iso or iso == "NO-WRITE":
        return False
    got = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return abs((got - want).total_seconds()) < 61


def show(iso, zone) -> str:
    if not iso or iso == "NO-WRITE":
        return str(iso)
    return dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(zone).strftime("%a %d %b %H:%M %Z")


# ---------------------------------------------------------------------------------------------------- reminders
def t_parse_phrases(qa, b) -> None:
    """Thu 22 Oct 2026 07:05 in Mumbai."""
    ctx, page = qa.open2(b, state={"reminders": {}})
    to_reminders(page)
    d = lambda day, hh, mm=0: dt.datetime(2026, 10, day, hh, mm, tzinfo=IST)
    cases = [
        ("Call Ana tomorrow", d(23, 9)),
        ("Read the Atlas deck tonight", d(22, 20)),
        ("Send memo monday", d(26, 9)),
        ("Plan offsite next week", d(26, 9)),
        ("Ping Varun at 5pm", d(22, 17)),
        ("Board prep at 17:30", d(22, 17, 30)),
        ("Wire check at 9:45am", d(22, 9, 45)),
        ("Pay invoice at 12am", d(23, 0)),
        ("Lunch with Tara at 12pm", d(22, 12)),
        ("Lunch with Rohan at 12", d(22, 12)),
        ("Check the data room in 2 hours", d(22, 9, 5)),
        ("Partner vote friday at 9", d(23, 9)),
        ("Email Ravi the term sheet", None),
        ("Price the note at 30% off", None),
        ("Send LP letter monday, not friday", d(26, 9)),
    ]
    for text, want in cases:
        got = add_via_form(page, text)
        check(f"reminder parse IST: {text!r} -> {want.strftime('%a %d %H:%M') if want else 'no time'}", same_instant(got, want), "got " + show(got, IST))
    # The hint under the form says the same as what is saved.
    box = page.locator("#view input[name=remind]")
    box.fill("Chase Atlas tomorrow at 5pm")
    hint = page.locator("#view .rem-when").inner_text()
    check("reminder form hint reads the parsed time", "Fri 23 Oct 17:00" in hint, hint)
    check("no script errors while adding reminders (IST)", not errs(page), "; ".join(errs(page)[:3]))
    ctx.close()


def t_clocks(qa, b) -> None:
    # Late night, 23:30 Thursday in Mumbai.
    late = dt.datetime(2026, 10, 22, 23, 30, tzinfo=IST)
    ctx, page = qa.open2(b, when=late, state={"reminders": {}})
    to_reminders(page)
    got = add_via_form(page, "Read the Halo memo tonight")
    ok = got not in (None, "NO-WRITE") and dt.datetime.fromisoformat(got.replace("Z", "+00:00")) > late
    check("23:30: 'tonight' gives a time still ahead, not one already past", ok, "got " + show(got, IST))
    got = add_via_form(page, "Call Ana tomorrow")
    check("23:30: 'tomorrow' is Fri 23 Oct 09:00", same_instant(got, dt.datetime(2026, 10, 23, 9, tzinfo=IST)), show(got, IST))
    # The "Later today" chip at 23:30.
    page.locator("#view .rem-form button", has_text="Later today").click()
    hint = page.locator("#view .rem-when").inner_text()
    n = len(page.evaluate("window.__writes"))
    page.locator("#view input[name=remind]").fill("Chip test late")
    page.locator("#view .rem-form button[type=submit]").click()
    page.wait_for_timeout(80)
    w = [x for x in page.evaluate("window.__writes")[n:] if x.get("path") == "state/reminders"]
    due = None
    if w:
        for v in (w[-1]["data"]["items"] or {}).values():
            if v.get("text") == "Chip test late":
                due = v.get("due")
    ok = bool(due) and dt.datetime.fromisoformat(due.replace("Z", "+00:00")) > late
    check("23:30: 'Later today' chip does not set a time already past", ok, f"hint {hint!r}, due {show(due, IST)}")
    ctx.close()

    # Sunday 25 Oct 10:00.
    sun = dt.datetime(2026, 10, 25, 10, 0, tzinfo=IST)
    ctx, page = qa.open2(b, when=sun, state={"reminders": {}})
    to_reminders(page)
    for text, want in (("Plan next week", dt.datetime(2026, 10, 26, 9, tzinfo=IST)), ("Call LP sunday", dt.datetime(2026, 11, 1, 9, tzinfo=IST)),
                       ("Send recap monday", dt.datetime(2026, 10, 26, 9, tzinfo=IST))):
        got = add_via_form(page, text)
        check(f"Sunday: {text!r} -> {want.strftime('%a %d %b %H:%M')}", same_instant(got, want), show(got, IST))
    ctx.close()

    # Month end, Sat 31 Oct; year end, Thu 31 Dec.
    for when, text, want in ((dt.datetime(2026, 10, 31, 11, 0, tzinfo=IST), "Close books tomorrow", dt.datetime(2026, 11, 1, 9, tzinfo=IST)),
                             (dt.datetime(2026, 12, 31, 22, 0, tzinfo=IST), "New year plan tomorrow", dt.datetime(2027, 1, 1, 9, tzinfo=IST)),
                             (dt.datetime(2026, 12, 31, 22, 0, tzinfo=IST), "Send thanks friday", dt.datetime(2027, 1, 1, 9, tzinfo=IST))):
        ctx, page = qa.open2(b, when=when, state={"reminders": {}})
        to_reminders(page)
        got = add_via_form(page, text)
        check(f"{when.strftime('%d %b')}: {text!r} -> {want.strftime('%d %b %Y %H:%M')}", same_instant(got, want), show(got, IST))
        ctx.close()


def t_zones(qa, b) -> None:
    # New York, Sat 31 Oct 10:00 EDT; US clocks go back on Sun 1 Nov.
    now = dt.datetime(2026, 10, 31, 10, 0, tzinfo=NY)
    ctx, page = qa.open2(b, when=now, tz="America/New_York", snap=snap_tz(qa, "America/New_York"), state={"reminders": {}})
    to_reminders(page)
    for text, want in (("Call Ana at 5pm", dt.datetime(2026, 10, 31, 17, tzinfo=NY)),
                       ("Send deck tomorrow", dt.datetime(2026, 11, 1, 9, tzinfo=NY)),
                       ("LP call monday at 10", dt.datetime(2026, 11, 2, 10, tzinfo=NY))):
        got = add_via_form(page, text)
        check(f"New York: {text!r} -> {want.strftime('%a %d %b %H:%M %Z')}", same_instant(got, want), show(got, NY))
    ctx.close()
    # The page follows config.tz even when the browser sits in Mumbai.
    ctx, page = qa.open2(b, when=now, tz="Asia/Kolkata", snap=snap_tz(qa, "America/New_York"), state={"reminders": {}})
    to_reminders(page)
    got = add_via_form(page, "Ping Varun at 5pm")
    check("config.tz New York, browser in Mumbai: 'at 5pm' is 17:00 New York", same_instant(got, dt.datetime(2026, 10, 31, 17, tzinfo=NY)), show(got, NY))
    ctx.close()
    # London, Thu 22 Oct 08:00 BST; UK clocks go back on Sun 25 Oct.
    now = dt.datetime(2026, 10, 22, 8, 0, tzinfo=LON)
    ctx, page = qa.open2(b, when=now, tz="Europe/London", snap=snap_tz(qa, "Europe/London"), state={"reminders": {}})
    to_reminders(page)
    for text, want in (("Send memo tomorrow", dt.datetime(2026, 10, 23, 9, tzinfo=LON)),
                       ("Plan monday", dt.datetime(2026, 10, 26, 9, tzinfo=LON)),
                       ("Review at 6pm", dt.datetime(2026, 10, 22, 18, tzinfo=LON))):
        got = add_via_form(page, text)
        check(f"London: {text!r} -> {want.strftime('%a %d %b %H:%M %Z')}", same_instant(got, want), show(got, LON))
    page.locator("#view .rem-form button", has_text="Monday 09:00").click()
    hint = page.locator("#view .rem-when").inner_text()
    check("London: 'Monday 09:00' chip says Mon 26 Oct 09:00 after the clock change", "Mon 26 Oct 09:00" in hint, hint)
    ctx.close()


def rem_state() -> dict:
    return {"reminders": {
        "rdue": {"text": "Chase Atlas Settlement for legal counsel", "due": "2026-10-22T06:30:00+05:30", "at": "2026-10-21T19:00:00+05:30"},
        "rsoon": {"text": "Call Vikram about Orbit runway", "due": "2026-10-22T08:30:00+05:30", "at": "2026-10-21T19:05:00+05:30"},
        "rlater": {"text": "Send the Q3 LP letter outline to Tara", "due": "2026-10-26T09:00:00+05:30", "at": "2026-10-21T19:10:00+05:30"},
        "rnone": {"text": "Think about the AI infra thesis", "at": "2026-10-21T19:10:00+05:30"},
        "rold": {"text": "Old finished one", "done_at": "2026-10-21T20:00:00+05:30", "at": "2026-10-20T10:00:00+05:30"},
    }}


def rem_writes(page) -> list[dict]:
    return [w for w in page.evaluate("window.__writes") if w.get("path") == "state/reminders"]


def t_actions(qa, b) -> None:
    ctx, page = qa.open2(b, state=rem_state(), sample={"answer": "- Counsel is Priya at Lexwell, 21 Oct.\n- Ask Ishaan."})
    page.wait_for_timeout(150)
    today = page.locator("section[aria-label='Your reminders']")
    check("due reminders sit on Today", today.count() == 1 and today.locator(".rem-row").count() == 2, str(today.count()))
    badge = page.locator('#rail-tabs [title="Your reminders"]')
    check("rail Reminders item says 2 due, with a badge", badge.get_attribute("aria-label") == "Reminders, 2 due" and badge.locator(".tab-badge").inner_text() == "2",
          str(badge.get_attribute("aria-label")))
    # Brief written once for each due reminder, not again on later renders.
    page.wait_for_timeout(200)
    n1 = len([s for s in page.evaluate("window.__samples") if "My reminder" in json.dumps(s)])
    for _ in range(3):
        page.locator("#theme-btn").click(); page.wait_for_timeout(60)
    to_reminders(page); page.wait_for_timeout(100)
    page.locator('#rail-tabs button[aria-label="Today"]').click(); page.wait_for_timeout(100)
    n2 = len([s for s in page.evaluate("window.__samples") if "My reminder" in json.dumps(s)])
    check("each due reminder gets one brief, not one per render", n1 == 2 and n2 == 2, f"{n1} then {n2}")
    opts = [o for s, o in zip(page.evaluate("window.__samples"), page.evaluate("window.__sampleOpts")) if "My reminder" in json.dumps(s)]
    check("reminder brief asks the quick tier", all(o and o.get("modelTier") == "quick" for o in opts), json.dumps(opts)[:200])
    check("brief text shows under the due reminder", "Lexwell" in today.inner_text())
    tw = [w for w in page.evaluate("window.__writes") if w.get("path") == "state/tldr"]
    check("brief saved to state/tldr", bool(tw) and any(k.startswith("rm:rdue:") for k in (tw[-1]["data"]["items"] or {})), str(len(tw)))
    # Done, then Undo.
    page.locator("section[aria-label='Your reminders'] .rem-row", has_text="Chase Atlas").locator("button.row-done").click()
    page.wait_for_timeout(80)
    w = rem_writes(page)[-1]
    check("Done writes only that reminder's done_at (update, merge)", w["op"] == "update" and list(w["data"]["items"].keys()) == ["rdue"] and w["data"]["items"]["rdue"].get("done_at"), json.dumps(w)[:200])
    check("Done takes it off Today", page.locator("section[aria-label='Your reminders'] .rem-row", has_text="Chase Atlas").count() == 0)
    page.locator(".toast button", has_text="Undo").click(); page.wait_for_timeout(80)
    w = rem_writes(page)[-1]
    check("Undo clears done_at", w["data"]["items"].get("rdue", {}).get("done_at", "x") is None, json.dumps(w)[:200])
    check("Undo brings it back on Today", page.locator("section[aria-label='Your reminders'] .rem-row", has_text="Chase Atlas").count() == 1)
    # Tomorrow.
    page.locator("section[aria-label='Your reminders'] .rem-row", has_text="Call Vikram").locator("button", has_text="Tomorrow").click()
    page.wait_for_timeout(80)
    w = rem_writes(page)[-1]
    check("Tomorrow moves it to Fri 23 Oct 09:00", same_instant(w["data"]["items"].get("rsoon", {}).get("due"), dt.datetime(2026, 10, 23, 9, tzinfo=IST)), json.dumps(w)[:200])
    # Drop.
    to_reminders(page)
    page.locator("#view .rem-row", has_text="Think about").locator("button", has_text="Drop").click()
    page.wait_for_timeout(80)
    w = rem_writes(page)[-1]
    check("Drop marks it done and dropped", w["data"]["items"].get("rnone", {}).get("dropped") is True)
    check("Drop offers Undo like Done does", page.locator(".toast button", has_text="Undo").count() == 1, page.locator("#toast-slot").inner_text())
    check("a dropped reminder is not listed under Done", page.locator("section[aria-label='Done reminders']", has_text="Think about").count() == 0)
    # Reopen.
    page.locator("section[aria-label='Done reminders'] .row", has_text="Old finished").locator("button", has_text="Reopen").click()
    page.wait_for_timeout(80)
    w = rem_writes(page)[-1]
    check("Reopen clears done_at", w["data"]["items"].get("rold", {}).get("done_at", "x") is None)
    check("reopened reminder is listed open", page.locator("section[aria-label='Coming up'] .rem-row", has_text="Old finished").count() == 1)
    check("no script errors in reminder actions", not errs(page), "; ".join(errs(page)[:3]))
    ctx.close()


def t_first_write(qa, b) -> None:
    ctx, page = qa.open2(b)  # no state/reminders doc yet
    to_reminders(page)
    add_via_form(page, "First ever reminder tomorrow")
    w = rem_writes(page)
    ok = bool(w) and w[-1]["op"] == "set" and all(set(v) >= {"text", "due", "at"} for v in w[-1]["data"]["items"].values())
    check("first reminder creates state/reminders with {items: {id: {text, due, at}}}", ok, json.dumps(w)[:200])
    ctx.close()


def t_brief_fail(qa, b) -> None:
    ctx, page = qa.open2(b, state=rem_state(), sample={"fail": "rate_limited"})
    page.wait_for_timeout(200)
    n1 = len([s for s in page.evaluate("window.__samples") if "My reminder" in json.dumps(s)])
    for _ in range(3):
        to_reminders(page); page.wait_for_timeout(60)
        page.locator('#rail-tabs button[aria-label="Today"]').click(); page.wait_for_timeout(60)
    n2 = len([s for s in page.evaluate("window.__samples") if "My reminder" in json.dumps(s)])
    check("a failed reminder brief is not retried on every render", n2 == n1, f"{n1} then {n2} calls")
    sec = page.locator("section[aria-label='Your reminders']")
    check("a failed brief says it failed, not just a bare button", sec.count() == 1 and ("could not" in sec.inner_text().lower() or "busy" in sec.inner_text().lower() or "try again" in sec.inner_text().lower()),
          sec.inner_text()[:200] if sec.count() else "")
    check("no script errors when the brief fails", not errs(page), "; ".join(errs(page)[:3]))
    ctx.close()


def t_bell(qa, b) -> None:
    ctx, page = qa.open2(b, state={"reminders": {}})
    page.locator(".fab-mini[aria-label='Remind me']").click(); page.wait_for_timeout(60)
    sheet = page.locator(".sheet")
    check("bell opens the Remind me sheet with focus in the field", sheet.count() == 1 and page.evaluate("document.activeElement && document.activeElement.name") == "remind")
    got = add_via_form(page, "Chase cap table tomorrow", scope=".sheet")
    check("bell sheet adds a reminder", same_instant(got, dt.datetime(2026, 10, 23, 9, tzinfo=IST)), show(got, IST))
    check("bell sheet lists the reminder just added", page.locator(".sheet .rem-row", has_text="Chase cap table").count() == 1, page.locator(".sheet").inner_text()[:200])
    # A chip, then typing a time: the chip stays pressed after the add.
    page.locator(".sheet .rem-form button", has_text="Tomorrow 09:00").click()
    add_via_form(page, "Another one", scope=".sheet")
    pressed = page.locator(".sheet .rem-form button[aria-pressed=true]").count()
    check("after Add, no time chip still looks picked", pressed == 0, f"{pressed} pressed")
    ctx.close()


def t_static(qa, b) -> None:
    snaps = deep(qa.snaps["aditi"]); snaps["config"]["demo"] = True
    data = {"order": ["aditi"], "members": {"aditi": {"label": "Aditi", "snaps": snaps, "state": rem_state()}}}
    page_html = open(qa.wrapper, encoding="utf-8").read()
    marker = "<script>\n(function () {"
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    path = os.path.join(OUT, "_static.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(page_html.replace(marker, '<script type="application/json" id="instinct-demo">' + blob + "</script>\n" + marker, 1))
    ctx, page = qa.open2(b, page_file=path, noRuntime=True)
    page.wait_for_timeout(150)
    check("static demo: due reminders on Today", page.locator("section[aria-label='Your reminders'] .rem-row").count() == 2)
    to_reminders(page)
    add_via_form(page, "Demo reminder tomorrow")
    check("static demo: adding a reminder works in memory", page.locator("#view .rem-row", has_text="Demo reminder").count() == 1)
    page.locator("#view .rem-row", has_text="Demo reminder").locator("button.row-done").click(); page.wait_for_timeout(60)
    check("static demo: Done moves it to Done", page.locator("section[aria-label='Done reminders']", has_text="Demo reminder").count() == 1)
    check("static demo: no Brief me button without Claude", page.locator("button", has_text="Brief me").count() == 0)
    check("static demo: no script errors", not errs(page), "; ".join(errs(page)[:3]))
    ctx.close()


# ---------------------------------------------------------------------------------------------------- Ask
def open_ask(page) -> None:
    page.locator('#rail-tabs button[aria-label="Ask"]').click(); page.wait_for_timeout(80)


def t_ask_styles(qa, b) -> None:
    ctx, page = qa.open2(b, sample={"answer": "Two deals need a decision."})
    open_ask(page)
    want = {"quick": ("claude-haiku-5-5", "low", "quick"), "balanced": (None, None, None), "thorough": ("claude-opus-5-5", "high", "complex")}
    for style, (model, effort, tier) in want.items():
        page.locator("#view select[name=style]").select_option(style)
        n = len(page.evaluate("window.__sampleOpts"))
        page.locator("#view textarea").fill("Which deals need a decision? " + style)
        page.locator("#view textarea").press("Enter"); page.wait_for_timeout(120)
        o = page.evaluate("window.__sampleOpts")[n]
        check(f"Ask {style}: model {model}, effort {effort}, tier {tier}", (o["model"], o["effort"], o["modelTier"]) == (model, effort, tier), json.dumps(o))
    # Custom after Quick: the Model and Effort lists show what will be used.
    page.locator("#view select[name=style]").select_option("quick")
    page.reload(); page.wait_for_timeout(250); open_ask(page)
    check("Ask style remembered across reload", page.locator("#view select[name=style]").input_value() == "quick")
    page.locator("#view select[name=style]").select_option("custom")
    shown = (page.locator("#view select[name=model]").input_value(), page.locator("#view select[name=effort]").input_value())
    n = len(page.evaluate("window.__sampleOpts"))
    page.locator("#view textarea").fill("custom question"); page.locator("#view textarea").press("Enter"); page.wait_for_timeout(120)
    o = page.evaluate("window.__sampleOpts")[n]
    used = ({"claude-haiku-5-5": "haiku", "claude-opus-5-5": "opus", "claude-sonnet-5-5": "sonnet", None: "auto"}[o["model"]], o["effort"] or "auto")
    check("Custom: the Model and Effort shown are the ones sent", shown == used, f"shown {shown}, sent {used}")
    page.locator("#view select[name=model]").select_option("sonnet")
    page.locator("#view select[name=effort]").select_option("medium")
    n = len(page.evaluate("window.__sampleOpts"))
    page.locator("#view textarea").fill("custom 2"); page.locator("#view textarea").press("Enter"); page.wait_for_timeout(120)
    o = page.evaluate("window.__sampleOpts")[n]
    check("Custom Sonnet + Medium sends sonnet, medium, default tier", (o["model"], o["effort"], o["modelTier"]) == ("claude-sonnet-5-5", "medium", "default"), json.dumps(o))
    page.reload(); page.wait_for_timeout(250); open_ask(page)
    check("Custom model and effort remembered across reload", page.locator("#view select[name=style]").input_value() == "custom" and
          page.locator("#view select[name=model]").input_value() == "sonnet" and page.locator("#view select[name=effort]").input_value() == "medium")
    ctx.close()


def answer_page(qa, b, md: str):
    ctx, page = qa.open2(b, sample={"answer": md})
    open_ask(page)
    page.locator("#view textarea").fill("q"); page.locator("#view textarea").press("Enter"); page.wait_for_timeout(150)
    return ctx, page


def t_ask_render(qa, b) -> None:
    md = ("Three deals lead.\n\n| Company | Stage | Raise |\n|---|---|---|\n| Atlas | Diligence | $2M |\n| Halo | IC | $1.5M | extra |\n| Orbit |\n"
          "| Pipe \\| Co | Seed | $3M |\n\n1. First thing\n\n2. Second thing\n3. Third thing\n\n- a bullet")
    ctx, page = answer_page(qa, b, md)
    ans = page.locator("#view .bubble.ant .answer")
    check("answer table renders with header and 4 rows", ans.locator("table.answer-table thead th").count() == 3 and ans.locator("table.answer-table tbody tr").count() == 4,
          f"{ans.locator('table.answer-table thead th').count()} th, {ans.locator('table.answer-table tbody tr').count()} rows")
    rows = ans.locator("table.answer-table tbody tr").all_inner_texts()
    check("ragged rows pad to the header width", ans.locator("table.answer-table tbody tr").nth(2).locator("td").count() == 3)
    check("an escaped pipe stays inside its cell ('Pipe | Co')", any("Pipe | Co" in r for r in rows), " / ".join(rows)[:200])
    nums = [li for li in ans.locator("ol").evaluate_all("els => els.map(e => [e.start || 1, e.children.length])")]
    seq = []
    for start, cnt in nums:
        seq += list(range(start, start + cnt))
    check("a numbered list split by a blank line keeps counting 1, 2, 3", seq == [1, 2, 3], str(nums))
    check("no horizontal page scroll with a table", page.evaluate("document.documentElement.scrollWidth - window.innerWidth") <= 0)
    ctx.close()


def chart_md(spec: dict) -> str:
    return "Here is the picture.\n\n```chart\n" + json.dumps(spec) + "\n```\n\nDone."


def t_charts(qa, b) -> None:
    cases = [
        ("bar with negatives", {"type": "bar", "title": "Growth", "unit": "%", "labels": ["A", "B", "C"], "values": [12, -8, 0]}, 3),
        ("line with negatives", {"type": "line", "title": "Burn", "unit": "$", "labels": ["Jul", "Aug", "Sep"], "values": [-200000, -150000, -90000]}, 3),
        ("all zero values", {"type": "bar", "title": "Zero", "labels": ["A", "B"], "values": [0, 0]}, 2),
        ("one label", {"type": "line", "title": "One", "labels": ["Q3"], "values": [5]}, 1),
    ]
    for name, spec, n in cases:
        ctx, page = answer_page(qa, b, chart_md(spec))
        fig = page.locator("#view .bubble.ant figure.chart-fig svg")
        marks = fig.locator("rect.ch-bar, circle.ch-dot").count()
        ok = fig.count() == 1 and marks == n and page.locator("#view .bubble.ant", has_text="Done.").count() == 1
        bad = page.evaluate("Array.from(document.querySelectorAll('#view svg.chart *')).some(e => ['x','y','cx','cy','width','height','points'].some(a => /NaN|Infinity/.test(e.getAttribute(a) || '')))")
        check(f"chart {name}: draws {n} marks, text after it shows", ok and not bad, f"fig {fig.count()} marks {marks} nan {bad}")
        ctx.close()
    # 13 labels: the answer should not silently drop one.
    spec = {"type": "bar", "title": "Thirteen", "labels": [f"M{i}" for i in range(13)], "values": list(range(13))}
    ctx, page = answer_page(qa, b, chart_md(spec))
    marks = page.locator("#view svg.chart rect.ch-bar").count()
    check("chart with 13 labels shows all 13 (or says it cut)", marks == 13 or "12 of 13" in page.locator("#view .bubble.ant").inner_text(), f"{marks} bars")
    ctx.close()
    # A missing value is not drawn as zero.
    spec = {"type": "bar", "title": "Runway", "labels": ["Atlas", "Halo", "Orbit"], "values": [14, None, 9]}
    ctx, page = answer_page(qa, b, chart_md(spec))
    vals = page.evaluate("Array.from(document.querySelectorAll('#view svg.chart text.ch-val')).map(e => e.textContent)")
    check("a missing value (null) is not drawn as a 0 bar", "0" not in vals, str(vals))
    ctx.close()
    # Fewer values than labels: no NaN in the label text.
    spec = {"type": "line", "title": "Short", "labels": ["A", "B", "C"], "values": [1, 2]}
    ctx, page = answer_page(qa, b, chart_md(spec))
    al = page.locator("#view svg.chart").get_attribute("aria-label") if page.locator("#view svg.chart").count() else ""
    check("fewer values than labels: chart label has no NaN", "NaN" not in (al or ""), str(al))
    ctx.close()


def t_stream(qa, b) -> None:
    ctx, page = qa.open2(b, sample={"answer": "x"}, stream=True)
    open_ask(page)
    page.locator("#view textarea").fill("Runway?"); page.locator("#view textarea").press("Enter"); page.wait_for_timeout(80)
    full = "Two are short.\n\n- Atlas: 9 months\n\n```chart\n{\"type\": \"bar\", \"title\": \"Runway\", \"labels\": [\"Atlas\", \"Halo\"], \"values\": [9, 14]}\n```\n\nCheck Halo."
    cut = full.index('"labels"') + 12
    page.evaluate("t => window.__push(t, false)", full[:cut]); page.wait_for_timeout(60)
    t = page.locator("#view .bubble.ant").inner_text()
    check("streaming: an open chart fence shows the text before it and no raw JSON", "Two are short." in t and "labels" not in t and "```" not in t, t[:160])
    check("streaming: Stop shows while live", page.locator("#view .ask-form button", has_text="Stop").count() == 1)
    page.evaluate("t => window.__push(t, false)", full[: full.index("```\n\nCheck") + 3]); page.wait_for_timeout(60)
    check("streaming: the chart draws once its fence closes", page.locator("#view .bubble.ant svg.chart").count() == 1)
    page.evaluate("t => window.__push(t, true)", full); page.wait_for_timeout(80)
    t = page.locator("#view .bubble.ant").inner_text()
    check("streaming: final answer has the chart and the line after it", page.locator("#view .bubble.ant svg.chart").count() == 1 and "Check Halo." in t, t[-120:])
    check("streaming: Ask button returns after the answer", page.locator("#view .ask-form button", has_text="Ask").count() == 1)
    check("streaming: no script errors", not errs(page), "; ".join(errs(page)[:3]))
    ctx.close()
    # A code block that is not a chart is shown, not silently dropped.
    ctx, page = answer_page(qa, b, "Here is the formula.\n\n```\nIRR = 24%\n```\n\nThat is it.")
    t = page.locator("#view .bubble.ant").inner_text()
    check("a plain fenced block is shown, not dropped", "IRR = 24%" in t, t[:160])
    ctx.close()


def t_ask_errors(qa, b) -> None:
    for code, needle in (("not_granted", "allowed"), ("rate_limited", "busy"), ("unavailable", "allowed")):
        ctx, page = qa.open2(b, sample={"fail": code})
        open_ask(page)
        page.locator("#view textarea").fill("Who owes me?"); page.locator("#view textarea").press("Enter"); page.wait_for_timeout(150)
        t = page.locator("#view .bubble.ant").inner_text() if page.locator("#view .bubble.ant").count() else ""
        check(f"Ask error {code}: clear message", needle in t.lower() and "thinking" not in t.lower(), t[:160])
        check(f"Ask error {code}: Ask button back (not Stop)", page.locator("#view .ask-form button", has_text="Ask").count() == 1)
        check(f"Ask error {code}: no script errors", not errs(page), "; ".join(errs(page)[:3]))
        ctx.close()


def t_quick(qa, b) -> None:
    ctx, page = qa.open2(b, sample={"answer": "Three things you owe."})
    page.locator(".fab-main").click(); page.wait_for_timeout(60)
    check("floating Ask opens the quick sheet, focus in the box", page.locator(".sheet[aria-label='Ask ant.']").count() == 1 and page.evaluate("document.activeElement.tagName") == "TEXTAREA")
    page.locator(".sheet textarea").fill("What do I owe?"); page.locator(".sheet textarea").press("Enter"); page.wait_for_timeout(150)
    check("quick sheet shows the answer", "Three things" in page.locator(".sheet").inner_text())
    page.keyboard.press("Escape"); page.wait_for_timeout(40)
    page.locator("body").click(position={"x": 700, "y": 10})
    page.keyboard.press("/"); page.wait_for_timeout(60)
    check("'/' opens the quick sheet", page.locator(".sheet[aria-label='Ask ant.']").count() == 1)
    page.keyboard.press("Escape")
    page.locator("#view").click(position={"x": 5, "y": 5}) if page.locator("#view").count() else None
    open_ask(page)
    page.locator("#view textarea").click(); page.keyboard.type("a/b")
    check("'/' typed in the Ask box stays text", page.locator("#view textarea").input_value().endswith("a/b") and page.locator(".sheet").count() == 0)
    ctx.close()


# ---------------------------------------------------------------------------------------------------- PDF
def t_pdf_panels(qa, b) -> None:
    ctx, page = qa.open2(b, sample={"answer": "- A line.", "json": {}})
    opened = []

    def pdf_once(label: str) -> None:
        sheet = page.locator(".sheet.drawer")
        if sheet.count() != 1:
            check(f"PDF {label}: panel opened", False, "no drawer"); return
        n = len(page.evaluate("window.__downloads"))
        page.locator(".sheet-foot .pdf-btn").click(); page.wait_for_timeout(150)
        d = page.evaluate("window.__downloads")[n:]
        check(f"PDF {label}: one save with a .pdf name", len(d) == 1 and d[0]["filename"].endswith(".pdf") and d[0]["filename"].startswith("2026-10-22 "), json.dumps(d)[:200])
        opened.append(label)
        page.keyboard.press("Escape"); page.wait_for_timeout(40)

    for sec in ("Decisions", "Threads"):
        loc = page.locator(f"section[aria-label='{sec}'] .row-hit")
        if loc.count():
            loc.first.click(); page.wait_for_timeout(120); pdf_once("Today " + sec)
    page.locator('#rail-tabs button[aria-label="Pipeline"]').click(); page.wait_for_timeout(100)
    page.locator("table.deals tbody tr .row-hit").first.click(); page.wait_for_timeout(150)
    pdf_once("Pipeline deal")
    pit = page.locator("section[aria-label='Pitches'] .row-hit")
    if pit.count():
        pit.first.click(); page.wait_for_timeout(150); pdf_once("Pipeline pitch")
    for tab in ("People", "Portfolio", "LPs"):
        page.locator(f'#rail-tabs button[aria-label="{tab}"]').click(); page.wait_for_timeout(100)
        page.locator("#view tbody .cell-hit").first.click(); page.wait_for_timeout(150)
        pdf_once(tab)
    # A meeting note, opened from search.
    nt = list(qa.snaps["aditi"]["notes"]["items"].values())[0]
    page.locator(".fab-main").click(); page.locator(".sheet textarea").fill(nt["title"]); page.wait_for_timeout(100)
    page.locator(".sheet .hit", has_text=nt["title"]).first.click(); page.wait_for_timeout(150)
    pdf_once("Meeting note")
    # Double tap on PDF: one save prompt, not two.
    page.locator('#rail-tabs button[aria-label="Today"]').click(); page.wait_for_timeout(80)
    page.locator("section[aria-label='Decisions'] .row-hit").first.click(); page.wait_for_timeout(120)
    n = len(page.evaluate("window.__downloads"))
    page.locator(".sheet-foot .pdf-btn").dblclick(); page.wait_for_timeout(200)
    d = page.evaluate("window.__downloads")[n:]
    check("PDF double tap asks to save once", len(d) == 1, f"{len(d)} saves")
    check("no script errors across panel PDFs", not errs(page), "; ".join(errs(page)[:3]))
    ctx.close()


def t_pdf_text(qa, b) -> None:
    s = deep(qa.snaps["aditi"])
    # A meeting note with hostile text and 500 lines, opened from its panel.
    nid = list(s["notes"]["items"])[0]
    note = s["notes"]["items"][nid]
    hostile = "Fee ₹2,50,000 → Łukasz Nowak 😀 “quoted” — done… " + "x" * 3000
    note["lines"] = [{"t": "00:00:01", "who": "Aditi Rao", "text": hostile}] + [{"t": "00:00:%02d" % (i % 60), "who": "Varun Khanna", "text": f"Line {i} of the call."} for i in range(500)]
    note["more"] = 0
    ctx, page = qa.open2(b, snap=s, sample={"answer": "- ok"})
    title = note["title"]
    page.locator(".fab-main").click(); page.locator(".sheet textarea").fill(title); page.wait_for_timeout(100)
    hit = page.locator(".sheet .hit", has_text=title)
    if hit.count():
        hit.first.click(); page.wait_for_timeout(200)
    sheet = page.locator(".sheet.drawer")
    if not sheet.count():
        check("PDF text: a panel with the long note opened", False, "could not open note " + title)
        ctx.close(); return
    page.evaluate("window.__pdf = { text: [], links: [], pages: 1 }")
    n = len(page.evaluate("window.__downloads"))
    page.locator(".sheet-foot .pdf-btn").click(); page.wait_for_timeout(300)
    pdf = page.evaluate("window.__pdf")
    text = "\n".join(pdf["text"])
    check("PDF text: saved once", len(page.evaluate("window.__downloads")[n:]) == 1)
    check("PDF text: rupee becomes Rs, arrow becomes ->", "Rs 2,50,000" in text and "->" in text, [t for t in pdf["text"] if "Fee" in t][:1])
    check("PDF text: no character outside Latin-1 reaches jsPDF", all(all(ord(c) < 256 for c in t) for t in pdf["text"]))
    check("PDF text: a name with a non-Latin-1 letter keeps a readable form (Lukasz, not ukasz)", "Lukasz" in text, [t[:60] for t in pdf["text"] if "ukasz" in t][:1])
    check("PDF text: a note line keeps a space between its time and the speaker", any("00:01 Aditi Rao" in t for t in pdf["text"]), [t[:30] for t in pdf["text"] if "Fee" in t][:1])
    lines_in = sum(1 for t in pdf["text"] if "of the call" in t)
    check("PDF text: 500 lines span several pages", pdf["pages"] >= 5 and lines_in >= 500, f"{pdf['pages']} pages, {lines_in} lines")
    check("PDF text: the source link of the note is collected", any("granola" in l for l in pdf["links"]), str(pdf["links"][:3]))
    check("PDF text: no script errors", not errs(page), "; ".join(errs(page)[:3]))
    ctx.close()


def t_pdf_fail(qa, b) -> None:
    for code, needle in (("declined", None), ("rate_limited", "already open"), ("unavailable", "could not save")):
        ctx, page = qa.open2(b, sample={"answer": "- ok"}, dlFail=code)
        page.locator("section[aria-label='Decisions'] .row-hit").first.click(); page.wait_for_timeout(120)
        page.locator(".sheet-foot .pdf-btn").click(); page.wait_for_timeout(200)
        t = page.locator("#toast-slot").inner_text().lower()
        ok = ("saved" not in t) and (needle is None or needle in t)
        check(f"PDF save {code}: handled ({needle or 'quiet'})", ok and not errs(page), t[:120])
        ctx.close()
    ctx, page = qa.open2(b, sample={"answer": "- ok"}, dlNull=True)
    page.locator("section[aria-label='Decisions'] .row-hit").first.click(); page.wait_for_timeout(120)
    vis = page.locator(".sheet-foot .pdf-btn").count()
    if vis:
        page.locator(".sheet-foot .pdf-btn").click(); page.wait_for_timeout(200)
    t = page.locator("#toast-slot").inner_text().lower()
    check("no downloads capability: PDF hidden or says it is not available", vis == 0 or "not available" in t, t[:120])
    ctx.close()
    ctx, page = qa.open2(b, sample={"answer": "- ok"}, pdf=False)
    page.locator("section[aria-label='Decisions'] .row-hit").first.click(); page.wait_for_timeout(120)
    page.locator(".sheet-foot .pdf-btn").click(); page.wait_for_timeout(1500)
    t = page.locator("#toast-slot").inner_text().lower()
    # 0.12.1: jsPDF ships inside the page, so there is no CDN that can fail: the PDF saves with no outside request.
    check("jsPDF is built in: a PDF saves without loading anything from a CDN", bool(page.evaluate("window.__downloads")), t[:120])
    check("jsPDF cannot load: no page error", not [e for e in page._qa_errors if "pageerror" in e.lower() or "uncaught" in e.lower()], "; ".join(page._qa_errors[:3]))
    page.locator(".sheet-foot .pdf-btn").click(); page.wait_for_timeout(1500)
    t = page.locator("#toast-slot").inner_text().lower()
    check("jsPDF is built in: a second save works too", len(page.evaluate("window.__downloads") or []) >= 2, t[:120])
    ctx.close()


def t_empathy(qa, b) -> None:
    s = demo.sample_research(deep(qa.snaps["aditi"]))
    ctx, page = qa.open2(b, snap=s, sample={"answer": "- ok", "json": {}})
    page.locator('#rail-tabs button[aria-label="Pipeline"]').click(); page.wait_for_timeout(100)
    page.locator("table.deals tbody tr", has_text="Atlas Settlement").locator(".row-hit").click(); page.wait_for_timeout(200)
    page.locator(".sheet .people-list .link-btn").first.click(); page.wait_for_timeout(200)
    btn = page.locator(".sheet .emp-block button", has_text="Empathy map PDF")
    if not btn.count():
        check("empathy map PDF button found", False, "no button"); ctx.close(); return
    page.evaluate("window.__pdf = { text: [], links: [], pages: 1 }")
    btn.first.click(); page.wait_for_timeout(300)
    pdf = page.evaluate("window.__pdf"); d = page.evaluate("window.__downloads")
    text = "\n".join(pdf["text"])
    check("empathy map PDF: two pages", pdf["pages"] == 2, f"{pdf['pages']} pages")
    # Page 2 opens with the firm or company, or (0.12.1) with the founder's company and its space when it was researched.
    mark = next((m for m in ("THE FIRM OR COMPANY", "WHAT THEY DO") if m in text), None)
    p2 = text[text.find(mark):] if mark else ""
    check("empathy map PDF: page 2 has the company, earlier calls and talking points", p2 and "FROM YOUR EARLIER CALLS AND MAIL" in p2 and "TALKING POINTS" in p2 and "1. " in p2, text[-300:])
    check("empathy map PDF: file named date, person, company", len(d) == 1 and d[0]["filename"].endswith(".pdf") and d[0]["filename"].startswith("2026-") and "Ishaan Verma" in d[0]["filename"] and "Atlas" in d[0]["filename"], json.dumps(d))
    check("empathy map PDF: LinkedIn link collected", any("linkedin" in l for l in pdf["links"]), str(pdf["links"]))
    check("empathy map PDF: no script errors", not errs(page), "; ".join(errs(page)[:3]))
    ctx.close()


def t_settings(qa, b) -> None:
    rat = [{"id": "rt_note", "item_id": "x1", "value": "note", "note": "Name the counsel, not the firm", "title": "Atlas legal", "at": "2026-10-21T10:00:00+05:30"},
           {"id": "rt_edit", "item_id": "x2", "kind": "draft_edit", "value": "edited", "note": "Shorter sign-off", "title": "Intro to Halo", "at": "2026-10-20T10:00:00+05:30"},
           {"id": "rt_plain", "item_id": "x3", "value": "useful", "title": "Plain rating", "at": "2026-10-20T09:00:00+05:30"}]
    # Ratings come from the collection: a db wrapper feeds these three in.
    ctx = b.new_context(viewport=Q.DESK, timezone_id="Asia/Kolkata")
    page = ctx.new_page()
    page.route("**/fonts.g*/**", lambda r: r.abort())
    qa_cfg = {"snap": qa.snaps["aditi"], "open_all": False, "inline": False, "state": {"settings": {}}}
    rat_js = json.dumps(rat)
    page.add_init_script("window.__QA__ = " + json.dumps(qa_cfg, default=str) + ";" + Q.MOCK + WRAP + r"""
    (function () { var u = window.claude.use; window.claude.use = function (n) { return u(n).then(function (x) { if (n !== 'db' || !x) return x;
      var c0 = x.collection; return Object.assign({}, x, { collection: function (name) { var q = c0(name); if (name !== 'ratings') return q;
        var R = """ + rat_js + r"""; var me = { orderBy: function () { return me; }, limit: function () { return me; }, where: function () { return me; }, add: q.add,
          onSnapshot: function (next) { setTimeout(function () { next({ docs: R.map(function (r) { var d = Object.assign({}, r); delete d.id; return { id: r.id, exists: true, data: function () { return d; } }; }), size: R.length, empty: false, docChanges: function () { return []; } }); }, 20); return function () {}; } };
        return me; } }); }); }; })();""")
    errors: list[str] = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.clock.set_fixed_time(Q.T0)
    page.goto("file://" + qa.wrapper); page.wait_for_timeout(300)
    page._qa_errors = errors
    page.locator('#rail-tabs [aria-label="Settings"]').click(); page.wait_for_timeout(100)
    # Icon chips: for each tool row with a seg, tap a level not pressed and read the write.
    groups = page.locator("#view .tool-row .seg[role=group]")
    ng = groups.count()
    bad = []
    for i in range(ng):
        g = groups.nth(i)
        label = g.get_attribute("aria-label")
        btns = g.locator("button")
        for j in range(btns.count()):
            bt = page.locator("#view .tool-row .seg[role=group]").nth(i).locator("button").nth(j)
            if bt.get_attribute("aria-pressed") == "true":
                continue
            word = bt.get_attribute("aria-label")
            n = len(page.evaluate("window.__writes"))
            bt.click(); page.wait_for_timeout(80)
            w = [x for x in page.evaluate("window.__writes")[n:] if x.get("path") == "state/settings"]
            acc = (w[-1]["data"]["items"].get("access") or {}) if w else {}
            g2 = page.locator("#view .tool-row .seg[role=group]").nth(i)
            now_word = g2.locator("xpath=following-sibling::span[contains(@class,'lvl-word')]").inner_text() if g2.count() else ""
            pressed = g2.locator("button[aria-pressed=true]").get_attribute("aria-label") if g2.count() else ""
            if not w or now_word != word or pressed != word:
                bad.append(f"{label}/{word}: write {bool(w)} word {now_word!r} pressed {pressed!r}")
    check(f"Settings: each icon chip writes state/settings and updates its word ({ng} tools)", ng >= 2 and not bad, "; ".join(bad[:4]))
    w = [x for x in page.evaluate("window.__writes") if x.get("path") == "state/settings"]
    acc = w[-1]["data"]["items"].get("access") if w else {}
    check("Settings: access map holds one level per tool key", bool(acc) and all(v in ("read", "write", "off", "draft", "ask", "send") for v in acc.values()), json.dumps(acc))
    learned = page.locator("section[aria-label='What ant. learned from you']")
    t = learned.inner_text()
    check("Settings: learned lists the note and the draft edit, not plain ratings", "Name the counsel" in t and "You edited a draft: Intro to Halo" in t and "Plain rating" not in t, t[:200])
    learned.locator(".tool-row", has_text="Name the counsel").locator("button", has_text="Remove").click(); page.wait_for_timeout(100)
    dels = page.evaluate("window.__deletes")
    check("Settings: Remove deletes that ratings doc only", dels == ["ratings/rt_note"], str(dels))
    check("Settings: removed note leaves the list", "Name the counsel" not in page.locator("section[aria-label='What ant. learned from you']").inner_text())
    check("Settings: no script errors", not errors, "; ".join(errors[:3]))
    ctx.close()
    # Phone width.
    for vp in (Q.PHONE, {"width": 320, "height": 640}):
        ctx, page = qa.open2(b, viewport=vp, state={"settings": {}})
        page.evaluate("1")
        # Settings sits in the header or bottom tabs on a phone.
        page.locator("#help-btn").click(); page.wait_for_timeout(80)
        page.locator(".sheet button", has_text="Settings and your tools").click(); page.wait_for_timeout(120)
        on = page.locator("section[aria-label='Your tools']").count() == 1
        over = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
        wide = page.evaluate("""Array.from(document.querySelectorAll('#view .tool-row, #view .seg, #view .access')).filter(e => e.offsetParent && e.getBoundingClientRect().right > window.innerWidth + 1).length""")
        check(f"Settings at {vp['width']}px: reachable, no sideways scroll, no row past the edge", on and over <= 0 and wide == 0, f"on {on} over {over} wide {wide}")
        ctx.close()


# ---------------------------------------------------------------------------------------------------- round 2 probes
def t_round2_parse(qa, b) -> None:
    ctx, page = qa.open2(b, state={"reminders": {}})
    to_reminders(page)
    d = lambda day, hh, mm=0: dt.datetime(2026, 10, day, hh, mm, tzinfo=IST)
    for text, want in (("Call Ana at 9", d(22, 9)), ("Call Ana at 1", d(22, 13)), ("Pay it tomorrow at 12am", d(23, 0)),
                       ("Wire at 9.30", d(22, 9, 30)), ("Call Ana at 7am.", d(23, 7)), ("Dinner at 11pm, then sleep", d(22, 23)),
                       ("Call Ana at 5, then email", d(22, 17)), ("Standup at 07:30", d(22, 7, 30)), ("Call Ana at 00:30", d(23, 0, 30))):
        got = add_via_form(page, text)
        check(f"round 2 parse IST 07:05: {text!r} -> {want.strftime('%a %d %H:%M')}", same_instant(got, want), "got " + show(got, IST))
    got = add_via_form(page, "Check today at 5am")
    ok = got not in (None, "NO-WRITE") and dt.datetime.fromisoformat(got.replace("Z", "+00:00")) > Q.T0
    check("round 2: 'today at 5am' at 07:05 is not saved in the past", ok, show(got, IST))
    ctx.close()
    syd = ZoneInfo("Australia/Sydney")
    now = dt.datetime(2027, 4, 2, 10, 0, tzinfo=syd)
    ctx, page = qa.open2(b, when=now, tz="Australia/Sydney", snap=snap_tz(qa, "Australia/Sydney"), state={"reminders": {}})
    to_reminders(page)
    got = add_via_form(page, "Board pack monday")
    check("Sydney: 'monday' after the April clock change is Mon 5 Apr 09:00 AEST", same_instant(got, dt.datetime(2027, 4, 5, 9, tzinfo=syd)), show(got, syd))
    ctx.close()
    now = dt.datetime(2027, 3, 13, 10, 0, tzinfo=NY)
    ctx, page = qa.open2(b, when=now, tz="America/New_York", snap=snap_tz(qa, "America/New_York"), state={"reminders": {}})
    to_reminders(page)
    got = add_via_form(page, "Send deck tomorrow at 9")
    check("New York spring forward: 'tomorrow at 9' is Sun 14 Mar 09:00 EDT", same_instant(got, dt.datetime(2027, 3, 14, 9, tzinfo=NY)), show(got, NY))
    got = add_via_form(page, "Odd one tomorrow at 2:30am")
    ok = got not in (None, "NO-WRITE") and show(got, NY)[:9] == "Sun 14 Ma" and show(got, NY)[11:16] in ("01:30", "03:30")
    check("New York spring forward: a 02:30 that does not exist lands at 01:30 or 03:30 on 14 Mar", ok, show(got, NY))
    ctx.close()


def t_round2_chart_pdf(qa, b) -> None:
    ctx, page = answer_page(qa, b, chart_md({"type": "bar", "title": "S", "labels": ["A", "B"], "values": ["9", "14"]}))
    check("chart with string values is left out", page.locator("#view svg.chart").count() == 0 and "Done." in page.locator("#view .bubble.ant").inner_text())
    ctx.close()
    ctx, page = answer_page(qa, b, chart_md({"type": "bar", "title": "Twenty", "labels": [f"M{i}" for i in range(20)], "values": list(range(1, 21))}))
    n = page.locator("#view svg.chart rect.ch-bar").count()
    al = page.locator("#view svg.chart").get_attribute("aria-label") or ""
    check("chart with 20 labels draws 16 and says first 16 of 20", n == 16 and "first 16 of 20" in al, f"{n} bars, {al[:60]}")
    ctx.close()
    ctx, page = qa.open2(b, viewport=Q.PHONE, sample={"answer": chart_md({"type": "bar", "title": "Ten", "labels": [f"Company {i}" for i in range(10)], "values": list(range(10))})})
    page.locator(".fab-main").click(); page.locator(".sheet textarea").fill("q"); page.locator(".sheet textarea").press("Enter"); page.wait_for_timeout(150)
    hs = page.evaluate("Array.from(document.querySelectorAll('.sheet svg.chart rect.ch-bar')).map(r => r.getAttribute('height'))")
    over = page.evaluate("(() => { var s = document.querySelector('.sheet svg.chart'); return s ? Math.round(s.getBoundingClientRect().right - innerWidth) : 99; })()")
    check("phone: 10 bars lie flat, one row each, inside the screen", len(hs) == 10 and all(h == "16" for h in hs) and over <= 0, f"{hs[:3]} over {over}")
    ctx.close()
    ctx, page = qa.open2(b, sample={"answer": "- ok"})
    page.locator("section[aria-label='Decisions'] .row-hit").first.click(); page.wait_for_timeout(120)
    page.locator(".sheet-foot .pdf-btn").click(); page.wait_for_timeout(2000)
    page.locator(".sheet-foot .pdf-btn").click(); page.wait_for_timeout(300)
    check("PDF: a second tap after the busy window saves again", len(page.evaluate("window.__downloads")) == 2, str(len(page.evaluate("window.__downloads"))))
    ctx.close()


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    qa = QA2(OUT)
    tests = [t_parse_phrases, t_clocks, t_zones, t_actions, t_first_write, t_brief_fail, t_bell, t_static,
             t_ask_styles, t_ask_render, t_charts, t_stream, t_ask_errors, t_quick,
             t_pdf_panels, t_pdf_text, t_pdf_fail, t_empathy, t_settings, t_round2_parse, t_round2_chart_pdf]
    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    with sync_playwright() as p:
        b = p.chromium.launch()
        for t in tests:
            if only and t.__name__ not in only:
                continue
            try:
                t(qa, b)
            except Exception as e:  # a test that crashes is a failed check, never a crashed suite
                check(f"{t.__name__} ran to the end", False, f"{type(e).__name__}: {e}"[:300])
        b.close()
    ok = sum(1 for r in RESULTS if r[1])
    print(f"{ok}/{len(RESULTS)} checks pass")
    return 1 if ("--strict" in sys.argv and ok < len(RESULTS)) else 0


if __name__ == "__main__":
    sys.exit(main())
