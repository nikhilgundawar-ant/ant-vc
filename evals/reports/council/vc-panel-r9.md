# Instinct for VCs: VC panel, round nine

**This is a simulated panel. No real investor took part.** One Claude agent played all seven: six people at the fictional Quillwater Ventures (Aditi Rao, Partner; Kabir Shah, Principal; Meera Iyer, Associate; Rohan Das, Analyst; Tara Menon, Head of Platform; Vikram Nair, CFO and IR) and a solo GP running a $30M fund alone.

## What I read and ran

- **Read, in order:**
  - my round-eight report (`vc-panel-r8.md`);
  - "Round nine: what changed" in `BUILD_LOG.md`;
  - the seven packs in `evals/runs/council/briefs-r9/`;
  - every `level-*-today-380.png`, `met-step-380.png`, `met-log-380.png` and `qa.json`. Its `page_sha256` (6cd4abc7f2c2) matches `home/index.html`;
  - the diff 75704b8 to 7ada649 for engine, skills, shared, home, `demo.py`, `replay.py` and `home_qa.py`.
- **The two Claude-run evals on 0.7.2 finished while I worked.** I read both and cite them:
  - `evals/runs/friday-meera/report.md`: 7 out of 10.
  - `evals/runs/friday-tara/report.md`: 7 out of 10.
  - Both are also saved as `evals/reports/claude-runs/r9-friday-*.md`.
  - I reproduced their main findings in my own replays.
- **Scratch copy:** `/tmp/vc-panel-r9/repo`, at 070b9d8, with `briefs-r9` copied in.
- **Uncommitted edits appeared in the real repository while I worked, and were still growing when I finished.** They touch `engine/instinct/cli.py` and `brief.py`, `home/index.html`, `evals/demo.py` and `evals/replay.py`. Two of them fix bugs I report below (the `holder` regex and the stuck "Draft coming" chip). I scored 070b9d8 only.
- **Suites, in the scratch copy:**
  - `--suite round9`: 9 of 9. `round8` 9 of 9, `round7` 10 of 10, `round6` 4 of 4, `round6b` 8 of 8, `evals6` 8 of 8, `evals8` 4 of 4, guard 652 of 652.
  - Full runner: 142 of 142 deterministic checks. Seven Claude-run scores were skipped, because the clone has no saved runs. The committed scorecard's 155 adds those 13.
  - Design lint: 0 violations in 214 rules.
  - Home QA, re-run here with Playwright: 452 of 452. Same page hash.
- **My own replays, beyond the suite:**
  - `replay._week` for all seven, Thu 22 to Mon 26, every run dumped.
  - `replay._replay_windowed` (each run reads only its own window) for all seven, to Fri 30, compared run by run with `_week`.
  - Meera's met logs saved as Home fills them in. Variant A: she never adds a step. Variant B: she types Halo's step on Friday at 10:00.
  - Tara with "Sent it" at Thu 10:00, then Aditi either sends the intro email (Mon 12:00) or stays quiet. In the quiet case, "Ask the team instead" is tapped on Thu 29, the note is written, and Tara marks it sent at 15:00.
  - Vikram and the solo GP mark the capital-call chase sent at Thu 10:00.
  - A trace of the `holder` lookup inside `_owed`.
  - Replayed Homes rendered in the real `home/index.html` with the QA harness. I read the visible text and opened rows, as each persona would.
- **Drafts in the replay come from `evals/demo.py`, not Claude.** I judged whether the engine asks for the right draft at the right time with the right inputs. Where only the demo wording is off, I say "demo only".

## In short

- **Round nine closed almost every round-eight test:**
  - On real read windows, Tara's Nimbus ask kept its warm path ("Aditi knows Raj Malhotra at Fable Bank") at every run, Thu 22 to Fri 30. With Aditi's email at Mon 12:00, it showed "Intro made on 26 Oct" at 12:28.
  - Tara sends Aditi one note for three asks: "Founder asks: Kestrel Pay, Orbit Treasury, Nimbus Collect" (Thu 06:28). The asks stay on Today until done, and on Thu 29 Today says "nudge Aditi".
  - The money is drafted. Peregrine's chase note is written Thu 06:20, and the row says "Draft ready: check the amount, then send it".
  - Meera's empty-step met log clears the old step. From Fri 06:29, Today asks "Halo Reconcile: met 22 Oct, add the next step".
  - Aditi's Friday board hero asks the board's question: "With 8.0 months left at $200K net burn a month, do we help them hire now, or wait?"
  - Quotes are dated ("Tanvi wrote on 21 Oct"), met pitches leave Rohan's inbound list, the solo GP's sample owns every deal, and no push about an ask is cut mid-name.
