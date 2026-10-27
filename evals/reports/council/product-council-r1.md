# Product council review: Instinct for VCs

Reviewed 22 Oct 2026, about 22:20 IST, against the build in `/home/claude/instinct-vc`.

- **Council:** senior PM, senior product designer, staff AI engineer, QA lead.
- **What we read:** every file the brief listed, the 11 named screenshots (plus row-open, pipeline-actions and vikram-lps), and the six per-level briefs.
- **What we ran:** the engine in memory to confirm the defects below, and the design lint. We changed no build file.

**Evidence note.** The screenshots (22:06) and per-level briefs (22:07) are older than the last edits to `home/index.html`, `brief.py` and `prep.py` (22:08) and to `cli.py` and `portfolio.py` (22:12).

- The pictures say "Key hire left" and "3 things prepared".
- The engine now says "Key person leaving" and "2 things prepared".
- So the pictures show the build one version back.
- The engine was edited again at 22:24 to 22:26, during this review. At 22:27 we re-ran the pulse wipe, tuning and trimming reproductions and re-checked every cited line. All still hold.

## Scores

| Lens | Score | In one line |
| --- | --- | --- |
| PM | 5/10 | The idea is right, the level profiles are sharp and the catches are real. But the hero and push say "N things prepared", setup takes far more than two taps, and three views go blank or show a false all-clear after the first hourly run. |
| Designer | 7/10 | Faithful to Evergreen, calm, a good phone layout, dark mode parity and undo everywhere. Let down by count-style hero copy, status shown as a glyph with no word, "Breach" used for work items, and tabs that show data a level does not use. |
| Engineer | 4/10 | A clean, fast, deterministic engine with a fragile and costly input path. Claude re-types every source into `bundle.json` every hour, and the documented pulse inputs wipe the LP, portfolio and competing-fund views. |
| QA lead | 4/10 | 34 of 34 checks pass, but each check is a single run against a fund the builder wrote. There are no replay, scale or real platform contract tests, and the three worst bugs sit in those gaps. |

---

## PM: 5/10

### What works

- Seven level profiles, each with weights, item counts, word budgets and an opening tab. A thoughtful ontology.
- Real catches, each with its source:
  - competing-fund signals that quote the founder,
  - overdue promises surfaced before the meeting,
  - "is back" from the pass log,
  - runway and burn drift,
  - LP re-up windows.
- The safety stance fits VCs: drafts and proposals only, quiet deals, approval per action.

### Level by level (from the six briefs)

- **Partner (Aditi).**
  - Caught: the competing term sheets (Atlas, Gravity), the Solace decision and Orbit's runway.
  - But the hero and the 07:00 push read "10:30 · Ishaan Verma, Atlas Settlement: 3 things prepared".
  - The partner meeting is not on the agenda. Today shows external meetings only (`prep.py:41-46`).
  - The Sunday pre-read exists only inside a scheduled-run transcript. Home has no place for it.
- **Principal (Kabir) and Associate (Meera).** The best fit: own pipeline, overdue promises with "You meet them today", competing funds.
  - Gap 1: a deal has one owner. An associate supporting a partner's deal sees nothing in "own" scope.
  - Gap 2: a draft arrives up to an hour after "Draft a note", and the next morning if tapped after 20:00.
- **Analyst (Rohan).** Inbound triage and the pass log work.
  - 14 inbound lines read "Score 93: book a call" with no reason.
  - Scores cluster at 93 and 65, so "book a call" means thesis fit, not quality.
  - Pass notes can only be copied one at a time when the Gmail connector has no create-draft tool.
- **Platform (Tara).** Founder asks are her top workflow, and they never reach her.
  - `portfolio-watch` step 4 saves asks into `snap/portfolio`.
  - Every engine build rewrites `snap/portfolio` without asks.
  - Home never renders asks.
  - Her Pipeline tab says "Every deal has a next step". That is false: her pipeline module is off.
