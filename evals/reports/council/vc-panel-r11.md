<!-- VC panel, round eleven. Written by one Claude agent playing all seven personas on a clean clone at be80587 (0.7.4). Simulated: no real investor took part. -->

# Instinct for VCs: VC panel, round eleven

**This is a simulated panel. No real investor took part.** One Claude agent played all seven: six people at the fictional Quillwater Ventures (Aditi Rao, Partner; Kabir Shah, Principal; Meera Iyer, Associate; Rohan Das, Analyst; Tara Menon, Head of Platform; Vikram Nair, CFO and IR) and a solo GP running a $30M fund alone.

## What I read and ran

- **Read, in order:**
  - my round-ten report (`evals/reports/council/vc-panel-r10.md`), whose "Reaching 9.5 or 10" tests are this round's bar;
  - "Round eleven: what changed" in `BUILD_LOG.md`;
  - `git diff a023dd2 be80587` for `engine/`, `skills/`, `shared/`, `home/`, `evals/demo.py`, `evals/replay.py` and `evals/home_qa.py` (28 files, 1,363 lines added, 210 removed);
  - the seven packs from `python3 evals/panel_pack.py --out DIR/evals/runs/council/briefs-r11`.
- **Fresh clone** at be80587 (0.7.4) in my own folder. The runner rewrote `evals/scorecard.md`. I ran `git checkout -- .` at the end: the clone has 0 changes.
- **Suites:**
  - `python3 evals/runner.py`: 174 of 174 pass, 7 Claude-run scores skipped in a clean clone, 205 s. (`BUILD_LOG.md` says 13 are skipped; the runner skips 7.)
  - `--suite round11`: 16 of 16 (95 s). `--suite guard`: 718 of 718.
  - `design_lint.py`: 0 violations in 216 CSS rules.
  - `home_qa.py --out DIR/evals/runs/council/home-r11`: 514 of 514, `page_sha256` 6cb163f442a1, matching `home/index.html`.
- **My own replays,** all with `replay._replay_windowed` and its hooks (each run reads only its own window). Observe-only hooks read Home after every run.
  - **All seven, no taps,** Thu 22 Oct to Mon 9 Nov (200 runs each): hero, every Today row, pushes and drafts. Scans for late promises, pushes and wording.
  - **Money,** Vikram and the solo GP, to Mon 23 Nov, 12 variants each:
    - no taps;
    - "Sent it" on the chase Thu 22 10:00, with and without the sent email in mail;
    - the second note also sent Thu 29 10:00, with and without mail;
    - Peter's in-thread reply Mon 26 ("The wire goes out on Wednesday");
    - an unrelated email from Peter Tue 27 ("AGM in December");
    - a reply after the second note was written, and one after it was sent;
    - the wire paid Thu 5 Nov, with and without the chase in mail, and after a reply.
  - **Asks,** Tara, to Mon 23 Nov, 9 variants:
    - "Sent it" Thu 22 and quiet; the nudge sent Thu 29;
    - "Ask the team instead" on Nimbus, and "Aditi said yes: ask the team" on Orbit, Thu 29 10:00, each team note written at 10:28 and sent at 15:00;
    - Aditi's reply in the thread to all three asks, and a partial reply;
    - Aditi's intro email Mon 26;
    - an unrelated email from Aditi naming Kestrel Pay;
    - the nudge sent, then a reply Mon 2 Nov.
  - **Pipeline,** Meera, to Mon 23 Nov, 3 variants: met logs saved Thu 19:05 with no steps; plus Halo's step from the Pipeline tab Fri 23 10:00; plus a Trellis step Mon 26 and the same step saved again Wed 28 10:00.
  - **Answered,** to Mon 23 Nov: Aditi "Sent it" on the markup Fri 23; Rohan "Sent it" on 19 pitch replies Thu 22.
  - The replay has no Claude, so my hooks emulate pulse step 3: `pending_actions` at each run, a tapped note written as rule 1 says, and every result recorded as applied.
  - **20 replayed Homes rendered** in the real `home/index.html` with the QA harness (`QA.open` with `snap`, `state`, `when`, `member`). Taps I made:
    - Sent it on Vikram's second-note hero, Kabir's promise hero and Tara's team note;
    - Close ask on Nimbus, and "Aditi said yes: ask the team" on Orbit;
    - Done on Aditi's paragraph row;
    - a met log Save (Beacon) and the step-only form (Rivulet);
    - a Pipeline step saved again (Trellis).
