"""Stress: side panels and the draft composer (QA specialist 1).

    python3 evals/stress/panels_send.py

Every check PASSES when Home behaves correctly, so a FAIL line is a live bug. Prints one PASS/FAIL line per check and
a summary line "N/M checks pass". Exits 0 either way (the summary is the result).
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.parse as U

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "evals"))
import home_qa as Q  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

OUT = os.environ.get("STRESS_OUT", "/tmp/claude-0/-home-claude/f41ebfd9-0635-5201-96ea-278169523f82/scratchpad/stress-panels")
RESULTS: list[tuple[bool, str, str]] = []

# A summary that names the intro's people, so Send stays plain Send (the off-topic path is tested on its own).
TL_ON = {"tldr": [{"text": "Arjun Khurana and Raj Malhotra intro for Gravity Payouts and Atlas Settlement", "cites": [1]}],
         "recommendation": {"text": "Approve the Gravity Payouts step", "why": []}, "subject": "Claude subject", "body": "Hi there. A body Claude wrote. Aditi"}
# Round 21's summary: it cites real events but names none of the intro's people, so Send is held back as Send anyway.
TL_OFF = {"tldr": [{"text": "Gravity Payouts set reference calls with three gig platforms.", "cites": [1]}, {"text": "Bluepeak is moving on terms.", "cites": [2]}],
          "recommendation": None, "subject": "S", "body": "B"}
SENDS = "window.__mcp.filter(m => m.tool === 'send_message')"
# Gmail that takes a while (or fails after a while): the in-flight window a real send has.
SLOW = """([ms, fail]) => window.claude.use('mcp').then(m => { const o = m.callTool; m.callTool = function (s, t, i) {
  if (t !== 'send_message') return o(s, t, i); window.__mcp.push({server: s, tool: t, input: i});
  return new Promise((res, rej) => setTimeout(() => fail ? rej({code: 'tool_error', message: 'quota'}) : res({content: [], payload: {id: 'm1'}}), ms)); }; })"""


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((bool(ok), name, detail))
    print(("PASS " if ok else "FAIL ") + name + ("" if ok or not detail else "  [" + detail[:220] + "]"), flush=True)


def errs(page) -> list[str]:
    return [e for e in page._qa_errors if "fonts.g" not in e and "ERR_FAILED" not in e]


def tab(page, name: str) -> bool:
    loc = page.locator(f"#rail-tabs [aria-label='{name}']:visible, #bottom-tabs [aria-label='{name}']:visible")
    if not loc.count():
        return False
    loc.first.click()
    page.wait_for_timeout(60)
    return True


def expand(page) -> None:
    for _ in range(6):
        f = page.locator("#view .fold-btn[aria-expanded='false']:visible")
        if not f.count():
            return
        f.first.click()
        page.wait_for_timeout(30)


def thread(qa, b, vp=Q.DESK, tl=TL_ON, **kw):
    """Aditi's first Threads row: the saved intro draft to Arjun and Raj."""
    mcp = kw.pop("mcp", {"pages": ["ok"]})
    ctx, page = qa.open(b, "t", vp, open_all=False, inline=False, sample={"answer": "x", "json": tl}, mcp=mcp, **kw)
    page.locator("section[aria-label='Threads'] .row-hit").first.click()
    page.wait_for_timeout(180)
    return ctx, page


def foot(page):
    return page.locator(".sheet-foot button").first


def ask_send(page) -> bool:
    if foot(page).is_disabled():  # a disabled Send is the guard working: nothing to tap
        return False
    foot(page).click()
    page.wait_for_timeout(50)
    return page.locator(".sheet .send-confirm").is_visible()


def send_now(page, wait=250) -> None:
    page.locator(".sheet .send-confirm button", has_text="Send now").click()
    page.wait_for_timeout(wait)


def writes(page, path=None, coll=None) -> list:
    return [w for w in page.evaluate("window.__writes") if (path and w.get("path") == path) or (coll and w.get("collection") == coll)]


