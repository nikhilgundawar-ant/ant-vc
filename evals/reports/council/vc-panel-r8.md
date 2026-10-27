# Instinct for VCs: VC panel, round eight

**This is a simulated panel. No real investor took part.** One Claude agent played all seven: six people at the fictional Quillwater Ventures (Aditi Rao, Partner; Kabir Shah, Principal; Meera Iyer, Associate; Rohan Das, Analyst; Tara Menon, Head of Platform; Vikram Nair, CFO and IR) and a solo GP running a $30M fund alone.

## What I read and ran

- **Read, in order:**
  - my round-seven report (`vc-panel-r7.md`);
  - "Round eight: what changed" in `BUILD_LOG.md`;
  - the seven packs in `evals/runs/council/briefs-r8/`;
  - every `level-*-today-380.png`, `met-log-380.png`, `qa.json` and `qa-round8.json`;
  - the diff 2b5f57b to 4ff0548 for engine, skills, shared, home, `demo.py` and `replay.py`;
  - the Claude-run eval of Meera's Friday run on 0.6.0.
- **Also read:** two Claude-run evals on 0.7.0, `r8-morning-brief-tara.md` and `r8-morning-brief-vikram.md`. They were saved in the repository, not yet committed, while I worked. I cite them as evidence on 0.7.0, and I reproduced their main finding myself.
- **Scratch copy:** `/tmp/vc-panel-r8/repo`. Its code matches 4ff0548. Uncommitted engine edits appeared in the real repository at 08:35, after my copy; I did not score them.
- **Suites, in the scratch copy:**
  - `--suite round8`: 9 of 9. `--suite round7`: 10 of 10.
  - `round6` 4 of 4, `round6b` 8 of 8, `evals6` 8 of 8, guard 607 of 607.
  - Full runner: 142 of 142. Design lint: 0 violations in 214 rules.
  - Home QA, re-run here: 428 of 428. Page hash 1457cbc5b5fe, the same as the committed `qa.json`.
- **My own replay** (`replay._week`, all seven, Thu 22 to Mon 26 Oct, every run dumped). On top of it:
  - Meera's three Thursday met logs saved exactly as Home fills them in, applied as pulse step 3 says, then Aditi's and Meera's Homes replayed to Fri 30 Oct: with and without a CRM stage date, and with no tap at all;
  - Tara's week to Fri 30 with "Sent it" tapped at Thu 10:00, and Aditi's intro email (Tara copied) landing Mon 12:00;
  - Tara rebuilt from bundles cut to the read windows in `shared/connectors.md`, and replayed on those windows to Thu 29;
  - the `drafts` command run as a subprocess (`python3 -I -S`) on ask and letter notes written without their ids;
  - "Move to Closing" from Atlas's own met log, the refresh entries' `met_with`, Vikram's capital call, Aditi's Monday chore, and every push's recorded subjects.
- **Drafts in the replay come from `evals/demo.py`**, not Claude. I judged whether the engine asks for the right draft at the right time with the right inputs, and I say where only the demo wording is off. The README's sample link is not scored this round.

## In short

- **Round eight delivered almost all of round seven's list.**
  - Heads-ups name what you owe: "15:30 Northgate Endowment: You owe them: answer the fee offset question, 43 days late" (Vikram, Thu 14:20).
  - Late founder promises on contested deals lead. Aditi's Monday push: "Send the term sheet markup: Ishaan (Atlas Settlement), 3 days late. Draft ready". Meera's Monday hero: Omkar's feedback, 7 days late, "The round is filling up".
  - The met log fills in from the meeting. Halo at Thu 17:29 offers "Move to Second meeting" and no stale step. "Move to Closing" is accepted.
  - Tara's cash-tight asks go to Aditi first, by address. Rows say "Asked Aditi on 22 Oct", and "Intro made on 26 Oct" once the intro email arrives.
  - A call with Kabir copies him in and asks the founder for times. No hour is offered twice across the team.
  - Words: "US companies with a team in India"; Tanvi's "until next week" kept; the sync's "with yours" kept; no "Hi all" for the solo GP.
  - The skills now describe asks, the letter and refreshes, and `drafts` keeps `action_id` and `note_kind`.
