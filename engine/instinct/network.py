"""Network: warm intro paths into a company, and relationships going cold."""

from __future__ import annotations

import heapq
import math
import re
from collections import defaultdict
from typing import Any

from .util import domain_of, fmt_short_date, norm_email


def _edges(ctx: dict[str, Any]) -> dict[str, dict[str, float]]:
    """Weighted undirected graph. Firm member to contact: strength/100. Contact to contact: co-occurrence.
    Colleague to colleague: 0.9."""
    g: dict[str, dict[str, float]] = defaultdict(dict)
    members = ctx["member_ids"]
    for mid, row in ctx["strengths"].items():
        for pid, s in row.items():
            w = max(0.05, s / 100)
            g[mid][pid] = max(g[mid].get(pid, 0), w)
            g[pid][mid] = max(g[pid].get(mid, 0), w)
    for a in members:
        for b in members:
            if a != b:
                g[a][b] = 0.9
    co: dict[tuple[str, str], int] = defaultdict(int)
    for it in ctx["interactions"]:
        ext = [p for p in it["person_ids"] if p not in members]
        for i in range(len(ext)):
            for j in range(i + 1, len(ext)):
                key = tuple(sorted((ext[i], ext[j])))
                co[key] += 1
    for (a, b), n in co.items():
        w = min(0.8, 0.3 + 0.15 * n)
        g[a][b] = max(g[a].get(b, 0), w)
        g[b][a] = max(g[b].get(a, 0), w)
    return g


def _norm(text: str) -> str:
    import re
    return re.sub(r"[^a-z0-9]", "", (text or "").lower())


def people_at(ctx: dict[str, Any], company: str) -> list[dict[str, Any]]:
    key = (company or "").strip().lower()
    nkey = _norm(key)
    cid = None
    for c_id, c in ctx["companies"].items():
        if key and (key == (c.get("name") or "").lower() or key == (c.get("domain") or "").lower()):
            cid = c_id
            break
    if cid is None and nkey:
        for c_id, c in ctx["companies"].items():
            stem = _norm((c.get("domain") or "").split(".")[0])
            if nkey == _norm(c.get("name") or "") or (len(stem) >= 5 and (stem == nkey or stem in nkey)):
                cid = c_id
                break
    if cid is None and "." in key:
        cid = ctx["domain_to_company"].get(key)
    if cid is None:
        return []
    return [p for p in ctx["people"] if p.get("company_id") == cid and not p.get("is_member")]


def intro_paths(ctx: dict[str, Any], company: str, max_paths: int = 3, max_hops: int = 3) -> dict[str, Any]:
    user = ctx.get("user_person")
    targets = people_at(ctx, company)
    if not user:
        return {"company": company, "paths": [], "note": "ant. does not know who you are yet. Run setup first."}
    if not targets:
        return {"company": company, "paths": [], "note": f"No one at {company} appears in your email, calendar or CRM."}
    g = _edges(ctx)
    target_ids = {t["id"] for t in targets}
    # Dijkstra on -log(weight), tracking hops.
    start = user["id"]
    best: dict[str, float] = {start: 0.0}
    heap = [(0.0, start, [start])]
    found: list[tuple[float, list[str]]] = []
    while heap and len(found) < max_paths * 4:
        cost, node, path = heapq.heappop(heap)
        if node in target_ids and node != start:
            found.append((cost, path))
            continue
        if len(path) - 1 >= max_hops:
            continue
        for nxt, w in g.get(node, {}).items():
            if nxt in path:
                continue
            c = cost - math.log(max(w, 1e-6))
            if c < best.get(nxt, float("inf")) + 1e-9 or nxt in target_ids:
                best[nxt] = min(best.get(nxt, float("inf")), c)
                heapq.heappush(heap, (c, nxt, path + [nxt]))
    seen_targets = set()
    paths = []
    for cost, path in sorted(found):
        if path[-1] in seen_targets:
            continue
        seen_targets.add(path[-1])
        hops = []
        for a, b in zip(path, path[1:]):
            pb = ctx["lookup"][b]
            last = ctx["last_touch"].get(a, {}).get(b) or ctx["last_touch"].get(b, {}).get(a)
            hops.append({"from": ctx["lookup"][a]["name"], "to": pb["name"], "to_id": b, "strength": int(round(g[a][b] * 100)),
                         "last_touch": fmt_short_date(last) if last else None})
        paths.append({"score": int(round(math.exp(-cost) * 100)), "hops": hops, "target": ctx["lookup"][path[-1]]["name"],
                      "first_hop": hops[0]["to"] if hops else None, "hop_count": len(hops),
                      "how": _describe(hops)})
        if len(paths) >= max_paths:
            break
    return {"company": company, "paths": paths, "note": None if paths else f"No warm path to {company} within {max_hops} hops."}


def _describe(hops: list[dict[str, Any]]) -> str:
    if not hops:
        return ""
    if len(hops) == 1:
        h = hops[0]
        return f"You know {h['to']} directly (strength {h['strength']}" + (f", last touch {h['last_touch']})" if h["last_touch"] else ")")
    first = hops[0]
    rest = " then ".join(f"{h['to']}" for h in hops[1:])
    return f"Ask {first['to']} (strength {first['strength']}), who can reach {rest}"


ROLE_LOCAL = re.compile(r"^(no-?reply|do-?not-?reply|newsletter|news|updates?|notifications?|digest|mailer|bounce|list|lists|"
                        r"hello|hi|info|team|community|events?|marketing|support|admin|billing|invoices?|receipts?)([+._-].*)?$", re.I)