# ---------------------------------------------------------------------------------------------- every panel, every place
def sweep(qa, b) -> None:
    plan = [(m, Q.DESK, 99) for m in ("aditi", "kabir", "rohan", "tara", "vikram", "solo")] + [(m, Q.PHONE, 3) for m in ("aditi", "kabir", "rohan", "tara", "vikram", "solo")]
    for member, vp, cap in plan:
        ctx, page = qa.open(b, "sweep", vp, member=member, open_all=False, inline=False, sample={"answer": "x", "json": TL_OFF}, mcp={"pages": ["ok"]})
        bad, opened = [], 0
        for t in ("Today", "Pipeline", "People", "Portfolio", "LPs"):
            if not tab(page, t):
                continue
            expand(page)
            n = min(page.locator("#view button.row-hit:visible").count(), cap)
            for i in range(n):
                tab(page, t)
                expand(page)
                hits = page.locator("#view button.row-hit:visible")
                if i >= hits.count():
                    break
                label = hits.nth(i).inner_text()[:36].replace("\n", " ")
                hits.nth(i).click()
                page.wait_for_timeout(90)
                sh = page.locator(".sheet")
                if not sh.count():
                    bad.append(f"{t}/{label}: no panel")
                    continue
                opened += 1
                txt = sh.first.inner_text()
                parts = ("TL;DR" in txt, sh.locator(".tl").count() > 0 or "No history yet" in txt, sh.locator(".sheet-foot .pdf-btn").count() == 1)
                if not all(parts):
                    bad.append(f"{t}/{label}: tldr,timeline,pdf={parts}")
                page.keyboard.press("Escape")
                page.wait_for_timeout(40)
                if page.locator(".sheet").count():
                    bad.append(f"{t}/{label}: Escape left it open")
                if "row-hit" not in (page.evaluate("document.activeElement && document.activeElement.className") or ""):
                    bad.append(f"{t}/{label}: focus not back on the row")
        e = errs(page)
        check(f"sweep {member} {vp['width']}px: {opened} panels open with TL;DR, timeline, PDF; Escape closes; focus returns; no errors",
              opened > 0 and not bad and not e, "; ".join(bad[:3] + e[:2]))
        ctx.close()


# ---------------------------------------------------------------------------------------------- navigation between panels
def navigation(qa, b) -> None:
    import demo
    rsnap = demo.sample_research(json.loads(json.dumps(qa.snaps["aditi"], default=str)))
    for vp in (Q.DESK, Q.PHONE):
        w = vp["width"]
        ctx, page = qa.open(b, "nav", vp, open_all=False, inline=False, sample={"answer": "x", "json": TL_OFF}, snap=rsnap)
        tab(page, "Pipeline")
        row = page.locator("table.deals tbody tr", has_text="Atlas Settlement").locator(".row-hit")
        row.click()
        page.wait_for_timeout(150)
        page.locator(".sheet .people-list .link-btn").first.click()
        page.wait_for_timeout(150)
        is_founder = page.locator(".sheet").get_attribute("aria-label") != "Atlas Settlement"
        page.locator(".sheet-h button", has_text="Back").click()
        page.wait_for_timeout(120)
        check(f"nav {w}px: deal -> founder -> Back returns to the deal", is_founder and page.locator(".sheet").get_attribute("aria-label") == "Atlas Settlement")
        page.locator(".sheet-h button[aria-label=Close]").click()
        page.wait_for_timeout(60)
        check(f"nav {w}px: the X closes and focus returns to the deal row", page.locator(".sheet").count() == 0 and
              "Atlas" in (page.evaluate("document.activeElement.textContent") or ""))
        row.click()
        page.wait_for_timeout(120)
        page.mouse.click(4, 4)
        page.wait_for_timeout(60)
        check(f"nav {w}px: a tap on the scrim closes the panel", page.locator(".sheet").count() == 0)
        # The note chip in a timeline opens the notes with Back.
        tab(page, "Today")
        page.locator("section[aria-label='Decisions'] .row-hit").first.click()
        page.wait_for_timeout(150)
        if page.locator(".sheet .tl-more").count():
            page.locator(".sheet .tl-more").click()
        chip = page.locator(".sheet .tl button.chip-source[aria-label^='Open meeting notes']:visible")
        had = chip.count() > 0
        if had:
            first = page.locator(".sheet").get_attribute("aria-label")
            chip.first.click()
            page.wait_for_timeout(150)
            page.locator(".sheet-h button", has_text="Back").click()
            page.wait_for_timeout(120)
            had = page.locator(".sheet").get_attribute("aria-label") == first
        check(f"nav {w}px: a notes chip in a timeline opens the notes, and Back returns", had)
        page.keyboard.press("Escape")
        check(f"nav {w}px: no script errors", not errs(page), "; ".join(errs(page)[:2]))
        ctx.close()

    # Prep card attendees open the person, Back returns to the prep.
    ctx, page = qa.open(b, "prep", Q.PHONE, open_all=False, inline=False, sample={"answer": "- a", "json": TL_OFF})
    page.locator("#view button.link-btn[aria-label^='Prep']:visible, #view .agenda-row:visible").first.click()
    page.wait_for_timeout(150)
    prep = page.locator(".sheet").get_attribute("aria-label") or ""
    att = page.locator(".sheet button.person-link")
    ok = att.count() > 0
    if ok:
        att.first.click()
        page.wait_for_timeout(150)
        page.locator(".sheet-h button", has_text="Back").click()
        page.wait_for_timeout(120)
        ok = page.locator(".sheet").get_attribute("aria-label") == prep
    check("prep: an attendee opens their person panel and Back returns to the prep", ok, prep)
    page.keyboard.press("Escape")
    page.wait_for_timeout(50)
    # P3: the prep and notes panels skip the panel anatomy (no TL;DR heading / no timeline fallback).
    page.locator("#view button.link-btn[aria-label^='Prep']:visible, #view .agenda-row:visible").first.click()
    page.wait_for_timeout(150)
    sh = page.locator(".sheet")
    txt = sh.inner_text()
    check("prep panel has a TL;DR area and a timeline or 'No history yet' like every other panel",
          "TL;DR" in txt and (sh.locator(".tl").count() > 0 or "No history yet" in txt), txt[:120].replace("\n", " "))
    ctx.close()

    # Reopen after re-render keeps the edit.
    ctx, page = thread(qa, b)
    page.locator(".sheet .composer [name=body]").fill("My own words, kept.")
    page.keyboard.press("Escape")
    tab(page, "Pipeline")
    tab(page, "Today")
    page.locator("section[aria-label='Threads'] .row-hit").first.click()
    page.wait_for_timeout(150)
    check("reopen after re-render: the edited draft is still there", page.locator(".sheet .composer [name=body]").input_value() == "My own words, kept.")
    ctx.close()


