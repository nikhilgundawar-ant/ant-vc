"""Portfolio watch: KPI drift from founder updates, board prep windows, founder asks."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from .util import money, parse_dt, pct, sid

import re

KEY_ROLES = ("cto", "cfo", "coo", "cpo", "ceo", "vp eng", "vp engineering", "vp sales", "head of engineering", "head of sales",
             "head of product", "head of risk", "chief", "co-founder", "cofounder", "founder")
# Whole words only: "cto" must not match "director".
KEY_ROLE_RE = re.compile(r"\b(" + "|".join(re.escape(k) for k in KEY_ROLES) + r")\b", re.I)


def drift(company: dict[str, Any], series: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """series: monthly KPI rows, oldest first: month, revenue_usd, plan_revenue_usd, burn_usd, cash_usd, churn_pct, departures."""
    if not series:
        return []
    rows = sorted(series, key=lambda r: (r.get("month") or ""))
    last = rows[-1]
    prev = rows[-2] if len(rows) > 1 else None
    name = company.get("name")
    url = last.get("source_url") or company.get("source_url")
    flags: list[dict[str, Any]] = []

    def flag(kind: str, headline: str, detail: str, priority: str, breach: bool = False, figure: str | None = None) -> None:
        """breach is True only for a figure past its threshold (runway, burn, revenue, churn). A person leaving is work: High."""
        flags.append({"id": sid("flag", company.get("id"), last.get("month"), kind, prefix="f"), "company_id": company.get("id"),
                      "company": name, "kind": kind, "headline": headline, "detail": detail, "text": f"{headline}: {detail}",
                      "priority": priority, "breach": breach, "figure": figure, "month": last.get("month"), "source_url": url})

    burn, cash = last.get("burn_usd"), last.get("cash_usd")
    stated = last.get("runway_months")
    if isinstance(stated, (int, float)) and stated > 0:
        # The founder's own runway (it knows about committed revenue and the plan) wins over cash divided by burn.
        if stated < 9:
            flag("runway", "Runway under 9 months", f"{stated:.1f} months by the founder's count", "urgent", True, f"{stated:.1f} mo")
    elif burn and cash is not None and burn > 0:
        runway = cash / burn
        if runway < 9:
            flag("runway", "Runway under 9 months", f"{runway:.1f} months left at {money(burn)} net burn a month", "urgent", True, f"{runway:.1f} mo")
    if prev and prev.get("burn_usd") and burn:
        change = (burn - prev["burn_usd"]) / prev["burn_usd"] * 100
        if change > 25:
            flag("burn", f"Burn up {pct(change)} in a month", f"{money(prev['burn_usd'])} to {money(burn)} a month", "high", True, pct(change))
    rev, plan = last.get("revenue_usd"), last.get("plan_revenue_usd")
    if rev is not None and plan:
        miss = (rev - plan) / plan * 100
        if miss < -15:
            flag("revenue", f"Revenue {pct(miss)} against plan", f"{money(rev)} against a plan of {money(plan)}", "high", True, pct(miss))
    if prev and last.get("churn_pct") is not None and prev.get("churn_pct") is not None:
        delta = last["churn_pct"] - prev["churn_pct"]
        if delta > 2:
            flag("churn", f"Churn up {delta:.1f}pp", f"{prev['churn_pct']:.1f}% to {last['churn_pct']:.1f}% a month", "medium", True, f"{delta:.1f}pp")
    for dep in (last.get("departures") or []) or []:
        role = str((dep.get("role") or ""))
        if KEY_ROLE_RE.search(role) and not re.search(r"chief of staff", role, re.I):
            flag("key_departure", "Key person leaving", f"{dep.get('name') or 'Someone'}, {role}", "high", False)
    return flags


def portfolio_flags(companies: list[dict[str, Any]], kpis: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    out = []
    for c in companies:
        out.extend(drift(c, kpis.get(c.get("id"), [])))
    order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
    out.sort(key=lambda f: (order.get(f["priority"], 9), f["company"] or ""))
    return out


def board_prep(ctx: dict[str, Any], days: int = 3) -> list[dict[str, Any]]:
    """Board meetings with portfolio companies in the next `days` days."""
    now = ctx["now"]
    out = []
    portfolio = {cid for cid, c in ctx["companies"].items() if c.get("status") == "portfolio"}
    for m in ctx["meetings"]:
        start = m.get("start")
        if not start or not (now <= start <= now + timedelta(days=days)):
            continue
        if "board" not in (m.get("title") or "").lower():
            continue
        comp_ids = {ctx["lookup"][pid].get("company_id") for pid in (m.get("external_ids") or []) if ctx["lookup"].get(pid)}
        hit = next((cid for cid in comp_ids if cid in portfolio), None)
        if hit:
            out.append({"meeting_id": m["id"], "title": m["title"], "start": start.isoformat(), "company_id": hit,
                        "company": ctx["companies"][hit].get("name"), "source_url": m.get("url")})
    return out


def kpi_table(companies: list[dict[str, Any]], kpis: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    table = {}
    for c in companies:
        rows = sorted(kpis.get(c.get("id"), []), key=lambda r: (r.get("month") or ""))
        if not rows:
            table[c["id"]] = {"name": c.get("name"), "kpis": None}
            continue
        last, prev = rows[-1], rows[-2] if len(rows) > 1 else {}
        runway = (last["cash_usd"] / last["burn_usd"]) if last.get("cash_usd") and last.get("burn_usd") else None
        growth = ((last["revenue_usd"] - prev["revenue_usd"]) / prev["revenue_usd"] * 100) if prev.get("revenue_usd") and last.get("revenue_usd") else None
        table[c["id"]] = {"name": c.get("name"), "month": last.get("month"), "revenue_usd": last.get("revenue_usd"),
                          "growth_pct": round(growth, 1) if growth is not None else None,
                          "burn_usd": last.get("burn_usd"), "runway_months": round(runway, 1) if runway else None,
                          "source_url": last.get("source_url")}
    return table