- **Drafts in the replay come from `evals/demo.py`, not Claude.** "Demo only" marks wording that only the demo gets wrong; it is not scored.
- No Claude-run eval on 0.7.4 was in the repo when this panel finished, so none is cited.

## In short

- **Round eleven meets seven of my nine round-ten tests in full and two in part,** each checked on the replay and on the page:
  - **Money is remembered to Mon 23 Nov.** After "Sent it", every Peregrine line says "chased Peter on 22 Oct". There is never a first chase again and never a third. "Call Peter" comes after two quiet notes. This holds with and without the sent email in mail, for Vikram and the solo GP.
  - **No old news is pushed as news:** 0 of 141 pushes for all seven to Mon 9 Nov.
  - **Carried rows keep true words:** "Maya wrote on 21 Oct", and "Their deadline 23 Oct has passed" with no "Decision by" fragment. No fund is lowercased. On Today, no own deal says "shared by the deal team".
  - **The nudge follows its asks.** It narrows when an ask moves on. "Nudge ready" shows on the run that writes it. Repeat pushes keep "Nudge Aditi on ...". A reply in the thread stops the nudge.
  - **Answered stays answered:** 0 of 19 pitch replies and 0 markup drafts come back, to Mon 23 Nov.
  - **Small fixes hold:** a partner's own boards say "your call before anyone sources", and old met logs fold into one line.
- **What still costs points shows when people answer, or when two weeks pass:**
  - **A reply ends the loop.** After Peter writes "The wire goes out on Wednesday", the line says "Peter replied on 26 Oct" for four weeks while $150K stays unpaid. There is no second note and no "call Peter". The same happens for the solo GP's $60K and for Tara's partial reply.
  - **Some replies are not replies.** An email from Peter about the AGM counts as his reply. So does Aditi's "Kestrel Pay: board pack" email.
  - **Late founder promises leave Today after a week** once no race runs. Aditi loses three such rows by Fri 6 Nov. Only their drafts stay, under Ready for you.
  - **Page wording ages:**
    - Pipeline rows read "Next: ... by 25 Oct" on Mon 9 Nov.
    - Folded pitch replies read ". Oldest pitch first."
    - Rohan's Sutra row flips seven times between "you already write to them" and "book a call".
- **Scores: average 9.29** (round ten: 9.21). Aditi and Meera reach 9.5. Kabir, Rohan and Tara hold at 9.5. Vikram and the solo GP hold at 9: their round-ten tests pass, but this round's reply check opens a new gap in the same money loop.

### Round-ten tests on this build

