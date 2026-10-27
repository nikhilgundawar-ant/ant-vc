"""Inbound triage: score a company against the firm's thesis and check the pass log.

Claude reads the pitch and extracts attributes; this module scores them the same
way every time, so a decision always comes with its reasons.
"""

from __future__ import annotations

import re
from typing import Any

from .names import strip_accents
from .util import acronyms, clip, fmt_date, money, parse_date, sid

CALL_AT = 70
INFO_AT = 45

# Adjacent on their own: these are financial services by name.
ADJACENT_SECTORS = ["fintech", "insurtech", "wealthtech", "lending marketplace", "fintech marketplace"]
# Jobs any company has: software for them is not financial software, whoever buys it.
GENERIC_JOB = re.compile(r"\b(data (infrastructure|platform|pipelines?|warehouse|stack)|analytics|business intelligence|ai (platform|infrastructure|agents?)|"
                         r"machine learning platform|ml platform|cyber ?security|security|identity and access|hr|recruiting|crm|marketing|"
                         r"sales enablement|devtools?|developer tools?|collaboration|observability|monitoring|customer support)\b", re.I)
# Generic software counts as adjacent only when it serves financial services.
GENERIC_SECTORS = ["b2b saas", "saas", "enterprise software", "proptech", "devtools", "data infrastructure", "ai infrastructure",
                   "b2b marketplace", "logistics software"]
FIN_HOOK = re.compile(r"\b(banks?|banking|nbfcs?|lenders?|lending|credit|bureaus?|payments?|payables?|accounts payable|receivables|"
                      r"treasury|finance|financial|fintech|insurance|insurers?|wealth|brokers?|accounting|invoices?|compliance|kyc|fraud)\b")
STAGE_ALIASES = {
    "pre-seed": ["pre-seed", "preseed", "pre seed", "angel"],
    "seed": ["seed", "seed+", "seed plus", "seed extension", "bridge to a"],
    "series a": ["series a", "series-a", "pre-series a", "pre-a", "pre a", "a round"],
    "series b": ["series b", "series-b", "b round"],
    "series c+": ["series c", "series d", "growth", "series e", "late stage"],
}
SIGNAL_WORDS = [
    (re.compile(r"\b(repeat|second-time|serial|2x|third-time) founder", re.I), 4, "repeat founder"),
    (re.compile(r"\bex[- ]?(stripe|razorpay|paytm|phonepe|google|amazon|goldman|jp ?morgan|hdfc|icici|visa|mastercard|cred|zerodha|slice|juspay|flipkart|uber|meta)\b", re.I), 3, "strong operator background"),
    (re.compile(r"\b(arr|mrr|revenue|run[- ]rate)\b[^.]{0,30}\$?₹?\d|[$₹]\s?\d[\d.,]*\s?(k|m|mn|million|cr|crore)?\s*(annuali[sz]ed\s+)?(arr|mrr|revenue|run[- ]rate)\b", re.I), 3, "revenue"),
    (re.compile(r"\b(live with|in production at|deployed at|signed)\b", re.I), 2, "live deployments"),
    (re.compile(r"\b(\d{2,3})%\s*(mom|month on month|month-over-month)\b", re.I), 2, "fast growth"),
]

NUMBER_WORDS = r"\d[\d,]*|several|a dozen|dozens|two|three|four|five|six|seven|eight|nine|ten|twelve|fifteen|twenty"
CUSTOMERS_RE = re.compile(rf"\b({NUMBER_WORDS})\b[^.]{{0,24}}\b(banks|nbfcs|lenders|insurers|brokers|customers|clients|hospitals|merchants|"
                          r"retail chains|exporters|advisors|enterprises)\b", re.I)


def _norm(text: Any) -> str:
    return strip_accents(str(text or "")).lower()


def _company_key(name: str) -> str:
    n = _norm(name)
    n = re.sub(r"\b(labs?|technologies|technology|tech|pvt|private|ltd|limited|inc|llc|corp|corporation|ai|hq|app)\b", " ", n)
    return re.sub(r"[^a-z0-9]+", "", n)


