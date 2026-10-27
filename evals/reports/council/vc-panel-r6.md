# Instinct for VCs: VC panel, round six

**This is a simulated panel. No real investor took part.** One Claude agent played all seven: the six people at the fictional Quillwater Ventures and a solo GP. The agent returned this report as text, as in round five, and the lead session saved it here. I did not write any files into the repo.

**What I read and ran**
- My round-five report, the round-six packs (`evals/runs/council/briefs-r6`), the screenshots, `BUILD_LOG.md`, and the diff from 0c68ca6 to HEAD (bc6d847 and 20039da).
- **Test suites, run in a scratch copy:**
  - `--suite round6`: 4 of 4 pass.
  - `--suite round6b`: 8 of 8.
  - `--suite evals6`: 8 of 8.
  - Full runner: 123 of 123.
  - Home QA: 388 of 388, read from `qa.json` (not re-run). The page hash matches `home/index.html`.
- **My own replay:** every run from Thu 22 Oct to Mon 26 Oct for all seven, through `replay._week`. On top of it I added checks on pushes, open drafts, slots, the Monday pack and Pipeline rows.
- **Drafts in the replay come from `evals/demo.py`** (templates and hand-written examples), not from Claude. I judged them as the demo shows them.

## In short

- **Round six fixed most of what round five asked.**
  - Pushes now fit the day: 51 pushes, none inside a meeting or its 15-minute lead-in, never more than four a day.
  - The sync pack is one list for the whole room.
  - Calendar truth holds in each deal owner's own Home.
- **What keeps everyone below 9:**
  - Drafts go stale. On Monday, 7 open drafts across four people still offer Thursday or Friday slots.
  - A handful of lines still read as machine-made.
  - Some work is found but not finished: Tara's intros, Vikram's letter.
- **The README's "sample Instinct Home" link opens an older build.** It has no "View as" switcher, so new readers cannot see the seven role views the README promises.

## Scores

| Persona | Level | R5 | R6 | Why, in one line |
|---|---|---|---|---|
| Aditi Rao | Partner | 8 | 8.5 | Four pushes Thursday, none in a meeting, and one pack for the room. But Monday's pushed paragraph leaves Today an hour later, and her Pipeline calls five freshly met deals Stale. |
| Kabir Shah | Principal | 8 | 8.5 | Lumen's agenda is right, and Thursday opens on his late Kite checklist. But Monday's "Draft ready" to Rohit still offers Friday 10:00 or 11:00. |
| Meera Iyer | Associate | 7.5 | 8.5 | Halo stays honest to Monday, and Copperleaf's unanswered question is found, quoted and drafted. Two of her five drafts are still bracket skeletons. |
| Rohan Das | Analyst | 7.5 | 8 | Colleagues' races are now one grey line. But Monday's hero draft offers Friday's slots, and two pass drafts tell fintech founders they are outside fintech. |
| Tara Menon | Platform | 7.5 | 8 | Every ask now names a path or says "none found", with the cash warning. No intro is drafted until she taps, and an ask never moves past "Asked". |
| Vikram Nair | CFO and IR | 7 | 8 | The Q3 letter is on Today and in Friday's push. Monday's push is an LP window ten weeks out, and "Instinct can draft it" is a phrase to type, not a draft. |
| Solo GP | $30M, alone | 7.5 | 8 | Own calendar, own $30M fund, 30 replies over two mornings. Friday's Harborline draft offers two Monday slots already offered on Thursday. |

- **Average: 8.2** (round five: 7.6).
- **Quillwater's six: 8.3** (round five: 7.6).
- All seven went up. None reaches 9.

## Round-five asks and the ten 9.5 tests