# ---------------------------------------------------------------------------------------------- the composer
def composer(qa, b) -> None:
    ctx, page = thread(qa, b)
    c = page.locator(".sheet .composer")
    to = c.locator("[name=to]")
    check("composer: Send stays plain Send when the summary names the thread's people", foot(page).inner_text().strip() == "Send", foot(page).inner_text())
    to.press("Enter")
    c.locator("[name=subject]").press("Enter")
    page.wait_for_timeout(40)
    check("safety: Enter in To or Subject never opens the confirm or sends", not page.locator(".sheet .send-confirm").is_visible() and not page.evaluate(SENDS))
    to.fill("")
    check("composer: Send with an empty To asks who it goes to, no confirm", not ask_send(page) and page.evaluate("document.activeElement.name") == "to")
    to.fill("not-an-email")
    check("composer: Send with only an invalid To does not confirm", not ask_send(page))
    to.fill("")
    c.locator("[name=cc]").fill("x@y.com")
    check("composer: only a Cc does not confirm (needs a To)", not ask_send(page))
    to.fill("a@b.com; c@d.com  e@f.com")
    ok = ask_send(page) and "a@b.com, c@d.com, e@f.com" in page.locator(".sheet .send-confirm").inner_text()
    check("composer: a list with semicolons and spaces reads as three addresses", ok)
    page.locator(".sheet .send-confirm button", has_text="Not yet").click()
    page.wait_for_timeout(40)
    check("composer: Not yet hides the confirm and sends nothing", not page.locator(".sheet .send-confirm").is_visible() and not page.evaluate(SENDS))
    to.fill("good@x.com, junk")
    ask_send(page)
    conf = page.locator(".sheet .send-confirm").inner_text() if page.locator(".sheet .send-confirm").is_visible() else ""
    check("composer: a To with a bad part ('junk') says so instead of silently dropping it", "junk" in conf or not conf, conf[:120])
    if page.locator(".sheet .send-confirm").is_visible():
        page.locator(".sheet .send-confirm button", has_text="Not yet").click()
    to.fill("Ishaan Verma <ishaan@atlassettle.com>")
    c.locator("[name=cc]").fill("")
    if ask_send(page):
        send_now(page)
    s = page.evaluate(SENDS)
    check("composer: 'Name <email>' sends to the bare address", bool(s) and s[-1]["input"]["to"] == ["ishaan@atlassettle.com"], json.dumps(s[-1]["input"]["to"]) if s else "no send")
    ctx.close()

    # Unicode, emoji, markup; the edit kept as guidance; the draft marked sent.
    ctx, page = thread(qa, b)
    body = "नमस्ते Raj 👋🏽, café – “quotes” <b>bold</b> & more.\n\nSecond para."
    page.locator(".sheet .composer [name=body]").fill(body)
    href = page.locator(".sheet .composer a", has_text="Open in Gmail").get_attribute("href") or ""
    qs = U.parse_qs(U.urlparse(href).query)
    check("Open in Gmail opens the draft as edited, not as first written", qs.get("body", [""])[0] == body, qs.get("body", [""])[0][:60])
    check("Open in Gmail opens the user's own account with To and Cc filled", qs.get("authuser") == ["aditi@quillwater.vc"] and qs.get("to") == ["arjun@gravitypayouts.com"] and bool(qs.get("cc")))
    ask_send(page)
    send_now(page)
    s = page.evaluate(SENDS)
    check("send: unicode and emoji go exactly as typed; htmlBody is Verdana and escapes markup",
          len(s) == 1 and s[0]["input"]["body"] == body and "Verdana" in s[0]["input"]["htmlBody"] and "&lt;b&gt;" in s[0]["input"]["htmlBody"] and "👋🏽" in s[0]["input"]["htmlBody"])
    items = writes(page, path="state/items")
    vals = list(((items[-1]["data"] or {}).get("items") or {}).values()) if items else []
    check("send: the draft and its promise are marked sent in state/items", bool(vals) and all(v.get("sent") for v in vals), json.dumps(vals)[:160])
    ed = [w["data"] for w in writes(page, coll="ratings") if (w.get("data") or {}).get("kind") == "draft_edit"]
    check("send: the edit is kept as draft_edit with before and after", len(ed) == 1 and ed[0]["after"] == body and ed[0]["before"].startswith("Hi Raj"))
    check("send: the draft_edit names the record it was about (ent)", bool(ed) and bool(ed[0].get("ent")), json.dumps(ed[0].get("ent") if ed else None))
    check("send: the panel closes after a send, no errors", page.locator(".sheet").count() == 0 and not errs(page), "; ".join(errs(page)[:2]))
    ctx.close()

    # Long body.
    ctx, page = thread(qa, b)
    long = ("This is a long line of the body. " * 320).strip()
    page.locator(".sheet .composer [name=body]").fill(long)
    ask_send(page)
    send_now(page)
    s = page.evaluate(SENDS)
    check("send: a 10,000 character body goes whole, once", len(s) == 1 and s[0]["input"]["body"] == long)
    ctx.close()

    # Double tap on Send now.
    ctx, page = thread(qa, b)
    ask_send(page)
    page.locator(".sheet .send-confirm button", has_text="Send now").dblclick()
    page.wait_for_timeout(300)
    check("safety: a double tap on Send now sends exactly once", len(page.evaluate(SENDS)) == 1, str(len(page.evaluate(SENDS))))
    ctx.close()

    # Send again while the first send is still on its way.
    ctx, page = thread(qa, b)
    page.evaluate(SLOW, [1200, False])
    page.wait_for_timeout(30)
    ask_send(page)
    send_now(page, 100)
    again = ask_send(page)
    if again and page.locator(".sheet .send-confirm button", has_text="Send now").count():
        send_now(page, 50)
    page.wait_for_timeout(1500)
    n = len(page.evaluate(SENDS))
    check("safety: while a send is on its way, Send cannot start a second one", n == 1, f"{n} send_message calls")
    ctx.close()

    # Gmail fails: nothing went out, the draft stays, no sent mark.
    for code, word in (("tool_error", "Nothing went out"), ("not_granted", "not allowed")):
        ctx, page = thread(qa, b, mcp={"pages": ["ok"], "fail": code})
        page.locator(".sheet .composer [name=body]").fill("Edited before the failure")
        ask_send(page)
        send_now(page)
        msg = page.locator(".sheet .send-confirm").inner_text() if page.locator(".sheet .send-confirm").count() else ""
        page.keyboard.press("Escape")
        page.locator("section[aria-label='Threads'] .row-hit").first.click()
        page.wait_for_timeout(150)
        kept = page.locator(".sheet .composer [name=body]").input_value() == "Edited before the failure"
        check(f"Gmail {code}: says '{word}', keeps the edited draft, marks nothing sent",
              word in msg and kept and not writes(page, path="state/items") and not [w for w in writes(page, coll="ratings") if (w.get("data") or {}).get("kind") == "draft_edit"], msg[:100])
        ctx.close()

    # A send that fails after the panel was closed must still say so.
    ctx, page = thread(qa, b)
    page.evaluate(SLOW, [600, True])
    page.wait_for_timeout(30)
    ask_send(page)
    send_now(page, 50)
    page.keyboard.press("Escape")
    page.wait_for_timeout(900)
    toast = " ".join(page.locator(".toast").all_inner_texts())
    check("Gmail fails after the panel closed: the user is told nothing went out", "did not send" in toast or "Nothing went out" in toast, toast[:100])
    ctx.close()

    # A send that lands after the user opened another panel must not close that one.
    ctx, page = thread(qa, b)
    page.evaluate(SLOW, [600, False])
    page.wait_for_timeout(30)
    ask_send(page)
    send_now(page, 50)
    page.keyboard.press("Escape")
    page.locator("section[aria-label='Decisions'] .row-hit").first.click()
    page.wait_for_timeout(900)
    check("a send landing later leaves the panel the user opened since alone", page.locator(".sheet").count() == 1)
    ctx.close()

    # Send anyway when the summary is off-topic.
    ctx, page = thread(qa, b, tl=TL_OFF)
    f = foot(page)
    held = f.inner_text().strip() == "Send anyway" and "btn-primary" not in (f.get_attribute("class") or "")
    ask_send(page)
    warn = page.locator(".sheet .send-confirm .watch-note").count() == 1
    send_now(page)
    check("off-topic summary: Send anyway, the confirm warns, then it sends once", held and warn and len(page.evaluate(SENDS)) == 1)
    ctx.close()

    # Team chips, Rewrite, I already sent it, Remind me tomorrow.
    ctx, page = thread(qa, b)
    chip = page.locator(".sheet .team-chips button").first
    mate = chip.get_attribute("title")
    chip.click()
    page.wait_for_timeout(40)
    on = mate in page.locator(".sheet [name=cc]").input_value() and page.locator(".sheet .team-chips button").first.get_attribute("aria-pressed") == "true"
    focus_kept = "chip" in (page.evaluate("document.activeElement.className") or "")
    page.locator(".sheet .team-chips button").first.click()
    page.wait_for_timeout(40)
    off = mate not in page.locator(".sheet [name=cc]").input_value() and "raj.malhotra@fablebank.in" in page.locator(".sheet [name=cc]").input_value()
    check("team chip: a tap copies the colleague in, a second tap takes them out, others stay", on and off)
    check("team chip: keyboard focus stays on the chip after a tap", focus_kept, page.evaluate("document.activeElement.tagName"))
    n0 = len(page.evaluate("window.__samples"))
    page.locator(".sheet .composer button", has_text="Rewrite").click()
    page.wait_for_timeout(120)
    check("Rewrite asks Claude again and puts its new draft in", len(page.evaluate("window.__samples")) > n0 and
          page.locator(".sheet .composer [name=body]").input_value() == TL_ON["body"] and not page.evaluate(SENDS))
    page.locator(".sheet button", has_text="Remind me tomorrow").click()
    page.wait_for_timeout(120)
    rem = writes(page, path="state/reminders")
    item = list(((rem[-1]["data"] or {}).get("items") or {}).values())[-1] if rem else {}
    check("Remind me tomorrow saves 'Follow up: <title>' due tomorrow 09:00 in the user's zone",
          item.get("text", "").startswith("Follow up: Intro") and item.get("due") == "2026-10-23T03:30:00.000Z", json.dumps(item))
    again = page.locator(".sheet .pn-actions button").last
    if again.is_enabled():
        again.click()
        page.wait_for_timeout(120)
    # The harness clock is frozen, so both taps get the same "r" + Date.now() id; on a real clock they are two reminders.
    n_rem = len(writes(page, path="state/reminders"))
    check("Remind me tomorrow tapped twice does not add the same reminder twice", n_rem == 1, f"{n_rem} reminder writes")
    page.locator(".sheet button", has_text="I already sent it").click()
    page.wait_for_timeout(150)
    items = writes(page, path="state/items")
    vals = list(((items[-1]["data"] or {}).get("items") or {}).values()) if items else []
    check("I already sent it marks the draft sent and never calls Gmail", bool(vals) and all(v.get("sent") for v in vals) and not page.evaluate(SENDS))
    ctx.close()

    # A deal's composer: once sent, the same draft cannot go out again.
    ctx, page = qa.open(b, "deal", Q.DESK, open_all=False, inline=False, sample={"answer": "x", "json": TL_ON}, mcp={"pages": ["ok"]})
    tab(page, "Pipeline")
    page.locator("table.deals tbody tr", has_text="Atlas Settlement").locator(".row-hit").click()
    page.wait_for_timeout(150)
    foot(page).click()
    page.wait_for_timeout(80)
    ask_send(page)
    send_now(page)
    if page.locator(".sheet").count() and ask_send(page) and page.locator(".sheet .send-confirm button", has_text="Send now").count():
        send_now(page)
    n = len(page.evaluate(SENDS))
    check("deal panel: after Send now the same email cannot be sent a second time", n == 1, f"{n} sends")
    ctx.close()

    # A pitch reply sent from Home leaves a record (otherwise the pitch still waits for a reply).
    ctx, page = qa.open(b, "pitch", Q.DESK, open_all=False, inline=False, sample={"answer": "x", "json": TL_ON}, mcp={"pages": ["ok"]})
    tab(page, "Pipeline")
    page.locator("section[aria-label='Pitches'] .row-hit").first.click()
    page.wait_for_timeout(150)
    foot(page).click()
    page.wait_for_timeout(80)
    ask_send(page)
    send_now(page)
    check("pitch: a reply sent from Home is recorded on the pitch", len(page.evaluate(SENDS)) == 1 and bool(writes(page, path="state/items") or writes(page, path="state/actions")))
    ctx.close()


