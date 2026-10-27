<!-- VC panel, round twelve. Written by one Claude agent playing all seven personas on a clean clone at 947db4c (0.7.5). Simulated: no real investor took part. Saved by the main session. -->

# Instinct for VCs: VC panel, round twelve

**This is a simulated panel. No real investor took part.** One Claude agent played all seven: six people at the fictional Quillwater Ventures (Aditi Rao, Partner; Kabir Shah, Principal; Meera Iyer, Associate; Rohan Das, Analyst; Tara Menon, Head of Platform; Vikram Nair, CFO and IR) and a solo GP running a $30M fund alone.

## What I read and ran

- **Read, in order:**
  - my round-eleven report (`evals/reports/council/vc-panel-r11.md`), whose "Reaching 9.5 or 10" tests are this round's bar;
  - "Round twelve: what changed" in `BUILD_LOG.md`;
  - `git diff be80587 947db4c` for `engine/`, `skills/`, `shared/`, `home/`, `evals/demo.py`, `evals/replay.py` and `evals/home_qa.py` (26 files, 1,335 lines added, 160 removed);
  - the seven packs from `python3 evals/panel_pack.py --out DIR/evals/runs/council/briefs-r12`.
- **Fresh clone** at 947db4c (0.7.5) in my own folder. The runner rewrote `evals/scorecard.md`. I ran `git checkout -- .` at the end: the clone has 0 changes.
- **Suites:**
  - `python3 evals/runner.py`: 193 of 193 pass, 7 Claude-run scores skipped in a clean clone, 254 s.
  - `--suite round12`: 19 of 19 (34 s). `--suite guard`: 718 of 718 (17 s).
  - `design_lint.py`: 0 violations in 219 CSS rules.
  - `home_qa.py --out DIR/evals/runs/council/home-r12`: 545 of 545, `page_sha256` a8cee518ad48, matching `home/index.html`.
- **My own replays,** all with `replay._replay_windowed` and its hooks (each run reads only its own window). Observe-only hooks keep Home at chosen hours for rendering.
  - **All seven, no taps,** Thu 22 Oct to Mon 23 Nov (340 runs each): hero, every Today row, pushes, drafts, Pipeline and pitches.
  - **Money,** Vikram and the solo GP, to Mon 23 Nov, 16 variants each:
    - "Sent it" on the chase Thu 22 10:00, with and without the sent email in mail;
    - Peter's in-thread reply Mon 26 ("The wire for the 5 Oct call goes out on Wednesday"), with and without mail, then unpaid, then the follow-up sent, then paid Thu 29;
    - "AGM in December" (other thread); "Could you send the Fund II Q3 report" (other thread); an AGM question inside the chase thread;
    - a reply with no date ("passed this to our treasury team"); "We will wire the amount next week";
    - the second note sent Thu 29 with no reply; a reply after it was written; a reply after it was sent;
    - the wire paid Thu 5 Nov, with and without the chase in mail.
  - **Asks,** Tara, to Mon 23 Nov, 12 variants: Sent it and quiet; the nudge sent; "Ask the team instead" on Nimbus Thu 29 10:00 (note written at the next check, sent 15:00, its nudge sent Thu 5 Nov); "Aditi said yes: ask the team" on Orbit; a reply naming all three; the partial reply ("Yes on Orbit Treasury. Let me think about the other two."), alone and followed by a second reply Wed 4 Nov; a reply naming none ("Let me think about these and come back to you."); the Kestrel board pack email; Aditi's intro email; the nudge sent, then a reply Mon 2 Nov.
  - **Pipeline,** Meera, to Mon 23 Nov: met logs Thu 19:05; plus Halo's step Fri 23 10:00; plus Trellis's step Mon 26 and saved again Wed 28 10:00. **The note to Aditi:** Sent it Thu 22 10:00, alone and with both drafts it names sent Fri 23.
  - **Answered,** to Mon 23 Nov: Aditi and the solo GP "Sent it" on the markup Fri 23; Rohan and the solo GP "Sent it" on every pitch reply Thu 22; Kabir "Sent it" on his checklist Mon 26; Aditi "Sent it" on the Arjun intro.
  - The replay has no Claude, so a hook plays pulse step 3: a note tapped in Home is written at the next check under the tap's id, and Pipeline steps reach the CRM at the next run.
  - **A drafts-command check.** The stock replay merges new drafts into the Home from before the build, and the demo's drafts carry no `first_made_at`. `instinct drafts` does neither. So I also ran Solo, Rohan, Meera, Aditi and the Meera and answered variants on a copy of `_replay_windowed`, in my folder, whose only change is to merge drafts as `drafts` does. Two stock-replay findings were harness only (six call replies re-slotted to Mon 23 Nov for the solo GP; two notes to Aditi at once on Mon 9 Nov). Findings that hold on both are scored.
  - **39 replayed Homes rendered** in the real `home/index.html` with the QA harness (`QA.open` with `snap`, `state`, `when`, `member`). Taps I made:
    - Sent it on Vikram's second-note hero (Thu 29) and on his chase row (Thu 22), and on Kabir's hero (Mon 26);
    - Got it on Kabir's "Rohan Das owes you" row;
    - "Aditi said yes: ask the team" on Orbit and Close ask on Kestrel (Tara);
    - Done on Aditi's paragraph row;
    - a met log Save with a step (Meera, Rivulet) and the folded met logs, Show them and Save (Aditi, Beacon);
    - Monday's prep from Friday's Today (Aditi, Meera);
    - a Pipeline step saved again (Meera, Trellis), read at 10:05 and 11:00.