| Round-ten test | Verdict | Evidence |
|---|---|---|
| 1. Money is remembered for the life of the call | Met | Vikram, Sent it Thu 22 10:00, to Mon 23 Nov, with and without the email in mail: "chased Peter on 22 Oct" from 10:20; 0 runs say "no touch"; no first chase again. Thu 29 06:20: "chased Peter on 22 Oct, no reply in 5 working days. Second note ready: check the amount, then send it". Second note sent Thu 29 10:00: "chased Peter again on 29 Oct"; from Thu 5 Nov "no reply in 5 working days: call Peter"; no third note. Same for the solo GP's $60K |
| 2. Old news is not pushed as news | Met | All seven to Mon 9 Nov: 0 of 141 pushes keyed `item:` name a signal Home showed two days or more before. No day has more than four pushes, and none is cut |
| 3. Carried signals keep true words | Met on Today | Aditi Thu 29 06:24 hero: "Intro Arjun to Raj Malhotra ... Two other funds with offers, decide by 31 Oct". Tue 3 Nov 07:24 hero is whole. Kabir Thu 29: "Maya wrote on 21 Oct: ...". Meera Wed 28 and Rohan Thu 29 keep the founder's dated words. Meera Fri 30 07:29: "Their deadline 23 Oct has passed. Abhishek wrote on 21 Oct ..." with no fragment. But the Pipeline tab still reads "Next: Partner meeting Monday by 26 Oct" on Mon 9 Nov |
| 4. Late work stays until done | Partly | Met: Aditi's paragraph on Today every morning Tue 27 Oct to Mon 9 Nov; Vikram's "Aditi Rao owes you" every morning; Thu 29 and Fri 30 the Arjun intro is the hero with the race. Not met: Fri 23 09:24 and 11:24 the Arjun row drops the race again, and at 09:24 a Gravity row has no detail |
| 5. A nudge follows its asks | Met | "Ask the team instead" on Nimbus Thu 29 10:00, team note sent 15:00. Fri 30 06:28: "Nimbus Collect moved on since this nudge was written: it now asks about Kestrel Pay and Orbit Treasury only", and the body names those two. After "Aditi said yes" on Orbit: Kestrel and Nimbus only. Thu 29 06:28 row ends "Nudge ready". Wed 4 Nov push: "Still open: Nudge Aditi on Kestrel and Orbit: no reply since 22 Oct. Note ready" |
| 6. Names and first runs | Partly | Met: Meera's Pipeline hero reads "Saffron Peak Capital" every run from Sat 24 to Mon 9 Nov; her first run names the holder ("Check the firm's view with Aditi"). Not met: Kabir Mon 26 06:28 still reads "Deal: next step was due 15 Oct" |
| 7. A partner is treated as the board partner | Met | Aditi's Portfolio, rendered Thu 22 and Mon 9 Nov: Orbit and Kestrel read "your call before anyone sources" |
| 8. Answered stays answered | Met | Rohan, Sent it on 19 replies Thu 22 10:00: none drafted again to Mon 23 Nov. Aditi, Sent it on the markup Fri 23, no Done, sent email not in mail: no markup draft again to Mon 23 Nov |
| 9. Met logs do not sit for a week (suggestion) | Met | Aditi Wed 28 08:00, rendered: "Log 4 meetings from 23 Oct, 22 Oct, 21 Oct", and "Show them" opens the four forms. The headline counts meetings once |

## Scores

| Persona | Level | R10 | R11 | Why, in one line |
|---|---|---|---|---|
| Aditi Rao | Partner | 9 | 9.5 | Her race, paragraph and board-partner tests now pass to Mon 9 Nov. Left: late founder promises leave Today's rows after a week, and Friday still drops the rival twice. |
| Kabir Shah | Principal | 9.5 | 9.5 | Every round-ten fix holds for two weeks. Left: an unnamed deal fact, and Pipeline rows that say "by" a date already past. |
| Meera Iyer | Associate | 9 | 9.5 | Names, carried words, the holder and the Pipeline loop are right to Mon 23 Nov. Left: page wording past its date, and an aging pitch reply. |
| Rohan Das | Analyst | 9.5 | 9.5 | Answered pitches stay answered to Mon 23 Nov. Left: a pitch that flips between "you already write to them" and "book a call", and a broken folded line in week two. |
| Tara Menon | Platform | 9.5 | 9.5 | The nudge follows its asks and a reply stops it. But an unrelated email counts as a reply, and a partial reply ends the nudge for every ask. |
| Vikram Nair | CFO and IR | 9 | 9 | The chase is remembered for the life of the call. But the new reply check ends the loop: a promised wire that never comes, or any email from Peter, silences it for four weeks. |
| Solo GP | $30M, alone | 9 | 9 | The same money gain and the same reply gap as Vikram, plus week-two wording on Today. |

Average 9.29 (round ten: 9.21); Quillwater's six 9.42. Two up half a point, five held, none down.

## Each persona