# ---------------------------------------------------------------------------------------------- Right call?
def ratings(qa, b) -> None:
    ctx, page = qa.open(b, "rate", Q.DESK, open_all=False, inline=False, sample={"answer": "x", "json": TL_ON}, mcp={"pages": ["ok"]})
    page.locator("section[aria-label='Decisions'] .row-hit").first.click()
    page.wait_for_timeout(220)
    page.locator(".sheet .judge button", has_text="Right").first.click()
    page.wait_for_timeout(80)
    votes = [w["data"] for w in writes(page, coll="ratings") if (w["data"] or {}).get("value") == "useful"]
    check("Right call? Right counts as one useful vote", len(votes) == 1, f"{len(votes)} useful rows")
    check("Right call? the pressed choice shows as pressed", page.locator(".sheet .judge button.chip-rate", has_text="Right").first.get_attribute("aria-pressed") == "true")
    page.locator(".sheet .judge button", has_text="Not right").click()
    page.locator(".sheet .judge input[name=why]").fill("Wrong person, ask the CFO")
    page.locator(".sheet .judge input[name=why]").press("Enter")
    page.wait_for_timeout(80)
    rs = [w["data"] for w in writes(page, coll="ratings")]
    notes = [r for r in rs if r.get("note")]
    check("Not right: the note is saved with about, ent and scope_kind", len(notes) == 1 and notes[0]["note"].startswith("Wrong person") and
          notes[0].get("about") == "Approve the Gravity Payouts step" and notes[0].get("ent") == "c:c_gravity" and notes[0].get("scope_kind") == "ready", json.dumps(notes)[:200])
    nu = [r for r in rs if r.get("value") == "not_useful"]
    check("Not right with a note counts as one not_useful vote", len(nu) == 1, f"{len(nu)} not_useful rows")
    page.keyboard.press("Escape")
    page.wait_for_timeout(60)
    check("after rating in a panel, closing it returns focus to the row", "row-hit" in (page.evaluate("document.activeElement.className") or ""),
          page.evaluate("document.activeElement.tagName"))
    ctx.close()