| Item | Verdict | Evidence |
|---|---|---|
| Ask 1: pushes that fit the day | Mostly | 0 of 51 pushes land inside a meeting or the 15 minutes before one. At most 4 a day for everyone. Aditi's Friday 10:24 push is gone: the 12:00 Beacon heads-up now goes at 09:24. But Aditi's Mon 06:24 push names "Write the portfolio highlights paragraph", and that row leaves Today at 07:24 and stays gone until 19:24. |
| Ask 2: clean words, real quotes | Mostly | Founders' words stay in quotes ("until next week", "our Series A"). Colleagues' shared notes are given as summaries. No cut text ("…") all week. Cobalt is one row ("Deal: next step was due 15 Oct."). New slips: "Week ahead: 1 meetings" (Aditi, Sun 17:24); `?". Deal:` (Meera, Mon 06:29); `next week.".` (Rohan, Sun and Mon); "We do not invest in d2c". |
| Ask 3: calendar truth past the weekend | Partly | In each owner's Home, Halo, Rivulet, Sable, Paysa, Ruplink and Prism are not Stale through Monday. Halo reads "Looks done: you met them on Thu 22 Oct" on Friday. But no CRM update is offered after any meeting: 0 proposals in all seven Homes through Monday. And Aditi's Pipeline shows Halo, Rivulet, Sable, Paysa and Ruplink as Stale on Sunday and Monday. |
| Ask 4: own work first | Mostly | Rohan gets one grey line, last: "7 deals your colleagues lead have a competing fund". Owners keep the founders' words and dates. But Kabir's Thursday Next up opens with "Rohan Das owes you: market map" above his own late "Forward the Cobalt AA notes". And Vikram's Monday push is "Banyan Family Office: re-up window opens 05 Jan". |
| Ask 5: right line, right place, right weight | Mostly | Lumen's agenda shows "They owe: send the updated deck with Q3 numbers (13 days late)", with no Vertex. The Q3 letter is on Today Thursday and Friday and in Friday's push. It still sits under "Commitments due", below four other rows. |
| Test 1: one pack for all, every field | Met | Thursday 12:00 sync: the same 12 rows for Aditi, Kabir and Meera, with Sterling AA under "Stalled". Monday 10:00: the same 12 rows for Aditi, Kabir, Meera and Rohan. Rows read "Lead: Meera · Partner: Aditi · Seed $2.5M". |
| Test 2: pushes fit the day, all visible | Mostly | 0 of 51 inside an event or its 15-minute lead-in. Thursday maximum is 4. Every pushed item is on Today when pushed, but Aditi's Monday paragraph is gone an hour later. |
| Test 3: "N days late", Kite on Thursday | Met | "Sanjay owes you: share the co-lending partner data, 8 days late" (Kabir, Thu 15:28). "Share the diligence checklist: Siddharth (Kite Pay), 2 days late" (Thu 06:28). |
| Test 4: calendar truth to Monday | Partly | Met in each owner's Home, and Gravity is not Stale on Monday. Not met in Aditi's Pipeline on Monday, where all of these show Stale: Halo "16 days in first meeting"; Rivulet and Sable "Next step was due 24 Oct"; Paysa "5 days in inbound"; Ruplink "9 days in inbound". |
| Test 5: Rohan's colleague line | Met | One low-weight "Your team" line, after his pitches. |
| Test 6: founders' words kept | Met | Vaultline keeps "until next week". Trellis keeps "our Series A". |
| Test 7: Lumen's agenda | Met | Maya's Q3 deck is under Lumen. Vertex is its own row in Next up. |
| Test 8: Vikram's Q3 letter | Met | On Today Thursday and Friday. Fri 06:20 push: "Due today: sign off on the capital account statements and Q3 LP letter draft". Shows "Instinct can draft it". Friday's Today row says "due tomorrow". |
| Test 9: Tara's asks | Partly | Path or "none found": yes. Nimbus has a path via Aditi to Raj Malhotra. Orbit and Kestrel say "No warm path found: ask your team". Intro draft: no, a tap asks for one at the next check. State: only "Asked 17 days ago". |
| Test 10: clean output and setup | Partly | 0 cut lines, 0 empty details, no slot offered twice in one morning, a reason on every pitch without a reply. Solo runs on its own calendar and $30M fund. But solo's Friday Harborline draft offers Mon 11:00 and 12:00, already offered on Thursday. The README sample link is an older build: no "View as", "Draft ready", "To decide" or guard banner in its code. |