- **What still keeps six of seven below 9.5:**
  - **The replay is not what a real run reads.** A morning brief reads 7 days of mail. Tara's Nimbus warm path then disappears. From Friday to Monday her row reads "Asked Aditi for the intro on 22 Oct. ... No warm path found: ask your team", and "Intro made" comes two days late.
  - **Money and due work can still vanish.** Peregrine's $150K capital call is Vikram's hero on Friday and Monday with no draft. Aditi's highlights paragraph, due Monday to Vikram, is on no row and in no push. A week-ahead line "claims" Vikram's 47-day fee offset without naming it, so Monday's push skips it.
  - **The met log stops at the meeting.** After an empty-step save, every Pipeline still shows "Next: Second meeting, 24 Oct", and nothing asks Meera for the new step.
  - **Asks in flight fall off Today** 21 days after the founder asked, before the five-day nudge. Tara sends Aditi three separate notes on one morning.
  - **Smaller:** an undated "until next week"; met pitches still in Rohan's inbound list; a carried push with Thursday's day count; sample data that gives the solo GP colleagues.

## Scores

| Persona | Level | R7 | R8 | Why, in one line |
|---|---|---|---|---|
| Aditi Rao | Partner | 9 | 9 | All eight of her round-seven complaints are fixed (Monday push, Friday heads-up, clean Pipeline, Move to Closing, review sent Friday). But on Monday the highlights paragraph she owes Vikram that day is on no row, push or hero. |
| Kabir Shah | Principal | 9 | 9.5 | No hour offered twice, his review goes out Friday, and Monday leads with the Kite checklist, "Tamarind Capital wants to lead". Only demo wording is left. |
| Meera Iyer | Associate | 9 | 9 | Halo's met log now moves the stage and writes no stale step, and Monday leads with Omkar's feedback. But two drafts are still bracket skeletons, and after an empty-step save nothing asks for the next step. |
| Rohan Das | Analyst | 8.5 | 9 | Plain pass reasons, Tanvi's words kept, Kabir copied on the Rhea call. But Paysa and Ruplink still sit in his inbound list on Monday, and "until next week" (written 21 Oct) is undated. |
| Tara Menon | Platform | 8.5 | 9 | Board notes to Aditi first, rows that say who was asked, "Intro made" from the mail. But a real morning brief loses the Nimbus warm path, and her asks drop off Today before the nudge. |
| Vikram Nair | CFO and IR | 8.5 | 9 | The 14:20 heads-up names the fee offset, no far-off LP is Overdue, and the letter row sits in Next up. But his top item, Peregrine's $150K call, never gets a draft, and Monday's push skips the 47-day fee offset. |
| Solo GP | $30M, alone | 8.5 | 9 | No team words, clean pass reasons, and the Raj note says the Arjun intro is on its way. But her $60K capital call has no draft and leaves Today on Friday, and a carried push says "day 4 of 10" on day 5. |

- **Average: 9.07** (round seven: 8.7).
- **Quillwater's six: 9.08** (round seven: 8.75).
- Five went up, two held, none went down. Kabir reaches 9.5.

## Round-seven tests and asks

