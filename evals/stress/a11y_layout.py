"""Stress: accessibility (WCAG 2.2 AA) and responsive layout of the 0.11.0 surfaces of ant. Home.

Side panels, composer, timeline, citations, founder 360, deals table filters, Ask pickers and charts, reminders tab and
sheet, the floating Ask and bell buttons, Settings icon chips, "What ant. learned from you".

    python3 evals/stress/a11y_layout.py

Prints one PASS/FAIL line per check, then "N/M checks pass". Every check passes when Home behaves correctly.
Exit code 0 always (this is a report, the summary line carries the result).
"""

from __future__ import annotations

import json
import os
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
EVALS = os.path.dirname(HERE)
sys.path.insert(0, EVALS)
import home_qa as Q  # noqa: E402
import demo  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

OUT = os.environ.get("STRESS_OUT", "/tmp/claude-0/-home-claude/f41ebfd9-0635-5201-96ea-278169523f82/scratchpad/stress-a11y")
qa = Q.QA(OUT)
ROWS: list[tuple[bool, str, str]] = []


def check(name: str, ok, detail: str = "") -> None:
    ROWS.append((bool(ok), name, detail))
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail and not ok else ""), flush=True)


TL = {"tldr": [{"text": "Gravity Payouts set reference calls with three gig platforms.", "cites": [1]},
               {"text": "and later it was set.", "cites": [8]}],
      "recommendation": {"text": "Approve the new next step for Gravity Payouts.", "why": [{"text": "Gravity Payouts agreed it in the partner prep.", "cites": [1]}]},
      "subject": "Quick reminder", "body": "Hi, a quick reminder. Aditi"}
LABELS = ["Orbit Treasury", "Kestrel Pay", "Gravity Payouts", "Atlas Settlement", "Bluepeak Labs", "Nimbus Credit",
          "Ferro Ledger", "Quanta Risk", "Helio Pay", "Lumen Bank", "Cobalt FX", "Delta Cards"]
MD = ("Runway by company.\n\n```chart\n" + json.dumps({"type": "bar", "title": "Runway, months", "unit": "", "labels": LABELS,
      "values": [8, 10, 12, -3, 14, 6, 9, 11, 5, 7, 13, 4]}) + "\n```")
REM = {"items": {}, "actions": {}, "reminders": {"rq1": {"text": "Call Vikram Rao about Orbit Treasury runway", "due": "2026-10-22T07:30:00+05:30", "at": "2026-10-21T19:00:00+05:30"}}}

ACTIVE = """(() => { var a = document.activeElement; if (!a || a === document.body || a === document.documentElement) return {body: true};
  return {body: false, inSheet: !!a.closest('.sheet'), tag: a.tagName, cls: String(a.className || ''), name: (a.getAttribute('aria-label') || a.textContent || '').trim().slice(0, 60),
          li: (a.closest('li.tl-ev') || {}).id || ''}; })()"""

# Accessible name, close enough for buttons, links and fields: aria-label, labelledby, text, title, a wrapping or for= label.
UNNAMED = """(scope) => { var root = document.querySelector(scope) || document.body;
  return Array.from(root.querySelectorAll('button, a[href], input:not([type=hidden]), select, textarea')).filter(e => e.getClientRects().length).filter(e => {
    if ((e.getAttribute('aria-label') || '').trim()) return false;
    var lb = e.getAttribute('aria-labelledby'); if (lb && lb.split(' ').some(id => (document.getElementById(id) || {}).textContent)) return false;
    if (/^(BUTTON|A)$/.test(e.tagName) && (e.textContent || '').trim()) return false;
    if ((e.getAttribute('title') || '').trim()) return false;
    if (e.closest('label') && e.closest('label').textContent.trim()) return false;
    if (e.id && document.querySelector('label[for="' + e.id + '"]')) return false;
    return true; }).map(e => e.outerHTML.slice(0, 90)); }"""

SMALL = """([sel, min]) => Array.from(document.querySelectorAll(sel)).filter(e => e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden')
  .map(e => { var r = e.getBoundingClientRect(); return [(e.getAttribute('aria-label') || e.textContent || '').trim().slice(0, 24), Math.round(r.width), Math.round(r.height)]; })
  .filter(x => Math.min(x[1], x[2]) < min)"""

OVERFLOW = """(() => { var d = document.documentElement.scrollWidth - innerWidth, s = document.querySelector('.sheet'), cut = [];
  if (s) { var sr = s.getBoundingClientRect();
    s.querySelectorAll('*').forEach(e => { var r = e.getBoundingClientRect(); if (!r.width || !e.getClientRects().length || e.closest('.table-wrap')) return;
      if (r.right > Math.min(sr.right, innerWidth) + 1 || r.left < Math.max(sr.left, 0) - 1) cut.push(e.tagName + '.' + String(e.className || '').slice(0, 30) + ' ' + Math.round(r.left) + '-' + Math.round(r.right)); }); }
  return {doc: d, sheet: s ? s.scrollWidth - s.clientWidth : 0, cut: cut.slice(0, 4)}; })()"""


