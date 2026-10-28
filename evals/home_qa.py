"""ant. Home QA: renders the page with a mock Claude runtime and golden Quillwater data, then clicks through it.

Needs Playwright with Chromium. Optional: INSTINCT_FONTS=<dir with raleway/nunito latin woff2 files> for true type.

    python3 evals/home_qa.py [--out evals/reports/home] [--only today,prep]

Writes screenshots and qa.json (one row per check) to --out. Exit code 1 if any check fails.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import os
import sys

sys.dont_write_bytecode = True  # an eval clone stays clean: no __pycache__ beside the code

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "evals"))
import demo  # noqa: E402

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
T0 = dt.datetime(2026, 10, 22, 7, 5, tzinfo=IST)
PHONE = {"width": 380, "height": 844}
DESK = {"width": 1440, "height": 900}

SKELETON = ('<!doctype html><html><head><meta charset=utf8><meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover">'
            '<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom)}'
            'body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}</style>{fonts}</head><body>{page}</body></html>')

MOCK = r"""
(function () {
  var CFG = window.__QA__ || {};
  window.__writes = []; window.__errors = [];
  if (CFG.noRuntime) return;
  var SNAP = CFG.snap || {}, STATE = CFG.state || {}, listeners = {};
  function snapOf(id, data) { return { id: id, exists: data !== undefined && data !== null, data: function () { return data; }, metadata: { fromCache: false, hasPendingWrites: false } }; }
  function merge(a, b) { Object.keys(b).forEach(function (k) { var v = b[k]; if (v && typeof v === "object" && !Array.isArray(v) && a[k] && typeof a[k] === "object") merge(a[k], v); else a[k] = v; }); return a; }
  function emit(key) { var fn = listeners[key]; if (fn) setTimeout(function () { fn(snapOf(key, STATE[key] ? { items: JSON.parse(JSON.stringify(STATE[key])) } : undefined)); }, 10); }
  function qsOf(list) { var docs = list.map(function (x, i) { return snapOf(x.id || ("d" + i), x.data); }); return { docs: docs, size: docs.length, empty: !docs.length, docChanges: function () { return []; }, metadata: {} }; }
  var db = {
    collection: function (name) {
      var q = {
        orderBy: function () { return q; }, limit: function () { return q; }, where: function () { return q; },
        onSnapshot: function (next, error) {
          if (name === "snap") {
            if (CFG.dbError) { setTimeout(function () { error && error({ code: "unavailable", message: "down" }); }, 20); return function () {}; }
            if (CFG.never) return function () {};
            setTimeout(function () { next(qsOf(Object.keys(SNAP).map(function (k) { return { id: k, data: SNAP[k] }; }))); }, 20);
          }
          if (name === "runs") setTimeout(function () { next(qsOf((CFG.runs || []).map(function (r, i) { return { id: "r" + i, data: r }; }))); }, 20);
          return function () {};
        },
        add: function (data) { window.__writes.push({ op: "add", collection: name, data: data }); return Promise.resolve({ id: "auto" + window.__writes.length }); }
      };
      return q;
    },
    doc: function (path) {
      var key = path.split("/")[1];
      if (path.indexOf("snap/") === 0) return {
        update: function (d) { if (!SNAP[key]) return Promise.reject({ code: "invalid_argument", message: "document does not exist" });
          merge(SNAP[key], JSON.parse(JSON.stringify(d))); window.__writes.push({ op: "update", path: path, data: d }); return Promise.resolve(); },
        set: function (d) { SNAP[key] = JSON.parse(JSON.stringify(d)); window.__writes.push({ op: "set", path: path, data: d }); return Promise.resolve(); }
      };
      return {
        onSnapshot: function (next) { listeners[key] = next; emit(key); return function () {}; },
        update: function (d) {
          if (CFG.readOnlyWrites) return Promise.reject({ code: "invalid_argument", message: "not allowed" });
          if (!STATE[key]) return Promise.reject({ code: "invalid_argument", message: "document does not exist" });
          merge(STATE[key], JSON.parse(JSON.stringify(d.items))); window.__writes.push({ op: "update", path: path, data: d }); emit(key); return Promise.resolve();
        },
        set: function (d) {
          if (CFG.readOnlyWrites) return Promise.reject({ code: "invalid_argument", message: "not allowed" });
          STATE[key] = JSON.parse(JSON.stringify(d.items)); window.__writes.push({ op: "set", path: path, data: d }); emit(key); return Promise.resolve();
        }
      };
    }
  };
  var user = { isOwner: function () { return Promise.resolve(CFG.owner !== false); } };
  window.__samples = []; window.__mcp = [];
  var sample = null, mcp = null;
  if (CFG.sample) {
    sample = function (input, opts) {
      window.__samples.push(input);
      if (CFG.sample.fail) return Promise.reject({ code: CFG.sample.fail, message: "mock" });
      var t = CFG.sample.answer || "An answer.";
      return new Promise(function (res) { setTimeout(function () { if (opts && opts.onText) opts.onText({ text: t, delta: t }); res({ text: t, truncated: false, modelTierApplied: "default" }); }, 30); });
    };
    sample.json = function (input) { window.__samples.push(input); return Promise.resolve(JSON.parse(JSON.stringify(CFG.sample.json || {}))); };
  }
  if (CFG.mcp) {
    var pages = CFG.mcp.pages || [], n = 0, files = 0;
    mcp = { callTool: function (server, tool, input) {
      window.__mcp.push({ server: server, tool: tool, input: input });
      if (CFG.mcp.fail) return Promise.reject({ code: CFG.mcp.fail, message: "mock" });
      if (tool === "get_page_text") return Promise.resolve({ content: [], payload: pages[Math.min(n++, pages.length - 1)] || "" });
      if (tool === "find") return Promise.resolve({ content: [], payload: '- link "' + (input.query || "") + '" [ref_7]' });
      if (tool === "search_files") return Promise.resolve({ content: [], payload: { files: [] } });
      if (tool === "create_file") { files += 1; return Promise.resolve({ content: [], payload: { id: "f" + files, webViewLink: "https://docs.google.com/document/d/f" + files + "/edit" } }); }
      return Promise.resolve({ content: [], payload: "ok" });
    } };
  }
  window.claude = { use: function (name) { return Promise.resolve(name === "db" ? (CFG.noDb ? null : db) : name === "user" ? user : name === "sample" ? sample : name === "mcp" ? mcp : null); } };
})();
"""


# Every visible piece of text, every status mark and every field edge, measured against what is really behind it
# (backgrounds composited up the tree). WCAG 2.2: 4.5:1 for text, 3:1 for large text, marks and field edges.
SCAN = r"""
(scope) => {
  function parse(c) { var m = String(c || "").match(/rgba?\(([^)]+)\)/); if (!m) return null;
    var p = m[1].split(/[\s,\/]+/).filter(Boolean).map(Number); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; }
  function over(t, b) { var a = t[3]; return [t[0] * a + b[0] * (1 - a), t[1] * a + b[1] * (1 - a), t[2] * a + b[2] * (1 - a), 1]; }
  function lum(c) { function f(v) { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); }
  function ratio(a, b) { var x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); }
  function bgOf(el) {
    var layers = [], e = el;
    while (e && e.nodeType === 1) { var c = parse(getComputedStyle(e).backgroundColor); if (c && c[3] > 0) { layers.push(c); if (c[3] >= 1) break; } e = e.parentElement; }
    var base = [255, 255, 255, 1];
    for (var i = layers.length - 1; i >= 0; i--) base = over(layers[i], base);
    return base;
  }
  function seen(el) { var cs = getComputedStyle(el); return el.getClientRects().length && cs.visibility !== "hidden" && Number(cs.opacity) > 0.05; }
  function name(el) { var t = (el.textContent || el.getAttribute("aria-label") || "").trim().replace(/\s+/g, " ");
    return el.tagName.toLowerCase() + (el.className && typeof el.className === "string" ? "." + el.className.trim().split(/\s+/).join(".") : "") + ' "' + t.slice(0, 48) + '"'; }
  var root = scope ? document.querySelector(scope) : document.body, out = { checked: 0, marks: 0, fails: [], min: 99 };
  function judge(el, fg, bg, need, kind) {
    var r = ratio(fg, bg); out.min = Math.min(out.min, r);
    if (r + 1e-6 < need) out.fails.push({ el: name(el), kind: kind, ratio: Math.round(r * 100) / 100, need: need,
      fg: "rgb(" + fg.slice(0, 3).map(Math.round).join(",") + ")", bg: "rgb(" + bg.slice(0, 3).map(Math.round).join(",") + ")" });
  }
  Array.prototype.forEach.call(root.querySelectorAll("*"), function (el) {
    if (!seen(el) || el.closest("svg.ah-mark")) return;
    var cs = getComputedStyle(el), bg = bgOf(el);
    var text = Array.prototype.some.call(el.childNodes, function (n) { return n.nodeType === 3 && n.textContent.trim(); });
    if (text) {
      var fg = parse(cs.color); if (!fg) return; if (fg[3] < 1) fg = over(fg, bg);
      var size = parseFloat(cs.fontSize), bold = Number(cs.fontWeight) >= 700;
      out.checked++; judge(el, fg, bg, size >= 24 || (size >= 18.66 && bold) ? 3 : 4.5, "text");
    }
    if (el.tagName === "INPUT") {
      var edge = String(cs.boxShadow || "").match(/rgba?\([^)]+\)/);
      if (edge) { var ec = parse(edge[0]); out.marks++; judge(el, ec[3] < 1 ? over(ec, bg) : ec, bg, 3, "field edge"); }
      if (!el.value && el.placeholder) { var ph = parse(getComputedStyle(el, "::placeholder").color); if (ph) { out.checked++; judge(el, ph[3] < 1 ? over(ph, bg) : ph, bg, 4.5, "placeholder"); } }
    }
    if (el.tagName === "path" && el.closest("svg.glyph, button svg, a svg")) {
      var best = 0, host = bgOf(el.closest("svg").parentElement);
      ["stroke", "fill"].forEach(function (k) { var c = parse(cs[k]); if (c && c[3] > 0) best = Math.max(best, ratio(c[3] < 1 ? over(c, host) : c, host)); });
      if (best) { out.marks++; out.min = Math.min(out.min, best); if (best + 1e-6 < 3) out.fails.push({ el: name(el.closest("svg").parentElement) + " icon", kind: "mark",
        ratio: Math.round(best * 100) / 100, need: 3 }); }
    }
  });
  // A selected tab or pressed chip is told apart by its fill: 3:1 against the unselected one beside it (WCAG 1.4.11).
  Array.prototype.forEach.call(root.querySelectorAll('[aria-selected="true"], [aria-pressed="true"]'), function (el) {
    if (!seen(el)) return;
    var attr = el.hasAttribute("aria-selected") ? "aria-selected" : "aria-pressed";
    var box = function (x) { return x.querySelector(".ah-tab-ico") && getComputedStyle(x).backgroundColor === "rgba(0, 0, 0, 0)" ? x.querySelector(".ah-tab-ico") : x; };
    var other = Array.prototype.filter.call(el.parentNode.children, function (x) { return x !== el && x.getAttribute(attr) === "false" && seen(x); })[0];
    var r = ratio(bgOf(box(el)), other ? bgOf(box(other)) : bgOf(el.parentElement));
    out.marks++; out.states = (out.states || 0) + 1; out.min = Math.min(out.min, r);
    if (r + 1e-6 < 3) out.fails.push({ el: name(el) + " (selected)", kind: "selected state", ratio: Math.round(r * 100) / 100, need: 3 });
  });
  var a = document.activeElement;
  if (a && a !== document.body && seen(a)) { var oc = parse(getComputedStyle(a).outlineColor), os = getComputedStyle(a).outlineStyle;
    if (oc && os !== "none") { out.marks++; judge(a, oc, bgOf(a.parentElement || a), 3, "focus ring"); } }
  out.min = Math.round(out.min * 100) / 100;
  return out;
}
"""


def fonts_css() -> str:
    d = os.environ.get("INSTINCT_FONTS")
    if not d or not os.path.isdir(d):
        return ""
    faces = []
    for fam, weights in (("Raleway", (200, 700)), ("Nunito", (400, 600, 700, 800))):
        for w in weights:
            path = os.path.join(d, f"{fam.lower()}-latin-{w}-normal.woff2")
            if os.path.exists(path):
                faces.append(f'@font-face{{font-family:"{fam}";font-weight:{w};font-style:normal;src:url("file://{path}") format("woff2")}}')
    return "<style>" + "".join(faces) + "</style>"


class _LazySnaps(dict):
    """{member: the demo's snapshots}, built the first time each is asked for."""
    def __missing__(self, member: str) -> dict:
        self[member] = demo.build(member)
        return self[member]


def bucket_label(it: dict) -> str:
    """The Today section Home puts a brief line in (home/index.html, bucketOf)."""
    w, k = it.get("status_word"), it.get("kind")
    if w == "team" or it.get("fyi"):
        return "Watch"
    if k in ("inbound", "pass_returned"):
        return "Decide"
    if k == "waiting" and it.get("to_you") is False:
        return "Watch"
    if k == "waiting" or w in ("waiting", "asked", "requested"):
        return "Waiting on others"
    if k in ("decision", "signal", "stale", "deal_move", "review"):
        return "Decide"
    if k in ("commitment", "question", "ask", "lp", "relationship") or it.get("late_fold"):
        return "Send"
    return "Watch"


DECIDE = "section[aria-label='Decide']"
SEND = "section[aria-label='Send']"
READY = "section[aria-label='Decide'], section[aria-label='Send']"
OPEN_LINES = "#view section.card:not([aria-label='Done today'])"


def ready_text(page) -> str:
    return " ".join(page.locator(READY).all_inner_texts())


class QA:
    def __init__(self, out: str):
        self.out = out
        self.rows: list[dict] = []
        os.makedirs(out, exist_ok=True)
        page = open(os.path.join(ROOT, "home", "index.html"), encoding="utf-8").read()
        self.wrapper = os.path.join(out, "_home.html")
        with open(self.wrapper, "w", encoding="utf-8") as fh:
            fh.write(SKELETON.replace("{fonts}", fonts_css()).replace("{page}", page))
        # The demo's Homes, built on first use: a caller that passes its own snapshots never builds (or reads) them.
        self.snaps = _LazySnaps()

    def check(self, scenario: str, name: str, ok: bool, detail: str = "") -> None:
        self.rows.append({"scenario": scenario, "check": name, "ok": bool(ok), "detail": detail})

    def open(self, browser, scenario: str, viewport=PHONE, when=T0, member="aditi", scheme="light", theme=None, **cfg):
        ctx = browser.new_context(viewport=viewport, timezone_id="Asia/Kolkata", color_scheme=scheme, device_scale_factor=2 if viewport == PHONE else 1)
        page = ctx.new_page()
        if theme:
            page.add_init_script("try { localStorage.setItem('instinct.theme', " + json.dumps(theme) + "); } catch (e) {}")
        page.route("**/fonts.googleapis.com/**", lambda r: r.abort())
        page.route("**/fonts.gstatic.com/**", lambda r: r.abort())
        qa = {"snap": cfg.pop("snap") if "snap" in cfg else self.snaps[member], "open_all": cfg.pop("open_all", True), **cfg}
        page.add_init_script("window.__QA__ = " + json.dumps(qa) + ";" + MOCK)
        errors: list[str] = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.clock.set_fixed_time(when)
        page.goto("file://" + self.wrapper)
        page.wait_for_timeout(250)
        page._qa_errors = errors  # type: ignore[attr-defined]
        return ctx, page

    def done_row(self, member: str = "aditi") -> tuple[str, str]:
        """The first row on Today that can be marked done: (section label, title)."""
        for sec in self.snaps[member]["brief"]["sections"]:
            for it in sec["items"]:
                if "done" in (it.get("actions") or []):
                    return bucket_label(it), it["title"]
        raise AssertionError("no row with Done on Today")

    def tap_done(self, page, member: str = "aditi") -> str:
        label, title = self.done_row(member)
        sec = page.locator(f"section[aria-label='{label}']")
        sec.locator(".row-hit", has_text=title).first.click()
        sec.locator(".row-actions button", has_text="Done").first.click()
        return title

    def shot(self, page, name: str) -> None:
        page.screenshot(path=os.path.join(self.out, name + ".png"), full_page=True)

    def common(self, page, scenario: str) -> None:
        overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
        self.check(scenario, "no horizontal scroll", overflow <= 0, f"overflow {overflow}px")
        primaries = page.evaluate("Array.from(document.querySelectorAll('#view .btn-primary')).filter(b => b.offsetParent).length")
        self.check(scenario, "at most one primary button", primaries <= 1, f"{primaries} primary")
        unnamed = page.evaluate("""Array.from(document.querySelectorAll('button, a')).filter(b => b.offsetParent &&
            !(b.textContent || '').trim() && !b.getAttribute('aria-label')).length""")
        self.check(scenario, "every control has a name", unnamed == 0, f"{unnamed} unnamed")
        tiny = page.evaluate("""Array.from(document.querySelectorAll('#view *')).filter(e => e.offsetParent && e.childNodes.length &&
            Array.from(e.childNodes).some(n => n.nodeType === 3 && n.textContent.trim()) && parseFloat(getComputedStyle(e).fontSize) < 11.5).length""")
        self.check(scenario, "no text under 11.5px", tiny == 0, f"{tiny} elements")
        errs = [e for e in page._qa_errors if "fonts.g" not in e and "ERR_FAILED" not in e]  # type: ignore[attr-defined]
        self.check(scenario, "no script errors", not errs, "; ".join(errs[:3]))

    # ------------------------------------------------------------------ scenarios
    def today(self, browser) -> None:
        for vp, tag in ((PHONE, "380"), (DESK, "1440")):
            sc = f"today-{tag}"
            ctx, page = self.open(browser, sc, vp)
            self.shot(page, f"today-{tag}")
            hero = page.locator(".ah-hero-card .statement").inner_text()
            self.check(sc, "hero states the fact, not a count", hero == "Review the board deck", hero)
            kicker = page.locator(".ah-hero-card .kicker").inner_text()
            self.check(sc, "hero kicker says one thing", len(kicker.split(" · ")) <= 2 and "draft" not in kicker.lower(), kicker)
            self.check(sc, "hero has at most three buttons", page.locator(".ah-hero-card .hero-actions .btn").count() <= 3)
            self.check(sc, "a drafted promise says so under its meeting", page.locator(".agenda-row.first .agenda-draft").count() == 1)
            sizes = page.evaluate("['theme-btn','help-btn'].map(id => { var r = document.getElementById(id).getBoundingClientRect(); return Math.min(r.width, r.height); })")
            self.check(sc, "header buttons are 40px targets", min(sizes) >= 40, str(sizes))
            atlas = page.locator(".agenda-row.first")
            self.check(sc, "the meeting carries its watch line", atlas.locator(".agenda-note", has_text="Bluepeak").count() == 1,
                       atlas.inner_text().replace("\n", " | ")[:160])
            sync = page.locator("button.agenda-row", has_text="Partner sync")
            self.check(sc, "partner sync has a decision pack", sync.count() == 1 and sync.locator(".agenda-note", has_text="Decide").count() >= 1)
            want = len(self.snaps["aditi"]["brief"]["meetings"])
            self.check(sc, "agenda lists every meeting, internal too", page.locator(".agenda-row").count() == want, f"{page.locator('.agenda-row').count()} of {want}")
            self.check(sc, "next meeting marked", page.locator(".agenda-row.is-next .agenda-time").inner_text() == "10:30")
            self.check(sc, "one Prep button on the hero", page.locator(".ah-hero-card button", has_text="Prep").count() <= 1)
            self.check(sc, "every row carries a status word", page.evaluate("""Array.from(document.querySelectorAll('#view .row')).every(r => !!r.querySelector('.status'))"""))
            self.check(sc, "copy brief offered", page.locator("button", has_text="Copy brief").count() == 1)
            self.check(sc, "Decide holds the CRM change and Send the drafts", page.locator(DECIDE, has_text="Approve").count() == 1 and
                       page.locator(SEND + " .row-title", has_text="Intro").count() >= 1)
            self.check(sc, "the day strip counts meetings, decisions, sends and waits",
                       page.locator(".daystrip .stat").count() == 4 and page.locator(".daystrip .stat", has_text="Decide").count() == 1)
            self.check(sc, "evidence line present", "sources" in page.locator(".evidence").inner_text())
            self.check(sc, "live pill shows the run time", page.locator("#hdr-live-text").text_content() == "As of 07:00",
                       page.locator("#hdr-live-text").inner_text())
            self.check(sc, "light on a light device, with a dark switch", page.evaluate("getComputedStyle(document.body).backgroundColor") == "rgb(244, 246, 242)"
                       and page.locator("#theme-btn[aria-label='Switch to dark mode']").count() == 1)
            self.check(sc, "demo banner shown", page.get_by_text("Sample data").count() == 1)
            self.common(page, sc)
            ctx.close()

    def done_undo(self, browser) -> None:
        sc = "done-undo"
        ctx, page = self.open(browser, sc, member="kabir")
        label, title = self.done_row("kabir")
        page.locator(f"section[aria-label='{label}'] .row-hit", has_text=title).first.click()
        self.shot(page, "row-open-380")
        page.locator(f"section[aria-label='{label}'] .row-actions button", has_text="Done").first.click()
        page.wait_for_timeout(120)
        writes = page.evaluate("window.__writes")
        first = writes[0] if writes else {}
        self.check(sc, "first tap creates state/items", first.get("op") == "set" and first.get("path") == "state/items", json.dumps(first)[:160])
        self.check(sc, "row disappears", page.locator(OPEN_LINES).get_by_text(title, exact=True).count() == 0)
        self.check(sc, "Done today lists it", page.locator("section[aria-label='Done today'] .row-title", has_text=title).count() == 1)
        self.check(sc, "toast offers undo", page.locator(".toast button", has_text="Undo").count() == 1)
        self.shot(page, "toast-380")
        page.locator(".toast button", has_text="Undo").click()
        page.wait_for_timeout(120)
        writes = page.evaluate("window.__writes")
        last = writes[-1] if writes else {}
        cleared = all(v.get("done_at") is None for v in (last.get("data", {}).get("items") or {}).values())
        self.check(sc, "undo clears done_at", last.get("op") == "update" and cleared, json.dumps(last)[:160])
        self.check(sc, "row returns after undo", page.locator(OPEN_LINES).get_by_text(title, exact=True).count() == 1)
        self.common(page, sc)
        ctx.close()

    def prep(self, browser) -> None:
        for vp, tag in ((PHONE, "380"), (DESK, "1440")):
            sc = f"prep-{tag}"
            ctx, page = self.open(browser, sc, vp)
            page.locator("button.agenda-row").first.click()
            page.wait_for_timeout(80)
            dlg = page.locator("[role=dialog]")
            self.check(sc, "prep sheet opens", dlg.count() == 1)
            self.check(sc, "three questions shown", dlg.locator("ol li").count() == 3)
            self.check(sc, "open promises shown", dlg.get_by_text("Open promises").count() == 1)
            self.check(sc, "watch line names the other fund", dlg.locator(".watch").count() == 1 and "Bluepeak" in dlg.locator(".watch").inner_text())
            self.check(sc, "the meeting's draft is ready to send from the sheet", dlg.get_by_text("Ready to send").count() == 1 and
                       dlg.locator("a", has_text="Open in Gmail").count() == 1)
            self.check(sc, "focus moves into the sheet", page.evaluate("document.activeElement.closest('[role=dialog]') !== null"))
            self.shot(page, f"prep-{tag}")
            page.keyboard.press("Escape")
            self.check(sc, "Escape closes", page.locator("[role=dialog]").count() == 0)
            ctx.close()

    def tabs(self, browser) -> None:
        for vp, tag in ((PHONE, "380"), (DESK, "1440")):
            for key in ("pipeline", "people", "portfolio", "lps"):
                sc = f"{key}-{tag}"
                ctx, page = self.open(browser, sc, vp)
                page.locator(f"{'#bottom-tabs' if vp == PHONE else '#rail-tabs'} button[aria-label='{ 'LPs' if key == 'lps' else key.capitalize() }']").click()
                page.wait_for_timeout(60)
                self.shot(page, f"{key}-{tag}")
                self.check(sc, "hero card renders", page.locator(".ah-hero-card .statement").count() == 1)
                if key == "portfolio":
                    self.check(sc, "negative growth in breach ink", page.locator("td.neg").count() >= 1)
                    self.check(sc, "true minus used", "−" in page.locator("table").inner_text())
                if key == "pipeline":
                    self.check(sc, "competing deals say Competing", page.locator(".deal-row .status.breach", has_text="Competing").count() >= 1)
                    self.check(sc, "pre-read shown", page.locator("section[aria-label='Partner meeting pre-read']").count() == 1)
                    deals = [d for d in self.snaps["aditi"]["pipeline"]["deals"].values() if d.get("active")]
                    on_pipe = {str(d.get("domain") or "").lower() for d in deals} | {str(d.get("company") or "").lower() for d in deals}
                    want_in = min(6, sum(1 for r in self.snaps["aditi"]["inbound"]["items"].values()
                                         if str(r.get("domain") or "").lower() not in on_pipe and str(r.get("company") or "").lower() not in on_pipe))
                    got_in = page.locator("section[aria-label='Pitches'] .row").count()
                    self.check(sc, "inbound listed with reasons", got_in == want_in and want_in > 0, f"{got_in} of {want_in}")
                    self.check(sc, "filters at this size", page.locator(".chip-filter", has_text="Needs a look").count() == 1)
                    self.check(sc, "early stages fold for a partner", page.locator(".stage-h button[aria-expanded=false]").count() >= 1)
                    self.check(sc, "every active deal is listed", *self._deal_count(page, "aditi"))
                if key == "people":
                    self.check(sc, "relationship table filled", page.locator("tbody tr").count() >= 10)
                if key == "lps":
                    want = len(self.snaps["aditi"]["lps"]["lps"])
                    self.check(sc, "every LP is listed", page.locator("tbody tr").count() == want, f"{page.locator('tbody tr').count()} of {want}")
                    self.check(sc, "re-up window visible", page.locator("th", has_text="Re-up window").is_visible())
                    fund = page.locator("section.fund")
                    self.check(sc, "fund summary: committed, called, unfunded", fund.count() == 1 and all(
                        t in fund.inner_text() for t in ("Fund II", "Committed", "Called", "Unfunded", "45% of commitments")),
                        fund.inner_text().replace("\n", " ")[:120] if fund.count() else "missing")
                    team = page.locator("section.card", has_text="With your team")
                    self.check(sc, "a colleague's LPs listed with their owner", team.count() == 1 and "With Vikram" in team.inner_text())
                    if vp == DESK:
                        self.check(sc, "called, unfunded and owner columns", all(page.locator("th", has_text=t).is_visible()
                                                                                for t in ("Called", "Unfunded", "Owner")))
                if key == "portfolio":
                    self.check(sc, "founder asks shown", page.locator("section[aria-label='Founders need'] .row").count() == 3)
                self.common(page, sc)
                ctx.close()

    def _deal_count(self, page, member: str) -> tuple[bool, str]:
        pdata, me = self.snaps[member]["pipeline"], self.snaps[member]["config"].get("user_email")
        want = sum(1 for d in pdata["deals"].values() if d["active"] and (pdata["scope"] != "own" or d.get("owner") == me))
        for _ in range(10):  # unfold early stages first
            folded = page.locator(".stage-h button[aria-expanded=false]")
            if not folded.count():
                break
            folded.first.click()
        got = page.locator(".deal-row").count()
        return got == want and want > 0, f"{got} of {want}"

    def pipeline_actions(self, browser) -> None:
        sc = "pipeline-actions"
        ctx, page = self.open(browser, sc, DESK)
        page.locator("#rail-tabs button[aria-label='Pipeline']").click()
        hit = page.locator(".deal-row .row-hit").first
        company = hit.locator(".row-title").inner_text()
        hit.click()
        page.locator(".deal-row .field[name=next]").first.fill("Reference calls with three customers")
        page.locator(".deal-row button[type=submit]").first.click()
        page.wait_for_timeout(120)
        w = page.evaluate("window.__writes")
        act = next((x for x in w if x.get("path") == "state/actions"), {})
        items = (act.get("data") or {}).get("items") or {}
        ok = any(v.get("type") == "next_step" and v["payload"]["text"].startswith("Reference") for v in items.values())
        self.check(sc, "next step saved as an approved action", ok, json.dumps(act)[:200])
        self.check(sc, "row shows the pending next step", page.get_by_text("saving to your CRM at the next check").count() >= 1)
        hit = page.locator(".deal-row .row-hit", has_text=company).first
        hit.click()
        page.locator(".deal-row button", has_text="Mark quiet").first.click()
        page.wait_for_timeout(120)
        w = page.evaluate("window.__writes")
        self.check(sc, "quiet saved", any(v.get("type") == "quiet" for x in w if x.get("path") == "state/actions" for v in ((x.get("data") or {}).get("items") or {}).values()))
        self.check(sc, "quiet chip shows", page.locator(".chip-quiet").count() >= 1)
        comp = page.locator(".deal-row", has=page.locator(".status.breach", has_text="Competing")).first
        comp.locator(".row-hit").click()
        comp.locator("button", has_text="Copy for partners").click()
        page.wait_for_timeout(120)
        self.check(sc, "a competing deal copies a line for partners", page.locator(".toast", has_text="Copied for your partners").count() == 1)
        self.shot(page, "pipeline-actions-1440")
        self.common(page, sc)
        ctx.close()

    def approvals(self, browser) -> None:
        sc = "approvals"
        ctx, page = self.open(browser, sc)
        page.locator(DECIDE + " button", has_text="Approve").click()
        page.wait_for_timeout(120)
        w = page.evaluate("window.__writes")
        ok = any(v.get("type") == "crm_update" for x in w if x.get("path") == "state/actions" for v in ((x.get("data") or {}).get("items") or {}).values())
        self.check(sc, "CRM change approved", ok)
        self.check(sc, "approved state shown", page.get_by_text("Approved. ant. saves it to your CRM at the next check.").count() >= 1)
        page.locator(SEND + " button[aria-label='Copy draft']").first.click()
        page.wait_for_timeout(120)
        self.check(sc, "copy gives feedback", page.locator(".toast").count() == 1, page.locator(".toast").inner_text() if page.locator(".toast").count() else "")
        markup = page.locator(SEND + " .row", has_text="term sheet markup")
        href = markup.locator("a", has_text="Open in Gmail").get_attribute("href") if markup.locator("a", has_text="Open in Gmail").count() else ""
        self.check(sc, "a draft kept in Home opens Gmail filled in, in the user's own account",
                   href.startswith("https://mail.google.com/mail/?authuser=aditi%40quillwater.vc&view=cm") and "ishaan%40atlassettle.com" in href
                   and markup.locator(".status", has_text="Ready to send").count() == 1, href[:90])
        self.common(page, sc)
        ctx.close()
        # An introduction goes to both people: the compose link carries the second one in cc.
        snap = json.loads(json.dumps(self.snaps["aditi"]))
        intro = next((k for k, d in snap["drafts"]["items"].items() if "raj" in str(d.get("to_name") or "").lower()), None)
        if intro:
            snap["drafts"]["items"][intro]["cc"] = "raj.malhotra@fablebank.in"
        ctx, page = self.open(browser, "intro-cc", PHONE, snap=snap)
        hrefs = [a.get_attribute("href") or "" for a in page.locator("a", has_text="Open in Gmail").all()]
        self.check("intro-cc", "an intro draft opens Gmail with the second person in cc", any("&cc=raj.malhotra%40fablebank.in" in h_ for h_ in hrefs),
                   f"{len(hrefs)} links")
        ctx.close()
        snap = json.loads(json.dumps(self.snaps["aditi"]))
        snap["proposals"]["items"]["pr_failed"] = {"type": "crm_update", "status": "failed", "title": "next step from the 20 Oct call",
                                                    "record": {"name": "Beacon Credit Rails"}, "reason": "The CRM refused the date format.",
                                                    "applied_at": "2026-10-22T06:55:00+05:30", "source_url": "https://notes.granola.ai/d/tr05"}
        ctx, page = self.open(browser, "failed-apply", PHONE, snap=snap)
        row = page.locator(DECIDE + " .row", has_text="Beacon Credit Rails")
        self.check("failed-apply", "a failed change says so", row.locator(".status", has_text="Failed").count() == 1)
        row.locator("button", has_text="Dismiss").click()
        page.wait_for_timeout(100)
        self.check("failed-apply", "dismiss hides it", page.locator(DECIDE + " .row", has_text="Beacon Credit Rails").count() == 0)
        ctx.close()

    def keyboard(self, browser) -> None:
        sc = "keyboard"
        ctx, page = self.open(browser, sc, DESK)
        page.keyboard.press("j")
        self.check(sc, "j focuses the first line", page.evaluate("document.activeElement.classList.contains('row-hit')"))
        page.keyboard.press("j")
        page.keyboard.press("1")
        page.wait_for_timeout(80)
        w = page.evaluate("window.__writes")
        self.check(sc, "1 rates the line useful", any(x.get("collection") == "ratings" and x["data"]["value"] == "useful" for x in w))
        page.keyboard.press("?")
        self.check(sc, "? opens help", page.locator("[role=dialog]", has_text="How ant. works").count() == 1)
        self.shot(page, "help-1440")
        page.keyboard.press("Escape")
        self.check(sc, "Escape closes help", page.locator("[role=dialog]").count() == 0)
        ctx.close()

    def theme(self, browser) -> None:
        """Home follows the device until the user picks: dark on a dark device, light on a light one. The switch and
        Help change it, and the choice survives a reload."""
        sc = "theme"
        ctx, page = self.open(browser, sc, PHONE, scheme="dark")
        bg = page.evaluate("getComputedStyle(document.body).backgroundColor")
        self.check(sc, "dark on a device set to dark", bg == "rgb(14, 19, 16)", bg)
        page.locator("#theme-btn").click()
        page.wait_for_timeout(60)
        bg = page.evaluate("getComputedStyle(document.body).backgroundColor")
        self.check(sc, "the switch turns on light", bg == "rgb(244, 246, 242)", bg)
        self.check(sc, "the switch says what it does next", page.locator("#theme-btn").get_attribute("aria-label") == "Switch to dark mode")
        page.reload()
        page.wait_for_timeout(250)
        self.check(sc, "the choice survives a reload", page.evaluate("getComputedStyle(document.body).backgroundColor") == "rgb(244, 246, 242)")
        page.locator("#help-btn").click()
        seg = page.locator("[role=dialog] .seg[aria-label='Appearance']")
        self.check(sc, "Help offers device, light and dark", seg.locator("button").count() == 3 and seg.locator("button[aria-pressed=true]").inner_text() == "Light")
        seg.locator("button", has_text="Match my device").click()
        page.wait_for_timeout(60)
        self.check(sc, "Match my device goes back to dark here", page.evaluate("getComputedStyle(document.body).backgroundColor") == "rgb(14, 19, 16)")
        dens = page.locator("[role=dialog] .seg[aria-label='Text size']")
        dens.locator("button", has_text="Compact").click()
        page.wait_for_timeout(60)
        self.check(sc, "Compact makes the text smaller", page.evaluate("getComputedStyle(document.body).fontSize") == "13.5px")
        dens.locator("button", has_text="Comfortable").click()
        page.wait_for_timeout(60)
        self.check(sc, "Comfortable is 15px", page.evaluate("getComputedStyle(document.body).fontSize") == "15px")
        page.keyboard.press("Escape")
        self.common(page, sc)
        ctx.close()
        for vp, tag in ((PHONE, "380"), (DESK, "1440")):
            ctx, page = self.open(browser, f"dark-{tag}", vp, theme="dark")
            self.shot(page, f"dark-{tag}")
            self.common(page, f"dark-{tag}")
            ctx.close()
        for vp, tag in ((PHONE, "320"), (PHONE, "360")):
            width = int(tag)
            ctx, page = self.open(browser, f"narrow-{tag}", {"width": width, "height": 780})
            self.check(f"narrow-{tag}", "header fits with the switch", page.evaluate("document.documentElement.scrollWidth - window.innerWidth") <= 0)
            self.check(f"narrow-{tag}", "switch and help stay on screen", page.evaluate(
                "['theme-btn','help-btn'].every(id => { var r = document.getElementById(id).getBoundingClientRect(); return r.right <= window.innerWidth && r.left >= 0; })"))
            self.shot(page, f"header-{tag}")
            ctx.close()

    # Each state Home can be in, scanned in both themes: what is on screen is measured, not the token table.
    COLOUR_STATES = [
        ("aditi-today", "aditi", PHONE, None), ("aditi-today-desk", "aditi", DESK, None), ("aditi-row-open", "aditi", PHONE, "row"),
        ("aditi-prep", "aditi", PHONE, "prep"), ("aditi-partner-pack", "aditi", PHONE, "partner"), ("aditi-help", "aditi", DESK, "help"),
        ("aditi-toast", "aditi", PHONE, "toast"), ("aditi-pipeline", "aditi", DESK, "pipeline"), ("aditi-deal-open", "aditi", PHONE, "deal"),
        ("aditi-people", "aditi", PHONE, "people"), ("aditi-portfolio", "aditi", DESK, "portfolio"), ("aditi-lps", "aditi", PHONE, "lps"),
        ("kabir-today", "kabir", PHONE, None), ("meera-pipeline", "meera", PHONE, "pipeline"), ("rohan-today", "rohan", PHONE, None),
        ("rohan-pipeline", "rohan", DESK, "pipeline"), ("tara-portfolio", "tara", PHONE, "portfolio"), ("vikram-lps", "vikram", PHONE, "lps"),
        ("vikram-today", "vikram", DESK, None), ("banners", "aditi", PHONE, "banners"), ("friday", "aditi", PHONE, "friday"),
        ("empty", "aditi", PHONE, "empty"), ("hover", "aditi", DESK, "hover"), ("focus", "aditi", DESK, "focus"),
    ]

    def colours(self, browser) -> None:
        report = {"states": [], "fails": []}
        for theme in ("light", "dark"):
            for name, member, vp, action in self.COLOUR_STATES:
                sc = f"colour-{theme}-{name}"
                extra: dict = {}
                when = T0
                if action == "banners":
                    live = json.loads(json.dumps(self.snaps["aditi"]))
                    live["config"]["demo"] = False
                    live["brief"]["unavailable"] = [{"source": "crm", "status": "revoked", "label": "Your CRM", "since": "2026-10-22T07:58:00+05:30"}]
                    extra = {"snap": live, "runs": [{"started": "2026-10-22T07:51:00+05:30", "finished": "2026-10-22T07:58:00+05:30"}]}
                    when = dt.datetime(2026, 10, 22, 13, 30, tzinfo=IST)
                if action == "friday":
                    when = dt.datetime(2026, 10, 23, 9, 0, tzinfo=IST)
                if action == "empty":
                    extra = {"snap": {}}
                ctx, page = self.open(browser, sc, vp, member=member, theme=theme, when=when, **extra)
                tabs = "#bottom-tabs" if vp == PHONE else "#rail-tabs"
                scope = None
                if action in ("pipeline", "people", "portfolio", "lps", "deal"):
                    label = {"lps": "LPs", "deal": "Pipeline"}.get(action, action.capitalize())
                    page.locator(f"{tabs} button[aria-label='{label}']").click()
                    for _ in range(10):
                        folded = page.locator(".stage-h button[aria-expanded=false]")
                        if not folded.count():
                            break
                        folded.first.click()
                    if action == "deal":
                        page.locator(".deal-row .row-hit").first.click()
                elif action is None or action in ("toast", "friday", "focus", "hover"):
                    today_tab = page.locator(f"{tabs} button[aria-label='Today'][aria-selected=false]")
                    if today_tab.count():
                        today_tab.click()
                    if action == "toast":
                        page.locator(".ah-hero-card button", has_text="Done").click()
                        page.wait_for_timeout(120)
                    elif action == "friday":
                        page.locator("#view section.card", has_text="One question").locator("button", has_text="9").first.click()
                    elif action == "focus":
                        page.keyboard.press("j")
                elif action == "row":
                    page.locator("#view .row-hit").first.click()
                elif action == "prep":
                    page.locator("button.agenda-row").first.click()
                    scope = "[role=dialog]"
                elif action == "partner":
                    page.locator("button.agenda-row", has_text="Partner sync").click()
                    scope = "[role=dialog]"
                elif action == "help":
                    page.locator("#help-btn").click()
                    scope = "[role=dialog]"
                page.wait_for_timeout(80)
                res = page.evaluate(SCAN, scope)
                if action == "hover":
                    for sel in (".btn-primary", ".btn-secondary", ".btn-ghost", ".chip-source", "#bottom-tabs .ah-tab, #rail-tabs .ah-tab"):
                        loc = page.locator((f"#view {sel}" if not sel.startswith("#") else sel) + " >> visible=true").first
                        if loc.count():
                            loc.hover()
                            page.wait_for_timeout(120)
                            r2 = page.evaluate(SCAN, None)
                            res["checked"] += r2["checked"]
                            res["fails"] += r2["fails"]
                            res["min"] = min(res["min"], r2["min"])
                report["states"].append({"theme": theme, "state": name, "checked": res["checked"], "marks": res["marks"], "min": res["min"],
                                         "fails": len(res["fails"])})
                for f in res["fails"]:
                    report["fails"].append({"theme": theme, "state": name, **f})
                self.check(sc, "every text and mark meets WCAG contrast", not res["fails"],
                           "; ".join(f"{f['el']} {f['ratio']}:1 < {f['need']}" for f in res["fails"][:3]) or f"{res['checked']} texts, {res['marks']} marks, min {res['min']}:1")
                if name in ("aditi-today", "aditi-prep", "aditi-pipeline", "aditi-partner-pack", "aditi-help", "tara-portfolio", "aditi-row-open"):
                    self.shot(page, f"{theme}-{name}")
                ctx.close()
        with open(os.path.join(self.out, "colours.json"), "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=1)

    def states(self, browser) -> None:
        # Home opens on Today when the day's top item is urgent, and on the level's own tab otherwise.
        for m, tab in (("meera", "Pipeline"), ("vikram", "LPs"), ("tara", "Portfolio")):
            sc = f"{m}-default"
            ctx, page = self.open(browser, sc, PHONE, member=m)
            sel = page.locator("#bottom-tabs button[aria-selected=true]").get_attribute("aria-label")
            self.check(sc, "an overdue hero opens Today", sel == "Today", sel or "")
            ctx.close()
            calm = json.loads(json.dumps(self.snaps[m]))
            calm["brief"]["hero"] = {"kind": "calm", "item_id": None, "kicker": "All clear", "statement": "Nothing needs you", "finding": "ant. keeps watching."}
            ctx, page = self.open(browser, sc + "-calm", PHONE, member=m, snap=calm)
            sel = page.locator("#bottom-tabs button[aria-selected=true]").get_attribute("aria-label")
            self.check(sc + "-calm", f"a calm day opens on {tab}", sel == tab, sel or "")
            if m == "meera":
                self.check(sc + "-calm", "associate sees only her deals", *self._deal_count(page, "meera"))
                self.check(sc + "-calm", "associate has no LPs tab", page.locator("#bottom-tabs button[aria-label='LPs']").count() == 0)
                self.shot(page, "meera-pipeline-380")
            if m == "vikram":
                self.check(sc + "-calm", "CFO has no Pipeline tab", page.locator("#bottom-tabs button[aria-label='Pipeline']").count() == 0)
                self.check(sc + "-calm", "LP money shows on a phone", page.locator("td .sub", has_text="committed").count() >= 1)
                self.check(sc + "-calm", "an unpaid capital call leads the LPs", "capital call" in page.locator(".ah-hero-card").inner_text().lower())
                banyan = page.locator("section.card .row", has_text="Banyan Family Office")
                self.check(sc + "-calm", "a tapped LP note shows Draft ready on its row", banyan.locator(".status", has_text="Draft ready").count() >= 1)
                self.shot(page, "vikram-lps-380")
            if m == "tara":
                first = page.locator("#view section.card").first.get_attribute("aria-label")
                self.check(sc + "-calm", "founder asks come first", first == "Founders need", first or "")
                hero = page.locator(".ah-hero-card .statement").inner_text()
                # The ask that needs her now: with every note still to send, the oldest ask, with its note one tap away.
                opens = page.locator(".ah-hero-card a, .ah-hero-card button", has_text=re.compile(r"Open draft|Open in Gmail|Copy draft")).count()
                self.check(sc + "-calm", "Portfolio leads with the ask that needs her, its note one tap away",
                           hero.startswith("Kestrel Pay") and opens >= 1, f"{hero}; draft buttons {opens}")
                self.shot(page, "tara-portfolio-380")
            self.common(page, sc + "-calm")
            ctx.close()
        live = json.loads(json.dumps(self.snaps["aditi"]))
        live["config"]["demo"] = False
        live["brief"]["unavailable"] = [{"source": "crm", "status": "revoked", "label": "Your CRM", "since": "2026-10-22T07:58:00+05:30"}]
        ctx, page = self.open(browser, "outage", PHONE, snap=live, when=dt.datetime(2026, 10, 22, 13, 30, tzinfo=IST),
                              runs=[{"started": "2026-10-22T07:51:00+05:30", "finished": "2026-10-22T07:58:00+05:30"}])
        self.check("outage", "connector banner", page.locator(".banner.is-warn", has_text="Your CRM: access revoked at Thu 07:58").count() == 1)
        self.check("outage", "stall banner after two quiet hours", page.locator(".banner.is-warn", has_text="has not checked since").count() == 1)
        self.shot(page, "banners-380")
        self.common(page, "outage")
        ctx.close()
        live2 = json.loads(json.dumps(self.snaps["aditi"]))
        live2["config"]["demo"] = False
        for sc, when, runs, late in (
                ("weekend-quiet", dt.datetime(2026, 10, 24, 15, 0, tzinfo=IST),
                 [{"started": "2026-10-24T13:22:00+05:30", "finished": "2026-10-24T13:29:00+05:30", "next_check_at": "2026-10-24T17:22:00+05:30"}], False),
                ("monday-before-first-run", dt.datetime(2026, 10, 26, 6, 10, tzinfo=IST),
                 [{"started": "2026-10-25T17:22:00+05:30", "finished": "2026-10-25T17:31:00+05:30", "next_check_at": "2026-10-26T06:22:00+05:30"}], False),
                ("check-late", dt.datetime(2026, 10, 22, 10, 45, tzinfo=IST),
                 [{"started": "2026-10-22T07:22:00+05:30", "finished": "2026-10-22T07:30:00+05:30", "next_check_at": "2026-10-22T08:22:00+05:30"}], True)):
            ctx, page = self.open(browser, sc, PHONE, snap=live2, when=when, runs=runs)
            shown = page.locator(".banner.is-warn", has_text="has not checked since").count() == 1
            self.check(sc, "stall banner only when the scheduled check is late" if late else "no stall banner while the schedule is quiet", shown == late)
            if late:
                pill, banner = page.locator("#hdr-live-text").inner_text(), page.locator(".banner.is-warn").inner_text()
                self.check(sc, "one last-check time on the page", "07:30" in pill and "07:30" in banner, f"{pill} | {banner[:60]}")
                self.shot(page, "stall-380")
            ctx.close()
        ctx, page = self.open(browser, "db-error", PHONE, dbError=True)
        page.wait_for_timeout(80)
        self.check("db-error", "database error says so", page.get_by_text("could not load its data").count() == 1)
        self.check("db-error", "no false first-brief message", page.get_by_text("Your first brief is on its way").count() == 0)
        ctx.close()
        ctx, page = self.open(browser, "slow", PHONE, never=True)
        page.wait_for_timeout(2800)
        self.check("slow", "slow load keeps the skeleton", page.locator(".skel").count() >= 1 and page.get_by_text("Your first brief is on its way").count() == 0)
        ctx.close()
        ctx, page = self.open(browser, "empty", PHONE, snap={})
        self.check("empty", "first-run state", page.get_by_text("Your first brief is on its way").count() == 1)
        self.shot(page, "empty-380")
        self.common(page, "empty")
        ctx.close()
        ctx, page = self.open(browser, "no-runtime", PHONE, noRuntime=True)
        self.check("no-runtime", "outside Claude message", page.get_by_text("Open ant. Home in the Claude app").count() == 1)
        ctx.close()
        ro = json.loads(json.dumps(self.snaps["kabir"]))
        ro["config"]["demo"] = False
        ctx, page = self.open(browser, "read-only", PHONE, snap=ro, owner=False, readOnlyWrites=True, member="kabir")
        page.wait_for_timeout(80)
        self.check("read-only", "read-only banner", page.get_by_text("It is read-only").count() == 1)
        self.tap_done(page, "kabir")
        self.check("read-only", "tap explains read-only", page.locator(".toast", has_text="Read-only").count() == 1)
        ctx.close()
        # A viewer abroad sees the user's own day and times, the zone the agenda is written in.
        ctx = browser.new_context(viewport=PHONE, timezone_id="America/New_York")
        page = ctx.new_page()
        page.route("**/fonts.g*/**", lambda r: r.abort())
        page.add_init_script("window.__QA__ = " + json.dumps({"snap": self.snaps["aditi"]}) + ";" + MOCK)
        page.clock.set_fixed_time(T0)
        page.goto("file://" + self.wrapper)
        page.wait_for_timeout(250)
        self.check("abroad", "the user's own date and time, wherever the viewer is",
                   page.locator("#hdr-date").inner_text() == "Thu 22 Oct" and page.locator("#hdr-live-text").text_content() == "As of 07:00",
                   page.locator("#hdr-date").inner_text() + " | " + page.locator("#hdr-live-text").text_content())
        ctx.close()
        ctx, page = self.open(browser, "stale-run", PHONE, when=dt.datetime(2026, 10, 22, 11, 30, tzinfo=IST))
        self.check("stale-run", "old run is labelled", page.locator("#hdr-live-text").text_content() == "Last check 07:00" and page.locator("#hdr-live").get_attribute("title") == "Last check 07:00")
        ctx.close()
        ctx, page = self.open(browser, "friday", PHONE, when=dt.datetime(2026, 10, 23, 9, 0, tzinfo=IST))
        card = page.locator("#view section.card", has_text="One question")
        self.check("friday", "Friday score card", card.count() == 1)
        card.locator("button", has_text="9").first.click()
        w = page.evaluate("window.__writes")
        self.check("friday", "score saved", any(x.get("collection") == "ratings" and x["data"]["kind"] == "weekly_score" and x["data"]["value"] == "9" for x in w))
        self.shot(page, "friday-380")
        ctx.close()

    def levels(self, browser) -> None:
        """Today and the opening tab for every level, on a phone: what each person sees first."""
        for m in ("aditi", "kabir", "meera", "rohan", "tara", "vikram", "solo"):
            sc = f"level-{m}"
            ctx, page = self.open(browser, sc, PHONE, member=m)
            self.shot(page, f"level-{m}-open-380")
            if page.locator("#bottom-tabs button[aria-label='Today'][aria-selected=false]").count():
                page.locator("#bottom-tabs button[aria-label='Today']").click()
                page.wait_for_timeout(60)
            self.shot(page, f"level-{m}-today-380")
            hero = page.locator(".ah-hero-card .statement").first.inner_text() if page.locator(".ah-hero-card .statement").count() else ""
            self.check(sc, "hero states a fact", bool(hero) and not hero.split(" ")[0].isdigit(), hero)
            if m == "rohan":
                page.locator("#bottom-tabs button[aria-label='Pipeline']").click()
                page.wait_for_timeout(60)
                first = page.locator(".stage-h b").first.inner_text()
                self.check(sc, "analyst pipeline opens on Mine, top of the funnel first",
                           page.locator(".chip-filter[aria-pressed=true]", has_text="Mine").count() == 1 and first in ("Inbound", "Screening", "First meeting"), first)
                self.shot(page, "level-rohan-pipeline-380")
            self.common(page, sc)
            ctx.close()

    def round6(self, browser) -> None:
        """Round six: a Sheet CRM copies instead of approving, a dead guard says so, an analyst's colleagues are one
        grey line, every founder ask has a path or says none, and the sync pack names lead, partner and round."""
        sheet = json.loads(json.dumps(self.snaps["aditi"]))
        sheet["config"]["crm_system"] = "sheet"
        ctx, page = self.open(browser, "sheet-crm", PHONE, snap=sheet)
        ready = page.locator(DECIDE)
        self.check("sheet-crm", "a Sheet CRM shows Copy change, never Approve", ready.locator("button", has_text="Copy change").count() >= 1 and
                   ready.locator("button", has_text="Approve").count() == 0)
        self.check("sheet-crm", "it says to paste it into the sheet", ready.locator(".status", has_text="Paste into your sheet").count() >= 1)
        ready.locator("button", has_text="Copy change").first.click()
        page.wait_for_timeout(120)
        self.check("sheet-crm", "copying a change confirms it", page.locator(".toast", has_text="Paste it into your sheet").count() == 1)
        w = page.evaluate("window.__writes") or []
        self.check("sheet-crm", "copying writes no approval", not any(x.get("path") == "state/actions" for x in w))
        self.shot(page, "sheet-crm-380")
        self.common(page, "sheet-crm")
        ctx.close()
        live = json.loads(json.dumps(self.snaps["aditi"]))
        live["config"]["demo"] = False
        ctx, page = self.open(browser, "guard-off", PHONE, snap=live, when=dt.datetime(2026, 10, 22, 9, 40, tzinfo=IST),
                              runs=[{"started": "2026-10-22T09:22:00+05:30", "status": "guard_off"},
                                    {"started": "2026-10-22T07:22:00+05:30", "finished": "2026-10-22T07:30:00+05:30", "next_check_at": "2026-10-22T08:22:00+05:30"}])
        banner = page.locator(".banner.is-warn", has_text="safety guard did not load")
        self.check("guard-off", "a check that found its guard off says so", banner.count() == 1, banner.inner_text()[:80] if banner.count() else "")
        self.check("guard-off", "no stall banner on top of it", page.locator(".banner.is-warn", has_text="has not checked since").count() == 0)
        self.shot(page, "guard-off-380")
        self.common(page, "guard-off")
        ctx.close()
        ctx, page = self.open(browser, "analyst-team", PHONE, member="rohan")
        page.locator("#bottom-tabs button[aria-label='Today']").click()
        page.wait_for_timeout(100)
        team = page.locator("section[aria-label='Watch'] .row")
        self.check("analyst-team", "colleagues' races are one grey line at the end", team.count() == 1 and
                   team.locator(".status", has_text="Your team").count() == 1, str(team.count()))
        self.check("analyst-team", "no urgent row names a colleague's lead", page.locator("#view .row", has_text=" leads)").count() == 0)
        self.common(page, "analyst-team")
        ctx.close()
        ctx, page = self.open(browser, "asks", PHONE, member="tara")
        page.locator("#bottom-tabs button[aria-label='Portfolio']").click()
        page.wait_for_timeout(100)
        card = page.locator("section[aria-label='Founders need']")
        rows = card.locator(".row")
        n = rows.count()
        said = sum(1 for i in range(n) if "Warm path" in rows.nth(i).inner_text() or "No warm path found" in rows.nth(i).inner_text())
        self.check("asks", "every founder ask names a warm path or says none was found", n >= 1 and said == n, f"{said} of {n}")
        nopath = card.locator(".row", has_text="No warm path found").first
        if nopath.count():
            nopath.locator(".row-hit").click()
            page.wait_for_timeout(80)
        # Round seven: the note to the team is drafted without a tap; the button stays for an ask that has none yet.
        self.check("asks", "an ask with no path has a note to the team, ready or one tap away",
                   card.locator("button", has_text="Draft a note to your team").count() >= 1 or
                   (nopath.count() and nopath.locator(".status", has_text="Draft ready").count() >= 1))
        self.common(page, "asks")
        ctx.close()
        ctx, page = self.open(browser, "sync-pack", PHONE)
        sync = page.locator("button[aria-label^='Prep for 12:00 Partner sync']")
        opened = False
        if sync.count():
            sync.first.click()
            page.wait_for_timeout(150)
            opened = page.get_by_text("To decide").count() >= 1
        facts = page.locator(".pack-facts")
        self.check("sync-pack", "pack rows name lead, partner, round and amount", opened and facts.count() >= 3 and
                   all("Lead:" in facts.nth(i).inner_text() and "$" in facts.nth(i).inner_text() for i in range(facts.count())),
                   facts.first.inner_text() if facts.count() else "no pack")
        # Stalled deals are their own list after the decisions, never ranked among them.
        card = next((c for c in self.snaps["aditi"]["prep"]["cards"].values() if c.get("kind") == "partner"), {})
        n_stalled = sum(1 for r in card.get("decisions") or [] if r.get("kind") == "stalled")
        heads = [page.locator(".kv h3").nth(i).inner_text() for i in range(page.locator(".kv h3").count())]
        stalled_box = page.locator(".kv", has=page.locator("h3", has_text="Stalled"))
        self.check("sync-pack", "stalled deals sit in their own list after To decide",
                   n_stalled >= 1 and "Stalled" in heads and heads.index("Stalled") == heads.index("To decide") + 1 and
                   stalled_box.locator("li").count() == n_stalled and stalled_box.locator(".status.breach").count() == 0, " / ".join(heads))
        self.common(page, "sync-pack")
        ctx.close()
        # A founder waiting on a reply: the row says so, with the answer drafted; the pipeline row says who and since when.
        ctx, page = self.open(browser, "waiting-founder", PHONE, member="meera")
        page.locator("#bottom-tabs button[aria-label='Today']").click()
        page.wait_for_timeout(100)
        row = page.locator("#view .row", has_text="Copperleaf Collect").first
        # The reply leaves the timeline for her to give: the chip says so, never only "Reply ready".
        self.check("waiting-founder", "the row says Waiting on you, with the reply drafted and the line she must fill",
                   row.count() == 1 and row.locator(".status", has_text="Waiting on you").count() == 1 and
                   row.locator(".status", has_text="Fill in 1 line").count() == 1, row.inner_text()[:120] if row.count() else "no row")
        self.check("waiting-founder", "it quotes the founder's own question", "what would the timeline look like?" in (row.inner_text() if row.count() else ""))
        page.locator("#bottom-tabs button[aria-label='Pipeline']").click()
        page.wait_for_timeout(100)
        prow = page.locator("#view .row", has_text="Copperleaf Collect").first
        self.check("waiting-founder", "the pipeline row says who waits and since when",
                   prow.count() == 1 and "Debashish asked on 13 Oct, no reply yet" in prow.inner_text() and
                   prow.locator(".status", has_text="Waiting on you").count() == 1, prow.inner_text()[:120] if prow.count() else "no row")
        self.shot(page, "waiting-founder-380")
        self.common(page, "waiting-founder")
        ctx.close()

    def round7(self, browser) -> None:
        """Round seven: a founder meeting logs in one tap; an ask's note is ready without a tap and shows as requested
        once sent; a waiting draft's times never sit in the past."""
        snap = self.snaps["meera"]
        prompt = next((p for p in (snap["pipeline"].get("met_prompts") or []) if p["company"] == "Halo Reconcile"), None)
        ctx, page = self.open(browser, "met-log", PHONE, member="meera")
        ready = page.locator(DECIDE)
        row = ready.locator(".row", has_text="Halo Reconcile: met")
        self.check("met-log", "a founder meeting on your deal offers a one-tap log", prompt is not None and row.count() == 1,
                   row.first.inner_text()[:100] if row.count() else "no row")
        if row.count():
            box = row.first.locator("input[name=next]")
            box.fill("Diligence plan with the CFO")
            sel = row.first.locator("select[name=stage]")
            if sel.count():
                sel.select_option(index=1)
            row.first.locator("button[type=submit]").click()
            page.wait_for_timeout(150)
            w = page.evaluate("window.__writes") or []
            acts = [v for x in w if x.get("path") == "state/actions" for v in ((x.get("data") or {}).get("items") or {}).values()]
            ns = next((v for v in acts if v.get("type") == "next_step"), {})
            pay = ns.get("payload") or {}
            self.check("met-log", "saving logs the step, the meeting date and the stage", pay.get("text") == "Diligence plan with the CFO" and
                       pay.get("met") == (prompt or {}).get("met_on") and bool(pay.get("stage")), json.dumps(pay)[:160])
        self.shot(page, "met-log-380")
        self.common(page, "met-log")
        ctx.close()
        tsnap = self.snaps["tara"]
        asks = [a for a in ((tsnap.get("asks") or {}).get("items") or {}).values() if a.get("status") != "done"]
        drafts = ((tsnap.get("drafts") or {}).get("items")) or {}
        noted = {a_ for d in drafts.values() for a_ in [d.get("action_id")] + list(d.get("action_ids") or []) if a_}
        nimbus = next((a for a in asks if a.get("company") == "Nimbus Collect"), {})
        did = next((k for k, d in drafts.items() if nimbus.get("item_id") in [d.get("action_id")] + list(d.get("action_ids") or [])), None)
        self.check("asks-ready", "every open ask has a note ready without a tap", bool(asks) and {a["item_id"] for a in asks} <= noted,
                   f"{len({a['item_id'] for a in asks} & noted)} of {len(asks)}")
        ctx, page = self.open(browser, "ask-requested", PHONE, member="tara", state={"items": {did: {"done_at": "2026-10-22T09:00:00+05:30"}}} if did else {})
        page.locator("#bottom-tabs button[aria-label='Portfolio']").click()
        page.wait_for_timeout(120)
        row = page.locator("section[aria-label='Founders need'] .row", has_text="Nimbus Collect").first
        # The row says who was asked and when: the colleague who knows the contact, the board partner, the team or the contact.
        self.check("ask-requested", "a sent note moves the ask on and says who was asked", bool(did) and row.count() == 1 and
                   row.locator(".status", has_text=re.compile(r"^(Asked Aditi for the intro|Asked Aditi|Asked the team|Intro requested)$")).count() == 1 and
                   "on 22 Oct" in row.inner_text(), row.inner_text()[:100] if row.count() else "no row")
        self.common(page, "ask-requested")
        ctx.close()
        from datetime import datetime as _dt
        past = [f"{m}: {d.get('to_name')}" for m, sn in self.snaps.items() for d in ((sn.get("drafts") or {}).get("items") or {}).values()
                for x in d.get("slots") or [] if _dt.fromisoformat(x) <= T0]
        self.check("draft-times", "no draft in any demo Home offers a time already past", not past, "; ".join(past[:3]))

    def round8(self, browser) -> None:
        """Round eight: the met log fills in from the meeting and saves in one tap; a team note opens Gmail to the whole
        team; an ask asks for a nudge after five quiet working days; a solo GP is never offered a note to a team."""
        import copy as _copy
        snap = _copy.deepcopy(self.snaps["meera"])
        prompts = snap["pipeline"].get("met_prompts") or []
        halo = next((p for p in prompts if p["company"] == "Halo Reconcile"), None)
        if halo:  # the evening after the second meeting: the invite names the stage, and the CRM's step was that meeting
            halo.update({"meeting": "Halo Reconcile: second meeting", "met_on": "2026-10-22", "prefill": "", "prefill_due": "",
                         "implied_stage": {"key": "second_meeting", "name": "Second meeting"}, "step_was_meeting": True,
                         "aid": f"ns_{halo['deal_id']}_2026-10-22"})
        ctx, page = self.open(browser, "met-prefill", PHONE, member="meera", snap=snap)
        row = page.locator(DECIDE + " .row", has_text="Halo Reconcile: met").first
        sel = row.locator("select[name=stage]") if row.count() else None
        chosen = sel.evaluate("s => s.options[s.selectedIndex].text") if sel is not None and sel.count() else ""
        empty = row.locator("input[name=next]").input_value() == "" if row.count() else False
        self.check("met-prefill", "the met log fills in from the meeting: the stage the invite names, no stale step",
                   bool(halo) and chosen == "Move to Second meeting" and empty and "which was this meeting" in (row.inner_text() if row.count() else ""),
                   f"{chosen}; empty step {empty}")
        if row.count():
            row.locator("button[type=submit]").click()
            page.wait_for_timeout(150)
        w = page.evaluate("window.__writes") or []
        acts = [v for x in w if x.get("path") == "state/actions" for v in ((x.get("data") or {}).get("items") or {}).values()]
        pay = (next((v for v in acts if v.get("type") == "next_step"), {}) or {}).get("payload") or {}
        ns_ids = [k for x in w if x.get("path") == "state/actions" for k, v in ((x.get("data") or {}).get("items") or {}).items()
                  if v.get("type") == "next_step"]
        self.check("met-prefill", "one tap saves the meeting and the stage, and clears the step that was this meeting",
                   pay.get("met") == "2026-10-22" and pay.get("stage") == "Second meeting" and pay.get("text") is None and
                   pay.get("clear_step") is True and ns_ids == [f"ns_{(halo or {}).get('deal_id')}_2026-10-22"], json.dumps(pay)[:160] + f" {ns_ids}")
        self.common(page, "met-prefill")
        ctx.close()
        tsnap = _copy.deepcopy(self.snaps["tara"])
        asks = [a for a in ((tsnap.get("asks") or {}).get("items") or {}).values() if a.get("status") != "done"]
        nimbus = next((a for a in asks if a.get("company") == "Nimbus Collect"), {})
        tsnap.setdefault("drafts", {}).setdefault("items", {})["dr_team_qa"] = {
            "to": "aditi@quillwater.vc, kabir@quillwater.vc", "to_name": "Aditi and Kabir", "subject": "Can anyone help Nimbus Collect?",
            "body": "Hi all,\n\nWho knows someone at a bank who fits?\n\nTara", "note_kind": "team", "source_label": "Email",
            "source_url": "https://mail.google.com/mail/u/0/#all/th0343", "in_gmail": False}
        ctx, page = self.open(browser, "team-note", PHONE, member="tara", snap=tsnap)
        drow = page.locator(SEND + " .row", has_text="Can anyone help Nimbus Collect?").first
        href = drow.locator("a", has_text="Open in Gmail").get_attribute("href") if drow.count() and drow.locator("a", has_text="Open in Gmail").count() else ""
        self.check("team-note", "a team note opens Gmail addressed to every colleague on it",
                   "to=aditi%40quillwater.vc%2Ckabir%40quillwater.vc" in str(href), str(href)[:120])
        self.common(page, "team-note")
        ctx.close()
        did = next((k for k, d in ((tsnap.get("drafts") or {}).get("items") or {}).items()
                    if nimbus.get("item_id") in [d.get("action_id")] + list(d.get("action_ids") or [])), None)
        late = dt.datetime(2026, 10, 30, 9, 0, tzinfo=IST)
        ctx, page = self.open(browser, "ask-nudge", PHONE, when=late, member="tara",
                              state={"items": {did: {"done_at": "2026-10-22T09:00:00+05:30"}}} if did else {})
        page.locator("#bottom-tabs button[aria-label='Portfolio']").click()
        page.wait_for_timeout(120)
        arow = page.locator("section[aria-label='Founders need'] .row", has_text="Nimbus Collect").first
        self.check("ask-nudge", "five working days after the note with no reply, the ask asks for a nudge",
                   bool(did) and arow.count() == 1 and arow.locator(".status", has_text="Nudge").count() == 1 and
                   "no reply in 6 working days" in arow.inner_text(), arow.inner_text()[:120] if arow.count() else "no row")
        self.common(page, "ask-nudge")
        ctx.close()
        ssnap = self.snaps["solo"]
        lone = [it for sec in ssnap["brief"]["sections"] for it in sec["items"] if it["kind"] == "ask" and not (it.get("entity") or {}).get("paths")]
        ctx, page = self.open(browser, "solo-asks", PHONE, member="solo")
        offered = []
        for it in lone:
            r_ = page.locator("#view .row", has_text=it["title"][:40]).first
            if r_.count():
                r_.locator(".row-hit").first.click()
                page.wait_for_timeout(60)
                if r_.locator("button", has_text=re.compile(r"note to your team|Draft a note")).count():
                    offered.append(it["title"][:40])
        text = page.locator("#view").inner_text()
        self.check("solo-asks", "a solo GP is offered no note to a team, and Today has no team words",
                   not offered and not re.search(r"Hi all|Your team|board partner|ask your team", text), "; ".join(offered[:2]))
        self.common(page, "solo-asks")
        ctx.close()

    def round9(self, browser) -> None:
        """Round nine: a met log saved with no step asks for the step alone; after a board note, "Yes, ask the team" has
        its own tap and its note shows as ready on the row; a solo GP's Pipeline shows no owner initials or partner."""
        import copy as _copy
        snap = _copy.deepcopy(self.snaps["meera"])
        prompts = snap["pipeline"].get("met_prompts") or []
        halo = next((p for p in prompts if p["company"] == "Halo Reconcile"), None)
        aid = f"nss_{(halo or {}).get('deal_id')}_2026-10-22"
        if halo:  # Thursday's log went to the CRM with no step: Friday's Today asks for the step alone
            snap["pipeline"]["met_prompts"] = [{"deal_id": halo["deal_id"], "company": "Halo Reconcile", "met_on": "2026-10-22", "step_only": True,
                                                "aid": aid, "next_step": None, "next_step_due": None, "stage": "Second meeting",
                                                "stage_key": "second_meeting", "source_url": halo.get("source_url")}] + \
                [p for p in prompts if p is not halo]
        ctx, page = self.open(browser, "met-step", PHONE, member="meera", snap=snap)
        row = page.locator(DECIDE + " .row", has_text="Halo Reconcile: met 22 Oct, add the next step").first
        shown = row.count() == 1 and row.locator("select[name=stage]").count() == 0
        blank_saved = True
        if row.count():  # what the user sees before Save
            row.scroll_into_view_if_needed()
            self.shot(page, "met-step-380")
        if row.count():
            row.locator("button[type=submit]").click()
            page.wait_for_timeout(100)
            blank_saved = any(x.get("path") == "state/actions" for x in (page.evaluate("window.__writes") or []))
            row.locator("input[name=next]").fill("Diligence plan with the CFO")
            row.locator("button[type=submit]").click()
            page.wait_for_timeout(150)
        acts = {k: v for x in (page.evaluate("window.__writes") or []) if x.get("path") == "state/actions"
                for k, v in ((x.get("data") or {}).get("items") or {}).items()}
        pay = (acts.get(aid) or {}).get("payload") or {}
        self.check("met-step", "a log saved with no step asks for the step alone, never saves it blank, and saves it under its own tap",
                   bool(halo) and shown and not blank_saved and pay.get("text") == "Diligence plan with the CFO" and not pay.get("met") and
                   not pay.get("stage"), f"shown {shown}; blank saved {blank_saved}; {json.dumps(pay)[:120]}")
        self.common(page, "met-step")
        ctx.close()
        tsnap = _copy.deepcopy(self.snaps["tara"])
        asks = ((tsnap.get("asks") or {}).get("items")) or {}
        orbit = next((a for a in asks.values() if a.get("company") == "Orbit Treasury"), {})
        drafts = ((tsnap.get("drafts") or {}).get("items")) or {}
        note = next((k for k, d in drafts.items() if orbit.get("item_id") in [d.get("action_id")] + list(d.get("action_ids") or [])), None)
        sent = {"items": {note: {"done_at": "2026-10-22T10:00:00+05:30"}}} if note else {}
        ctx, page = self.open(browser, "ask-team", PHONE, member="tara", state=sent)
        page.locator("#bottom-tabs button[aria-label='Portfolio']").click()
        page.wait_for_timeout(120)
        row = page.locator("section[aria-label='Founders need'] .row", has_text="Orbit Treasury").first
        offered, first_again = False, True
        if row.count():
            row.locator(".row-hit").first.click()
            page.wait_for_timeout(80)
            offered = row.locator("button", has_text="Aditi said yes: ask the team").count() == 1
            first_again = row.locator("button", has_text=re.compile(r"Draft the intro ask|Draft a note to your team")).count() > 0
            if offered:
                row.locator("button", has_text="Aditi said yes: ask the team").click()
                page.wait_for_timeout(150)
        acts = {k: v for x in (page.evaluate("window.__writes") or []) if x.get("path") == "state/actions"
                for k, v in ((x.get("data") or {}).get("items") or {}).items()}
        tap = acts.get(f"{orbit.get('item_id')}_team") or {}
        self.check("ask-team", "after the board note, 'Aditi said yes: ask the team' is a new tap with its own id, never the first note again",
                   bool(note) and offered and not first_again and tap.get("type") == "draft" and (tap.get("payload") or {}).get("note_kind") == "team" and
                   ((tap.get("payload") or {}).get("after") or {}).get("kind") == "board",
                   f"offered {offered}; first note again {first_again}; tap {sorted(acts)[:3]}")
        self.common(page, "ask-team")
        ctx.close()
        tsnap["drafts"]["items"][f"dr_{orbit.get('item_id')}_team"] = {
            "to": "kabir@quillwater.vc, meera@quillwater.vc", "to_name": "Kabir and Meera", "subject": "Can anyone help Orbit Treasury?",
            "body": "Hi all,\n\nAditi agreed we help Orbit hire. Who knows a senior engineer?\n\nTara", "action_id": f"{orbit.get('item_id')}_team",
            "note_kind": "team", "source_label": "Founder update", "source_url": "https://mail.google.com/mail/u/0/#all/th0400", "in_gmail": False}
        ctx, page = self.open(browser, "ask-team-ready", PHONE, member="tara", snap=tsnap, state=sent)
        page.locator("#bottom-tabs button[aria-label='Portfolio']").click()
        page.wait_for_timeout(120)
        row = page.locator("section[aria-label='Founders need'] .row", has_text="Orbit Treasury").first
        # The status names the note ("Team note ready"); a "Draft ready" chip beside it would say the same thing twice.
        self.check("ask-team-ready", "the team note shows as ready on the ask's row, said once", row.count() == 1 and
                   row.locator(".status", has_text=re.compile(r"(Team note|Draft) ready")).count() == 1, row.inner_text()[:120] if row.count() else "no row")
        self.common(page, "ask-team-ready")
        ctx.close()
        ctx, page = self.open(browser, "solo-pipeline", PHONE, member="solo")
        page.locator("#bottom-tabs button[aria-label='Pipeline']").click()
        page.wait_for_timeout(150)
        metas = page.locator("#view .row .row-meta .status").all_inner_texts()
        bad = [t for t in metas if re.search(r"^[A-Z]{2}(?: \u00b7|$)|Partner: ", t)]
        self.check("solo-pipeline", "a solo GP's Pipeline shows no owner initials and no partner", bool(metas) and not bad, "; ".join(bad[:3]))
        self.common(page, "solo-pipeline")
        ctx.close()

    def _replay_home(self, member: str, end: dt.datetime, hooks: list | None = None) -> tuple[dict, dict]:
        """The Home a windowed replay left: its snapshots, and its state as the page holds it."""
        import replay  # noqa: E402
        w = replay._replay_windowed(member, end, hooks)
        st = w["home"].get("state") or {}
        return w["home"]["snap"], {k: ((st.get(k) or {}).get("items") or {}) for k in ("items", "actions")}

    def round10(self, browser) -> None:
        """Round ten: asks that went out in one note get one nudge row on Today, with its draft and its note; each ask
        keeps its own row on Portfolio; the board partner's yes is an explicit tap; after a follow-up note is sent no row
        says "Draft coming"; a draft with blanks says how many lines to fill and what to check."""
        import replay  # noqa: E402
        thu29 = dt.datetime(2026, 10, 29, 7, 30, tzinfo=IST)
        snap, state = self._replay_home("tara", dt.datetime(2026, 10, 29, 6, 30, tzinfo=IST),
                                        [(dt.datetime(2026, 10, 22, 6, 0, tzinfo=IST), replay._intro_email),
                                         (dt.datetime(2026, 10, 22, 10, 0, tzinfo=IST), replay._sent_it("2026-10-22T10:00:00+05:30"))])
        ctx, page = self.open(browser, "nudge-group", PHONE, when=thu29, member="tara", snap=snap, state=state)
        page.locator("#bottom-tabs button[aria-label='Today']").click()
        page.wait_for_timeout(120)
        view = page.locator("#view")
        grp = view.locator(".row", has_text="founder asks wait on Aditi").first
        singles = view.locator(".row-title", has_text=re.compile(r"^(Orbit Treasury|Kestrel Pay):")).count()
        opened = ""
        if grp.count():
            grp.locator(".row-hit").first.click()
            page.wait_for_timeout(80)
            opened = grp.inner_text()
        self.check("nudge-group", "one row on Today for one note's nudge, with its draft, its note and a way to each ask",
                   grp.count() == 1 and singles == 0 and "Open in Gmail" in opened and "See each ask" in opened and
                   "Before you send" in opened and "Orbit Treasury" in opened and "Kestrel Pay" in opened,
                   f"group {grp.count()}; singles {singles}; {opened[:160]}")
        self.shot(page, "nudge-group-380")
        page.locator("#bottom-tabs button[aria-label='Portfolio']").click()
        page.wait_for_timeout(120)
        rows = {co: page.locator("section[aria-label='Founders need'] .row", has_text=co).first for co in ("Orbit Treasury", "Kestrel Pay")}
        ready = all(r.count() and r.locator(".status", has_text="Nudge ready").count() == 1 for r in rows.values())
        orbit = rows["Orbit Treasury"]
        yes_btn, plain = 0, 0
        if orbit.count():
            orbit.locator(".row-hit").first.click()
            page.wait_for_timeout(80)
            yes_btn = orbit.locator("button", has_text="Aditi said yes: ask the team").count()
            plain = orbit.locator("button", has_text=re.compile(r"^Yes, ask the team$")).count()
        self.check("nudge-group", "Portfolio keeps each ask's row, each with the nudge ready; the partner's yes is an explicit tap",
                   ready and yes_btn == 1 and plain == 0, f"ready {ready}; said-yes {yes_btn}; plain {plain}")
        self.common(page, "nudge-group")
        ctx.close()
        # The nudge marked sent: each ask says who was nudged, and no row offers a draft that is gone.
        nudge = next((k for k, d in ((snap.get("drafts") or {}).get("items") or {}).items() if d.get("note_kind") == "nudge"), None)
        st2 = json.loads(json.dumps(state))
        if nudge:
            st2.setdefault("items", {})[nudge] = {"done_at": "2026-10-29T10:00:00+05:30"}
        ctx, page = self.open(browser, "nudge-sent", PHONE, when=dt.datetime(2026, 10, 29, 11, 0, tzinfo=IST), member="tara", snap=snap, state=st2)
        page.locator("#bottom-tabs button[aria-label='Portfolio']").click()
        page.wait_for_timeout(120)
        txt = page.locator("section[aria-label='Founders need']").inner_text() if page.locator("section[aria-label='Founders need']").count() else ""
        self.check("nudge-sent", "once the nudge is sent, each ask says who was nudged and when",
                   bool(nudge) and txt.count("Nudged Aditi on 29 Oct") >= 2 and "Nudge ready" not in txt, txt[:160])
        self.common(page, "nudge-sent")
        ctx.close()
        # "Ask the team instead" on Nimbus, its note written and sent: no row on any tab says "Draft coming".
        import copy as _copy
        tsnap = _copy.deepcopy(self.snaps["tara"])
        asks = ((tsnap.get("asks") or {}).get("items")) or {}
        nim = next((a for a in asks.values() if a.get("company") == "Nimbus Collect"), {})
        drafts = ((tsnap.get("drafts") or {}).get("items")) or {}
        first = next((k for k, d in drafts.items() if nim.get("item_id") in [d.get("action_id")] + list(d.get("action_ids") or [])), None)
        tap = f"{nim.get('item_id')}_team"
        drafts[f"dr_{tap}"] = {"to": "kabir@quillwater.vc, meera@quillwater.vc", "to_name": "Kabir and Meera", "subject": "Can anyone help Nimbus Collect?",
                               "body": "Hi all,\n\nDivya at Nimbus Collect needs two banks as customers. Who knows someone?\n\nTara",
                               "action_id": tap, "note_kind": "team", "source_label": "Founder update",
                               "source_url": "https://mail.google.com/mail/u/0/#all/th0343", "in_gmail": False}
        st3 = {"items": {**({first: {"done_at": "2026-10-22T10:00:00+05:30"}} if first else {}), f"dr_{tap}": {"done_at": "2026-10-29T15:00:00+05:30"}},
               "actions": {tap: {"type": "draft", "status": "approved", "at": "2026-10-29T10:00:00+05:30",
                                 "payload": {"kind": "ask", "note_kind": "team", "next_of": nim.get("item_id"),
                                             "after": {"kind": "colleague", "to_name": "Aditi Rao", "at": "2026-10-22T10:00:00+05:30"}}}}}
        ctx, page = self.open(browser, "no-draft-coming", PHONE, when=dt.datetime(2026, 10, 30, 9, 0, tzinfo=IST), member="tara", snap=tsnap, state=st3)
        seen = []
        for tab in ("Today", "Portfolio"):
            b = page.locator(f"#bottom-tabs button[aria-label='{tab}']")
            if b.count():
                b.click()
                page.wait_for_timeout(120)
                for r_ in page.locator("#view .row").all():
                    if r_.locator(".row-hit").count():
                        r_.locator(".row-hit").first.click()
                        page.wait_for_timeout(30)
                seen.append(page.locator("#view").inner_text())
        nim_txt = page.locator("section[aria-label='Founders need'] .row", has_text="Nimbus Collect").first
        self.check("no-draft-coming", "after the follow-up team note is sent, no row on any tab says 'Draft coming'",
                   bool(first) and not any("Draft coming" in t for t in seen) and nim_txt.count() and "Asked the team" in nim_txt.inner_text(),
                   (nim_txt.inner_text()[:120] if nim_txt.count() else "no Nimbus row"))
        self.common(page, "no-draft-coming")
        ctx.close()
        # A draft with blanks: Meera's Friday Home says how many lines to fill, and what to check, on the row itself.
        msnap, mstate = self._replay_home("meera", dt.datetime(2026, 10, 23, 6, 30, tzinfo=IST))
        ctx, page = self.open(browser, "draft-gaps", PHONE, when=dt.datetime(2026, 10, 23, 8, 0, tzinfo=IST), member="meera", snap=msnap, state=mstate)
        row = page.locator("#view .row", has_text="Share feedback after the partner meeting").first
        chip = row.locator(".status", has_text="Fill in 3 lines").count() if row.count() else 0
        note = ""
        if row.count():
            row.locator(".row-hit").first.click()
            page.wait_for_timeout(80)
            note = row.locator(".draft-note").inner_text() if row.locator(".draft-note").count() else ""
        self.check("draft-gaps", "a draft with blanks says how many lines to fill, and its note names who holds the firm's view",
                   chip == 1 and "Fill in the 3 lines" in note and "Aditi" in note, f"chip {chip}; note {note[:140]}")
        self.shot(page, "draft-gaps-380")
        self.common(page, "draft-gaps")
        ctx.close()

    def _writes(self, page) -> dict:
        """What the page wrote to state/items in this context, merged: {id: fields}."""
        out: dict = {}
        for w in page.evaluate("window.__writes") or []:
            if w.get("path") == "state/items":
                out.update((w.get("data") or {}).get("items") or {})
        return out

    def round11(self, browser) -> None:
        """Round eleven: "Sent it" wherever a draft shows, writing the draft's id (and the promise's, never an ask's);
        "Close ask"; the hero and the Portfolio hero step aside when done; a pushed hero opens Today; a reply in mail
        stops the nudge; the prep sheet says what to check; an answered tap never reads "Draft coming"; a step saved
        again is saving; old met logs fold."""
        import copy as _copy
        import replay  # noqa: E402
        # 1. Vikram's hero is a promise with a draft: Open draft, Sent it, Done; Sent it closes the promise too.
        v = self.snaps["vikram"]
        vh = v["brief"]["hero"]
        ctx, page = self.open(browser, "hero-sent", PHONE, member="vikram")
        page.locator("#bottom-tabs button[aria-label='Today']").click()
        page.wait_for_timeout(120)
        btns = page.locator(".ah-hero-card .hero-actions .btn").all_inner_texts()
        page.locator(".ah-hero-card .hero-actions button", has_text="Sent it").first.click()
        page.wait_for_timeout(150)
        wr = self._writes(page)
        after = page.locator(".ah-hero-card .statement").inner_text()
        keys = {vh.get("draft"), vh.get("commitment_id"), vh.get("item_id")}
        self.check("hero-sent", "a promise hero with a draft offers Open draft, Sent it and Done; Sent it marks the draft and the promise",
                   any("draft" in b.lower() or "gmail" in b.lower() for b in btns) and "Sent it" in btns and "Done" in btns and len(btns) <= 3 and
                   keys <= set(wr) and all(wr[k].get("done_at") for k in keys),
                   f"buttons {btns}; wrote {sorted(wr)}")
        self.check("hero-sent", "once sent, the next line steps up as the hero", after != vh["statement"] and after != "Nothing urgent right now", after)
        self.common(page, "hero-sent")
        ctx.close()
        # 2. A capital-call row's Sent it marks only its draft: the call stays until it is paid.
        ctx, page = self.open(browser, "row-sent", PHONE, member="vikram")
        page.locator("#bottom-tabs button[aria-label='Today']").click()
        page.wait_for_timeout(120)
        row = page.locator("#view .row", has_text="Peregrine Trust owes").first
        row.locator(".row-hit").first.click()
        page.wait_for_timeout(60)
        row.locator("button", has_text="Sent it").first.click()
        page.wait_for_timeout(150)
        wr = self._writes(page)
        self.check("row-sent", "Sent it on a row marks its draft, and only its draft, sent", set(wr) == {"dr_l_cbd6326c5a"} and
                   wr["dr_l_cbd6326c5a"].get("done_at"), f"wrote {sorted(wr)}")
        ctx.close()
        # 3. Aditi's hero has no draft: Done steps the next line up, never "Nothing urgent right now" above it.
        a = self.snaps["aditi"]
        first_row = a["brief"]["sections"][0]["items"][0]["title"]
        ctx, page = self.open(browser, "hero-done", PHONE)
        page.locator(".ah-hero-card .hero-actions button", has_text="Done").first.click()
        page.wait_for_timeout(150)
        st = page.locator(".ah-hero-card .statement").inner_text()
        dup = page.locator(OPEN_LINES + " .row-title", has_text=first_row).count()
        self.check("hero-done", "Done on the hero steps the next line up, and it leaves the list", st == first_row and dup == 0, f"{st}; listed {dup}")
        self.shot(page, "hero-done-380")
        self.common(page, "hero-done")
        ctx.close()
        # 4. Tara: a pushed hero opens Today, though she starts on Portfolio; ask rows close with "Close ask", and the
        # Portfolio hero moves on when its ask is closed.
        t = self.snaps["tara"]
        ctx, page = self.open(browser, "close-ask", PHONE, member="tara")
        today_sel = page.locator("#bottom-tabs button[aria-label='Today'][aria-selected='true']").count()
        self.check("close-ask", "the hero a push named today opens Home on Today", today_sel == 1 and t["brief"]["hero"].get("pushed"), str(today_sel))
        page.locator("#bottom-tabs button[aria-label='Portfolio']").click()
        page.wait_for_timeout(120)
        hero0 = page.locator(".ah-hero-card .statement").inner_text()
        co0 = hero0.split(":")[0]
        # By its title: a row's detail can name other companies (one note carried three asks).
        row = page.locator("section[aria-label='Founders need'] .row").filter(
            has=page.locator(".row-title", has_text=re.compile("^" + re.escape(co0) + ":"))).first
        row.locator(".row-hit").first.click()
        page.wait_for_timeout(60)
        labels = row.locator(".row-actions button").all_inner_texts()
        row.locator("button", has_text="Close ask").first.click()
        page.wait_for_timeout(150)
        wr = self._writes(page)
        hero1 = page.locator(".ah-hero-card .statement").inner_text()
        ask_ids = {x.get("item_id") for x in ((t.get("asks") or {}).get("items") or {}).values()}
        self.check("close-ask", "an ask closes with 'Close ask', which writes only the ask, and the Portfolio hero moves on",
                   "Close ask" in labels and "Done" not in labels and len(wr) == 1 and set(wr) <= ask_ids and hero1 != hero0,
                   f"buttons {labels}; wrote {sorted(wr)}; hero {hero0[:40]} -> {hero1[:40]}")
        self.common(page, "close-ask")
        ctx.close()
        # 5. A closed promise's draft leaves Ready for you.
        mk = next(k for k, d in a["drafts"]["items"].items() if "markup" in str(d.get("subject")).lower())
        ctx, page = self.open(browser, "ready-closed", PHONE, state={"items": {a["drafts"]["items"][mk]["commitment_id"]: {"done_at": "2026-10-22T06:50:00+05:30"}}, "actions": {}})
        txt = ready_text(page)
        self.check("ready-closed", "a promise marked done takes its draft out of Ready for you", "term sheet markup" not in txt and "Intro" in txt, txt[:120])
        ctx.close()
        # 6. The prep sheet says what to check before a draft goes, and offers Sent it.
        ctx, page = self.open(browser, "prep-caveat", PHONE)
        page.locator(".agenda-row.first").click()
        page.wait_for_timeout(150)
        sheet = page.locator(".sheet").inner_text() if page.locator(".sheet").count() else ""
        self.check("prep-caveat", "a draft in the prep sheet shows 'Before you send' and Sent it", "Before you send" in sheet and "Sent it" in sheet,
                   sheet[sheet.find("Ready to send"):][:160] if "Ready to send" in sheet else sheet[:120])
        self.shot(page, "prep-caveat-380")
        ctx.close()
        # 7. A reply in mail stops the nudge: Aditi answered Tara's note on Mon 26 Oct.
        reply = {"id": "th_reply_asks", "subject": "Re: Founder asks: Kestrel Pay, Orbit Treasury, Nimbus Collect", "date": "2026-10-26T15:00:00+05:30",
                 "url": "https://mail.google.com/mail/u/0/#all/th_reply_asks",
                 "participants": [{"name": "Aditi Rao", "email": "aditi@quillwater.vc"}, {"name": "Tara Menon", "email": "tara@quillwater.vc"}],
                 "messages": [{"from": {"name": "Aditi Rao", "email": "aditi@quillwater.vc"}, "date": "2026-10-26T15:00:00+05:30",
                               "text": "Yes, let's help Orbit Treasury and Kestrel Pay hire now."}], "labels": [], "snippet": "Yes"}
        snap, state = self._replay_home("tara", dt.datetime(2026, 10, 29, 6, 30, tzinfo=IST),
                                        [(dt.datetime(2026, 10, 22, 10, 0, tzinfo=IST), replay._sent_it("2026-10-22T10:00:00+05:30")),
                                         (dt.datetime(2026, 10, 26, 15, 0, tzinfo=IST), replay._mail(reply))])
        ctx, page = self.open(browser, "replied", PHONE, when=dt.datetime(2026, 10, 29, 7, 30, tzinfo=IST), member="tara", snap=snap, state=state)
        page.locator("#bottom-tabs button[aria-label='Portfolio']").click()
        page.wait_for_timeout(120)
        orbit = page.locator("section[aria-label='Founders need'] .row").filter(
            has=page.locator(".row-title", has_text=re.compile(r"^Orbit Treasury:"))).first
        otxt = orbit.inner_text() if orbit.count() else ""
        # Aditi's reply named Orbit and Kestrel: Nimbus, the note's third ask, still waits, and its row says what came.
        nimbus = page.locator("section[aria-label='Founders need'] .row").filter(
            has=page.locator(".row-title", has_text=re.compile(r"^Nimbus Collect:"))).first
        ntxt = nimbus.inner_text() if nimbus.count() else ""
        self.check("replied", "an ask whose note got a reply says who replied and when, and offers no nudge; the note's ask the "
                              "reply left out says so, never 'no reply'",
                   "Aditi replied" in otxt and "replied on 26 Oct" in otxt and "Nudge" not in otxt and
                   "not this one" in ntxt and "no reply" not in ntxt.lower(), otxt[:100] + " | " + ntxt[:160])
        self.shot(page, "replied-380")
        self.common(page, "replied")
        ctx.close()
        # 8. A draft tap a run answered stays answered after the draft leaves Home: no "Draft coming" on day 16.
        vs = _copy.deepcopy(v)
        tide = next(it for sec in vs["brief"]["sections"] for it in sec["items"] if "Tidewater" in it["title"])
        vs.setdefault("proposals", {"items": {}}).setdefault("items", {})[tide["id"]] = {"type": "draft", "status": "applied", "applied_at": "2026-10-06T10:20:00+05:30",
                                                                                         "title": "Note to Tidewater Foundation"}
        st_d = {"items": {}, "actions": {tide["id"]: {"type": "draft", "status": "approved", "at": "2026-10-06T10:00:00+05:30",
                                                      "payload": {"kind": "lp", "entity": tide.get("entity") or {}}}}}
        ctx, page = self.open(browser, "coming-answered", PHONE, member="vikram", snap=vs, state=st_d)
        page.locator("#bottom-tabs button[aria-label='Today']").click()
        page.wait_for_timeout(120)
        trow = page.locator("#view .row", has_text="Tidewater").first
        ttxt = trow.inner_text() if trow.count() else ""
        self.check("coming-answered", "a tap a run answered never reads 'Draft coming', after its draft left Home", trow.count() == 1 and "Draft coming" not in ttxt, ttxt[:120])
        ctx.close()
        # 9. A step saved again on the Pipeline tab, after the last one was applied, is saving, not lost.
        m = _copy.deepcopy(self.snaps["meera"])
        me = str((m.get("config") or {}).get("user_email") or "").lower()
        did, dd = next((k, d) for k, d in ((m.get("pipeline") or {}).get("deals") or {}).items()
                       if d.get("active") and d.get("company") and str(d.get("owner") or "").lower() == me)
        m.setdefault("proposals", {"items": {}}).setdefault("items", {})[f"ns_{did}"] = {"type": "next_step", "status": "applied", "applied_at": "2026-10-18T10:29:00+05:30"}
        st_p = {"items": {}, "actions": {f"ns_{did}": {"type": "next_step", "status": "approved", "at": "2026-10-22T06:55:00+05:30",
                                                       "payload": {"deal_id": did, "company": dd.get("company"), "text": "Partner meeting on 3 Nov", "due": None}}}}
        ctx, page = self.open(browser, "step-resaved", PHONE, member="meera", snap=m, state=st_p)
        page.locator("#bottom-tabs button[aria-label='Pipeline']").click()
        page.wait_for_timeout(150)
        prow = page.locator("#view .deal-row").filter(has=page.locator(".row-title", has_text=re.compile("^" + re.escape(dd["company"]) + "$"))).first
        ptxt = prow.inner_text() if prow.count() else ""
        self.check("step-resaved", "a step saved again after the last was applied shows as saving", "Partner meeting on 3 Nov" in ptxt and "saving" in ptxt, ptxt[:140])
        ctx.close()
        # 10. Meetings left unlogged for more than two working days fold into one line.
        asnap, astate = self._replay_home("aditi", dt.datetime(2026, 10, 28, 6, 30, tzinfo=IST))
        n_old = sum(1 for p_ in ((asnap.get("pipeline") or {}).get("met_prompts") or []) if not p_.get("step_only") and p_.get("met_on") <= "2026-10-23")
        ctx, page = self.open(browser, "met-fold", PHONE, when=dt.datetime(2026, 10, 28, 8, 0, tzinfo=IST), member="aditi", snap=asnap, state=astate)
        page.locator("#bottom-tabs button[aria-label='Today']").click()
        page.wait_for_timeout(120)
        fold = page.locator("#view .row", has_text=re.compile(r"^Log \d+ meetings from")).count()
        forms = page.locator("#view form.met-form").count()
        btn = page.locator("#view button", has_text="Show them")
        if btn.count():
            btn.first.click()
            page.wait_for_timeout(100)
        forms2 = page.locator("#view form.met-form").count()
        self.check("met-fold", "two or more meetings unlogged for over two working days fold into one line, forms a tap away",
                   n_old < 2 or (fold == 1 and forms2 >= n_old > forms), f"old {n_old}; fold {fold}; forms {forms} -> {forms2}")
        self.common(page, "met-fold")
        ctx.close()

    def round12(self, browser) -> None:
        """Round twelve: the page says what it knows the moment a tap lands (a nudge marked sent, an ask closed, a chase
        sent), compares times as instants, says "was due" for a date gone by, clears what others owe with Got it, shows a
        pitch you answered as answered, opens Monday's prep from a Friday, opens on the row a push named, and says how late
        a promise is under Ready for you."""
        import copy as _copy
        import replay  # noqa: E402
        thu29 = dt.datetime(2026, 10, 29, 7, 30, tzinfo=IST)
        # 1. Sent it on a grouped nudge: the row says it went, at once, and the Portfolio hero stops offering it.
        snap, state = self._replay_home("tara", dt.datetime(2026, 10, 29, 6, 30, tzinfo=IST),
                                        [(dt.datetime(2026, 10, 22, 10, 0, tzinfo=IST), replay._sent_it("2026-10-22T10:00:00+05:30"))])
        ctx, page = self.open(browser, "nudge-sent", PHONE, when=thu29, member="tara", snap=snap, state=state)
        page.locator("#bottom-tabs button[aria-label='Today']").click()
        page.wait_for_timeout(120)
        grp = page.locator("#view .row", has_text=re.compile(r"founder asks wait on Aditi")).first
        has_grp = grp.count() == 1
        if has_grp:
            grp.locator(".row-hit").first.click()
            page.wait_for_timeout(60)
            grp.locator("button", has_text="Sent it").first.click()
            page.wait_for_timeout(150)
        gtxt = page.locator("#view .row", has_text=re.compile(r"founder asks wait on Aditi")).first.inner_text() if has_grp else ""
        page.locator("#bottom-tabs button[aria-label='Portfolio']").click()
        page.wait_for_timeout(120)
        ph = page.locator(".ah-hero-card").inner_text()
        self.check("nudge-sent", "Sent it on a grouped nudge says 'Nudged Aditi' at once, on Today and the Portfolio hero",
                   has_grp and "Nudged Aditi" in gtxt and "Nudge ready" not in gtxt and "Nudge ready" not in ph, f"row: {gtxt[:120]}; hero: {ph[:120]}")
        # Close ask on one ask: the Portfolio hero counts the asks still open.
        nim = page.locator("section[aria-label='Founders need'] .row").filter(has=page.locator(".row-title", has_text=re.compile("^Nimbus Collect:"))).first
        open_before = page.locator("section[aria-label='Founders need'] .row").count()
        if nim.count():
            nim.locator(".row-hit").first.click()
            page.wait_for_timeout(60)
            nim.locator("button", has_text="Close ask").first.click()
            page.wait_for_timeout(150)
        ph2 = page.locator(".ah-hero-card .finding").inner_text() if page.locator(".ah-hero-card .finding").count() else ""
        m_ = re.search(r"(\d+) more open", ph2)
        left_ = page.locator("section[aria-label='Founders need'] .row").count()
        self.check("nudge-sent", "after Close ask the Portfolio hero's 'more open' counts the asks still showing",
                   (int(m_.group(1)) if m_ else 0) == max(0, left_ - 1) and left_ == open_before - 1, f"{ph2[-60:]}; rows {open_before} -> {left_}")
        self.common(page, "nudge-sent")
        ctx.close()
        # 2. A step saved again after the last was applied, with the tap in UTC and the run in +05:30, shows as saving.
        m = _copy.deepcopy(self.snaps["meera"])
        me = str((m.get("config") or {}).get("user_email") or "").lower()
        did, dd = next((k, d) for k, d in ((m.get("pipeline") or {}).get("deals") or {}).items()
                       if d.get("active") and d.get("company") and str(d.get("owner") or "").lower() == me)
        m.setdefault("proposals", {"items": {}}).setdefault("items", {})[f"ns_{did}"] = {"type": "next_step", "status": "applied",
                                                                                          "applied_at": "2026-10-22T06:28:00+05:30"}
        st_p = {"items": {}, "actions": {f"ns_{did}": {"type": "next_step", "status": "approved", "at": "2026-10-22T01:30:00.000Z",
                                                       "payload": {"deal_id": did, "company": dd.get("company"), "text": "Reference calls with Shreya", "due": None}}}}
        ctx, page = self.open(browser, "utc-step", PHONE, member="meera", snap=m, state=st_p)
        page.locator("#bottom-tabs button[aria-label='Pipeline']").click()
        page.wait_for_timeout(150)
        prow = page.locator("#view .deal-row").filter(has=page.locator(".row-title", has_text=re.compile("^" + re.escape(dd["company"]) + "$"))).first
        ptxt = prow.inner_text() if prow.count() else ""
        self.check("utc-step", "a tap stamped in UTC after a run's +05:30 apply reads as newer: the step shows as saving",
                   "Reference calls with Shreya" in ptxt and "saving" in ptxt, ptxt[:140])
        ctx.close()
        # 3. Two weeks on, a Pipeline step whose date has passed reads "was due", never "by" a day gone.
        ctx, page = self.open(browser, "was-due", PHONE, when=dt.datetime(2026, 11, 9, 8, 0, tzinfo=IST), member="meera")
        page.locator("#bottom-tabs button[aria-label='Pipeline']").click()
        page.wait_for_timeout(150)
        for _ in range(8):
            folded = page.locator(".stage-h button[aria-expanded=false]")
            if not folded.count():
                break
            folded.first.click()
        details = page.locator("#view .deal-row .row-detail").all_inner_texts()
        past = [t_ for t_ in details if re.search(r"\bby (\d{2}) (Oct|Nov)\b", t_) and
                dt.date(2026, {"Oct": 10, "Nov": 11}[re.search(r"\bby (\d{2}) (Oct|Nov)\b", t_).group(2)],
                        int(re.search(r"\bby (\d{2}) (Oct|Nov)\b", t_).group(1))) < dt.date(2026, 11, 9)]
        self.check("was-due", "no Pipeline row says 'by' a date that has passed", bool(details) and not past, "; ".join(past[:2]))
        ctx.close()
        # 4. A colleague's or a founder's promise to you clears with Got it.
        t = self.snaps["tara"]
        wrow = next((it for sec in t["brief"]["sections"] for it in sec["items"] if it.get("kind") == "waiting"), None)
        ctx, page = self.open(browser, "got-it", PHONE, member="tara")
        page.locator("#bottom-tabs button[aria-label='Today']").click()
        page.wait_for_timeout(120)
        ok_, wrote = False, []
        if wrow:
            r_ = page.locator("#view .row").filter(has=page.locator(".row-title", has_text=wrow["title"][:30])).first
            if r_.count():
                r_.locator(".row-hit").first.click()
                page.wait_for_timeout(60)
                b_ = r_.locator("button", has_text="Got it")
                ok_ = b_.count() == 1
                if ok_:
                    b_.first.click()
                    page.wait_for_timeout(150)
                    wrote = sorted(self._writes(page))
        self.check("got-it", "what someone owes you clears with Got it, which marks the promise", ok_ and bool(wrow) and wrow.get("commitment_id") in wrote,
                   f"{(wrow or {}).get('title')}: wrote {wrote}")
        ctx.close()
        # 5. A pitch you replied to: Sent it on its reply, and the Pitches list says you replied.
        ctx, page = self.open(browser, "pitch-replied", PHONE, member="meera")
        page.locator("#bottom-tabs button[aria-label='Today']").click()
        page.wait_for_timeout(120)
        # Its reply is under Ready for you, or on the pitch's own row on Today: Sent it is wherever it shows.
        rfy = page.locator(SEND + " .row", has_text="Harborline").first
        if not rfy.count() or not rfy.locator("button", has_text="Sent it").count():
            rfy = page.locator("#view .row", has_text="Harborline").first
            if rfy.count() and rfy.locator(".row-hit").count():
                rfy.locator(".row-hit").first.click()
                page.wait_for_timeout(60)
        sent_ok = False
        if rfy.count():
            btn = rfy.locator("button", has_text="Sent it")
            sent_ok = btn.count() >= 1
            if sent_ok:
                btn.first.click()
                page.wait_for_timeout(150)
        page.locator("#bottom-tabs button[aria-label='Pipeline']").click()
        page.wait_for_timeout(150)
        pit = page.locator("section[aria-label='Pitches'] .row", has_text="Harborline").first
        pt = pit.inner_text() if pit.count() else ""
        self.check("pitch-replied", "after Sent it on a pitch's reply, the Pitches list says you replied, not 'Book a call'",
                   sent_ok and "You replied" in pt and "Book a call" not in pt, pt[:120])
        ctx.close()
        # 6. Friday: the next working day's meetings open their prep from Today.
        fsnap, fstate = self._replay_home("meera", dt.datetime(2026, 10, 23, 6, 35, tzinfo=IST))
        ctx, page = self.open(browser, "monday-prep", PHONE, when=dt.datetime(2026, 10, 23, 7, 0, tzinfo=IST), member="meera", snap=fsnap, state=fstate)
        page.locator("#bottom-tabs button[aria-label='Today']").click()
        page.wait_for_timeout(120)
        agenda = page.locator(".ah-agenda").inner_text()
        link = page.locator(".ah-agenda .link-btn").first
        opened = ""
        if link.count():
            link.click()
            page.wait_for_timeout(150)
            opened = page.locator(".sheet").inner_text() if page.locator(".sheet").count() else ""
        self.check("monday-prep", "on a Friday Today names Monday's meetings, and each opens its prep",
                   "Monday:" in agenda and "partner meeting" in opened.lower(), f"{agenda[-80:]}; sheet {opened[:60]}")
        self.shot(page, "monday-prep-380")
        ctx.close()
        # 6b. The note to Aditi waits under Ready for you with Sent it; once both drafts it names are sent, it leaves.
        hold_ = next(((k, d) for k, d in (((fsnap.get("drafts") or {}).get("items")) or {}).items() if d.get("kind") == "holder"), (None, {}))
        ctx, page = self.open(browser, "holder-note", PHONE, when=dt.datetime(2026, 10, 23, 7, 0, tzinfo=IST), member="meera", snap=fsnap, state=fstate)
        page.locator("#bottom-tabs button[aria-label='Today']").click()
        page.wait_for_timeout(120)
        hrow = page.locator(SEND + " .row", has_text="Your view on").first
        htxt = hrow.inner_text() if hrow.count() else ""
        has_sent = hrow.count() == 1 and hrow.locator("button", has_text="Sent it").count() == 1
        pointed = page.locator("#view .row .done-note", has_text="Note to Aditi ready").count()
        self.shot(page, "holder-note-380")
        ctx.close()
        st2 = _copy.deepcopy(fstate)
        for k_ in hold_[1].get("holds") or []:
            st2.setdefault("items", {})[k_] = {"done_at": "2026-10-23T07:05:00+05:30"}
        ctx, page = self.open(browser, "holder-note", PHONE, when=dt.datetime(2026, 10, 23, 7, 10, tzinfo=IST), member="meera", snap=fsnap, state=st2)
        page.locator("#bottom-tabs button[aria-label='Today']").click()
        page.wait_for_timeout(120)
        after_ = page.locator(SEND + " .row", has_text="Your view on").count()
        self.check("holder-note", "the note to the partner whose view drafts wait on shows under Ready for you with Sent it, "
                              "each draft it names points at it, and it leaves once every one is sent",
                   bool(hold_[0]) and "Aditi" in htxt and has_sent and after_ == 0 and pointed == len(hold_[1].get("holds") or []),
                   f"{htxt[:140]}; rows pointing at it {pointed}; after both sent {after_}")
        self.common(page, "holder-note")
        ctx.close()
        # 7. A push that named a row, not the hero: Home opens on Today with that row open.
        ts = _copy.deepcopy(self.snaps["tara"])
        first_row = next(it for sec in ts["brief"]["sections"] for it in sec["items"] if it["id"] != (ts["brief"].get("hero") or {}).get("item_id"))
        ts["brief"]["pushed_item"] = first_row["id"]
        ts["brief"]["hero"]["pushed"] = False
        ctx, page = self.open(browser, "pushed-row", PHONE, member="tara", snap=ts)
        page.wait_for_timeout(150)
        today_sel = page.locator("#bottom-tabs button[aria-label='Today'][aria-selected='true']").count()
        exp = page.locator(f".row-hit[data-id='{first_row['id']}']").get_attribute("aria-expanded") if page.locator(f".row-hit[data-id='{first_row['id']}']").count() else None
        self.check("pushed-row", "a push that named a row opens Home on Today with that row open", today_sel == 1 and exp == "true",
                   f"today {today_sel}; expanded {exp}")
        ctx.close()
        # 8. Under Ready for you, a promise's draft says how late the promise is.
        asnap, astate = self._replay_home("aditi", dt.datetime(2026, 11, 9, 6, 30, tzinfo=IST))
        ctx, page = self.open(browser, "late-drafts", PHONE, when=dt.datetime(2026, 11, 9, 8, 0, tzinfo=IST), member="aditi", snap=asnap, state=astate)
        page.locator("#bottom-tabs button[aria-label='Today']").click()
        page.wait_for_timeout(120)
        rtxt = ready_text(page)
        fold = page.locator("#view .row-title", has_text=re.compile(r"promises? more than a week late")).count()
        self.check("late-drafts", "a late promise's draft says how late it is, and the late ones are named on Today",
                   bool(re.search(r"\d+ days late", rtxt)) and fold >= 1, f"fold rows {fold}; {rtxt[:140]}")
        self.common(page, "late-drafts")
        ctx.close()
        # 9. Sent it on a chase: the hero says it went until the next check, and offers no stale "ready".
        vsnap, vstate = self._replay_home("vikram", dt.datetime(2026, 10, 29, 6, 30, tzinfo=IST),
                                          [(dt.datetime(2026, 10, 22, 10, 0, tzinfo=IST),
                                            replay._mark_sent(lambda did, d: "capital call" in str(d.get("subject") or "").lower(), "2026-10-22T10:00:00+05:30"))])
        ctx, page = self.open(browser, "chase-sent", PHONE, when=thu29, member="vikram", snap=vsnap, state=vstate)
        page.locator("#bottom-tabs button[aria-label='Today']").click()
        page.wait_for_timeout(120)
        hero_before = page.locator(".ah-hero-card").inner_text()
        hb = page.locator(".ah-hero-card .hero-actions button", has_text="Sent it")
        had_sent = hb.count() >= 1
        if had_sent:
            hb.first.click()
            page.wait_for_timeout(150)
        hero_after = page.locator(".ah-hero-card").inner_text()
        self.check("chase-sent", "after Sent it on a chase the hero says it was marked sent, with no 'Second note ready'",
                   "Peregrine" in hero_before and had_sent and "Marked sent" in hero_after and "Second note ready" not in hero_after,
                   f"{hero_after[:160]}")
        self.common(page, "chase-sent")
        ctx.close()

    def round13(self, browser) -> None:
        """Round thirteen: Done on one of two promises that share an email closes that promise only, never the email, and
        never says it was sent; the email then says which lines to take out. Sent it on the note to a partner turns the
        rows it names to "Asked Aditi", then to "Aditi replied". A CRM step you marked sent reads as sent on Pipeline."""
        import copy as _copy
        import replay  # noqa: E402
        fri = dt.datetime(2026, 10, 23, 7, 0, tzinfo=IST)
        # 1. Done on one promise of two in one email.
        tsnap, tstate = self._replay_home("tara", dt.datetime(2026, 10, 23, 6, 40, tzinfo=IST))
        shared_ = next(((k, d) for k, d in (((tsnap.get("drafts") or {}).get("items")) or {}).items() if len(d.get("commitment_ids") or []) > 1), (None, {}))
        whats_ = {c_: str((((tsnap.get("commitments") or {}).get("items") or {}).get(c_) or {}).get("what") or "") for c_ in shared_[1].get("commitment_ids") or []}
        first_c, second_c = (list(whats_) + [None, None])[:2]
        ctx, page = self.open(browser, "shared-done", PHONE, when=fri, member="tara", snap=tsnap, state=tstate)
        page.locator("#bottom-tabs button[aria-label='Today']").click()
        page.wait_for_timeout(120)
        row1 = page.locator("#view .row", has_text=whats_.get(first_c) or "-").first
        tapped = row1.count() == 1
        if tapped:
            row1.locator(".row-hit").first.click()
            page.wait_for_timeout(60)
            row1.locator(".row-actions button", has_text="Done").first.click()
            page.wait_for_timeout(150)
        toast1 = page.locator(".toast").inner_text() if page.locator(".toast").count() else ""
        w1 = page.evaluate("window.__writes") or []
        keys1 = set(((w1[-1] if w1 else {}).get("data") or {}).get("items") or {})
        marks1 = [v for v in (((w1[-1] if w1 else {}).get("data") or {}).get("items") or {}).values()]
        row2 = page.locator("#view .row", has_text=whats_.get(second_c) or "-").first
        note2, ready_ = "", 0
        if row2.count():
            row2.locator(".row-hit").first.click()
            page.wait_for_timeout(60)
            note2 = row2.locator(".draft-note").inner_text() if row2.locator(".draft-note").count() else ""
            ready_ = row2.locator("button", has_text="Sent it").count()
        self.check("shared-done", "Done on one of two promises in one email closes that promise, not the email: no 'Marked sent', "
                                  "the other promise keeps the email, which says to take the closed promise's lines out",
                   bool(shared_[0]) and tapped and "Marked done" in toast1 and "sent" not in toast1.lower() and shared_[0] not in keys1 and
                   all(m_.get("closed_by") == "done" and not m_.get("sent") for m_ in marks1) and ready_ >= 1 and
                   "marked done: take its lines out" in note2,
                   f"toast {toast1[:60]!r}; wrote {sorted(keys1)}; Sent it on the other row {ready_}; note {note2[:120]!r}")
        self.shot(page, "shared-done-380")
        done2 = False
        if row2.count():
            btn2 = row2.locator(".row-actions button", has_text="Done")
            if btn2.count():
                btn2.first.click()
                page.wait_for_timeout(150)
                done2 = True
        w2 = page.evaluate("window.__writes") or []
        keys2 = (((w2[-1] if w2 else {}).get("data") or {}).get("items") or {})
        ready2 = page.locator(READY).locator(".row", has_text=shared_[1].get("subject") or "-").count()
        self.check("shared-done", "Done on the second closes the email too, as done, never as sent",
                   done2 and shared_[0] in keys2 and (keys2.get(shared_[0]) or {}).get("closed_by") == "done" and
                   not (keys2.get(shared_[0]) or {}).get("sent") and ready2 == 0 and page.get_by_text("Marked sent").count() == 0,
                   f"wrote {sorted(keys2)}; ready rows {ready2}")
        self.common(page, "shared-done")
        ctx.close()
        # 2. Sent it on the note to Aditi: the rows it names say she was asked; once she replied, that she did.
        msnap, mstate = self._replay_home("meera", dt.datetime(2026, 10, 23, 6, 35, tzinfo=IST))
        hold_ = next(((k, d) for k, d in (((msnap.get("drafts") or {}).get("items")) or {}).items() if d.get("kind") == "holder"), (None, {}))
        ctx, page = self.open(browser, "holder-sent", PHONE, when=fri, member="meera", snap=msnap, state=mstate)
        page.locator("#bottom-tabs button[aria-label='Today']").click()
        page.wait_for_timeout(120)
        hrow = page.locator(SEND + " .row", has_text="Your view on").first
        sent_ok = False
        if hrow.count():
            hrow.locator(".row-hit").first.click()
            page.wait_for_timeout(60)
            b_ = hrow.locator("button", has_text="Sent it")
            if b_.count():
                b_.first.click()
                page.wait_for_timeout(150)
                sent_ok = True
        asked_ = page.locator("#view .row .done-note", has_text="Asked Aditi at 07:00").count()
        self.check("holder-sent", "after Sent it on the note to Aditi, each row it names says 'Asked Aditi at 07:00 for the firm's view'",
                   bool(hold_[0]) and sent_ok and asked_ == len(hold_[1].get("holds") or []), f"rows saying it {asked_} of {len(hold_[1].get('holds') or [])}")
        ctx.close()
        rs = _copy.deepcopy(msnap)
        rs["drafts"]["items"][hold_[0]]["replied"] = {"on": "2026-10-23T11:05:00+05:30", "url": "https://mail.google.com/mail/u/0/#all/th_hold_reply"}
        rst = _copy.deepcopy(mstate)
        rst.setdefault("items", {})[hold_[0]] = {"done_at": "2026-10-23T07:00:00+05:30", "sent": True}
        ctx, page = self.open(browser, "holder-sent", PHONE, when=dt.datetime(2026, 10, 23, 11, 30, tzinfo=IST), member="meera", snap=rs, state=rst)
        page.locator("#bottom-tabs button[aria-label='Today']").click()
        page.wait_for_timeout(120)
        rep_ = page.locator("#view .row .done-note", has_text="Aditi replied at 11:05").count()
        self.check("holder-sent", "once Aditi replied, those rows say 'Aditi replied at 11:05: read it, then send'",
                   rep_ == len(hold_[1].get("holds") or []), f"rows saying it {rep_}")
        self.shot(page, "holder-replied-380")
        self.common(page, "holder-sent")
        ctx.close()
        # 3. A step you marked sent: Pipeline says it went, never that it is next.
        asnap, astate = self._replay_home("aditi", dt.datetime(2026, 10, 26, 6, 30, tzinfo=IST),
                                          [(dt.datetime(2026, 10, 23, 10, 0, tzinfo=IST),
                                            replay._mark_sent(lambda did, d: "markup" in str(d.get("subject") or "").lower(), "2026-10-23T10:00:00+05:30"))])
        ctx, page = self.open(browser, "step-sent", PHONE, when=dt.datetime(2026, 10, 26, 8, 0, tzinfo=IST), member="aditi", snap=asnap, state=astate)
        page.locator("#bottom-tabs button[aria-label='Pipeline']").click()
        page.wait_for_timeout(120)
        arow = page.locator("#view .row", has_text="Atlas Settlement").first
        atxt = arow.inner_text() if arow.count() else ""
        self.check("step-sent", "a CRM step you marked sent reads 'Sent 23 Oct: send term sheet markup' on Pipeline, never 'Next:'",
                   "Sent 23 Oct: send term sheet markup" in atxt and "Next: Send term sheet markup" not in atxt, atxt[:160])
        self.shot(page, "step-sent-380")
        self.common(page, "step-sent")
        ctx.close()

    def redesign(self, browser) -> None:
        """Round sixteen: sections fold and remember it, Focus, the day strip, one action line per row, Activity with
        Undo, the select, and research on the prep card."""
        sc = "folds"
        ctx, page = self.open(browser, sc, PHONE, open_all=False)
        heads = page.locator("#view section.card .fold-btn")
        self.check(sc, "every Today section has a fold header", heads.count() >= 3 and page.locator("#view section.card[aria-label] > .sec-h:not(:has(.fold-btn))").count() == 0)
        folded = page.locator("#view section.card.is-folded")
        names = [x.get_attribute("aria-label") for x in folded.all()]
        self.check(sc, "Waiting and Watch start folded, Decide and Send open", all(n in ("Waiting on others", "Watch", "Done today") for n in names)
                   and page.locator(DECIDE + ":not(.is-folded)").count() == 1, str(names))
        if folded.count():
            first = folded.first
            label = first.get_attribute("aria-label")
            self.check(sc, "a folded section keeps its count and top line", first.locator(".count").count() == 1 and first.locator(".fold-peek").count() == 1)
            first.locator(".fold-btn").click()
            page.wait_for_timeout(60)
            self.check(sc, "a tap opens it", page.locator(f"section[aria-label=\"{label}\"]:not(.is-folded)").count() == 1)
            page.reload()
            page.wait_for_timeout(250)
            self.check(sc, "the fold is remembered", page.locator(f"section[aria-label=\"{label}\"]:not(.is-folded)").count() == 1)
        page.locator(".day-tools button", has_text="Focus").click()
        page.wait_for_timeout(60)
        open_ = [x.get_attribute("aria-label") for x in page.locator("#view section.card[aria-label]:not(.is-folded)").all()]
        self.check(sc, "Focus folds everything but the schedule", open_ == ["Schedule"], str(open_))
        page.locator(".daystrip .stat", has_text="Decide").click()
        page.wait_for_timeout(120)
        self.check(sc, "a day-strip cell opens its section", page.locator(DECIDE + ":not(.is-folded)").count() == 1)
        page.locator(".day-tools button", has_text="Focus").click()
        page.wait_for_timeout(60)
        rdy = page.locator(DECIDE + " .row", has=page.locator("button.row-hit[data-id^='rdy:']")).first
        closed = rdy.locator("button", has_text="Approve").is_visible() is False if rdy.locator("button", has_text="Approve").count() else True
        rdy.locator(".row-hit").click()
        page.wait_for_timeout(60)
        rdy = page.locator(DECIDE + " .row", has=page.locator("button.row-hit[data-id^='rdy:']")).first
        self.check(sc, "a CRM change reads like any row: closed until tapped, then Approve", closed and rdy.locator("button", has_text="Approve").is_visible())
        drow = page.locator(SEND + " .row").first
        drow.locator(".row-hit").click()
        page.wait_for_timeout(60)
        drow = page.locator(SEND + " .row").first
        self.check(sc, "a draft opens with Open in Gmail first, Sent it quiet and Copy as an icon",
                   drow.locator("a.btn-secondary", has_text="Open in Gmail").count() == 1 and drow.locator("button.btn-ghost", has_text="Sent it").count() == 1
                   and drow.locator("button[aria-label='Copy draft']").count() == 1)
        ctl = page.evaluate("Array.from(document.querySelectorAll('#view button, #view a, #view input, #view select')).filter(e => e.offsetParent).length")
        self.check(sc, "Today shows few controls at once", ctl <= 32, f"{ctl} visible")
        self.shot(page, "folds-380")
        self.common(page, sc)
        ctx.close()

        sc = "hero-fold"
        for m in ("aditi", "kabir", "meera", "rohan", "tara", "vikram", "solo"):
            ctx, page = self.open(browser, sc, {"width": 380, "height": 844}, member=m, open_all=False)
            y = page.evaluate("(() => { var e = document.querySelector('.ah-hero-card .btn-primary'); return e ? e.getBoundingClientRect().bottom : 0; })()")
            self.check(sc, f"{m}: the top line's main button is on the first phone screen, above the tab bar", y <= 784, f"bottom at {round(y)}px")
            ctx.close()

        sc = "row-actions"
        ctx, page = self.open(browser, sc, PHONE)
        page.locator("#view .row", has=page.locator("button.row-hit:not([data-id^='rdy:'])")).first.locator(".row-hit").click()
        row = page.locator("#view .row", has=page.locator("button.row-hit:not([data-id^='rdy:'])")).first
        self.check(sc, "an open row shows one line of actions, with Later and Rate folded",
                   row.locator("button", has_text="Later").count() == 1 and row.locator("button", has_text="Tomorrow").is_visible() is False
                   and row.locator(".chip-rate").first.is_visible() is False)
        row.locator("button", has_text="Later").click()
        page.wait_for_timeout(60)
        row = page.locator("#view .row", has=page.locator("button.row-hit:not([data-id^='rdy:'])")).first
        self.check(sc, "Later opens the snooze times", row.locator("button", has_text="Tomorrow").is_visible())
        self.shot(page, "row-later-380")
        ctx.close()

        sc = "activity"
        ctx, page = self.open(browser, sc, PHONE, member="kabir")
        label, title = self.done_row("kabir")
        page.locator(f"section[aria-label='{label}'] .row-hit", has_text=title).first.click()
        page.locator(f"section[aria-label='{label}'] .row-actions button", has_text="Done").first.click()
        page.wait_for_timeout(120)
        page.locator("#activity-btn").click()
        page.wait_for_timeout(80)
        entry = page.locator("section[aria-label='Today'] .log-row", has_text=title)
        self.check(sc, "Activity lists the tap under Today, by category", entry.count() == 1 and page.locator("section[aria-label='Today'] .log-cat", has_text="Done").count() == 1)
        self.shot(page, "activity-380")
        entry.locator("button", has_text="Reopen").click()
        page.wait_for_timeout(120)
        w = page.evaluate("window.__writes")
        last = (w[-1] if w else {}).get("data", {}).get("items") or {}
        self.check(sc, "Reopen from Activity clears the tap and records it", any(v.get("done_at") is None and v.get("undone") for v in last.values()), json.dumps(last)[:160])
        page.locator("#bottom-tabs button[aria-label='Today']").click()
        page.wait_for_timeout(60)
        self.check(sc, "the line is back on Today", page.locator(OPEN_LINES).get_by_text(title, exact=True).count() == 1)
        self.common(page, sc)
        ctx.close()

        sc = "activity-crm"
        snap = json.loads(json.dumps(self.snaps["aditi"]))
        props = snap["proposals"]["items"]
        pid = next(k for k, v in props.items() if v.get("type") == "crm_update")
        props[pid] = {**props[pid], "status": "applied", "applied_at": "2026-10-22T07:02:00+05:30"}
        state = {"items": {}, "actions": {pid: {"type": "crm_update", "status": "approved", "payload": {"fields": props[pid].get("fields"), "record": props[pid].get("record")},
                                               "at": "2026-10-22T06:40:00+05:30", "t": "Atlas: stage"},
                                         "ns_x": {"type": "next_step", "status": "approved", "payload": {"deal_id": "x", "company": "Halo", "text": "Diligence"},
                                                  "at": "2026-10-22T06:45:00+05:30", "t": "Halo: next step Diligence"}}}
        ctx, page = self.open(browser, sc, PHONE, snap=snap, state=state)
        page.locator("#activity-btn").click()
        page.wait_for_timeout(80)
        crm = page.locator(".log-row", has_text="Atlas: stage")
        pend = page.locator(".log-row", has_text="Halo: next step")
        self.check(sc, "an applied CRM change offers Reverse in CRM; one still waiting offers Withdraw",
                   crm.locator("button", has_text="Reverse in CRM").count() == 1 and pend.locator("button", has_text="Withdraw").count() == 1)
        crm.locator("button", has_text="Reverse in CRM").click()
        page.wait_for_timeout(120)
        w = page.evaluate("window.__writes")
        items = next((x.get("data") or {}).get("items") for x in reversed(w) if x.get("path") == "state/actions")
        self.check(sc, "Reverse asks the next check to put the old values back", (items.get("rv_" + pid) or {}).get("type") == "revert"
                   and (items.get("rv_" + pid) or {}).get("payload", {}).get("of") == pid, json.dumps(items)[:160])
        page.locator(".log-row", has_text="Halo: next step").locator("button", has_text="Withdraw").click()
        page.wait_for_timeout(120)
        w = page.evaluate("window.__writes")
        items = next((x.get("data") or {}).get("items") for x in reversed(w) if x.get("path") == "state/actions")
        self.check(sc, "Withdraw stops a change that has not been made", (items.get("ns_x") or {}).get("status") == "withdrawn")
        self.common(page, sc)
        ctx.close()

        sc = "select"
        ctx, page = self.open(browser, sc, DESK, snap={**self.snaps["aditi"], "config": {**self.snaps["aditi"]["config"], "demo": True}})
        ctx.close()
        sc = "research"
        ctx, page = self.open(browser, sc, PHONE)
        page.locator("button.agenda-row").first.click()
        page.wait_for_timeout(80)
        dlg = page.locator("[role=dialog]")
        self.check(sc, "the prep card says research runs by itself in the desktop app, and offers Claude instead", dlg.get_by_text("Research", exact=True).count() == 1 and
                   ((dlg.locator("button", has_text="Ask Claude instead").count() == 1 and "Claude desktop app" in dlg.inner_text()) or
                    (dlg.locator("a", has_text="This morning's map in Drive").count() == 1 and dlg.locator("button", has_text="Research now").count() == 0)))
        ctx.close()
        snap = json.loads(json.dumps(self.snaps["aditi"]))
        cards = snap["prep"]["cards"]
        k0 = next(iter(cards))
        cards[k0]["research"] = [{"name": "Ishaan Rao", "headline": "CEO, Atlas Settlement", "says": "Settlement is the bottleneck", "thinks": "Banks move slowly",
                                  "does": "Posts weekly on cross-border rails", "feels": "Pressed for time before the round", "points": ["Ask about the bank partner"],
                                  "source_url": "https://www.linkedin.com/in/example", "read_at": "2026-10-22"}]
        ctx, page = self.open(browser, "research-map", PHONE, snap=snap)
        page.locator("button.agenda-row").first.click()
        page.wait_for_timeout(80)
        txt = page.locator("[role=dialog]").inner_text() if page.locator("[role=dialog]").count() else ""
        self.check("research-map", "a research run's empathy map shows on the card: says, thinks, does, feels and the source",
                   all(t in txt for t in ("Ishaan Rao", "Says", "Thinks", "Does", "Feels", "LinkedIn, read in your browser")), txt[-200:])
        self.shot(page, "research-380")
        ctx.close()

    def round17(self, browser) -> None:
        """Round seventeen: Ask from every screen, research that runs by itself in the Claude app's browser, and
        automatic CRM changes."""
        sc = "ask"
        ctx, page = self.open(browser, sc, PHONE, sample={"answer": "- **Atlas Settlement**: term sheet markup is due 23 Oct."})
        self.check(sc, "Ask is a tab, and the search icon is in the header", page.locator("#bottom-tabs button[aria-label='Ask']").count() == 1
                   and page.locator("#ask-btn").count() == 1)
        page.locator("#ask-btn").click()
        page.wait_for_timeout(60)
        box = page.locator("[role=dialog] textarea")
        box.fill("atlas")
        page.wait_for_timeout(60)
        hits = page.locator("[role=dialog] .hit").all_inner_texts()
        self.check(sc, "typing finds matches in the Home's own data", any("Atlas Settlement" in x for x in hits), str(hits[:3]))
        box.fill("What do I owe Atlas?")
        box.press("Enter")
        page.wait_for_timeout(200)
        got = page.locator("[role=dialog] .bubble.ant").inner_text() if page.locator("[role=dialog] .bubble.ant").count() else ""
        sent = page.evaluate("window.__samples")
        first = sent[0] if sent else []
        self.check(sc, "Enter asks Claude with the Home's data and streams the answer", "term sheet markup" in got and isinstance(first, list)
                   and "DATA" in first[0]["content"] and "Atlas Settlement" in first[0]["content"] and first[-1]["content"] == "What do I owe Atlas?", got[:80])
        page.keyboard.press("Escape")
        page.locator("#bottom-tabs button[aria-label='Ask']").click()
        page.wait_for_timeout(60)
        self.check(sc, "the Ask tab keeps the conversation", page.locator(".bubble.me", has_text="What do I owe Atlas?").count() == 1)
        self.shot(page, "ask-380")
        page.locator("#bottom-tabs button[aria-label='Today']").click()
        page.keyboard.press("/")
        page.wait_for_timeout(60)
        self.check(sc, "/ opens Ask from any screen", page.locator("[role=dialog]", has_text="Ask ant.").count() == 1)
        self.common(page, sc)
        ctx.close()
        ctx, page = self.open(browser, "ask-none", PHONE)
        page.locator("#bottom-tabs button[aria-label='Ask']").click()
        page.wait_for_timeout(60)
        self.check("ask-none", "without Claude, Ask still finds things and says what it needs", "open in the Claude app" in page.locator("#view").inner_text())
        ctx.close()

        sc = "research-auto"
        profile = ("Ishaan Verma\nCEO at Atlas Settlement\nAbout\nBuilding settlement rails for cross-border payments. Posts weekly about bank partnerships.\n"
                   "Experience\nAtlas Settlement, CEO, 2023 to now\nActivity\nWe just signed our second bank partner.")
        mp = {"match": True, "name": "Ishaan Verma", "headline": "CEO, Atlas Settlement", "says": "Settlement is the bottleneck in cross-border payments.",
              "thinks": "He likely worries banks move slower than his round.", "does": "Signs bank partners and posts about them weekly.",
              "feels": "Probably pressed for time before the term sheet deadline.", "company": "Seed-stage settlement rails, two bank partners.",
              "points": ["Ask when the second bank goes live", "Ask about Bluepeak's terms", "Confirm the ESOP pool"]}
        ctx, page = self.open(browser, sc, {"width": 320, "height": 780}, sample={"answer": "ok", "json": mp},
                              mcp={"pages": ["Search results People Ishaan Verma CEO Atlas Settlement", profile, "results", profile, "results", profile]})
        page.wait_for_timeout(5)
        self.check(sc, "while research runs on a 320px phone, the page stays inside the screen",
                   page.evaluate("document.documentElement.scrollWidth - window.innerWidth") <= 0)
        page.wait_for_timeout(900)
        calls = page.evaluate("window.__mcp")
        tools = sorted({c["tool"] for c in calls})
        clicks = [c["input"] for c in calls if c["tool"] == "computer"]
        writes = [w for w in page.evaluate("window.__writes") if str(w.get("path", "")).startswith("snap/research")]
        people = {}
        for w in writes:
            people.update(((w.get("data") or {}).get("people")) or {})
        self.check(sc, "on opening Home, ant. researches today's people in the app's browser by itself and keeps the map",
                   "ishaan@atlassettle.com" in people and people["ishaan@atlassettle.com"].get("says") and
                   any(c["server"] == "host:claude_browser" and c["tool"] == "navigate" and "linkedin.com" in c["input"]["url"] for c in calls), f"tools {tools}; kept {sorted(people)[:3]}")
        self.check(sc, "it only reads: navigate, page text, find and one click on the profile link per person, never typing",
                   set(t for t in tools if t not in ("search_files", "create_file")) <= {"navigate", "get_page_text", "find", "computer"}
                   and all(c.get("action") == "left_click" and "profile" in c.get("action_summary", "") for c in clicks), str(clicks[:2]))
        self.check(sc, "each map is saved as a Google Doc in the research folder", any(c["tool"] == "create_file" and c["input"].get("contentMimeType") == "text/html" for c in calls)
                   and str(people.get("ishaan@atlassettle.com", {}).get("drive_url", "")).startswith("https://docs.google.com/"))
        page.locator("button.agenda-row").first.click()
        page.wait_for_timeout(80)
        txt = page.locator("[role=dialog]").inner_text() if page.locator("[role=dialog]").count() else ""
        self.check(sc, "the prep card shows the map: says, thinks, does, feels and the source", all(t in txt for t in ("Says", "Thinks", "Does", "Feels", "LinkedIn, read in your browser")), txt[-160:])
        self.shot(page, "research-auto-380")
        ctx.close()
        ctx, page = self.open(browser, "research-signin", PHONE, sample={"answer": "ok", "json": mp}, mcp={"pages": ["Sign in to LinkedIn. Join now"]})
        page.wait_for_timeout(500)
        banner = page.locator("#banner-slot").inner_text() + " " + page.locator("#view").inner_text()
        self.check("research-signin", "when LinkedIn wants a sign-in, Home says so once and stops", "Sign in to LinkedIn" in banner and
                   sum(1 for c in page.evaluate("window.__mcp") if c["tool"] == "navigate") == 1, banner[:120])
        ctx.close()
        ctx, page = self.open(browser, "research-demo", PHONE, sample={"answer": "ok", "json": mp}, mcp={"pages": [profile]},
                              snap={**self.snaps["aditi"], "config": {**self.snaps["aditi"]["config"], "firm_domain": "atlassettle.com"}})
        page.wait_for_timeout(400)
        self.check("research-demo", "colleagues at your own firm are never researched", not any(c["tool"] == "navigate" and "Ishaan" in c["input"].get("url", "") for c in page.evaluate("window.__mcp")))
        ctx.close()

        sc = "by-itself"
        snap = json.loads(json.dumps(self.snaps["aditi"]))
        pid = next(k for k, v in snap["proposals"]["items"].items() if v.get("type") == "crm_update")
        snap["proposals"]["items"][pid] = {**snap["proposals"]["items"][pid], "status": "applied", "applied_at": "2026-10-22T07:01:00+05:30"}
        ctx, page = self.open(browser, sc, PHONE, snap=snap, state={"items": {}, "actions": {}, "settings": {"auto_apply": True}}, open_all=True)
        self.check(sc, "the Decide badge counts only what needs you", page.locator(DECIDE + " .sec-h .count").inner_text() ==
                   page.locator(".daystrip .stat", has_text="Decide").locator("b").inner_text())
        self.check(sc, "Today says what ant. did by itself, and Done today lists it with Undo", page.locator(".recap", has_text="by itself").count() == 1 and
                   page.locator("section[aria-label='Done today'] .log-row", has_text="Done by itself").locator("button", has_text="Reverse in CRM").count() == 1)
        ctx.close()
        ctx, page = self.open(browser, "ask-contrast", PHONE, sample={"answer": "- Atlas Settlement: markup due 23 Oct."})
        page.locator("#ask-btn").click()
        page.locator("[role=dialog] textarea").fill("What is due?")
        page.locator("[role=dialog] textarea").press("Enter")
        page.wait_for_timeout(200)
        res = page.evaluate(SCAN, ".sheet")
        self.check("ask-contrast", "the Ask answer passes contrast in light mode", not res["fails"], json.dumps(res["fails"][:2]))
        self.check("ask-contrast", "the finished answer is announced once for screen readers", "Atlas Settlement" in page.locator("#ask-status").text_content())
        ctx.close()
        for m in ("aditi", "kabir", "meera", "rohan", "tara", "vikram", "solo"):
            ctx, page = self.open(browser, "hero-banner", {"width": 380, "height": 844}, member=m, open_all=False, sample={"answer": "ok"}, mcp={"pages": ["Sign in to LinkedIn. Join now"]})
            page.wait_for_timeout(300)
            y = page.evaluate("(() => { var e = document.querySelector('.ah-hero-card .btn-primary'); return e ? e.getBoundingClientRect().bottom : 0; })()")
            self.check("hero-banner", f"{m}: with the research banner showing, the main button stays above the tab bar", y <= 784, f"bottom at {round(y)}px")
            wide = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            self.check("hero-banner", f"{m}: the banner never widens the page", wide <= 0, f"overflow {wide}px")
            ctx.close()

        for m in ("aditi", "kabir", "meera", "rohan", "tara", "vikram", "solo"):
            ctx, page = self.open(browser, "narrow-tabs", {"width": 320, "height": 700}, member=m, open_all=False)
            for tab in ("Today", "Pipeline", "People", "Portfolio", "LPs", "Ask"):
                b_ = page.locator(f"#bottom-tabs button[aria-label='{tab}']")
                if not b_.count():
                    continue
                b_.click()
                page.wait_for_timeout(60)
                wide = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
                self.check("narrow-tabs", f"{m} {tab}: fits a 320px screen", wide <= 0, f"overflow {wide}px")
            page.locator("#bottom-tabs button[aria-label='Today']").click()
            page.wait_for_timeout(60)
            hidden = page.evaluate("""(() => { var bar = document.getElementById('bottom-tabs').getBoundingClientRect().top, n = 0;
              var els = Array.from(document.querySelectorAll('#view button, #view a[href], #view input, #view textarea, #view select')).filter(e => e.offsetParent);
              els.forEach(e => { e.focus(); var r = e.getBoundingClientRect(); if (r.top >= bar - 1) n += 1; }); return n; })()""")
            self.check("narrow-tabs", f"{m}: no focused control hides under the tab bar", hidden == 0, f"{hidden} hidden")
            page.locator("#bottom-tabs button[aria-label='People']").click()
            page.wait_for_timeout(60)
            bad = page.evaluate("Array.from(document.querySelectorAll('.table-wrap')).filter(w => w.scrollWidth > w.clientWidth + 1 && w.getAttribute('tabindex') !== '0').length")
            self.check("narrow-tabs", f"{m}: a table that scrolls sideways can be reached by keyboard", bad == 0, f"{bad} unreachable")
            ctx.close()

        sc = "auto-apply"
        ctx, page = self.open(browser, sc, PHONE, state={"items": {}, "actions": {}, "settings": {"auto_apply": True}})
        self.check(sc, "in automatic mode a CRM change says it applies by itself, offers Apply now and Don't apply, and leaves the Decide count",
                   page.locator(DECIDE + " .status", has_text="Applies by itself").count() >= 1 and page.locator(DECIDE + " button", has_text="Apply now").count() >= 1
                   and page.locator(DECIDE + " button", has_text="Don't apply").count() >= 1 and page.locator(".daystrip .stat", has_text="+1 runs by itself").count() == 1)
        page.locator("#help-btn").click()
        seg = page.locator("[role=dialog] .seg[aria-label='CRM changes and calendar holds']")
        seg.locator("button", has_text="Ask me first").click()
        page.wait_for_timeout(80)
        w = [x for x in page.evaluate("window.__writes") if x.get("path") == "state/settings"]
        self.check(sc, "Help switches automatic mode off, saved for the hourly checks", bool(w) and (w[-1]["data"]["items"] or {}).get("auto_apply") is False, json.dumps(w[-1:])[:120])
        ctx.close()

    def run(self, only: set[str] | None = None) -> int:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for name in ("today", "done_undo", "prep", "tabs", "pipeline_actions", "approvals", "keyboard", "theme", "colours", "states", "levels",
                         "round6", "round7", "round8", "round9", "round10", "round11", "round12", "round13", "redesign", "round17"):
                if only and name not in only:
                    continue
                try:
                    getattr(self, name)(browser)
                except Exception as e:  # a crash is a failed check, not a crashed harness
                    self.check(name, "scenario ran", False, f"{type(e).__name__}: {str(e)[:200]}")
            browser.close()
        failed = [r for r in self.rows if not r["ok"]]
        import hashlib
        page_sha = hashlib.sha256(open(os.path.join(ROOT, "home", "index.html"), "rb").read()).hexdigest()[:12]
        name = "qa.json" if not only else "qa-" + "-".join(sorted(only)) + ".json"
        with open(os.path.join(self.out, name), "w", encoding="utf-8") as fh:
            json.dump({"checks": len(self.rows), "failed": len(failed), "complete": not only, "scenarios": sorted(only) if only else "all",
                       "page_sha256": page_sha, "rows": self.rows}, fh, indent=1)
        print(f"{len(self.rows) - len(failed)}/{len(self.rows)} checks pass")
        for r in failed:
            print(f"FAIL {r['scenario']}: {r['check']} {r['detail']}")
        return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "evals", "reports", "home"))
    ap.add_argument("--only")
    a = ap.parse_args()
    return QA(a.out).run(set(a.only.split(",")) if a.only else None)


if __name__ == "__main__":
    sys.exit(main())