- **What keeps all seven below 9.5:**
  - **The real run still reads less than the pack shows.** A pulse reads no CRM people, and Home does not carry them forward. Run by run, the windowed week differs from the pack's replay for 6 (Aditi) to 44 (Kabir, Rohan, Tara) of 48 runs. Rows lose the company and the rival ("Promised to Arjun Khurana, due 20 Oct, 4 days late"). Quotes lose the founder ("They wrote on 21 Oct"). Vikram's heads-up says "09:00 Ledgerlane". Aditi's Saturday hero changes.
  - **What a draft needs never reaches the user once the draft sits on a row or the hero.** Examples: "check it still stands", "Fill in the 3 lines", "found no fee offset clause". The Tara eval found this (0 of 4 notes visible), and I saw the same for Kabir and Meera on Friday. Meera's Monday push says "Draft ready" for a draft with three blank lines.
  - **The sponsoring partner is never named.** The `holder` regex in `cli.py` line 1489 holds two backspace characters instead of word boundaries, so it never matches. The fix is in the uncommitted tree.
  - **After "Sent it", money and asks stall.** The capital call never says it was chased, and no second note follows. One unanswered email to Aditi becomes three nudges. After a follow-up note is sent, Home says "Draft coming at the next check" for good. That fix is also uncommitted.
  - **Late work still slips away after its day.** Aditi's highlights paragraph is on Today on Monday only. Meera's step request ends after five working days, though no step was set.
- **Scores: average 9.0** (round eight: 9.07). Six hold at 9. Kabir goes from 9.5 to 9: the build did not get worse for him, but the real read windows and the hidden draft notes take away his "only demo wording left".

**Round-eight tests on this build**

| Round-eight test | Verdict | Evidence |
|---|---|---|
| 1. The replay reads what a real run reads | Half met | Tara: the path held at every run, and the intro showed as made at Mon 12:28. Aditi and Vikram kept every path and warning, but not names: Sat 24 09:24 hero flips; Thu 07:20 push "09:00 Ledgerlane" |
| 2. One note per person; asks to the end | Met, with edges | One note at Thu 06:28. Orbit and Kestrel stay on Today to Fri 30, with "nudge Aditi" on Thu 29. "Yes, ask the team" has its own id. Edges: three nudges for one email; a stuck "Draft coming" chip |
| 3. Money drafted before the brief | Met, with an edge | Chase note at Thu 06:20; heroes say "Draft ready" on Fri and Mon; the same for the solo GP. At Thu 06:20 the letter row still reads "Instinct drafts it ... · Draft ready" |
| 4. Nothing due or late vanishes | Met on the day only | The highlights paragraph is a row at every Monday run. Vikram's Monday push names the fee offset. 0 pushes record a name they do not say. From Tue 27 the late paragraph is on no row and in no push |
| 5. The step after a met log | Met to Thu 29 | Step request every run from Fri 06:29. No Pipeline shows "Second meeting, 24 Oct". Aditi's Halo: 1, 5 and 7 days. On Fri 30 the request is gone and the deal is "No next step set" |
| 6. Quotes dated; met pitches move on | Met | "Tanvi wrote on 21 Oct" on Monday. Paysa and Ruplink leave the inbound list. "first call" maps to First meeting |
| 7. Carried lines are current | Met | Solo Fri 07:24 gives no day count. Fri 09:24: "Next step: Founder call on terms". No "the an" |
| 8. The board's question leads | Met | Fri 08:24 and 09:24 hero, quoted above |
| 9. The solo sample speaks for one | Met | QA "solo-pipeline"; "Solace Treasury: decision prep" |
| 10. The shared link is current | Not scored | As in round eight |

## Scores