class Touch:
    """A browser whose contexts are touch screens, so (pointer: coarse) matches as on a real phone."""
    def __init__(self, b):
        self.b = b

    def new_context(self, **kw):
        kw["has_touch"] = True
        kw["is_mobile"] = True
        return self.b.new_context(**kw)


def errs(page):
    return [e for e in page._qa_errors if "fonts.g" not in e and "ERR_FAILED" not in e]


def panel(page, section="Decisions"):
    page.locator(f"section[aria-label='{section}'] .row-hit").first.click()
    page.wait_for_timeout(250)


# ---------------------------------------------------------------------------- keyboard
def keyboard(b, rsnap):
    ctx, page = qa.open(b, "kb", Q.DESK, open_all=False, inline=False, sample={"answer": "x", "json": TL}, mcp={"pages": ["ok"]})
    opener = page.locator("section[aria-label='Decisions'] .row-hit").first
    opener_name = opener.inner_text()[:30]
    opener.focus(); page.keyboard.press("Enter"); page.wait_for_timeout(300)
    a = page.evaluate(ACTIVE)
    check("K1 opening a panel by keyboard puts focus inside it", a.get("inSheet"), json.dumps(a))
    out, names = 0, []
    for _ in range(45):
        page.keyboard.press("Tab")
        a = page.evaluate(ACTIVE); names.append(a.get("name", ""))
        out += 0 if a.get("inSheet") else 1
    check("K2 Tab never leaves the open panel (focus trap)", out == 0, f"{out} of 45 tabs left the panel")
    check("K3 the footer buttons and the PDF button are reachable by Tab", "PDF" in names and any(n.startswith("Approve") for n in names), ", ".join(dict.fromkeys(names)))
    out = 0
    for _ in range(25):
        page.keyboard.press("Shift+Tab")
        out += 0 if page.evaluate(ACTIVE).get("inSheet") else 1
    check("K4 Shift+Tab never leaves the open panel", out == 0, f"{out} left")
    cites = page.locator(".sheet .cite")
    cites.first.focus(); page.keyboard.press("Enter"); page.wait_for_timeout(200)
    a = page.evaluate(ACTIVE)
    check("K5 a citation moves focus to its timeline event's link", a.get("li") == "tl-0" and a.get("tag") in ("A", "BUTTON"), json.dumps(a))
    c8 = page.locator(".sheet .cite", has_text="8")
    if c8.count():
        c8.first.focus(); page.keyboard.press("Enter"); page.wait_for_timeout(200)
        a = page.evaluate(ACTIVE)
        check("K6 a citation to a folded event unfolds the timeline and focuses that event", a.get("li") == "tl-7" and not page.evaluate("document.getElementById('tl-7').hidden"), json.dumps(a))
    else:
        check("K6 a citation to a folded event unfolds the timeline and focuses that event", False, "no cite 8 shown")
    page.keyboard.press("Escape"); page.wait_for_timeout(120)
    a = page.evaluate(ACTIVE)
    check("K7 Escape closes the panel and focus returns to the row that opened it", page.locator(".scrim").count() == 0 and opener_name[:12] in a.get("name", ""), json.dumps(a))
    # Approve from the footer: the panel closes; focus must land on something, not on <body>.
    opener = page.locator("section[aria-label='Decisions'] .row-hit").first
    opener.focus(); page.keyboard.press("Enter"); page.wait_for_timeout(300)
    foot = page.locator(".sheet-foot button").first
    label = foot.inner_text().strip()
    foot.focus(); page.keyboard.press("Enter"); page.wait_for_timeout(300)
    a = page.evaluate(ACTIVE)
    check(f"K8 after {label} in a panel's footer, focus lands on a control, not the page body", not a.get("body"), json.dumps(a))
    # "/" opens Ask from a focused row, types into the box, and Escape gives focus back.
    page.locator("#view .row-hit").first.focus()
    before = page.evaluate(ACTIVE)
    page.keyboard.press("/"); page.wait_for_timeout(150)
    a = page.evaluate(ACTIVE)
    check("K9 '/' opens Ask with the cursor in its box", page.locator(".sheet[aria-label='Ask ant.']").count() == 1 and a.get("tag") == "TEXTAREA", json.dumps(a))
    page.keyboard.type("a/b")
    check("K10 '/' typed inside the Ask box is just a character", page.locator(".sheet .ask-form textarea").input_value() == "a/b" and page.locator(".scrim").count() == 1)
    page.keyboard.press("Escape"); page.wait_for_timeout(100)
    a = page.evaluate(ACTIVE)
    check("K11 Escape from Ask returns focus to where it was", a.get("name") == before.get("name") and not a.get("body"), json.dumps(a))
    # Enter in the deals filter only filters.
    page.locator("#rail-tabs button[aria-label='Pipeline']").click(); page.wait_for_timeout(120)
    box = page.locator(".filter-row input[name='f-company']")
    box.focus(); page.keyboard.type("At"); page.keyboard.press("Enter"); page.wait_for_timeout(120)
    a = page.evaluate(ACTIVE)
    check("K12 Enter in the deals company filter opens nothing and keeps focus in the box", page.locator(".scrim").count() == 0 and a.get("tag") == "INPUT", json.dumps(a))
    check("K13 no script errors on the keyboard walk", not errs(page), "; ".join(errs(page)[:2]))
    ctx.close()

    # The composer: Enter in a field never sends; Send now leaves focus somewhere real.
    ctx, page = qa.open(b, "kb2", Q.DESK, open_all=False, inline=False, sample={"answer": "x", "json": TL}, mcp={"pages": ["ok"]})
    panel(page, "Threads")
    page.locator(".sheet .composer [name=subject]").focus(); page.keyboard.press("Enter"); page.wait_for_timeout(120)
    page.locator(".sheet .composer [name=to]").focus(); page.keyboard.press("Enter"); page.wait_for_timeout(120)
    sent = [m for m in page.evaluate("window.__mcp") if m["tool"] == "send_message"]
    check("K14 Enter in To or Subject neither sends nor opens the confirm", not sent and page.locator(".sheet .send-confirm").is_hidden())
    page.locator(".sheet .composer [name=body]").fill("Hi both, connecting you as promised. Aditi")
    page.locator(".sheet-foot button").first.focus(); page.keyboard.press("Enter"); page.wait_for_timeout(150)
    a = page.evaluate(ACTIVE)
    check("K15 Send moves focus to Send now in the confirm", a.get("name") == "Send now", json.dumps(a))
    page.keyboard.press("Enter"); page.wait_for_timeout(300)
    a = page.evaluate(ACTIVE)
    sent = [m for m in page.evaluate("window.__mcp") if m["tool"] == "send_message"]
    check("K16 after Send now, focus lands on a control, not the page body", len(sent) == 1 and not a.get("body"), json.dumps(a))
    ctx.close()

    # Founder 360: Back by keyboard, then Escape gives focus back to the deal row.
    ctx, page = qa.open(b, "kb3", Q.DESK, open_all=False, inline=False, sample={"answer": "x", "json": TL}, snap=rsnap)
    page.locator("#rail-tabs button[aria-label='Pipeline']").click(); page.wait_for_timeout(120)
    op = page.locator("table.deals tbody tr", has_text="Atlas Settlement").locator(".row-hit")
    op.focus(); page.keyboard.press("Enter"); page.wait_for_timeout(250)
    page.locator(".sheet .people-list .link-btn").first.focus(); page.keyboard.press("Enter"); page.wait_for_timeout(250)
    a = page.evaluate(ACTIVE)
    check("K17 a founder opened from a deal focuses Back first", a.get("name") == "Back" and page.evaluate("document.querySelector('.sheet').getAttribute('aria-label')") == "Ishaan Verma", json.dumps(a))
    page.keyboard.press("Enter"); page.wait_for_timeout(250)
    check("K18 Back by keyboard returns to the deal", page.evaluate("document.querySelector('.sheet').getAttribute('aria-label')") == "Atlas Settlement")
    page.keyboard.press("Escape"); page.wait_for_timeout(120)
    a = page.evaluate(ACTIVE)
    check("K19 Escape after Back returns focus to the deal row", "Atlas Settlement" in a.get("name", ""), json.dumps(a))
    # A typed next step survives an accidental Escape (the draft composer already keeps its edits this way).
    op.click(); page.wait_for_timeout(250)
    page.locator(".sheet .field[name=next]").fill("Call the CFO on Friday")
    page.keyboard.press("Escape"); page.wait_for_timeout(100)
    op.click(); page.wait_for_timeout(250)
    kept = page.locator(".sheet .field[name=next]").input_value()
    check("K20 a typed next step is not lost when Escape closes the deal panel", kept == "Call the CFO on Friday", repr(kept))
    ctx.close()

    # The bell: the reminder sheet, Enter saves, Escape returns to the bell.
    ctx, page = qa.open(b, "kb4", Q.DESK, open_all=False, state=json.loads(json.dumps(REM)))
    page.locator(".fab .fab-mini").focus(); page.keyboard.press("Enter"); page.wait_for_timeout(150)
    a = page.evaluate(ACTIVE)
    check("K21 the bell opens Remind me with the cursor in its box", a.get("tag") == "INPUT", json.dumps(a))
    page.keyboard.type("Chase Atlas legal tomorrow at 5pm"); page.keyboard.press("Enter"); page.wait_for_timeout(150)
    w = [x for x in page.evaluate("window.__writes") if x.get("path") == "state/reminders"]
    check("K22 Enter in Remind me saves exactly one reminder", len(w) == 1, f"{len(w)} writes")
    page.keyboard.press("Escape"); page.wait_for_timeout(100)
    a = page.evaluate(ACTIVE)
    check("K23 Escape from Remind me returns focus to the bell", a.get("name") == "Remind me" and not a.get("inSheet"), json.dumps(a))
    ctx.close()

    # Round 2: closing a sheet must not hand focus to an older toast's Undo, where Enter would undo an unrelated action.
    ctx, page = qa.open(b, "kb5", Q.DESK, open_all=False, inline=False, sample={"answer": "x", "json": TL}, mcp={"pages": ["ok"]}, state=json.loads(json.dumps(REM)))
    panel(page, "Decisions")
    page.locator(".sheet-foot button", has_text="Skip").click(); page.wait_for_timeout(300)
    page.locator(".fab .fab-mini").click(); page.wait_for_timeout(150)
    page.locator(".sheet button", has_text="All reminders").click(); page.wait_for_timeout(300)
    a = page.evaluate(ACTIVE)
    n = len(page.evaluate("window.__writes"))
    page.keyboard.press("Enter"); page.wait_for_timeout(200)
    undone = [w for w in page.evaluate("window.__writes")[n:] if "withdrawn" in json.dumps(w)]
    check("K24 after All reminders, focus is not on the earlier Skip's Undo, and Enter undoes nothing", a.get("name") != "Undo" and not undone, json.dumps(a) + f" {len(undone)} undo writes")
    ctx.close()