- **Drafts in the replay come from `evals/demo.py`, not Claude.** "Demo only" marks wording that only the demo gets wrong; it is not scored.
- No Claude-run eval on 0.7.5 was in the repo when this panel finished, so none is cited.

## In short

- **Round twelve meets six of my nine round-eleven tests in full and three in part. None is missed.**
  - **A reply is not payment.** After Peter writes "The wire goes out on Wednesday", Thu 29 reads "Peter said it would go on 28 Oct, still unpaid. Second note ready", for Vikram and the solo GP. Dateless replies, "next week" and late replies are all followed up.
  - **Only a real reply counts.** The AGM email and the Kestrel board pack no longer stop anything.
  - **A partial reply keeps the rest.** The nudge thanks Aditi for Orbit and asks about Kestrel and Nimbus only.
  - **A tap narrows the nudge at the next check** (10:28, not the next morning).
  - **Late promises never go silent.** Aditi's four late founder promises are on Today every morning to Mon 23 Nov, as rows or one line, each with how late it is.
  - **Page words age well.** No Pipeline row says "by" a past date, folded replies keep their count by kind, and folded deal facts name the deal.
  - **Introductions ask nothing of the founder** in front of Raj.
  - **Old pitch replies leave** after a week (on the drafts-command replay).
- **What still costs points shows in weeks two to four:**
  - **Money misses a week.** The weekly money push drifts from Wednesday to Thursday to Friday, then skips a whole week, in 6 of 7 Vikram variants. The solo GP's $60K call is never pushed in 32 days.
  - **Some replies are still misread:**
    - an LP email that only says "Fund II" counts as Peter's reply;
    - a "let me think" reply ends Tara's loop for four weeks;
    - the partial-reply nudge is pushed as "no reply since 22 Oct".
  - **Passed dates still read as live:**
    - the solo GP's hero says "Another fund is moving" for a deadline that passed;
    - review and digest pushes name passed races;
    - Meera's new note to Aditi treats Monsoon Arc's deadline as "Instinct's suggestion".
  - **Things that left come back.** A call reply pruned on day 8 is rewritten as new the same morning. Monday's digest revives three-week-old pitches, so Rohan's Sutra reads "book a call" again.
- **Scores: average 9.5** (round eleven: 9.29). Kabir reaches 10 and Vikram 9.5. Aditi, Meera, Rohan and Tara hold at 9.5. The solo GP holds at 9.

### Round-eleven tests on this build