### Aditi Rao, Partner (9.5, up from 9)

Better since round ten:
- Thu 29 and Fri 30 06:24 hero: "Intro Arjun to Raj Malhotra at Fable Bank | Promised to Arjun Khurana (Gravity Payouts), due 20 Oct. Two other funds with offers, decide by 31 Oct". Thu 29 push: "Intro Arjun ... 9 days late. Draft ready".
- "Write the portfolio highlights paragraph" is on Today every morning, Tue 27 Oct to Mon 9 Nov (14 days late on Mon 9 Nov).
- Tue 3 Nov 07:24 hero is whole: "Send the term sheet markup | ... Term sheet from Bluepeak Partners, decide by 05 Nov". Thu 5 Nov push: "Atlas Settlement: term sheet from Bluepeak Partners, decide today".
- 25 pushes to Mon 9 Nov: none is old news, none is cut, no day has more than four.
- Portfolio, rendered Mon 9 Nov: "Runway under 9 months: your call before anyone sources"; Nimbus reads "Warm path: you know Raj Malhotra".
- Wed 28 08:00, rendered: the four unlogged meetings fold into one row. Save on Beacon logs it, with `clear_step` because the CRM's step was that meeting.
- Sent it on the markup Fri 23: no new markup draft to Mon 23 Nov.

Still costs time or trust:
- Fri 23 09:24 and 11:24: the Arjun row reads "Promised to Arjun Khurana (Gravity Payouts), due 20 Oct, 3 days late", without the race. These are the same two runs as round ten. At 09:24, "Gravity Payouts: two other funds with offers" shows with an empty detail.
- Late promises to founders leave Today's rows once they are 8 days late and no race runs:
  - the co-op deck (Ledgerline) from Sat 31 Oct;
  - the partner vote outcome (Solace) from Tue 3 Nov;
  - the markup from Fri 6 Nov, 14 days late, the day after Atlas's deadline;
  - the Arjun intro on Mon 2 Nov.
  Rendered Mon 9 Nov, their drafts are still under Ready for you, but without how late they are.
- Pipeline tab, rendered Mon 9 Nov: 18 of 19 rows read "Next: ... by" a past date. For example: "Gravity Payouts: Their deadline 31 Oct has passed. Next: Partner meeting Monday by 26 Oct". The chip beside it says "Next step was due 26 Oct".
- The Arjun and Raj introduction ends "Could you also send the updated unit economics when you have it?". That asks the founder for numbers in front of the banker. The engine attaches `they_owe` to an introduction that copies Raj, and the morning-brief skill says to add the line. The wording is the demo's; the instruction is the build's.
- Fri 6 Nov push: "Vikram Nair owes you: Q3 LP letter draft. Promised for 24 Oct, 13 days late". That letter waits on her own paragraph, which is 11 days late.
- Fri 13 Nov, after Sent it on the markup: the hero reads "Decide on Atlas Settlement ... Next step: Send term sheet markup". It repeats the CRM's old step.

For 10: a late founder promise keeps a row or one line until done; the Friday trim keeps the race; introductions ask nothing of the founder in front of the other party.

### Kabir Shah, Principal (9.5, held)

Better:
- Thu 29 06:28 Lumen row: "Maya wrote on 21 Oct: 'Two other funds are in diligence with us and want to move fast.'" No "shared by the deal team", and no past "next ... by".
- 20 pushes to Mon 9 Nov with no old news. Lumen comes back only in the Thursday review ("Review ready: Lumen Ledger: two other funds in diligence", Thu 29 and Thu 5 Nov).
- Mon 26 07:30, rendered: the hero "Share the diligence checklist" offers Open draft, Sent it and Done. Sent it marks the draft, the promise and the row, and "Send the cohort analysis questions" steps up.
- The Kite Pay hero keeps "Tamarind Capital wants to lead" to Mon 9 Nov.