# ---------------------------------------------------------------------------- names and roles
def names(b, rsnap):
    ctx, page = qa.open(b, "nm", Q.DESK, open_all=False, inline=False, sample={"answer": MD, "json": TL}, mcp={"pages": ["ok"]}, snap=rsnap, state=json.loads(json.dumps(REM)))
    seen = []

    def dialog(tag):
        d = page.evaluate("(() => { var s = document.querySelector('.sheet'); return s ? [s.getAttribute('role'), s.getAttribute('aria-modal'), s.getAttribute('aria-label')] : null; })()")
        seen.append((tag, d, page.evaluate(UNNAMED, ".sheet")))

    panel(page, "Decisions"); dialog("decision"); page.keyboard.press("Escape")
    panel(page, "Threads"); dialog("thread")
    alerts = page.evaluate("Array.from(document.querySelectorAll('.sheet [role=alert]')).filter(e => e.getClientRects().length).map(e => e.className)")
    check("N1 an off-topic summary warns once, as role=alert", alerts == ["watch-note"], str(alerts))
    nested = page.evaluate("""Array.from(document.querySelectorAll('.sheet [aria-live], .sheet [role=alert], .sheet [role=status]')).filter(e => e.getClientRects().length &&
        e.parentElement.closest('[aria-live], [role=alert], [role=status]')).map(e => e.className)""")
    check("N2 no live region sits inside another live region (each warning is read once)", not nested, str(nested))
    page.keyboard.press("Escape")
    page.locator(".fab .fab-mini").click(); page.wait_for_timeout(120); dialog("remind"); page.keyboard.press("Escape")
    page.locator(".fab .fab-main").click(); page.wait_for_timeout(120)
    page.locator(".sheet .ask-form textarea").fill("runway?"); page.keyboard.press("Enter"); page.wait_for_timeout(400)
    dialog("ask")
    chart = page.evaluate("(() => { var s = document.querySelector('.sheet svg.chart'); return s ? [s.getAttribute('role'), s.getAttribute('aria-label')] : null; })()")
    check("N3 an Ask chart is an image named with every value", bool(chart) and chart[0] == "img" and all(l in chart[1] for l in LABELS), str(chart)[:120])
    page.keyboard.press("Escape")
    page.locator("#rail-tabs button[aria-label='Pipeline']").click(); page.wait_for_timeout(120)
    page.locator("table.deals tbody tr", has_text="Atlas Settlement").locator(".row-hit").click(); page.wait_for_timeout(250)
    dialog("deal")
    page.locator(".sheet .people-list .link-btn").first.click(); page.wait_for_timeout(250)
    dialog("founder"); page.keyboard.press("Escape")
    for tag, d, unnamed in seen:
        check(f"N4 the {tag} panel is a labelled modal dialog", bool(d) and d[0] == "dialog" and d[1] == "true" and bool((d[2] or "").strip()), str(d))
        check(f"N5 every control in the {tag} panel has a name", not unnamed, "; ".join(unnamed[:2]))
    check("N6 the deals filter row has a named control per column", not page.evaluate(UNNAMED, ".filter-row") and page.locator(".filter-row :is(select, input)").count() >= 4)
    rb = page.locator("#rail-tabs button[title='Your reminders']")
    check("N7 the Reminders tab says how many are due, not just a red number", rb.count() == 1 and "1 due" in (rb.get_attribute("aria-label") or ""), str(rb.get_attribute("aria-label") if rb.count() else None))
    check("N8 the floating buttons are a named group with named buttons", page.evaluate("(() => { var f = document.querySelector('.fab'); return !!f && f.getAttribute('role') === 'group' && !!f.getAttribute('aria-label') && Array.from(f.querySelectorAll('button')).every(b => b.getAttribute('aria-label')); })()"))
    page.locator("#rail-tabs button[aria-label='Settings']").click(); page.wait_for_timeout(150)
    chips = page.locator("#view .seg[aria-label$='what ant. may do'] button")
    check("N9 Settings access chips are icon-only but named, with a pressed state", chips.count() >= 6 and all(chips.nth(i).get_attribute("aria-label") and chips.nth(i).get_attribute("aria-pressed") in ("true", "false") for i in range(chips.count())))
    learned = page.locator("section[aria-label='What ant. learned from you']")
    check("N10 'What ant. learned from you' is a named section with a heading", learned.count() == 1 and learned.locator("h2").count() == 1)
    check("N11 every control on Settings has a name", not page.evaluate(UNNAMED, "#view"), "; ".join(page.evaluate(UNNAMED, "#view")[:2]))
    check("N12 no script errors while naming", not errs(page), "; ".join(errs(page)[:2]))
    ctx.close()


