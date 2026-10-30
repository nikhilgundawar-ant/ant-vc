"""Design lint for ant. Home: Anthill Evergreen rules plus the artifact page contract.

Checks colours (tokens only), theme parity, radii, spacing, type floors and ceilings, fonts, the Anthill tile mark,
gradients and uppercase, and unsafe script patterns. Prints a report, or JSON with --json.

    python3 evals/design_lint.py [--file home/index.html] [--json]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARK = ('<rect width="1024" height="1024" rx="256" fill="#344C3D"/><rect x="8" y="8" width="1008" height="1008" rx="248" fill="none" '
        'stroke="#F4F6F2" stroke-opacity=".14" stroke-width="16"/><g transform="translate(143.4,155.6) scale(0.72)"><rect x="352" y="158" '
        'width="320" height="160" rx="80" fill="#F4F6F2"/><rect x="224" y="415" width="576" height="160" rx="80" fill="#9DB29A"/><rect x="96" '
        'y="672" width="832" height="160" rx="80" fill="#F4F6F2"/></g>')
RADII = {"999px", "16px", "12px", "9px", "3px", "0", "0px"}
# The 4px ladder plus the half-steps the Anthill component recipes use (agenda 10/14, hero 26/28/30, rail 10/14).
SPACING = {0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 40, 48, 64, 80, 96}
FONT_WEIGHTS = {"Raleway": {"200", "700"}, "Nunito": {"400", "600", "700", "800"}}
COLOR_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(")
SAFE_HOSTS = ("https://fonts.googleapis.com", "https://fonts.gstatic.com")


def split_parts(html: str) -> tuple[str, str, str]:
    css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S))
    js = "\n".join(re.findall(r"<script[^>]*>(.*?)</script>", html, re.S))
    markup = re.sub(r"<style[^>]*>.*?</style>|<script[^>]*>.*?</script>", "", html, flags=re.S)
    return css, js, markup


def css_rules(css: str) -> list[tuple[str, str]]:
    """Flatten CSS into (selector-with-context, declarations). Handles one level of @media nesting."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out: list[tuple[str, str]] = []
    i, n = 0, len(css)
    while i < n:
        j = css.find("{", i)
        if j < 0:
            break
        head = css[i:j].strip()
        depth, k = 1, j + 1
        while k < n and depth:
            depth += 1 if css[k] == "{" else -1 if css[k] == "}" else 0
            k += 1
        body = css[j + 1:k - 1]
        if head.startswith("@media") or head.startswith("@supports"):
            for sel, decl in css_rules(body):
                out.append((head + " " + sel, decl))
        elif head.startswith("@keyframes"):
            pass
        else:
            out.append((head, body))
        i = k
    return out


def decls(body: str) -> list[tuple[str, str]]:
    res = []
    for part in body.split(";"):
        if ":" in part:
            prop, val = part.split(":", 1)
            res.append((prop.strip().lower(), val.strip()))
    return res


DARK_SEL = ':root[data-ah-theme="dark"]'


def is_token_block(sel: str) -> bool:
    s = re.sub(r"\s+", " ", sel)
    return s in (":root", DARK_SEL)


# ---------------------------------------------------------------- contrast (WCAG 2.2)
def parse_colour(val: str) -> tuple[float, float, float, float] | None:
    val = val.strip()
    m = re.fullmatch(r"#([0-9a-fA-F]{6})", val)
    if m:
        h = m.group(1)
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 1.0)
    m = re.fullmatch(r"rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*(?:,\s*([\d.]+)\s*)?\)", val)
    if m:
        return (float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)) if m.group(4) else 1.0)
    return None


def over(top: tuple, bottom: tuple) -> tuple[float, float, float, float]:
    a = top[3]
    return (top[0] * a + bottom[0] * (1 - a), top[1] * a + bottom[1] * (1 - a), top[2] * a + bottom[2] * (1 - a), 1.0)


def luminance(c: tuple) -> float:
    def ch(v: float) -> float:
        v = v / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(c[0]) + 0.7152 * ch(c[1]) + 0.0722 * ch(c[2])


def ratio(fg: tuple, bg: tuple) -> float:
    a, b = luminance(fg), luminance(bg)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


