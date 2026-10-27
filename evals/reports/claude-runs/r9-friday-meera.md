<!-- Claude-run eval, round nine. Written by a Claude agent running the pulse skill against the mock connectors; saved by the main session (the agent could not write files). -->

# Eval report: friday-meera

- Plugin: Instinct for VCs 0.7.2, commit 070b9d8. Engine `check`: ok, engine 0.7.2.
- Member: Meera Iyer, Associate, Quillwater Ventures (fictional).
- Run: her scheduled "Instinct" run, Fri 23 Oct 2026 06:29 Asia/Kolkata. Skill: `pulse`, which did the morning brief this morning.
- All my files are in `evals/runs/friday-meera/work/`.

## 1. What I ran, in order

Eval-mode adjustments:

- Pulse step 0 (guard canary): skipped. Eval mode loads no guard.
- Pulse step 1.1 (copy the engine): not done. Eval mode runs the engine from the repo with `python3 -I -S engine/instinct.py`.
- No questions for the user and no connector cards: every mock connector was connected.

The run:

1. `status`: every connector connected. Gmail has no create-draft tool.
2. Home link: the eval prompt carried none, so I took it from `artifact list` (`https://claude.ai/artifact/mock-instinct-home`).
3. `db list` for `snap`, `state` and `runs` into `work/home-db`. Pasted the snap and state result lines into `home-db/versions.txt`. Copied `snap/config.json` to `config.json`.
4. `due --now 2026-10-23T06:29:00+05:30`:
   - `run`: true.
   - Jobs: `morning_brief` and `pulse`. Build mode: `daily`.
   - Every connector window starts 2026-10-22T19:29.
   - Run id: `r20261023T0629`.
5. `db set runs/r20261023T0629` with `started` and `jobs`: version 1.
6. `actions`: 3 pending `next_step` taps. Nothing refused, nothing to check by hand.
7. For each tap: `crm record`, then an applying mark (`db update`, run row versions 2, 3 and 4), then one `crm update`, then `crm record` again (section 2).
8. Wrote `work/applied.json`.
9. Reads, using the Morning brief windows:
   - **Gmail:** `search --after 2026-10-16` found 19 threads, the newest Wed 21 Oct 20:00. I read all 19 with `thread`. Nothing has arrived since the window start.
   - **Calendar:** 23 Sep 06:29 to 6 Nov 06:29 holds 18 events. There are none today or tomorrow. Next is the Mon 26 Oct partner meeting.
   - **Granola:** `list --after 2026-10-22` returned nothing. No notes exist for Thursday's Sable, Rivulet or Halo meetings.
   - **CRM:**
     - Deals: 45 returned, 37 kept. I left out 6 Passed and 2 Portfolio. They already showed this run's writes.
     - Companies 90, people 100, notes 5, pass log 20.
   - **Drive:** `search empathy` returned nothing, so the bundle has `empathy_maps: {}`.
   - **LP data:** not read. LP watch is off for an associate, so there is no `lps` key.
   - Nothing new arrived (no pitches, notes or founder updates). So there were no extracted, inbound, KPI, ask or pack files.
10. Wrote `work/bundle.json` from those reads, not from the `bundle` shortcut. I used a small helper, `work/assemble_bundle.py`, to copy the reads into the bundle shape. It sets `now` to 06:29, `transcripts: []` and no `lps` key.
11. `build --mode daily --run-id r20261023T0629 --started 2026-10-23T06:29:00+05:30 --jobs morning_brief,pulse --applied applied.json`:
    - Exit 0. 12 items, 309 words (budget 450), no warnings.
    - Push (send true): "Sable Fraud AI: term sheet from Monsoon Arc Ventures, decide today".
    - `owed.json`: 3 entries.
12. Prep questions: none to write. `snap/prep` has no cards, because there are no meetings today or tomorrow.
13. Sources for the drafts:
    - `granola transcript` for tr05 (Sable, 20 Oct) and tr15 (Rivulet, 17 Oct). For my own context I also listed notes from 15 Oct onwards.
    - `drive search` for Rivulet, Sable, feedback, partner meeting and Harborline: nothing.
