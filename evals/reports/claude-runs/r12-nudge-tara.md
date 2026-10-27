<!-- Claude-run eval, round twelve. Written by a Claude agent running the pulse skill against the mock connectors on a clean clone at 947db4c (0.7.5), writing bundle.json by hand in one Write call; saved by the main session (the agent could not write files). -->

# Eval report: nudge-tara (round 12)

I couldn't save this to `DIR/evals/runs/nudge-tara/report.md`: the harness refused the Write ("Subagents should return findings as text, not write report files"). So this text is the report, as the brief allows. Everything else is in `evals/runs/nudge-tara/`.

I score 0.7.5 at **8.5 out of 10 as Tara**, up from 8.
- **What got better:** round eleven's two medium problems are fixed. Home no longer goes stale after Sent it, and the push opens Home on the row it names. The rest of the morning held up well.
- **Two medium problems remain:**
  - **The hero's draft names a day that does not hold, and nothing will catch it.** It says "I will introduce you Thu 29 Oct" on Thu 29 Oct, before Rahul can answer. The rewrite dropped "by", so the engine's stale-date check misses it from Friday on.
  - **Done on the hero quietly drops the dinner invite.** The invite rides in the same draft. After Done, its row says "Marked sent 29 Oct" though nothing went, and no run drafts it again.

**Run details:**
- **Plugin version:** 0.7.5 (plugin.json, the pulse and morning-brief SKILL.md metadata, engine `check`).
- **Commit:** `947db4c Round twelve: a note to the partner the work waits on, replies that answer, times true at every hour, Friday sees Monday; version 0.7.5`.
- **`git status --short`:** empty before the run and empty after. No tracked file was edited.
  - Only ignored paths were written: `evals/runs/`.
  - Python also made ignored `__pycache__` folders in `engine/instinct/` and `evals/`, because I ran the engine and the QA harness from the clone.
- **Member:** Tara Menon (`tara`), Head of Platform, level `platform`. Her config opens Home on Portfolio. Brief time 07:00, run minute :28.
- **Run:** the scheduled "Instinct" weekday run on Thu 29 Oct 2026 at 06:28 Asia/Kolkata (run id `r20261029T0628`), then the 07:28 pulse (`r20261029T0728`).
- **Skill:** `skills/pulse/SKILL.md` with jobs `morning_brief` and `pulse`, plus `skills/morning-brief/SKILL.md` steps 5 to 8 and `references/owed-kinds.md`.
- **Home link:** `https://claude.ai/artifact/mock-instinct-home`, from `artifact list`. `schedule list` shows only names and crons, not the prompt.

**Eval-mode adjustments:**
- I skipped pulse step 0, because no guard loads in eval mode.
- I ran the engine from the clone, isolated (`python3 -I -S <DIR>/engine/instinct.py`), instead of copying it. The work folders were `evals/runs/nudge-tara/` (06:28) and `evals/runs/nudge-tara/w0728/` (07:28).
- I passed `--now 2026-10-29T06:28:00+05:30` to `due`, and 07:28 for the next run. `actions` got each run's start time.
- Every Home read and write used the mock `db` commands. `db list` stood in for the ordered runs query.
- Every connector read went through `mock_connectors.py --as tara` with `INSTINCT_RUN=nudge-tara`. I called no real app tool and opened no answer file.
- I wrote both `bundle.json` files by hand, each in one Write call, from my own window reads.
- I used short python one-liners to print compact CRM rows and to compare the CRM with Home's pipeline. A scheduled run's guard would refuse these, so a real run must do both by eye (finding 5).
- Between the runs I played the page and the world:
  - I wrote Tara's four taps to `state/items` and `state/actions` with `db update`, exactly as the QA harness recorded the page's writes.
  - I added Aditi's 07:05 reply with `world add`.
- I read the round-eleven report only after the 06:28 run, so it could not steer the run.
- No AskUserQuestion or connector-card moment came up.

## 1. What I ran, in order

