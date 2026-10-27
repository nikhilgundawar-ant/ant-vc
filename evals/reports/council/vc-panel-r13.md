<!-- VC panel, round thirteen. Written by one Claude agent playing all seven personas on a clean clone at caa70d3 (0.7.6). Simulated: no real investor took part. -->

# Instinct for VCs: VC panel, round thirteen

**This is a simulated panel. No real investor took part.** One Claude agent played all seven: six people at the fictional Quillwater Ventures (Aditi Rao, Partner; Kabir Shah, Principal; Meera Iyer, Associate; Rohan Das, Analyst; Tara Menon, Head of Platform; Vikram Nair, CFO and IR) and a solo GP running a $30M fund alone.

## What I read and ran

- **Read, in order:**
  - my round-twelve report (`evals/reports/council/vc-panel-r12.md`), whose "Reaching 9.5 or 10" tests are this round's bar;
  - "Round thirteen: what changed" in `BUILD_LOG.md`;
  - `git diff 947db4c caa70d3` for `engine/`, `skills/`, `shared/`, `home/`, `evals/demo.py`, `evals/replay.py` and `evals/home_qa.py` (27 files, 1,252 lines added, 207 removed);
  - the seven packs from `python3 evals/panel_pack.py --out DIR/evals/runs/council/briefs-r13`.