| Round-eleven test | Verdict | Evidence |
|---|---|---|
| 1. A reply is not payment | Met | Vikram, Sent it Thu 22, Peter's reply Mon 26 11:00, unpaid. Mon 26 11:20: "Peter replied on 26 Oct, saying it goes on 28 Oct". Thu 29 06:20: "Peter said it would go on 28 Oct, still unpaid. Second note ready: check the amount, then send it", and its "Before you send" reads "They said the money would go on 28 Oct and it has not come". Same with the chase in mail, and for the solo GP's $60K. Follow-up sent Thu 29: "call Peter" from Thu 5 Nov, no third note |
| 2. Only a real reply counts | Met | Vikram, "AGM in December" Tue 27: Thu 29 06:20 drafts the second note; no line says "Peter replied". Tara, Kestrel board pack Tue 27: the Thu 29 nudge names all three asks (rendered). But see Vikram: an email asking for the "Fund II Q3 report" still counts as a reply |
| 3. A partial reply keeps the rest | Partly | Met: Thu 29 06:28 nudge for Kestrel and Nimbus only, "Thanks on Orbit Treasury"; Portfolio rows say "Aditi answered on Orbit Treasury on 26 Oct, not this one"; still waiting on Tue 3 Nov. Not met: Today's "Aditi replied ... read it" rows link only the founder update. Only Portfolio has "The reply" |
| 4. Late founder promises stay | Partly | Met: Aditi, no taps, Fri 23 Oct to Mon 23 Nov. The deck, vote outcome, markup and Arjun intro are on Today every morning, as rows or in "3 promises more than a week late: send the term sheet markup (17 days late); ...". Fri 23 09:24 keeps the race, and no row is empty. Not met: Fri 23 11:24, the Arjun row again reads only "due 20 Oct, 3 days late" |
| 5. A nudge narrows within the hour | Met | "Ask the team instead" on Nimbus Thu 29 10:00. At 10:28 the nudge is rewritten: "Nimbus Collect moved on since this nudge was written: it now asks about Kestrel Pay and Orbit Treasury only", and the body names those two (rendered 10:30). Thu 5 Nov 06:28 push: "Still open: Nimbus Collect: nudge the team, no reply since 29 Oct. Note ready" |
| 6. Page words age well | Partly | Met: rendered Mon 9 Nov, no Pipeline row says "by" a past date (0 of 37 Aditi, 0 of 13 Meera, 0 of 6 Kabir; "was due" instead). Folded replies read "5 asks for more, 12 kind passes. Oldest pitch first". Kabir Mon 26: "Cobalt AA: next step was due 15 Oct." Partly: Sutra keeps "you already write to them" on every run to Thu 5 Nov. After the pitch ages off, Monday's digest (Mon 9 Nov 07:25) brings it back as "book a call" |
| 7. Money reaches the phone and stays true after a tap | Met as written | No taps: the call is pushed Wed 28 Oct and Thu 5 Nov. Thu 29 07:00, Sent it on the second-note hero: "Marked sent 29 Oct: the next check updates this line". Paid Thu 5 Nov: Peregrine's last touch reads 15 days, never "no touch". But past Mon 9 Nov, and in other variants, a hero week goes with no push (see Vikram) |
| 8. Introductions ask nothing of the founder (suggestion) | Met | Aditi and the solo GP: the Arjun and Raj introduction, Thu 22 and its Fri 23 refresh, has no "Could you also" line; 0 owed entries carry both `cc` and `they_owe` |
| 9. Old pitch replies (suggestion) | Met | Solo GP, no taps, Mon 9 Nov (drafts-command replay): Ready for you holds no pitch reply. On the stock replay six call replies are re-slotted to Mon 23 Nov, but only because the replay's drafts carry no `first_made_at`. One real gap remains (see Meera and Rohan) |

## Scores

| Persona | Level | R11 | R12 | Why, in one line |
|---|---|---|---|---|
| Aditi Rao | Partner | 9.5 | 9.5 | Late promises stay visible for a month and the intro asks nothing of Arjun. Left: one Friday pulse still drops the race, and "Next step: Send term sheet markup" returns after Sent it. |
| Kabir Shah | Principal | 9.5 | 10 | Both of his round-eleven items pass for four weeks, and Sent it and Got it work on the page. What is left is cosmetic. |
| Meera Iyer | Associate | 9.5 | 9.5 | Pipeline words are true and the loop holds to Mon 23 Nov. Left: the new note to Aditi redates Monsoon Arc's deadline as "Instinct's suggestion", and an old reply is reborn and never says it is late. |
| Rohan Das | Analyst | 9.5 | 9.5 | Folded replies keep their counts and answered pitches stay answered. Left: Monday's digest brings back three-week-old pitches as new ("book a call" for a founder he writes to). |
| Tara Menon | Platform | 9.5 | 9.5 | Only real replies count, a partial reply keeps the rest, and a tap narrows the nudge within the hour. Left: the push still says "no reply", Today does not link the reply, and a "let me think" reply ends the loop. |
| Vikram Nair | CFO and IR | 9 | 9.5 | A reply that names a day is followed after it, and every money variant reaches a second note, a call or the wire. Left: a "Fund II" email counts as Peter's reply, and the weekly money push skips a week. |
| Solo GP | $30M, alone | 9 | 9 | Money and folded replies hold. Left: "Another fund is moving" on a passed deadline, and the $60K call never reaches her phone. |