**The 06:28 run:**
1. **Setup.** Cloned, checked out `947db4c`, tree clean. `seed_eval.py nudge tara` gave 14 snapshots, 76 runs (last 60 kept) and 3 drafts.
2. **Reading.** `eval-mode.md` first. Then the pulse and morning-brief skills, `owed-kinds.md`, and `shared/engine.md`, `home.md`, `connectors.md`, `safety.md` and `delivery.md`.
3. **`status`.** All connectors connected, mock clock 29 Oct 06:28. Gmail has `update_draft` but no create-draft tool, so drafts stay in Home (`in_gmail` false).
4. **Finding Home.** `schedule list` gave the two tasks. `artifact list` gave the Home link.
5. **`engine check`.** Ok, engine 0.7.5.
6. **Reading Home.** 14 snap documents (all version 1), 2 state documents and 60 runs. I wrote `versions.txt` from the 16 result lines and copied `config.json`. Home held:
   - the 22 Oct note to Aditi (`dr_t_1d7b287123`, three asks), marked sent on 22 Oct at 10:00;
   - Nimbus, already reading "Intro made on 26 Oct: tap Close ask";
   - an empty `state/actions`;
   - two waiting promise drafts: one to Rahul (the CFO names plus the dinner line) and one to Fatima (the guest list).
7. **`due`.** Run true, jobs `morning_brief, pulse`, mode daily, window 28 Oct 19:28 (Drive and LPs 28 Oct 06:28), run id `r20261029T0628`.
8. **Run row** created (version 1).
9. **`actions`.** Nothing pending, refused or to check by hand.
10. **Morning-brief reads:**
    - Mail, 7 days: 2 threads, both read in full. One is Tara's sent 22 Oct note, with no reply in it. The other is Aditi's 26 Oct Nimbus intro.
    - Calendar, 29 Sep to 12 Nov: 4 events, all past (15, 16 and 22 Oct). Nothing today or Friday.
    - Notes since 28 Oct: none.
    - CRM: deals (45: 37 open, 6 passed, 2 portfolio), companies (90), people (100) and passes (20). I read no CRM notes, because the Morning brief row does not list them.
    - No LPs, since LP watch is off.
11. **CRM against Home.** The same 37 open deals, with no change in stage, next step, its date or last contact. None closed.
12. **`bundle.json` by hand,** 50 KB:
    - 2 threads; the 602-character note was cut to 596 by dropping the sign-off;
    - 4 events and `transcripts: []`;
    - 37 open deals, 49 companies (12 portfolio, 37 pipeline) and 53 people at them;
    - `people_partial` and `companies_partial` true, 20 passes, and no `lps` or notes.
13. **Nothing new to process.** No new notes, pitches or founder updates, so no `extracted`, `inbound`, `kpis`, `asks`, `packs` or `applied` files.
14. **Build (daily).** 8 items, 183 of 350 words, no warnings.
    - The hero was "Intro two CFO candidates", 8 days late.
    - Push: "Nudge Aditi on Kestrel Pay and Orbit Treasury: no reply since 22 Oct".
    - `owed.json` had 1 entry.
15. **No prep cards,** since there are no meetings today or Friday, so no `questions`.
16. **Drafting** (morning-brief step 6, owed-kinds `ask_nudge`).
    - I ran five more searches for a reply from Aditi: `from:aditi@quillwater.vc`, "aditi", Kestrel, Orbit and "Founder asks". None found.
    - I wrote the nudge into `owed-drafts.json`. With no Gmail create tool, there was no drafting mark.
17. **`drafts`.** Wrote `dr_t_1d7b287123_nudge` and refused nothing.
    - The push line became "...no reply since 22 Oct. Note ready".
    - The Today row, both heroes and Copy brief switched to "Nudge ready".
18. **Brief check (step 7).**
    - The hero states a fact, and every line has a link.
    - Tara's late promises sit above what she waits on.
    - Nothing repeats, and the words are within the budget.
19. **`db batch`.** Pipeline, people, directory, drafts, brief, asks and portfolio, all to version 2. I finished the run row from `run/home/run.json` (version 2).
20. **Final line:** `Nudge Aditi on Kestrel Pay and Orbit Treasury: no reply since 22 Oct. Note ready` (80 characters).

That run made 25 mock calls; with everything after, 43 in all. None sent mail, saved a Gmail draft, made a calendar hold, wrote to the CRM or made a schedule.

**Bundle comparison, done separately.** I ran `bundle --out bundle-mock.json --now 2026-10-29T06:28:00+05:30 --mode daily --after 2026-10-28T19:28:00+05:30`, then built from it against the same pre-run Home.
- **The same ids everywhere:**
  - 2 threads, 4 events, 0 transcripts and 20 passes;
  - 37 deals, 49 companies and 53 people;
  - both partial flags, and no LPs, KPIs or empathy maps.