- **Finance and IR (Vikram).** The one thing that matters is "Answer the fee offset question", promised to Helen Park, due 09 Sep, before the 15:30 Northgate meeting.
  - His hero is the 09:00 fund admin call instead.
  - After the first hourly pulse, his LPs tab reads "Every LP is in touch" (Engineer, defect 1).
- **Solo GP.** Inherits all of the above.

### Setup is not "1 to 2 taps plus three answers"

The real path:

1. Accept the plugin card.
2. One sign-in per connector. Gmail and Google Calendar are separate entries in `.mcp.json`; Granola, the CRM, Drive and Slack add one each.
3. A "Tell me when you're done connecting" question.
4. The three answers.
5. Up to 7 scheduled-task creations, each of which may ask for approval.
6. Per setup step 7.3, opening up to 7 task settings to switch on automatic approval.

That is 15 to 30 interactions. Other problems:

- The README says "about 10 minutes". Setup step 0 says "under 15 minutes". Neither holds at real volume (see Engineer, cost).
- The level question offers 7 options. The question tool usually caps options at 4. This is untested.

### What would stop a VC using it daily

1. False all-clears and blank tabs after the first pulse (LPs, portfolio, competing funds).
2. Pushes nearly every hour on a meeting-heavy day (see QA, path 5).
3. Promises that never close. Nothing checks sent mail, so finished items stay Overdue until tapped.
4. The hero and push name a count instead of the decision.
5. No search or filter at 300 deals. A 10x bundle gives the hero "70 deals need a call this week".

---

## Designer: 7/10

### What works

- **Brand fidelity:**
  - Evergreen tokens throughout.
  - Raleway 200 and 700 and Nunito, all within the type floors.
  - True minus, and a dash for null.
  - One primary button per view, and the 3px hero rule.
  - Dark mode parity (`dark-380`).
  - Lint clean: 170 rules, 0 violations.
- **Phone first:**
  - Bottom tabs and 16px gutters.
  - Tables drop columns under 560px.
  - Prep opens as a sheet.
  - 10-second undo toasts and skeleton loaders.
  - A read-only banner, a demo banner, and an empty state with a clear promise (`empty-380`).

### Issues

- **The hero copy is a count: "3 things prepared"** (`today-380`).
  - The system's grammar is figure-led, for example "Atlas at 10:30: Bluepeak term sheet, decide by 05 Nov".
  - "Prep me" appears three times above the fold, and two of them open the same card.
- **Status is not always a word plus a glyph.** These rows show a glyph and no word:
  - Decide on Solace (day 9 of 7),
  - Kestrel burn up 43.3%,
  - Saffire churn up 3.7pp,
  - the Tidewater and Peregrine LP rows.

  See `today-1440`, `portfolio-1440` and `lps-380`. Priority is never written. High shows only as a green diamond.
- **Two vocabularies are mixed.**
  - "Breach" labels an LP due a touch and a key hire leaving.
  - The design system keeps Breach for figures and Urgent, High, Medium and Low for work.
  - A revenue miss shows a red "Breach". A 43% burn jump at the same priority shows a quiet green diamond.
- **People shows mailing lists as relationships.**
  - "VC Weekly", "Orbit Treasury Updates" and "Founder Forum" appear among top relationships (`people-380`).
  - Nisha Grover shows Strength 96 under "Going cold" and 59 in the table. One is lifetime strength, the other is recency-weighted (`network.py` decay vs `top_people`).
- **Tabs ignore modules.**
  - An analyst sees an LPs tab full of re-up windows.
  - Platform and Finance see "Every deal has a next step" on Pipeline.
  - Fix: hide tabs whose module is off, or say "Not part of your setup".
- **The phone LP table hides "Re-up window"**, the column that drives every LP alert (`index.html:826`).
- **Pipeline rows** spend a whole line on a lone "CRM" chip. They show no owner and no round size. There is no "Needs a look" filter and no search.
- **The prep sheet** shows the competing term sheet only as question 1, with no "Watch" line as in the chat card. Overdue promises in the sheet carry no "Overdue" word.
- **Error states are mixed up** (`index.html:442`, `:608`, `:914`).
  - A database error shows "Open Instinct Home in the Claude app".
  - A slow load shows "Your first brief is on its way" to an existing user after 2.5 s.
  - The stale pill turns grey after 3 hours but never says why or how to fix it.
