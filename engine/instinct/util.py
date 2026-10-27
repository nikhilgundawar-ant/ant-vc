"""Small shared helpers: ids, dates, emails, words, JSON IO."""

from __future__ import annotations

import hashlib
import json
import os
import re
import unicodedata
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Iterable
from zoneinfo import ZoneInfo

FREEMAIL = {
    "gmail.com", "googlemail.com", "yahoo.com", "yahoo.co.in", "outlook.com", "hotmail.com",
    "live.com", "icloud.com", "me.com", "proton.me", "protonmail.com", "rediffmail.com",
    "aol.com", "zoho.com", "zohomail.in", "fastmail.com", "hey.com",
}

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


# ---------------------------------------------------------------- JSON IO

def load(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def dump(obj: Any, path: str) -> str:
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False, default=_json_default)
        fh.write("\n")
    return path


def _json_default(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, set):
        return sorted(value)
    raise TypeError(f"not JSON serialisable: {type(value).__name__}")


# ---------------------------------------------------------------- ids

def sid(*parts: Any, prefix: str = "") -> str:
    """A short stable id from the natural key, so a record keeps its id across runs."""
    raw = "|".join("" if p is None else str(p).strip().lower() for p in parts)
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]
    return f"{prefix}{digest}" if not prefix or prefix.endswith("_") else f"{prefix}_{digest}"


def slug(text: str, limit: int = 48) -> str:
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return text[:limit] or "x"


# ---------------------------------------------------------------- dates

def tzinfo(name: str | None) -> ZoneInfo:
    try:
        return ZoneInfo(name or "UTC")
    except Exception:  # unknown zone name: fall back to UTC rather than crash a scheduled run
        return ZoneInfo("UTC")


def parse_dt(value: Any, tz: str | None = None) -> datetime | None:
    """Parse ISO datetimes and dates. Naive values are read in `tz`."""
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, date):
        dt = datetime.combine(value, time(0, 0))
    else:
        text = str(value).strip().replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            try:
                dt = datetime.combine(date.fromisoformat(text[:10]), time(0, 0))
            except ValueError:
                return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tzinfo(tz))
    return dt


def parse_date(value: Any, tz: str | None = None) -> date | None:
    dt = parse_dt(value, tz)
    if dt is None:
        return None
    if tz:
        dt = dt.astimezone(tzinfo(tz))
    return dt.date()


def days_between(earlier: date | None, later: date | None) -> int | None:
    if earlier is None or later is None:
        return None
    return (later - earlier).days


def fmt_date(d: date | datetime | None) -> str:
    """Anthill date style: 02 Jul 2026."""
    if d is None:
        return "—"
    if isinstance(d, datetime):
        d = d.date()
    return f"{d.day:02d} {MONTHS[d.month - 1]} {d.year}"


def fmt_short_date(d: date | datetime | None) -> str:
    if d is None:
        return "—"
    if isinstance(d, datetime):
        d = d.date()
    return f"{d.day:02d} {MONTHS[d.month - 1]}"


def fmt_time(dt: datetime | None, tz: str | None = None) -> str:
    if dt is None:
        return "—"
    if tz:
        dt = dt.astimezone(tzinfo(tz))
    return f"{dt.hour:02d}:{dt.minute:02d}"


def local_now(now: Any, tz: str) -> datetime:
    dt = parse_dt(now, tz) if now else datetime.now(timezone.utc)
    return dt.astimezone(tzinfo(tz))


# ---------------------------------------------------------------- emails

def norm_email(email: str | None) -> str:
    """Lowercase; for Gmail drop dots and +tags, since Gmail ignores them."""
    if not email:
        return ""
    email = email.strip().lower()
    if "@" not in email:
        return email
    local, domain = email.rsplit("@", 1)
    local = local.split("+", 1)[0]
    if domain in ("gmail.com", "googlemail.com"):
        local = local.replace(".", "")
        domain = "gmail.com"
    return f"{local}@{domain}"