- **Different:** the shortcut adds 13 CRM notes, firm and thesis, snippets and a message `to`. It cuts the note at exactly 600 characters, mid-word ("...Ta").
- **Effect:** none that matters.
  - Both builds gave the same `brief.md`, `owed.json` and push (before `drafts`).
  - They also gave the same pipeline, people, directory and commitments.
  - Asks and portfolio differ only by my `drafts` step.
  - Both rewrote `snap/directory` with the same 100 people in another order: one extra write each morning, as in round eleven.

## 2. The pending taps

- **06:28: none.** The 22 Oct note was a morning-brief draft that Tara marked sent in `state/items`, not a tap.
- **07:28: one,** `t_3461c2ec2f_team`: "Aditi said yes: ask the team" on Orbit Treasury, tapped at 07:10.
  - Draft rule 1 applies: a follow-on to a sent note, `note_kind` team, `after.kind` board, `after.at` 06:45 (the nudge's sent time), `nudged` true.
  - I searched mail since `after.at` and found Aditi's 07:05 reply in the note's thread, so the note quotes her.
  - The draft stays in Home, so it needed no applying mark.
  - `applied.json` was `{"t_3461c2ec2f_team": {"status": "applied"}}`. `snap/proposals` shows it applied at 07:28.

## 3. The owed entries and their drafts

**06:28: one entry, `dr_t_1d7b287123_nudge`.**
- kind `ask_nudge`, `note_kind` nudge, `nudge_of` board;
- `note_draft` `dr_t_1d7b287123`, `sent_on` 2026-10-22;
- `re` "Founder asks: Kestrel Pay, Orbit Treasury, Nimbus Collect";
- `action_ids` `t_1d7b287123_nudge` and `t_3461c2ec2f_nudge`;
- items Kestrel Pay (Neel Bhatt), then Orbit Treasury (Vikram Rao), in the note's order.

Nimbus was left out, since the intro was made on 26 Oct. There was no `answered` field (finding 7). The engine's context: "No reply since you wrote on 22 Oct: one short nudge on Kestrel Pay and Orbit Treasury. Send it as a reply to your 22 Oct note, so the asks stay in view".

**The reply search (owed-kinds step 1).**
- The note's thread held only Tara's message.
- Aditi's only mail since was the 26 Oct intro. It answers the Nimbus ask, not one in `items`.
- So I wrote the nudge, and thanked her for Nimbus in the first line, as owed-kinds says for an ask already answered.

**The nudge.** It stays in Home (`in_gmail` false). To aditi@quillwater.vc, subject "Re: Founder asks: Kestrel Pay, Orbit Treasury, Nimbus Collect":

```
Hi Aditi,

Thanks for introducing Divya to Raj at Fable Bank on 26 Oct.

Following up on my note of 22 Oct. Two founder asks still need your view:

1. Kestrel Pay: Neel Bhatt asked for introductions to senior engineers, two hires this quarter. Burn is up 43.3% in a month. Should we help them hire now?
2. Orbit Treasury: Vikram Rao asked for introductions to senior engineers, two hires this quarter. Runway is under 9 months. Should we help them hire now?

A quick yes or no on each is plenty.

Tara
```

- **Context:** "No answer from Aditi on Kestrel Pay or Orbit Treasury since your note of 22 Oct (she made the Nimbus Collect intro on 26 Oct). Send this as a reply to your 22 Oct note, so the asks stay in view".
- **Source:** "Your 22 Oct note" (the sent thread), so its link opens the thread to reply in.
- **Every line is sourced:** the 26 Oct intro thread, the 22 Oct note (both asks and both flags, as it named them), and `snap/asks`.

**07:28: the tap's draft, `dr_t_3461c2ec2f_team`.**
- **To:** aditi, kabir, meera, rohan and vikram @quillwater.vc.
- **`to_name`:** "Aditi, Kabir, Meera, Rohan and Vikram Nair". Vikram Nair is named in full, because the founder is Vikram Rao.
- **Subject:** "Orbit Treasury: intros to senior backend engineers".

```
Hi all,

Vikram Rao at Orbit Treasury asked us for introductions to senior backend engineers, for the two hires they want to make this quarter. I asked Aditi on 22 Oct, and on 29 Oct she replied: "Yes on Orbit: please ask the team." Do you know someone who fits? Reply to me and I will set up the introduction.

Tara
```

- **Context:** "Aditi's yes is in her reply of 29 Oct at 07:05, in your 22 Oct thread, and the note quotes it. Orbit's runway is left out, since this goes to the whole firm".
- **Source:** Orbit's 11 Oct founder update ("any intros to senior backend engineers would help us hire the two this quarter").

**Two drafts were already waiting and were not listed** (both from earlier runs):
- `dr_k_e9eab86816` to Rahul, the hero's draft. It carries both promises to him (finding 1):

```
Hi Rahul,

Good to see you on Thu 22 Oct. As promised, two CFO candidates for Tallyfin: George Thomas and Swati Kulkarni. Both are in our network. Tell me who you would like to meet first, and I will introduce you Thu 29 Oct.

Could you also send the CTO job description when you have it?

I would also love you to join the founders dinner: I will send the details.

Tara
```

- `dr_k_45c5b75374` to Fatima, the guest list. It is fine: it now asks for the venue shortlist once.

## 4. Next-run check

I used the harness's `QA` class at `PHONE` (380 px). It loaded the documents from `evals/runs/nudge-tara/db/` (`{"data", "version"}`), with state as `{"items", "actions"}` maps and runs newest first. Screenshots and logs are in `evals/runs/nudge-tara/qa/`.

**At 06:40 Tara taps the push.**
- **Opening view.** Home opens on Today, not her Portfolio default. The live pill reads 06:28.
  - The nudge row, which the push named, is already open and in view.
  - The page scrolled 344 px, and the row sits at 370 to 772 px of 844.
- **Hero.** "You promised · 8 days late: Intro two CFO candidates", with Open draft, Sent it and Done.
  - Its note: "It said "by Tue 27 Oct", which has passed: the next working day is in its place, as Instinct's suggestion. The new date is Instinct's suggestion: change it if you like".
  - The draft says "introduce you Thu 29 Oct", which is today.
- **Next up, in order:**
  - the guest list for Fatima (Overdue, Draft ready);
  - "2 founder asks wait on Aditi ... 5 working days. Nudge ready", with Nudge ready, Founder updates and Your note;
  - the Tallyfin key person;
  - Rahul owes the CTO job description.
- **Below that:** Fatima owes the venues, "Invite Rahul to the founders dinner" (No date, Draft ready), and Nimbus.
- **The nudge row, opened:** Before you send, Open in Gmail, Sent it, Copy draft, See each ask and Snooze.
  - Open in Gmail is a new message to Aditi with the "Re:" subject, the full body and Tara's authuser.
  - "Your note" opens the 22 Oct thread.
- **Portfolio.**
  - The hero reads "Founder asks · one note: 2 founder asks wait on Aditi ... Nudge ready. 1 more open", with Open draft, Sent it and Copy.
  - The Kestrel and Orbit rows read "Nudge to Aditi ready, no reply since 22 Oct".
  - Each offers Close ask, Open in Gmail, Sent it, Copy draft and "Aditi said yes: ask the team".
- **Phone checks pass on every screen:** no sideways scroll, one primary button, every control named, no text under 11.5 px, no script errors.

**The taps,** each in its own page at its own time, with state carried forward:
- **06:45: Sent it on the Today nudge row.**
  - It writes only `dr_t_1d7b287123_nudge`, and the toast says "Marked sent".
  - The row at once reads "Nudged Aditi on 29 Oct: no answer yet on Kestrel Pay and Orbit Treasury."
  - The Portfolio hero steps aside to Nimbus ("2 more open"). Kestrel and Orbit read "Nudged Aditi on 29 Oct".
- **06:46: Close ask on Nimbus** (Portfolio).
  - It writes only `t_742d2f63d5`, and the toast says "Ask closed".
  - The hero moves to Orbit with "1 more open", which is right.
  - My first try wrote nothing: my locator hit the row's expander, whose text holds "tap Close ask" (finding 9).
- **06:50: Sent it on the hero.**
  - It writes the draft, both promises (the CFO intro and the dinner invite) and the row.
  - Fatima's guest list steps up as the hero, and the invite row leaves too.
- **07:05 (the world):** Aditi replies in the note's thread: "Thanks Tara. Yes on Orbit: please ask the team, Vikram needs those two engineers. Let us hold on Kestrel until we see their October burn."
- **07:10: "Aditi said yes: ask the team" on Orbit.**
  - It writes `t_3461c2ec2f_team`: draft, team, `next_of`, `after` board at 06:45, nudged.
  - The toast says "Instinct drafts it at the next check. Nothing is sent."
  - Orbit reads "Team note coming at the next check", and Kestrel keeps "Nudged Aditi".
  - Today's grouped row becomes the Kestrel row.
- **Tried separately, not carried forward:**
  - **Done on the hero (06:50).** It writes the row, the CFO promise and the shared draft, but not the invite. The invite row then reads "Marked sent 29 Oct" (finding 2).
  - **Sent it on Fatima's row (06:55).** It writes her draft, the promise and the row, and the row leaves.
  - **See each ask.** It opens Portfolio.
- **The harness's own round 11 and 12 scenarios:** 68 of 68 checks pass.

**The 07:28 pulse:**
- **`due` and `actions`.** Jobs `pulse`, window 06:28, run `r20261029T0728`. One pending tap: the Orbit team note.
- **Reads.**
  - Mail since 06:28 shows the 06:45 nudge in the note's thread, with Aditi's 07:05 reply after it.
  - The 06:50 note to Rahul is in its own sent thread. So the mock now puts a Sent it in sent mail.
  - No events today or Friday, no notes, and no CRM changes against Home.
- **Bundle by hand:**
  - 2 threads: the note's thread (the nudge and Aditi's reply) and the note to Rahul;
  - `events: []` and `transcripts: []`;
  - `crm.partial` true with no deals.