def is_relationship(ctx: dict[str, Any], pid: str) -> bool:
    """A real relationship is two-way: you met them, or you wrote to a thread they are on. Lists, newsletters and
    role addresses (no-reply, updates, team) only ever write to you, so they never rank."""
    if "_two_way" not in ctx:
        user_email = ctx.get("user_email")
        ids: set[str] = set()
        for it in ctx["interactions"]:
            if it["type"] == "meeting" or (user_email and user_email in (it.get("senders") or set())):
                ids.update(it["person_ids"])
        ctx["_two_way"] = ids
    if pid not in ctx["_two_way"]:
        return False
    p = ctx["lookup"].get(pid) or {}
    for e in (p.get("emails") or [p.get("email")]):
        local = (norm_email(e) or "@").split("@")[0]
        if local and ROLE_LOCAL.match(local):
            return False
    return True


def decay(ctx: dict[str, Any], top: int = 50, days: int = 60) -> list[dict[str, Any]]:
    """People among your 50 strongest relationships ever who have gone quiet for 60 days. Strength is the same
    number People shows (recency-weighted); strength_was is what it was at its peak."""
    user = ctx.get("user_person")
    if not user:
        return []
    life = ctx["lifetime"].get(user["id"], {})
    now_strength = ctx["strengths"].get(user["id"], {})
    ranked = [kv for kv in sorted(life.items(), key=lambda kv: -kv[1]) if is_relationship(ctx, kv[0])][:top]
    out = []
    for pid, s in ranked:
        last = ctx["last_touch"].get(user["id"], {}).get(pid)
        if not last:
            continue
        gap = (ctx["now"] - last).days
        if gap > days:
            p = ctx["lookup"][pid]
            comp = ctx["companies"].get(p.get("company_id") or "", {})
            out.append({"person_id": pid, "name": p["name"], "company": comp.get("name"), "company_status": comp.get("status"),
                        "strength": now_strength.get(pid, 0),
                        "strength_was": s, "days_since": gap, "last_touch": last.date().isoformat(), "source_url": p.get("source_url")})
    out.sort(key=lambda r: -r["strength_was"])
    return out


def top_people(ctx: dict[str, Any], limit: int = 200) -> list[dict[str, Any]]:
    user = ctx.get("user_person")
    if not user:
        return []
    row = ctx["strengths"].get(user["id"], {})
    out = []
    for pid, s in sorted(row.items(), key=lambda kv: -kv[1]):
        if len(out) >= limit:
            break
        if not is_relationship(ctx, pid):
            continue
        p = ctx["lookup"][pid]
        comp = ctx["companies"].get(p.get("company_id") or "", {})
        last = ctx["last_touch"].get(user["id"], {}).get(pid)
        out.append({"id": pid, "name": p["name"], "company": comp.get("name"), "title": p.get("title"), "strength": s,
                    "last_touch": last.date().isoformat() if last else None,
                    "days_since": (ctx["now"] - last).days if last else None, "source_url": p.get("source_url")})
    return out


# What a founder asks for, as the kind of company or role that answers it: "intro to two banks as customers" wants
# people at banks; "two CFO candidates" wants people who are CFOs.
ASK_ORGS = (r"\bbanks?\b", r"\bnbfcs?\b", r"\binsur(?:er|ers|ance)\b", r"\blenders?\b", r"\bbrokers?\b", r"\bfamily offices?\b")
ASK_ROLES = (r"\bcfos?\b", r"\bctos?\b", r"\bcros?\b", r"\b(?:head|vp) of (?:sales|engineering|product)\b")


def ask_paths(ctx: dict[str, Any], ask: str, company_id: str | None = None, limit: int = 3) -> list[dict[str, Any]]:
    """Warm paths for a founder's ask: the people in the firm's network who answer it, each with the colleague who
    knows them best. One per company, strongest first, never someone at the asking company. Empty when the ask is
    not one a person can answer (hiring engineers, a pricing question)."""
    text = str(ask or "").lower()
    orgs = [re.compile(r, re.I) for r in ASK_ORGS if re.search(r, text, re.I)]
    roles = [re.compile(r, re.I) for r in ASK_ROLES if re.search(r, text, re.I)]
    if not orgs and not roles:
        return []
    members = list(ctx.get("member_ids") or [])
    me = (ctx.get("user_person") or {}).get("id")
    rows = []
    for p in ctx.get("people") or []:
        if p.get("is_member") or p["id"] in members or (company_id and p.get("company_id") == company_id):
            continue
        comp = (ctx.get("companies") or {}).get(p.get("company_id") or "") or {}
        # A bank is a company called a bank, not a startup that sells to banks; a CFO candidate is not a CFO we back.
        org_hit = any(r.search(str(comp.get("name") or "")) for r in orgs)
        role_hit = any(r.search(str(p.get("title") or "")) for r in roles) and comp.get("status") not in ("portfolio", "pipeline")
        if not (org_hit or role_hit):
            continue
        strength, mid = max(((ctx["strengths"].get(m, {}).get(p["id"], 0), m) for m in members), default=(0, None))
        if strength < 30 or not mid:
            continue
        colleague = "You" if mid == me else str((ctx["lookup"].get(mid) or {}).get("name") or "").split(" ")[0] or None
        rows.append({"person": p["name"], "person_id": p["id"], "email": (p.get("emails") or [None])[0], "title": p.get("title"),
                     "company": comp.get("name"), "colleague": colleague, "colleague_id": mid, "strength": int(strength)})
    rows.sort(key=lambda r: -r["strength"])
    out, seen = [], set()
    for r in rows:
        key = r["company"] or r["person"]
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
        if len(out) >= limit:
            break
    return out