| Item | Verdict | Evidence |
|---|---|---|
| Ask 1: real run matches the replay, and is published | Mostly | Morning brief step 6.3 now describes `kind: "letter"` and `kind: "ask"`; `shared/engine.md` lists both. `drafts` keeps `action_id` and `note_kind`: my subprocess run kept 3 of 3 ask notes and the letter's `commitment_id`, with the ids left out of the drafts. The Tara and Vikram Claude-run evals were done. But Tara's found the Nimbus path lost in a real brief, and I reproduced it (see test 1). The link is not scored this round. |
| Ask 2: the met log is one tap | Met, with edges | Halo at Thu 17:29: title "Halo Reconcile: second meeting", step left empty, "Move to Second meeting" preselected, row reads "which was this meeting". Beacon at Fri 12:24 the same. A CRM contact in the last five working days counts in every Home. "Move to Closing" from Atlas's own form is pending; Passed, Portfolio, Won, Closed won and Lost are refused. Edges: the CRM's old step stays as "next", and nothing asks for the new one. |
| Ask 3: rank by what it costs to miss | Mostly | Heads-ups name what you owe (Vikram Thu 14:20, Aditi Fri 08:24). Monday: Aditi's push is the markup, row reason "Term sheet from Bluepeak Partners"; Meera's hero is Omkar's feedback. Banyan is never Overdue. Vikram's Friday letter row is second in Next up. Side effects: Aditi's due-today chore vanishes; a week-ahead line hides Vikram's fee offset from Monday's push. |
| Ask 4: times and rewrites hold for everyone | Met | Rohan's Rhea draft: "I have copied Kabir here. Could you share two or three times that suit you next week?" (cc kabir@, no slots). Refresh entries carry `met_with` (for example `['Arjun Khurana']`) and `met_title`. Fri 06:24: "Hi Raj, Arjun, / Arjun, good to see you on Thu 22 Oct". Vikram's Helen draft loses "when we meet today". |
| Ask 5: founder asks and words, last mile | Mostly | Board notes to aditi@ for Orbit and Kestrel; team notes by address (QA `team-note`); "Asked Aditi on 22 Oct", "Intro made on 26 Oct"; 0 "Us-India", 0 "intro to", 0 "Hi all" in any draft; "No one in your network fits yet" for the solo GP. Gaps: the dinner push names the path but not the ready note; asks leave Today at 21 days; the solo met log still quotes "partner vote prep". |
| Test 1: real runs keep the links | Mostly | Ids survive the real CLI, and "Sent it" moves rows on. But replayed on the real read windows, Fri 06:28 to Mon 13:28 read: "Asked Aditi for the intro on 22 Oct. Divya Raman asked on 13 Oct. No warm path found: ask your team". "Intro made" arrives Wed 28, two days after the email. A fresh build on those windows sends all three notes to all five colleagues. The Claude-run eval saw the Nimbus note go to the team on Thursday. |
| Test 2: the shared link is current | Not scored | Per this round's brief. It is republished from this build at release. |
| Test 3: heads-ups name what you owe | Met | Vikram, Thu 14:20: "15:30 Northgate Endowment: You owe them: answer the fee offset question, 43 days late". Aditi, Fri 08:24: "10:00 Orbit Treasury: You owe them: review the board deck, 1 day late". |
| Test 4: late founder promises beat chores | Mostly | Aditi, Mon 06:24: "Send the term sheet markup: Ishaan (Atlas Settlement), 3 days late. Draft ready". Meera, Mon 06:29 hero: "Share feedback after the partner meeting ... The round is filling up". But the chore is not named "alongside": "Write the portfolio highlights paragraph" is on no Aditi row Monday, 06:24 to 19:24. |
| Test 5: the CFO's list | Met | Mon 06:20, first Next up row: "Answer the fee offset question ... 47 days late". 0 LP rows Overdue more than 30 days before a window, all week. Fri 06:20: letter row second in Next up, "due Sat 24 Oct, so today", no LP touch above it. |
| Test 6: words survive the budget | Met | "until next week" on the Vaultline row at all 7 runs, Sun 09:25 to Mon 09:25. "with yours" on Aditi's sync line at every run, Thu 06:24 to 11:24. |
| Test 7: no hour offered twice across the team | Met | 0 clashes at the Thu, Fri and Mon mornings across six Homes. Kabir's Monday Rohit draft offers "Tue 27 Oct at 10:00 or 11:00"; no colleague's draft offers his hours. |
| Test 8: refreshes tell the truth | Met | No "good to see you" to Raj; no "when we meet today" after the meeting. Demo wording still keeps Kabir's 19 Oct line "Thanks for the customer reference list and the security audit report you are sending over" (the 22 Oct meeting has no notes, so the skill says keep it and ask him to check). |
| Test 9: one tap clears the team's Pipeline | Met, but the test is weak | My tap replay to Fri 30: 3 of 3 pending; none stale for Aditi Sat to Thu; Closing accepted. But with no tap at all, the three are also clean Sat to Mon (the CRM's 19 Oct contact counts). Untapped, Halo and Rivulet turn stale Tue 27 and Sable Thu 29. Tapped, all three stay clean through Thu 29. The tap's value shows Tue to Thu, outside the test. |
| Test 10: asks addressed, words clean | Mostly | Board notes to aditi@; Thu 13:28 push "14:30 Founder community: Divya needs two banks as customers: Aditi knows Raj Malhotra"; nudge after five working days on the Portfolio tab; no "Us-India" or "intro to"; no "Hi all", "Your team" or "board partner" for the solo GP. Gaps: Orbit leaves Today Tue 27 and Kestrel Wed 28, before the Thu 29 nudge. The solo met log quotes "Solace Treasury: partner vote prep" at every run. |