- **Fresh clone** at caa70d3 (0.7.6) in my own folder. The runner rewrote `evals/scorecard.md`. I ran `git checkout -- .` at the end: 0 changes in the clone. My scripts and outputs sit under the git-ignored `evals/runs/`.
- **Suites:**
  - `python3 evals/runner.py`: 211 of 211 pass, 7 Claude-run scores skipped in a clean clone, 769 s (slow because another agent's runner shared the two CPUs).
  - `--suite round13`: 18 of 18 (78 s). `--suite guard`: 718 of 718 (17 s).
  - `design_lint.py`: 0 violations in 219 CSS rules.
  - `home_qa.py --out DIR/evals/runs/council/home-r13`: 565 of 565, `page_sha256` 7e755edf2ead, matching `home/index.html`.
- **My own replays:** 46 runs of `replay._replay_windowed` to Mon 23 Nov, each run reading only its own window, with the stock hooks plus a few of my own (a reply in the draft's own thread, my own sent message in mail, a paid wire, Got it, a Pipeline step save).
  - **All seven, no taps**, Thu 22 Oct to Mon 23 Nov.
  - **Money**, Vikram and the solo GP, 9 variants each: Sent it Thu 22 10:00, with and without the sent email in mail; Peter's reply Thu 22 16:00 *before* Sent it (tap Fri 23 09:00); "Could you send the Fund II Q3 report" (other thread); "the wire goes out on Wednesday" Mon 26, then the second note sent Thu 29; "We paid it last Friday. Please check with your bank."; paid Thu 5 Nov; Sent it at 14:00.
  - **Asks**, Tara, 9 variants: Sent it and quiet; "Let me think about these and come back to you", alone and followed by a real answer Wed 28; the partial reply "Yes on Orbit. Let me think about the other two."; a reply before Sent it, naming the companies (tap 19:00) and naming none (tap next morning).
  - **Done and Sent it on a shared email** (Tara's CFO intro and dinner invite in one email): Done on either promise first; Sent it first, then Done on the other.
  - **Partner note**, Meera: sent Thu 22 10:00 and quiet; sent and answered Thu 22 14:00; answered at 11:00 *before* Sent it at 16:00; the note and both drafts sent; the note sent on Sable's decision day.
  - **Pipeline**, Meera: met logs Thu 19:05, Halo's step Fri 23 10:00, Trellis's step Wed 28 10:00, to Mon 23 Nov.
  - **Answered**: Aditi Sent it on the markup Fri 23; Kabir Sent it on his checklist and Got it on Rohan's market map Mon 26; Rohan and the solo GP Sent it on every pitch reply Thu 22.
- **Rendered** 16 replayed Homes in the real `home/index.html` with `QA.open` (`snap`, `state`, `when`, `member`). Taps I made on the page:
  - Sent it on Vikram's chase hero (Fri 23 08:40 and Thu 29 08:05), then read Today and LPs;
  - Done on Tara's CFO row, then Sent it on her dinner invite row (same email);
  - opened Tara's group nudge row (partial reply) and her deferred ask rows;
  - opened Meera's Rivulet row after the note was sent, and after Aditi answered;
  - read Pipeline after Aditi's markup went, and Meera's Pipeline after a saved step.
- **Drafts in the replay come from `evals/demo.py`, not Claude.** "Demo only" marks wording only the demo gets wrong; it is not scored.

## In short

- **Round thirteen meets six of my ten round-twelve tests in full and four in part. None is missed.**
  - **Money every week.** In all 18 money variants, the unpaid call reaches the phone every Wednesday from 28 Oct to 18 Nov, for Vikram and for the solo GP. Last round the solo GP got none in 32 days.
  - **Only money talk counts.** "Could you send the Fund II Q3 report" is no longer a reply. The second note comes Thu 29.
  - **No "no reply" after a partial reply.** Pushes say "Aditi answered on Orbit; Kestrel and Nimbus still wait. Note ready", and Today's Orbit row links "The reply".
  - **Done is never Sent it.** Done on one of two promises in one email closes that promise only. The page says "take its lines out", and the next check rewrites the email for the promise left.
  - **The note to a partner waits on her.** No second note in any variant. Rows read "Asked Aditi on 22 Oct for the firm's view", then "Aditi replied at 14:00: read it, then send".
  - **The race shows once on Friday**, and a passed deadline is never "Another fund is moving".
  - **Gone means gone.** Old call replies leave on day 8 and are not written again. The Monday digest no longer brings back old pitches.
- **What still costs points:**
  - **A deferring reply's nudge vanishes.** It is written Mon 2 Nov 06:28 and deleted at 07:28. Tara's rows say "nudge Aditi" for three weeks, with no draft to send.
  - **"We paid it last Friday" is not heard.** Five working days later the second note asks Peter "when we should expect it".
  - **Passed races still lead.** The solo GP's hero is Atlas's passed race on 17 mornings. One Thursday review push drops the "passed" flag.
  - **Small repeats.** The CRM's old step in a race row after Sent it. Paysa Labs flickers back to "book a call". Vaultline's "oversubscribed" is pushed every Wednesday.
- **Scores: average 9.71** (round twelve: 9.5). Meera reaches 10, the solo GP 9.5. Kabir holds at 10. Aditi, Rohan, Tara and Vikram hold at 9.5.

## Round-twelve tests on this build

| Round-twelve test | Verdict | Evidence |
|---|---|---|
| 1. A fund word is not a reply | Met | Vikram, Sent it Thu 22, "Fund II Q3 report" email Tue 27 09:00. Thu 29 06:20 hero: "chased Peter on 22 Oct, no reply in 5 working days. Second note ready". No line says "Peter replied". Same for the solo GP |
| 2. A reply that defers is followed | Partly | Met: Aditi's "Let me think about these and come back to you" (Mon 26 15:00) gives "Aditi replied on 26 Oct: the answer is to follow", then Mon 2 Nov 06:28 a nudge for all three asks. Not met: the nudge draft is gone at 07:28 (traced run by run) and never written again. Rendered Tue 3 Nov: three "Nudge" rows offer only Close ask. Pushes Wed 4, Thu 5, Wed 11 to Thu 19 Nov say "nudge Aditi, the answer Aditi promised on 26 Oct has not come", with no note |
| 3. No "no reply" after a partial reply | Met | Thu 29 06:28 push: "Aditi answered on Orbit Treasury; Kestrel Pay and Nimbus Collect still wait. Note ready". Repeats Wed 4, 11, 18 Nov say the same. Rendered Thu 29: the Orbit row reads "Aditi replied on 26 Oct: read it, then answer here" with a "The reply" chip; the group row's "Before you send" names only Kestrel and Nimbus |
| 4. Money every week, team or solo | Met | Every variant, both members: one money push each Wednesday, 28 Oct, 4, 11 and 18 Nov, in every week with five money mornings. Week 43 has two mornings only. Solo GP: "Peregrine Trust: owes $60K on a capital call" on each of those Wednesdays (round twelve: none in 32 days) |
| 5. Passed is not moving | Partly | Met: the kicker reads "Their deadline passed" (solo GP, Fri 6 Nov, rendered). Aditi's review pushes Thu 12 and 19 Nov read "Review ready: Atlas Settlement: term sheet from Bluepeak Partners, their deadline passed". Not met: the solo GP's Thu 12 Nov 15:24 push reads "Review ready: Atlas Settlement: term sheet from Bluepeak Partners", no flag, when the race is the hero. And that passed race is her hero on 17 mornings, Fri 6 to Mon 23 Nov |
| 6. A rival's date is never Instinct's | Met | Meera, no taps: Sat 24 09:29 the note is rebuilt once as "Your view on 2 founder emails", Sable dropped. No line to Mon 23 Nov says "Instinct's suggestion" about Monsoon Arc's date |
| 7. Gone means gone | Partly | Met: Meera's Harborline and Rohan's Tessera and Rupee Rails replies are re-slotted to Thu 29, leave Fri 30, and are never written again. Mon 9 Nov after the digest: 0 pitches back, Sutra keeps "you already write to them". Not met: Rohan's "Paysa Labs is back: Score 96: book a call" returns on the first pulse after each morning, Fri 30 Oct to Thu 5 Nov. He met them on 22 Oct |
| 8. The Friday trim keeps the race once | Met | Aditi, no taps, Fri 23 06:24 to 12:24: the Arjun row reads "due 20 Oct, 3 days late. Two other funds with offers, decide by 31 Oct" at every run, 11:24 included |
| 9. Sent it ends the old step | Partly | Met: Fri 13 Nov, rendered. The hero reads "The CRM's step, send term sheet markup, went on 23 Oct: update it". Pipeline reads "Sent 23 Oct: send term sheet markup. Add the next step". Prep carries `step_went`. Not met: the Atlas race row on Thu 19 15:24, Fri 20 and Sun 22 Nov reads "Term sheet, next: send term sheet markup, was due 23 Oct" |
| 10. A second note to a partner (suggestion) | Met | Meera, note sent Thu 22 10:00, drafts unsent: no second note to Mon 23 Nov, in all four note variants. But see Meera: a silent partner is never followed up |

## Scores

| Persona | Level | R12 | R13 | Why, in one line |
|---|---|---|---|---|
| Aditi Rao | Partner | 9.5 | 9.5 | The Friday race holds and review pushes say "passed". Left: the race row still names the step she sent, and the late-work line stopped saying its drafts are ready. |
| Kabir Shah | Principal | 10 | 10 | Nothing regressed in four weeks. Sent it and Got it still work on the page. What is left is cosmetic. |
| Meera Iyer | Associate | 9.5 | 10 | All three of her items pass. The note to Aditi drops Sable, waits on her, and turns rows into "Asked Aditi", then "Aditi replied". |
| Rohan Das | Analyst | 9.5 | 9.5 | The digest no longer revives old pitches. Left: Paysa Labs flickers back to "book a call", and Vaultline's old hold is pushed weekly. |
| Tara Menon | Platform | 9.5 | 9.5 | The partial-reply push and the reply link now pass. Left: the deferring reply's nudge is deleted within the hour, so a three-week loop has nothing to send. |
| Vikram Nair | CFO and IR | 9.5 | 9.5 | Money every week, and "Fund II" alone is no reply. Left: "we paid it last Friday" gets a chase asking when it will come, and the heroes keep "no touch in 96 days" after Sent it. |
| Solo GP | $30M, alone | 9 | 9.5 | Her $60K call reaches her phone every week now, and a passed race is no longer "moving". Left: that passed race leads Today for 17 mornings. |

Average 9.71 (round twelve: 9.5); Quillwater's six 9.67. Two up half a point, five held, none down.

## Each persona

### Aditi Rao, Partner (9.5, held)

Better since round twelve:
- The Friday trim keeps the race. Fri 23, every run from 06:24 to 12:24: "Promised to Arjun Khurana (Gravity Payouts), due 20 Oct, 3 days late. Two other funds with offers, decide by 31 Oct".
- After Sent it on the markup (Fri 23 10:00), rendered Fri 13 Nov:
  - hero: "Decide on Atlas Settlement | Term sheet out for 27 days, usually 10. The CRM's step, send term sheet markup, went on 23 Oct: update it";
  - Pipeline: "Sent 23 Oct: send term sheet markup. Add the next step".
- Review pushes say when a race has passed: Thu 12 and Thu 19 Nov, "Review ready: Atlas Settlement: term sheet from Bluepeak Partners, their deadline passed".
- No taps: late promises stay on Today every morning to Mon 23 Nov. Rendered Mon 9 Nov, Ready for you says how late each draft is ("To Ishaan Verma, 17 days late").
- Done on her paragraph row closes that promise only.
- 39 pushes to Mon 23 Nov, at most four a day, none old news.

Still costs time or trust:
- After Sent it, the Atlas race row reads "Term sheet, next: send term sheet markup, was due 23 Oct" (Thu 19 15:24, Fri 20, Sun 22 Nov). The hero right next to it says the step went.
- From Thu 5 Nov the line "3 promises more than a week late: send the term sheet markup (17 days late); ..." ends with no word on drafts. Through Wed 4 it said "Drafts are under Ready for you". All three drafts are still there.
- The pushes "3 promises more than a week late" (Fri 6, Wed 11, Wed 18 Nov) still name none of them.
- "Still open: Decide on Beacon Credit Rails" goes out Thu 12 and Thu 19 Nov, a week apart. Fine, but it is the same line.

For 10: a race row never names a step she marked sent; the late line says where its drafts are; its push names the oldest promise.

### Kabir Shah, Principal (10, held)

What works:
- Mon 26 08:00, Sent it on "Share the diligence checklist": at 09:10 the hero steps up to "Send the cohort analysis questions", and the checklist is gone.
- Got it on "Rohan Das owes you: market map of AA players" removes the row, and it stays gone.
- No taps, four weeks: his late promises take turns as the morning push, each with its days late. No push repeats on two mornings in a row.
- The folded deal fact names its deal: "Forward the Cobalt AA notes | ... Cobalt AA: next step was due 15 Oct."

Small, not scored:
- The Thursday review push reads "Review ready: Lumen Ledger: two other funds in diligence" four weeks running (29 Oct to 19 Nov).
- Demo only: "Could you also market map of AA players?"

To stay at 10: nothing above regresses.

### Meera Iyer, Associate (10, up from 9.5)

Better:
- **The note to Aditi drops what no longer holds.** No taps: Thu 22 06:29, "Your view on 2 founder emails and Sable Fraud AI". Sat 24 09:29, rebuilt once as "Your view on 2 founder emails". Nothing calls Monsoon Arc's deadline "Instinct's suggestion".
- **Sent it on the note** (Thu 22 10:00), rendered Fri 23 15:10:
  - the Rivulet and Trellis rows and the Sable hero read "Asked Aditi on 22 Oct for the firm's view";
  - no second note to Mon 23 Nov in any of four variants.
- **Aditi answers** (Thu 22 14:00), rendered 15:10: those rows read "Aditi replied at 14:00: read it, then send". Her reply is kept on the note.
- An answer that came at 11:00, before Sent it at 16:00, is on the note at the next morning's read (Fri 23 06:29).
- The note sent on Sable's decision day (Fri 23 07:10), no answer: the 14:29 push reads "Sable Fraud AI: no word from Aditi yet, decide today".
- Her Harborline reply is re-slotted to Thu 29, leaves Fri 30, and is never written again.
- The Pipeline loop holds to Mon 23 Nov. Halo's and Trellis's saved steps reach the CRM at the next run. Rendered Wed 28 10:12: "Term sheet draft to Neha by 06 Nov (saving to your CRM at the next check)".

Still costs, but not enough to hold her at 9.5:
- **A silent partner is never followed up.** With the note sent and Aditi quiet, the rows say "Asked Aditi on 22 Oct" for a month. Her pushes keep asking for "3 lines to fill" on the drafts that wait on Aditi. No line suggests a nudge or a word at Monday's partner meeting.
- The "no word from Aditi" push fires only when the note went the same day. With the note sent Thu 22 and Sable due Fri 23, it never fires.
- Ember Credit's 21 Oct meeting leaves the met-log prompts unlogged by Mon 9 Nov.

To stay at 10: after five quiet working days, the waiting rows offer a short nudge to the partner, or name the note at the next partner meeting.

### Rohan Das, Analyst (9.5, held)

Better:
- The Mon 9 Nov digest brings back no pitch (0 in the list, against 25 last round). Nothing reads "book a call" for a pitch from 17 to 21 Oct.
- Sutra reads "you already write to them" on every run while it is listed.
- Sent it on all 19 pitch replies Thu 22: none is drafted again.
- The Tessera and Rupee Rails call replies leave Fri 30 and never come back.

Still costs:
- "Paysa Labs is back: Revisit condition met ... Score 96: book a call" is back on the first pulse after each morning, Fri 30 Oct to Thu 5 Nov. He met them on 22 Oct and owes Rhea a call with Kabir. A narrow read seems to lose the "met" mark.
- "Still open: Vaultline: the round is oversubscribed" is pushed Wed 28 Oct, 4, 11 and 18 Nov. Tanvi held the allocation "until next week" on 21 Oct.
- The call replies are re-slotted every morning for a week ("The times this draft offered are today or earlier, too short notice").

For 10: a pitch he met never reads "book a call" on any run; a hold "until next week" ages after that week.

### Tara Menon, Head of Platform (9.5, held)

Better:
- **The partial reply** ("Yes on Orbit. Let me think about the other two.", Mon 26):
  - Thu 29 06:28 push: "Aditi answered on Orbit Treasury; Kestrel Pay and Nimbus Collect still wait. Note ready";
  - the repeats (Wed 4, 11, 18 Nov) say the same, never "no reply";
  - rendered Thu 29: the Orbit row has "The reply" chip, and the nudge thanks her on Orbit and asks only about the other two.
- **A reply before Sent it counts.** Reply Thu 22 15:00, tap 19:00: Fri 23 06:28 reads "Aditi replied on 22 Oct: read it, then answer here", and no nudge comes.
- **Done is never Sent it.** Done on "Intro two CFO candidates" (it shares an email with the dinner invite):
  - page: toast "Marked done"; the write has `closed_by: "done"` and leaves the email alone;
  - the invite row keeps "Draft ready" and Sent it, with "Before you send: Intro two CFO candidates is marked done: take its lines out";
  - the next check (07:28) rewrites the email for the invite only;
  - in the other order, Sent it first closes both, and a later Done changes nothing.
- No "Still open" line on two mornings in a row: the repeats now take turns.

Still costs:
- **The deferring reply's nudge disappears.** "Let me think about these and come back to you" (Mon 26):
  - Mon 2 Nov 06:28 the nudge is written for all three asks;
  - at 07:28 it is pruned (the check that a nudge is moot counts the deferring reply as an answer), and it is never written again;
  - rendered Tue 3 Nov: three separate "Nudge" rows, each with only Close ask;
  - pushes for three weeks say "nudge Aditi, the answer Aditi promised on 26 Oct has not come", one company at a time, with nothing to send.
- When the tap comes the next morning (reply Thu 22 15:00, Sent it Fri 23 09:00), the reply is found only on Mon 26. Until then the rows say "Asked Aditi for the intro on 23 Oct", a day after she answered.
- Demo only: the CFO email's date. On Mon 26 Instinct put "by Wed 28 Oct" in place of "this week". The demo did not mark that date as Instinct's suggestion, as the skill says to, so on Thu 29 the engine kept it as hers: "I will introduce you by Wed 28 Oct ... I am sorry this is late". The engine relies on that marker in free text, which is fragile.

For 10: a deferred answer's nudge survives until sent or answered, as one note for the asks it covers.

### Vikram Nair, CFO and IR (9.5, held)

Better:
- **Money every week.** In all nine variants, one push each Wednesday from 28 Oct to 18 Nov:
  - no taps: "Peregrine Trust: owes $150K on a capital call. Draft ready";
  - after Sent it: "chased Peter" (Wed 28), then "Second note ready" (Wed 4 to 18 Nov).
- **"Fund II" alone is no answer.** The Q3 report email (Tue 27) changes nothing: Thu 29, "chased Peter on 22 Oct, no reply in 5 working days. Second note ready".
- **A reply before Sent it counts.** Peter writes Thu 22 16:00, Vikram taps Fri 23 09:00: Mon 26 "Peter replied on 22 Oct, saying it goes on 28 Oct"; Thu 29 "Peter said it would go on 28 Oct, still unpaid. Second note ready".
- The Wednesday reply, then the second note sent Thu 29 10:00: "chased Peter again on 29 Oct", then from Thu 5 Nov "no reply in 5 working days: call Peter". No third note.
- Paid Thu 5 Nov: the line leaves Fri 6.
- Rendered Fri 23 08:40, Sent it on the chase hero: the LPs hero now reads "Marked sent 23 Oct: the next check updates this", no longer "Draft a note".

Still costs:
- **"We paid it last Friday. Please check with your bank."** (Mon 26, in the chase's thread):
  - the row reads only "Peter replied on 26 Oct";
  - Mon 2 Nov: "Peter replied on 26 Oct, still unpaid. Second note ready";
  - the note's context, "They replied on 26 Oct and the money has not come", sets up a chase asking "when we should expect it", to an LP who says he paid. Nothing says "check the bank first".
- After Sent it, both heroes still say "no touch in 96 days" beside "Marked sent", until the next check. Rows drop it; heroes do not.
- With the reply before the tap: "chased Peter on 23 Oct, Peter replied on 22 Oct". The chase takes the tap's date.
- From Thu 5 Nov Today says "call Peter", but the weekly push still says "owes $150K on a capital call, chased Peter".

For 10: a reply that says it was paid reads "Peter says it was paid on 23 Oct: check the account", with no chase; the heroes drop "no touch" after Sent it; the push says "call Peter" once Today does.

### Solo GP (9.5, up from 9)

Better:
- **Her $60K call reaches her phone.** No taps: "Peregrine Trust: owes $60K on a capital call. Draft ready" on Wed 28 Oct, 4, 11 and 18 Nov. Last round: never in 32 days.
- All nine money variants behave as Vikram's: the Fund II email is not a reply; "said it would go on 28 Oct, still unpaid"; "call Peter" after two notes; paid, the line leaves.
- A passed race is not "moving". Rendered Fri 6 Nov: "Their deadline passed | Atlas Settlement: term sheet from Bluepeak Partners".
- The Gravity review push Thu 5 Nov reads "two other funds with offers, their deadline passed".
- Old pitch replies leave on day 8 and do not come back after the digest.

Still costs:
- The passed Atlas race is her hero on 17 mornings, Fri 6 to Mon 23 Nov. The label is now true, but it is old news at the top of Today for over two weeks. Her late markup to the same founder sits below it.
- Thu 12 Nov 15:24: "Review ready: Atlas Settlement: term sheet from Bluepeak Partners", with no "passed". The flag is lost when the race is itself the hero.
- "We paid it last Friday" gets the same chase as for Vikram.
- "Paysa Labs is back ... book a call" flickers in on two Fri 23 pulses.

For 10: a passed race leads Today for at most two working days, then steps down to a row; every review push that names it says "passed"; a "we paid" reply is never chased.

## Top five changes

1. **Keep a deferred answer's nudge** (Tara).
   - The moot check should not count a reply marked `defers` as an answer once five working days have passed. Today it prunes the nudge the hour after it is written.
   - Show the three asks as one "3 founder asks wait on Aditi" row with "Nudge ready", as for a quiet note.
   - Push "Note ready" with it.
2. **Hear "we paid"** (Vikram, the solo GP).
   - A reply in the chase's thread that says it was paid, sent or wired in the past ("paid it last Friday", "wired on Monday") should read "Peter says it was paid: check the account".
   - Write no second chase from it. Offer a short "checking on our side" note only if the money still has not shown after five working days.
   - After Sent it, drop "no touch in N days" on the heroes too. Push "call Peter" once Today says it.
3. **Passed races step down** (the solo GP, Aditi).
   - A race whose deadline passed leads Today at most two working days, then moves to a row.
   - Every review push that names it says "their deadline passed", hero or not.
   - A race row never repeats a step marked sent ("next: send term sheet markup").
4. **A met pitch stays met, an old hold ages** (Rohan).
   - Keep `met_on` with the pitch in Home, so a narrow pulse never turns Paysa Labs back into "book a call".
   - "Until next week", read on 21 Oct, ages after Fri 30 Oct: "Vaultline's allocation was held until w/c 26 Oct: ask Tanvi if it still stands".
5. **Follow up a quiet partner** (Meera).
   - Five working days after the note to a partner with no answer, the waiting rows offer one short nudge, or name the note under Monday's partner meeting.
   - Fire "no word from Aditi yet, decide today" whenever the note named a decision due today, whatever day it went.
   - Keep "Drafts are under Ready for you" on the late-work line when they are.

## Reaching 10: tests on the same replay

1. **A deferred nudge stays.**
   - Setup: Tara, Sent it Thu 22 10:00; Aditi replies Mon 26 15:00 "Let me think about these and come back to you."
   - Pass: the nudge written Mon 2 Nov is still under Ready for you on Tue 3 and Wed 4 Nov, as one draft for three asks, and the pushes end "Note ready".
   - Today: written 06:28, pruned 07:28; rendered Tue 3 Nov, only Close ask.
2. **"We paid" is not chased.**
   - Setup: Vikram, Sent it Thu 22; Peter writes Mon 26 11:00 in the thread "We paid it last Friday. Please check with your bank."
   - Pass: Mon 26 to Mon 2 Nov, no second note; the row says Peter says it was paid and asks Vikram to check.
   - Today: Mon 2 Nov "Peter replied on 26 Oct, still unpaid. Second note ready", asking when to expect it.
3. **Heroes are true after Sent it.**
   - Setup: Vikram, render Fri 23 08:40, Sent it on the chase hero.
   - Pass: neither the Today hero nor the LPs hero says "no touch in 96 days".
   - Today: both do, beside "Marked sent 23 Oct".
4. **A passed race steps down.**
   - Setup: solo GP, no taps, Fri 6 to Mon 23 Nov.
   - Pass: the passed Atlas race is the hero on two working days at most, and every push naming it says "passed" (Thu 12 Nov 15:24 included).
   - Today: hero on 17 mornings; Thu 12 push unflagged.
5. **Sent it ends the old step everywhere.**
   - Setup: Aditi, Sent it on the markup Fri 23 10:00.
   - Pass: no line on any run to Mon 23 Nov says "next: send term sheet markup".
   - Today: the race row on Thu 19 15:24, Fri 20 and Sun 22 Nov.
6. **Met stays met.**
   - Setup: Rohan, no taps, to Fri 6 Nov.
   - Pass: no run shows "Paysa Labs is back ... book a call".
   - Today: the first pulse after each morning, Fri 30 Oct to Thu 5 Nov.
7. **A hold ages.**
   - Setup: Rohan, no taps.
   - Pass: from Mon 2 Nov no push says "Vaultline: the round is oversubscribed" as news; any line says the hold was for w/c 26 Oct.
   - Today: pushed Wed 4, 11 and 18 Nov.
8. **A quiet partner is followed up** (for Meera to stay at 10).
   - Setup: Meera, Sent it on the note Thu 22 10:00, Aditi silent.
   - Pass: by Fri 30 Oct the Rivulet and Trellis rows offer one short nudge to Aditi, or Monday's partner card names the note.
   - Today: "Asked Aditi on 22 Oct" to Mon 23 Nov, and nothing else.
9. **The late line says where its drafts are** (a suggestion).
   - Setup: Aditi, no taps, Thu 5 to Mon 23 Nov.
   - Pass: "3 promises more than a week late ..." ends "Drafts are under Ready for you" while they are, and its push names the oldest.
   - Today: neither, from Thu 5 Nov.
10. **A date Instinct set is known as Instinct's** (a suggestion, engine side).
    - Setup: Tara, no taps; the Mon 26 redate puts "by Wed 28 Oct" in the CFO email.
    - Pass: the engine records that date as its own suggestion (not from free text in `context`), so Thu 29 moves it two working days out.
    - Today: the replay keeps "by Wed 28 Oct ... I am sorry this is late" (Demo only here, but the engine depends on Claude writing the marker).