# ---------------------------------------------------------------------------- contrast
CHART_CONTRAST = """(() => { function parse(c) { var m = String(c || '').match(/rgba?\\(([^)]+)\\)/); if (!m) return null; var p = m[1].split(/[\\s,\\/]+/).filter(Boolean).map(Number); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; }
  function lum(c) { function f(v) { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); } return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); }
  function ratio(a, b) { var x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); }
  function bg(el) { var e = el; while (e) { var c = parse(getComputedStyle(e).backgroundColor); if (c && c[3] >= 1) return c; e = e.parentElement; } return [255, 255, 255, 1]; }
  var s = document.querySelector('svg.chart'); if (!s) return null; var b = bg(s.parentElement), out = {};
  [['.ch-bar:not(.neg)', 'fill', 3], ['.ch-bar.neg', 'fill', 3], ['.ch-lab', 'fill', 4.5], ['.ch-val', 'fill', 4.5]].forEach(q => { var e = s.querySelector(q[0]); if (!e) return;
    out[q[0]] = [Math.round(ratio(parse(getComputedStyle(e)[q[1]]), b) * 100) / 100, q[2]]; });
  return out; })()"""


def contrast(b, rsnap):
    for theme in ("light", "dark"):
        for vp in (Q.PHONE, Q.DESK):
            tag = f"{theme} {vp['width']}"
            ctx, page = qa.open(b, "c", vp, theme=theme, open_all=False, inline=False, sample={"answer": MD, "json": TL}, mcp={"pages": ["ok"]}, snap=rsnap, state=json.loads(json.dumps(REM)))
            tabs = "#bottom-tabs" if vp == Q.PHONE else "#rail-tabs"
            fails = []

            def scan(name, scope="[role=dialog]"):
                r = page.evaluate(Q.SCAN, scope)
                fails.extend(f"{name}: {f['el'][:44]} {f['ratio']}:1<{f['need']}" for f in r["fails"])
            panel(page, "Decisions"); scan("decision")
            page.keyboard.press("Escape")
            panel(page, "Threads"); scan("thread")
            page.locator(".sheet .composer [name=body]").fill("Hi there"); page.locator(".sheet-foot button").first.click(); page.wait_for_timeout(100); scan("confirm")
            page.keyboard.press("Escape")
            scan("today with the floating buttons", None)
            page.locator(f"{tabs} button[aria-label='Pipeline']").click(); page.wait_for_timeout(120)
            page.locator(".filter-bar button", has_text="Filters").click() if vp == Q.PHONE else None
            scan("deals table and filters", None)
            page.locator("table.deals tbody tr", has_text="Atlas Settlement").locator(".row-hit").click(); page.wait_for_timeout(250)
            page.locator(".sheet .people-list .link-btn").first.click(); page.wait_for_timeout(250); scan("founder")
            page.keyboard.press("Escape")
            page.locator(".fab .fab-mini").click(); page.wait_for_timeout(100); scan("remind sheet"); page.keyboard.press("Escape")
            page.locator(".fab .fab-main").click(); page.wait_for_timeout(100)
            page.locator(".sheet .ask-form textarea").fill("runway?"); page.keyboard.press("Enter"); page.wait_for_timeout(400); scan("ask with chart")
            ch = page.evaluate(CHART_CONTRAST)
            page.keyboard.press("Escape")
            if vp == Q.DESK:
                page.locator("#rail-tabs button[title='Your reminders']").click(); page.wait_for_timeout(100); scan("reminders tab", None)
                page.locator("#rail-tabs button[aria-label='Settings']").click(); page.wait_for_timeout(100); scan("settings", None)
            check(f"C1 {tag}: every text and mark on the new surfaces meets WCAG contrast", not fails, "; ".join(dict.fromkeys(fails)))
            bad = {k: v for k, v in (ch or {}).items() if v[0] + 1e-6 < v[1]}
            check(f"C2 {tag}: chart bars (negative too) and labels meet contrast", bool(ch) and not bad, json.dumps(bad))
            ctx.close()
    ctx, page = qa.open(b, "c-sys", Q.PHONE, scheme="dark", open_all=False, inline=False, sample={"answer": "x", "json": TL})
    dark = page.evaluate("document.documentElement.getAttribute('data-ah-theme')")
    panel(page, "Decisions")
    r = page.evaluate(Q.SCAN, "[role=dialog]")
    check("C3 a dark system scheme with no saved choice opens dark, and a panel there passes contrast", dark == "dark" and not [f for f in r["fails"] if "Written by Claude" not in f["el"]], f"{dark} {len(r['fails'])}")
    ctx.close()


