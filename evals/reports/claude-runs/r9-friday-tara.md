<!-- Claude-run eval, round nine. Written by a Claude agent running the pulse skill against the mock connectors; saved by the main session (the agent could not write files). -->

# Eval report: friday-tara

Tara Menon, Head of Platform, Quillwater Ventures (fictional). Scheduled "Instinct" run on Fri 23 Oct 2026 at 06:28 IST. Plugin 0.7.2, repo commit 070b9d8. Mock connectors only. Home was seeded before the run and not re-seeded.

Final line of the run: `Send the founder guest list: Fatima (Talentbridge), due today. Draft ready`

## 1. What I ran, in order

Setup and step 0
- Read `evals/eval-mode.md`, `skills/pulse/SKILL.md`, `skills/morning-brief/SKILL.md` and all of `shared/*.md`.
- `mock status`: every connector is connected. Gmail has no `create_draft`, so drafts stay in Home with `in_gmail` false. Note: the mock clock says Thu 22 Oct 07:00, not Friday.
- `mock artifact list`: Home is `https://claude.ai/artifact/mock-instinct-home`.
- Step 0 (guard canary): skipped. No guard is loaded in eval mode.

Step 1, load
- Ran the engine from the repo (`python3 -I -S engine/instinct.py`), as eval mode says, instead of a copy. `check`: ok, engine 0.7.2.
- Read Home with `db list`: `snap` (13 docs), `state` (2 docs) and `runs` (14 rows) into `work/home-db`. All were at version 1.
- Pasted the 15 `snap` and `state` result lines into `work/home-db/versions.txt`.
- Ran `cp home-db/snap/config.json config.json`.
- Run minute: `schedules` gives `CRON_TZ=Asia/Kolkata 28 6-19 * * 1-5`, and Thursday's runs sit at :28. So Friday's first run is 06:28.

Step 2, what is due
- `due --now 2026-10-23T06:28:00+05:30` returned:
  - `run` true, jobs `morning_brief, pulse`, `build_mode` daily.
  - `window_start` 2026-10-22T19:28 for every connector.
  - `run_id` r20261023T0628.
- `db set runs/r20261023T0628` with `started` and `jobs`: version 1.

Step 3, apply what the user approved
- `actions`: one pending tap, `t_3461c2ec2f_team` (type `draft`, ask, `note_kind` team). Nothing refused or to check by hand.
- Read the sources for it (section 2). Wrote `work/drafts.json` and `work/applied.json`.
- No applying mark: no tool outside Home was called.

Step 4, read the window (morning-brief windows)
- Mail, 7 days (`gmail search --after 2026-10-16`): 3 threads. A newsletter (th0427), and two "Community event" threads with Fatima (th0264) and Divya (th0276). Read each in full.
- All mail, searched for Aditi's answer on Orbit: 45 threads, none from Aditi after 13 Oct.
- Calendar, 23 Sep to 6 Nov: 5 events. Two were on Thursday (Tallyfin hiring at 11:00, Founder community at 14:30). Nothing on Friday or Saturday.
- Notes since the window start (`granola list --after 2026-10-22`): none. Only tr08 and tr21 exist.
- CRM: 37 open deals, 90 companies (people span all of them), 100 people, 5 notes, 20 passes. LP watch is off, so there is no `lps` key.
- Drive search: 5 data-room files, none needed.
- No new pitches, founder updates or notes. So there were no `extracted`, `inbound`, `kpis`, `asks` or `packs` files.
- Wrote `work/bundle.json` from these reads. A small script, `work/make_bundle.py`, copies my saved reads into the bundle shape; I did not use the `bundle` shortcut. No `unavailable`.

Step 5, build
- Ran `build --mode daily --run-id r20261023T0628 --started 2026-10-23T06:28:00+05:30 --jobs morning_brief,pulse --applied applied.json --drafts drafts.json`.
- Result: 9 items, 227 words (budget 350), no warnings, push `send` true. `owed.json` has 1 entry.
- Batch: 4 documents (brief, pipeline, proposals, drafts). Skipped as unchanged: prep, people, portfolio, lps, commitments, inbound, review, asks.
- Prep questions: there are no prep cards today or tomorrow, so the `questions` command was not needed.