| Persona | Level | R8 | R9 | Why, in one line |
|---|---|---|---|---|
| Aditi Rao | Partner | 9 | 9 | The board hero, the Monday chore and the dated Pipeline are fixed. But her real weekend Home loses names and rivals, and the late highlights paragraph is gone from Tuesday. |
| Kabir Shah | Principal | 9.5 | 9 | His refreshed drafts now say "check it still stands", but he never sees it. The real windows strip companies from his rows on 44 of 48 runs. |
| Meera Iyer | Associate | 9 | 9 | The step after a met log works end to end. But the partner is never named, "Draft ready" sits on a three-blank draft, and "rivulet Payments" is lowercased in her copy brief. |
| Rohan Das | Analyst | 9 | 9 | Every round-eight item is fixed. On real windows, his heads-up before the Ruplink call reads "Inbound for 6 days, usually 3", not the revisit verdict. |
| Tara Menon | Platform | 9 | 9 | Asks now hold to the end on real windows. But a sent team note leaves "Draft coming at the next check", and one quiet email gives three nudges. |
| Vikram Nair | CFO and IR | 9 | 9 | The capital call is drafted. After he sends it, nothing tracks it, and real-window heads-ups name "Ledgerlane" and "Northgate". |
| Solo GP | $30M, alone | 9 | 9 | Every round-eight item is fixed and her words are her own. But her $60K chase is not followed after sending, and her weekend Home flips. |

- **Average: 9.0** (round eight: 9.07).
- **Quillwater's six: 9.0** (round eight: 9.08).
- Six held, one went down half a point, none went up. The fixes are real. The new evidence, from this round's own windowed replay and Home renders, costs each persona about as much as the fixes gave.

## Each persona

### Aditi Rao, Partner (9)

**Better since round eight**
- Fri 08:24 hero: "Review the board deck. Promised to Vikram Rao (Orbit Treasury), due 22 Oct. You meet them at 10:00. With 8.0 months left at $200K net burn a month, do we help them hire now, or wait?" The runway leads, and the hiring is her call.
- Mon 06:24 to 19:24: "Write the portfolio highlights paragraph: Promised to Vikram Nair, due today" is a Next up row at every run.
- Sun 17:24 "Week ahead: 1 meeting, decide Gravity Payouts by 31 Oct, 3 promises late" records no subjects, so Mon 06:24 can lead with "Intro Arjun to Raj Malhotra at Fable Bank: Gravity Payouts, 6 days late. Draft ready".
- Tara's three asks reach her as one email (Thu 06:28).
- After Meera's met logs, her Pipeline shows Halo in "Second meeting" for 1 day on Fri 23, 5 on Tue 27 and 7 on Thu 29, and never "Next: Second meeting, 24 Oct".
- The headline counts her met logs: "5 things for today, 1 urgent, and 1 meeting to log" (Thu 06:24).

**Still costs time or trust**
- **Real weekend windows** (Sat 24 09:24 to Sun 25 13:24, windowed replay):
  - Her hero changes from "Intro Arjun to Raj Malhotra at Fable Bank. Promised to Arjun Khurana (Gravity Payouts), due 20 Oct. Two other funds with offers" to "Atlas Settlement: term sheet from Bluepeak Partners. They wrote on 21 Oct: ...".
  - The row becomes "Promised to Arjun Khurana, due 20 Oct, 4 days late", with no company and no rival. The rival is what ranked it first.
- **The late chore vanishes again.** On the windowed replay to Fri 30, "Write the portfolio highlights paragraph" is on no row and in no push from Tue 27. The pushes name the markup, the deck and the Arjun intro instead. Vikram's Today never shows that he is waiting on it.
- **Draft notes are hidden.** On Friday her markup and intro drafts are refreshed with "check it still stands, or tap Done if it was settled in the room". Both now ride on Next up rows, where Home shows "Draft ready", "Open in Gmail" and "Copy draft", but not that line.
- Fri 09:24, Signals: "Gravity Payouts: two other funds with offers :: Arjun wrote on 20 Oct." The budget trim cut the quote and left only the date.
- Four met-log forms sit open from Friday to Monday ("and 4 meetings to log"). On Mon 26, Solace's form still fills in "Partner vote" due 23 Oct, a date already past.

**For 9.5 or 10**
- Real-window rows keep "(Gravity Payouts). Two other funds with offers" and "Ishaan wrote".
- A late promise to a colleague who is waiting on it stays visible until it is done.
- Every draft shows what it needs before she opens it.