## Still wrong, per persona

**Aditi (partner)**
- **Mon 06:24, push:** "Write the portfolio highlights paragraph: Vikram, due today". The row is on Today at 06:24. From 07:24 to 19:24 it is gone.
- **Sun 17:24, push:** "Week ahead: 1 meetings, decide Gravity Payouts by 31 Oct, 3 promises late".
- **Thu 13:24 and 15:24, Today:** two Urgent rows, both from deals Kabir leads:
  - "Lumen Ledger: two other funds in diligence (Kabir leads)"
  - "Kite Pay: Tamarind Capital wants to lead (Kabir leads)"
  - Their only detail is "From Maya's email, shared to the CRM by the deal team." The 12:00 sync had just covered both.
- **Sun and Mon, Pipeline:** five deals show Stale although the team met them:
  - Halo, Rivulet and Sable (Meera met all three on Thursday).
  - Paysa (Rohan, Thursday) and Ruplink (Rohan, Friday).
- **The board deck promise goes out three times in 26 hours:**
  - Thu 06:24: due today.
  - Thu 17:24: board tomorrow.
  - Fri 08:24: "You owe them: Review the board deck, 1 day late". This third push adds nothing.
- **Thu 06:24, Next up:** "Decide on Beacon", "Decide on Ironwood" and "Decide on Solace" repeat three votes already in the 12:00 sync pack.

**Kabir (principal)**
- **Mon 06:28, Next up:** "Schedule tech diligence with the CTO advisor, 3 days late · Draft ready". The draft asks: "Would Fri 23 Oct at 10:00 or Fri 23 Oct at 11:00 IST work for you?"
- **Fri 06:28, push:** the same "Draft ready", with slots only 3.5 and 4.5 hours away.
- **Thu 06:28, Next up** (also in `level-kabir-today-380.png`): "Rohan Das owes you: market map of AA players" sits above his own "Forward the Cobalt AA notes, 3 days late".
- **Mon 06:28, push:** "Share the diligence checklist: Siddharth (Kite Pay), 6 days late. Draft ready". The draft still cites the 19 Oct check-in and thanks them for reports "you are sending over", though they met on Thursday at 11:30.
- **Mon 08:28, heads-up:** "Decide on Gravity Payouts by 31 Oct, and 10 more". It does not say that his Kite Pay and Lumen Ledger are on that list.

**Meera (associate)**
- **Thu 06:29, drafts:** two are skeletons of three bracketed lines each. "Share our view on pricing" reads "[Our view, in one line] / [The one or two reasons] / [What would change our mind]"; the partner-meeting feedback draft has its own three. Honest, but they save little time.
- **Mon 06:29, Today:** `"...what would the timeline look like?". Deal: 9 days in first meeting (usually 7).`
- **Mon:** no CRM update is offered after Thursday's Halo, Rivulet and Sable meetings. Halo's row still reads "Next: Second meeting by 24 Oct", but that second meeting happened on Thursday.
- **Mon 06:29, Ready for you:** the Harborline reply still offers "Fri 23 Oct at 10:00 or Fri 23 Oct at 11:00".
- **Thu 15:29, hero:** "Last spoke 20 Oct: `Halo Reconcile <> Quillwater`", a raw invite title.
- **Fri and Mon:** "12 things for today" (5 and then 6 urgent).

**Rohan (analyst)**
- **Mon 06:25, hero:** "Set up a call with Kabir, 3 days late". The draft offers Fri 23 Oct at 10:00 or 11:00. His Tessera and Rupee Rails replies also still offer Friday slots.
- **Thu 06:25, pass drafts with the wrong reason:**
  - Zorro Pay (payment orchestration, Berlin) and Ledgerly (reconciliation, San Francisco) are told "It sits outside what we invest in, which is fintech infrastructure and B2B software for financial services".
  - The engine's real reason is geography: "Outside our geographies: Berlin, Germany" and "US only, no India link".
  - The cause: the demo template drops reasons that start with "Outside".
  - Glowkart gets "We do not invest in d2c".