Morning brief step 6, draft what is owed
- One entry, a `refresh` (section 3). Wrote `work/owed-drafts.json`.
- `drafts --out run --drafts owed-drafts.json`: wrote `dr_k_e9eab86816`, refused none.

Morning brief step 7, check the brief
- The hero states a fact: "You promised: Send the founder guest list. Promised to Fatima Sheikh (Talentbridge), due today", with its notes link.
- Every line has a source link.
- The overdue promise (CFO intro, 2 days late) sits above the two "owes you" lines.
- No lines repeat. 227 of 350 words.
- Level check: the three founder asks rank 6th to 8th of 9, below two "waiting on them" lines. Reported as finding 3, not reordered.

Pulse step 6, write and log
- `db batch --file run/home/batch.json`: pipeline v2, proposals v2, drafts v2, brief v2.
- `db update runs/r20261023T0628 --file run/home/run.json --if-version 1`: version 2.
- Mock log: 34 calls. No send, reply or forward. No Gmail draft call. No CRM or calendar write.

## 2. The pending tap

What the payload said
- id `t_3461c2ec2f_team`, approved Thu 22 Oct 18:40.
- `kind` ask, ask `a_22f89a4288` (Orbit Treasury, no `paths`).
- `note_kind` team, `next_of` `t_3461c2ec2f`.
- `after`: board note to Aditi Rao, at 2026-10-22T10:00. That is the time Tara marked it sent.

Who I wrote to, and why
- Pulse step 3: a tap that follows a sent note writes the note its `note_kind` names. `team` goes to the colleagues: all firm members in `snap/config`, in `to` as a comma list.
- So the note goes to Aditi, Kabir, Meera, Rohan and Vikram Nair, not to Tara herself.
- The ask's cash `warning` did not send it to Aditi again. Her board note was already sent, which is what `next_of` and `after` say.
- None of those five addresses has a waiting draft. The Aditi note in `snap/drafts` is marked sent in `state/items`, so it does not count.

Sources used
- The ask in `snap/asks`.
- Orbit's September update (upd_orbit, 11 Oct): "any intros to senior backend engineers would help us hire the two this quarter".
- CRM person P-101: Vikram Rao, CEO, Orbit Treasury.
- The sent note `dr_t_1d7b287123` and its done mark, which show Aditi was asked on 22 Oct.
- Aditi's yes is not in Tara's mail. The only record of it is the tap itself.

The draft
- id `dr_t_3461c2ec2f_team`, `action_id` `t_3461c2ec2f_team`, `note_kind` team, `in_gmail` false.
- to: `aditi@quillwater.vc, kabir@quillwater.vc, meera@quillwater.vc, rohan@quillwater.vc, vikram@quillwater.vc`.
- to_name: "Aditi, Kabir, Meera, Rohan and Vikram". This is the engine's own style for team notes.
- Subject: "Orbit Treasury: who knows senior backend engineers?"
- First lines: "Hi all, Vikram Rao, CEO of Orbit Treasury, asked in their September update for introductions to senior backend engineers, so they can make two hires this quarter. I checked with Aditi on 22 Oct, and we want to help. Do you know anyone who fits?"
- Context: "You asked Aditi on 22 Oct and tapped Yes, ask the team. Her yes is not in your mail, so check line two before you send".
- Left out on purpose: the runway flag. Meera and Rohan were not on Orbit's update.
- Source link: `https://mail.google.com/mail/u/0/#all/upd_orbit`.
- No Gmail link, because there is no create-draft tool. Home's "Open in Gmail" opens a filled-in message to all five.

`applied.json`
- `{"t_3461c2ec2f_team": {"status": "applied"}}`.
- The build turned it into a `snap/proposals` row with status applied.
- `actions` on the written Home now lists nothing pending, so the tap will not be drafted twice.

## 3. Every entry in `run/owed.json`

There was one entry: `dr_k_e9eab86816`, kind `refresh`, to Rahul Sharma (Tallyfin, rahul@tallyfin.com).

Why it is listed
- The draft (CFO candidates, promise `k_e9eab86816`, 2 days late) was written Thu 06:28.
- Tara met Rahul at 11:00 that day ("Tallyfin: hiring"). The meeting has no notes.

