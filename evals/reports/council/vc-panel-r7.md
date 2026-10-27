# Instinct for VCs: VC panel, round seven

**This is a simulated panel. No real investor took part.** One Claude agent played all seven: six people at the fictional Quillwater Ventures (Aditi Rao, Partner; Kabir Shah, Principal; Meera Iyer, Associate; Rohan Das, Analyst; Tara Menon, Head of Platform; Vikram Nair, CFO and IR) and a solo GP running a $30M fund alone.

**What I read and ran**
- My round-six report, the round-seven packs (`evals/runs/council/briefs-r7`), the Home screenshots (including `met-log-380.png`, `waiting-founder-380.png` and every `level-*-today-380.png`), the diff from 20039da to 81c3e95 (0.6.0) and the "Round seven" section of `BUILD_LOG.md`.
- **Tests, run in a scratch copy** (`/tmp/vc-panel-r7/repo`):
  - `--suite round7`: 10 of 10.
  - `--suite round6`: 4 of 4. `--suite round6b`: 8 of 8. `--suite evals6`: 8 of 8.
  - Full runner: 133 of 133. Guard: 574 of 574. Design lint: 0 violations.
  - Home QA: 403 of 403, read from `qa.json` (not re-run).
- **My own replay:** every run from Thu 22 Oct to Mon 26 Oct for all seven, through `replay._week`. On top of it:
  - every draft in full, and every open draft's times on each morning, across all Homes;
  - when each owner's "met" log first appears;
  - Tara's week replayed with "Sent it" tapped on her three ask notes;
  - Aditi's Pipeline rebuilt after Meera's met logs, saved the way Home fills them in;
  - a `pending_actions` probe ("Move to Closing") and a `drafts` command probe (does an ask note keep its link?).
- The README's sample link, read with the Artifact tool.
- **Drafts in the replay come from `evals/demo.py`**, not from Claude. I judged whether the engine asks for the right draft at the right time with the right inputs. Where only the demo wording is off, I say so.

## In short

- **Round seven delivered most of round six's list.**
  - On Monday, no open draft in any Home offers a past time: 0 of 73.
  - Tara's three founder asks have notes on her first morning. Vikram's Q3 letter is drafted on Thursday from the KPIs and the LP list, gaps marked.
  - Every deal owner gets a "met" log within one run of each founder meeting.
  - Pass replies give the reason that decided the pass. Own work leads. What a push names stays on Today.
- **What keeps everyone below 9.5:**
  - The README's sample link still opens an old build with no "View as" (round-six ask 5, wanted by all seven).
  - The real run does not match the replay for asks and the letter. The morning-brief skill does not describe them, and the `drafts` command drops an ask note's `action_id`.
  - The met log, saved as Home fills it in, does not clear the deal in a colleague's Pipeline. The round-seven test passes only because it also resets the stage date, which no tap does.
  - Ranking still misses at the top: a chore due today beats late founder promises, a heads-up skips what you owe the person you are about to meet, and an LP touch ten weeks out leads Vikram's Monday.
  - New small embarrassments: "Us-India" in four founder emails, "Hi all" team notes for a solo GP, one colleague's hour offered twice across two Homes, and "Move to Closing" refused by the engine.

## Scores

| Persona | Level | R6 | R7 | Why, in one line |
|---|---|---|---|---|
| Aditi Rao | Partner | 8.5 | 9 | Monday's pushed paragraph stays on Today all day, and the sync line names her own votes. But Monday's push picks that internal paragraph over three late founder promises, and her Pipeline still calls freshly met deals Stale on Sunday. |
| Kabir Shah | Principal | 8.5 | 9 | Every draft now offers future times and knows about Thursday's meetings. But Tue 27 Oct at 10:00 and 11:00 are offered twice: by him to Rohit, and by Rohan to Rhea for "a call with Kabir". |
| Meera Iyer | Associate | 8.5 | 9 | A met log within one run of each of her three Thursday meetings, and the Harborline reply has fresh times. Two drafts are still bracket skeletons, and Monday opens on a list due today while Omkar's feedback is 7 days late. |
| Rohan Das | Analyst | 8 | 8.5 | Today is down to 12 lines and pass replies give the real reason. But two founders read "India and Us-India", and Vaultline loses "until next week" for seven runs before the meeting it is on. |
| Tara Menon | Platform | 8 | 8.5 | All three asks have a note the first morning. But the team notes have no recipient, ask the team to source before Aditi is asked, and an ask never moves past "Intro requested". |
| Vikram Nair | CFO and IR | 8 | 8.5 | The Q3 letter is drafted with gaps marked, and Friday's push and row agree. But the 14:20 heads-up for Helen skips her 43-day-late answer, and Monday's list still opens on an LP touch ten weeks out. |
| Solo GP | $30M, alone | 8 | 8.5 | No slot clash and no "partner prep" title. But two drafts go "To Your team" saying "check with the board partner": she has no team, and she is the board. |