- **Build** with `--applied` and `--drafts`: 6 items, 155 words, no warnings.
  - `owed.json` was empty, so there was nothing to narrow. The push was "Nothing new".
  - The batch wrote brief, pipeline, people, portfolio, commitments, proposals, drafts and asks.
  - I finished the run row. Final line: `Nothing new`.
- **What the engine made of the reply.**
  - Both asks carry `replied` (Aditi, 29 Oct 07:05, after the nudge).
  - Orbit reads "Team note ready ... Aditi said yes on 29 Oct".
  - Kestrel reads "Aditi replied on 29 Oct: read it, then answer here", and gets no second nudge.
  - Nimbus and both of Rahul's promises are done.

**Nothing was lost.** At 07:35 on the phone:
- The hero is "You promised · 6 days late: Send the founder guest list".
- Orbit reads "Team note ready".
  - Open in Gmail has all five colleagues in To, with the subject and body.
  - It also offers Sent it, Copy draft and Close ask.
  - It is the Portfolio hero too, with "1 more open".
- Kestrel offers Close ask, "Aditi said yes: ask the team" and Snooze. On Today it has no link to the reply; on Portfolio it has "The reply" (finding 3).
- The Tallyfin flag, Rahul's CTO job description and Fatima's venues are all still there. The phone checks pass.

