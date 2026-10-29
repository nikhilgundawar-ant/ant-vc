"""Safety rails that run on every output: sources, quiet deals, injected instructions, send tools."""

from __future__ import annotations

import os
import re
from typing import Any

INJECTION = [
    re.compile(r"\bignore (all |any |your |the )?(previous|prior|above|earlier)? ?(instructions|rules|prompts?)\b", re.I),
    re.compile(r"\b(disregard|override|bypass) (all |your |the )?(instructions|rules|guidelines|safety)\b", re.I),
    re.compile(r"\byou are (now|no longer)\s+(a|an|acting|in|free|my|bound|unrestricted|jailbroken|allowed)\b", re.I),
    re.compile(r"\b(system prompt|developer message|jailbreak mode|jailbroken)\b", re.I),
    re.compile(r"\b(assistant|claude|ai)[,:]?\s+(please\s+)?(forward|send|email|transfer|wire|export|share|delete)\b", re.I),
    re.compile(r"\b(forward|send|email) (this|all|every|the)\b[^.]{0,40}\b(to|at)\b[^.]{0,40}@", re.I),
    re.compile(r"\b(mark|score|rate) (this|us|our company)\b[^.]{0,30}\b(100|top|highest|priority|call)\b", re.I),
    re.compile(r"<\s*(script|iframe)\b", re.I),
    re.compile(r"\bBEGIN (INSTRUCTIONS|PROMPT)\b", re.I),
    # Imperatives aimed at the reader: at a sentence start or after "please", never "we will send the deck to all investors".
    re.compile(r"(?:^|[.!?:]\s+|\b(?:please|kindly)\s+)(?:forward|send|share|email)\b[^.]{0,40}\bto (?:all|every|everyone|everybody)\b", re.I | re.M),
    re.compile(r"\b(?:everyone|everybody|all contacts) in your (?:crm|contacts|address book|inbox)\b", re.I),
    re.compile(r"\breply with (?:your|the|all)\b[^.]{0,30}\b(?:phone|numbers|emails?|passwords?|contacts|credentials)\b", re.I),
    re.compile(r"\bshare your\b[^.]{0,30}\b(?:data room|access|credentials|passwords?|login)\b", re.I),
]

# Tools a skill must never call. Drafts are fine; sends are not.
FORBIDDEN_TOOLS = [
    "send_message", "gmail_send", "send_email", "Gmail__reply", "Gmail__forward", "`reply`", "`forward`", "send_draft",
    "update_draft", "trash_thread", "trash_message", "delete_event", "delete_draft", "mark_thread_spam", "slack_send_message",
    "slack_schedule_message", "respond_to_event", "share_file", "trash_file", "update_event",
]


def detect_injection(text: str) -> list[str]:
    hits = []
    for rx in INJECTION:
        m = rx.search(text or "")
        if m:
            hits.append(m.group(0))
    return hits


def check_sources(items: list[dict[str, Any]], field: str = "source_url") -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    keep, dropped = [], []
    for it in items:
        url = it.get(field) or (it.get("source") or {}).get("url")
        (keep if url else dropped).append(it)
    return keep, dropped


def filter_quiet(items: list[dict[str, Any]], quiet_ids: set[str], surface: str) -> list[dict[str, Any]]:
    """Quiet deals stay on the user's own Home only."""
    if surface == "home":
        return items
    return [it for it in items if not ({it.get("deal_id"), (it.get("entity") or {}).get("id")} & quiet_ids)]


NUM_RE = re.compile(r"(?<![A-Za-z])(?:[$₹])?\d[\d,]*(?:\.\d+)?(?:\s?(?:%|x|K|M|B|Cr|L|mn|bn))?")


def numbers_in(text: str) -> list[str]:
    out = []
    for m in NUM_RE.finditer(text or ""):
        token = m.group(0).strip()
        digits = re.sub(r"[^\d.]", "", token)
        if digits and digits not in ("0",) and len(digits.replace(".", "")) >= 1:
            out.append(token)
    return out


