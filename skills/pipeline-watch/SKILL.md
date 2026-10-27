---
name: pipeline-watch
description: Watches a venture firm's deal pipeline for stale deals, missing next steps and signals that another fund is moving, and writes the weekly pipeline review and the partner-meeting pre-read. Use when the user says "pipeline review", "which deals are stuck", "partner meeting pre-read", "where are my deals", or when a scheduled task runs pipeline-watch.
metadata:
  version: "0.7.8"
---

# Pipeline watch

Three jobs. Every hour (inside the pulse): catch stale deals and competing funds. Thursday afternoon: the weekly review. Sunday evening: the partner-meeting pre-read. The scheduled run's `due` command says when the review and pre-read are due.

Plugin root: `${CLAUDE_PLUGIN_ROOT}`. If that is not a real path, use the folder two levels above this skill's base directory. Follow `<plugin root>/shared/safety.md` throughout.

## 1. Load and gather

Copy the engine and read Home (`skills/pulse/SKILL.md` step 1). Gather the CRM deals, the last 14 days of mail with founders of open deals (full text of their latest messages), and the last 14 days of calendar. Without a CRM, use `snap/pipeline` from Home as the deal list. Write `bundle.json`.

## 2. Build

```bash
python3 -I -S instinct-engine/instinct.py build --bundle bundle.json --config config.json --home ./home-db --versions ./home-db/versions.txt --out run --mode review
```

The engine marks a deal stale when it is past its stage's dwell time, has no next step, has an overdue next step, or has had no contact in 7 days at First meeting or later. It flags a competing fund when a founder's own email says another fund has a term sheet, wants to lead, the round is filling, or there is a decision deadline. Our own emails never count.

## 3. Read the signals yourself

Open each competing-fund thread in `run/report.json` and the pipeline snapshot. Confirm the evidence line says what the founder said, and the deadline is right. If the engine missed a clear signal in a thread you read (for example "we're signing with another fund on Monday"), add it to the review by hand with its source link and a short reason.

## 4. Write the review (Thursday mode)

Use `<plugin root>/templates/pipeline-review.md`. Sections: moves this week, deals that need a call, stale deals with one suggested next step each, competing funds with deadlines, share of active deals with no next step. Every line links to the deal or thread as a markdown link. Under 300 words. Save it as `review.md` and pass it to the build with `--digest review.md --digest-kind review`; Home shows it on the Pipeline tab for a week.

## 5. Write the pre-read (Sunday mode)

Use `<plugin root>/templates/partner-preread.md`: moves this week, decisions needed (deals at partner meeting or term sheet, and deals with a competing fund), portfolio flags (from `snap/portfolio`), inbound worth discussing (score 70 or more). One line per item with the ask for the partners, each linked. Under 400 words. Partners read this: leave out every quiet deal. Save it as `preread.md` and pass it with `--digest preread.md --digest-kind preread`; the build warns if a quiet deal slipped in.

## 6. Propose next steps

For each stale deal the user owns, propose one dated next step ("Book a reference call with two customers by Tue 27 Oct"). Save each in `snap/proposals` as a `crm_update` proposal, status `proposed`, with fields `next_step` and `next_step_due`, each with its `current` value from the CRM and the `proposed` one (shape in `shared/home.md`). The user taps Approve in Home; the next pulse writes it to the CRM.

## 7. Deliver

Write the snapshots. In chat, show the review or pre-read. In a scheduled run, end with the engine's `report.push_line`.