Average 9.5 (round eleven: 9.29); Quillwater's six 9.58. Two up half a point, five held, none down.

## Each persona

### Aditi Rao, Partner (9.5, held)

Better since round eleven:
- Late promises stay, no taps, every morning to Mon 23 Nov:
  - Mon 2 Nov: "2 promises more than a week late: intro Arjun to Raj Malhotra at Fable Bank (13 days late); share the co-op bank partnership deck (10 days late). Drafts are under Ready for you", with the markup as the hero and the vote outcome as a row;
  - Mon 9 Nov: "3 promises more than a week late: send the term sheet markup (17 days late); share the co-op bank partnership deck (17 days late); share the partner vote outcome (14 days late)", and the Arjun intro on its own row (20 days late).
- Rendered Mon 9 Nov, Ready for you says how late each draft is: "To Ishaan Verma, 17 days late", "To Mohan Kulkarni, 17 days late", "To Varun Khanna, 14 days late".
- Fri 23 09:24: the Arjun row keeps "Two other funds with offers, decide by 31 Oct", and no row has an empty detail.
- The Arjun and Raj introduction asks nothing of Arjun, on Thu 22 and in Friday's refresh.
- Mon 9 Nov: "Vikram Nair owes you: Q3 LP letter draft ... It may wait on yours: write the portfolio highlights paragraph, 14 days late".
- Friday sees Monday (rendered Fri 23 07:00): "Monday: 10:00 Monday partner meeting" opens the card. It leads "Decide on Gravity Payouts by 31 Oct, and 10 more", and Sable comes last: "Deadline 23 Oct passes before this meeting: decide by then".
- Taps: Done on the paragraph row closes the row and the promise. The folded met logs ("Log 3 meetings from 23 Oct, 22 Oct") open three forms, and Save on Beacon writes the log.
- 25 pushes to Mon 9 Nov (39 to Mon 23 Nov): none old news, none cut, at most four a day.

Still costs time or trust:
- Fri 23 11:24: the Arjun row reads "Promised to Arjun Khurana (Gravity Payouts), due 20 Oct, 3 days late", with no race.
  - The engine cut the race phrase because Gravity's own race row was on the list.
  - Then that row was bumped to put "Review the board deck" back.
  - So the race shows nowhere. 10:24 and 12:24 are right.
- After Sent it on the markup (Fri 23 10:00), from Fri 13 Nov to Mon 23 Nov the hero reads "Decide on Atlas Settlement | Term sheet out for 27 days, usually 10. Next step: Send term sheet markup". It repeats the CRM's old step.
- The Thursday review push names a race whose deadline has passed: "Review ready: Atlas Settlement: term sheet from Bluepeak Partners" (Thu 12 and Thu 19 Nov; Atlas decided by 5 Nov).
- The push "3 promises more than a week late" (Fri 6, Wed 11, Wed 18 Nov) names none of them.

For 10: the race shows once even when a row is bumped; Sent it closes the CRM's old step; a review push says when a race's date has passed.

### Kabir Shah, Principal (10, up from 9.5)

Better:
- The folded deal fact names its deal: Mon 26 and Fri 30 06:28, "Forward the Cobalt AA notes | ... Cobalt AA: next step was due 15 Oct."
- Rendered Mon 9 Nov, Pipeline: 0 of 6 rows say "by" a past date; 5 say "was due" (for example "Next: Cohort analysis review, was due 26 Oct").
- Mon 26 08:00, rendered: Sent it on the hero "Share the diligence checklist" marks the draft, the promise and the row, and "Send the cohort analysis questions" steps up.
- Got it on "Rohan Das owes you: market map of AA players" marks the promise received, and the row leaves.
- Four weeks with no taps: his four late promises stay on Today, each with how long its deal has sat ("Vertex Card Issuing: 48 days in due diligence (usually 21)").
- On Friday, Today lists Monday's partner meeting with its prep. 20 pushes to Mon 9 Nov (32 to Mon 23 Nov), no old news.

Small, not scored:
- Pipeline rows say the date twice ("Next: ..., was due 26 Oct" and a "Next step was due 26 Oct" chip).
- The Thursday review push reads "Review ready: Lumen Ledger: two other funds in diligence" four weeks running.
- After Sent it, the stepped-up hero's kicker reads "You promised · Overdue" until the next check.
- Demo only: "Could you also market map of AA players?" in the Cobalt notes draft.