## 5. Findings, worst first

1. **The hero's draft names a day that does not hold, and the engine will never catch it (medium; engine, skill text and eval harness).**
   - The hero's draft to Rahul says "I will introduce you Thu 29 Oct". It is Thu 29 Oct, and the intro needs Rahul's pick first.
   - The 28 Oct rewrite followed owed-kinds: a passed date that Instinct suggested "gets the next working day". Read on Wed 28 Oct, that is Thu 29 Oct: the very morning she reads it.
   - The hero's note says "the next working day is in its place", but the draft names today.
   - The note also says "Instinct's suggestion" twice. That comes from the stand-in drafter in `evals/demo.py` (`context_extra`, about line 528).
   - The rewrite dropped "by". The engine's `PROMISED_DATE` (`engine/instinct/cli.py`, about line 2471) needs one of these lead words before the date: by, before, until, till, no later than, on or before.
   - I ran `_stale_words` on this body for 29 Oct, 30 Oct and 2 Nov. It finds nothing, as written or with "on". Only "by Thu 29 Oct" is caught.
   - So from Fri 30 Oct the hero's draft promises a past date again (round eleven's case), and no run rewrites it.
   - **Fix:**
     - Engine: flag any named date in a waiting draft once it is before today, with or without a lead word ("Thu 29 Oct", "on 29 Oct").
     - Engine: also flag it on its own day when the draft first asks the reader for something ("Tell me who ... and I will ...").
     - owed-kinds.md, `redate`: when Instinct picks the new date, choose two working days out, or drop the date ("as soon as you tell me"). Keep "by" in the new phrase.
     - `evals/demo.py` `_redate`: keep the lead word, and say "Instinct's suggestion" once.