- **Mon 06:25, Today:** Coinvault and Glowkart each say "book a first meeting or pass", though both pass replies were drafted on Thursday.
- **Mon 06:25:** 16 things on Today. Three are the same hidden-instructions warning (Prana, Paperplane, Snackbox), shown every morning since Thursday.
- **Sun 09:25 to Mon:** Vaultline's detail ends `until next week.".`

**Tara (platform)**
- **Thu to Mon:** Orbit and Kestrel say "No warm path found: ask your team".
  - Nothing is drafted until she taps "Draft a note to your team", and then only at the next check.
  - The only state an ask ever shows is "Asked 17 days ago".
- **Thu 06:28 to 13:28:** Nimbus shows under the 14:30 dinner as "They asked: intro to two banks as customers", with no path. "Warm path: Aditi knows Raj Malhotra at Fable Bank" first appears on Friday. The 13:28 push has no path either.
- **Mon 06:28, push:** repeats "Intro two CFO candidates: Rahul (Tallyfin), 5 days late. Draft ready", though she met Rahul on Thursday at 11:00.

**Vikram (CFO and IR)**
- **Mon 06:20, push:** "Banyan Family Office: re-up window opens 05 Jan", ten weeks away. Meanwhile his own work is late:
  - The Q3 LP letter: 2 days late.
  - The runway model: 10 days late.
  - The fee offset answer: 47 days late.
- **Thu to Mon:** "Instinct can draft it: say 'draft the quarterly letter'" is a phrase to type in chat. There is no draft and no button.
- **Fri 06:20:** the push says the letter is "Due today". Friday's Today row says "due tomorrow".
- **Sun 17:20, push:** "Week ahead: Peregrine Trust: owes $150K on a capital call". It does not sum up the week.
- **Thu 07:20, push:** "You owe: Sign off on the capital account statements", with a capital letter mid-line.

**Solo GP**
- **Fri 06:24:** the Harborline reply offers "Mon 26 Oct at 11:00 or Mon 26 Oct at 12:00". Thursday's open drafts already offered Mon 11:00 to Rhea (Paysa) and Mon 12:00 to Arnav (Tessera). Two founders could accept the same hour.
- **Thu and Fri drafts:** the same wrong Zorro Pay, Ledgerly and "d2c" passes as Rohan's.
- **Mon 06:24, Ready for you:** the Ruplink and Paysa replies still offer Friday slots.
- **`level-solo-today-380.png`:** Ready for you asks her to "Approve" "Gravity Payouts: next step from the partner prep on 15 Oct". A solo GP has no partner prep.
- **The board deck promise** goes out three times in 26 hours, as for Aditi.

## Top five changes

1. **Drafts that are true on the day you see them, and finished (6 of 7: Kabir, Meera, Rohan, solo, Tara, Vikram).**
   - Each morning, re-check every open draft. A past slot gets new slots. A slot already offered in any open draft is never offered again. On Monday, 7 open drafts across four people offer Thursday or Friday slots.
   - Rewrite a draft after a meeting with that person.
   - A pass reply uses the engine's reason. Fix the demo template that drops "Outside our geographies".
   - Finish the job without a tap: a ready draft for each founder ask (to the warm path, or to the team), and a ready Q3 letter draft for Vikram.
2. **Clean words, last mile (5 of 7: Aditi, Meera, Rohan, Vikram, solo).**
   - Plurals ("1 meeting").
   - No stray period after a closing quote.
   - No capital letter after "You owe:".
   - No raw invite titles.
   - Acronyms in capitals.
   - No row whose only detail is where the fact came from.
   - A week-ahead push that sums up the week for every level.
3. **What was pushed stays on Today, and your own work leads (3 of 7: Aditi, Kabir, Vikram).**
   - A pushed item stays on Today until it is done or the day ends.
   - Your own promises come before what others owe you, in the list as in the push.
   - "A late promise" in the morning line means a promise, not an LP touch window.