## Still wrong, per persona

**Aditi (partner)**
- **Mon 06:24 to 19:24:** "Write the portfolio highlights paragraph" (promised to Vikram, due 26 Oct) is on no Today row, no push and no hero.
  - It survives only inside the 10:00 meeting's prep card.
  - Vikram's Home says "Aditi Rao owes you: write the portfolio highlights paragraph ... due today".
  - In round seven it led the push. Now it is gone. The fix should demote it, not drop it.
- **Fri 09:24, hero for the 10:00 Orbit board (8.0 months of runway):** "You owe them: review the board deck, 1 day late | Vikram asked: introductions to senior engineers: hiring two this quarter (05 Oct)".
  - The card's first prep seed: "What would make the introductions to senior engineers: hiring two this quarter easiest for you?"
  - The runway comes second. Tara's note asks Aditi whether to help them hire at all. That is the board's question.
- **Thu morning:** Tara's Home writes Aditi three separate emails (Nimbus intro, Kestrel, Orbit), with no line linking them.
- **Her Pipeline after Meera's met logs:** Halo and Rivulet show "Next: Second meeting, 24 Oct" every day to Fri 30, though the meeting was on 22 Oct.
  - If the CRM does not move its stage date, Halo reads "Second meeting 13d" on Friday and "16d" on Monday.
- **Sun 17:24:** "Week ahead: 1 meeting, decide Gravity Payouts by 31 Oct, 3 promises late" records the Arjun intro as its subject. So Monday's push skips it. Harmless here (the markup also qualifies), but see Vikram.

**Kabir (principal)**
- **Fri 06:28, refreshed Kite draft:** "Sid, good to see you on Thu 22 Oct. As promised at our check-in on 19 Oct ... Thanks for the customer reference list and the security audit report you are sending over."
  - The meeting was "Kite Pay: references" and has no notes, so the engine rightly keeps the draft.
  - Demo wording only: the context reads "brought up to date", not "check the reference line still stands", as the skill now asks.
- **Demo subjects read as tasks:** "Schedule tech diligence with the CTO advisor", "Forward the Cobalt AA notes". The skill now forbids this; the demo still does it.
- Nothing in the engine that would embarrass him.

**Meera (associate)**
- **Thu 06:29 to Mon:** Omkar's feedback and Neha's pricing view are still three bracketed lines each.
  - This is honest: the 19 Oct partner meeting has no notes anywhere.
  - But the draft could say who holds the answer (the partner who ran that meeting), not only "Fill in the 3 lines".
- **After the tap (my replay):** Halo and Rivulet are saved with an empty step, as Home fills them in.
  - From Fri 23 to Fri 30, Halo never comes back to her Today to ask for a next step.
  - The CRM keeps "Second meeting, 24 Oct" as next.
  - Fri 30, the Rivulet row reads "Deal: next step was due 24 Oct", about the meeting she logged.
- **Mon 06:29:** "12 things for today, 6 urgent", plus four met-log forms (Rivulet, Halo, Sable, Ember) that the headline does not count.

**Rohan (analyst)**
- **Mon 06:25:** Paysa Labs ("you met them on 22 Oct") and Ruplink ("you met them on 23 Oct") still sit under "Inbound worth a look", next to their met logs. Round eight's rule ("a met pitch with a deal leaves the inbound list") skips returning passes.
- **Sun 09:25 to Mon 09:25, Vaultline:** "Tanvi says: '... a small allocation for Quillwater until next week.'"
  - She wrote it on Wed 21 Oct. By Monday, "next week" is this week, and the row gives no date.
