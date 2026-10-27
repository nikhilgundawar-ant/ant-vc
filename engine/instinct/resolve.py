"""Entity resolution: one person per human, across email, calendar, notes and CRM.

Rules and confidences are documented in ontology/resolution-rules.md. Below 0.80
nothing merges; those pairs become needs_review rows.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from .names import display_name, first_relation, name_from_email, normalize_name, split_name
from .util import domain_of, is_freemail, norm_email, sid

MERGE_AT = 0.80


class _UF:
    def __init__(self) -> None:
        self.parent: dict[int, int] = {}

    def find(self, x: int) -> int:
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> int:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra
        return ra


def observations(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten every place a person appears into observation rows."""
    obs: list[dict[str, Any]] = []

    def add(name: str | None, email: str | None, source: str, ref: str | None, **extra: Any) -> None:
        email = (email or "").strip()
        name = (name or "").strip()
        if not email and not name:
            return
        if not name and email:
            name = name_from_email(email)
        obs.append({"name": name, "email": email, "source": source, "ref": ref, **extra})

    for th in (bundle.get("threads") or []):
        for p in (th.get("participants") or []):
            add(p.get("name"), p.get("email"), "email", f"thread:{th.get('id')}", url=th.get("url"))
    for ev in (bundle.get("events") or []):
        for a in (ev.get("attendees") or []):
            add(a.get("name"), a.get("email"), "calendar", f"event:{ev.get('id')}", url=ev.get("url"))
    for tr in (bundle.get("transcripts") or []):
        ref = f"event:{tr['event_id']}" if tr.get("event_id") else f"transcript:{tr.get('id')}"
        for a in (tr.get("attendees") or []):
            add(a.get("name"), a.get("email"), "notes", ref, url=tr.get("url"))
    # The firm's own people, whether or not this read saw them: a colleague's CRM relationships (the warm paths) attach
    # to them even on a morning when they wrote nothing to the user.
    firm = bundle.get("firm") or {}
    for m in (firm.get("members") or []) + ([bundle["user"]] if isinstance(bundle.get("user"), dict) else []):
        if isinstance(m, dict) and m.get("email"):
            add(m.get("name"), m.get("email"), "firm", "firm:members", title=m.get("title"))
    crm = (bundle.get("crm") or {}) or {}
    companies = {c.get("id"): c for c in (crm.get("companies") or [])}
    for p in (crm.get("people") or []):
        comp = companies.get(p.get("company_id")) or {}
        add(p.get("name"), p.get("email"), "crm", f"crm:{p.get('id')}", crm_id=p.get("id"),
            company_domain=comp.get("domain"), title=p.get("title"), url=p.get("url"))
    return obs


def _cluster_profile(rows: list[dict[str, Any]]) -> dict[str, Any]:
    names = [r["name"] for r in rows if r.get("name")]
    emails = sorted({norm_email(r["email"]) for r in rows if r.get("email")})
    corp = sorted({domain_of(e) for e in emails if e and not is_freemail(e)})
    free = sorted({e for e in emails if e and is_freemail(e)})
    refs = {r["ref"] for r in rows if r.get("ref")}
    crm_ids = sorted({r["crm_id"] for r in rows if r.get("crm_id")})
    for r in rows:
        if r.get("company_domain") and not is_freemail(r["company_domain"]):
            corp = sorted(set(corp) | {r["company_domain"].lower()})
    best = display_name(names)
    first, last = split_name(best)
    firsts = {split_name(n)[0] for n in names if n}
    return {
        "names": names, "display": best, "first": first, "last": last, "firsts": firsts,
        "emails": emails, "corp": corp, "free": free, "refs": refs, "crm_ids": crm_ids,
    }


def _pair_score(a: dict[str, Any], b: dict[str, Any]) -> tuple[float, str]:
    if not a["last"] or not b["last"] or a["last"] != b["last"]:
        return 0.0, "different last name"
    rels = {first_relation(x, y) for x in a["firsts"] | {a["first"]} for y in b["firsts"] | {b["first"]}}
    if "same" in rels:
        rel = "same"
    elif "nick" in rels:
        rel = "nick"
    elif "initial" in rels:
        rel = "initial"
    else:
        return 0.0, "different first name"
    shared_corp = set(a["corp"]) & set(b["corp"])
    shared_ref = bool(a["refs"] & b["refs"])
    corp_conflict = bool(a["corp"]) and bool(b["corp"]) and not shared_corp
    one_personal_only = (not a["corp"] and a["free"]) or (not b["corp"] and b["free"])
    if a["crm_ids"] and b["crm_ids"] and set(a["crm_ids"]).isdisjoint(b["crm_ids"]):
        return 0.30, "two different CRM records"
    if corp_conflict:
        return 0.40, "same name at two different companies"
    if rel == "initial":
        return (0.75, "initial and last name, same work domain") if shared_corp else (0.0, "initial only")
    if shared_corp:
        return (0.95, "same name, same work domain") if rel == "same" else (0.85, "short form of first name, same work domain")
    if one_personal_only and shared_ref:
        return 0.82, "same name, personal and work address in the same meeting or thread"
    if one_personal_only and rel == "same":
        return 0.60, "same name, personal and work address, never seen together"
    return 0.0, "not enough evidence"