- **Minor:** in Inkwell the toast should be the paper ink overlay. The page keeps a dark overlay.

---

## Engineer: 4/10

### What works

- **Code quality:**
  - The engine uses the standard library only, with clear modules.
  - Commitments must quote the transcript.
  - Every line needs a source.
  - Quiet filter, version pins and size caps.
  - A lint for send tools.
- **Speed:** a 10x bundle (2,840 threads, 315 deals) builds in 0.22 s. The engine is not the bottleneck.

### Verified defects

We reproduced these in memory and wrote no files.

1. **S0. The documented pulse inputs wipe three views.**
   - The `connectors.md` Pulse row reads "CRM: Deals" and lists no LPs.
   - With that bundle, `build_all` (`cli.py:158`, `:172-173`, `:317-326`) writes:
     - `snap/lps` with 0 LPs and the hero "Every LP is in touch",
     - `snap/portfolio` with 0 companies and "No portfolio flags this week".
   - Competing-fund signals also vanish, because deals no longer map to companies.
   - The push becomes "10:30 · Ishaan Verma, Atlassettle: 1 thing prepared".
   - Reproduced: the setup run had 4 LP alerts, 5 portfolio flags and 2 competing signals. The next pulse had 0, 0 and 0.
2. **S0 at scale. Commitments are dropped newest first.**
   - `homedb._fit` keeps the first 80% of dict keys (`homedb.py:74`).
   - `merge` appends new items last, and nothing prunes.
   - Past 240 KiB (about 380 commitments, or 5 to 10 weeks for a busy partner), every new promise is cut.
   - Reproduced: 1,200 commitments in, the 313 oldest kept.
3. **S1. Tuning inverts and compounds.**
   - Some defaults sit below the 0.3 floor (Platform `deal_move` 0.2, analyst `lp` 0.0). They rise to 0.3 after "Not useful", with the note "I now show more deal move items because you rated them: 0 useful, 3 not useful".
   - Tuning counts every rating kept for 60 days, every Sunday. One burst of 3 "Not useful" on signals moves a partner's signal weight from 1.2 to 0.33 over 8 Sundays.
   - The stale-threshold rule never fires. Home rates stale items under the group `deal_move` (`brief.py` KIND_GROUP), but tuning looks for `stale`.
4. **S1. The hero and push are chronological.**
   - `brief.hero` picks any meeting within 240 minutes before any decision (`brief.py:251-253`).
   - `_push_line` repeats it.
   - The prep `finding` ranks "they owe us" above a competing term sheet (`prep.py:127-139`).
5. **S1. The golden fund is hard-coded.** `pipeline.py:77` and `:161` special-case "quillwater". A real firm's own name will count as "another fund".
6. **S1. CRM lost update and repeated side effects.**
   - The pulse applies approved fields blindly, so a colleague's newer stage can be reverted.
   - Applied actions are not idempotent. If a run dies after the tool call but before the Home write, the next pulse makes a second draft or calendar hold.
7. **S2. Every build rewrites `snap/config`** (`cli.py:341`). A settings change made during a pulse is overwritten on the conflict retry, while the scheduled task already carries the new time.
8. **S2. The pulse window start is never read.**
   - Pulse step 1.3 uses the last `runs` row as the window start.
   - `shared/home.md` reads only `snap`, `state` and `ratings`, so the window is always "two hours ago".
   - The Saturday 10:00 pulse misses new pitches and notes from Friday 20:00 to Saturday 08:00.
9. **S2. Null lists crash the engine.** The QA connector tester's logs show crashes on events null and threads null, and when `snap/config` is missing.

### Schedules and cost

- **Runs per user:**
  - 14 each weekday (13 pulses plus the brief),
  - 15 on Monday and Thursday,
  - 3 on Saturday,
  - 4 to 5 on Sunday.

  About 79 to 80 runs a week.