# ---------------------------------------------------------------------------------------------- static demo and source-level safety
def static_and_source(qa, b) -> None:
    snaps = json.loads(json.dumps(qa.snaps["aditi"], default=str))
    snaps["config"]["demo"] = True
    data = json.dumps({"order": ["aditi"], "members": {"aditi": {"label": "Aditi", "snaps": snaps, "state": {"items": {}, "actions": {}, "reminders": {}}}}}).replace("</", "<\\/")
    html = open(qa.wrapper, encoding="utf-8").read()
    marker = "<script>\n(function () {"
    html = html.replace(marker, f'<script type="application/json" id="instinct-demo">{data}</script>\n' + marker, 1)
    path = os.path.join(OUT, "_static.html")
    open(path, "w", encoding="utf-8").write(html)
    real, qa.wrapper = qa.wrapper, path
    try:
        ctx, page = thread(qa, b)
        page.locator(".sheet .composer [name=body]").fill("Edited in the demo")
        ask_send(page)
        send_now(page)
        check("static demo: Send now never calls Gmail and writes nothing", not page.evaluate("window.__mcp") and not page.evaluate("window.__writes"))
        toast = " ".join(page.locator(".toast").all_inner_texts())
        check("static demo: the toast after Send now says nothing was sent", "nothing was sent" in toast, toast[:100])
        ctx.close()
    finally:
        qa.wrapper = real
    src = open(os.path.join(ROOT, "home", "index.html"), encoding="utf-8").read()
    calls = re.findall(r"callTool\([^)]*send_message", src)
    check("source: Gmail send_message is called from one place only (Send now)", len(calls) == 1 and src.count("send_message") == 1, str(len(calls)))
    sched = open(os.path.join(ROOT, "schedules.json"), encoding="utf-8").read()
    guard = open(os.path.join(ROOT, "hooks", "guard.py"), encoding="utf-8").read()
    check("scheduled runs: the guard marker is in both schedule prompts and in the guard", sched.count("[ant-vc-scheduled-run]") == 2 and "ant-vc-scheduled-run" in guard)