To stay at 10: these stay small, and nothing above regresses.

### Meera Iyer, Associate (9.5, held)

Better:
- Rendered Mon 9 Nov, Pipeline: 0 of 13 rows say "by" a past date; all 13 say "was due".
- The Pipeline loop holds to Mon 23 Nov:
  - met logs at Thu 19:05 give "1 meeting to log and 2 next steps to add";
  - Halo's step, saved Fri 23 10:00, is in the CRM at 10:29;
  - Trellis's step, saved again Wed 28 10:00, reads "Term sheet draft to Neha by 06 Nov (saving to your CRM at the next check)" at 10:05 and "Next: Term sheet draft to Neha by 06 Nov" at 11:00 (both rendered);
  - Rivulet's step request lasts to Mon 23 Nov;
  - a met log saved from Ready for you writes its step and its stage (rendered Fri 23, Rivulet).
- The new note to Aditi, Thu 22 06:29:
  - one short note lists "Rivulet Payments: feedback after the partner meeting, for Omkar, was due Mon 19 Oct", Trellis's pricing view and "Sable Fraud AI: ... decide by Fri 23 Oct";
  - the rows it names say "Note to Aditi ready, under Ready for you";
  - once both drafts are sent, no new note comes.
- Friday sees Monday (rendered): her card says Sable's deadline "passes before this meeting: decide by then with Aditi".

Still costs:
- Mon 26 06:29: the morning "redates" the note to Aditi. Its row reads "It said 'by Fri 23 Oct', which has passed: the next working day is in its place, as Instinct's suggestion". That date was Monsoon Arc's deadline for Sable, not Meera's or Instinct's. (The demo's body then says "decide Tue 27 Oct": Demo only.)
- After Sent it on the note (Thu 22 10:00), with the two drafts unsent:
  - a fresh, identical note to Aditi is drafted Tue 27 Oct, Mon 2, Fri 6, Thu 12 and Wed 18 Nov;
  - none says it follows up her 22 Oct note.
- The Harborline reply (score 93, written Thu 22) never says it is late:
  - on Fri 30 (day 8) the build drops it, but the same morning lists it for new times, so it is written again as new;
  - it is then re-slotted every morning to Fri 6 Nov (drafts-command replay).
- Ember Credit's 21 Oct meeting leaves the prompts on Thu 29 without being logged ("1 next step to add").
- Demo only: "Could you also give data room access?"

For 10: a rival's deadline is never Instinct's date; a reply that leaves stays gone; a second note to a partner says it follows up.

### Rohan Das, Analyst (9.5, held)

Better:
- Sent it on all 19 pitch replies Thu 22 10:00: none is drafted again to Mon 23 Nov.
- Folded replies keep their count (drafts-command replay, rendered Thu 29): "17 replies to pitches, ready to send / 5 asks for more, 12 kind passes. Oldest pitch first".
- Sutra reads "you already write to them" on every run from Thu 22 to Thu 5 Nov.
- 19 pushes to Mon 9 Nov: none cut, no old news.

Still costs:
- Monday's digest brings old pitches back as new:
  - Fri 6 Nov the 14-day pitch list empties;
  - the Mon 9 Nov 07:25 digest reads 120 days of mail and adds 25 pitches back with today's date, though they arrived 17 to 21 Oct;
  - rendered Mon 9 Nov 08:00, "Inbound worth a look" holds five, including "Sutra Compliance: Score 96: book a call" (he writes to them) and "Paysa Labs is back ... book a call" (he met them on 22 Oct).
  - Partly harness: the replay hands the digest every pitch in its window, and the digest's read is metadata only.
  - But the engine keeps each pitch's arrival date and still lists it as new, and it looks for meetings only 14 days back.
- The call replies to Tessera Settle and Rupee Rails are re-slotted every morning from Fri 23 Oct to Fri 6 Nov, and written again as new on day 8.
- "Still open: Vaultline: the round is oversubscribed" is pushed Wed 28 Oct, 4, 11 and 18 Nov. Tanvi held the allocation "until next week" on 21 Oct.

For 10: a pitch in touch stays in touch whatever a wide read brings; an old pitch never returns as new; a hold "until next week" ages.

### Tara Menon, Head of Platform (9.5, held)