- **Collisions, with no lock:**
  - Sunday week-ahead at 17:42 vs the weekend pulse at 18:00.
  - Monday digest at 07:39 (120 days of metadata) vs the 08:00 pulse.
  - Thursday review at 15:37 vs the 16:00 pulse.
  - Every pulse fires at minute 0 for every user.
- **What each run does.** Each run is a fresh session. It reads 5 to 8 instruction files, copies the engine, lists Home, reads the connectors, then re-types everything into `bundle.json`.
- **Bundle sizes:**
  - The golden partner bundle is 218 KiB of JSON for 142 threads and 45 deals. Threads average 694 bytes and deals 376.
  - At 300 deals and 5,000 emails a month, each pulse re-types every deal and 7 days of founder threads.
  - Estimate: 15K to 60K output tokens per pulse before any reasoning, 13 times a weekday.
  - A real 45-minute transcript is about 40 KB. The golden ones are under 1 KB. So setup's "30 days of full transcripts" means several MB to type.
  - This is the biggest scale risk, and it is untested: eval mode allows a bundle shortcut.
- **Approval mode.**
  - `create_trigger` may return tasks that ask before acting. If so, each pulse likely stops at its first ArtifactData write, and Home freezes after the first brief. Setup mentions this in one line only.
  - Switching on automatic approval fixes that, but it also approves the send-capable tools the connectors expose: Gmail send_message, reply and forward, and Slack send. Those tools sit in a session that reads strangers' pitch emails every hour.
  - The QA security tester found that the regex injection detector misses all 4 realistic payloads and simple evasions. The model's judgement is the only guard.
  - Runs can also write `state/actions`, so an injected run could approve its own CRM change.
- **Unverified platform behaviour:**
  - ArtifactData `list` with `out_dir`, and paging for `ratings`.
  - `set` with `if_version`.
  - Whether "Nothing new" is truly silent.
  - The plugin card from SendUserFile.

  One check came out fine: the page's `db.update()` merge is correct. Nested objects merge, which we checked against the runtime typings.

---

## QA lead: 4/10

### What the suite proves

Engine logic on one fictional fund:

- resolution, stale deals, competing funds, commitments and triage,
- KPI drift, LP alerts and intro paths,
- top-5 items per level, schedules and tuning direction,
- the injection regex cases,
- Home click-through on phone and desktop, and the design lint.

### Why only 4

- The goldens and expected answers are written by the builder, and the code is tuned to them ("quillwater" in the regex). There is one fund and one "now".
- Every check is a single run. The wipe bug needs two runs in a row, and no test runs setup then pulse.
- At 22:12 the scorecard held 1 of 6 Claude-in-the-loop rows (KPIs). Morning brief, prep, post-meeting, triage and memo were absent.
- The screenshots and briefs are older than the final code.
- The Home mock database is shaped to the page. That is fine for `update()`, but nothing tests the real ArtifactData tool.

### Riskiest untested paths, and the missing test

1. **The hourly sequence:** setup, then pulses with the exact Pulse-row inputs, then brief, digest and tuning.
   - Missing: a 5-day replay test with invariants. LP count stable, commitments only grow, no false all-clear hero, pushes per day under a cap.
2. **Real volume:** 300 active and 2,000 old deals, 1,500 commitments, 3,000 threads and 40 KB transcripts, with Claude building the bundle itself.
   - Missing: a scale eval with a time and token budget per run.
3. **Scheduled task approval mode.**
   - Missing: a staging run that creates the tasks without automatic approval, and checks that Home shows a stall banner within 2 hours.
4. **Injection under automatic approval.**
   - Missing: an eval-mode pulse with a recording mock of every send tool, and a pitch that asks to forward, approve or post. Pass only on zero send calls and zero writes to `state/*`.
5. **Push volume.**
   - Missing: a count of pushes for a 6-meeting day.
   - Today's rule ("a prep card for a meeting in the next 150 minutes") pushes 2 to 3 times per meeting.