### Kabir Shah, Principal (9, down from 9.5)

**Better since round eight**
- Fri 06:28: the refreshed Kite and Lumen drafts carry "Written before your 22 Oct meeting, which has no notes: check it still stands, or tap Done if it was settled in the room". This is what I asked for.
- Subjects name the company: "Vertex Card Issuing: tech diligence with the CTO advisor".
- Mon 06:28: "Share the diligence checklist: Siddharth (Kite Pay), 6 days late. Draft ready", with "Tamarind Capital wants to lead" in the hero. Mon 08:28: "10:00 Monday partner meeting: 11 to decide, yours: Kite Pay and Lumen Ledger".

**Still costs time or trust**
- **He never sees that check.** I rendered his Fri 06:28 Home. All four drafts ride on the hero or a row. "Ready for you" holds only his three met logs. Opening "Send the cohort analysis questions" or "Forward the Cobalt AA notes" shows "Open in Gmail" and "Copy draft", but no note. The Kite draft still thanks Sid for "the security audit report you are sending over".
- **The real windows change his day.** 44 of his 48 windowed runs differ from the pack:
  - Thu 07:28 to 19:28: "Schedule tech diligence with the CTO advisor :: Promised to Rohit Saluja, due tomorrow". A second row appears: "Vertex Card Issuing: 30 days in due diligence (usually 21) :: Next: Tech diligence call by 27 Oct. No contact in 9 days". The pack merges both into one line with the company.
  - Fri 07:28 push: "Review ready: Vertex Card Issuing: 31 days in due diligence (usually 21)". The pack says "Review ready: Lumen Ledger and 2 more deals need you this week".
  - Sat 24 09:28 hero: "Promised to Siddharth Menon, due 20 Oct". Kite Pay and Tamarind Capital are gone.
- Three met-log forms stay open from Thursday evening to Monday ("and 3 meetings to log").
- **Demo only:** the Fri 06:28 reslot offers "Mon 26 Oct at 11:00 or Mon 26 Oct at 12:00". His partner meeting ends at 11:00, and the skill asks for 30 minutes clear. The demo's `free_slots` checks overlap only.

**For 9.5 or 10**
- The note under every draft shows on the hero and the row.
- Real-window rows match the pack, with no duplicate stale row.

### Meera Iyer, Associate (9)

**Better since round eight**
- Her Thu 19:05 met logs clear the old step. From Fri 06:29 her Today reads "Halo Reconcile: met 22 Oct, add the next step. The meeting is in your CRM. The deal has no next step yet", with one field, a date and Save.
- When she types "Diligence plan with the CFO" at Fri 10:00 (my variant B), the 10:29 run applies it. The request goes, and both her Pipeline and Aditi's show the step.
- No Pipeline anywhere shows "Next: Second meeting, 24 Oct" after the logs.
- The Friday eval confirms the loop: "it applied the taps, cleared the old step, asked for the new one and refreshed the drafts".

**Still costs time or trust**
- **The partner is never named.** `cli.py` line 1489 reads `re.search(r"\x08(feedback|view|...)\x08", ...)`, with literal backspace characters. It never matches. At Thu 06:29, the entries for "Share feedback after the partner meeting" and "Share our view on pricing" have no `holder`, so the drafts never say Aditi holds the firm's view. No test covers it. The eval's finding 7 hit the same gap.
- **"Draft ready" over blanks.** Fri 06:29 render: "Share feedback after the partner meeting. Promised to Omkar Patil (Rivulet Payments), due 19 Oct, 4 days late. The round is filling up", with "Draft ready" and "Open in Gmail". The draft has three bracketed lines. "Fill in the 3 lines" lives only in the hidden context. The Mon 06:29 push says "Share feedback after the partner meeting: Omkar, 7 days late. Draft ready".
- Thu 19:29 (windowed, after the logs apply): "Deal: rivulet Payments moved to Second Meeting." This shows on Today and in the copy brief she may paste for colleagues. The eval saw it at Fri 06:29.
- Fri 06:29 headline: "12 things for today, 5 urgent, and 3 meetings to log". Two of the three are step requests for meetings she already logged.
- **The request ends too soon.** In variant A (no step added), on Fri 30 06:29 the request is gone. Both Pipelines then call Halo and Rivulet stale ("No next step set", "No contact in 8 days"), and Halo is on no Today row. The suite stops at Thu 29.
- The Pipeline row looks up `ns_<deal>`, while met logs save as `ns_<deal>_<date>` (`home/index.html` line 1181). A saved log does not show there until the next run (eval finding 2).
- **Real windows:** at every pulse from Thu 07:29, Lattice KYC flips from "you already write to them: answer in your thread" to "book a call" (eval finding 11).
- **Demo only:** the Sable reference questions were written by the demo, and the refresh keeps them as if sourced (eval finding 1).