Better:
- The Kestrel board pack email (Tue 27, another thread) is not a reply: the Thu 29 nudge names all three asks (rendered).
- The partial reply (Mon 26 15:00, "Yes on Orbit Treasury. Let me think about the other two."):
  - Orbit reads "Aditi replied on 26 Oct: read it, then answer here";
  - Thu 29 06:28 writes a nudge for Kestrel and Nimbus only, "Thanks on Orbit Treasury. And Kestrel Pay: ...";
  - Portfolio rows read "Nudge to Aditi ready: Aditi answered on Orbit Treasury on 26 Oct, not this one", and Orbit's has "The reply";
  - her second reply (Wed 4 Nov 12:00) answers the other two at 12:28.
- "Ask the team instead" on Nimbus Thu 29 10:00:
  - at 10:28 the nudge asks about Kestrel and Orbit only, and Nimbus reads "Team note ready" (rendered 10:30);
  - the team note sent at 15:00 reads "Asked the team on 29 Oct";
  - Thu 5 Nov the team nudge is written, and its push ends "Note ready".
- "Aditi said yes" on Orbit, and Aditi's intro email Mon 26, each take their ask out of the nudge at the next check.
- The nudge sent Thu 29, still quiet: Thu 5 Nov "Nudged Aditi on 29 Oct, still no reply: ask the team instead" (Nimbus) and "raise it with Aditi directly" (Orbit, Kestrel).
- Rendered taps: "Aditi said yes: ask the team" shows "Team note coming at the next check"; Close ask on Kestrel removes it, and the Portfolio hero counts "1 more open".

Still costs:
- After the partial reply, the push says what the rows never say. Thu 29: "Nudge Aditi on Kestrel Pay and Nimbus Collect: no reply since 22 Oct. Note ready". Wed 4, 11 and 18 Nov: "Still open: ... no reply since 22 Oct".
- On Today, "Aditi replied on 26 Oct: read it" links only the founder update. Only Portfolio's row links the reply.
- A reply that defers ends the loop. Aditi's "Let me think about these and come back to you" (Mon 26) marks all three replied. No nudge and no push follow to Mon 23 Nov.
- No taps: "Still open: Intro two CFO candidates" is pushed two or three mornings in a row (Wed 4 to Thu 5, Wed 11 to Fri 13, Wed 18 to Thu 19 Nov).
- Her CFO draft (Demo only): from Wed 28 Oct it promises "I will introduce you Thu 29 Oct". The demo dropped "by", so no new date comes. But the build's note still says "the next working day is in its place" on Mon 9 Nov.

For 10: a reply that defers is nudged after five working days; no line or push says "no reply" after she answered; every replied row links the reply.

### Vikram Nair, CFO and IR (9.5, up from 9)

Better:
- Peter's reply in the thread (Mon 26 11:00, "The wire for the 5 Oct call goes out on Wednesday"), unpaid:
  - Mon 26 11:20: "chased Peter on 22 Oct, Peter replied on 26 Oct, saying it goes on 28 Oct";
  - Thu 29 06:20: "Peter said it would go on 28 Oct, still unpaid. Second note ready: check the amount, then send it";
  - the row's "Before you send": "They said the money would go on 28 Oct and it has not come: a short follow-up";
  - the follow-up sent Thu 29: "chased Peter again on 29 Oct", then "no reply in 5 working days: call Peter" from Thu 5 Nov to Mon 23 Nov, and no third note.
- Every other reply ends right:
  - "AGM in December" (other thread): no "Peter replied", and the second note comes Thu 29;
  - an AGM question in the chase thread, or "passed this to our treasury team": "Peter replied", then five working days later "still unpaid. Second note ready";
  - "We will wire the amount next week": "saying it goes on 06 Nov", followed up Mon 9 Nov;
  - "the wire goes out on 4 Nov", after the second note was written: the note is withdrawn at 13:20 and written again Thu 5 Nov. The same reply after the note was sent: Thu 5 Nov "still unpaid: call Peter".
- Paid Thu 5 Nov (with or without the chase in mail): the line leaves Fri 6, and the LPs tab gives Peregrine's last touch as 15 days.
- Thu 29 07:00, rendered: Sent it on the second-note hero gives "Marked sent 29 Oct: the next check updates this line", with no "Second note ready" anywhere on Today.
- No taps: the call leads Today every morning from Fri 23 Oct, and is pushed Wed 28 Oct and Thu 5 Nov ("Peregrine Trust: owes $150K on a capital call. Draft ready").