2. **Done on the hero quietly drops the dinner invite (medium; Home and engine).**
   - Rahul's draft carries two promises (`commitment_ids`): the CFO names and the dinner invite. Sent it closes both, which is right.
   - Done closes only the CFO promise but marks the shared draft done.
   - The invite row then reads "Marked sent 29 Oct", though nothing was sent. Home cannot tell Done from Sent it (`sentNow` in `home/index.html`, about line 863).
   - The engine never drafts the invite again:
     - in `_owed`, `have_c` (`engine/instinct/cli.py`, about line 1902) counts every draft's promises, closed drafts included;
     - an undated promise only rides in a waiting draft (about line 2333).
   - So a promise to a founder vanishes under a false label, and Done sits one tap from Sent it.
   - **Fix:**
     - Home: on Done, mark the draft done only when every promise it carries is done.
     - Home: record how it closed (`closed_by: "done"` or `"sent"`), and never show "Marked sent" for a Done.
     - Engine: count only open drafts in `have_c`, so the invite rides in the next email to Rahul, or comes back as a line of its own.
     - Add the case to Home QA.

3. **After a reply, Today says "read it" with nothing to read (low; engine and Home).**
   - Kestrel's Today row says "Aditi replied on 29 Oct: read it, then answer here". Its only link is the founder update.
   - The same ask on Portfolio has "The reply".
   - The brief's ask rows carry no `reply_url`. Home works it out only in the Portfolio card (`home/index.html`, about line 1630).
   - **Fix:** put `reply_url` (from `snap/asks` `replied.url`) on the brief's ask rows, or have Today's rows use the Portfolio card's lookup.

4. **A promise Instinct wrote into an email is not tracked once it is sent (low; engine).**
   - Tara's sent note says "Tell me who you would like to meet first, and I will introduce you Thu 29 Oct." Instinct wrote that line.
   - Sent it closed the CFO promise, and nothing now follows the intro that comes after Rahul answers.
   - **Fix:** when a sent draft carries a new promise that Instinct wrote, keep it as a commitment (owed to the reader, due on the date it names). Or keep the old promise open, "waiting on Rahul's pick".

5. **The morning bundle is heavy to write by hand (low; skill text and engine).**
   - The Morning brief row asks for every open-deal company and the people there.
   - That made a 50 KB bundle: 49 companies with sectors and descriptions, 53 people and 37 deals.
   - Home's directory already holds the same companies and people.
   - A real scheduled run must copy all of it in one Write and compare deals with Home by eye, with no script.
   - **Fix:** with the partial flags, send only the rows that changed since the directory's `as_of`, or ids and status for the rest. Or let the engine fill them from the directory when the CRM read matches.