**For 9.5 or 10**
- A draft with blanks says so on its row and in the push.
- The context names Aditi.
- Step requests last until a step is set, and are counted apart from meetings to log.

### Rohan Das, Analyst (9)

**Better since round eight**
- Mon 06:25: "Vaultline: the round is oversubscribed. Tanvi wrote on 21 Oct: 'Our seed is oversubscribed, but we've kept a small allocation for Quillwater until next week.'"
- Paysa and Ruplink are off "Inbound worth a look" and wait as met logs. "Paysa Labs: first call" and "Ruplink: intro call" both offer First meeting.
- The Rhea draft copies Kabir in and offers no hours.

**Still costs time or trust**
- **Real windows weaken his two pitch heads-ups:**
  - Fri 13:25: "15:00 Ruplink: Inbound for 6 days, usually 3. Set a next step after this meeting". The pack says "15:00 Ruplink: Revisit condition met: AA licence granted in September". Before a returning company's call, he gets a nag, not the reason to take it.
  - Thu 09:25: "11:00 Paysa Labs: You owe them: set up a call with Kabir, due 23 Oct", in place of "Met our bar: two marketplaces live on payouts, $310K annualised revenue".
  - Sat 24: "They wrote on 21 Oct" for Tanvi, and "Promised to Rhea Khosla, due 23 Oct" with Paysa Labs gone.
- Thu 29 15:25 (windowed): "Review ready: Bharat Risk Labs: 13 days in screening (usually 7). Next: Screening memo…" This push is cut.
- **Demo only:** the Rhea draft's note reads "Kabir is copied in: their calendar picks the time". It is Rhea who picks the times.

**For 9.5 or 10**
- Heads-ups on real windows keep the revisit verdict.
- No push ends in "…".

### Tara Menon, Head of Platform (9)

**Better since round eight**
- Thu 06:28: one email to Aditi, "Founder asks: Kestrel Pay, Orbit Treasury, Nimbus Collect", cash warnings first.
- On real windows, the Nimbus row reads "Asked Aditi for the intro on 22 Oct. Divya Raman asked on 13 Oct. Warm path: Aditi knows Raj Malhotra at Fable Bank" every morning. On Tue 27: "Intro made on 26 Oct: tap Done to close it."
- Thu 13:28 push: "14:30 Founder community: Divya needs two banks as customers: asked Aditi on 22 Oct".
- Orbit and Kestrel stay on Today to Fri 30. On Thu 29: "Asked Aditi on 22 Oct, no reply in 5 working days: nudge Aditi."
- "Yes, ask the team" makes its own tap, and the eval's team note showed as "Draft ready".

**Still costs time or trust**
- **A stuck chip.** With Aditi quiet, I tapped "Ask the team instead" on Nimbus (Thu 29 10:00), let the note be written, and marked it sent at 15:00. On Fri 30, Today and Portfolio both read "Asked the team on 29 Oct" next to "Draft coming at the next check". That line never goes. The same code path serves "Yes, ask the team". The fix is in the uncommitted tree, and the eval saw it too.
- **Three nudges for one email.** On Thu 29 06:28 (Aditi quiet), three rows say "nudge Aditi". The pushes are "Nimbus Collect: nudge Aditi, no reply since 22 Oct" (Thu 29) and "Orbit Treasury: nudge Aditi, no reply since 22 Oct" (Fri 30). She sent one email. No nudge is drafted.
- **A button that says yes when no yes came.** The same morning, Orbit's row says Aditi has not replied in 5 working days, yet its only next button is "Yes, ask the team". From that tap alone, the eval's team note had to say "I checked with Aditi on 22 Oct, and we want to help" (eval finding 5).
- "Runway under 9 months: check with Aditi before sourcing" stays on the row after she asked, and after the team note (eval finding 2).
- The notes on her drafts are hidden ("0 of 4 context lines were visible", eval finding 1). Her Portfolio hero, the tab she lands on, ignores where asks stand (eval finding 4).
- **Real windows:** "Send the founder guest list :: Promised to Fatima Sheikh, due tomorrow" at every Thursday pulse, with Talentbridge gone.

