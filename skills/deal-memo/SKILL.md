---
name: deal-memo
description: Drafts an investment committee memo for a deal at diligence or later from meeting notes, data room files, CRM notes, company data and references, with every claim linked to its source and no invented numbers. Use when the user says "write the memo for", "IC memo", "draft the investment memo", or "memo for partner meeting".
metadata:
  version: "0.10.0"
---

# Deal memo

The memo does the assembly so the investor can spend their time on judgment. Every factual claim links to its source. The judgment sections are left as clear prompts for the human.

Plugin root: `${CLAUDE_PLUGIN_ROOT}`. If that is not a real path, use the folder two levels above this skill's base directory. Follow `<plugin root>/shared/safety.md` throughout. Rule 5 governs this skill: no number without its source.

## 1. Find the deal

The deal the user named. If it is earlier than Diligence, say a memo usually starts at Diligence and ask whether to go ahead.

## 2. Gather sources

Give each source a short id and keep its full text in `sources.json` as `{"<id>": "<text>"}`:

- meeting notes and transcripts with the founders (id: the notes id),
- data room files from Drive or DocSend (id: the file id),
- CRM notes and fields for the deal (id: the note id),
- the founder threads of the last 60 days (id: the thread id),
- company data from PitchBook, Harmonic or Crunchbase, else web search (id: a short slug, keep the URL),
- reference call notes if any.

## 3. Draft

Follow `<plugin root>/templates/memo.md`. Write every factual sentence as a claim in `memo.json`:

```json
{"deal": "<company>", "claims": [{"section": "Traction", "text": "ARR is $2.4M, growing 9% month on month.", "source_id": "dr_lumen_metrics"}]}
```

Rules for claims:

- Copy numbers exactly as the source states them. Do not compute new numbers unless the formula is written in the claim ("Runway is about 13 months: $4.1M cash at $310K burn").
- One source per claim. If two sources disagree, write both claims and flag the conflict.
- If a number the template asks for is missing, write "Not in the data room" and add it to the open questions.

## 4. Check

```bash
python3 -I -S instinct-engine/instinct.py memo-check --memo memo.json --sources sources.json
```

Fix every unlinked claim and every number not found in its source. Run the check again until it passes. Never weaken a claim's source to pass.

## 5. Leave the judgment to the human

End with three headed prompts the investor fills in: "Why this could be a fund returner", "What would make us wrong", "Our recommendation". Under each, list the two or three facts from the memo that bear on it.

## 6. Deliver

Create the memo as a document the user can edit and share (the Docs artifact type when it is offered; otherwise a Google Doc when the user asks for one; otherwise a Markdown file). Each claim keeps its source link. Tell the user in one line how many claims, how many sources, and the open questions.