What I wrote, following step 6.5 (no notes: keep the draft, open with one line that names the meeting and claims nothing)
- Subject kept: "Tallyfin: two CFO candidates".
- First lines: "Hi Rahul, Good to see you on Thursday. As promised, two CFO candidates for Tallyfin: George Thomas and Swati Kulkarni. Both are in our network. Tell me who you would like to meet first, and I will introduce you."
- One change besides the opening line: I dropped "this week" from the last sentence. It was written on Thursday and reads badly on a Friday.
- Context: "Written before your 22 Oct Tallyfin meeting, which has no notes: check it still stands, or tap Done if it was settled in the room. Names from your CRM (tagged CFO candidate): check each is open to a move".
- `commitment_id` kept. No slots, no cc, `in_gmail` false.

Sources
- The owed entry.
- Transcript tr08, which holds the promise: "I'll send you intros to two CFO candidates by Wednesday."
- CRM P-180 George Thomas and P-181 Swati Kulkarni, both tagged "CFO candidate".
- Their threads: th0366, th0274, th0272, th0273, th0275.
- Calendar event ev_tallyfin_today.

Gaps
- No bracketed gap.
- Nothing in the sources says whether either person is open to a move, so that stays a check in `context`.

Not listed, and correctly so
- The guest list to Fatima (due today) is already drafted, and Fatima was not at Thursday's meeting.
- All three asks already have notes.
- Triage is off for this level.

## 4. The check: what Home would show

How I checked
- Re-read Home after the writes (`db list` into `work/check/home-db`).
- Rendered the real `home/index.html` in headless Chromium with a mock data runtime, clock at Fri 06:40 (`work/check/render.js`, output `render_0640.json`).
- Expanded every row and searched the full page text (`work/check/fulltext.js`).
- Ran two local rebuilds that were not written to Home:
  - the 07:28 pulse with nothing new (`check/sim`);
  - Tara marking the team note sent at 09:00 (`check/sent`).

Does each founder ask row say where it stands?
- Yes, on Today and on the Portfolio tab:
  - Nimbus Collect: "Asked Aditi for the intro on 22 Oct."
  - Orbit Treasury: "Asked Aditi on 22 Oct."
  - Kestrel Pay: "Asked Aditi on 22 Oct."
- But the Portfolio hero has no status, and it is the first thing Tara sees (her Home opens on Portfolio). It reads: "Nimbus Collect: an introduction to two banks as customers. Divya Raman asked on 13 Oct. 2 more open". See finding 4.

Does the Orbit row show the new team note as ready?
- Yes. The chips are "Asked Aditi" and "Draft ready".
- Open in Gmail fills in all five colleagues, the subject and the body. Copy draft works.
- Weak spots (findings 2 and 3):
  - The text still says "Runway under 9 months: check with Aditi before sourcing".
  - Nothing says the draft is the team note.
  - The chat brief, shareable brief and push do not mention it.
- After a simulated send, the row flips to "Asked the team on 23 Oct" and offers no further tap. Good. But "check with Aditi before sourcing" is still there.

Is the note Tara already sent untouched?
- Yes. `dr_t_1d7b287123` is identical before and after.
- `state/items` and `state/actions` are unchanged.
- No row offers it as waiting. The Nimbus and Kestrel rows show no draft.

Does any ask drop off Today?
- No. All three stay under "Founders need" on Today and on Portfolio.
- The 07:28 rebuild is quiet ("Nothing new") and keeps all four drafts and all three ask states.

Also found during the check
- None of the four drafts' `context` lines appears anywhere on Home. See finding 1.
- Kestrel's row already offers "Yes, ask the team", before any reply from Aditi. The label is the only cue that it means "Aditi said yes".

## 5. Findings, worst first

