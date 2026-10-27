"""Name normalisation and first-name compatibility (nicknames, short forms, initials)."""

from __future__ import annotations

import re
import unicodedata

HONORIFICS = {"mr", "mrs", "ms", "miss", "dr", "prof", "sir", "shri", "smt", "jr", "sr", "ii", "iii"}

# Short forms that are not simple prefixes of the full name.
NICKNAMES = {
    "bob": {"robert"}, "rob": {"robert"}, "bobby": {"robert"}, "bill": {"william"}, "will": {"william"},
    "liz": {"elizabeth"}, "beth": {"elizabeth"}, "betty": {"elizabeth"}, "kate": {"katherine", "kathryn", "katharine"},
    "kat": {"katherine", "kathryn"}, "katie": {"katherine", "kathryn"}, "mike": {"michael"}, "mick": {"michael"},
    "jim": {"james"}, "jimmy": {"james"}, "jamie": {"james"}, "joe": {"joseph"}, "joey": {"joseph"},
    "tony": {"anthony", "antony"}, "drew": {"andrew"}, "andy": {"andrew"}, "dick": {"richard"}, "rick": {"richard"},
    "rich": {"richard"}, "ted": {"edward", "theodore"}, "ned": {"edward"}, "eddie": {"edward"}, "peggy": {"margaret"},
    "maggie": {"margaret"}, "meg": {"margaret"}, "jenny": {"jennifer"}, "jen": {"jennifer"}, "chuck": {"charles"},
    "charlie": {"charles"}, "hank": {"henry"}, "harry": {"henry", "harold"}, "jack": {"john"}, "johnny": {"john"},
    "sandy": {"alexandra", "sandra"}, "sasha": {"alexander", "alexandra"}, "venky": {"venkatesh", "venkat", "venkataraman"},
    "balu": {"balaji", "balasubramanian"}, "chandu": {"chandrashekhar", "chandrasekhar"}, "gopi": {"gopinath", "gopal"},
    "suri": {"suresh"}, "kittu": {"krishna"}, "pappu": {"prakash"}, "bunty": {"bhupinder"}, "sonu": {"sonal"},
    "babu": {"prabhu"}, "nandu": {"nandakumar", "nandan"}, "jaggi": {"jagdish"}, "titu": {"amitabh"},
}


def strip_accents(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()


def normalize_name(name: str | None) -> str:
    """'Menon, Siddharth (Kite Pay)' -> 'siddharth menon'."""
    if not name:
        return ""
    text = strip_accents(str(name))
    text = re.sub(r"\(.*?\)|\[.*?\]|<.*?>", " ", text)
    text = text.replace("’", "'")
    if "," in text:
        last, _, rest = text.partition(",")
        if rest.strip() and len(last.split()) <= 2:
            text = f"{rest} {last}"
    text = re.sub(r"[^a-zA-Z' .-]", " ", text)
    parts = [p.strip(" .'-").lower() for p in re.split(r"[\s]+", text)]
    parts = [p for p in parts if p and p not in HONORIFICS]
    return " ".join(parts)


def split_name(name: str) -> tuple[str, str]:
    norm = normalize_name(name)
    if not norm:
        return "", ""
    parts = norm.split()
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[-1]


def is_initial(token: str) -> bool:
    return len(token.rstrip(".")) == 1


def first_relation(a: str, b: str) -> str:
    """Relation between two first names: same, nick, initial or diff."""
    a, b = a.rstrip("."), b.rstrip(".")
    if not a or not b:
        return "diff"
    if a == b:
        return "same"
    if is_initial(a) or is_initial(b):
        return "initial" if a[0] == b[0] else "diff"
    if b in NICKNAMES.get(a, set()) or a in NICKNAMES.get(b, set()):
        return "nick"
    short, long_ = (a, b) if len(a) < len(b) else (b, a)
    if len(short) >= 3 and long_.startswith(short):
        return "nick"
    return "diff"


def compatible_first(a: str, b: str) -> bool:
    return first_relation(a, b) in ("same", "nick")


def name_from_email(email: str) -> str:
    """Best-effort display name from an address: 'siddharth.menon@x' -> 'Siddharth Menon'."""
    local = (email or "").split("@", 1)[0]
    local = local.split("+", 1)[0]
    parts = [p for p in re.split(r"[._-]+", local) if p and not p.isdigit()]
    if not parts:
        return ""
    return " ".join(p.capitalize() for p in parts[:3])


def display_name(variants: list[str]) -> str:
    """Pick the fullest variant: prefer two or more tokens and the longest first name."""
    cleaned = [v.strip() for v in variants if v and v.strip()]
    if not cleaned:
        return ""

    def score(v: str) -> tuple[int, int, int]:
        first, last = split_name(v)
        return (1 if last else 0, 0 if is_initial(first) else 1, len(first))

    best = max(cleaned, key=score)
    first, last = split_name(best)
    if "," in best:
        return " ".join(w.capitalize() for w in normalize_name(best).split())
    return best if best[:1].isupper() else " ".join(w.capitalize() for w in best.split())