# ---------------------------------------------------------------------------- layout
def hostile(snap):
    s = json.loads(json.dumps(snap, default=str))
    longw = "Supercalifragilisticexpialidociouspaymentsinfrastructurecompany" * 2
    for sec in s["brief"]["sections"]:
        for it in sec["items"][:1]:
            it["title"] = longw + ": " + it["title"]
            it["detail"] = (it.get("detail") or "") + " " + longw
    for d in list(s["pipeline"]["deals"].values())[:3]:
        if isinstance(d, dict) and "company" in d:
            d["company"] = longw
    return s


def layout(b, rsnap):
    widths = (320, 360, 380, 414, 768, 1024, 1280, 1440, 1920)
    bad, fab_bad, table_bad = [], [], []
    for w in widths:
        vp = {"width": w, "height": 800 if w < 760 else 900}
        ctx, page = qa.open(b, "l", vp, open_all=False, inline=False, sample={"answer": "x", "json": TL}, mcp={"pages": ["ok"]}, snap=rsnap)
        phone = page.locator("#bottom-tabs").is_visible()
        tabs = "#bottom-tabs" if phone else "#rail-tabs"

        def look(name):
            o = page.evaluate(OVERFLOW)
            if o["doc"] > 0 or o["sheet"] > 0 or o["cut"]:
                bad.append(f"{w} {name} {json.dumps(o)}")
        look("today")
        f = page.evaluate("""(() => { var f = document.querySelector('.fab').getBoundingClientRect(), t = document.querySelector('#bottom-tabs'), tr = t.getBoundingClientRect();
            var shown = getComputedStyle(t).display !== 'none' && tr.height > 0;
            return {over: shown && f.bottom > tr.top, out: f.left < 0 || f.right > innerWidth || f.bottom > innerHeight}; })()""")
        if f["over"] or f["out"]:
            fab_bad.append(f"{w} {json.dumps(f)}")
        panel(page, "Threads")
        look("thread panel")
        geo = page.evaluate("(() => { var s = document.querySelector('.sheet.drawer').getBoundingClientRect(), ft = document.querySelector('.sheet-foot').getBoundingClientRect(); return [Math.round(s.width), Math.round(innerHeight - s.bottom), Math.round(innerWidth - s.right), Math.round(ft.bottom - innerHeight)]; })()")
        if (phone and (geo[0] != w or geo[1] != 0)) or (not phone and (geo[0] > 560 or geo[2] != 0)) or geo[3] > 0:
            bad.append(f"{w} panel geometry {geo}")
        page.keyboard.press("Escape")
        page.locator(f"{tabs} button[aria-label='Pipeline']").click(); page.wait_for_timeout(150)
        if phone:
            page.locator(".filter-bar button", has_text="Filters").click(); page.wait_for_timeout(60)
        look("pipeline")
        t = page.evaluate("(() => { var t = document.querySelector('table.deals'), wr = t.closest('.table-wrap'), fb = document.querySelector('.filter-bar'); return [t.scrollWidth, wr.clientWidth, fb ? fb.scrollWidth - fb.clientWidth : 0]; })()")
        if t[2] > 0 or (phone and t[0] > t[1] + 1):
            table_bad.append(f"{w} {t}")
        page.locator("table.deals tbody tr", has_text="Atlas Settlement").locator(".row-hit").click(); page.wait_for_timeout(250)
        look("deal panel")
        page.locator(".sheet .people-list .link-btn").first.click(); page.wait_for_timeout(250)
        look("founder panel")
        page.keyboard.press("Escape")
        if w in (320, 1440):
            qa.shot(page, f"layout-{w}")
        ctx.close()
    check("L1 at 320 to 1920 wide: no sideways page scroll and nothing cut off in Today, panels, Pipeline, deal and founder", not bad, "; ".join(bad[:3]))
    check("L2 the floating buttons stay on screen and never cover the bottom tab bar", not fab_bad, "; ".join(fab_bad[:3]))
    check("L3 panels fit (full width from the bottom on a phone, 560 wide at the right on a laptop) and the footer is on screen", not [x for x in bad if "geometry" in x])
    check("L4 the filter bar never scrolls sideways and the deals table fits on a phone", not table_bad, "; ".join(table_bad[:3]))

    # Long unbroken names wrap.
    hs = hostile(rsnap)
    for w in (320, 1440):
        vp = {"width": w, "height": 800 if w < 760 else 900}
        ctx, page = qa.open(b, "long", vp, open_all=False, inline=False, sample={"answer": "x", "json": TL}, snap=hs)
        tabs = "#bottom-tabs" if w < 760 else "#rail-tabs"
        res = [("today", page.evaluate(OVERFLOW))]
        page.locator("#view .row-hit").first.click(); page.wait_for_timeout(250)
        res.append(("panel", page.evaluate(OVERFLOW)))
        page.keyboard.press("Escape")
        page.locator(f"{tabs} button[aria-label='Pipeline']").click(); page.wait_for_timeout(150)
        res.append(("pipeline", page.evaluate(OVERFLOW)))
        page.locator("table.deals tbody tr .row-hit").first.click(); page.wait_for_timeout(250)
        res.append(("deal", page.evaluate(OVERFLOW)))
        badl = [f"{n} {json.dumps(o)}" for n, o in res if o["doc"] > 0 or o["sheet"] > 0 or o["cut"]]
        check(f"L5 {w}: a 120-letter unbroken name wraps on Today, in its panel, in the table and in the deal panel", not badl, "; ".join(badl[:2]))
        check(f"L6 {w}: no script errors with hostile names", not errs(page), "; ".join(errs(page)[:2]))
        ctx.close()

    # A toast (Undo) and the floating buttons share the bottom edge.
    for vp in (Q.PHONE, Q.DESK):
        ctx, page = qa.open(b, "toast", vp, open_all=False)
        page.locator(".ah-hero-card button", has_text="Done").click(); page.wait_for_timeout(150)
        ov = page.evaluate("""(() => { var t = document.querySelector('.toast'), f = document.querySelector('.fab'); if (!t || !f) return 'missing';
            var a = t.getBoundingClientRect(), b = f.getBoundingClientRect(); return !(a.right <= b.left || a.left >= b.right || a.bottom <= b.top || a.top >= b.bottom) ? [Math.round(a.left), Math.round(a.right), Math.round(a.top), Math.round(b.left), Math.round(b.top)] : 'clear'; })()""")
        check(f"L7 {vp['width']}: the Undo toast does not sit on top of the floating Ask and bell", ov == "clear", str(ov))
        ctx.close()

    # A chart with a dozen bars, on the narrowest phone.
    ctx, page = qa.open(b, "chart", {"width": 320, "height": 700}, open_all=False, inline=False, sample={"answer": MD, "json": TL})
    page.locator(".fab .fab-main").click(); page.wait_for_timeout(100)
    page.locator(".sheet .ask-form textarea").fill("runway?"); page.keyboard.press("Enter"); page.wait_for_timeout(400)
    r = page.evaluate("""(() => { var s = document.querySelector('.sheet svg.chart'); if (!s) return null; var t = Array.from(s.querySelectorAll('text.ch-lab')).map(e => e.getBoundingClientRect()), ov = 0;
        for (var i = 1; i < t.length; i++) for (var j = 0; j < i; j++) { var a = t[i], c = t[j]; if (a.left < c.right - 1 && c.left < a.right - 1 && a.top < c.bottom - 1 && c.top < a.bottom - 1) ov++; }
        var vbw = s.viewBox.baseVal.width || 360;
        var e = s.querySelector('text.ch-lab'); return {overlap: ov, px: Math.round(parseFloat(getComputedStyle(e).fontSize) * s.getBoundingClientRect().width / vbw * 10) / 10}; })()""")
    check("L8 a 12-bar chart at 320 wide: labels do not overlap", bool(r) and r["overlap"] == 0, json.dumps(r))
    check("L9 a chart at 320 wide: label text renders at 11.5px or more", bool(r) and r["px"] >= 11.5, json.dumps(r))
    qa.shot(page, "chart-320")
    ctx.close()
    # Round 2: a 12-point line chart thins its labels; the ones left must sit inside the chart and apart.
    line = "x\n\n```chart\n" + json.dumps({"type": "line", "title": "T", "unit": "", "labels": LABELS, "values": [3 + i for i in range(12)]}) + "\n```"
    ctx, page = qa.open(b, "line", {"width": 414, "height": 800}, open_all=False, inline=False, sample={"answer": line, "json": TL})
    page.locator(".fab .fab-main").click(); page.wait_for_timeout(100)
    page.locator(".sheet .ask-form textarea").fill("burn?"); page.keyboard.press("Enter"); page.wait_for_timeout(400)
    r = page.evaluate("""(() => { var s = document.querySelector('.sheet svg.chart'); if (!s) return null; var sr = s.getBoundingClientRect();
        var t = Array.from(s.querySelectorAll('text.ch-lab')).map(e => e.getBoundingClientRect()), ov = 0, out = 0;
        t.forEach((a, i) => { if (a.left < sr.left - 1 || a.right > sr.right + 1) out++; if (i && a.left < t[i - 1].right - 1) ov++; });
        return {labels: t.length, outside: out, overlap: ov}; })()""")
    check("L10 a 12-point line chart with company names: thinned labels sit inside the chart and do not overlap", bool(r) and not r["outside"] and not r["overlap"], json.dumps(r))
    ctx.close()