6. **Tuning over many weeks.**
   - Missing: an 8-Sunday simulation that checks each rating moves a weight once, and never against its sign.
7. **CRM concurrency and partial failure.**
   - Missing two tests: approve, a colleague edits, then the pulse applies; and stop the run right after an apply, then rerun it.
8. **A second fictional fund** with different names, stages and CRM (for example HubSpot owner ids).
   - Missing: catches overfitting and owner-mapping gaps.
9. **The fallback install path.**
   - Scheduled prompts name the `instinct-vc` skill but not the repo.
   - If the plugin card fails and setup runs from the repo, every scheduled run lands in a session without the skill.
   - Missing: a fallback-install test that checks the first scheduled run finds and runs the skill.

---

## Top ten fixes, ranked

1. **S0. Stop the pulse wiping LPs, portfolio and competing-fund signals.**
   - **Where:** `engine/instinct/cli.py` (`build_all`, `_snapshots`) and the Pulse row in `shared/connectors.md`.
   - **What:**
     - Carry stored LPs, companies and signals forward when the bundle lacks them, as KPIs and people already are.
     - Never write an all-clear hero from missing input.
   - **Why it matters to a VC:** Finance, partners and solo GPs see "Every LP is in touch" and lose "another fund is moving" within an hour of the brief.
   - **Effort:** M.
2. **S0. Make scheduled runs actually run, and run safely.**
   - **Where:** `skills/setup` step 7, `schedules.json`, `engine/instinct/schedules.py` and `home/index.html`.
   - **What:**
     - One "Instinct" task that picks its mode by local time (brief, pulse, review, digest, tuning). That means one approval and one auto toggle.
     - Read `permission_mode` from the result and guide the toggle.
     - A Home banner when no run has finished in 2 hours.
     - Turn off send, reply, forward and Slack-send tools for these runs.
     - Runs never write to `state/*`.
   - **Why it matters to a VC:** today Home can freeze after the first brief, or run on automatic approval with send tools next to strangers' email.
   - **Effort:** M.
3. **S0 at scale. Keep promises true.**
   - **Where:** `engine/instinct/homedb.py` (`_fit`), `commitments.py` (`merge`, `due_view`) and `skills/pulse` step 4.
   - **What:**
     - Prune done and stale items, and trim oldest first or split by month.
     - Close "You owe" items when sent mail shows them done, with a one-tap confirm.
   - **Why it matters to a VC:** promise tracking is the trust feature. Today it drops new promises after 5 to 10 weeks and nags about finished ones.
   - **Effort:** M.
4. **S1. Lead with the one thing.**
   - **Where:** `engine/instinct/brief.py` (`hero`), `cli.py` (`_push_line`) and `prep.py` (`finding`).
   - **What:**
     - Pick the hero by score, with the next meeting as context.
     - Hero and push state the fact: "Atlas at 10:30: Bluepeak term sheet, decide by 05 Nov".
     - Order the prep finding: competing deadline, promise you owe, their overdue promise, pass note.
   - **Why it matters to a VC:** every level's 07:00 push today is "N things prepared". Vikram's hero misses a 43-day-overdue LP answer due before his LP meeting.
   - **Effort:** S.
5. **S1 (likely S0 for heavy users). Make the hourly pulse cheap and incremental.**
   - **Where:** `skills/pulse` steps 1 to 3, the windows in `shared/connectors.md`, a new engine `ingest` command, and `skills/setup` step 3.
   - **What:**
     - A "nothing new" gate that ends the run in one line.
     - Read only CRM changes since the last run.
     - Reuse stored deals and threads.
     - Adapters that take raw connector output.
     - Cap setup reads (about 150 threads and 10 full transcripts) to keep the 10-minute promise.
   - **Why it matters to a VC:** about 80 runs a week per user, each re-typing every deal. At 300 deals and 5,000 emails a month that is slow, costly and error-prone.
   - **Effort:** L.