# Every text and mark colour Home uses, on every surface it sits on. Text needs 4.5:1; marks and field edges 3:1.
TEXT_PAIRS = [
    ("--ah-ink", ["--ah-page", "--ah-surface", "--ah-modal", "--ah-surface-2", "--ah-tint", "--ah-breach-tint", "--ah-control-2"]),
    ("--ah-ink-2", ["--ah-page", "--ah-surface", "--ah-modal", "--ah-surface-2", "--ah-tint", "--ah-breach-tint", "--ah-control-2"]),
    ("--ah-ink-3", ["--ah-page", "--ah-surface", "--ah-modal"]),
    ("--ah-hero", ["--ah-page", "--ah-surface", "--ah-modal", "--ah-tint", "--ah-tint-hover", "--ah-control-2"]),
    ("--ah-breach-ink", ["--ah-page", "--ah-surface", "--ah-modal", "--ah-breach-tint"]),
    ("--ah-on-hero", ["--ah-hero"]),
    ("--ah-overlay-text", ["--ah-overlay-ink"]),
]
MARK_PAIRS = [
    ("--ah-hero-fill", ["--ah-surface", "--ah-track"]), ("--ah-breach-ink", ["--ah-surface", "--ah-track"]),
    ("--ah-field", ["--ah-surface", "--ah-modal"]), ("--ah-hero", ["--ah-page", "--ah-surface", "--ah-modal"]),
]


def contrast_report(tokens: dict[str, dict[str, str]]) -> list[dict]:
    """Each pair in each theme. A see-through token sits on the page or a card: both are checked and the worse counts."""
    rows = []
    for theme, toks in tokens.items():
        def solid(name: str, ground: str) -> tuple | None:
            c = parse_colour(toks.get(name, ""))
            if c is None:
                return None
            if c[3] >= 1:
                return c
            g = parse_colour(toks.get(ground, "")) or (255, 255, 255, 1.0)
            return over(c, g)
        for pairs, need, kind in ((TEXT_PAIRS, 4.5, "text"), (MARK_PAIRS, 3.0, "mark")):
            for fg, bgs in pairs:
                for bg in bgs:
                    worst = None
                    for ground in ("--ah-page", "--ah-surface", "--ah-modal"):
                        b = solid(bg, ground)
                        f = parse_colour(toks.get(fg, ""))
                        if b is None or f is None:
                            continue
                        f = over(f, b) if f[3] < 1 else f
                        r = ratio(f, b)
                        worst = r if worst is None else min(worst, r)
                    if worst is not None:
                        rows.append({"theme": theme, "kind": kind, "fg": fg, "bg": bg, "ratio": round(worst, 2), "need": need, "ok": worst >= need})
    return rows


def px_values(val: str) -> list[float]:
    val = re.sub(r"env\([^)]*\)", "", val)
    return [float(x) for x in re.findall(r"(-?\d+(?:\.\d+)?)px", val)]