# ---------------------------------------------------------------------------- touch targets and motion
def touch(b):
    tb = Touch(b)
    ctx, page = qa.open(tb, "touch", Q.PHONE, open_all=False, inline=False, sample={"answer": "x", "json": TL}, mcp={"pages": ["ok"]}, state=json.loads(json.dumps(REM)))
    coarse = page.evaluate("matchMedia('(pointer: coarse)').matches")
    small = lambda sel, mn=44: page.evaluate(SMALL, [sel, mn])
    s1 = small("#view .row-done, .fab button")
    s_pills = small("#view .pills .pill")
    page.locator("section[aria-label='Decisions'] .row-hit").first.tap(); page.wait_for_timeout(250)
    s_foot = small(".sheet-foot .btn")
    s_rate = small(".sheet .judge .chip-rate")
    s_chips = small(".sheet .chip, .sheet .sheet-h .btn")
    s_cite = small(".sheet .cite", 24)
    page.keyboard.press("Escape"); page.wait_for_timeout(80)
    page.locator("section[aria-label='Threads'] .row-hit").first.tap(); page.wait_for_timeout(250)
    s_chips += small(".sheet .team-chips button")
    page.keyboard.press("Escape"); page.wait_for_timeout(80)
    page.locator(".fab .fab-mini").tap(); page.wait_for_timeout(120)
    s_chips += small(".sheet .chip")
    page.keyboard.press("Escape"); page.wait_for_timeout(80)
    page.locator("#bottom-tabs button[aria-label='Settings'], #bottom-tabs button[aria-label='More']").count()
    check("T0 the touch run really matches (pointer: coarse)", coarse)
    check("T1 phone: done circles and the floating buttons are 44px or more", not s1, str(s1[:4]))
    check("T2 phone: the panel footer buttons are 44px or more", not s_foot, str(s_foot[:4]))
    check("T3 phone: Right / Not right under a summary are 44px tall on touch (the rule at line 538 says so)", not s_rate, str(s_rate[:4]))
    check("T4 phone: the day pills on Today are 44px or more", not s_pills, str(s_pills[:4]))
    check("T5 phone: chips in panels and sheets (sources, team, quick times, Ask/Remind switch, Close) are 44px or more", not s_chips, str(s_chips[:6]))
    check("T6 phone: citation numbers are at least 24px (WCAG 2.5.8; the rule at line 524 asks for 24)", not s_cite, str(s_cite[:3]))
    ctx.close()
    ctx, page = qa.open(tb, "touch-set", Q.PHONE, open_all=False)
    # Settings on a phone: from the header's last tab or Today's footer, wherever the build puts it.
    page.evaluate("document.querySelector('#rail-tabs button[aria-label=\"Settings\"]') && document.querySelector('#rail-tabs button[aria-label=\"Settings\"]').click()")
    page.wait_for_timeout(150)
    chips = small("#view .seg[aria-label$='what ant. may do'] button")
    check("T7 phone: the Settings access chips are 44px or more", page.locator("#view .seg[aria-label$='what ant. may do'] button").count() >= 6 and not chips, str(chips[:3]))
    ctx.close()

    ctx, page = qa.open(b, "motion", Q.DESK, open_all=False, inline=False, sample={"answer": "x", "json": TL})
    page.emulate_media(reduced_motion="reduce")
    page.evaluate("""(() => { window.__smooth = []; var o = Element.prototype.scrollIntoView; Element.prototype.scrollIntoView = function (a) { window.__smooth.push(a && a.behavior || 'auto'); return o.call(this, a); }; })()""")
    dur = page.evaluate("getComputedStyle(document.querySelector('.fab-main')).transitionDuration")
    check("M1 reduced motion: CSS transitions are off", dur in ("0s", "0ms"), dur)
    panel(page, "Decisions")
    page.locator(".sheet .cite").first.click(); page.wait_for_timeout(150)
    anim = page.evaluate("(() => { var li = document.getElementById('tl-0'); return getComputedStyle(li.querySelector('.tl-body')).animationName; })()")
    sm = page.evaluate("window.__smooth")
    check("M2 reduced motion: a citation jump does not flash-animate", anim == "none", anim)
    check("M3 reduced motion: a citation jump does not smooth-scroll", bool(sm) and "smooth" not in sm, str(sm))
    ctx.close()


def main() -> int:
    t0 = time.time()
    with sync_playwright() as p:
        b = p.chromium.launch()
        rsnap = demo.sample_research(json.loads(json.dumps(qa.snaps["aditi"], default=str)))
        for fn in (keyboard, names, contrast, layout, touch):
            try:
                fn(b, rsnap) if fn is not touch else fn(b)
            except Exception as e:  # a crash in one area is a failed check, not a dead run
                check(f"{fn.__name__} ran to the end", False, repr(e)[:200])
        b.close()
    ok = sum(1 for r in ROWS if r[0])
    print(f"{ok}/{len(ROWS)} checks pass ({round(time.time() - t0)}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