Still costs:
- Mon 26 and Fri 30 06:28: "Forward the Cobalt AA notes ... Deal: next step was due 15 Oct". The deal is still not named.
- Pipeline tab, rendered Mon 9 Nov: 5 of 6 rows read "Next: ... by" a past date (for example "Lumen Ledger: Next: Cohort analysis review by 26 Oct"), beside a "Next step was due" chip.
- Demo only: "Could you also market map of AA players?" in the Cobalt notes draft.

For 10: name the deal in a folded fact, and say "was due" on the Pipeline tab.

### Meera Iyer, Associate (9.5, up from 9)

Better:
- Pipeline hero "Trellis Banking API: Saffron Peak Capital wants to lead" on every run from Sat 24 to Mon 9 Nov. The Thu 5 Nov push keeps the capital.
- Fri 30 07:29 Sable row: "Their deadline 23 Oct has passed. Abhishek wrote on 21 Oct: '...need an answer by Friday.'" Mon 9 Nov: "Second meeting, next: diligence kickoff, was due 24 Oct. From Abhishek's email, in your CRM."
- First run names the holder: "Check the firm's view with Aditi, who sponsors the deal".
- 20 pushes to Mon 9 Nov with no old news.
- The Pipeline loop holds to Mon 23 Nov:
  - met logs at Thu 19:05 give "1 meeting to log and 2 next steps to add";
  - Halo's step, saved Fri 23 10:00, reaches the CRM at 10:29;
  - Trellis's step, saved again Wed 28 10:00, reads "Partner meeting on 3 Nov by 03 Nov (saving to your CRM at the next check)" at 10:05 (rendered) and is in the CRM at 10:29;
  - Rivulet's step request lasts to Mon 23 Nov, and its form saves the text (rendered).

Still costs:
- Pipeline tab, rendered Mon 9 Nov: 11 of 13 rows read "Next: ... by" a past date (for example "Next: Diligence plan by 25 Oct").
- The Harborline Treasury reply (score 93, written Thu 22) is still "ready to send" on Mon 9 Nov. It is re-slotted, with no word that it is two weeks late.
- Ember Credit's unlogged 21 Oct meeting leaves the prompts on Thu 29. The headline drops "1 meeting to log" though it was never logged.
- Demo only: "Could you also give data room access?"

For 10: Pipeline words true on the day, and an old reply that says it is late or leaves.

### Rohan Das, Analyst (9.5, held)

Better:
- "Sent it" on all 19 pitch replies Thu 22 10:00: none is drafted again to Mon 23 Nov. Rendered Mon 9 Nov, Ready for you holds no pitch reply.
- The Vaultline row keeps "Tanvi wrote on 21 Oct: ..." to Mon 9 Nov. The review push keeps whole clauses: "Bharat Risk Labs: 13 days in screening. Screening memo, was due 23 Oct".
- 19 pushes to Mon 9 Nov: none is cut, and none is old news sent as new.

Still costs:
- Sutra Compliance flips 7 times between "you already write to them: answer in your thread" and "book a call" (Wed 28 Oct to Tue 3 Nov), then reads "book a call" to Mon 9 Nov. The flag holds only while a run's read has the thread.
- Rendered Mon 9 Nov with no taps: "19 replies to pitches, ready to send" over ". Oldest pitch first." Home holds 0 pitches and 19 reply drafts: pitches are kept 14 days, drafts 30.
- Morning pushes "Still open: Vaultline: the round is oversubscribed" on Wed 28 Oct and Wed 4 Nov.

For 10: a pitch you write to stays "in touch", and the folded line keeps its count by kind.

### Tara Menon, Head of Platform (9.5, held)

Better:
- Thu 29 06:28, the run that writes the nudge:
  - the row reads "Your 22 Oct note to Aditi: no answer yet on Kestrel Pay, Nimbus Collect and Orbit Treasury, 5 working days. Nudge ready";
  - the push reads "Nudge Aditi on Kestrel, Nimbus and Orbit: no reply since 22 Oct. Note ready";
  - the Portfolio hero opens the draft.
