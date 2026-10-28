---
name: portfolio-watch
description: Reads portfolio founders' updates into KPIs, flags drift early (runway under 9 months, burn jumps, revenue misses, key hires leaving, churn spikes), captures founder asks and preps board meetings three days ahead. Use when the user asks "how is the portfolio", "any portfolio flags", "prep me for the board meeting", "what do founders need", or when the Monday digest or pulse finds founder updates.
metadata:
  version: "0.9.0"
---

# Portfolio watch

Catch trouble before the board meeting, and make the firm's help visible.

Plugin root: `${CLAUDE_PLUGIN_ROOT}`. If that is not a real path, use the folder two levels above this skill's base directory. Follow `<plugin root>/shared/safety.md` throughout.

## 1. Find the updates

Founder updates from portfolio companies (CRM status portfolio, or their email domains): monthly investor updates, board decks, KPI sheets in Drive. Use the window of the run.

## 2. Read the KPIs

For each update, extract one row per month it reports. Use only numbers the update states. Convert to US dollars per month.

```json
{"<CRM company id>": [{"month": "2026-09", "revenue_usd": 198000, "plan_revenue_usd": 195000, "burn_usd": 200000, "cash_usd": 1600000,
  "runway_months": null, "churn_pct": 1.3, "departures": [{"name": "", "role": ""}], "source_url": "<link to the update>"}]}
```

`burn_usd` is net burn: cash going out minus cash coming in, per month. Most updates say "burn" and mean net. If an update gives only total spend and revenue, net burn is spend minus revenue; say "net burn computed" in your summary. If the founder states runway in months, put it in `runway_months`: the engine uses the founder's number over cash divided by burn. Leave a field null when the update does not state it. `departures` is `[]` when nobody is leaving; list someone only when the update says they are leaving or have left, with their role. Read churn as monthly logo churn unless the update says otherwise. Convert rupees at Rs 1 crore = $120K and Rs 1 lakh = $1.2K, and note "approx" in your summary when you converted. Save as `kpis.json`.

On a first run (Home has no KPI history for a company), also read the update before the latest one, so the engine can measure month-on-month change in burn and churn.

## 3. Build and read the flags

Run the engine `build` with `--kpis kpis.json --asks asks.json`. It keeps up to six months of history in Home and flags: runway under 9 months (Urgent), burn up more than 25% in a month (High), revenue more than 15% under plan (High), churn up more than 2 points (Medium), each shown as a Breach because a figure crossed its line, and a key person leaving (High).

For each flag, write one line of context from the update itself ("Burn up 43% to $215K: two senior hires in September").

## 4. Founder asks

From updates, mail and Slack: requests for help like "could you intro us to", "any leads on a CFO would help", "looking for advice on". A status line is not an ask: "Team: hiring two engineers this quarter" reports a plan; it becomes an ask only when the founder asks us for something ("intros to senior engineers would help"). Save each in `asks.json` as `{"company", "company_id", "ask": "<what they need, in a few words>", "who", "kind": "intro|hiring|customer|advice|other", "date", "source_url"}` and pass it to the build with `--asks asks.json`. Asks live in their own document, so later builds keep them until the user marks one done. Platform users see these first.

## 5. Board prep (three days ahead)

For a board meeting with a portfolio company in the next three days: the latest KPIs and flags, open asks, open promises in both directions, last board's decisions (from notes), and three questions for the board. Save as the meeting's prep card.

## 6. Deliver

Write the snapshots. In chat, show flags first, then asks, then the KPI table. The flags are in `run/report.json` under `flags`. In a scheduled run, end with the engine's `report.push_line`, or exactly `Nothing new`.