def stage_key(stage_text: Any) -> str | None:
    t = _norm(stage_text)
    if not t:
        return None
    for key, aliases in STAGE_ALIASES.items():
        if any(a == t or a in t for a in aliases):
            if key == "seed" and ("pre-seed" in t or "preseed" in t or "pre seed" in t):
                return "pre-seed"
            if key == "series a" and ("pre-series a" in t or "pre-a" in t or "pre a" in t):
                return "series a"
            return key
    return None


REGIONS = {
    "india": ["india", "bangalore", "bengaluru", "mumbai", "delhi", "new delhi", "gurgaon", "gurugram", "pune", "hyderabad", "chennai",
              "noida", "kochi", "kolkata", "jaipur", "indore", "ahmedabad", "chandigarh", "lucknow", "coimbatore", "nagpur", "surat",
              "bhubaneswar", "thiruvananthapuram", "mysuru", "visakhapatnam"],
    "united states": ["us", "usa", "u.s.", "united states", "america", "san francisco", "new york", "nyc", "sf", "bay area", "delaware",
                      "california", "seattle", "austin", "boston", "los angeles", "chicago", "miami", "denver", "atlanta", "palo alto"],
    "canada": ["canada", "toronto", "vancouver", "montreal", "waterloo"],
    "united kingdom": ["uk", "u.k.", "united kingdom", "england", "london", "manchester", "edinburgh", "cambridge", "oxford", "bristol"],
    "europe": ["europe", "eu", "germany", "berlin", "munich", "france", "paris", "netherlands", "amsterdam", "spain", "madrid", "barcelona",
               "sweden", "stockholm", "denmark", "copenhagen", "finland", "helsinki", "ireland", "dublin", "portugal", "lisbon",
               "switzerland", "zurich", "italy", "milan", "poland", "warsaw", "estonia", "tallinn", "belgium", "brussels", "austria", "vienna"],
    "southeast asia": ["southeast asia", "sea", "singapore", "indonesia", "jakarta", "vietnam", "ho chi minh", "hanoi", "thailand",
                       "bangkok", "malaysia", "kuala lumpur", "philippines", "manila"],
    "middle east": ["middle east", "mena", "uae", "dubai", "abu dhabi", "saudi", "riyadh", "qatar", "doha", "bahrain", "israel", "tel aviv"],
    "africa": ["africa", "nigeria", "lagos", "kenya", "nairobi", "south africa", "cape town", "johannesburg", "egypt", "cairo", "ghana", "accra"],
    "latin america": ["latin america", "latam", "brazil", "sao paulo", "mexico", "mexico city", "argentina", "buenos aires", "colombia",
                      "bogota", "chile", "santiago", "peru", "lima"],
    "australia": ["australia", "sydney", "melbourne", "new zealand", "auckland", "anz"],
}
GLOBAL_WORDS = ("global", "anywhere", "worldwide", "any geography")
REGION_LABEL = {"united states": "US", "united kingdom": "UK", "us": "US", "uk": "UK", "uae": "UAE", "eu": "EU", "sea": "Southeast Asia"}


def regions_in(text: Any) -> set[str]:
    t = _norm(text)
    found = set()
    for region, words in REGIONS.items():
        if any(re.search(rf"(?<![a-z]){re.escape(w)}(?![a-z])", t) for w in words):
            found.add(region)
    if "united kingdom" in found:
        found.add("europe")
    return found


def _label(region: str) -> str:
    if "-" in str(region):
        return "-".join(_label(part) for part in str(region).split("-"))  # "us-india" reads "US-India"
    return REGION_LABEL.get(region, region.title())


def where_we_invest(geos: list[Any]) -> str:
    """The thesis regions in words a founder reads: "companies building in India, or US companies with a team in India"."""
    out = []
    for g in [str(x).strip().lower() for x in geos or [] if str(x).strip()]:
        if "-" in g:
            a, b = g.split("-", 1)
            out.append(f"{_label(a)} companies with a team in {_label(b)}")
        else:
            out.append(f"companies building in {_label(g)}")
    return ", or ".join(out)