1. **Draft caveats in `context` never reach the user in Home.**
   - What happened: all three waiting drafts are linked to the hero or a visible row. There, Home offers only "Open draft" or "Open in Gmail", and "Copy draft". The `context` line shows only in the "Ready for you" card, which skips any draft a row already shows. With every row expanded, 0 of 4 context lines were visible.
   - Why it matters: lines the skills require are lost:
     - "Check it still stands, or tap Done if it was settled in the room" (refresh).
     - "Check each is open to a move" (CFO names).
     - "Her yes is not in your mail" (team note).
     - Tara opens Gmail and can send without seeing any of them.
   - Where:
     - `home/index.html`: itemRow and heroCard (the draft buttons), and readyForYou with `shownDrafts`.
     - The skills rely on it: `skills/morning-brief/SKILL.md` steps 6.1 and 6.5, `skills/pulse/SKILL.md` step 3.
   - Change: show the draft's `context` as one muted line under the row's draft buttons and under the hero's Open draft. Or stop putting must-read checks only in `context`.

2. **The Orbit row keeps saying "check with Aditi before sourcing" after her yes.**
   - What happened: the engine rebuilds the cash warning on every build. It never clears it once a `_team` or `_intro` tap follows the board note. The line still shows with the team note ready, and again after the team note is sent. The status chip "Asked Aditi" sits next to "Draft ready", which reads as if the draft goes to Aditi.
   - Where: `engine/instinct/brief.py` candidates(), in the ask block (warning and sent state). `home/index.html` asksCard builds the same text for the Portfolio tab.
   - Change:
     - When an approved `<id>_team` or `<id>_intro` tap exists after a board note, say "Aditi said yes on 22 Oct" and drop "check with Aditi before sourcing".
     - When that next note is ready, label the row "Team note ready".

3. **Tara's own next step ranks below "waiting on them" lines, and only the page knows the note is ready.**
   - What happened: engine ask rows carry no `draft`. They take the "requested" penalty (minus 20) even when Tara's next note is ready. So Orbit ranks 7th of 9, below "Rahul owes you" and "Fatima owes you". The level reminder says Platform puts founder asks first. `brief.md`, the shareable brief and the push cannot say "team note ready".
   - Where: `engine/instinct/brief.py`, the ask block. `engine/instinct/cli.py` builds `drafts_by_action` but uses it only for the prep cards' `note_state`.
   - Change: use `drafts_by_action` for brief ask rows too. Set `draft`, set the state to "ready", drop the penalty, and say "Team note ready" in the detail.

4. **The Portfolio hero, Tara's landing view, ignores where asks stand.**
   - What happened: `opens_on` is portfolio. The hero says "Nimbus Collect ... Divya Raman asked on 13 Oct. 2 more open".
     - It has no "Asked Aditi for the intro on 22 Oct".
     - It does not point at the one thing Tara can do now, the Orbit team note.
     - `snap/portfolio` and `snap/asks` were skipped as unchanged and still show Thursday 19:28.
   - Where: `engine/instinct/cli.py`, the portfolio hero for the asks level and the `snap/asks` hero. Both pick the newest ask by date.
   - Change: build the hero from the ask that needs the user, with its state. A ready note comes first, then the oldest ask with no note out.

5. **What a team note may say about the partner's answer is undefined.**
   - What happened:
     - Pulse step 3 says the team note says "who was asked already and when (`after`)", and "nothing you cannot source".
     - `after` holds who and when the board note was marked sent, not the answer.
     - Aditi's yes is not in Tara's mail.
     - I wrote "I checked with Aditi on 22 Oct, and we want to help", resting on the tap, and flagged it in `context`. Home hides that line (finding 1).
   - Where: `skills/pulse/SKILL.md` step 3, `draft`. The page builds `after` in `home/index.html`.
   - Change:
     - Say plainly that a "Yes, ..." tap is the user's word that the partner agreed, and what the note may say about it.
     - Ask the run to search mail for the partner's reply since `after.at`, and quote it when found.
     - Optionally add `after.answer` to the payload.

6. **No privacy guidance for a whole-team note about a cash-tight company.**
   - What happened: the team note goes to every firm member. Orbit's update, with the runway, went only to Aditi, Kabir, Vikram Nair and Tara. Neither skill says whether the `warning` may go in a team note. I left it out; another run might not.
   - Where: `skills/pulse/SKILL.md` step 3 and `skills/morning-brief/SKILL.md` step 6.3, under `team`.
   - Change: add one line: "A team note names the founder, the company and the ask only. Leave the cash flag out."

