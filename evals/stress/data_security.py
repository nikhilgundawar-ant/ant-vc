"""Stress: hostile and broken data reaching ant. Home (QA specialist 2, data robustness and web security).

    python3 evals/stress/data_security.py

Prints one PASS/FAIL line per check and a summary `N/M checks pass`. Exits 0 either way (a report, not a gate).
Every check passes when the app behaves correctly.
"""

from __future__ import annotations
import re

import copy
import json
import os
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import home_qa as Q  # noqa: E402
import demo  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

import tempfile  # noqa: E402
OUT = os.environ.get("STRESS_OUT") or os.path.join(tempfile.gettempdir(), "ant-stress-data")
RESULTS: list[tuple[bool, str, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((bool(ok), name, detail))
    print(("PASS " if ok else "FAIL ") + name + ("" if not detail else "  [" + str(detail)[:300] + "]"), flush=True)


def clone(x):
    return json.loads(json.dumps(x, default=str))


def errs(page) -> list[str]:
    return [e for e in page._qa_errors if "fonts.g" not in e and "ERR_FAILED" not in e and "Failed to load resource" not in e]


# --------------------------------------------------------------------------------------------- hostile strings
XSS = ' <img src=x onerror=alert(1)></script><script>alert(2)</script><svg onload=alert(3)>‮​‍עברית \U0001F680\U0001F469‍\U0001F469‍\U0001F467'
LONG = " https://docs.google.com/document/d/1AbCdEfGhIjKlMnOpQrStUvWxYz0123456789abcdefGHIJ/edit?usp=sharing"
TEXT_KEYS = {"text", "title", "name", "company", "description", "what", "detail", "headline", "statement", "subject", "body", "why", "quote",
             "reason", "next_step", "summary", "finding", "meeting_title", "context", "label", "source_label", "to_name", "kicker", "markdown",
             "who", "src", "ask", "commitment", "figure", "evidence", "warning", "board_question", "last_met_title", "hq", "lead", "partner", "market"}
LONG_KEYS = {"text", "title", "name", "company", "description", "what", "detail", "headline", "statement", "subject", "why", "next_step",
             "summary", "meeting_title", "who", "finding"}
URL_KEYS = {"url", "source_url", "empathy_map_url", "competing_source_url", "drive_url", "webViewLink"}
BAD_URLS = ["javascript:alert(1)", "data:text/html,<script>alert(1)</script>", " javascript:alert(1)", "JaVaScRiPt:alert(1)",
            "vbscript:msgbox(1)", "//evil.example/x", "java\tscript:alert(1)", "file:///etc/passwd"]


def hostile(x, n=[0]):
    if isinstance(x, dict):
        for k, v in list(x.items()):
            if isinstance(v, str):
                if k in TEXT_KEYS:
                    x[k] = v + XSS
                elif k in URL_KEYS:
                    n[0] += 1
                    x[k] = BAD_URLS[n[0] % len(BAD_URLS)]
            elif isinstance(v, list) and k == "sources":
                x[k] = [BAD_URLS[i % len(BAD_URLS)] for i in range(len(v))]
            else:
                hostile(v)
    elif isinstance(x, list):
        for v in x:
            if not isinstance(v, str):
                hostile(v)
    return x


def long_tokens(x):
    if isinstance(x, dict):
        for k, v in list(x.items()):
            if isinstance(v, str) and k in LONG_KEYS:
                x[k] = v + LONG
            else:
                long_tokens(v)
    elif isinstance(x, list):
        for v in x:
            long_tokens(v)
    return x


AUDIT = r"""() => {
  var bad = [], on = [];
  document.querySelectorAll('a[href]').forEach(function (a) { var h = a.getAttribute('href'); if (!/^https?:\/\//i.test(h)) bad.push(h.slice(0, 60)); });
  document.querySelectorAll('*').forEach(function (e) { for (var i = 0; i < e.attributes.length; i++) if (/^on/i.test(e.attributes[i].name)) on.push(e.tagName + ' ' + e.attributes[i].name); });
  return { bad: bad, on: on, scripts: document.querySelectorAll('script').length, imgs: document.querySelectorAll('#view img, .sheet img, #view svg[onload]').length,
           iframes: document.querySelectorAll('iframe, object, embed').length };
}"""

TABS = ("Today", "Pipeline", "People", "Portfolio", "LPs", "Ask")


def tab(page, name, phone=False):
    if name == "Reminders":
        page.locator("#rail-tabs button[title='Your reminders']").click()
    elif name == "Settings":
        page.locator("#rail-tabs button[aria-label='Settings']").click()
    elif name == "Activity":
        page.locator("#activity-btn").click()
    else:
        page.locator(f"{'#bottom-tabs' if phone else '#rail-tabs'} button[aria-label='{name}']").click()
    page.wait_for_timeout(120)


def close(page):
    page.keyboard.press("Escape")
    page.wait_for_timeout(60)


TL = {"tldr": [{"text": "Line one" + XSS, "cites": [1]}], "recommendation": {"text": "Do it" + XSS, "why": [{"text": "Because" + XSS, "cites": [1, 99, -1]}]},
      "subject": "Re: hi" + XSS, "body": "Hello" + XSS}


def scenario_injection(qa, b):
    base = demo.sample_research(clone(qa.snaps["aditi"]))
    snap = hostile(clone(base))
    rem = {"items": {}, "actions": {}, "reminders": {f"r{i}": {"text": "Call" + XSS, "due": "2026-10-22T06:00:00+05:30", "at": "2026-10-21T19:00:00+05:30"} for i in range(3)}}
    for vp, tagn in ((Q.DESK, "1440"), (Q.PHONE, "380")):
        phone = vp == Q.PHONE
        ctx, page = qa.open(b, "inject", vp, open_all=False, inline=False, snap=snap, state=rem, sample={"answer": "x", "json": TL}, mcp={"pages": ["ok"]})
        dialogs: list[str] = []
        page.on("dialog", lambda d: (dialogs.append(d.message), d.dismiss()))
        page.wait_for_timeout(200)
        s0 = page.evaluate(AUDIT)["scripts"]
        worst = {"bad": [], "on": [], "scripts": s0, "imgs": 0, "iframes": 0}
        panels = 0

        def merge(a):
            worst["bad"] += a["bad"]; worst["on"] += a["on"]; worst["scripts"] = max(worst["scripts"], a["scripts"])
            worst["imgs"] = max(worst["imgs"], a["imgs"]); worst["iframes"] = max(worst["iframes"], a["iframes"])

        for t in TABS + (("Reminders", "Settings", "Activity") if not phone else ()):
            tab(page, t, phone)
            merge(page.evaluate(AUDIT))
            hits = page.locator("#view .row-hit, #view .cell-hit")
            for i in range(min(hits.count(), 4 if not phone else 2)):
                try:
                    hits.nth(i).click(timeout=1500)
                    page.wait_for_timeout(150)
                    if page.locator(".sheet").count():
                        panels += 1
                    merge(page.evaluate(AUDIT))
                    close(page)
                except Exception:
                    close(page)
        if not phone:
            # A founder's panel from a deal: research map with hostile competitor urls and sources.
            tab(page, "Pipeline")
            row = page.locator("table.deals tbody tr", has_text="Atlas Settlement").locator(".row-hit")
            if row.count():
                row.first.click(); page.wait_for_timeout(200)
                merge(page.evaluate(AUDIT))
                nb = page.locator(".sheet .tl button.chip-source", has_text="Granola")
                if nb.count():
                    nb.first.click(); page.wait_for_timeout(200); panels += 1
                    merge(page.evaluate(AUDIT))
                    check("inject: a hostile meeting note opens as text", page.locator(".sheet").count() == 1 and "<img src=x" in page.locator(".sheet").inner_text(), "note panel")
                    close(page)
                    page.locator("table.deals tbody tr", has_text="Atlas Settlement").locator(".row-hit").first.click(); page.wait_for_timeout(200)
                lb = page.locator(".sheet .people-list .link-btn")
                if lb.count():
                    lb.first.click(); page.wait_for_timeout(200); panels += 1
                    merge(page.evaluate(AUDIT))
                    page.locator(".sheet-foot .pdf-btn").first.click(); page.wait_for_timeout(150)
                    links = page.evaluate("window.__pdf.links")
                    check("inject: PDF of a hostile founder panel carries only http(s) links", all(str(u).startswith(("http://", "https://")) for u in links), str(links[:4]))
                close(page)
            # A hostile draft: composer shows the subject and body as text.
            tab(page, "Today")
            thr = page.locator("section[aria-label='Threads'] .row-hit")
            if thr.count():
                thr.first.click(); page.wait_for_timeout(200)
                body = page.locator(".sheet .composer [name=body]")
                check("inject: hostile draft body is shown as plain text in the editor", body.count() == 1 and "<img src=x" in body.input_value() and not page.evaluate(AUDIT)["on"],
                      body.input_value()[:80] if body.count() else "no composer")
                close(page)
        check(f"inject {tagn}: no dialog ever opens", not dialogs, str(dialogs[:3]))
        check(f"inject {tagn}: no on* attribute anywhere in the DOM", not worst["on"], str(worst["on"][:4]))
        check(f"inject {tagn}: no script, img, iframe or object injected", worst["scripts"] == s0 and worst["imgs"] == 0 and worst["iframes"] == 0, json.dumps({k: worst[k] for k in ("scripts", "imgs", "iframes")}))
        check(f"inject {tagn}: every rendered link is http(s) (safeUrl)", not worst["bad"], str(sorted(set(worst["bad"]))[:5]))
        check(f"inject {tagn}: panels opened and no script errors", panels >= 5 and not errs(page), f"{panels} panels; " + "; ".join(errs(page)[:3]))
        ctx.close()


def scenario_long_tokens(qa, b):
    snap = long_tokens(clone(qa.snaps["aditi"]))
    ctx, page = qa.open(b, "long", Q.PHONE, open_all=False, inline=False, snap=snap, sample={"answer": "x", "json": {"tldr": [], "recommendation": None}}, mcp={"pages": ["ok"]})
    page_over, sheet_over = {}, {}
    for t in ("Today", "Pipeline", "People", "Portfolio", "LPs"):
        tab(page, t, True)
        page_over[t] = page.evaluate("document.documentElement.scrollWidth - innerWidth")
        hits = page.locator("#view .row-hit, #view .cell-hit")
        if hits.count():
            hits.first.click(); page.wait_for_timeout(200)
            sheet_over[t] = page.evaluate("(() => { var s = document.querySelector('.sheet'); return s ? s.scrollWidth - s.clientWidth : 0; })()")
            close(page)
    qa.shot(page, "long-token-380")
    check("long url in titles at 380: no horizontal page scroll on any tab", all(v <= 0 for v in page_over.values()), json.dumps(page_over))
    check("long url in titles at 380: side panels do not scroll sideways", all(v <= 0 for v in sheet_over.values()), json.dumps(sheet_over))
    hero = page.evaluate("""(() => { var s = document.querySelector('.ah-hero-card .statement'); if (!s) return 0;
      var c = s.closest('.ah-hero-card').getBoundingClientRect(); return Math.round(Math.max(s.getBoundingClientRect().right, s.getBoundingClientRect().left + s.scrollWidth) - c.right); })()""")
    check("long url in the hero statement (LPs tab) wraps inside its card", hero <= 0, f"spills {hero}px past the card")
    ctx.close()


# --------------------------------------------------------------------------------------------- Ask answers
def ask(qa, b, answer, vp=Q.DESK):
    ctx, page = qa.open(b, "ask", vp, open_all=False, sample={"answer": answer})
    dialogs: list[str] = []
    page.on("dialog", lambda d: (dialogs.append(d.message), d.dismiss()))
    tab(page, "Ask", vp == Q.PHONE)
    page.locator(".ask-form textarea").fill("question")
    page.keyboard.press("Enter")
    page.wait_for_timeout(350)
    page._dialogs = dialogs
    return ctx, page


def scenario_ask(qa, b):
    md = ("Lead line [click](javascript:alert(1)) [ok](https://example.com/a) [d](data:text/html,x) <img src=x onerror=alert(1)> [x](https://ex.com/\"onmouseover=alert(1))\n\n"
          "```chart\n{not json at all\n```\n\n"
          "```chart\nnull\n```\n\n"
          "```chart\n{\"type\": \"bar\", \"title\": \"StrLabels\", \"labels\": \"abc\", \"values\": [1, 2, 3]}\n```\n\n"
          "```chart\n{\"type\": \"bar\", \"title\": \"Huge\", \"labels\": " + json.dumps([f"L{i}" for i in range(5000)]) + ", \"values\": " + json.dumps(list(range(5000))) + "}\n```\n\n"
          "```chart\n{\"type\": \"bar\", \"title\": \"Neg\", \"unit\": \"%\", \"labels\": [\"a\", \"b\", \"c\"], \"values\": [-40, 10, -5]}\n```\n\n"
          "```chart\n{\"type\": \"bar\", \"title\": \"NaNs\", \"labels\": [\"a\", \"b\"], \"values\": [\"NaN\", 3]}\n```\n\n"
          "after the charts")
    ctx, page = ask(qa, b, md)
    bub = page.locator(".bubble.ant").last
    hrefs = page.evaluate("Array.from(document.querySelectorAll('.bubble.ant a')).map(a => a.getAttribute('href'))")
    check("ask: markdown links render only for http(s); javascript: and data: stay text", hrefs == ["https://example.com/a"] or all(h.startswith("https://") for h in hrefs) and "https://example.com/a" in hrefs, str(hrefs))
    check("ask: raw HTML in an answer stays text", page.evaluate(AUDIT)["on"] == [] and page.locator(".bubble.ant img").count() == 0 and "<img" in bub.inner_text())
    check("ask: a chart with bad JSON or null is left out and the rest renders", "after the charts" in bub.inner_text())
    check("ask: a chart with string labels does not draw or crash", page.locator(".bubble.ant figcaption", has_text="StrLabels").count() == 0)
    huge = page.locator(".bubble.ant figure", has_text="Huge")
    check("ask: a 5000-point chart draws at most 16 bars and says it cut", huge.count() == 1 and huge.locator("rect.ch-bar").count() <= 16 and "of 5000" in huge.inner_text(), str(huge.locator("rect.ch-bar").count() if huge.count() else 0))
    neg = page.locator(".bubble.ant figure", has_text="Neg")
    ys = page.evaluate("Array.from(document.querySelectorAll('.bubble.ant figure')).filter(f => f.textContent.indexOf('Neg') >= 0).flatMap(f => Array.from(f.querySelectorAll('text.ch-val')).map(t => Number(t.getAttribute('y'))))")
    check("ask: negative values draw as negative bars with labels inside the chart", neg.count() == 1 and neg.locator("rect.ch-bar.neg").count() == 2 and all(0 <= y <= 210 for y in ys), str(ys))
    check("ask: a chart with NaN values is left out", page.locator(".bubble.ant figcaption", has_text="NaNs").count() == 0)
    check("ask: no dialog and no script errors with hostile markdown", not page._dialogs and not errs(page), "; ".join(errs(page)[:3]))
    ctx.close()

    md2 = ("Extremes\n\n```chart\n{\"type\": \"line\", \"title\": \"Extreme\", \"labels\": [\"a\", \"b\"], \"values\": [1e308, -1e308]}\n```\n\n"
           "```chart\n{\"type\": \"bar\", \"title\": \"Short\", \"labels\": [\"a\", \"b\", \"c\"], \"values\": [5]}\n```\n")
    ctx, page = ask(qa, b, md2)
    bad_attr = page.evaluate("Array.from(document.querySelectorAll('.bubble.ant svg *')).filter(e => Array.from(e.attributes).some(a => /NaN|Infinity/.test(a.value))).length")
    check("ask: extreme values (1e308, -1e308) draw no NaN or Infinity coordinates", bad_attr == 0 and not errs(page), f"{bad_attr} elements; " + "; ".join(errs(page)[:2]))
    lab = page.evaluate("(() => { var f = Array.from(document.querySelectorAll('.bubble.ant figure')).find(f => f.textContent.indexOf('Short') >= 0); return f ? f.querySelector('svg').getAttribute('aria-label') + ' | ' + f.textContent : null; })()")
    check("ask: fewer values than labels never shows NaN", lab is not None and "NaN" not in lab, str(lab))
    ctx.close()

    wide = "| " + " | ".join(f"Column{i}" for i in range(30)) + " |\n|" + "---|" * 30 + "\n| " + " | ".join("x" * 40 for _ in range(30)) + " |\n"
    ctx, page = ask(qa, b, "A table\n\n" + wide + "\n" + "N" * 400, Q.PHONE)
    over = page.evaluate("document.documentElement.scrollWidth - innerWidth")
    check("ask 380: a 30-column table and a 400-char word cause no page scroll", over <= 0 and page.locator(".bubble.ant table.answer-table").count() == 1, f"{over}px")
    ctx.close()


# --------------------------------------------------------------------------------------------- missing data
def strip_fields(snap):
    for sec in (snap.get("brief") or {}).get("sections") or []:
        for i, it in enumerate(sec.get("items") or []):
            for k in ("source", "entity", "detail", "deal_id"):
                it.pop(k, None)
            it["due"] = ["not a date", None, "2026-13-45", "", 12345][i % 5]
            if i % 3 == 0:
                it.pop("actions", None)
    for d in ((snap.get("pipeline") or {}).get("deals") or {}).values():
        for k in ("source_url", "domain", "last_contact", "stage_entered", "owner", "partner", "round"):
            d.pop(k, None)
        d["last_contact_days"] = None
    for i, (k, d) in enumerate(list(((snap.get("pipeline") or {}).get("deals") or {}).items())[:3]):
        d.pop("company", None); d.pop("stage", None); d["stage_key"] = "made_up_stage"
    for p in (snap.get("people") or {}).get("top") or []:
        p.pop("source_url", None); p["last_touch"] = "yesterday-ish"; p["days_since"] = None
    for i in range(4):
        for evs in ((snap.get(f"timeline_{i}") or {}).get("items") or {}).values():
            for j, e in enumerate(evs):
                if j % 4 == 0: e["at"] = "garbage"
                elif j % 4 == 1: e["at"] = None
                elif j % 4 == 2: e.pop("src", None); e.pop("url", None)
    for n in ((snap.get("notes") or {}).get("items") or {}).values():
        n["lines"] = None; n["date"] = "nope"; n.pop("url", None)
    for d in ((snap.get("drafts") or {}).get("items") or {}).values():
        d.pop("to", None); d.pop("subject", None); d["made_at"] = "bad"
    return snap


BAD_TEXT = ("undefined", "NaN", "Invalid Date", "[object Object]")


def visit_all(qa, b, name, snap, state=None, open_panels=True):
    ctx, page = qa.open(b, name, Q.DESK, open_all=False, inline=False, snap=snap, state=state or {"items": {}, "actions": {}, "reminders": {}},
                        sample={"answer": "x", "json": {"tldr": [], "recommendation": None}}, mcp={"pages": ["ok"]})
    page.wait_for_timeout(150)
    rendered, opened, junk = {}, 0, set()
    for t in TABS[:-1] + ("Reminders", "Settings", "Activity"):
        try:
            tab(page, t)
        except Exception as e:
            rendered[t] = "no tab: " + str(e)[:40]
            continue
        txt = page.locator("#view").inner_text()
        rendered[t] = len(txt.strip())
        for w in BAD_TEXT:
            if w in txt:
                junk.add(f"{t}:{w}")
        if open_panels:
            hits = page.locator("#view .row-hit, #view .cell-hit")
            for i in range(min(hits.count(), 2)):
                try:
                    hits.nth(i).click(timeout=1500); page.wait_for_timeout(120)
                    if page.locator(".sheet").count():
                        opened += 1
                        st = page.locator(".sheet").inner_text()
                        for w in BAD_TEXT:
                            if w in st:
                                junk.add(f"{t} panel:{w}")
                    close(page)
                except Exception:
                    close(page)
    e = errs(page)
    ctx.close()
    return rendered, opened, junk, e


def scenario_missing(qa, b):
    full = clone(qa.snaps["aditi"])
    cases = []
    s = clone(full); [s.pop(f"timeline_{i}", None) for i in range(4)]; cases.append(("no timeline docs", s))
    s = clone(full); s["config"].pop("firm_members", None); s.pop("directory", None); cases.append(("no firm_members, no directory", s))
    s = clone(full); [s.pop(k, None) for k in ("notes", "pipeline", "people", "portfolio", "lps", "drafts", "commitments", "inbound", "prep", "digests", "asks", "proposals")]
    cases.append(("no notes, pipeline, people, portfolio, lps, drafts", s))
    s = clone(full); cases.append(("missing fields, null and bad dates", strip_fields(s)))
    s = {"config": clone(full["config"]), "brief": {"as_of": full["brief"]["as_of"], "sections": [{"key": "top", "label": "Next up", "items": []}]},
         "pipeline": {"as_of": full["brief"]["as_of"], "deals": {}, "stages": [], "scope": "own"}, "people": {"top": []}, "portfolio": {"companies": {}}, "lps": {"lps": {}}}
    cases.append(("member with zero rows", s))
    s = {"config": {}, "brief": {}}
    cases.append(("bare config and brief", s))
    bad_rem = {"items": {}, "actions": {}, "reminders": {"rb1": {"text": "Bad due", "due": "next tuesday", "at": "2026-10-21T19:00:00Z"},
                                                        "rb2": {"text": "Null due", "due": None, "at": None}, "rb3": {"due": "2026-10-22T09:00:00Z"}}}
    rendered, opened, junk, e = visit_all(qa, b, "missing-rem", clone(full), state=bad_rem, open_panels=False)
    check("missing [reminder with a bad due date]: page renders and no script errors", not e and all(isinstance(n, int) and n > 0 for n in rendered.values()), "; ".join(e[:2]) + " " + json.dumps(rendered))
    for label, snap in cases:
        rendered, opened, junk, e = visit_all(qa, b, "missing", snap)
        dead = [t for t, n in rendered.items() if not isinstance(n, int) or n == 0]
        check(f"missing [{label}]: every tab renders something", not dead, json.dumps(rendered))
        check(f"missing [{label}]: no script errors", not e, "; ".join(e[:3]))
        check(f"missing [{label}]: no undefined/NaN/Invalid Date/[object Object] on screen", not junk, str(sorted(junk)[:6]))
        if label in ("no timeline docs", "missing fields, null and bad dates", "no firm_members, no directory"):
            check(f"missing [{label}]: panels still open", opened >= 4, f"{opened} opened")


# --------------------------------------------------------------------------------------------- scale
def scale_snap(full):
    s = clone(full)
    deals = s["pipeline"]["deals"]
    stages = [st["key"] for st in s["pipeline"]["stages"]]
    names = {st["key"]: st["name"] for st in s["pipeline"]["stages"]}
    tmpl = next(iter(deals.values()))
    for i in range(300 - len(deals)):
        d = clone(tmpl)
        k = stages[i % len(stages)]
        d.update({"company": f"Scale Co {i:03d}", "company_id": f"c_scale{i}", "domain": f"scale{i}.example", "stage_key": k, "stage": names[k],
                  "days_in_stage": i % 40, "raise_usd": 1_000_000 + i * 10_000, "owner": s["config"]["user_email"], "active": True})
        deals[f"d_scale{i}"] = d
    s["pipeline"]["scope"] = "all"
    evs = [{"id": f"big{i}", "at": f"2026-{(i % 9) + 1:02d}-{(i % 27) + 1:02d}T{i % 24:02d}:00:00+05:30", "src": "Gmail", "url": f"https://mail.google.com/mail/u/0/#all/x{i}",
            "kind": "email", "text": f"Event {i}"} for i in range(400)]
    s["timeline_1"]["items"]["c:c_atlas"] = evs
    notes = s["notes"]["items"]
    nt = next(iter(notes.values()))
    for i in range(100):
        n = clone(nt); n["id"] = f"nscale{i}"; n["title"] = f"Scale note {i}"; notes[n["id"]] = n
    drafts = s["drafts"]["items"]
    dt_ = next(iter(drafts.values()))
    for i in range(50):
        d = clone(dt_); d["subject"] = f"Scale draft {i}"; d.pop("commitment_id", None); drafts[f"dr_scale{i}"] = d
    return s


def scenario_scale(qa, b):
    snap = scale_snap(qa.snaps["aditi"])
    rem = {"items": {}, "actions": {}, "reminders": {f"rs{i}": {"text": f"Reminder {i}", "due": f"2026-10-{20 + i % 8:02d}T{8 + i % 10:02d}:00:00.000Z", "at": "2026-10-20T00:00:00.000Z"} for i in range(60)}}
    t0 = time.time()
    ctx, page = qa.open(b, "scale", Q.DESK, open_all=False, inline=False, snap=snap, state=rem, sample={"answer": "x", "json": {"tldr": [], "recommendation": None}}, mcp={"pages": ["ok"]})
    page.wait_for_selector("#view section", timeout=10000)
    load = time.time() - t0
    T = r"""(sel) => { var b = document.querySelector(sel); var t = performance.now(); b.click(); var x = document.querySelector('#view').offsetHeight; return performance.now() - t; }"""
    page.evaluate(T, "#rail-tabs button[aria-label='Pipeline']")
    tp = page.evaluate(T, "#rail-tabs button[aria-label='Pipeline']")
    tt = page.evaluate(T, "#rail-tabs button[aria-label='Today']")
    check("scale: Today renders under 1.5 s (300 deals, 50 drafts, 60 reminders, 100 notes)", tt < 1500, f"{tt:.0f} ms (page load {load:.1f}s)")
    tab(page, "Pipeline")
    for _ in range(12):
        f = page.locator(".stage-h button[aria-expanded=false]")
        if not f.count():
            break
        f.first.click()
    tp2 = page.evaluate(T, "#rail-tabs button[aria-label='Pipeline']")
    check("scale: Pipeline renders under 1.5 s with 300 deals", max(tp, tp2) < 1500, f"{tp:.0f} ms, unfolded {tp2:.0f} ms")
    for _ in range(12):
        f = page.locator(".stage-h button[aria-expanded=false]")
        if not f.count():
            break
        f.first.click()
    rows = page.locator(".deal-row").count()
    check("scale: all 300 deals are listed", rows == 300, f"{rows} rows")
    inp = page.locator("table.deals .filter-row input").first
    if inp.count():
        inp.fill("Scale Co 01")
        page.wait_for_timeout(250)
        got = page.locator(".deal-row").all_inner_texts()
        check("scale: a column filter narrows 300 deals to the matching ones", 0 < len(got) <= 12 and all("Scale Co 01" in g for g in got), f"{len(got)} rows")
        inp.fill("")
        page.wait_for_timeout(200)
    else:
        check("scale: a column filter narrows 300 deals to the matching ones", False, "no text filter input")
    sort = page.locator("table.deals th button.th-sort").first
    t = time.time(); sort.click(); page.wait_for_timeout(50); ts = time.time() - t
    first = page.locator(".deal-row").first.inner_text()
    sort.click(); page.wait_for_timeout(50)
    first2 = page.locator(".deal-row").first.inner_text()
    check("scale: sorting 300 deals works both ways and stays fast", first != first2 and ts < 1.5, f"{ts:.2f}s; {first[:30]!r} vs {first2[:30]!r}")
    row = page.locator("table.deals tbody tr", has_text="Atlas Settlement").locator(".row-hit")
    t = time.time(); row.first.click(); page.wait_for_selector(".sheet .tl", timeout=5000); tpanel = time.time() - t
    n_ev = page.locator(".sheet .tl .tl-ev").count()
    more = page.locator(".sheet .tl-more")
    check("scale: a panel with 400 timeline events opens under 1.5 s", tpanel < 1.5, f"{tpanel:.2f}s")
    check("scale: a 400-event timeline tells the user how many there are (not a silent cap of 24)",
          any(ch.isdigit() for ch in (more.inner_text() if more.count() else "")) and bool(re.search(r"of (\d+)", more.inner_text() if more.count() else "")) and int(re.search(r"of (\d+)", more.inner_text()).group(1)) >= 400,
          f"{n_ev} events in DOM; more button: {more.inner_text() if more.count() else 'none'}")
    close(page)
    tab(page, "Reminders")
    nrem = page.locator("#view .row").count()
    check("scale: 60 reminders all reachable on Reminders", nrem >= 60, f"{nrem} rows")
    check("scale: no script errors", not errs(page), "; ".join(errs(page)[:3]))
    ctx.close()


# --------------------------------------------------------------------------------------------- timeline order
def scenario_order(qa, b):
    s = clone(qa.snaps["aditi"])
    evs = [
        {"id": "o_e1", "at": "2026-10-22T06:30:00+05:30", "src": "Gmail", "url": "https://mail.google.com/x1", "kind": "email", "text": "ORDER-B 06:30 IST"},
        {"id": "o_e2", "at": "2026-10-22T01:20:00Z", "src": "Gmail", "url": "https://mail.google.com/x2", "kind": "email", "text": "ORDER-A 06:50 IST written in UTC"},
        {"id": "o_e4", "at": "2026-10-21T12:15:00-07:00", "src": "Gmail", "url": "https://mail.google.com/x4", "kind": "email", "text": "ORDER-C 00:45 IST written in PDT"},
    ]
    s["timeline_1"]["items"]["c:c_atlas"] = evs + (s["timeline_1"]["items"].get("c:c_atlas") or [])
    dup = {"id": "o_dup", "at": "2026-10-22T05:00:00+05:30", "src": "Gmail", "url": "https://mail.google.com/d", "kind": "email", "text": "DUP-EVENT"}
    for i in (0, 2, 3):
        s[f"timeline_{i}"]["items"].setdefault("c:c_atlas", []).append(dict(dup))
    ctx, page = qa.open(b, "order", Q.DESK, open_all=False, inline=False, snap=s, sample={"answer": "x", "json": {"tldr": [], "recommendation": None}}, mcp={"pages": ["ok"]})
    tab(page, "Pipeline")
    page.locator("table.deals tbody tr", has_text="Atlas Settlement").locator(".row-hit").first.click()
    page.wait_for_selector(".sheet .tl", timeout=5000)
    texts = page.evaluate("Array.from(document.querySelectorAll('.sheet .tl .tl-text')).map(t => t.textContent)")
    pos = {k: next((i for i, t in enumerate(texts) if t.startswith(k)), -1) for k in ("ORDER-A", "ORDER-B", "ORDER-C")}
    check("order: timeline sorts by instant across time zones (UTC 06:50 IST before +05:30 06:30)", 0 <= pos["ORDER-A"] < pos["ORDER-B"] < pos["ORDER-C"], json.dumps(pos) + " " + str(texts[:4]))
    check("order: the same event id in three shards shows once", sum(1 for t in texts if t == "DUP-EVENT") == 1, str(sum(1 for t in texts if t == "DUP-EVENT")))
    ctx.close()

    # A date-only stamp for a user west of UTC keeps its calendar day.
    s = clone(qa.snaps["aditi"])
    s["config"]["tz"] = "America/Los_Angeles"
    s["timeline_1"]["items"]["c:c_atlas"] = [{"id": "o_day", "at": "2026-10-23", "src": "Affinity", "url": "https://x.affinity.co/1", "kind": "crm", "text": "DATE-ONLY 23 Oct"}] + (s["timeline_1"]["items"].get("c:c_atlas") or [])
    ctx, page = qa.open(b, "order-tz", Q.DESK, open_all=False, inline=False, snap=s, sample={"answer": "x", "json": {"tldr": [], "recommendation": None}}, mcp={"pages": ["ok"]})
    tab(page, "Pipeline")
    page.locator("table.deals tbody tr", has_text="Atlas Settlement").locator(".row-hit").first.click()
    page.wait_for_selector(".sheet .tl", timeout=5000)
    when = page.evaluate("(() => { var li = Array.from(document.querySelectorAll('.sheet .tl .tl-ev')).find(l => l.textContent.indexOf('DATE-ONLY') >= 0); return li ? li.querySelector('time').textContent : null; })()")
    check("order: a date-only event shows its own day for a user in Los Angeles (23 Oct, not 22 Oct)", bool(when) and when.startswith("23 "), str(when))
    ctx.close()



# --------------------------------------------------------------------------------------------- round 2: the new paths
def scenario_round2(qa, b):
    code = "Here is the raw text\n\n```\n<img src=x onerror=alert(1)></script>\n" + "Z" * 400 + "\n```\n\nAfter code"
    ctx, page = ask(qa, b, code, Q.PHONE)
    pre = page.locator(".bubble.ant pre.answer-code")
    over = page.evaluate("document.documentElement.scrollWidth - innerWidth")
    bub = page.evaluate("(() => { var b = document.querySelector('.bubble.ant:last-of-type') || document.querySelector('.bubble.ant'); return b ? Math.round(b.getBoundingClientRect().right - innerWidth) : 0; })()")
    check("r2 ask 380: a fenced block shows hostile HTML as text, scrolls inside itself, no page scroll", pre.count() == 1 and "<img src=x" in pre.inner_text() and not page.evaluate(AUDIT)["on"]
          and page.locator(".bubble.ant img").count() == 0 and over <= 0 and bub <= 0, f"pre={pre.count()} page over {over}px, bubble past edge {bub}px")
    ctx.close()

    t = "Revenue" + "R" * 120 + XSS
    md = ("Charts\n\n```chart\n" + json.dumps({"type": "bar", "title": t, "labels": [f"Label{i}" + XSS for i in range(40)], "values": list(range(40))}) + "\n```\n\n"
          "```chart\n" + json.dumps({"type": "line", "title": "Gaps", "labels": ["a", "b", "c", "d"], "values": [1, None, 3, None]}) + "\n```\n\n"
          "```chart\n" + json.dumps({"type": "bar", "title": "Strs", "labels": ["a", "b"], "values": ["8", 3]}) + "\n```\n")
    ctx, page = ask(qa, b, md, Q.PHONE)
    cap = page.locator(".bubble.ant figcaption").first.inner_text() if page.locator(".bubble.ant figcaption").count() else ""
    over = page.evaluate("document.documentElement.scrollWidth - innerWidth")
    capover = page.evaluate("(() => { var f = document.querySelector('.bubble.ant figcaption'); return f ? Math.round(f.getBoundingClientRect().left + f.scrollWidth - f.closest('.bubble').getBoundingClientRect().right) : 0; })()")
    check("r2 ask 380: a long hostile chart title with (first 16 of 40) stays text and inside the bubble", "(first 16 of 40)" in (cap + page.evaluate("Array.from(document.querySelectorAll('.bubble.ant svg')).map(s=>s.getAttribute('aria-label')).join(' ')"))
          and not page.evaluate(AUDIT)["on"] and over <= 0 and capover <= 0, f"caption ends {cap[-30:]!r}; page over {over}px; caption past bubble {capover}px")
    bad_attr = page.evaluate("Array.from(document.querySelectorAll('.bubble.ant svg *')).filter(e => Array.from(e.attributes).some(a => /NaN|Infinity|undefined/.test(a.value))).length")
    gaps = page.locator(".bubble.ant figure", has_text="Gaps")
    check("r2 ask: a line chart with null gaps draws only real points, no NaN", gaps.count() == 1 and gaps.locator("circle.ch-dot").count() == 2 and bad_attr == 0 and not errs(page), f"{bad_attr} bad attrs; " + "; ".join(errs(page)[:2]))
    check("r2 ask: a chart with string values is left out", page.locator(".bubble.ant figcaption", has_text="Strs").count() == 0)
    ctx.close()

    # The send confirm: what is not an address is named back, as text.
    for vp, tagn in ((Q.PHONE, "380"), (Q.DESK, "1440")):
        ctx, page = qa.open(b, "r2-send", vp, open_all=False, inline=False, sample={"answer": "x", "json": {"tldr": [], "recommendation": None}}, mcp={"pages": ["ok"]})
        page.locator("section[aria-label='Threads'] .row-hit").first.click(); page.wait_for_timeout(250)
        had_note = page.locator(".sheet .watch-note").count()
        to = page.locator(".sheet .composer [name=to]")
        to.fill('Ishaan "<b>x</b>" <ishaan@atlassettle.com>, <img src=x onerror=alert(1)>' + "Q" * 120 + ", notanaddress")
        foot = page.locator(".sheet-foot button").first
        foot.click(); page.wait_for_timeout(120)
        conf = page.locator(".sheet .send-confirm")
        ctext = conf.inner_text() if conf.count() else ""
        sheet_over = page.evaluate("(() => { var s = document.querySelector('.sheet'); return s ? s.scrollWidth - s.clientWidth : 0; })()")
        check(f"r2 send {tagn}: the confirm sends only to the real address and names what was left out, as text",
              "Send to ishaan@atlassettle.com" in ctext and "Left out, not an address" in ctext and not page.evaluate(AUDIT)["on"] and page.locator(".sheet img").count() == 0,
              ctext[:200])
        check(f"r2 send {tagn}: a long left-out token does not make the panel scroll sideways", sheet_over <= 0, f"{sheet_over}px")
        page.locator(".sheet .send-confirm button", has_text="Not yet").click(); page.wait_for_timeout(60)
        foot.click(); page.wait_for_timeout(120)
        ctext2 = page.locator(".sheet .send-confirm").inner_text()
        check(f"r2 send {tagn}: a second Send does not claim the summary looked off (the panel had no warning)",
              had_note > 0 or "summary looked off" not in ctext2, ctext2[:160])
        sent = [m for m in page.evaluate("window.__mcp") if m["tool"] == "send_message"]
        check(f"r2 send {tagn}: nothing sent before Send now", not sent, json.dumps(sent)[:120])
        ctx.close()

    # Outlook-style "Last, First <email>" is one person, not a stray word.
    ctx, page = qa.open(b, "r2-outlook", Q.DESK, open_all=False, inline=False, sample={"answer": "x", "json": {"tldr": [], "recommendation": None}}, mcp={"pages": ["ok"]})
    page.locator("section[aria-label='Threads'] .row-hit").first.click(); page.wait_for_timeout(250)
    page.locator(".sheet .composer [name=to]").fill("Verma, Ishaan <ishaan@atlassettle.com>")
    page.locator(".sheet-foot button").first.click(); page.wait_for_timeout(120)
    ctext = page.locator(".sheet .send-confirm").inner_text()
    check("r2 send: 'Verma, Ishaan <ishaan@x.com>' is not reported as a left-out address 'Verma'", "Left out" not in ctext, ctext[:160])
    ctx.close()

    # A bare date from an earlier year keeps its year, like a timestamp from an earlier year does.
    s = clone(qa.snaps["aditi"])
    s["timeline_1"]["items"]["c:c_atlas"] = [{"id": "r2_old", "at": "2025-03-05", "src": "Affinity", "url": "https://x.affinity.co/2", "kind": "crm", "text": "OLD-DAY"},
                                             {"id": "r2_old_t", "at": "2025-03-06T10:00:00+05:30", "src": "Affinity", "url": "https://x.affinity.co/3", "kind": "crm", "text": "OLD-TIME"}] + (s["timeline_1"]["items"].get("c:c_atlas") or [])
    ctx, page = qa.open(b, "r2-year", Q.DESK, open_all=False, inline=False, snap=s, sample={"answer": "x", "json": {"tldr": [], "recommendation": None}}, mcp={"pages": ["ok"]})
    tab(page, "Pipeline")
    page.locator("table.deals tbody tr", has_text="Atlas Settlement").locator(".row-hit").first.click()
    page.wait_for_selector(".sheet .tl", timeout=5000)
    page.evaluate("document.querySelectorAll('.sheet .tl .tl-ev').forEach(li => li.hidden = false)")
    w = page.evaluate("Object.fromEntries(Array.from(document.querySelectorAll('.sheet .tl .tl-ev')).filter(l => /OLD-/.test(l.textContent)).map(l => [l.querySelector('.tl-text').textContent, l.querySelector('time').textContent]))")
    check("r2 order: a bare date from 2025 shows its year, as a 2025 timestamp does", "2025" in str(w.get("OLD-DAY")) and "2025" in str(w.get("OLD-TIME")), json.dumps(w))
    ctx.close()


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    qa = Q.QA(OUT)
    t0 = time.time()
    with sync_playwright() as p:
        b = p.chromium.launch()
        for fn in (scenario_injection, scenario_long_tokens, scenario_ask, scenario_missing, scenario_scale, scenario_order, scenario_round2):
            try:
                fn(qa, b)
            except Exception as e:  # a crash in one scenario is a failed check, not a dead run
                check(f"{fn.__name__}: ran to the end", False, repr(e)[:300])
        b.close()
    ok = sum(1 for r in RESULTS if r[0])
    print(f"{ok}/{len(RESULTS)} checks pass ({time.time() - t0:.0f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