def _canon(num: str) -> str:
    return re.sub(r"[^\d.]", "", num).rstrip(".")


DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?(?:\s+\d{4})?\b|"
                     r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2}(?:,?\s+\d{4})?\b|"
                     r"\b(?:q[1-4]|h[12]|fy)\s?'?\d{2,4}\b|\b(?:19|20)\d{2}\b", re.I)
METRICS = {
    "arr": ("arr", "annual recurring", "run-rate", "run rate"), "mrr": ("mrr", "monthly recurring"), "revenue": ("revenue", "sales"), "burn": ("burn",),
    "cash": ("cash", "in the bank"), "runway": ("runway",), "churn": ("churn",), "margin": ("margin",),
    "growth": ("growth", "growing", "grew", "month on month", "mom"), "retention": ("nrr", "net revenue retention", "retention"),
    "volume": ("gmv", "tpv", "volume"), "cac": ("cac",), "valuation": ("valuation", "pre-money", "post-money"),
    "raise": ("raising", "raise", "round size"), "take_rate": ("take rate", "take-rate"),
    "customers": ("customers", "clients", "merchants", "platforms", "lenders", "banks", "brokers"),
}


def _blank_dates(text: str) -> str:
    return DATE_RE.sub(lambda m: " " * len(m.group(0)), text or "")


def _tokens(text: str) -> list[tuple[str, str, int, int]]:
    """(canonical value, unit, start, end) for each number, with dates blanked out first."""
    out = []
    for m in NUM_RE.finditer(_blank_dates(text)):
        tok = m.group(0).strip()
        val = _canon(tok)
        if not val or val in ("0",):
            continue
        low = tok.lower()
        unit = "%" if low.endswith("%") else "x" if low.endswith("x") else "$" if tok[:1] in "$₹" else ""
        mag = next((u for u in ("k", "m", "b", "cr", "l", "mn", "bn") if low.endswith(u)), "")
        out.append((val + mag, unit, m.start(), m.end()))
    return out


def _label_spans(text: str) -> list[tuple[int, int, str]]:
    """Metric words in the text as (start, end, metric), longest match first, so "net revenue retention" is not "revenue"."""
    found = sorted(((m.start(), m.end(), key) for key, words in METRICS.items() for w in words
                    for m in re.finditer(rf"\b{re.escape(w)}\b", text)), key=lambda x: -(x[1] - x[0]))
    kept: list[tuple[int, int, str]] = []
    for a, b, key in found:
        if not any(a < kb and b > ka for ka, kb, _ in kept):
            kept.append((a, b, key))
    return sorted(kept)


FAMILIES = [{"arr", "mrr", "revenue"}, {"burn", "runway", "cash"}, {"retention", "churn"}]
_BREAK = re.compile(r"[.;]\s|\n")


def _same_metric(a: str, b: str) -> bool:
    return a == b or any(a in fam and b in fam for fam in FAMILIES)


def _label_at(labels: list[tuple[int, int, str]], pos: int, end: int, text: str) -> str | None:
    """The metric a number belongs to, within its own sentence: a metric word right after it ("14 banks", "$2.4M ARR"),
    else the nearest one before it ("ARR: $2.4M", within 60 characters), else one shortly after it."""
    before, after = [], []
    for a, b, key in labels:
        if b <= pos and pos - b <= 60 and not _BREAK.search(text[b:pos]):
            before.append((pos - b, key))
        elif a >= end and a - end <= 25 and not _BREAK.search(text[end:a]):
            after.append((a - end if not text[end:a].strip() else 99, key))
    adjacent = [x for x in after if x[0] <= 2]
    after = [(d if d != 99 else 25, k) for d, k in after]
    if adjacent:
        return min(adjacent)[1]
    if before:
        return min(before)[1]
    return min(after)[1] if after else None