def lint(path: str) -> dict:
    html = open(path, encoding="utf-8").read()
    # Vendored libraries (jsPDF, MIT) ride inside the page as text and are not Home's own code: they are not linted.
    html = re.sub(r'<script type="text/plain" id="ah-[a-z]+">.*?</script>', "", html, flags=re.S)
    v: list[str] = []
    css, js, markup = split_parts(html)
    rules = css_rules(css)

    # 1. Page contract
    if re.search(r"<!doctype|<html[\s>]|<head[\s>]|<body[\s>]", html, re.I):
        v.append("contract: page must not carry its own doctype, html, head or body tags")
    if not re.search(r"<title>[^<]{2,60}</title>", html[:8192]):
        v.append("contract: <title> missing from the first 8 KB")
    if 'name="claude:viewport-fit-sides" content="cover"' not in html:
        v.append("contract: viewport-fit-sides meta missing")
    if "max(16px, env(safe-area-inset-left, 0px))" not in css or "max(16px, env(safe-area-inset-right, 0px))" not in css:
        v.append("contract: side gutter max(16px, env(safe-area-inset-*)) missing")
    for href in re.findall(r'<link[^>]+href="([^"]+)"', markup):
        if not href.startswith(SAFE_HOSTS):
            v.append(f"contract: stylesheet or preconnect from a host outside Google Fonts: {href}")
    for src in re.findall(r'<script[^>]+src="([^"]+)"', html):
        v.append(f"contract: external script {src} (Home loads none)")
    body_bg = any(sel.strip() == "body" and any(p == "background" and "var(--" in val for p, val in decls(b)) for sel, b in rules)
    if not body_bg:
        v.append("contract: body needs an explicit token background")

    # 2. Fonts
    fam = re.search(r"fonts\.googleapis\.com/css2\?([^\"']+)", markup)
    if fam:
        for name, weights in re.findall(r"family=([A-Za-z+]+):wght@([0-9;]+)", fam.group(1)):
            name = name.replace("+", " ")
            if name not in FONT_WEIGHTS:
                v.append(f"type: third family loaded: {name}")
                continue
            extra = set(weights.split(";")) - FONT_WEIGHTS[name]
            if extra:
                v.append(f"type: {name} weights outside the system: {sorted(extra)}")
    for sel, body in rules:
        if is_token_block(sel) or sel.strip() == "@font-face":  # a face that ships inside the page declares its name
            continue
        for prop, val in decls(body):
            if prop == "font-family" and val not in ("var(--ah-display)", "var(--ah-body)", "inherit"):
                v.append(f"type: font-family outside the tokens in '{sel}': {val}")

    # 3. Colour only through tokens
    for sel, body in rules:
        if is_token_block(sel):
            continue
        for prop, val in decls(body):
            if COLOR_RE.search(val):
                v.append(f"colour: literal colour in '{sel}' {prop}: {val[:60]}")
    if COLOR_RE.search(js):
        for m in COLOR_RE.finditer(js):
            v.append(f"colour: literal colour in script near '{js[max(0, m.start() - 30):m.end() + 10].strip()}'")
    markup_no_mark = re.sub(r'<svg class="ah-mark".*?</svg>', "", markup, flags=re.S)
    for m in COLOR_RE.finditer(markup_no_mark):
        v.append(f"colour: literal colour in markup near '{markup_no_mark[max(0, m.start() - 30):m.end() + 10].strip()}'")
    if re.search(r"(linear|radial|conic)-gradient", css + js):
        v.append("colour: gradient found (Anthill never uses gradients)")

    # 4. Themes: light is the default on every device (the owner asked for it); dark is a remembered choice.
    light, dark = {}, {}
    for sel, body in rules:
        s = re.sub(r"\s+", " ", sel)
        vals = {p: val for p, val in decls(body) if p.startswith("--")}
        if s == ":root":
            light.update(vals)
        elif s == DARK_SEL:
            dark.update(vals)
    if "prefers-color-scheme: dark" in css:
        v.append("theme: light is the default; no prefers-color-scheme dark block")
    if not dark:
        v.append(f"theme: the dark choice needs its token block ({DARK_SEL})")
    if set(dark) - set(light):
        v.append(f"theme: tokens only defined in dark: {sorted(set(dark) - set(light))}")
    colour_tokens = {k for k, val in light.items() if COLOR_RE.search(val) and not k.startswith("--ah-elev")}
    if colour_tokens - set(dark) - {"--ah-sage", "--ah-mid-sage", "--ah-breach"}:
        v.append(f"theme: colour tokens dark does not redefine: {sorted(colour_tokens - set(dark) - {'--ah-sage', '--ah-mid-sage', '--ah-breach'})}")
    if 'id="theme-btn"' not in markup:
        v.append("theme: the header needs the light and dark switch")
    if not re.search(r'localStorage\.getItem\("instinct\.theme"\)', html.split("<div class=\"ah-shell\">")[0]):
        v.append("theme: the saved choice must apply before the page paints (inline script above the shell)")
    used = set(re.findall(r"var\((--[a-z0-9-]+)", css + js))
    if used - set(light):
        v.append(f"theme: tokens used but never defined: {sorted(used - set(light))}")
    dark_full = {**light, **dark}
    for row in contrast_report({"light": light, "dark": dark_full}):
        if not row["ok"]:
            v.append(f"contrast: {row['theme']} {row['kind']} {row['fg']} on {row['bg']} is {row['ratio']}:1 (needs {row['need']})")

    # 5. Radii, spacing, type. A media-query rule inherits family and weight from the base rule for the same selector.
    base_type: dict[str, tuple[str | None, str | None]] = {}
    for sel, body in rules:
        if is_token_block(sel):
            continue
        base_sel = re.sub(r"^@media[^)]*\)(\s*and\s*\([^)]*\))*\s*", "", sel).strip()
        family, weight = base_type.get(base_sel, (None, None))
        sizes: list[float] = []
        for prop, val in decls(body):
            if prop == "border-radius":
                for part in val.split():
                    if part not in RADII:
                        v.append(f"radius: {part} in '{sel}' (allowed 999, 16, 12, 9, 3, 0)")
            if prop in ("gap", "row-gap", "column-gap") or prop.startswith("padding") or prop.startswith("margin"):
                for x in px_values(val):
                    if abs(x) not in SPACING:
                        v.append(f"spacing: {x:g}px in '{sel}' {prop} is off the ladder")
            if prop == "font-family":
                family = "display" if "--ah-display" in val else "body"
            if prop == "font-weight":
                weight = val
            if prop == "font-size":
                sizes += px_values(val)
            if prop == "text-transform" and "uppercase" in val:
                v.append(f"type: uppercase in '{sel}' (only the agent label is uppercase)")
        if not sel.startswith("@media"):
            base_type[base_sel] = (family, weight)
        for s in sizes:
            if s < 11.5:
                v.append(f"type: {s:g}px text in '{sel}' is under the 11.5px floor")
            if family == "display" and weight == "200" and s < 26:
                v.append(f"type: Raleway 200 at {s:g}px in '{sel}' (floor 26px)")
            if family == "display" and weight == "700" and s < 17:
                v.append(f"type: Raleway 700 at {s:g}px in '{sel}' (floor 17px)")
            if family != "display" and s > 26:
                v.append(f"type: Nunito at {s:g}px in '{sel}' (ceiling 26px)")
    for m in re.finditer(r"font-size:\s*([\d.]+)px", js + markup):
        if float(m.group(1)) < 11.5:
            v.append(f"type: inline {m.group(1)}px text under the floor")

    # 6. The mark: the exact Evergreen tile, 24px, never bare strata
    marks = re.findall(r'<svg class="ah-mark"[^>]*>(.*?)</svg>', markup, re.S)
    if not marks:
        v.append("mark: the Anthill tile mark is missing")
    for inner in marks:
        if inner.strip() != MARK:
            v.append("mark: tile SVG differs from the Evergreen master")
    if not re.search(r"\.ah-mark\s*\{[^}]*width:\s*24px[^}]*height:\s*24px", css):
        v.append("mark: .ah-mark must render at 24px")

    # 7. Script safety: text nodes only, safe links, no blocked dialogs
    for pat, why in ((r"\.innerHTML|\.outerHTML|insertAdjacentHTML|document\.write", "HTML injection sink"),
                     (r"\beval\(|new Function\(", "dynamic code"), (r"\balert\(|\bconfirm\(|\bprompt\(|window\.print", "blocked dialog"),
                     (r"window\.open\(", "window.open (use real links)")):
        if re.search(pat, js):
            v.append(f"script: {why}")
    for m in re.finditer(r"href:\s*([^,}]+)", js):
        if not m.group(1).strip().startswith("safeUrl("):
            v.append(f"script: link not passed through safeUrl: {m.group(1).strip()[:40]}")
    if "localStorage" in js and not re.search(r"try\s*\{[^}]*localStorage", js):
        v.append("script: localStorage access must sit inside try/catch")

    return {"file": os.path.relpath(path, ROOT), "violations": v, "rules": len(rules)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=os.path.join(ROOT, "home", "index.html"))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    res = lint(a.file)
    if a.json:
        print(json.dumps(res, indent=1))
    else:
        print(f"{res['file']}: {res['rules']} CSS rules, {len(res['violations'])} violations")
        for x in res["violations"]:
            print("  -", x)
    return 0 if not res["violations"] else 1


if __name__ == "__main__":
    sys.exit(main())