- **Paysa met log ("Paysa Labs: first call"):** the stage menu offers only "Still Inbound" or "Move to Screening". "First call" is not an alias, so he cannot log a first meeting from the form.

**Tara (platform)**
- **Real run (Claude-run eval on 0.7.0, reproduced):** a morning brief reads 7 days of mail, and Aditi is not in it, so the Nimbus warm path is recomputed to none.
  - On the eval's real Thursday run, the Nimbus note went to all five colleagues.
  - In my replay on the real read windows (setup wide on Thursday, then 7-day morning briefs), Fri 06:28 and Mon 06:28 read: "Asked Aditi for the intro on 22 Oct. Divya Raman asked on 13 Oct. No warm path found: ask your team".
  - Aditi's intro lands Mon 12:00, but with no path the Mon 13:28 row still says "Asked Aditi for the intro". The path comes back on Tue 27, only because her own email puts her in Tara's mail. "Intro made on 26 Oct" shows on Wed 28.
  - A fresh build on the same windows also loses the board routing: all three notes go to the team.
- **Thu 06:28:** three notes to Aditi (two board notes and the Nimbus request) with no linking line.
- **Tue 27 and Wed 28 (my replay, "Sent it" at Thu 10:00):** Orbit, then Kestrel, drop off Today, because the founders asked on 05 and 06 Oct.
  - Her notes went out on 22 Oct.
  - The Thu 29 nudge shows only on the Portfolio tab.
- **Wed 28 06:28 (my extended replay):** push "Still open: Nimbus Collect: an introduction to two banks as customers. Path: Aditi…".
  - It is cut mid-name.
  - The row says "Intro made on 26 Oct: tap Done to close it".
- **After "Asked Aditi":** there is no next state for "Aditi said yes, ask the team".
  - By pulse step 3, a later "Draft a note to your team" tap writes `dr_<action id>`. That is the id of the note already marked sent, so Home would hide the new one.
- **Words:** "Kestrel Pay: introductions to senior engineers: hiring two this quarter, before we source" (three colons). Partly demo wording, but the ask text itself carries the colon.

**Vikram (CFO and IR)**
- **Fri 06:20 and Mon 06:20, hero:** "Peregrine Trust owes $150K on a capital call | Called on 05 Oct, 21 days ago; no touch in 99 days", with an Open button and no draft.
  - The fee offset and the letter are drafted before the brief. The money is not.
  - The Claude-run eval found the same: `owed.json` has no kind for an LP alert.
- **Mon 06:20, push:** "Model the runway scenarios: Neel (Kestrel Pay), 10 days late".
  - The fee offset, 47 days late to an LP he met on Thursday, is skipped.
  - Sunday's "Week ahead: no meetings booked, 4 promises late" recorded it as its subject without naming it.
- **Fri 06:20, letter row:** "... so today. Instinct drafts it from the KPI history and the LP list", next to "Draft ready". It still promises a draft that exists.
- **The letter itself (Claude-run eval):**
  - About 3,700 characters, so Home's "Open in Gmail" is off (limit 1,800) and he gets Copy only.
  - It showed "Paid in: $35.85M" against "$36M called", which tells every LP that one LP has not paid. Nothing in lp-watch step 4 warns against it.
- **Demo wording:** the letter's watch list gives revenue, not why each company is on it ("Orbit Treasury: $198K revenue in Sep 2026, 2% ahead of plan").