def domain_of(email: str | None) -> str:
    if not email or "@" not in email:
        return ""
    return email.rsplit("@", 1)[1].strip().lower()


def is_freemail(domain_or_email: str | None) -> bool:
    if not domain_or_email:
        return False
    domain = domain_of(domain_or_email) if "@" in domain_or_email else domain_or_email.lower()
    return domain in FREEMAIL


# ---------------------------------------------------------------- text

WORD_RE = re.compile(r"[A-Za-z0-9À-ɏ][A-Za-z0-9À-ɏ'’.%$/+-]*")


def words(text: str) -> int:
    return len(WORD_RE.findall(text or ""))


def clip(text: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0].rstrip(",;:.")
    return cut + "…"


DANGLING = re.compile(r"\s+(and|or|with|the|a|an|to|of|for|in|on|at|by|from|but|so|as|than|then|their|its|your|our)$", re.I)


def fit_line(text: Any, limit: int = 89) -> str:
    """A phone line that fits without an ellipsis: whole, else up to its last clause that fits, else its last whole
    word that ends a phrase. A push is read on a lock screen, where "..." reads as a fault."""
    t = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(t) <= limit:
        return t
    cut = t[:limit + 1]
    marks = [cut.rfind(x) for x in (". ", "; ", ", ", ": ", " · ", " (")]
    m = max(marks)
    if m >= limit // 2:
        return cut[:m].rstrip(" ,;:.(")
    out = cut[:cut.rfind(" ")] if " " in cut else cut[:limit]
    while DANGLING.search(out):
        out = DANGLING.sub("", out)
    return out.rstrip(" ,;:.-(")


def fit_sentences(text: str, limit: int) -> str:
    """At most `limit` characters made of whole sentences: the later sentences go first, never cut mid-word. A first
    sentence longer than the limit keeps its whole clauses, then whole words."""
    text = re.sub(r"\s+", " ", text or "").strip()
    if len(text) <= limit:
        return text
    # A sentence ends after its mark, or after a closing quote that follows it ('next week." Raise it...').
    parts = re.split(r"(?<=[.!?])\s+|(?<=[.!?][\"\u201d\u2019')])\s+", text)
    out = ""
    for p in parts:
        nxt = (out + " " + p).strip()
        if len(nxt) > limit:
            break
        out = nxt
    if out:
        return out
    first = parts[0]
    clauses = re.split(r"(?<=[,;:])\s+", first)
    out = ""
    for c in clauses:
        nxt = (out + " " + c).strip()
        if len(nxt) > limit:
            break
        out = nxt
    if not out or re.search(r":$", out.rstrip()):
        # Nothing but a speaker's label ('Arjun wrote on 20 Oct:'): keep their first words instead, never the label alone.
        out = first[:limit].rsplit(" ", 1)[0]
    out = out.rstrip(",;: ")
    if out.count('"') % 2 or out.count("\u201c") > out.count("\u201d"):
        # Cut inside someone's words: the quote ends on an ellipsis, never left open or closed as if it were whole, and
        # never on a word that leads nowhere ("on...").
        out = out.rstrip(".")
        while DANGLING.search(out):
            out = DANGLING.sub("", out)
        return out.rstrip(",;: ") + "\u2026" + ("\u201d" if out.count("\u201c") > out.count("\u201d") else '"')
    return out + ("" if ends_sentence(out) else ".")


def ends_sentence(text: str) -> bool:
    """True when the text already ends a sentence, a closing quote after the mark included ('next week."')."""
    return bool(re.search(r"[.!?][\"\u201d\u2019')]*$", (text or "").rstrip()))


def join_sentences(first: str, second: str) -> str:
    """Two sentences as one line: a period only where the first does not already end one ("...look like?" Deal: ...)."""
    first = (first or "").rstrip()
    if not first:
        return second
    return f"{first} {second}" if ends_sentence(first) else f"{first.rstrip(',;: ')}. {second}"