def _first_names_conflict(a: dict[str, Any], b: dict[str, Any]) -> bool:
    """Guard: never join clusters that each hold a different address at the same company with incompatible first names."""
    shared = set(a["corp"]) & set(b["corp"])
    if not shared:
        return False
    return first_relation(a["first"], b["first"]) == "diff"


def resolve_people(bundle: dict[str, Any], overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    """overrides: the user's answers from Home, {"merge": [[email_a, email_b]], "apart": [[email_a, email_b]]}.
    A merge joins the two clusters; apart keeps them separate and stops asking."""
    firm_domain = ((bundle.get("firm") or {}).get("domain") or "").lower()
    overrides = overrides or {}
    obs = observations(bundle)
    uf = _UF()
    by_email: dict[str, int] = {}
    by_crm: dict[str, int] = {}
    merges: list[dict[str, Any]] = []

    # Rule 1 and 2: exact email (normalised) and CRM id.
    for i, row in enumerate(obs):
        uf.find(i)
        e = norm_email(row.get("email"))
        if e:
            if e in by_email:
                uf.union(by_email[e], i)
            else:
                by_email[e] = i
        cid = row.get("crm_id")
        if cid:
            if cid in by_crm:
                uf.union(by_crm[cid], i)
            else:
                by_crm[cid] = i
    for a_email, b_email in (overrides.get("merge") or []):
        ia, ib = by_email.get(norm_email(a_email)), by_email.get(norm_email(b_email))
        da, db = domain_of(a_email), domain_of(b_email)
        if firm_domain and (da == firm_domain) != (db == firm_domain) and not is_freemail(da if db == firm_domain else db):
            continue  # never fold someone at the firm into a person at another company
        if ia is not None and ib is not None:
            uf.union(ia, ib)
            merges.append({"into": obs[ia].get("name"), "from": obs[ib].get("name"), "emails": sorted({norm_email(a_email), norm_email(b_email)}),
                           "rule": "you said same person", "confidence": 1.0})
    apart = {frozenset((norm_email(a), norm_email(b))) for a, b in (overrides.get("apart") or [])}

    def kept_apart(pa: dict[str, Any], pb: dict[str, Any]) -> bool:
        return any(frozenset((x, y)) in apart for x in pa["emails"] for y in pb["emails"])

    # Name-only observations (no email, no CRM id) attach to the same-name cluster seen in the same ref,
    # or to the single cluster anywhere with that exact full name.
    groups: dict[int, list[int]] = defaultdict(list)
    for i in range(len(obs)):
        groups[uf.find(i)].append(i)
    name_only = [i for i, r in enumerate(obs) if not r.get("email") and not r.get("crm_id")]
    if name_only:
        with_email = {root: _cluster_profile([obs[i] for i in idx]) for root, idx in groups.items()
                      if any(obs[i].get("email") or obs[i].get("crm_id") for i in idx)}
        by_full: dict[str, set[int]] = defaultdict(set)
        for root, prof in with_email.items():
            for n in prof["names"]:
                by_full[normalize_name(n)].add(root)
        for i in name_only:
            row = obs[i]
            f, l = split_name(row["name"])
            same_ref = [root for root, prof in with_email.items()
                        if row.get("ref") in prof["refs"] and prof["last"] == l and first_relation(prof["first"], f) in ("same", "nick")]
            if len(same_ref) == 1:
                uf.union(same_ref[0], i)
                continue
            exact = by_full.get(normalize_name(row["name"]), set())
            if len(exact) == 1:
                uf.union(next(iter(exact)), i)
        groups = defaultdict(list)
        for i in range(len(obs)):
            groups[uf.find(i)].append(i)

    profiles = {root: _cluster_profile([obs[i] for i in idx]) for root, idx in groups.items()}

    # Colleagues at the firm match by email only.
    def is_colleague(p: dict[str, Any]) -> bool:
        return bool(firm_domain) and firm_domain in p["corp"]

    by_last: dict[str, list[int]] = defaultdict(list)
    for root, prof in profiles.items():
        if prof["last"] and not is_colleague(prof):
            by_last[prof["last"]].append(root)

    candidates: list[tuple[float, str, int, int]] = []
    for last, roots in by_last.items():
        for x in range(len(roots)):
            for y in range(x + 1, len(roots)):
                score, rule = _pair_score(profiles[roots[x]], profiles[roots[y]])
                if score > 0:
                    candidates.append((score, rule, roots[x], roots[y]))
    candidates.sort(key=lambda c: -c[0])

    needs_review: list[dict[str, Any]] = []
    for _first_score, _rule, ra, rb in candidates:
        a_root, b_root = uf.find(ra), uf.find(rb)
        if a_root == b_root:
            continue
        pa, pb = profiles.get(a_root) or _cluster_profile([]), profiles.get(b_root) or _cluster_profile([])
        score, rule = _pair_score(pa, pb)  # re-score: earlier merges may have changed either side
        if apart and kept_apart(pa, pb):
            continue
        if score >= MERGE_AT:
            if _first_names_conflict(pa, pb):
                needs_review.append(_review_row(pa, pb, 0.5, "same company, different first names"))
                continue
            keep = uf.union(a_root, b_root)
            merged_rows = [obs[i] for i in range(len(obs)) if uf.find(i) == keep]
            profiles[keep] = _cluster_profile(merged_rows)
            merges.append({"into": pa["display"], "from": pb["display"], "emails": sorted(set(pa["emails"]) | set(pb["emails"])),
                           "rule": rule, "confidence": score})
        elif score >= 0.5:
            needs_review.append(_review_row(pa, pb, score, rule))

    final: dict[int, list[int]] = defaultdict(list)
    for i in range(len(obs)):
        final[uf.find(i)].append(i)

    people = []
    email_to_id: dict[str, str] = {}
    for root, idx in final.items():
        rows = [obs[i] for i in idx]
        prof = _cluster_profile(rows)
        crm_id = prof["crm_ids"][0] if prof["crm_ids"] else None
        key = crm_id or (prof["emails"][0] if prof["emails"] else prof["display"])
        pid = sid("person", key, prefix="p")
        company_domain = prof["corp"][0] if prof["corp"] else None
        title = next((r.get("title") for r in rows if r.get("title")), None)
        sources = sorted({r["source"] for r in rows})
        url = next((r.get("url") for r in rows if r.get("source") == "crm" and r.get("url")), None) or next(
            (r.get("url") for r in rows if r.get("url")), None)
        person = {
            "id": pid, "name": prof["display"], "emails": prof["emails"], "company_domain": company_domain,
            "title": title, "crm_id": crm_id, "sources": sources, "refs": sorted(prof["refs"]),
            "colleague": bool(firm_domain) and firm_domain in prof["corp"], "source_url": url,
        }
        people.append(person)
        for e in prof["emails"]:
            email_to_id[e] = pid
    # needs_review rows refer to people by display name; attach ids where we can.
    for row in needs_review:
        row["a_id"] = next((email_to_id[e] for e in row["a_emails"] if e in email_to_id), None)
        row["b_id"] = next((email_to_id[e] for e in row["b_emails"] if e in email_to_id), None)
    needs_review = [r for r in needs_review if r["a_id"] != r["b_id"]]
    people.sort(key=lambda p: (p["colleague"], p["name"].lower()))
    return {"people": people, "merges": merges, "needs_review": _dedupe_reviews(needs_review), "email_to_id": email_to_id,
            "observations": len(obs)}


def _review_row(a: dict[str, Any], b: dict[str, Any], score: float, rule: str) -> dict[str, Any]:
    return {"a": a["display"], "b": b["display"], "a_emails": a["emails"], "b_emails": b["emails"],
            "confidence": round(score, 2), "rule": rule}


def _dedupe_reviews(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen, out = set(), []
    for r in rows:
        key = tuple(sorted([str(r.get("a_id")), str(r.get("b_id"))]))
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def person_lookup(people: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """email (normalised) -> person, plus id -> person."""
    out: dict[str, dict[str, Any]] = {}
    for p in people:
        out[p["id"]] = p
        for e in (p.get("emails") or []):
            out[norm_email(e)] = p
    return out


def find_person(lookup: dict[str, dict[str, Any]], email: str | None = None, name: str | None = None,
                people: list[dict[str, Any]] | None = None) -> dict[str, Any] | None:
    if email:
        hit = lookup.get(norm_email(email))
        if hit:
            return hit
    if name and people:
        target = normalize_name(name)
        exact = [p for p in people if normalize_name(p["name"]) == target]
        if len(exact) == 1:
            return exact[0]
        tf, tl = split_name(name)
        close = [p for p in people if split_name(p["name"])[1] == tl and first_relation(split_name(p["name"])[0], tf) in ("same", "nick")]
        if len(close) == 1:
            return close[0]
    return None


def counts_by_source(people: list[dict[str, Any]]) -> dict[str, int]:
    c: Counter[str] = Counter()
    for p in people:
        for s in (p.get("sources") or []):
            c[s] += 1
    return dict(c)