7. **Pulse step 3's `draft` rules are one long block with no clear order.**
   - What happened:
     - The warning rule ("the first note goes to the board partner") comes before the follow-up rule ("A tap that follows a note already sent ..."). Orbit carries a warning, so a first-match reading would write to Aditi again.
     - "The same person" is undefined for a comma-list `to`. By the text, a waiting one-to-one draft to Kabir would be rewritten into the team note.
   - Where: `skills/pulse/SKILL.md` step 3, `draft`.
   - Change: write it as an ordered list:
     1. `next_of` set: use its `note_kind`.
     2. Warning: board.
     3. Paths: contact or colleague.
     4. Otherwise: team.
     - Also say that a team note never merges into a one-to-one draft.

8. **Carried drafts age, and nothing re-dates them.**
   - What happened:
     - The Rahul draft said "I will introduce you this week". Step 6.5 says to keep lines "unless something newer changes them", but has no rule for time words. I dropped "this week".
     - Today's hero draft (the guest list to Fatima) has the context "Guests from today's 14:30 dinner planning invite", which now names the wrong day.
     - Its body also says "I will add Rahul from Tallyfin once he confirms". But the promise to invite Rahul is still open and undated.
     - Undated promises never enter `owed.json`, so that invite never gets drafted.
   - Where: `skills/morning-brief/SKILL.md` step 6.5, and the engine's `owed` rules (due within two days or overdue).
   - Change: tell runs to replace "today", "tomorrow" and "this week" with dates in carried drafts. Consider listing an undated email promise when a related draft goes out.

9. **Two Vikrams.**
   - What happened: the team note's `to_name` uses first names ("... Rohan and Vikram"). The founder is also Vikram (Rao), while the colleague is Vikram Nair. I named the founder in full in the body.
   - Where: `engine/instinct/cli.py`, the team entries. I copied the same style.
   - Change: use full names in a team note's `to_name` when a first name matches the founder's.

10. **The repository changed while this run was going.**
    - What happened: tracked files changed after my session started, with no commit:
      - `engine/instinct/cli.py` at 09:46:11 and `home/index.html` at 09:46:47.
      - Also `evals/demo.py`, `evals/replay.py`, `evals/scorecard.md` and `evals/reports/home/*.png`. I did not open these.
      - My `versions.txt` is from 09:45:44, and my build ran at about 09:50.
    - The `cli.py` change is a word-boundary fix for `holder` and does not touch Tara.
    - The page change stops "Draft coming at the next check" from sticking once a tap's draft exists. With the old page, the Orbit row would have kept that chip after the team note was sent.
    - I did not edit any tracked file.
    - Change: run evals on a clean checkout pinned to a commit, and log `git status` with the run.

11. **Smaller items.**
    - The run row's `read` lists only bundle keys. So `due` keeps Drive's window at Thu 19:28, even though Drive was searched. Low impact.
    - The seeded Thursday 19:28 brief showed the asks as plain "asked". A local rebuild at Thu 19:28 shows "Asked Aditi on 22 Oct", so this is a seed artifact, not an engine gap.
    - The mock world stops on Thursday morning (status `now` is Thu 07:00). Thursday's meetings have no notes, and Aditi's yes cannot be in mail. That limits what this eval can test.
    - For a Platform user with the pipeline off, the morning-brief read still pulls all 37 open deals and the pass log. The `shared/connectors.md` row does not depend on the level.

What worked well
- `due` picked the right run and windows. `actions` listed exactly the one tap.
- The id rules were clear: `dr_<action id>`, never the sent note's id. The page found the draft and showed "Draft ready" with a working Open in Gmail.
- The engine caught that Rahul's draft predates Thursday's meeting. Step 6.5's no-notes wording was easy to follow.
- The sent note and `state/*` were untouched.
- The asks stayed on Today with who and when. The next hour stays quiet.
- Nothing was sent, and nothing outside Home was written.

## 6. Score

**7 out of 10.** The run is safe and the ask loop works end to end. But a real Head of Platform would land on a hero that ignores where asks stand, see "check with Aditi" after Aditi said yes, and never see the checks the drafts carry in `context`.