# ---------------------------------------------------------------------------------------------- round 2: what the fixes changed
def round2(qa, b) -> None:
    # Close the panel while a send is on its way, reopen it, and send again: still only one email.
    ctx, page = thread(qa, b)
    page.evaluate(SLOW, [1200, False])
    page.wait_for_timeout(30)
    ask_send(page)
    send_now(page, 80)
    page.keyboard.press("Escape")
    page.locator("section[aria-label='Threads'] .row-hit").first.click()
    page.wait_for_timeout(150)
    if page.locator(".sheet .composer [name=body]").count() and ask_send(page) and page.locator(".sheet .send-confirm button", has_text="Send now").count():
        send_now(page, 50)
    page.wait_for_timeout(1500)
    n = len(page.evaluate(SENDS))
    check("round2: closing and reopening the panel mid-send cannot start a second send", n == 1, f"{n} sends")
    ctx.close()

    # After a failure: label back to Send, enabled, draft kept, a retry sends once.
    ctx, page = thread(qa, b)
    page.evaluate(SLOW, [300, True])
    page.wait_for_timeout(30)
    page.locator(".sheet .composer [name=body]").fill("Kept after the failure")
    ask_send(page)
    send_now(page, 600)
    f = foot(page)
    check("round2: after a failed send the footer reads Send and is enabled", f.inner_text().strip().startswith("Send") and "Sending" not in f.inner_text() and f.is_enabled(), f.inner_text())
    check("round2: after a failed send the edited draft is still in the box", page.locator(".sheet .composer [name=body]").input_value() == "Kept after the failure")
    page.evaluate(SLOW, [100, False])
    page.wait_for_timeout(30)
    ask_send(page)
    send_now(page, 400)
    s = page.evaluate(SENDS)
    check("round2: a retry after a failure sends once, as edited, and closes the panel",
          len(s) == 2 and s[-1]["input"]["body"] == "Kept after the failure" and page.locator(".sheet").count() == 0, f"{len(s)} calls")
    ctx.close()

    # A display name with a comma in it, unquoted, as Outlook writes it.
    ctx, page = thread(qa, b)
    page.locator(".sheet .composer [name=to]").fill("Verma, Ishaan <ishaan@atlassettle.com>")
    ask_send(page)
    conf = page.locator(".sheet .send-confirm").inner_text()
    check("round2: 'Verma, Ishaan <email>' sends to the address and does not call the surname a bad address", "Left out" not in conf and "ishaan@atlassettle.com" in conf, conf[:120])
    ctx.close()

    # Focus after Send now goes back to Today, not to nothing.
    ctx, page = thread(qa, b)
    ask_send(page)
    send_now(page, 300)
    check("round2: after Send now, focus lands on a row or a section, not on the page body",
          page.evaluate("document.activeElement && document.activeElement !== document.body"), page.evaluate("document.activeElement.tagName"))
    toast = " ".join(page.locator(".toast").all_inner_texts())
    check("round2: one toast after a send, and it says it went from Gmail", "Gmail" in toast or "Sent" in toast, toast[:100])
    items = writes(page, path="state/items")
    keys = []
    for w in items:
        keys += list(((w["data"] or {}).get("items") or {}).keys())
    check("round2: a send writes each sent mark once", len(items) == 1 and len(keys) == len(set(keys)), f"{len(items)} writes")
    ctx.close()

    # Deal send records a sent item and closes; person send records too.
    ctx, page = qa.open(b, "deal2", Q.DESK, open_all=False, inline=False, sample={"answer": "x", "json": TL_ON}, mcp={"pages": ["ok"]})
    tab(page, "Pipeline")
    page.locator("table.deals tbody tr", has_text="Atlas Settlement").locator(".row-hit").click()
    page.wait_for_timeout(150)
    foot(page).click()
    page.wait_for_timeout(80)
    ask_send(page)
    send_now(page)
    rec = [v for w in writes(page, path="state/items") for v in ((w["data"] or {}).get("items") or {}).values() if v.get("sent")]
    check("round2: a deal send records one sent item and closes the panel", len(rec) >= 1 and page.locator(".sheet").count() == 0 and len(page.evaluate(SENDS)) == 1)
    tab(page, "People")
    page.locator("#view tbody .cell-hit").first.click()
    page.wait_for_timeout(150)
    has = page.locator(".sheet-foot button").first
    ok = True
    if has.count() and "Write" in has.inner_text():
        n0 = len(writes(page, path="state/items"))
        has.click(); page.wait_for_timeout(80)
        ask_send(page); send_now(page)
        ok = len(writes(page, path="state/items")) > n0 and len(page.evaluate(SENDS)) == 2
    check("round2: a person send records a sent item", ok)
    ctx.close()

    # Verdict: switching Right -> Not right -> Right writes one row per tap.
    ctx, page = qa.open(b, "rate2", Q.DESK, open_all=False, inline=False, sample={"answer": "x", "json": TL_ON}, mcp={"pages": ["ok"]})
    page.locator("section[aria-label='Decisions'] .row-hit").first.click()
    page.wait_for_timeout(220)
    for lab in ("Right", "Not right", "Right"):
        page.locator(".sheet .judge button.chip-rate", has_text=lab).first.click() if lab != "Right" else page.locator(".sheet .judge button.chip-rate").first.click()
        page.wait_for_timeout(60)
    rs = writes(page, coll="ratings")
    check("round2: three taps on Right call? write three rows", len(rs) == 3, f"{len(rs)} rows")
    page.keyboard.press("Escape")
    page.wait_for_timeout(60)
    check("round2: focus returns to the row after rating several times", "row-hit" in (page.evaluate("document.activeElement.className") or ""))
    ctx.close()

    # Approve a CRM change from its panel: focus returns to Today.
    ctx, page = qa.open(b, "appr", Q.DESK, open_all=False, inline=False, sample={"answer": "x", "json": TL_ON}, mcp={"pages": ["ok"]})
    page.locator("section[aria-label='Decisions'] .row-hit").first.click()
    page.wait_for_timeout(150)
    ap = page.locator(".sheet-foot button", has_text="Approve")
    had = ap.count() > 0
    if had:
        ap.first.click(); page.wait_for_timeout(150)
    check("round2: after Approve in a panel, focus is on a row, not the page body", had and page.evaluate("document.activeElement !== document.body"),
          page.evaluate("document.activeElement.tagName"))
    ctx.close()


def main() -> int:
    t0 = time.time()
    qa = Q.QA(OUT)
    with sync_playwright() as p:
        b = p.chromium.launch()
        for part in (composer, ratings, round2, static_and_source, navigation, sweep):
            try:
                part(qa, b)
            except Exception as e:  # a crash in one part is a failed check, the rest still run
                check(f"{part.__name__} ran to the end", False, repr(e)[:200])
        b.close()
    ok = sum(1 for r in RESULTS if r[0])
    print(f"{ok}/{len(RESULTS)} checks pass ({time.time() - t0:.0f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
