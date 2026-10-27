<!-- Claude-run eval, round ten. Written by a Claude agent running the pulse skill against the mock connectors on a clean clone at a023dd2, writing bundle.json by hand in one Write call (the product council's rule); saved by the main session (the agent could not write files). -->

# Eval report: friday-meera (round 10)

- Plugin: instinct-vc 0.7.3 (`.claude-plugin/plugin.json`; pulse and morning-brief skills both 0.7.3)
- Commit: `a023dd2 Round ten: one nudge per note, drafts say what they need, money and asks followed after sending; version 0.7.3`
- `git status --short`: clean before and after (everything written is under the ignored `evals/runs/`)
- Member: `meera` (Meera Iyer, Associate, Quillwater Ventures, Asia/Kolkata)
- Run: Fri 23 Oct 2026, 06:29 IST, run id `r20261023T0629`, jobs `morning_brief` and `pulse`, build mode `daily`
- Skill: `skills/pulse/SKILL.md`, plus `skills/morning-brief/SKILL.md` steps 5 to 7; the weekday task in `schedules.json`
- Final line: `Sable Fraud AI: term sheet from Monsoon Arc Ventures, decide today`

Eval-mode adjustments: skipped pulse step 0 (no guard loads in eval mode); ran the engine from the clone; passed `--now 2026-10-23T06:29:00+05:30` to `due`; used the mock `db` commands for every Home read and write. Called mock `status` once to learn Gmail's tool list (no create-draft tool, so every draft stayed in Home). For Sable, the applying mark and the CRM call ran in one shell line, mark first.

## 1. What I ran, in order

Setup: clone at `a023dd2`, clean; `seed_eval.py friday meera` gave 14 snapshots, 14 runs, 6 drafts and 3 taps (`ns_d_rivulet_2026-10-22`, `ns_d_halo_2026-10-22`, `ns_d_sable_2026-10-22`); read the skills, shared docs and templates (no answer files opened).

1. `status`: everything connected; Gmail has no create-draft tool; the mock's own "now" reads Thu 22 Oct 07:00.
2. `db list` for snap, state and runs: 14 snap documents, 3 approved `next_step` taps stamped Thu 19:05, `state/items` empty, 14 run rows (last Thu 19:29). `versions.txt` (16 lines) and `config.json` written (associate, 450 words, 12 items, triage `own`, LP watch off).
3. `due --now 2026-10-23T06:29`: jobs `morning_brief, pulse`, mode `daily`, windows from Thu 19:29, run id `r20261023T0629`; run row created.
4. `actions`: 3 pending. `crm record` for the three deals: all open, each step still matched its payload. Each tap applied after its own applying mark (row versions 2, 3, 4), then re-read to confirm. `applied.json` written.
5. Reads: calendar (Friday and Saturday empty; 18 events 23 Sep to 6 Nov; next meeting Mon 26 Oct 10:00 partner meeting); Gmail since 16 Oct (19 threads, none after the window start); Granola since 22 Oct (nothing: Thursday's three meetings have no notes); CRM 45 deals (37 open), 90 companies, 100 people, 20 passes.
6. `bundle.json` written by hand in one Write call (60,311 bytes).
7. `build --mode daily --applied applied.json`: hero the Sable term sheet; push "Sable Fraud AI: term sheet from Monsoon Arc Ventures, decide today"; 12 items, 310 words, no warnings; 3 owed entries.
8. No prep cards (no meetings Friday or Saturday).
9. Draft sources read (transcripts tr15 and tr05; CRM notes empty; Drive empty). `owed-drafts.json` (3 drafts); `drafts` wrote 3, refused 0.
10. Brief check passed. `db batch` (brief, pipeline, proposals, directory, drafts at version 2); run row finished (version 5) with the three applying marks kept, the push line and key.

Totals: 11.1 minutes; 57 connector calls, 3 CRM writes; no send, reply, forward or draft-save calls.

## 2. The pending taps

1. `ns_d_rivulet_2026-10-22`: met 22 Oct, stage "Second meeting", `clear_step`. Applied in one call: stage to "Second Meeting", stage-entered date 22 Oct, next step and due cleared, last contact 22 Oct. Home now asks "Rivulet Payments: met 22 Oct, add the next step".
2. `ns_d_halo_2026-10-22`: same shape, same four changes, applied.
3. `ns_d_sable_2026-10-22`: step "Diligence kickoff" due 24 Oct, already in the CRM, so recorded under `already`; last contact 22 Oct. Result `{"status": "applied", "already": ["next_step", "next_step_due"]}`.

## 3. `run/owed.json` and the drafts

1. `dr_i_0e2115836d`, `reslot`: the Harborline Treasury pitch reply (score 93, call) offered Fri 23 Oct 10:00 and 11:00, today. New times Mon 26 Oct 14:00 and Tue 27 Oct 11:00 IST, clear of Monday's partner meeting. Context flags that Harborline is in Delaware and Bangalore: check the IST times suit Elena.
2. `dr_k_454489f888`, `refresh`: "Share feedback after the partner meeting" to Omkar (4 days late, holder Aditi), written before the 22 Oct "Rivulet Payments: follow-up", which has no notes. Opens "Good to see you on Thursday", keeps the three bracketed lines; context: fill in the 3 lines, check the firm's view with Aditi, check it still stands or tap Done if it was settled in the room.
3. `dr_k_48cf2d4ce7`, `refresh`: "Send the reference questions" to Abhishek (1 day late), written before the 22 Oct references meeting, no notes. Three suggested questions, marked as Instinct's; same check line.

Rightly not owed: the Trellis pricing view (a draft waits, no meeting since), the NBFC list for Leena (draft written after their meeting), the Copperleaf question (a reply waits), Halo's slot confirmation (looks done), Lattice KYC (already in touch), Dhruv Data (ask for more; associates draft replies only to calls).

## Writing bundle.json by hand

60,311 bytes in one Write call (deals 14.0 KB, companies 11.9 KB, people 11.8 KB, threads 10.8 KB, events 6.6 KB, passes 4.8 KB); about 3 minutes and 15,000 to 20,000 output tokens; 0 errors when checked field by field against the tool output. Partial people and companies saved about 25 KB. Hard parts: all or nothing (one slip means writing 60 KB again); nothing checks it; the documented shape drops company descriptions and pass ids; the text leaves some choices open; and every pulse needs it again (the 07:29 pulse needed 21,778 bytes, since the CRM cannot filter deals by update time: about 370 KB of copied JSON a weekday).

## 4. Next-run check

Rendered in the real page with the harness's mock runtime (phone width, Fri 06:35, no script errors).

- Hero: "Another fund is moving. Sable Fraud AI: term sheet from Monsoon Arc Ventures", their deadline before her next step, with Abhishek's quote; Open, Snooze.
- Push at 06:29: "Sable Fraud AI: term sheet from Monsoon Arc Ventures, decide today" (66 characters).
- Today: no meetings; Next up: Rivulet feedback (Overdue, Fill in 3 lines), Trellis pricing view (Due today, Fill in 3 lines), Sable reference questions (Overdue, Draft ready), Trellis competing fund (Urgent); Signals: Rivulet's round filling up; Commitments due (6); Ready for you: Rivulet and Halo "met 22 Oct, add the next step", Ember "met 21 Oct", and the Harborline draft.
- The 07:29 pulse, rebuilt from a hand-written 21,778-byte bundle: same 12 items, hero and met prompts; drafts and proposals unchanged; push "Review ready: Trellis Banking API: Saffron Peak Capital wants to lead" (Thursday's held review). Nothing lost.

## 5. Findings, worst first

1. **High (skill text and engine): a missed deal silently disappears.** When the CRM cannot filter by update time, `connectors.md` says to send every open deal without `crm.partial`, and "a deal missing from that list is no longer open". So every run hand-types about 37 deals. Leaving one out of a test pulse bundle (Mosaic Wealth Infra, her own deal, 16 days into a 10-day stage) made it vanish from her pipeline with no warning. Fix: never close a deal by leaving it out; when Home shows a deal open and the bundle omits it, keep it and warn; close a deal only when the bundle sends it with a closed stage. Have pulses send `crm.partial: true` with only the deals that changed against Home. Longer term, let the engine build the bundle from saved tool output.
2. **Medium (skill text): the morning brief's calendar range contradicts itself.** Step 2 says "Include today's and tomorrow's events"; the `connectors.md` row says 30 days back to 14 ahead. With only today and tomorrow, both refresh entries vanished. Fix: step 2 points at the connectors window, with today's and tomorrow's events making the agenda.
3. **Medium (engine and Home): People says "Today" for people not touched today.** Daily and pulse builds reuse People's `top` with `days_since` frozen at the last setup or digest. Fix: recompute `days_since` from `last_touch` and now on every build, and move `last_touch` forward with this run's meetings and mail.
4. **Low to medium (engine and skill text): narrow reads erode Home's directory.** The documented bundle shape has no company `description` and no pass `id`, and the engine replaces whole directory rows, so this run erased 49 descriptions and 20 pass ids. Fix: merge fields into existing rows and keep any field the bundle did not send; add both to the documented shape.
5. **Low to medium (skill text and engine): Friday prep stops at Saturday.** Monday's 10:00 partner meeting gets no prep until Monday's run. Fix: on a Friday, treat the next working day as "tomorrow" for prep cards.
6. **Low to medium (product): today's top three items wait on Aditi, and nothing helps Meera ask her.** Fix: an owed kind that drafts one short note to the deal's `holder`, listing each draft waiting on the firm's view and any competing deadline due today.
7. **Low (skill text): no way to know if the stage-entered date is writable.** Fix: setup records in `snap/config` whether it is, and under which field.
8. **Low (skill text): the `already` example names one field.** Fix: "list every field that already held its value".
9. **Low (skill text): the slot rule ignores the founder's time zone.** Fix: when the pitch or thread places the founder in another zone, prefer the overlap.
10. **Low (eval harness): the seeded history does not add up.** Taps stamped Thu 19:05 but the 19:29 run never applied them (stamp them after 19:29); the mock clock reads Thu 07:00 and the mail ends Wed 20:00; no Slack in the tool map.

## 6. Score: 7 out of 10 (as Meera)

The push names the one thing that cannot wait; her Thursday met logs landed correctly and Home asks for the two missing next steps; the stale Harborline times were replaced with real free slots; the two drafts written before Thursday's meetings were caught and refreshed honestly; nothing was sent or made up. It loses points because her hardest work today, the firm's view on Sable, Rivulet and Trellis, gets no help beyond bracketed shells; People says "Today" for people she did not contact; and Monday's partner meeting has no prep on a Friday. Behind the scenes, the 60 KB hand-typed bundle and the silent deal drop are risks she cannot see.