# A line left for the user to fill in a draft: "[Add the timeline]", never a markdown link's "[text](url)", nor the
# brackets mail itself carries ("[sic]", "[EXTERNAL]", "[cid:image001.png]").
GAP_RE = re.compile(r"\[(?!\s*(?:sic\b|external\b|cid:|image\b|mailto:|https?:|attachment\b))(?=[^\]\n]*[A-Za-z])[^\[\]\n]{2,200}\](?!\()", re.I)


def draft_gaps(body: Any) -> int:
    """How many bracketed lines a draft leaves for the user to fill before it is sent."""
    return len(GAP_RE.findall(str(body or "")))


def plural(n: int, word: str, many: str | None = None) -> str:
    """ "1 day", "2 days": counts in plain English."""
    return f"{n} {word if n == 1 else (many or word + 's')}"


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def first(items: Iterable[Any], default: Any = None) -> Any:
    for item in items:
        return item
    return default


def money(usd: float | None) -> str:
    """$38.9K / $2.5M style, per the Anthill number rules for dollar clients."""
    if usd is None:
        return "—"
    sign = "−" if usd < 0 else ""
    usd = abs(usd)
    if usd >= 1_000_000_000:
        return f"{sign}${usd / 1_000_000_000:.1f}B"
    if usd >= 1_000_000:
        value = usd / 1_000_000
        return f"{sign}${value:.1f}M".replace(".0M", "M")
    if usd >= 1_000:
        return f"{sign}${usd / 1_000:.1f}K".replace(".0K", "K")
    return f"{sign}${usd:.0f}"


def pct(value: float | None, digits: int = 1) -> str:
    if value is None:
        return "—"
    sign = "−" if value < 0 else ""
    return f"{sign}{abs(value):.{digits}f}%"


SEPARATORS = r"(?:<>|<->|\bx\b|/|\||&|\+|-|\u2013|:)"


def clean_title(title: Any, firm: Any = None) -> str:
    """A calendar title as a person would say it: "Halo Reconcile <> Quillwater" is "Halo Reconcile"."""
    t = re.sub(r"\s+", " ", str(title or "")).strip()
    word = str(firm or "").split(" ")[0]
    if word:
        w = re.escape(word)
        t = re.sub(rf"\s*{SEPARATORS}\s*{w}(?:\s+\w+)?\s*$", "", t, flags=re.I)
        t = re.sub(rf"^{w}(?:\s+\w+)?\s*{SEPARATORS}\s*", "", t, flags=re.I)
    t = re.sub(r"\s*<->?\s*|\s*<>\s*", " and ", t).strip(" -:/|")
    return t or str(title or "")


ACRONYMS = {"d2c": "D2C", "b2b": "B2B", "b2c": "B2C", "b2b2c": "B2B2C", "saas": "SaaS", "ai": "AI", "kyc": "KYC", "aml": "AML",
            "upi": "UPI", "aa": "AA", "nbfc": "NBFC", "bnpl": "BNPL", "lp": "LP", "lps": "LPs", "gp": "GP", "ic": "IC", "cfo": "CFO",
            "cto": "CTO", "ceo": "CEO", "api": "API", "apis": "APIs", "esg": "ESG", "crm": "CRM", "nft": "NFT", "nfts": "NFTs",
            "msme": "MSME", "msmes": "MSMEs", "sme": "SME", "smes": "SMEs", "ml": "ML", "uk": "UK", "uae": "UAE", "eu": "EU", "mena": "MENA", "latam": "LatAm", "vc": "VC"}


def acronyms(text: Any) -> str:
    """Known acronyms in capitals: "d2c" reads "D2C", "saas" reads "SaaS". Words in quotes stay as written."""
    t = str(text or "")
    if '"' in t or "\u201c" in t:
        return t
    return re.sub(r"\b[A-Za-z0-9]+\b", lambda m: ACRONYMS.get(m.group(0).lower(), m.group(0)) if m.group(0).islower() else m.group(0), t)