def check_memo(claims: Any, sources: dict[str, str]) -> dict[str, Any]:
    """Every claim needs a source id that exists. Every number in a claim must appear in that source, with the same unit,
    and, when the claim names a metric the source also names, next to that metric. Dates are not numbers here.
    A derived claim ("derived": true, "inputs": ["$4.1M", "$310K"]) is checked through its inputs."""
    if isinstance(claims, dict):
        claims = claims.get("claims") or []
    unlinked, invented = [], []
    for c in claims:
        if not isinstance(c, dict):
            continue
        sid_ = c.get("source_id")
        if not sid_ or sid_ not in sources:
            unlinked.append(c)
            continue
        src = sources[sid_] or ""
        src_tokens = _tokens(src)
        src_low = _blank_dates(src).lower()
        src_labels = _label_spans(src_low)
        claim_text = c.get("inputs") and " ".join(str(x) for x in c["inputs"]) if c.get("derived") else (c.get("text") or "")
        claim_low = _blank_dates(claim_text or "").lower()
        claim_labels = [] if c.get("derived") else _label_spans(claim_low)
        for val, unit, cpos, cend in _tokens(claim_text or ""):
            hits = [(pos, e) for v, u, pos, e in src_tokens if v == val and (u == unit or not unit or not u)]
            if not hits:
                invented.append({"claim": c.get("text"), "number": val, "source_id": sid_, "why": "not in the source"})
                continue
            clabel = _label_at(claim_labels, cpos, cend, claim_low)
            if clabel:
                labels = [_label_at(src_labels, pos, e, src_low) for pos, e in hits]
                if labels and all(lab and not _same_metric(lab, clabel) for lab in labels):
                    invented.append({"claim": c.get("text"), "number": val, "source_id": sid_,
                                     "why": f"in the source, but as {labels[0]}, not {clabel}"})
    return {"claims": len(claims), "unlinked": unlinked, "invented_numbers": invented, "ok": not unlinked and not invented}


def lint_skills(root: str) -> list[dict[str, Any]]:
    """Fail any skill text that tells Claude to call a send-, delete- or change-type tool. Claude itself has no exceptions.
    The one thing skills may name is Home's own capability manifest (`"server": "Gmail", "tools": ["send_message"]`), which
    lets the page send a draft only after the user taps Send and then Send now; Claude never calls the tool."""
    violations = []
    for folder, _, files in os.walk(root):
        if any(part in (".git", "evals", "__pycache__") for part in folder.split(os.sep)):
            continue
        for f in files:
            if not f.endswith(".md"):
                continue
            path = os.path.join(folder, f)
            check_text = open(path, encoding="utf-8").read()
            manifest_spans = [(x.start(), x.end()) for x in re.finditer(r'\{"server": "Gmail", "tools": \["send_message"\]\}', check_text)]
            for tool in FORBIDDEN_TOOLS:
                for m in re.finditer(re.escape(tool), check_text):
                    line = check_text[: m.start()].count("\n") + 1
                    context = check_text[max(0, m.start() - 80): m.end() + 80]
                    if tool == "send_message" and any(a <= m.start() < b for a, b in manifest_spans):
                        continue  # inside Home's capability manifest: the page, not Claude, after the user's two taps
                    if re.search(r"\b(never|do not|don't|must not|cannot|can't)\b[^.\n]{0,40}\b(call|calls|use|uses|run|runs|invoke|touch)\b[^.\n]{0,40}" + re.escape(tool), context, re.I) or \
                       re.search(r"\bno\b[^.\n]{0,20}" + re.escape(tool) + r"\b[^.\n]{0,10}\b(call|calls|ever)\b", context, re.I) or \
                       re.search(re.escape(tool) + r"[^.\n]{0,40}\b(is forbidden|never)\b", context, re.I):
                        continue  # a prohibition, not an instruction
                    violations.append({"file": os.path.relpath(path, root), "line": line, "tool": tool})
    return violations