Still costs:
- "Could you send the Fund II Q3 report when it is ready?" (other thread, Tue 27) counts as Peter's reply:
  - the line reads "Peter replied on 27 Oct", which is false, and the second note waits to Tue 3 Nov;
  - "fund" is one of the words that mark an email as about the call.
- The weekly money push walks from Wednesday to Thursday to Friday, then skips a week:
  - with no taps, 16 to 20 Nov: hero five mornings, no push;
  - after Sent it, 9 to 13 Nov; after the Wednesday reply, 2 to 6 Nov; after the AGM email, 9 to 13 Nov;
  - only 1 of 7 variants has a money push in every week it leads.
- Thu 22 08:00, rendered: after Sent it on the chase row, the row still says "no touch in 95 days" beside "Marked sent 22 Oct", and the LPs tab still offers "Draft a note", until the next check.
- Demo only: "Add it before you send" in the fee offset draft, for four weeks.

For 10: only money talk counts as an answer; the call reaches his phone in every calendar week it leads; the LPs tab is true within the hour after Sent it.

### Solo GP (9, held)

Better:
- Money as for Vikram, in all 16 variants: Thu 29 "Peter said it would go on 28 Oct, still unpaid. Second note ready"; the AGM email is not a reply; "call Peter" after two notes; paid, the line leaves.
- Old pitch replies leave (drafts-command replay):
  - Fri 30 Oct: "8 replies to pitches, ready to send / 2 calls, 2 asks for more, 4 kind passes. Oldest pitch first";
  - Mon 9 Nov: no pitch reply under Ready for you.
- The Arjun and Raj introduction asks nothing of Arjun.
- 24 pushes to Mon 9 Nov, no old news.

Still costs:
- Fri 6 to Thu 12 Nov, the hero reads "Another fund is moving | Atlas Settlement: term sheet from Bluepeak Partners | Their deadline 05 Nov has passed."
- Mon 16 Nov 07:24, the digest pushes "Atlas Settlement: term sheet from Bluepeak Partners, their deadline passed 05 Nov". Home said so ten days earlier.
- The $60K call never reaches her phone:
  - it is on Today all 23 mornings in every variant, never the hero;
  - so it is never pushed in 32 days, not even when the second note is ready.
- The Paysa Labs and Lattice KYC call replies are written again as new on day 8 and re-slotted daily to Fri 6 Nov.
- Tue 10 Nov, after the digest: "Paysa Labs is back ... book a call" returns.
- Demo only: "Separately, my introduction to Arjun is on its way today" stays in her Nimbus note to Raj to Sat 21 Nov.

For 9.5: a passed deadline is not "moving"; an unpaid call reaches her phone at least weekly; old pitches do not come back.

## Top five changes

1. **Replies that keep the loop alive** (Tara, Vikram).
   - An LP email is an answer only in the chase's thread or when it speaks of this call's money. "Fund II" alone is not enough.
   - A reply that defers ("let me think", "I will come back to you") gets a nudge after five working days, as a dateless LP reply already does.
   - After a partial reply, pushes say what the rows say: "Aditi answered on Orbit; Kestrel and Nimbus still wait. Note ready". Never "no reply".
   - Today's "Aditi replied" rows link the reply, as Portfolio's do.
2. **Money every calendar week** (Vikram, the solo GP).
   - Push the leading call once in each Monday-to-Friday week, not "not in the last seven days", so it cannot skip a week.
   - Give a solo GP's unpaid call a weekly push too (or let it lead after two weeks), and push "Second note ready" when it is written.
   - Within the hour after Sent it, drop "no touch in 95 days" and the LPs tab's "Draft a note".
3. **A passed date is never news** (the solo GP, Aditi, Meera, Rohan).
   - No "Another fund is moving" kicker once the deadline has passed.
   - The Thursday review push and the Monday digest say "deadline passed" or lead with something live.
   - A rival's deadline in a draft is never redated as Instinct's suggestion. A note whose decision date has passed is rewritten without that decision.
   - A hold the founder set "until next week" ages ("Vaultline's allocation was held until w/c 26 Oct").
4. **What left stays gone** (Meera, Rohan, the solo GP).
   - Do not list a reply for new times on the morning the build drops it, so it is never written again as new.
   - A wide read never brings back a pitch that arrived more than 14 days ago. Keep "in touch" and "met" with the pitch.
   - A second note to a partner after one was sent says it follows up ("Following up on my note of 22 Oct").
