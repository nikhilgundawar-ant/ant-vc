<!-- Claude-run eval, round seven. Written by a Claude agent running the pulse skill against the mock connectors; saved by the main session. -->

# friday-meera: Meera's scheduled run, Fri 23 Oct 2026, 06:29 IST

Instinct for VCs 0.6.0, pulse skill, against the mock connectors. All files are in `evals/runs/friday-meera/work/`. Every connector and Home call went through `INSTINCT_RUN=friday-meera python3 evals/mock_connectors.py --as meera ...`. No real tool was called. No skill was edited. No answer file was opened.

## 1. What I ran, in order

1. Read `evals/eval-mode.md`, `skills/pulse/SKILL.md`, `shared/safety.md`, `shared/engine.md`, `shared/home.md`, `shared/connectors.md`, `skills/morning-brief/SKILL.md`, and the post-meeting, inbound-triage and portfolio-watch skills, plus `templates/pass-note.md`. Later I read the engine code for owed entries and the `drafts` command (`engine/instinct/cli.py`) to see what reslot and refresh mean. I also read the top of `evals/mock_connectors.py` to see how it handles paths and logging.
2. Step 0 (guard canary): skipped. Eval mode loads no guard.
3. `status`: every connector connected. Gmail has no `create_draft`, so drafts stay in Home.
4. Step 1: Home link taken from the prompt. `db list` for `snap`, `state` and `runs` into `work/home-db`. Pasted the snap and state lines into `home-db/versions.txt`. Copied `snap/config.json` to `config.json`.
5. Step 2: `python3 -I -S engine/instinct.py due --home ./home-db --config config.json --now 2026-10-23T06:29:00+05:30`. Result: `run` true, jobs `morning_brief` and `pulse`, `build_mode` daily, `window_start` 2026-10-22T19:29+05:30 for every connector, `run_id` r20261023T0629.
6. Created the run row: `db set --collection runs --id r20261023T0629 --json '{"started": "2026-10-23T06:29:00+05:30", "jobs": ["morning_brief", "pulse"]}'` (version 1).
7. Step 3: `actions --home ./home-db`. One pending tap, `ns_d_halo`. Applied it (section 3 below). Wrote `applied.json`.
8. Step 4, Morning brief windows:
   - `bundle` called once to look at it. Not used: it is pinned to the mock clock (now 22 Oct 07:00) and is not windowed (68 threads, events from July).
   - `gmail search --after 2026-10-16` (7 days): 19 threads. `gmail search --after 2026-10-22`: none.
   - `granola list --after 2026-10-22`: none. `granola list --after 2026-10-14`: 5 older notes, all already processed.
   - `calendar list` from 23 Sep to 6 Nov: 18 events. Nothing today or tomorrow. Next is Mon 26 Oct 10:00 to 11:00, Monday partner meeting.
   - `crm deals`, `companies`, `people`, `notes`, `passes`, and `carta lps`.
   - `gmail thread` for all 19 threads, plus `neg_copperleaf` (a waiting draft depends on it).
   - Wrote `bundle.json` by hand: now 23 Oct 06:29, 19 threads (latest message, plus Meera's own latest when someone wrote after it), 18 events, `transcripts: []` (read, nothing new), the full CRM, pass log and LP list.
   - Nothing new since the window start: no notes, pitches or founder updates. So no `extracted`, `inbound`, `kpis`, `asks` or `packs` files.
9. Step 5: `build --mode daily --run-id r20261023T0629 --started 2026-10-23T06:29:00+05:30 --jobs morning_brief,pulse --applied applied.json`. Three owed entries. Push `send` true.
10. Prep questions: `run/home/snap__prep.json` has no cards. There are no meetings today or tomorrow, and the push names no prep card. Nothing to write, so I did not run `questions`.
11. Sources for the drafts: `granola transcript` tr05 and tr15; 7 `drive search` calls (reference, Sable, Rivulet, partner meeting, feedback, questions, Harborline): nothing; `crm notes` for d_rivulet and d_sable: none; `granola list --after 2026-08-01`; 10 `gmail search` queries; `gmail thread th0350`.
12. Wrote `owed-drafts.json`. Ran `drafts --out run --drafts owed-drafts.json`: 3 written, 0 refused.
13. Morning brief step 7 check: the hero states a fact (Sable term sheet), every line has a source, 279 words against a 450 budget, no warnings.
14. Step 6: `db batch --file run/home/batch.json` wrote pipeline, proposals, drafts and brief (each now version 2). `db update --collection runs --id r20261023T0629 --file run/home/run.json --if-version 2` (version 3). `db get` to confirm.
15. Sanity check, not a skill step, local files only: rebuilt the new Home in `work/verify-home` and ran `actions` (nothing pending) and `due` at 07:29 (pulse only, no second brief).

No questions to the user. No connector cards to suggest. No Gmail drafts.

## 2. Every entry in run/owed.json

All three rewrite drafts already waiting in Home. All keep their ids. All are in Home with `in_gmail` false and no drafting mark, because there is no create-draft tool.

### dr_i_0e2115836d: reslot, to Elena Fischer (elena@harborline.co), Harborline Treasury

- Pitch scored 93, decision call. The waiting draft offered Fri 23 Oct 10:00 and 11:00 IST, which is today. `avoid_slots` was empty.
- Subject (kept): "Re: Harborline Treasury"
- First two sentences: "Thanks for sending Harborline Treasury our way. It fits what we back, and we would like to hear more."
- The times sentence: "Would Mon 26 Oct at 11:30 or Tue 27 Oct at 10:00 IST work for a 30-minute call?"
- Times offered: Mon 26 Oct 11:30 to 12:00 IST and Tue 27 Oct 10:00 to 10:30 IST. Both are weekdays after today. Monday's only event ends at 11:00, so 11:30 leaves a gap. Tuesday is empty. No other draft offers times.
- `slots` recorded: `["2026-10-26T11:30:00+05:30", "2026-10-27T10:00:00+05:30"]`
- Context: "Inbound pitch, score 93: call. The times it offered were today, too short notice: two new ones from your calendar"

### dr_k_454489f888: refresh (met_on 2026-10-22), to Omkar Patil (omkar@rivuletpay.com), Rivulet Payments

- Promise k_454489f888, "Share feedback after the partner meeting", made 17 Oct, due 19 Oct.
- Subject (changed): "Rivulet Payments: feedback after our partner meeting". The old subject, "Share feedback after the partner meeting", read like a task.
- First two sentences: "Thanks, good to catch up on Thursday. As promised, here is our feedback after the partner meeting."
- The three gaps stay: "[Where we landed, in one line]", "[What we liked]", "[What we would want to see next]". No written feedback exists in notes, Drive, the CRM or mail.
- Why only one line: the 22 Oct 13:00 "Rivulet Payments: follow-up" has no notes, so I could not say what was said. The context asks Meera to fill the lines, or tap Done if she gave the feedback in that meeting.
- No times offered.

### dr_k_48cf2d4ce7: refresh (met_on 2026-10-22), to Abhishek Joshi (abhishek.joshi@sablefraud.ai), Sable Fraud AI

- Promise k_48cf2d4ce7, "Send the reference questions", made 20 Oct, due 22 Oct.
- Subject (kept): "Sable Fraud AI: reference questions for your customers"
- First two sentences: "Thanks for making time on Thursday. As promised, here are our reference questions so you can brief your customers:"
- Kept the three questions and the closing line about the fraud loss benchmarks.
- The 22 Oct 10:00 "Sable Fraud AI: references" has no notes. The three questions are in no source (not in tr05, Drive or the CRM), so the context says so: "The 3 questions are not in your notes: check them before you send".
- I left out the Monsoon Arc term sheet deadline. No source holds an answer, and the hero already covers it.
- No times offered.

Not in owed.json and untouched: the pricing view to Neha (dr_k_a4b63d1828, due today) and the timeline reply to Debashish (dr_ca724068f9). Both are still waiting in Home.

## 3. The waiting tap

- `ns_d_halo`, type `next_step`, Halo Reconcile, tapped 22 Oct 19:05. Payload: text "Diligence plan with the CFO", due 2026-10-30, current "Second meeting", current_due 2026-10-24, met 2026-10-22, stage "Second meeting".
- Re-read: `crm record --id d_halo`. Stage "First Meeting" (open). Next step "Second meeting", which matches `current`. Due 2026-10-24. Last contact 2026-10-19.
- Applying mark first: `db update --collection runs --id r20261023T0629 --json '{"applying": {"ns_d_halo": "2026-10-23T06:29:00+05:30"}}' --if-version 1`
- One CRM write: `crm update --id d_halo --json '{"next_step": "Diligence plan with the CFO", "next_step_due": "2026-10-30", "last_contact": "2026-10-22", "stage": "Second Meeting"}'`
  - `next_step` and `next_step_due`: the payload's `text` and `due`.
  - `last_contact`: the payload's `met`, because the CRM held an earlier date.
  - `stage`: "Second Meeting", the CRM's own spelling of the payload's "Second meeting".
- `crm record` again: all four fields set. `stage_entered` stayed 2026-10-10.
- `applied.json`: `{"ns_d_halo": {"status": "applied"}}`. No field already held its new value and none was skipped.
- The build turned it into `snap/proposals` item `ns_d_halo`, status applied, applied_at 06:29. Halo's "you met them" prompt is gone from the pipeline.

## 4. Final line

Sable Fraud AI: term sheet from Monsoon Arc Ventures, decide today

That is `report.push_line`, 66 characters, with `report.push.send` true.

## 5. Where the skill text was unclear, contradictory or impossible to follow

Most important first.

1. **Which stage name to write to the CRM.** `skills/pulse/SKILL.md` step 3: "when it has `stage`, move the deal to that stage (never to passed or closed: the engine refuses those)." The payload holds Home's name ("Second meeting"). The CRM's option is "Second Meeting". `shared/engine.md` says "Use CRM ids and stage names exactly as the CRM shows them. The engine maps stage names to its own stages", but nothing says how to map back for a write. A real CRM may reject the wrong label, or create a new option and set off automations. The skill also never says what happens to the stage date. The mock kept `stage_entered` at 10 Oct, so Home now shows Halo at 13 days in Second meeting, against a norm of 10. A Sheet or Notion CRM, which has "the date it entered the stage" as a column (`shared/connectors.md`), would go stale the same way.
2. **Refresh when the meeting has no notes.** `skills/morning-brief/SKILL.md` step 6.4: "`kind: "refresh"` means you met the person on `met_on` after it was written, so read that meeting's notes and rewrite it to reflect what was said, or keep it with one line on the meeting when it still stands". All three 22 Oct meetings have no notes. Without them I cannot tell whether the promise "still stands" (Meera may have given Omkar the feedback in the room). The text does not say what the "one line" may claim when nothing is recorded.
3. **"Keep it" versus "sources only".** The same step 6.4 says to keep the waiting draft. But step 6.1 says "Write from those sources only ... Leave a bracketed gap ... only when the tools truly do not hold it, never a guess", and `shared/safety.md` rule 4 says "A line without a source is dropped." The waiting Sable draft lists three reference questions that are in no source. Keeping it breaks 6.1. Rewriting it breaks 6.4. I kept the questions and flagged them in `context`.
4. **owed.json is said never to list what step 4 then rewrites.** `skills/morning-brief/SKILL.md` step 6, opening paragraph: "It never lists a flagged pitch, a pitch from a founder the user already talks to ..., or anything drafted before." Every entry today was a draft already waiting (reslot or refresh). That paragraph lists what owed.json holds and leaves these kinds out. Only point 4, and `shared/engine.md`, explain them.
5. **"Passed" does not match what the engine does.** Step 6.4: "`kind: "reslot"` means the times it offered have passed". The engine also reslots times later the same day, which matches the other rule in that step ("A time today or earlier is never left in a draft"). At 06:29 the 10:00 and 11:00 slots had not passed, so the engine's own context line ("The times this draft offered have passed") was false. I wrote my own context.
6. **No rules for picking times without a suggest-time tool.** Step 6.2: "`call` offers two slots from the user's calendar (its suggest-time tool when there is one)". There is no rule on working hours, weekends, call length, gaps around other meetings, or the founder's time zone. `shared/connectors.md` only says "two free slots per call offer". I picked 30-minute weekday slots inside the working day, clear of meetings.
7. **No subject rule for promise drafts.** Step 6 sets a subject only for a founder's question ("the subject is "Re: " and the entry's `subject`"). The waiting promise drafts use the promise text as the subject ("Share feedback after the partner meeting", "Share our view on pricing"), which reads like a task to the founder. For a refresh, the text does not say whether to keep the subject.
8. **What "result" closes an applying mark.** `shared/home.md` Write step 2: "A mark with no result after it tells the next run not to repeat that call". No step writes a result to the run row. The finished row keeps `applying` with nothing after it. The result lives in `snap/proposals`, through `--applied`. It worked (the next run sees nothing pending), but the sentence suggests something should be on the row.
9. **One CRM call or one per field.** `skills/pulse/SKILL.md` step 3: "Before each tool call that changes something outside Home ... mark it applying". A `next_step` tap can change four fields. If they go in separate calls, every mark rewrites the same key. I used one call.
10. **`current_due` is never used.** Step 3 checks only "If its next step no longer matches the payload's `current`". The payload also has `current_due`. The text does not say whether a changed due date means "Changed in the CRM since you set it". Here both matched.
11. **Morning brief reads the LP list at every level.** `skills/morning-brief/SKILL.md` step 2 lists "the pass log and the LP list". Meera's LP module is off. I read it as written. It is harmless but wasted. "Open deals" is also loose: I sent every deal the CRM returned, so the engine can see passed ones.

## 6. What went wrong, or looked wrong

- Nothing in the run failed. Every write landed the first time with no version conflict, and no draft was refused.
- Writing this report to `evals/runs/friday-meera/report.md` was blocked: the harness does not let a subagent write report files. The caller needs to save it.
- Halo now reads "13 days in Second meeting" because the stage moved but `stage_entered` did not. It is not flagged stale today, but the figure is wrong (item 1 above).
- The Sable draft from an earlier run contains three reference questions found in no source (item 3 above).
- The engine's reslot context says the times "have passed" when they were later today (item 5 above).
- The brief's headline says "12 things for today, 5 urgent", while `report.json` and the run row say `items: 11`.
- The run row's `read` leaves out `drive`, although I searched Drive for draft sources. The engine builds `read` from the bundle. The next run's Drive window stays at 22 Oct 19:29. Harmless here.
- Mock limits: `gmail search --query` matches subject and snippet only, not names or addresses ("omkar" found nothing). `crm update` does not touch `stage_entered`. The `bundle` shortcut cannot stand in for a 23 Oct read.
- I read `crm deals` once before the CRM write, to check how the CRM spells stages, and again for the bundle. Both are reads, so this is harmless.
- `work/bundle-shortcut.json` and `work/verify-home/` are inspection files, not run outputs.