14. Wrote `work/owed-drafts.json` with 3 drafts, all `in_gmail: false`. Gmail has no create-draft tool, so there were no drafting marks.
15. `drafts --out run --drafts owed-drafts.json`: 3 written, 0 refused.
16. Brief check (morning-brief step 7) found one repeated fact (finding 4). I added it to the run row's `warnings`.
17. `db batch` with `run/home/batch.json` wrote pipeline v2, proposals v2, drafts v2 and brief v2. The other documents were unchanged and skipped.
18. `db update runs/r20261023T0629 --if-version 4` from `run/home/run.json` plus my warning: version 5.
19. Final line: `Sable Fraud AI: term sheet from Monsoon Arc Ventures, decide today`

Audit from `mock_log.jsonl`:

- 3 CRM writes, all for approved taps.
- No send, reply, forward or Gmail draft attempt. No calendar write.

## 2. The pending taps

All three were saved Thu 22 Oct 19:05 from the met-log form. Each deal was still open, and each still held the payload's `current` and `current_due`, so all three applied.

### Rivulet Payments (`ns_d_rivulet_2026-10-22`)

- Payload: `text` null, `due` null, `current` "Second meeting", `current_due` 2026-10-24, `met` 2026-10-22, `stage` "Second meeting", `clear_step` true.
- Applying mark: 2026-10-23T06:30:00. Then one CRM call: `{"next_step": null, "next_step_due": null, "last_contact": "2026-10-22", "stage": "Second Meeting", "stage_entered": "2026-10-23"}`.

| Field | Before | After |
| --- | --- | --- |
| stage | First Meeting | Second Meeting |
| stage_entered | 2026-10-17 | 2026-10-23 |
| next_step | Second meeting | null |
| next_step_due | 2026-10-24 | null |
| last_contact | 2026-10-19 | 2026-10-22 |

- `applied.json`: `{"status": "applied"}`.

### Halo Reconcile (`ns_d_halo_2026-10-22`)

- Payload: the same shape as Rivulet: no text, `clear_step` true, `met` 2026-10-22, `stage` "Second meeting".
- Applying mark: 06:30:20. Then one CRM call with the same five fields.

| Field | Before | After |
| --- | --- | --- |
| stage | First Meeting | Second Meeting |
| stage_entered | 2026-10-10 | 2026-10-23 |
| next_step | Second meeting | null |
| next_step_due | 2026-10-24 | null |
| last_contact | 2026-10-19 | 2026-10-22 |

- `applied.json`: `{"status": "applied"}`.

### Sable Fraud AI (`ns_d_sable_2026-10-22`)

- Payload: `text` "Diligence kickoff", `due` 2026-10-24, the same as `current` and `current_due`. `met` 2026-10-22. `stage` null.
- Applying mark: 06:30:40. Then one CRM call: `{"last_contact": "2026-10-22"}`. The step and its date already held the payload's values, so I did not write them again. There was no stage move.

| Field | Before | After |
| --- | --- | --- |
| stage | Second Meeting | Second Meeting |
| next_step | Diligence kickoff | Diligence kickoff |
| next_step_due | 2026-10-24 | 2026-10-24 |
| last_contact | 2026-10-21 | 2026-10-22 |

- `applied.json`: `{"status": "applied", "already": ["next_step", "next_step_due"]}`.

Notes on these choices:

- **Stage option.** "Second meeting" maps to the CRM's own option "Second Meeting". Six deals already held that option, so nothing new was created.
- **Stage date.** I wrote `stage_entered` as today because pulse step 3 says so. See finding 6.
- **Snapshot.** `snap/proposals` now shows all three as applied. Rivulet and Halo are titled "Met 22 Oct, stage to Second meeting". Sable is titled "Next step: Diligence kickoff".

## 3. Every entry in `run/owed.json`