**For 9.5 or 10**
- One nudge per person per email, with a short draft.
- "Yes, ask the team" only when the partner's reply is in mail, or as a plain "Aditi said yes" choice.
- No stuck chips. The landing hero shows where her asks stand.

### Vikram Nair, CFO and IR (9)

**Better since round eight**
- Thu 06:20: a draft to Peter Quinn, "Fund II: capital call of 5 Oct": "our records show $150K still to come from Peregrine Trust. Could you let me know when we should expect it?" From 07:20 the row reads "Draft ready: check the amount, then send it". The Friday and Monday heroes say the same.
- Mon 06:20 push: "Answer the fee offset question: Helen (Northgate Endowment), 47 days late. Draft ready".
- The letter gives "Fund II: $80M, 45% called", with no paid-in figure. Its watch list leads with the reason: "Orbit Treasury: Runway under 9 months (8.0 months left at $200K net burn a month)". From 07:20 the row reads "Draft ready: check the figures, then send it".

**Still costs time or trust**
- **Nothing follows the chase.** I marked it sent at Thu 22 10:00 on the windowed replay. Every morning to Fri 30, his hero is the same unpaid line. On Fri 30 it reads "Peregrine Trust owes $150K on a capital call. Called on 05 Oct, 25 days ago; no touch in 103 days". It never says "chased Peter on 22 Oct", and no second note comes after five working days. "No touch" only clears if his sent email is also in the read.
- **Real windows:** Thu 07:20 push "09:00 Ledgerlane: You owe them: sign off on the capital account statements, due 23 Oct". The pack says "Ledger & Lane Fund Services". Thu 14:20: "15:30 Northgate: ...". His hero reads "Promised to Helen Park (Northgate)", and his rows drop Kestrel Pay. 43 of 48 runs differ.
- Thu 06:20, the run that drafts the letter, shows "Q3 LP letter draft: Promised to Aditi Rao, due 24 Oct. Instinct drafts it from the KPI history and the LP list · Draft ready". The sample Home screenshot shows the same.
- Helen's draft holds "[Add how monitoring fees offset the management fee under the Fund II agreement.]". Its note, "found no fee offset clause. Add it before you send", sits behind the hero's "Open draft" and is never shown. This is an email to an LP.
- Aditi's highlights paragraph, which his letter needs, is on his Today on no day.
- **Demo only:** the watch list gives Ferro's revenue miss twice, as a percentage and again as "23% behind plan".

**For 9.5 or 10**
- A sent chase reads "Chased Peter on 22 Oct" and gets a second note after five quiet working days.
- Heads-ups use the CRM's company names.
- The letter row is right on the first run too.

### Solo GP (9)

**Better since round eight**
- Her Pipeline shows no owner initials and no partner. The Solace log reads "Solace Treasury: decision prep. It still says next: Your decision by 23 Oct".
- Fri 07:24: "Review ready: Atlas Settlement and 7 more deals need you this week". Fri 09:24: "12:00 Beacon Credit Rails: Term sheet, day 5 of 10. Next step: Founder call on terms".
- The $60K chase is drafted, says "Draft ready", and stays on Today every morning.
- Asks with no warm path use her words and offer no draft: "Runway under 9 months: weigh the hires against the runway before sourcing. No one in your network fits yet".

**Still costs time or trust**
- **Real weekend windows:** her Sat 24 09:24 hero flips, as Aditi's does, to "Atlas Settlement ... They wrote on 21 Oct", and the Arjun row loses Gravity Payouts and its rival.
- **Money after sending:** I marked the chase sent at Thu 10:00. To Fri 30 the row reads "Called on 05 Oct, 25 days ago; no touch in 103 days", with no "chased" state and no second note. She is her own IR.
- Kestrel's ask says "Burn up 43.3% in a month: weigh the hires against the runway". Kestrel has 14.1 months of runway, and the flag is burn.
- Thu 06:24 writes 25 drafts, and Fri 06:24 writes or rewrites 11 more. Home groups them well ("18 replies to pitches, ready to send"). With a Gmail tool that creates drafts, though, all of them would land in her Gmail drafts folder.
- The notes on her drafts are hidden on rows, as for everyone.