- **Average: 8.7** (round six: 8.2).
- **Quillwater's six: 8.75** (round six: 8.3).
- All seven went up. Three reach 9. None reaches 9.5.

## Round-six asks and the ten 9.5 tests

| Item | Verdict | Evidence |
|---|---|---|
| Ask 1: drafts true on the day, and finished | Mostly | Monday: 0 of 73 open drafts offer a past time (Aditi 3, Kabir 4, Meera 6, Rohan 20, Tara 5, Vikram 2, solo 33). Kabir's Rohit draft moves from "Fri 23 Oct at 10:00" (Thu) to "Mon 26 Oct at 11:00" (Fri) to "Tue 27 Oct at 10:00" (Mon). Drafts written before a meeting gain "Good to see you on Thu 22 Oct". Asks and the letter are drafted without a tap. Gaps: "Us-India"; the skill a real run follows; one hour offered twice across two Homes. |
| Ask 2: clean words, last mile | Mostly | "Week ahead: 1 meeting, decide Gravity Payouts by 31 Oct, 3 promises late" (Aditi, Sun 17:24). `look like?" Deal: 9 days` (Meera, Mon 06:29). "You owe: sign off on the capital account statements" (Vikram, Thu 07:20). "Last met 20 Oct" (Meera, Thu 15:29). "We do not invest in D2C". New: "(India and Us-India)" in four founder emails; "is looking for intro to two banks"; "10:00 Orbit Treasury: Vikram asked: intros to senior engineers: hiring two this quarter". |
| Ask 3: pushed stays, own work first | Mostly | Aditi's "Write the portfolio highlights paragraph" is on Today at all 14 Monday runs, 06:24 to 19:24. Kabir's Thursday list: "Forward the Cobalt AA notes" first, "Rohan Das owes you" second. Vikram's Monday push: "Model the runway scenarios: Neel (Kestrel Pay), 10 days late". Gap: Vikram's Monday list still opens on "LP: Banyan Family Office: Re-up window opens 05 Jan", marked Overdue. |
| Ask 4: one tap after a founder meeting | Partly | The prompt comes within one run of every meeting: Meera Sable 10:29, Rivulet 13:29, Halo 17:29; Kabir Lumen 10:28, Kite 12:28, Prism 17:28; Rohan Paysa 11:25, Ruplink Fri 15:25; Aditi Atlas 11:24, Gravity 15:24, Beacon Fri 12:24. But one tap on Save writes the CRM's old step back ("Second meeting", due 24 Oct, "Still First meeting"), and Aditi's Pipeline on Sun 17:24 and Mon 06:24 still shows Halo, Rivulet and Sable as Stale. "Move to Closing" is refused. |
| Ask 5: real product at the README link | Not met | The page at the link has 0 "View as", 0 "Draft ready", 0 met logs and 0 "Intro requested". |
| Test 1: what was pushed stays put | Met | round7: 0 dropped. Aditi's Monday paragraph is a Next up row at every run, 06:24 to 19:24. |
| Test 2: no dead or double slots | Met, within each Home | 0 past and 0 repeated times at every morning run in each Home. Solo's Harborline reply offers "Wed 28 Oct at 12:00 or Wed 28 Oct at 14:00", shared with no other draft. Across Homes, see Kabir. |
| Test 3: drafts after meetings | Met | Kabir's Monday Kite draft: "Good to see you on Thu 22 Oct." Rohan, Mon 06:25: "Coinvault Exchange: ... Pass reply drafted 22 Oct: send it, then move the deal to Passed" (Glowkart the same). |
| Test 4: pass reasons match the engine | Mostly | All 25 pass replies (Rohan 12, solo 13) give the engine's deciding reason. Zorro Pay and Ledgerly name geography. Glowkart: "We do not invest in D2C". But: "It is outside the regions we invest in (India and Us-India)". |
| Test 5: own work first, everywhere | Met | Vikram's Mon 06:20 push is his own late work. Kabir's own late promise sits above what Rohan owes him. |
| Test 6: team calendar truth | Partly | The owner's prompt comes on time. With the stage moved, Aditi's Saturday Pipeline is clean (round7 test 6). With Save as Home fills it in, Sun 17:24: Halo "15 days in first meeting, past the 7-day mark, Next step was due 24 Oct", Rivulet the same, Sable "Next step was due 24 Oct". The test resets `stage_entered` without changing the stage, which no tap does. |
| Test 7: clean words | Met | round7: 0 found across every Today line and push. Every week-ahead line has two or three parts. Drafts are outside this test; see "Us-India". |
| Test 8: founder asks, finished | Partly | 3 of 3 asks have a note at Thu 06:28. The 14:30 dinner line: "They asked: intro to two banks as customers. Path: Aditi knows Raj Malhotra". States: "Asked 17 days ago", then "Intro requested on 22 Oct" after "Sent it". No "intro made" or "closed". Team notes have no recipient. |
| Test 9: finance deliverable, drafted | Met, in the replay | Thu 06:20: "Q3 LP letter: draft for your review", with "Fund II: $80M, 45% called", six companies against plan, a watch list and bracketed gaps. Fri 06:20: push "Due today: sign off on the capital account statements and Q3 LP letter draft", row "due Sat 24 Oct, so today". The skill a real run follows still calls the letter work "the user can ask for". |
| Test 10: Today short, link current | Partly | At most 12 lines every morning (Meera and Rohan sit at 12). Flagged pitches show on Thursday only. The link is old. The solo view has no "partner prep, meeting or sync" in Today, but has two "To Your team" drafts, "check with the board partner", "Partner meeting Monday" in a proposal and "Partner vote" in a met log. |