5. **Small trims and repeats** (Aditi, Meera, Tara).
   - Cut a race phrase from a promise row only after the last bump, so the race always shows once (Fri 23 11:24).
   - After Sent it, never repeat the CRM's old step as the next step ("Send term sheet markup").
   - An unlogged meeting keeps "1 meeting to log" until logged (Ember Credit).
   - Do not push the same "Still open" line on two mornings in a row.

## Reaching 9.5 or 10: tests on the same replay

1. **A fund word is not a reply.**
   - Setup: Vikram, Sent it on the chase Thu 22 10:00. Peter emails "Fund II Q3 report" (another thread) Tue 27 09:00: "Could you send the Fund II Q3 report when it is ready?"
   - Pass: Thu 29 06:20 has the second note ready, and no line says "Peter replied".
   - Today: "Peter replied on 27 Oct"; the second note waits to Tue 3 Nov.
2. **A reply that defers is followed.**
   - Setup: Tara, Sent it Thu 22. Aditi replies in the thread Mon 26 15:00: "Let me think about these and come back to you."
   - Pass: by Tue 3 Nov a nudge is ready for the three asks, or each row says she will come back and offers one.
   - Today: no nudge and no push to Mon 23 Nov.
3. **No "no reply" after a partial reply.**
   - Setup: Tara's partial reply Mon 26 15:00.
   - Pass: the Thu 29 06:28 push and every "Still open" repeat say she answered on Orbit, and Today's Orbit row links the reply.
   - Today: "Nudge Aditi on Kestrel Pay and Nimbus Collect: no reply since 22 Oct. Note ready", and the reply is linked on Portfolio only.
4. **Money every week, for one person or a team.**
   - Setup: Vikram's no-tap, Sent it, Wednesday-reply and AGM variants, to Mon 23 Nov.
   - Pass: every Monday-to-Friday week with three or more hero mornings has a money push.
   - Today: one such week has none in 6 of 7 variants (with no taps: 16 to 20 Nov).
   - Solo GP: pass when the $60K call is pushed at least once in each week it stays unpaid. Today: 0 pushes in 32 days, in 17 variants.
5. **Passed is not moving.**
   - Solo GP, no taps, Fri 6 to Thu 12 Nov. Pass: no hero kicker "Another fund is moving" on a passed deadline, and no push on Mon 16 Nov naming that deadline as news.
   - Aditi, Thu 12 and Thu 19 Nov. Pass: the review push does not lead with Atlas's passed race unflagged.
6. **A rival's date is never Instinct's.**
   - Setup: Meera, no taps, Mon 26 Oct 06:29.
   - Pass: the note to Aditi drops Sable's passed decision, or says it passed. No line calls Monsoon Arc's deadline "Instinct's suggestion".
   - Today: "It said 'by Fri 23 Oct', which has passed: the next working day is in its place, as Instinct's suggestion".
7. **Gone means gone.**
   - Setup: merge drafts as `instinct drafts` does (or check a real run).
   - Pass: Meera's Harborline reply (written Thu 22) and Rohan's Tessera and Rupee Rails replies leave by Fri 30 and are not written again.
   - Rohan, Mon 9 Nov 08:00 (after the digest). Pass: no pitch that arrived 17 to 21 Oct is on "Inbound worth a look", Sutra keeps "you already write to them", and Paysa Labs never reads "book a call".
8. **The Friday trim keeps the race once.**
   - Aditi, no taps, Fri 23 11:24. Pass: the Arjun row, or a Gravity row, says "Two other funds with offers, decide by 31 Oct".
   - Today: neither does.
9. **Sent it ends the old step.**
   - Setup: Aditi, Sent it on the markup Fri 23 10:00.
   - Pass: from Fri 13 Nov no hero or row says "Next step: Send term sheet markup", or it says the markup went on 23 Oct and the CRM step needs updating.
   - Today: it repeats to Mon 23 Nov.
10. **A second note to a partner says it follows up** (a suggestion).
    - Setup: Meera, Sent it on the note to Aditi Thu 22 10:00; the drafts stay unsent.
    - Pass: the next note (Tue 27 or later) refers to the 22 Oct note, or waits five working days for her answer.
    - Today: an identical fresh note on Tue 27 Oct, Mon 2, Fri 6, Thu 12 and Wed 18 Nov.