**For 9.5 or 10**
- Money followed after sending.
- Weekend rows that keep names and rivals.
- Flags in the ask's own terms ("weigh the hires against the burn").

## Top five changes

1. **Carry people forward so a pulse keeps what the morning read found** (helps all seven; Kabir, Rohan, Tara and Vikram most).
   - `_carry_forward` (`cli.py` line 111) restores companies, deals and LPs from Home, but not people. Keep a people index in Home (name, emails, company id, title) and use it on pulses and weekend runs.
   - Carry `in_touch` and the revisit verdict on pitches.
   - A heads-up names the CRM's company, never a domain stem.
2. **Show what a draft needs before it is sent** (helps all seven; Meera, Vikram and Kabir most).
   - Put the draft's `context` under the hero's and the row's draft buttons.
   - A draft with blanks says "Fill in 3 lines" on its row and in its push, never just "Draft ready".
   - Fix the `holder` regex (commit the working-tree fix), carry `holder` onto refresh entries, and add a test.
3. **Follow money and asks after "Sent it"** (helps Vikram, the solo GP, Tara and Aditi).
   - A sent capital-call chase reads "Chased Peter on 22 Oct", and a second note is drafted after five quiet working days.
   - One nudge per person per email, with a short draft.
   - "Yes, ask the team" only once the partner's yes is in mail, or as an explicit "Aditi said yes" tap. Drop "check with Aditi" once she was asked.
   - Commit the "Draft coming" fix, with a QA scenario for a sent follow-up note.
4. **Keep late work visible until it is done** (helps Aditi, Vikram and Meera).
   - A promise to a colleague who is waiting on it stays on Today, or in a push clause, after its due day. The waiting side sees it too.
   - The step request stays until a step is set, not five working days. Count it as "1 next step to add", apart from "meetings to log".
   - The Pipeline row reads the dated met-log ids (`ns_<deal>_<date>`, `nss_...`).
5. **Words true at every hour** (helps all seven).
   - No push ends in "…", review lines included.
   - A trimmed quote keeps words, never just "Arjun wrote on 20 Oct."
   - Write "Deal: Rivulet Payments moved to Second meeting", with the capital and Home's label.
   - The letter row says "Draft ready" on its first run, too.
   - A met log never prefills a past date.
   - Demo: slots 30 minutes clear of meetings; "Rhea picks the time"; suggested questions marked as Instinct's own.

## Reaching 9.5 or 10: tests on the same replay

1. **The real windows match the pack.**
   - For each of the seven, run `replay._replay_windowed(m, Mon 26 20:30)` next to `replay._week(m)`.
   - At every run, the hero, the Today rows (titles and details) and the push match, apart from mail that is new in that window. Today 6, 44, 20, 44, 44, 43 and 13 of 48 runs differ (Aditi, Kabir, Meera, Rohan, Tara, Vikram, solo).
   - In particular:
     - Vikram's Thu 07:20 push names "Ledger & Lane Fund Services".
     - Aditi's Sat 24 09:24 hero stays "Intro Arjun to Raj Malhotra at Fable Bank", with "(Gravity Payouts). Two other funds with offers".
     - Kabir's Thu 07:28 row keeps "(Vertex Card Issuing)", with no second Vertex row.
     - Rohan's Fri 13:25 heads-up keeps "Revisit condition met".
     - Meera's Lattice KYC keeps "you already write to them" at every pulse.
2. **What a draft needs reaches the user.**
   - Kabir's Home at Fri 06:28 shows "check it still stands, or tap Done if it was settled in the room" under the Kite hero and the Lumen row.
   - Meera's Omkar row at Fri 06:29 says it has 3 lines to fill and names Aditi.
   - Meera's Mon 06:29 push does not say "Draft ready" for that draft.
   - Vikram's Thu 06:20 hero shows "found no fee offset clause".
   - `cli.py` contains no `\x08`. The Thu 06:29 entries for Omkar's feedback and Neha's pricing view carry `holder: "Aditi Rao"`.