## Still wrong, per persona

**Aditi (partner)**
- **Mon 06:24, push:** "Write the portfolio highlights paragraph: Vikram, due today". On the same Today, three founder promises are late:
  - "Send the term sheet markup ... 3 days late" (Atlas, with Bluepeak's term sheet on the table);
  - "Intro Arjun to Raj Malhotra at Fable Bank ... 6 days late";
  - "Share the co-op bank partnership deck ... 3 days late".
  - The rule "a deadline day always wins" picks the internal chore.
- **Sun 17:24 and Mon 06:24, Pipeline:** if Meera saves her three met logs as Home fills them in, Halo, Rivulet and Sable are still Stale for Aditi ("15 days in first meeting, past the 7-day mark", "Next step was due 24 Oct"). The form pre-fills the CRM's old step and "Still First meeting", and a fresh CRM last contact does not stop the dwell rule.
- **Fri 08:24, push:** "10:00 Orbit Treasury: Vikram asked: intros to senior engineers: hiring two this quarter". This is a board meeting at 8.0 months of runway, with her deck review a day late. Both facts were skipped because the board-eve line named the company the night before.
- **Thu 13:24 and 15:24, Next up:** "Decide on Beacon Credit Rails" and "Decide on Ironwood Compliance" come back at the first run after the 12:00 sync that voted on them.
- **Thu 09:24 and 10:24, agenda:** the sync line "And 9 more, with yours: Atlas Settlement, Beacon Credit Rails and 2 more" drops out under her 200-word budget, and returns at 11:24.
- **Met log:** "Move to Closing" for Atlas Settlement (offered Thu 11:24) or Beacon Credit Rails (Fri 12:24) is refused at the next check: "A next step moves a deal forward, never to passed or closed." The step and the last contact go with it.
- **Fri 06:24, refreshed intro draft:** "Hi Raj, Arjun, Good to see you on Thu 22 Oct." Raj was not in the meeting. Demo wording, but the refresh entry carries only the meeting date, not who was there.
- **Thu 15:24:** "Review ready: Decide on Beacon Credit Rails" is deferred (she is in the Gravity meeting) and never sent, though Friday has room.

**Kabir (principal)**
- **Mon 06:28, Ready for you:** the Rohit draft offers "Tue 27 Oct at 10:00 or Tue 27 Oct at 11:00". Rohan's open draft to Rhea (Paysa), written Fri 06:25, offers "a call with Kabir" at the same two hours. Both founders can say yes to 10:00. Each Home avoids only its own drafts, and Rohan's times come from his own calendar ("Slots from your calendar").
- **Fri 06:28 to Mon, Kite draft:** "Good to see you on Thu 22 Oct. As promised at our check-in on 19 Oct, here is our diligence checklist. Thanks for the customer reference list and the security audit report you are sending over." The meeting is named; the rest still speaks from 19 Oct. Demo wording; the engine did ask for the rewrite.
- **Thu 15:28:** "Review ready: Banyan Risk Cloud: no next step set" is deferred behind the Prism heads-up and never sent. Friday has one push. Meera's review (Thu 15:29) goes the same way; only Rohan's review is ever pushed.

**Meera (associate)**
- **Thu 06:29, drafts:** Omkar's feedback and Neha's pricing view are still three bracketed lines each. Unchanged since round six.
- **Thu 17:29, met log for Halo:** it pre-fills "Second meeting" by 24 Oct and "Still First meeting", though the 16:30 meeting was the second meeting (the invite reads "Halo Reconcile: second meeting"). One tap writes stale facts to the CRM.
- **Mon 06:29, hero and push:** "Share our NBFC partner list: Leena (Ember Credit), due today". Below it, Omkar's feedback is 7 days late, on a deal where he wrote "The round is almost full now, so we'd need to hear back soon."
- **Fri and Mon:** "12 things for today", with 5 and then 6 urgent, plus four met-log forms in Ready for you that the 12-line cap does not count.

**Rohan (analyst)**
- **Thu 06:25, pass drafts to Zorro Pay and Ledgerly:** "It is outside the regions we invest in (India and Us-India)". The engine's `why_pass` title-cases "us-india". Ledgerly is a US company; the rule needs words a founder can read.
- **Sun 09:25 to Mon 09:25 (seven runs), Vaultline row:** only "Raise it at the 10:00 Monday partner meeting." Tanvi's "we've kept a small allocation for Quillwater until next week" is cut by the word budget. This is the window where Monday's heads-up says "yours: Vaultline". The quote is back at 10:25, after the meeting starts.
- **Fri 06:25, Rhea draft:** "let's set up a call with Kabir. Would Tue 27 Oct at 10:00 or Tue 27 Oct at 11:00". Times from Rohan's calendar only; Kabir offers the same hours to Rohit on Monday.
- **Mon 06:25:** Paysa and Ruplink still sit under "Inbound worth a look" ("you met them on 22 Oct", "on 23 Oct"), next to their met logs.

**Tara (platform)**
- **Thu 06:28, drafts "Can anyone help Kestrel Pay?" and "Can anyone help Orbit Treasury?":** no address in To. "Open in Gmail" opens a message to no one. The firm members are in her config.
- **Same drafts:** "Who knows someone who fits? One flag before we source: runway under 9 months: check with Aditi before sourcing." The note asks the team to source, and to check with Aditi first, in one email to everyone. With a warning, the first note should go to Aditi.
- **Thu 13:28, push:** "14:30 Founder community: Divya asked: intro to two banks as customers (13 Oct)". No path and no "note ready". The hero adds "Last spoke 16 Oct: Community event".
- **With "Sent it" tapped at Thu 10:00 (my replay):** rows read "Intro requested on 22 Oct. ... No warm path found: ask your team". A team note is not an intro request. Nothing moves past "requested" through Monday, and nothing nudges.
- **In a real run:** the morning-brief skill does not describe `kind: "ask"`, and `drafts` keeps `commitment_id`, `inbound_id` and `question_id` but not `action_id`. A note written to the skill's step 7 shape is stored with no link (checked in the scratch copy). The ask rows would show neither "Draft ready" nor "Intro requested".

**Vikram (CFO and IR)**
- **Thu 14:20, push:** "15:30 Northgate Endowment: LP: $8M committed, $3.6M called, re-up window opens 10 Jan". He is about to meet Helen, whose fee offset answer is 43 days late with a draft ready. The push leaves it out because the 06:20 push named it.
- **Mon 06:20, Next up:** opens with "LP: Banyan Family Office: Re-up window opens 05 Jan; no touch in 84 days", marked Overdue, above "Answer the fee offset question ... 47 days late".
- **Fri 06:20, Today:** "Q3 LP letter draft: ... due Sat 24 Oct, so today" is the last row, under "Commitments due", after "Signals". The push leads with it; the list does not.
- **Thu 06:20, letter draft:** "Orbit Treasury: $198K revenue in 2026-09" (a raw month), 6 of 12 companies, and Ferro's 22.6% miss listed under "Portfolio highlights".
- **In a real run:** morning-brief step 1 still says the letter is work "the user can ask for". `kind: "letter"` is in neither the skill nor `shared/engine.md`.
- **Fri 06:20, refreshed Helen draft:** "Good to see you on Thu 22 Oct. ... Glad to go through it when we meet today." Demo wording.

**Solo GP**
- **Thu 06:24, `level-solo-today-380.png`:** "Draft: Can anyone help Kestrel Pay? To Your team", and the same for Orbit. The body: "Hi all, ... check with the board partner before sourcing." She has no team and is the board partner.
- **Fri 06:24, Zorro Pay and Ledgerly:** "(India and Us-India)", as for Rohan.
- **Thu 06:24:** two emails to Raj Malhotra on one morning (the Arjun intro with Raj in cc, and "Intro: Nimbus Collect"), with no line linking them.
- **Same screen:** "Gravity Payouts: next step from your notes on 15 Oct" still shows "Partner meeting Monday" as the current step, and "Solace Treasury: met 21 Oct" says "It still says next: Partner vote" with "Still IC". The solo replays the partner's CRM.
- **Met log:** "Move to Closing" is refused for Atlas and Beacon, as for Aditi.

## Top five changes

1. **Make the real run match the replay, and publish it (7 of 7).**
   - Publish the current demo at the README's sample link, and check its hash against `qa.json`. It is the link all seven would forward.
   - Describe `kind: "ask"` and `kind: "letter"` in morning-brief step 6 and in `shared/engine.md`. Delete "say so in context so the user can ask for it".
   - Make `drafts` copy `action_id` from `owed.json`, as it does `commitment_id`.
   - Run one Claude-run eval of Tara's and Vikram's Thursday briefs, scored on "Draft ready" on each ask row and on the letter row.
2. **Make the met log one tap that clears the team's Pipeline (4 of 7: Aditi, Meera, Rohan, solo).**
   - Pre-fill from the meeting, not from the CRM's old step: the stage the invite implies ("second meeting": Move to Second meeting) and a next step dated after the meeting.
   - In every Home, treat a CRM last contact in the last five working days like a calendar meeting: not stale for dwell or for a missed step.
   - Accept "Move to Closing". Refuse only Passed, Lost and Won.
   - Test the tap through `pending_actions` and the pulse, not by editing the CRM.
3. **Rank by what it costs to miss (4 of 7: Aditi, Meera, Rohan, Vikram).**
   - A meeting heads-up names what you owe the person you are about to meet, even if the morning push named it.
   - A chore due today does not outrank a founder promise 3 or more days late on a deal with a rival.
   - An LP touch more than 30 days before its window is never "Overdue" and never first.
   - A Saturday deadline ranks as Friday's work in the list, as the push already says.
   - Under the word budget, cut "Raise it at..." before the founder's words, and keep the sync's "with yours" line.
4. **Times and rewrites that hold for everyone in the email (5 of 7: Aditi, Kabir, Rohan, Vikram, solo).**
   - A call with a colleague takes times free on both calendars, and those times count as held in the colleague's Home too.
   - A refreshed draft knows who was in the meeting, greets only them, and drops lines the meeting made false.
   - Give the refresh entry the attendees and the notes link, so Claude rewrites rather than prepends.
5. **Founder asks and founder-facing words, last mile (4 of 7: Aditi, Rohan, Tara, solo).**
   - Team notes go to the firm members in config. When an ask carries a warning, the first note goes to the board partner.
   - A solo GP gets no "Hi all", "Your team" or "board partner". With no warm path, offer people from her own network, or say there are none.
   - States that move: asked, note ready, requested, made, closed. A nudge after five working days. A team note reads "Asked the team on 22 Oct", not "Intro requested".
   - The heads-up before the dinner names the path and the ready note.
   - "US-India", in a reason a founder can read ("We back companies building in India, or US companies with a team in India"). "An introduction to", not "intro to". The solo view filters partner wording that comes from the CRM.

## Reaching 9.5: tests on the same replay

1. **Real runs keep the links.** Write Tara's Thursday `owed.json` notes in the skill's step 7 shape and run `drafts`. Every ask note keeps its `action_id`. Home shows "Draft ready" on all three ask rows, and "Sent it" moves each to the next state. The skill names `kind: "ask"` and `kind: "letter"`.
2. **The shared link is current.** The page at the README's sample link contains "View as", and its hash matches `qa.json`.
3. **Heads-ups name what you owe.** Vikram's Thu 14:20 push names the fee offset answer. Aditi's Fri 08:24 push names the runway or the deck, not "intros to senior engineers".
4. **Late founder promises beat chores.** On Monday, Aditi's 06:24 push and Meera's 06:29 hero name a founder promise 3 or more days late on a deal with a rival (the Atlas markup; Omkar's feedback), or name it alongside the chore.
5. **The CFO's list.** At Mon 06:20, Vikram's first Next up row is his own late work, and no LP row more than 30 days from its window says "Overdue". At Fri 06:20, the Q3 letter row sits in Next up, above every LP touch.
6. **Words survive the budget.** Every Rohan run from Sun 09:25 to Mon 09:25 keeps "until next week" on the Vaultline row. Every Aditi run from Thu 06:24 to 11:24 keeps "with yours" on the sync line.
7. **No hour offered twice across the team.** At every morning run, across all six Quillwater Homes, no time sits in two open drafts that involve the same person. A "call with Kabir" counts as Kabir's.
8. **Refreshes tell the truth.** No refreshed draft says "Good to see you" to someone who was not in the meeting (Raj, Fri 06:24), and none says "when we meet today" about a meeting already held (Helen, Fri 06:20).
9. **One tap clears the team's Pipeline.** Meera saves each of her three met logs as Home fills them in, through `pending_actions` and the pulse. Aditi's Pipeline then shows none of Halo, Rivulet or Sable as Stale on Saturday, Sunday or Monday. Approving "Move to Closing" with a step for Atlas gives a pending action, not a refusal.
10. **Asks addressed, words clean.** Tara's team notes have firm addresses in To. With a warning (Orbit, Kestrel), the first note goes to Aditi. Tara's Thu 13:28 push names "Aditi knows Raj Malhotra". An ask requested five working days ago with no reply shows a nudge. No draft contains "Us-India" or "for intro to". The solo Home contains no "Hi all", "Your team", "board partner", "Partner meeting" or "Partner vote" in any row, proposal, met log or draft.

## Reproduce

- Every check ran on a scratch copy at 81c3e95: `/tmp/vc-panel-r7/repo`. I changed nothing in the repository except writing this report.
- Replay dumps, one per persona: `/tmp/vc-panel-r7/dump/`.
- Scripts, each taking the repo path first: last round's in `/tmp/vc-panel-r7/` (`dump_week.py`, `checks.py`, `check_vis.py`, `check_drafts.py`, `check_mon.py`), and this round's in `/tmp/vc-panel-r7/scripts/` (`met_prompts.py`, `vaultline.py`, `drafts_full.py`, `tap_week.py`, `crop.py`).
- These folders are temporary.