### 1. `dr_i_0e2115836d` (reslot): Elena Fischer, Harborline Treasury

- Why: a reply to her pitch (score 93, call), waiting since Thursday. It offered Fri 23 Oct at 10:00 and 11:00, which is today and too short notice.
- Subject: `Re: Harborline Treasury` (kept).
- Body:
  > Hi Elena,
  > Thanks for sending Harborline Treasury our way. It fits what we back, and we would like to hear more. Would Mon 26 Oct at 14:00 or Tue 27 Oct at 11:00 IST work for a 30-minute call?
  > Meera
- Context: "Inbound pitch, score 93: call. The times it first offered (Fri 23 Oct) were too close, so two new ones from your calendar".
- Slots: 2026-10-26T14:00+05:30 and 2026-10-27T11:00+05:30.
  - Both are working days after today, between 10:00 and 18:00.
  - Both are clear of the only event in the next seven working days, the Mon 10:00 to 11:00 partner meeting.
  - `avoid_slots` was empty, and no other open draft offers times.
- Sources: the pitch email (`in_harborline`) and the calendar read.
- Gaps: none.

### 2. `dr_k_454489f888` (refresh): Omkar Patil, Rivulet Payments

- Why: written Thu 06:29 before the Thu 13:00 "Rivulet Payments: follow-up" meeting. That meeting has no notes.
- Subject: `Rivulet Payments: our feedback` (kept).
- Body:
  > Hi Omkar,
  > Good to see you on Thursday.
  > As promised, here is the feedback after the partner meeting.
  > [Where we landed, in one line]
  > [What we liked]
  > [What we would want to see next]
  > Happy to talk it through.
  > Meera
- Context: "Written before your 22 Oct meeting, which has no notes: check it still stands, or tap Done if you gave the feedback in the room. If not, fill in the 3 lines: your notes and Drive still hold no written feedback".
- Sources:
  - tr15, line 2: the promise "I'll come back with feedback after our Monday partner meeting".
  - No notes for Thursday's meeting. No Drive file. No CRM note on `d_rivulet`.
- Gaps: the three feedback lines are the firm's view, and no source holds them. I left the brackets. The entry had no `holder`, so the context cannot name Aditi (finding 7).

### 3. `dr_k_48cf2d4ce7` (refresh): Abhishek Joshi, Sable Fraud AI

- Why: written Thu 06:29 before the Thu 10:00 "Sable Fraud AI: references" meeting. That meeting has no notes.
- Subject: `Sable Fraud AI: reference questions for your customers` (kept).
- Body:
  > Hi Abhishek,
  > Good to see you on Thursday.
  > As promised, here are our reference questions so you can brief your customers:
  > 1. How long did it take to go live with Sable?
  > 2. What change have you seen in false positives since launch?
  > 3. What would make you expand your use of Sable next year?
  > Thanks for the fraud loss benchmarks you are sending over.
  > Meera
- Context: "Written before your 22 Oct references meeting, which has no notes: check it still stands, or tap Done if it was settled in the room. The three questions are Instinct's suggestions, not from your notes: edit them freely".
- Sources:
  - tr05, line 2: the promise.
  - tr05, line 3: the benchmarks Abhishek owes, now 2 days late.
  - tr05, line 1: the topics (two issuers live, false positives down 40%).
  - No notes for Thursday's meeting. No Drive file.
- Gaps: no brackets. The three questions came from Thursday's draft and are in no source. I kept them, as step 6.5 says, and said so in the context (finding 1).

The engine left two waiting drafts out of `owed.json`, which is correct:

- Trellis "our view on pricing" (due today) was already drafted.
- The Copperleaf timeline reply was already drafted.

## 4. Next-run check (not a skill step)

I rebuilt the Fri 07:29 run locally in `work/next/`. I read Home again, did the Pulse reads and built into a local folder. I did not write to Home and did not create a run row.