4. **After every founder meeting, one tap to update the CRM (3 of 7: Aditi, Meera, Rohan).**
   - The owner's Ready for you gets "Met Thu 22 Oct: set the next step" (with Copy change on a Sheet CRM).
   - Once it is applied, every colleague's Pipeline stops calling those deals Stale.
5. **Show the real product at the README link (7 of 7: it is the link each of them would forward).**
   - Publish the output of `evals/build_demo_page.py` to the "sample Instinct Home" link, and check its hash against `qa.json`.
   - Remove partner wording from the solo view.

## Reaching 9.5: tests on the same replay

1. **What was pushed stays put.** For every push Thursday to Monday, the item it names stays on Today (hero, a row, or a line under a meeting) at every later run that day, until it is done. Aditi's "Write the portfolio highlights paragraph" is on Today from Mon 07:24 to 19:24.
2. **No dead or double slots.**
   - At every morning run, every open draft offers only future slots.
   - No slot appears in two of one person's open drafts.
   - On Monday, 0 drafts offer past slots (today: Kabir 1, Meera 1, Rohan 3, solo 2).
   - Solo's Harborline reply shares no slot with the Paysa or Tessera replies.
3. **Drafts after meetings.**
   - Monday's Kite checklist draft (Kabir) mentions the 22 Oct meeting, or is flagged "written before your 22 Oct meeting".
   - Rohan's Coinvault and Glowkart rows say "pass drafted 22 Oct: move to Passed".
4. **Pass reasons match the engine.**
   - The Zorro Pay and Ledgerly replies name geography.
   - No reply says "outside what we invest in" to a company the engine marked "In thesis".
   - "D2C" keeps its capitals.
5. **Own work first, everywhere.**
   - Vikram's Monday push names his own late work (the Q3 letter or the fee offset answer).
   - Kabir's Thursday Next up lists "Forward the Cobalt AA notes" above "Rohan Das owes you".
6. **Team calendar truth.**
   - Within one run of each founder meeting on Thursday and Friday, the owner's Ready for you offers "Met on <date>: set the next step".
   - With those taps applied, Aditi's Pipeline shows none of Halo, Rivulet, Sable, Paysa or Ruplink as Stale on Saturday, Sunday or Monday.
7. **Clean words.** Across every Today row and push Thursday to Monday:
   - No "1 <plural>" (such as "1 meetings").
   - No `.".` and no `?".`.
   - No capital letter after "You owe:" or "You owe them:".
   - No row detail that only says where a fact came from.
   - No raw invite title such as `Halo Reconcile <> Quillwater`.
   - Every week-ahead push holds at least two of: meeting count, decisions with dates, promises late.
8. **Founder asks, finished.**
   - By Thu 07:00, each of Tara's three asks has a ready draft in Ready for you (to the warm path, or to the team).
   - Each ask has a state that moves: asked, intro requested, intro made, closed.
   - Thursday's 14:30 dinner line for Nimbus names "Aditi knows Raj Malhotra at Fable Bank".
9. **Finance deliverable, drafted.**
   - By Fri 07:00, Vikram's Ready for you holds a Q3 LP letter draft built from the portfolio KPIs and the LP list, with its gaps marked.
   - Friday's push and Today row agree on the due day.
10. **Today stays short, and the shared link is current.**
    - Every morning, Today has at most 12 rows at every level. A pitch warning shown one morning folds into the Pitches list the next. Rohan's Monday has 16 rows today.
    - The README's sample link opens the round-six demo with "View as" for all seven people.
    - The solo view contains no "partner prep", "partner meeting" or "partner sync".

## Reproduce

- The checks ran on a scratch copy. The repository itself is untouched.
- The scripts (`dump_week.py`, `checks.py`, `check_vis.py`, `check_mon.py`, `check_drafts.py`) and per-persona run logs are in `/tmp/claude-0/-home-claude/f41ebfd9-0635-5201-96ea-278169523f82/scratchpad`. That folder is temporary.
- Each script takes the repo path as its first argument and replays the week with `replay._week`.