6. **A partial "hold" reply has no tap that fits (low; Home).**
   - Aditi said to hold on Kestrel until its October numbers.
   - Kestrel offers Close ask, "Aditi said yes: ask the team", and Snooze for 1 hour, Tomorrow or Next week.
   - Tara must snooze it a week at a time, or close an ask that is still alive.
   - **Fix:** once an ask has a reply, offer "Wait for the next update" (until the company's next founder update, or 30 days).

7. **The nudge entry does not say Aditi already answered Nimbus (low; engine).**
   - The engine left Nimbus out (intro made on 26 Oct) but set no `answered`.
   - So the thanks line rests on Claude's judgment: I wrote one, and another run may not.
   - **Fix:** when an ask on the note was made or answered after `sent_on`, set `answered`. For example: `{"companies": ["Nimbus Collect"], "on": "2026-10-26", "kind": "made"}`. Then the nudge opens with thanks every time.

8. **Small words on the nudge and ask rows, and in the copied brief (low; engine and Home).**
   - The nudge row's detail ends "Nudge ready", and the status chip says "Nudge ready" again.
   - Its source chip says "Founder updates" but opens only Orbit's update.
   - Today's row has "Your note", but the Portfolio rows for the same nudge do not.
   - After the yes tap, the Orbit row says both "Team note coming at the next check" and "Draft coming at the next check".
   - Copy brief keeps app words ("tap Close ask", "Nudge ready").
   - Open in Gmail is still a new message, not a reply in the thread.
   - **Fix:**
     - Drop the state from the detail when the chip shows it, and say "coming" once.
     - Label the source "Founder update (Orbit)", or link both updates.
     - Show "Your note" on the Portfolio rows too.
     - Strip tap words from the shareable text.

9. **A row's own text holds "tap Close ask" (low; Home).**
   - Nimbus's detail says "Intro made on 26 Oct: tap Close ask". That text sits inside the row's expander button.
   - A tap aimed at "Close ask" by its text hits the expander and folds the row. My script did this, as round eleven's did.
   - A screen reader reads the instruction as part of the row's name.
   - **Fix:** say only "Intro made on 26 Oct" in the row and leave the action to the button, or give the expander an `aria-label` of its title.

10. **The mock Gmail search misses a sender (low; eval harness).**
    - `from:aditi@quillwater.vc` returned nothing. "aditi" did not return the 26 Oct intro, which she sent.
    - A run that searches for a reply as owed-kinds asks could miss one. Here the 7-day listing caught it.
    - **Fix:** in `mock_connectors.py`, support `from:` and `to:`, and match a query against participants.

11. **The bundle shortcut still reads a little more than the Morning brief row (low; eval harness).**
    - It adds 13 CRM notes, firm and thesis, snippets and a message `to`, and cuts text at 600 characters mid-word.
    - Nothing changed for Tara.
    - **Fix:** for `--mode daily`, leave notes out (or add notes to the row in `shared/connectors.md`), and cut at a word or line.

## 6. Score: 8.5 out of 10 (as Tara)

**The morning did its main job, better than last round:**
- One push named the right thing and said the note was ready. Home opened on that very row, open and in view.
- The nudge was short and sourced, and thanked Aditi for Nimbus. "Your note" opens the thread I am told to reply in.
- Every tap I made held, and Home said so at once, on Today and on Portfolio.
- The next hour saw my nudge and Aditi's reply.
  - It drafted the team note to the right five people, quoted her yes and left the runway out.
  - It did not nudge Kestrel again. Nothing was lost.

**What cost points:**
- My top card's draft promises the intro "Thu 29 Oct": today, before Rahul can even answer. From tomorrow it is a past date that nothing will catch.
- Had I tapped Done instead of Sent it, the dinner invite would have gone quietly, labelled "Marked sent".

**Smaller things:**
- Kestrel says "read it" with no link on Today.
- A "hold" answer has no tap.
- A few rows say the same thing twice.

## Round-eleven findings

| # | Round-eleven finding | Now | Note |
| --- | --- | --- | --- |
| 1 | The hero's draft promises a date that has passed | Partly | The 28 Oct rewrite made it "Thu 29 Oct": today, not past. It dropped "by", so the engine never flags it once it passes (finding 1) |
| 2 | Today and the Portfolio hero say "Nudge ready" after Sent it | Fixed | The row reads "Nudged Aditi on 29 Oct" at once, the Portfolio hero steps aside, and "more open" counts right after Close ask |
| 3 | Open in Gmail opens a new message; no link to the note; doubled chips | Partly | Today's row links "Your note", and the doubled "Draft ready" is gone. Open in Gmail is still a new message, the Portfolio rows lack the link, and "Nudge ready" shows twice (finding 8) |
| 4 | The push names a row, but Home opens on another hero | Fixed | Home opens on Today with the pushed row open and in view |
| 5 | The reply test reads too wide | Fixed | owed-kinds now says "an email that answers one of the asks in `items`", and that a partial reply answers only those |
| 6 | An undated promise never joins the waiting email | Fixed, new gap | Rahul's draft carries the dinner line, the row says Draft ready, and Sent it closes both. Done drops it (finding 2) |
| 7 | A seeded draft asks for the same thing twice | Fixed | Fatima's draft asks once |
| 8 | The bundle shortcut reads more than a morning run | Partly | Partial flags now, and no LPs, KPIs or empathy maps. It still adds notes, firm and thesis (finding 11) |
| 9 | Sent it leaves no sent mail in the mock | Fixed | The 07:28 read saw the nudge in the note's thread, and the note to Rahul |

New this round: findings 2 to 7, 9 and 10, plus the new part of finding 1 (the bare date the engine cannot see).

**Files** (all under `/tmp/claude-0/-home-claude/f41ebfd9-0635-5201-96ea-278169523f82/scratchpad/evals-r12/nudge-tara/evals/runs/nudge-tara/`):
- `bundle.json`, `bundle-mock.json`, `owed-drafts.json`, `run/` (06:28)
- `w0728/` (07:28 run)
- `qa/` (scripts, logs `look-0640.json`, `taps2.json`, `look-0735.json`, screenshots in `qa/shots/`)
- `mock_log.jsonl`
- `report.md` was not written: the harness refused it.