- "Ask the team instead" on Nimbus Thu 29 10:00:
  - rendered 11:30, the row reads "Team note ready" with Sent it;
  - after Sent it, "Asked the team on 29 Oct";
  - Fri 30 the nudge asks about Kestrel and Orbit only;
  - Wed 4 Nov push: "Still open: Nudge Aditi on Kestrel and Orbit ... Note ready";
  - Thu 5 Nov drafts a team nudge.
- "Aditi said yes" on Orbit works the same way (Kestrel and Nimbus left). Orbit reads "Team note ready ... Aditi said yes on 29 Oct".
- Aditi's reply in the thread, Mon 26 15:00:
  - no nudge and no push to Mon 23 Nov;
  - each ask reads "Aditi replied on 26 Oct: read it, then answer here", with Close ask and "Aditi said yes: ask the team" (rendered);
  - the yes tap shows "Team note coming at the next check";
  - Close ask writes only the ask.
- Nudge sent Thu 29: by Thu 5 Nov, "Nudged Aditi on 29 Oct, still no reply: ask the team instead" (Nimbus) and "raise it with Aditi directly" (Orbit, Kestrel).
- Aditi's intro email Mon 26: the Thu 29 nudge names Kestrel and Orbit only.

Still costs:
- Aditi's email "Kestrel Pay: board pack for 6 Nov", Tue 27, in another thread, counts as her reply. Kestrel leaves the Thu 29 nudge and reads "Aditi replied on 27 Oct: read it, then answer here" to Mon 23 Nov.
- A partial reply ("Yes on Orbit Treasury. Let me think about the other two.") marks all three replied. No nudge comes for Kestrel or Nimbus to Mon 23 Nov.
- "read it" has no link: the rows offer Close ask and the next note, not the reply.
- Thu 29 10:28 to Fri 06:28 (rendered 11:30): the row names two asks, but its "Before you send" still names three and the body still bumps Nimbus.
- Thu 5 Nov 06:28 push: "Still open: Nimbus Collect: nudge the team, no reply since 29 Oct". That run wrote the nudge, but the push has no "Note ready" (Thu 12 Nov has it).
- No taps: the three asks leave Today one by one (Kestrel Fri 30, Orbit Mon 2 Nov, Nimbus Wed 4 Nov). The Portfolio tab keeps them.

For 10: only a real reply counts, the asks a reply leaves open keep their nudge, and a tapped change narrows the nudge within the hour.

### Vikram Nair, CFO and IR (9, held)

Better:
- "Sent it" on the chase Thu 22 10:00, run to Mon 23 Nov, with or without the sent email in mail:
  - from 10:20 every Peregrine line says "chased Peter on 22 Oct";
  - no run after it says "no touch";
  - no first chase again.
- Thu 29 06:20 hero: "chased Peter on 22 Oct, no reply in 5 working days. Second note ready: check the amount, then send it". It no longer says "The morning brief drafts a second note".
- Second note sent Thu 29 10:00: "chased Peter again on 29 Oct". From Thu 5 Nov: "no reply in 5 working days: call Peter". No third note to Mon 23 Nov.
- Peter's reply Mon 26: no second note. A second note written Thu 29 06:20 is withdrawn after Peter's 12:00 reply; one run shows both lines.
- Wire paid Thu 5 Nov: the call line leaves from Fri 6 Nov.
- "Aditi Rao owes you: write the portfolio highlights paragraph" is on Today every morning, Tue 27 Oct to Mon 9 Nov.

Still costs:
- A reply that only promises the wire ends the loop. Mon 23 Nov still reads "Called on 05 Oct, 49 days ago; chased Peter on 22 Oct, Peter replied on 26 Oct":
  - no second note, no "call Peter" and no push in four weeks;
  - rendered Mon 9 Nov, the row is fifth on Today.