6. **S1. Push once, push less.**
   - **Where:** `skills/pulse` step 7, plus the ids already pushed in the engine report.
   - **What:**
     - Push only new items.
     - One prep push per meeting, about 60 minutes before.
     - A daily cap of about 4.
     - Check that "Nothing new" is silent.
   - **Why it matters to a VC:** a partner with 6 meetings is pushed nearly every hour and will mute Instinct.
   - **Effort:** S.
7. **S1. Apply CRM changes and drafts safely.**
   - **Where:** `skills/pulse` step 2 and `cli.py` (`pending_actions`).
   - **What:**
     - Re-read the record, and apply only if the field still equals the proposal's "current" value.
     - Mark "applying" before the tool call, so a retry never makes a second draft or hold.
   - **Why it matters to a VC:** firm CRMs are shared. Reverting a partner's stage change breaks trust.
   - **Effort:** S.
8. **S1. Fix weekly tuning.**
   - **Where:** `engine/instinct/tuning.py`, `skills/tuning` step 1 and `brief.py` (KIND_GROUP).
   - **What:**
     - Count only ratings since the last tuning.
     - Never move a weight against the rating's sign: start sub-floor defaults at the floor, or exempt them.
     - Rate stale items as `stale`.
   - **Why it matters to a VC:** three "Not useful" taps can bury competing-fund alerts over 8 weeks, while the note claims the opposite.
   - **Effort:** S.
9. **S1. Make Home fit each level and tell the truth.**
   - **Where:** `home/index.html` (tabs, `statusFor`, `glyphFor`, `viewPortfolio`, `viewLps`) and the engine snapshots.
   - **What:**
     - Hide tabs whose module is off.
     - Give every row a word plus a glyph. Use Urgent, High, Medium and Low for work, and Breach for figures.
     - Render founder asks, the Thursday review and the Sunday pre-read.
     - Show the re-up window on phones.
   - **Why it matters to a VC:** Platform's top workflow is invisible, an analyst sees LP data, and burn spikes look harmless.
   - **Effort:** M.
10. **S1. Generalize beyond Quillwater, and test it.**
    - **Where:** `engine/instinct/pipeline.py:77` and `:161`, `resolve.py`, `network.py` and `evals/runner.py`.
    - **What:**
      - Take the firm name from config.
      - Drop newsletters and no-reply senders from People.
      - Use one strength number.
      - Add a second fictional fund, the 5-day replay test and the scale test.
      - Regenerate the screenshots and briefs on the final code.
    - **Why it matters to a VC:** today a real firm's own name reads as a competitor, and "VC Weekly" ranks among top relationships.
    - **Effort:** M.

## Also worth doing

- **Net burn, not gross (S1, S).** `portfolio-watch` step 2 should say net burn and keep the founder's stated runway. A gross-burn read creates a false Urgent runway flag before a board meeting.
- **Faster drafts (M).** Draft at tap time with the page's ask-Claude capability, or pre-draft every "You owe" item in the pulse, so "Draft a note" is not an hour away.
- **Deal teams (M).** An owner plus supporting members, so associates see the deals they work on.
- **Reasons on inbound lines (S).** For example "Seed, $2M, B2B payments, Bangalore".
- **Internal meetings on the agenda (S).** The partner meeting and IC, with the pre-read.
- **A run lock (S).** Skip the run if a `runs` row started in the last 50 minutes and has not finished.
- **Pulse window start (S).** Read `runs`, or store `last_run_at`.
- **Null-safe bundle loading (S).**

## How we checked

- **Pulse wipe:** ran `engine.cli.build_all` in memory on the golden partner bundle. First a setup run, then a pulse bundle built per the Pulse row (CRM deals only, no LPs).
- **Tuning:** ran `tuning.tune` on made-up ratings over 8 Sundays.
- **Trimming:** ran `homedb._fit` on 1,200 commitments and on 600 deals.
- **Speed:** timed a 10x bundle.
- **Design lint:** ran `evals/design_lint.py`, which only reads: 0 violations.
- **Runtime merge:** read the db runtime typings for `update()`. Nested objects merge, so the page's state writes are safe.
- **No writes:** `PYTHONDONTWRITEBYTECODE` was set, and no build file changed.