- `due` (07:29): jobs `pulse`, windows from 06:29. `actions`: nothing pending.
- Reads:
  - 0 new mail, plus 14 threads from founders of open deals over the last 7 days.
  - 0 events today or tomorrow.
  - 0 notes.
  - 37 open deals, with no `crm.partial`, because the mock CRM cannot filter by update time.
- The build ran clean.

### Is there a "met 22 Oct, add the next step" prompt for Halo and Rivulet?

Yes. `snap/pipeline.met_prompts` holds:

- Rivulet Payments: `step_only: true`, aid `nss_d_rivulet_2026-10-22`, met_on 2026-10-22, `next_step` null.
- Halo Reconcile: `step_only: true`, aid `nss_d_halo_2026-10-22`, met_on 2026-10-22, `next_step` null.
- Ember Credit: the ordinary met-log form for 21 Oct, which has not been logged yet.

Home's Today renders these as "Rivulet Payments: met 22 Oct, add the next step" and "Halo Reconcile: met 22 Oct, add the next step". This run's own snapshot already holds the same prompts, so Meera sees them from 06:29.

### Does any Pipeline deal still show the old step?

Not after this run.

- Rivulet and Halo:
  - No next step, stage "Second meeting", day 0.
  - Their Pipeline rows read "Met 22 Oct. Add the next step".
- No deal anywhere carries "Second meeting by 24 Oct". The only "Second meeting" step left is Copperleaf's own live step, due 25 Oct.
- Sable keeps "Diligence kickoff by 24 Oct".
- Overnight, though, the Pipeline tab did show the old step. From Thu 19:05 to Fri 06:29 the Rivulet and Halo rows said "Next: Second meeting by 24 Oct" (finding 2).

### What do the two drafts written before Thursday's meetings say in their context?

On the next run they are unchanged from what this run wrote. They are not listed for refresh again, because the `drafts` command moved their `made_at` to 06:29 today.

- Rivulet: "Written before your 22 Oct meeting, which has no notes: check it still stands, or tap Done if you gave the feedback in the room. If not, fill in the 3 lines: your notes and Drive still hold no written feedback".
- Sable: "Written before your 22 Oct references meeting, which has no notes: check it still stands, or tap Done if it was settled in the room. The three questions are Instinct's suggestions, not from your notes: edit them freely".

Before this run they said:

- Rivulet: "You promised this on 17 Oct, due 19 Oct. Instinct found no written feedback in your notes or Drive. Fill in the 3 lines before you send".
- Sable: "You promised this on 20 Oct, due 22 Oct".

### Also seen on the next run

- It would push "Review ready: Trellis Banking API: Saffron Peak Capital wants to lead" (finding 12).
- The brief still has the lowercase "rivulet Payments" line (finding 3) and the repeated Rivulet fact (finding 4).
- The headline still says "3 meetings to log" (finding 5).
- Lattice KYC's `in_touch` flips to null (finding 11).

## 5. Findings, worst first

### 1. A refresh keeps lines that no source holds

- **What happened.** Thursday's run wrote three reference questions into the Sable draft. None is in any source. The 20 Oct notes (tr05) hold only the promise, "two issuers are live" and "false positives are down forty percent". Thursday's context did not say the questions were Instinct's own. This run is told to keep them, so content no source holds goes to a founder under Meera's name.
- **Where.** `skills/morning-brief/SKILL.md` step 6.5 says "Its own lines were written from sources by an earlier run ... keep them". Step 6.1 says "Write from those sources only ... never a guess". 6.5 assumes something that was not true here.
- **Change.**
  - Say whether Instinct may write content such as questions. If it may, the context must say "suggested by Instinct" every time.
  - On a refresh, check each kept line against the draft's `source_url` before keeping it.

### 2. The Pipeline tab does not see met logs saved under dated ids