- Any email from Peter counts as a reply. "AGM in December" on Tue 27 gives "Peter replied on 27 Oct" to Mon 23 Nov, and no second note.
- No taps: the call is the hero on 12 of 13 weekday mornings to Mon 9 Nov, but none of his 18 pushes names it. His own late promises win the push every morning.
- Thu 29 07:00, after Sent it on the second-note hero (rendered): the hero still says "Second note ready: check the amount, then send it", with no draft button, until the next check.
- Paid while the chase is not in mail: "LP: Peregrine Trust: No touch in 110 days" from Fri 6 Nov, 15 days after the chase.
- Demo only: Friday's rewrite of the fee-offset note keeps "Add it before you send" without saying what "it" is.

For 9.5: a reply that does not pay is followed after the date it names; only a real answer counts; the money hero reaches his phone.

### Solo GP (9, held)

Better:
- Money as for Vikram: "chased Peter on 22 Oct" to Mon 23 Nov, one second note, "call Peter" after two.
- 24 pushes to Mon 9 Nov with no old news.
- Kestrel's ask says "weigh the hires against the burn before sourcing".

Still costs:
- The same reply gaps as Vikram. After Peter's "wire goes out on Wednesday", the line reads "Peter replied on 26 Oct" to Mon 23 Nov with $60K unpaid. An unrelated email counts too.
- Rendered Mon 9 Nov: "27 replies to pitches, ready to send" over ". Oldest pitch first." These replies were written 22 and 23 Oct. Their call replies are re-slotted with the same "Thanks for sending ... our way" (Sutra four times by Thu 5 Nov).
- Mon 9 Nov hero: "Another fund is moving: Atlas Settlement: term sheet from Bluepeak Partners | Their deadline 05 Nov has passed."
- The Arjun and Raj introduction asks Arjun for unit economics in front of Raj, as for Aditi.
- Demo only: "Separately, my introduction to Arjun is on its way today" stays in a note waiting since 22 Oct.

For 9.5: the money loop survives a reply; folded replies keep their words; a passed deadline is not "moving".

## Top five changes

1. **Count only real replies, and keep the loop alive after one** (Vikram, the solo GP, Tara).
   - An LP reply must be in the chase's thread or speak of the call. An ask reply must be in the note's thread or answer that ask, never any email naming the company.
   - A reply that names a date, or answers part of a note, gets a follow-up when that date or five working days pass ("Peter said the wire would go on 28 Oct; still unpaid. Second note ready"). Keep the unanswered asks in the next nudge.
   - Link "read it" to the reply.
2. **Late work stays visible however late** (Aditi most).
   - A promise to a founder more than a week late keeps its row, or one line ("3 promises more than a week late"), with how late it is. A race ending is no reason to drop it.
   - When a meeting hero trims the rows, keep a row's race and date, and never leave a row with no detail (Fri 23 09:24 and 11:24).
3. **True within the hour** (Tara, Vikram).
   - Narrow a waiting nudge at the run after the tap, not the next morning.
   - Say "Note ready" on the run that writes any nudge, a single ask's included.
   - After "Sent it" on a capital-call hero, say the note went until the next check.
   - Push the money hero at least once a week while it is the hero.
4. **Page words that age well** (Meera, Aditi, Kabir, Rohan, the solo GP).
   - Pipeline rows say "was due 25 Oct" once the date has passed, never "by 25 Oct".
   - Keep each reply draft's kind on the draft, so the folded line keeps "3 asks for more, 12 kind passes" after the pitch list prunes.
   - Remember "you already write to them" once a run has seen it (Sutra).
   - Name the deal in a folded deal fact ("Cobalt AA: next step was due 15 Oct").
5. **Drafts and lines that hold up as they age** (Aditi, the solo GP, Meera).
   - No "could you also send ..." in an introduction that copies a third person.
   - A pitch reply waiting more than a week says it is late, or leaves.
   - After "Sent it", do not repeat the CRM's old step as the next step ("Send term sheet markup" on Fri 13 Nov).
   - When a colleague's late work waits on yours, say so ("Vikram's Q3 letter waits on your paragraph").

## Reaching 9.5 or 10: tests on the same replay

