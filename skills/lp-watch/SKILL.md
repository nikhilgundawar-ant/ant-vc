---
name: lp-watch
description: Keeps a venture firm's LP relationships warm and quarterly reporting painless. Flags LPs untouched before their re-up window, tracks LP questions, and drafts the quarterly LP letter from portfolio KPIs and fund data. Use when the user asks "which LPs need a touch", "LP update", "draft the quarterly letter", "Fund III re-up", or when the Monday digest runs for partner, finance or solo GP profiles.
metadata:
  version: "0.7.8"
---

# LP watch

LP relationships decay quietly. This skill makes sure no LP in a re-up window goes 45 days without a touch, and the quarterly letter drafts itself.

Plugin root: `${CLAUDE_PLUGIN_ROOT}`. If that is not a real path, use the folder two levels above this skill's base directory. Follow `<plugin root>/shared/safety.md` throughout.

## 1. Gather

LPs from Carta, the CRM or the LP sheet in Drive: name, fund, commitment, re-up window, contacts and the last recorded touch. Mail and meetings with LP contacts in the last 120 days (metadata). Open LP questions from mail and meeting notes. Write `bundle.json` with `lps` filled. If the LP source cannot be read, set `unavailable.lps` and leave `lps` out: Home keeps the LPs it has and says the source is down, never "every LP is in touch".

## 2. Alerts

Run the engine `build`. It flags an LP as due a touch when its re-up window opens within 90 days (or is open) and no one at the firm has touched it in 45 days, Overdue once that window is a month away or open, and High when it has gone 90 days without a touch. Run by hand, draft a short, specific note for each alert: a portfolio highlight they would care about, or the answer to their last question, and save it to `snap/drafts`. A scheduled run drafts only what `owed.json` lists (a capital call still unpaid after two weeks, for the LP's owner); other notes wait for the user's tap on "Draft a note" in Home.

## 3. LP questions

List each open question with who asked, when, and the promised date. Overdue answers go to the top of the finance brief.

## 4. Quarterly letter (when it is promised, or when asked)

A scheduled morning run drafts it when the promise is near: `owed.json` lists it (`kind: "letter"`), and `skills/morning-brief/SKILL.md` step 6.3 says how; it goes as a draft to the person it was promised to. Asked in chat, write the same letter and, if the user wants, also as a document they can edit.

Use `<plugin root>/templates/lp-letter.md`. Sections: Fund summary, Portfolio highlights, New investments, Follow-ons and markdowns, Exits, Pipeline and market, Asks. Take every number from the entry's `inputs` (the LP list, the KPI history, the CRM's new investments and pipeline) or from Carta, the KPI history in `snap/portfolio` and the CRM, each with its source beside it. Leave out every quiet deal (`snap/pipeline` deals with `quiet: true`): LPs read this letter. Give called capital, never paid-in beside it: a gap between the two tells every LP that someone has not paid. A watch-list company leads with why it is there (the flag and its figure). Leave the partner's commentary, and any part a colleague said they will write, as a bracketed prompt. Then run `python3 -I -S instinct-engine/instinct.py letter-check --letter letter.md`: it lists any missing section and any line that names paid-in capital. Fix both before the draft is saved. The engine never hands the letter a paid-in figure.

## 5. Deliver

Write the snapshots. In a scheduled run, end with the engine's `report.push_line`, or exactly `Nothing new`.