3. **Money and asks after sending.**
   - Vikram, windowed, "Sent it" at Thu 22 10:00:
     - Fri 23 06:20 reads "Chased Peter on 22 Oct".
     - Thu 29 06:20 has a second chase note ready.
     - No run after the tap says "no touch in".
   - The same for the solo GP's $60K.
   - Tara, Aditi quiet:
     - Thu 29 06:28 has one nudge naming Nimbus, Orbit and Kestrel, with a draft.
     - Orbit does not offer "Yes, ask the team" while the row says "no reply".
     - After the team note is marked sent, no row on any tab says "Draft coming at the next check".
4. **Nothing late vanishes.**
   - Aditi, windowed to Fri 30: "Write the portfolio highlights paragraph" is a row or a push clause at every morning from Tue 27 until Done.
   - Vikram's Today shows "Aditi owes you: the portfolio highlights paragraph" from Tue 27.
   - Meera, variant A: Fri 30 06:29 still asks "Halo Reconcile: met 22 Oct, add the next step". The headline counts it as a next step, not a meeting to log.
5. **Words at every hour.**
   - No push in any windowed run to Fri 30 ends in "…". Today, Rohan's Thu 29 15:25 push does.
   - No Today line is just "<Name> wrote on <date>." (Aditi, Fri 09:24).
   - Meera's Thu 19:29 line reads "Deal: Rivulet Payments moved to Second meeting".
   - Vikram's Thu 06:20 letter row reads "Draft ready: check the figures, then send it".
   - Aditi's Mon 26 Solace form does not prefill a step due 23 Oct.
6. **QA shows what the user sees.**
   - `met-step-380.png` shows the step-only row before Save. Today it shows the page after Save.
   - A new scenario renders an ask after its follow-up note is sent and finds no "Draft coming".

## Reproduce

- **Scratch copy:** `/tmp/vc-panel-r9/repo` (code at 070b9d8, with `evals/runs/council/briefs-r9` copied in). My runs regenerated its screenshots, `qa.json` and `evals/scorecard.md`. I changed nothing in the real repository except this report.
- **Suites:**
  - `python3 evals/runner.py`
  - `python3 evals/runner.py --suite round9`, and the same for `round8`, `round7`, `round6`, `round6b`, `evals6`, `evals8` and `guard`
  - `python3 evals/design_lint.py`
  - `python3 evals/home_qa.py`
- **Scripts:** in `/tmp/vc-panel-r9/scripts/`. Each takes the repo path first.
  - `dump_week.py <repo> <outdir>`: every `_week` run for all seven (push and subjects, hero, rows, drafts in full, met logs, Pipeline).
  - `window_vs_full.py <repo>`: the windowed week against `_week`, run by run, for all seven.
  - `mornings_to_fri30.py <repo> <outdir>`: every member on real windows to Fri 30, no taps.
  - `meera_steps.py <repo> A|B`: blank-step met logs, without (A) or with (B) a step typed on Friday, for Meera and Aditi to Fri 30.
  - `meera_moved.py <repo>`: the lowercased stage-move line.
  - `meera_fri_home.py <repo> <out.json>`: Meera's Friday Home with the step requests, for rendering.
  - `tara_week.py <repo> intro|quiet`: "Sent it" at Thu 10:00, with or without Aditi's intro email.
  - `tara_team_instead.py <repo> <out.json>`: "Ask the team instead" on Thu 29, the note written, then sent.
  - `tara_thu29_home.py <repo> <out.json>`: Tara's Thu 29 Home with Aditi quiet.
  - `vikram_call_sent.py <repo> tap|mail [member]`: the chase marked sent, for Vikram or `solo`.
  - `holder_trace.py <repo>`: traces `_owed` at the `holder` lines.
  - `dump_home.py <repo> <member> "<Day HH>" <out.json>`: the Home a `_week` run left.
  - `render_home.py <repo> <home.json> <ISO time> <member> <out.png> [tab] [row filter]`: renders a Home in the real page with the QA harness and prints what the user reads.
  - `crop.py`: cuts tall phone screenshots.
- **Outputs:** dumps in `/tmp/vc-panel-r9/dump/`, renders in `/tmp/vc-panel-r9/shots/`, crops in `/tmp/vc-panel-r9/crops/`.
- These folders are temporary.