1. **A reply is not payment.**
   - Setup: Vikram, windowed, "Sent it" on the chase Thu 22 10:00. Peter replies in the thread Mon 26 11:00: "The wire for the 5 Oct call goes out on Wednesday." The call stays unpaid. Run to Mon 23 Nov.
   - Pass: by Thu 29 Oct 06:20 the Peregrine line says the wire has not come, and a second note is ready.
   - Today: "chased Peter on 22 Oct, Peter replied on 26 Oct" every run to Mon 23 Nov, with no draft and no push.
   - The same for the solo GP's $60K.
2. **Only a real reply counts.**
   - Vikram: Peter emails "AGM in December" Tue 27 (another thread, no word of the call). Pass: Thu 29 06:20 drafts the second note, and no line says "Peter replied". Today: "Peter replied on 27 Oct" to Mon 23 Nov.
   - Tara: Aditi emails "Kestrel Pay: board pack for 6 Nov" Tue 27. Pass: the Thu 29 nudge names all three asks. Today: Kestrel is dropped and reads "Aditi replied on 27 Oct".
3. **A partial reply keeps the rest.**
   - Setup: Tara; Aditi replies in the thread Mon 26: "Yes on Orbit Treasury. Let me think about the other two."
   - Pass: by Tue 3 Nov, Kestrel and Nimbus have a nudge or a "waiting on Aditi" line. Every "Aditi replied" row opens the reply.
   - Today: no nudge to Mon 23 Nov, and no link.
4. **Late founder promises stay.**
   - Aditi, no taps, to Mon 9 Nov. Pass: the co-op deck, the partner vote outcome, the markup and the Arjun intro are on Today every morning, as rows or in one line, with how late each is.
   - Today: they leave the rows from Sat 31 Oct, Tue 3 Nov and Fri 6 Nov, and on Mon 2 Nov.
   - Fri 23 09:24 and 11:24. Pass: the Arjun row keeps "Two other funds with offers, decide by 31 Oct", and no row has an empty detail.
5. **A nudge narrows within the hour.**
   - Tara, "Ask the team instead" on Nimbus Thu 29 10:00. Pass: at 10:28 the nudge's "Before you send" and its body name Kestrel and Orbit only. Today: only from Fri 30 06:28.
   - Thu 5 Nov 06:28. Pass: the push for the team nudge written that morning ends "Note ready".
6. **Page words age well,** rendered Mon 9 Nov. Pass means each of these:
   - no Pipeline row for Aditi, Meera or Kabir reads "Next: ... by" a past date (today: 18 of 19 for Aditi, 11 of 13 for Meera, 5 of 6 for Kabir);
   - Rohan's and the solo GP's folded replies keep their count by kind (today: ". Oldest pitch first.");
   - Rohan's Sutra row keeps "you already write to them" on every run, Thu 22 to Mon 9 Nov (today: 7 flips);
   - Kabir's Mon 26 06:28 folded line names the deal.
7. **Money reaches the phone and stays true after a tap.**
   - Vikram, no taps, Thu 22 to Mon 9 Nov. Pass: the call is pushed at least once a week while it is the hero. Today: hero on 12 mornings, 0 of 18 pushes.
   - Thu 29 07:00, "Sent it" on the second-note hero. Pass: the hero no longer says "Second note ready ... then send it". Today: it does until the next check.
   - Wire paid Thu 5 Nov. Pass: no "No touch in 110 days" after a chase marked sent. Today: from Fri 6 Nov, when the chase is not in mail.
8. **Introductions ask nothing of the founder in front of the other party** (a suggestion).
   - Aditi and the solo GP, Thu 22. Pass: the Arjun and Raj introduction has no line asking Arjun for the unit economics, and `owed.json` carries no `they_owe` on an entry with `cc`.
9. **Old pitch replies** (a suggestion).
   - Solo GP, no taps, Mon 9 Nov. Pass: a pitch reply written on 22 Oct either says it is late or has left Ready for you.
   - Today: 27 are still "ready to send", and the call replies are re-slotted with the same opener.