**Solo GP**
- **Thu 06:24:** "Peregrine Trust owes $60K on a capital call ... no touch in 95 days", with no draft. From Fri 06:24 it is off her Today: founder rows fill the seven lines, though the money is still unpaid. She is her own IR.
- **Fri 07:24, push:** "Review ready: Decide on Beacon Credit Rails. Term sheet out, day 4 of 10". Thursday's review, carried to Friday, keeps Thursday's count; on Friday it is day 5 (Aditi's 09:24 push says "day 5 of 10").
- **Fri 09:24, push:** "12:00 Beacon Credit Rails: Last met 20 Oct: catch-up". Before a founder call on terms, it says only when they last met.
- **Demo data only, but it is what "View as solo" shows:**
  - every Solace met-log row quotes "Solace Treasury: partner vote prep" (Thu to Mon);
  - 30 of the 37 deals in her Pipeline have a colleague as owner, so their rows show that colleague's initials ("ME", "RO", "KA") and "Partner: Aditi".

## Top five changes

1. **Make the replay read what a real run reads, and keep what a wider read found (7 of 7; Tara and Aditi feel it now).**
   - Feed each replayed run the bundle its skill reads (`shared/connectors.md`): 7 days of mail for the morning brief; today and tomorrow for a pulse.
   - Never let a narrow read erase an ask's `paths` or `warning_to`. Recompute them only when the colleague is visible, or add the firm members from config as people.
   - Detect "Intro made" from the kept path, so it still fires after a narrow read.
   - Re-run the Tara and Vikram Claude-run evals on the fix.
2. **Draft the money, and never drop due work (3 of 7: Vikram, the solo GP, Aditi).**
   - Add an owed kind for an overdue capital call: a short reminder to the LP's contact, drafted before the brief in the LP owner's Home.
   - A promise due today never leaves Today. When the cap cuts it, the push names it in a clause, or it takes the last row.
   - A push records only the subjects its line names.
   - The letter row says "Draft ready". A long letter opens as a document or copies cleanly into Gmail. lp-watch step 4 never sets paid-in next to called.
3. **Finish the met log (4 of 7: Meera, Aditi, Rohan, the solo GP).**
   - After a save with no step, the owner's Today asks for one the next morning ("Halo Reconcile: met 22 Oct, add the next step") until it is set.
   - When the CRM's step was the meeting, mark it done, so colleagues read "No next step since 22 Oct", not "Next: Second meeting, 24 Oct".
   - Set the stage date when the CRM keeps one. When it does not, colleagues' Homes date the move from the logged contact.
   - Add "first call" to the first-meeting aliases.
   - Test from Tue 27 to Thu 29, not only Sat to Mon.
4. **Follow asks to the end (2 of 7: Tara, Aditi).**
   - One note per person per morning: the three asks for Aditi become one email, or each names the others (`also`).
   - An ask with a note out stays on Today until made or closed, whatever the founder's ask date. The five-day nudge shows on Today.
   - After a board note, "Yes, ask the team" makes a new draft id, never the sent note's id.
   - A made intro is never pushed as "Still open". No push is cut with "…".
   - The dinner heads-up and the meeting line say "note ready" for an ask, as they do for a promise.
5. **Keep words true as days pass (4 of 7: Rohan, the solo GP, Aditi, Kabir).**
   - Date a founder's quote once it is two days old ("Tanvi wrote on 21 Oct").
   - A met pitch leaves "Inbound worth a look", returning passes included.
   - A carried push recomputes its numbers on the day it goes out.
   - A heads-up with nothing new names the meeting's purpose ("Founder call on terms").
   - A cash warning leads a board card's seeds. Fix "the an introduction" in the seed text.
   - Demo: subjects in the reader's words. The solo sample's calendar titles and deal owners speak for one person.

## Reaching 9.5: tests on the same replay

1. **The replay reads what a real run reads.**
   - Replay Tara Thu 22 to Fri 30 with each run's bundle cut to its row in `shared/connectors.md`.
   - Every morning the Nimbus row keeps "Warm path: Aditi knows Raj Malhotra at Fable Bank".
   - With Aditi's intro email (Tara copied) landing Mon 12:00, the row reads "Intro made on 26 Oct" by Mon 13:28.
   - The same windowed replay for Aditi and Vikram loses no path, name or warning against the full-bundle replay.
2. **One note per person, asks followed to the end.**
   - Thu 06:28: Tara's Home holds one email to aditi@quillwater.vc covering all three asks, or three that name each other.
   - With "Sent it" at Thu 10:00 and no reply, Orbit and Kestrel stay on Today through Fri 30. Thu 29 06:28 shows "nudge Aditi" on Today.
   - A "Yes, ask the team" tap yields a team note with its own id, shown as "Draft ready".
3. **Money is drafted before the brief.**
   - Thu 06:20: Vikram's Home holds a draft to Peregrine Trust's contact about the $150K call. His Friday and Monday heroes say "Draft ready". The solo GP gets the same for $60K, and the row stays on her Today until paid or snoozed.
   - The letter row says "Draft ready" without "Instinct drafts it".
4. **Nothing due or late vanishes.**
   - Mon 26: at every Aditi run, "Write the portfolio highlights paragraph" is a Today row or is named in the 06:24 push, while the push still leads with a late contested founder promise.
   - Vikram's Mon 06:20 push, or his Sun 17:20 line, names the fee offset.
   - No run's `push_subjects` holds a subject its line does not name.
5. **The step after a met log.**
   - Meera saves Halo and Rivulet with an empty step at Thu 19:05.
   - From Fri 06:29 until she adds one, her Today shows "Halo Reconcile: met 22 Oct, add the next step".
   - No Pipeline in any Home shows "Next: Second meeting, 24 Oct" for them, and no stale reason calls the logged meeting a missed step.
   - Aditi's Pipeline reads "Second meeting, 1 day" for Halo on Fri 23, whether or not the CRM keeps a stage date. Check Tue 27 to Thu 29 as well.
6. **Quotes carry their age; met pitches move on.**
   - Mon 26 06:25: the Vaultline row dates Tanvi's words ("wrote on 21 Oct"), or says "this week".
   - From Fri 15:25, Paysa and Ruplink are off Rohan's "Inbound worth a look". Paysa's met log offers "Move to First meeting".
7. **Carried lines are current.**
   - The solo GP's Fri 07:24 review push says "day 5 of 10", or gives no count.
   - Her Fri 09:24 Beacon heads-up names the call ("Founder call on terms").
   - No prep seed in any Home contains "the an ".
8. **The board meeting leads with the board's question.** At Fri 08:24 and 09:24, Aditi's Orbit hero and first prep seed put the runway (8.0 months) next to the hiring ask, and the hiring is framed as her decision.
9. **The solo sample speaks for one person.** In "View as solo", no row, met log or Pipeline fact contains "partner vote", a colleague's initials, or "Partner: Aditi".
10. **The shared link is current at release.** The page at the README's sample link contains "View as", and its hash matches `qa.json` (1457cbc5b5fe for this build).

## Reproduce

- Every check ran on the scratch copy `/tmp/vc-panel-r8/repo` (code at 4ff0548). My runs regenerated its screenshots and `evals/scorecard.md`. I changed nothing in the repository except writing this report.
- Replay dumps, one per persona: `/tmp/vc-panel-r8/dump/`. Screenshot crops: `/tmp/vc-panel-r8/crops/`.
- Scripts in `/tmp/vc-panel-r8/scripts/`. Each takes the repo path first.
  - `dump_week.py`: every run Thu to Mon; push, hero, rows, drafts in full, met-log prefill, Pipeline.
  - `tap_week.py`: Meera's met logs saved as Home fills them, applied as the pulse does, Aditi and Meera replayed to Fri 30. Add `today` to print their Today rows.
  - `tara_asks.py`: "Sent it" at Thu 10:00, intro email Mon 12:00, replay to Fri 30. Add `--no-intro` to leave the email out.
  - `windowed_tara.py`: Tara built from the morning-brief read windows, and the Thursday-setup then Friday-brief sequence.
  - `windowed_nudge.py`: Tara on the real read windows from Thu 22 to Thu 29, with "Sent it" and Aditi's intro email; prints the Nimbus row each morning.
  - `real_drafts.py`: the `drafts` command as a subprocess on ask and letter notes without ids.
  - `closing_and_refresh.py`: "Move to Closing" from Atlas's form; Friday's refresh entries.
  - `vikram_peregrine.py`, `probe_aditi_mon.py`: the capital call draft, and Aditi's Monday chore.
  - `crop.py`: cuts the tall phone screenshots.
- These folders are temporary.