- **What happened.**
  - `dealRow` in `home/index.html` (line 1189) looks up `actionOf("ns_" + id)`.
  - Met logs are saved as `ns_<deal>_<met date>`, and step-only taps as `nss_<deal>_<met date>`. `actionOf` (line 500) is an exact match.
  - So after Meera saved the logs at 19:05 Thursday, the Rivulet and Halo rows kept showing "Next: Second meeting by 24 Oct" until this run. That step was the meeting that had already happened.
  - A step typed in Today's step-only form never shows as "saving to CRM" in Pipeline.
  - The Pipeline row's own form (line 1223) saves `ns_<deal>`, which Today's prompt does not check. So Today keeps asking for a step she just typed in Pipeline until the next run.
  - If an undated log with `text: null` exists, line 1191 prints "null (saving to CRM at the next check)".
- **Change.**
  - Look up the newest approved `ns_<deal>_*` or `nss_<deal>_*` tap.
  - Show "Met 22 Oct, saving to your CRM" when a log has no text.
  - Use one id scheme for both forms.

### 3. The brief lowercases the company name when it folds in a stage move

- **What happened.** The brief prints "Deal: rivulet Payments moved to Second Meeting." and "Deal: halo Reconcile moved to Second Meeting." This shows in Home, in `brief.md` and in the Copy brief text (`brief-shareable.md`) that Meera may paste for colleagues. The next run repeats it.
- **Where.** `engine/instinct/brief.py`, around line 931.
  - A `deal_move` title is "<Company> moved to <stage>", with no ": ".
  - So `split(": ")` keeps the company name, and `_lower_first` lowercases it.
  - The stage also uses the CRM's spelling, "Second Meeting", where Home says "Second meeting".
- **Change.** Title deal moves "<Company>: moved to <stage>", or strip the company before folding. Show Home's stage label.

### 4. One fact appears twice in the brief

- **What happened.** "The round is filling up" sits on the Rivulet feedback promise line under Next up. The same signal also has its own row under Signals. Step 7 says no two lines say the same thing. I logged it in the run row's warnings, as the skill says.
- **Where.** `engine/instinct/brief.py`, lines 169 to 182. A late promise to a company where another fund is moving takes the signal's phrase, and the signal keeps its own row.
- **Change.** When the phrase rides on a promise line, drop the signal's own row, or do not attach it.

### 5. "3 meetings to log" counts meetings Meera already logged

- **What happened.** Home's headline reads "12 things for today, 5 urgent, and 3 meetings to log". Two of the three are Halo and Rivulet, which she logged on Thursday. They only need a next step, and she may think her taps failed. `brief.md` and the Copy brief say only "12 things for today, 5 urgent", so the two headlines also differ.
- **Where.** `engine/instinct/cli.py`, around line 2367: `n_log = len(met_prompts)`.
- **Change.** Count step-only prompts apart, for example "1 meeting to log, 2 next steps to add".

### 6. Stage date: the skill says "today", the engine says the meeting day

- **What happened.**
  - Pulse step 3 says to set a writable stage-entered date to today. It also says "Home counts the days in the new stage from today either way".
  - The engine actually dates a met-log move from the meeting (`_applied_stage_moves`, `cli.py` around line 1797).
  - I followed the skill and wrote 23 Oct for Rivulet and Halo. The CRM's date is later, so it wins, and Home shows day 0.
  - A local what-if build without that write gives 22 Oct, day 1.
  - So the firm's CRM now says both deals entered Second Meeting a day after the meeting that moved them.
- **Also.** `shared/safety.md` rule 7 says "apply the proposal's own fields, nothing else", and the guard text says "apply only the fields the approved proposal names". `stage_entered` is not in the payload, so the two texts pull against each other.
- **Change.**
  - In `skills/pulse/SKILL.md` step 3, set the stage date to the payload's `met` date.
  - Fix the "from today" sentence.
  - Say plainly that this one extra field is allowed.

### 7. Refresh entries lose the promise's context

- **What happened.**
  - `owed.json` refresh entries carry no `holder`, `what`, `due` or `overdue`. The engine sets `holder` only on `promise` entries (`cli.py` around line 1488).
  - The Rivulet feedback is the firm's view, and Home names Aditi Rao as the deal's partner. But the refresh cannot say "check it with Aditi".
  - The engine's suggested context also replaces the old one, which told Meera to fill in the three lines. Step 6.5 does not say to keep that, so I merged them by hand.