def geo_fit(company: dict[str, Any], thesis: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    """15 when the company sits in a thesis region, or in both ends of a thesis corridor ("us-india").
    0 outside, including one end of a corridor with no link to the other. No thesis geographies: no penalty."""
    geos = [str(g) for g in (thesis.get("geographies") or []) if str(g).strip()]
    where = company.get("geography") or company.get("hq") or ""
    if not geos or any(w in _norm(g) for g in geos for w in GLOBAL_WORDS):
        return 15, {"ok": True, "text": "Geography open"}
    have = regions_in(where)
    primary: set[str] = set()
    corridors: list[set[str]] = []
    for g in geos:
        rs = regions_in(g.replace("-", " "))
        if len(rs - {"europe"} if "united kingdom" in rs else rs) >= 2:
            corridors.append(rs)
        else:
            primary |= rs
    if have & primary:
        return 15, {"ok": True, "text": f"In our geography: {', '.join(_label(r) for r in sorted(have & primary))}"}
    for c in corridors:
        if c <= have:
            return 15, {"ok": True, "text": " and ".join(_label(r) for r in sorted(c)) + " link"}
    for c in corridors:
        if have & c:
            here = sorted(have & c)[0]
            other = sorted(c - have)[0]
            return 0, {"ok": False, "text": f"Outside our geographies: {_label(here)} only, no {_label(other)} link"}
    return 0, {"ok": False, "text": f"Outside our geographies: {where or 'unknown'}"}


def score(company: dict[str, Any], thesis: dict[str, Any]) -> dict[str, Any]:
    reasons: list[dict[str, Any]] = []
    text_blob = " ".join(_norm(company.get(k)) for k in ("sector", "description", "product", "customers", "hq", "geography", "team", "traction"))
    text_blob += " " + " ".join(_norm(t) for t in (company.get("sector_tags") or []))

    # Sector, 40.
    keywords = [_norm(k) for k in (thesis.get("sector_keywords") or [])] + [_norm(s) for s in (thesis.get("sectors") or [])]
    sector_hit = next((k for k in keywords if k and re.search(rf"\b{re.escape(k)}\b", text_blob)), None)
    # The product's job is what comes before "for"; who buys it comes after. A finance word only in the buyer
    # ("data infrastructure for credit bureaus") makes generic software adjacent, not in thesis.
    what = _norm(company.get("sector")).split(" for ")[0]
    if sector_hit and what and GENERIC_JOB.search(what) and not any(k and re.search(rf"\b{re.escape(k)}\b", what) for k in keywords):
        s_sector = 15
        reasons.append({"ok": False, "text": f"Adjacent to thesis: {what} sold to {sector_hit} firms"})
    elif sector_hit:
        s_sector = 40
        reasons.append({"ok": True, "text": f"In thesis: {sector_hit}"})
    else:
        adj = next((a for a in ADJACENT_SECTORS if re.search(rf"\b{re.escape(a)}\b", text_blob)), None)
        if not adj and FIN_HOOK.search(text_blob):
            adj = next((a for a in GENERIC_SECTORS if re.search(rf"\b{re.escape(a)}\b", text_blob)), None)
        s_sector = 15 if adj else 0
        reasons.append({"ok": False, "text": f"Adjacent to thesis: {adj}" if adj else "Outside thesis sectors"})

    # Stage, 20.
    sk = stage_key(company.get("stage"))
    wanted = [stage_key(s) for s in (thesis.get("stages") or [])]
    if sk and sk in wanted:
        s_stage = 20
        reasons.append({"ok": True, "text": f"Stage fits: {sk}"})
    elif sk == "series b":
        s_stage = 5
        reasons.append({"ok": False, "text": "Later than our stage: Series B"})
    else:
        s_stage = 0
        reasons.append({"ok": False, "text": f"Stage outside thesis: {sk}" if sk else "Stage unknown"})

    # Round size vs our check, 15.
    raise_usd = company.get("raise_usd")
    lo, hi = thesis.get("check_min_usd") or 500_000, thesis.get("check_max_usd") or 3_000_000
    if raise_usd is None:
        s_check = 5
        reasons.append({"ok": False, "text": "Round size not stated"})
    elif lo <= raise_usd <= 4 * hi:
        s_check = 15
        reasons.append({"ok": True, "text": f"Round of {money(raise_usd)}: room for our {money(lo)} to {money(hi)} check"})
    elif raise_usd <= 6 * hi:
        s_check = 8
        reasons.append({"ok": False, "text": f"Round of {money(raise_usd)} is at the edge of our check size"})
    else:
        s_check = 0
        reasons.append({"ok": False, "text": f"Round of {money(raise_usd)} does not fit our check size"})

    # Geography, 15. Regions come from the thesis: "india", "us-india" (a corridor), "europe", "global" and so on.
    s_geo, geo_reason = geo_fit(company, thesis)
    reasons.append(geo_reason)

    # Team and traction signals, 10.
    s_sig, sig_labels = 0, []
    for rx, w, label in SIGNAL_WORDS:
        if rx.search(text_blob):
            s_sig += w
            sig_labels.append(label)
    # Paying customers: a count of customers, never a pilot, and never people "on the platform" (they may pay nothing).
    # Judged on each count and the words right around it: "40 paying customers and 1,200 users" still counts the 40.
    for m in CUSTOMERS_RE.finditer(text_blob):
        near = text_blob[max(0, m.start() - 20): m.end() + 28].lower()
        own = m.group(0).lower() + text_blob[m.end(): m.end() + 28].lower()
        if "pilot" in near or "trial" in near or \
                re.search(r"\b(on the platform|on our platform|signed up|sign-ups|sign ups|waitlist|downloads|free|unpaid|onboarded|registered)\b", own):
            continue
        s_sig += 3
        sig_labels.append("paying customers")
        break
    s_sig = min(10, s_sig)
    if sig_labels:
        reasons.append({"ok": True, "text": "Signals: " + ", ".join(sorted(set(sig_labels)))})

    total = s_sector + s_stage + s_check + s_geo + s_sig
    # Gates a partner would apply before reading further.
    if s_sector == 0:
        total = min(total, 40)
    elif s_sector < 40:
        total = min(total, 65)
    if s_geo == 0:
        total = min(total, 40)
    elif s_geo < 15:
        total = min(total, 60)
    if sk in ("series b", "series c+") and raise_usd and raise_usd > 4 * hi:
        total = min(total, 40)
        reasons.insert(0, {"ok": False, "text": f"Later stage and a larger round than we lead: {money(raise_usd)} {sk.title()}"})
    anti = next((a for a in (thesis.get("anti_patterns") or []) if re.search(rf"\b{re.escape(_norm(a))}\b", text_blob)), None)
    if anti:
        total = min(total, 25)
        reasons.insert(0, {"ok": False, "text": f"Anti-pattern: {acronyms(anti)}"})
    decision = "call" if total >= CALL_AT else "more_info" if total >= INFO_AT else "pass"
    return {"score": int(total), "decision": decision, "anti_pattern": anti, "reasons": reasons,
            "parts": {"sector": s_sector, "stage": s_stage, "check": s_check, "geography": s_geo, "signals": s_sig}}


def pass_log_hit(company: dict[str, Any], passes: list[dict[str, Any]]) -> dict[str, Any] | None:
    key = _company_key((company.get("name") or ""))
    dom = _norm(company.get("domain"))
    for p in passes:
        if dom and _norm(p.get("domain")) == dom:
            return p
        if key and _company_key((p.get("company") or "")) == key:
            return p
    return None


def _short_phrase(text: str, n: int) -> str:
    """At most n characters, ending on a whole phrase, never an ellipsis: "treasury management for Indian exporters
    and importers" reads "treasury management for Indian exporters"."""
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= n:
        return text
    head = text[:n + 1]
    cut = max((head.rfind(w) for w in (" and ", " for ", " with ", " that ", " to ", " in ", " of ", " on ")), default=-1)
    out = text[:cut] if cut > n // 3 else head[:head.rfind(" ")] if " " in head else head[:n]
    return re.sub(r"\s+(and|for|with|that|to|in|of|on|the|a|an)$", "", out.strip(" ,;:-"), flags=re.I)


def _facts(c: dict[str, Any]) -> str:
    """One short line a partner can scan: stage, round, what they build, where."""
    parts = []
    if c.get("stage"):
        parts.append(str(c["stage"]).strip().title().replace("Pre-Seed", "Pre-seed"))
    if c.get("raise_usd"):
        parts.append(money(c["raise_usd"]))
    sector = re.split(r"[,;(]", str(c.get("sector") or ""))[0].strip()
    if sector:
        parts.append(_short_phrase(sector, 48))
    hq = _places(c.get("hq"))
    if hq:
        parts.append(hq)
    return ", ".join(parts)


def _places(hq: Any) -> str:
    """Each place a pitch names, by its city or state: "Delaware, US and Bangalore, India" is "Delaware and Bangalore"."""
    places = [p.split(",")[0].strip() for p in re.split(r"\s+(?:and|&)\s+|\s*[;/|]\s*", str(hq or "")) if p.strip()]
    places = [p for i, p in enumerate(places) if p and p not in places[:i]][:2]
    return " and ".join(places)


def _revisit_check(chk: Any) -> dict[str, Any] | None:
    """Claude's reading of a returning pitch against the revisit condition: met true or false, with the evidence."""
    if not isinstance(chk, dict) or chk.get("met") not in (True, False):
        return None
    return {"met": chk["met"], "evidence": clip(str(chk.get("evidence") or ""), 140)}


def triage(companies: list[dict[str, Any]], thesis: dict[str, Any], passes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for c in companies:
        res = score(c, thesis)
        if c.get("injection_flag") and res["decision"] == "call":
            # An email that hides instructions for AI tools never earns "book a call" on its own: a person reads it first.
            res = {**res, "decision": "more_info",
                   "reasons": [{"ok": False, "text": "Hidden instructions for AI tools: read it yourself before booking"}] + res["reasons"]}
        hit = pass_log_hit(c, passes)
        note = None
        if hit:
            when = parse_date(hit.get("date"))
            note = f"We passed on {fmt_date(when)}: {hit.get('reason')}"
            if hit.get("revisit_trigger"):
                note += f". Revisit if: {hit['revisit_trigger']}"
        out.append({
            "id": sid("inbound", c.get("thread_id") or c.get("name"), prefix="i"), "company": c.get("name"),
            "domain": c.get("domain"), "thread_id": c.get("thread_id"), "source_url": c.get("source_url"),
            "from": c.get("from"), "score": res["score"], "decision": res["decision"], "reasons": res["reasons"],
            "anti_pattern": res["anti_pattern"], "pass_log": note, "parts": res["parts"],
            "pass_date": (hit or {}).get("date"), "pass_reason": (hit or {}).get("reason"), "revisit_trigger": (hit or {}).get("revisit_trigger"),
            "revisit_check": _revisit_check(c.get("revisit_check")) if hit else None,
            "injection_flag": bool(c.get("injection_flag")), "injection_quote": c.get("injection_quote"), "facts": _facts(c),
        })
    out.sort(key=lambda r: -r["score"])
    return out


def suggest_thesis(portfolio: list[dict[str, Any]], passes: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate what the firm actually invested in, for Claude to turn into a thesis the user confirms."""
    from collections import Counter
    sectors: Counter[str] = Counter()
    stages: Counter[str] = Counter()
    geos: Counter[str] = Counter()
    checks = []
    for c in portfolio:
        for s in (c.get("sectors") or []) or []:
            sectors[_norm(s)] += 1
        if c.get("entry_stage"):
            stages[stage_key(c["entry_stage"]) or _norm(c["entry_stage"])] += 1
        if c.get("hq"):
            geos[_norm(c["hq"]).split(",")[-1].strip()] += 1
        if c.get("check_usd"):
            checks.append(c["check_usd"])
    reasons: Counter[str] = Counter(_norm(p.get("reason")) for p in passes if p.get("reason"))
    checks.sort()
    return {
        "top_sectors": sectors.most_common(6), "top_stages": stages.most_common(4), "top_geographies": geos.most_common(4),
        "check_range_usd": [checks[0], checks[-1]] if checks else None,
        "check_median_usd": checks[len(checks) // 2] if checks else None,
        "common_pass_reasons": reasons.most_common(6),
    }