- **Change.** Carry `holder` and the due date onto refresh and reslot entries. In step 6.5, say "keep what the old context asked for, then add the check".

### 8. The by-hand bundle is very large for a guarded run (inferred, not seen)

- **What happened.**
  - This morning's bundle is about 100 KB: 90 companies, 100 people, 37 deals, 19 threads and 18 events. The CRM part alone is 62 KB.
  - The real guard allows only the engine and plain file commands, so a real run must type all of it through the Write tool every morning.
  - I used a small script here. A real run cannot.
- **Risk.** Slow runs, cut-off files, or retyped values that drift from the CRM.
- **Change.** Let the engine take the raw connector results as files and assemble the bundle. Or narrow the morning CRM read, for example to people at open-deal, portfolio and meeting companies.

### 9. Small gaps in pulse step 3 for `next_step`

- **Same values.** Sable kept the same step and date. The skill says "set the next step and its due date" but not what to do when they already hold those values. I wrote only `last_contact` and recorded `already`. The engine and Home took it fine.
- **Empty value.** "Empty the next step" does not say whether to write null or "". I used null, and the engine read it as no step.
- **Change.** Add one sentence for each case.

### 10. Friday's brief does not draft a promise due Monday

- **What happened.** Ember, "Share our NBFC partner list", is due Mon 26 Oct. The two-day horizon counts calendar days (`due_view(..., horizon_days=2)` in `engine/instinct/commitments.py`). So on a Friday it waits until Monday 06:29.
- **Change.** Count working days, or reach over the weekend on Fridays.

### 11. Pulse runs blank a fact the morning read found

- **What happened.**
  - In the next-run rebuild, Lattice KYC's pitch flips `in_touch` from true to null.
  - The Pulse row reads only threads with founders of open deals, so Meera's own thread with Sonia (`th0233`) is not read.
  - The Pitches list loses "You already write to them" every hour, and `snap/inbound` is rewritten every run.
- **Change.** Carry `in_touch` forward from Home when the thread was not in this run's read.

### 12. Thursday's review is pushed on Friday, against the delivery doc

- **What happened.** The 07:29 run would push "Review ready: Trellis Banking API: Saffron Peak Capital wants to lead". That is one hour after the morning push.
- **Where.**
  - The engine means to do this: `cli.py` around line 1071 sends the review on the next working day.
  - `shared/delivery.md` says a held line goes "at the next free run the same day, or stays in Home".
- **Change.** Add the review exception to `delivery.md`, or drop it.

### What worked well

- **Run row.** `due`, `actions` and the run row flow were clear and exact. The version pins never conflicted.
- **Tap rules.** The `next_step` rules were easy to follow:
  - check the deal is still open;
  - check the current values;
  - one CRM call;
  - last contact only when later;
  - the CRM's own stage option.
- **Met prompts.** The engine turned both `clear_step` logs into step-only prompts in the same run. The old step was gone from the rebuilt data.
- **Owed list.** `owed.json` was right:
  - a reslot for today's call times;
  - refreshes for both drafts written before Thursday's meetings;
  - no second draft for Trellis or Copperleaf.
  - Refreshed drafts get a new `made_at`, so they do not come back.
- **No create-draft tool.** Handled cleanly: drafts stay in Home, no marks, no workaround.
- **Hero and push.** They fit an associate: her own deal's deadline today. 309 words, within budget, and every line has a source.
- **Safety held.** No sends, deletes, Gmail drafts or calendar writes. CRM writes only for the three approved taps.

## 6. Score

**7 / 10.** The core loop worked: it applied the taps, cleared the old step, asked for the new one and refreshed the drafts. Before a partner sees it, fix the brief text bugs, the Pipeline tab's overnight lag, the stage date written a day late and the carried-forward questions that no source holds.
