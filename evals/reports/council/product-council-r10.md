<!-- Product council, round ten. Written by one Claude agent playing all four members on a clean clone at 947db4c (0.7.5). Simulated: no real reviewer took part. Saved by the main session. -->

**This is a simulated council. No real reviewer took part.** One Claude agent played all four members.

# Instinct for VCs: product council, round ten

The members are a product manager, a product designer (Anthill Evergreen), an AI engineer (prompting, tool safety, the guard) and a QA lead. I reviewed commit 947db4c (version 0.7.5, the build's "round twelve") on 23 Oct 2026, in a fresh clone at `/tmp/r12-council`. I judged it against round nine (`evals/reports/council/product-council-r9.md`: average 8.25, no-go on 0.7.3) and its conditions J to P and F.

- The runner and Home QA rewrote tracked outputs. I ran `git checkout -- .` at the end, and the clone ended clean (`nothing to commit, working tree clean`).
- My own scripts and renders are in `/tmp/r12-council-scripts/`. The report is also at `/tmp/r12-council-report.md`.
- I did not change `/home/claude/instinct-vc`. I read three untracked report files there (the Claude-run reports, below) and ran `git status` and `git log` there once.

## What I read and ran

- Read:
  - the round-nine report;
  - BUILD_LOG.md ("Round eleven" and "Round twelve"), TRUST.md and README.md;
  - `shared/safety.md`, `shared/home.md` and `shared/engine.md`;
  - the pulse and morning-brief skills, `references/owed-kinds.md` and `hooks/guard.py`;
  - the full diff `a023dd2..947db4c` (117 files, +5275, -397).
- Ran, on the clean clone:
  - `python3 evals/runner.py`: 193 of 193 pass. 7 Claude-run rows are skipped (no saved runs). 253.5 s.
  - `--suite round11`: 16 of 16. `--suite round12`: 19 of 19. `--suite guard`: 718 of 718.
  - `python3 evals/home_qa.py`: 545 of 545. The page hash matches (a8cee518ad48). Colours: 48 states, 0 fails, lowest 3.24 (a mark).
  - `design_lint.py`: 219 rules, 0 violations. `engine lint`: ok.
  - `claude plugin validate .`: passes with warnings. With `--profile directory` it is refused (LICENSE_MISSING, PRIVACY_URL_MISSING).
- My own probes and replays:
  - 88 guard probes, fed to `hooks/guard.py` as PreToolUse JSON in four transcript layouts: the prompt as a string, meta rows first, the prompt in text blocks, and a normal session. All 352 came out as expected.
  - Reply probes on asks and on a capital-call chase, with taps and mail landing at set times, to Wed 4 Nov.
  - The note to the partner (`kind: "holder"`) over two weeks: unsent, sent and answered, one held draft sent, and with a quiet deal.
  - Two Pipeline steps four days apart, with the pulse's step 3 run every hour, using local and UTC tap stamps.
  - All seven members, no taps, every run to Mon 23 Nov (352 runs each). I checked the word budget, the item cap, pushes a day and cut pushes.
  - The money push week by week to Wed 25 Nov. A step request after a blank met log to Wed 25 Nov. An unsent nudge to Wed 2 Dec.
  - A "faithful" replay (`faithful.py`). It is the same harness, but the morning's drafts are written over the build's own output, row by row, as `cmd_drafts` writes them. I used it wherever the round-twelve harness differs from a real run (finding 10).
  - 12 Home states from those probes, light and dark, at 380 and 1440 wide. 48 renders: 0 contrast fails, lowest 3.24, 0 px overflow, no script errors.
- The three Claude-run evals on 0.7.5 (condition F):
  - None of the three had `evals/runs/<run>/report.md` in its scratchpad folder. Each agent's Write was refused ("subagents should return findings as text").
  - The main session saved the returned reports as untracked files in the source repo: `evals/reports/claude-runs/r12-friday-meera.md` (8 of 10), `r12-friday-tara.md` (8 of 10) and `r12-nudge-tara.md` (8.5 of 10).
  - I read them and reproduced their worst findings on the engine (findings 1 and 5).

## Scores

| Member | R9 | R10 | Why, in one line |
|---|---|---|---|
| PM | 8.0 | 7.5 | Five of seven conditions are met, and the new work (the note to the partner, partial replies, Friday sees Monday) is useful. But one natural Done can close a late promise to a founder as "sent". A reply that lands before Sent it is still "no reply". The note to the partner is drafted again after she answered, and it names a deal you marked quiet. "We paid last Friday" shows as a promise to pay. Still no real account. |
| Designer | 8.5 | 8.0 | Every new state is clean in both themes at both widths, and the new pointers help ("Note to Aditi ready, under Ready for you", "Monday:" links, "You replied"). But Done shows "Marked sent" and closes the other promise in a shared draft. An undated promise loses its draft buttons after the first check. Some lines state false things. A partial nudge row says "Nudge Aditi" and "Nudge ready" together. The late-work line takes Today over its item cap. |
| AI engineer | 8.5 | 8.0 | Both guard gaps are closed, the docs say exactly what is enforced, and 352 probes in four layouts hold. But a new draft kind breaks safety rule 6 (quiet deals). The holder note follows up without checking mail (round nine's 6.3 problem again). The new text reading is brittle: past days read as promises, any "fund" counts, and past facts are flagged as missed dates. And "since the note went" means "since the tap". |
| QA lead | 8.0 | 7.5 | 193, 16, 19, 718 and 545 are all green, and most of round nine's pin gaps are closed. But the suites pass over a high-severity defect and four mediums. The replay harness writes drafts unlike a real run. The weekly-money pin stops two weeks before its defect. Every reply pin taps Sent it first. Quiet deals in internal drafts, `people_partial` and the item cap with the late line are unpinned. |

**Average: 7.75** (round nine: 8.25).

## Round-nine conditions

| Condition | Verdict | Evidence |
|---|---|---|
| J. A nudge, a second chase or "no reply" only when the mail read holds no answer since the note went out. Pin both reply probes. | Partly met | Both round-nine probes are pinned and pass (round11). Partial replies and the AGM email are pinned too (round12). But a reply that lands before the user taps Sent it is never seen, for asks or for chases (finding 2). When the morning finds an answer the engine missed, the row and the push still say "no reply". |
| K. A chase keeps its sent record while the call is unpaid; never a first again, never a third. Pin to Mon 23 Nov both ways. | Met | round11 pin: Vikram and solo, with and without the second note: first again 0, third 0, "chased Peter" on Mon 23 Nov. My LP probes: no first note again and no third note in any variant. |
| L. Each Pipeline save is applied at the next run. Pin two steps four days apart, on the replay and in Home QA. | Met | My replay (`probe_l.py`): Thu 22 10:29 and Mon 26 10:29 both applied; with UTC stamps, Mon 26 11:29. Home QA `step-resaved` and `utc-step` show "saving". The round11 pin itself is a unit check of `pending_actions`. |
| M. A later tap takes the ask out of a waiting nudge; engine and Home pick an ask's draft by one rule. Pin on Today and Portfolio. | Met | "Aditi said yes" on Orbit at Thu 29 10:00 narrows the nudge to Kestrel and Nimbus at 10:28 (`probe_m.py`). Today and Portfolio agree in my renders (both themes, both widths). Pinned with "Ask the team instead" (round11, round12 #15). The "said yes" variant is not pinned. |
| N. "Before you send" on the prep sheet's drafts. Pin it. | Met | Home QA `prep-caveat`: "Before you send: You promised this on 20 Oct, due 23 Oct. Attach the markup before you send". |
| O. Fix findings 6 and 7, pin, docs exact. | Met | Artifact reads with `path`, `paths` or `out_dir` deny; a plain read and list pass. Verb-nouns at either end or alone deny; plurals at the end read. round11 pin plus my 352 probes. TRUST.md, safety.md and the guard's comment say the same thing. |
| P. Findings 8, 9, 10 and the pin gaps of finding 11. | Partly met | Fixed: pulse step 3 passes `--now <started>`, and `pending_actions` falls back to the clock. The step request stays to Wed 25 Nov, day 34 (`probe_p9.py`). No "Draft coming" on an answered tap (QA `coming-answered`). Money pin to Mon 23 Nov. Still open: `people_partial` is unpinned, and a partial people read on a Home with no directory still drops warm paths with no warning (finding 11). |
| F. Fresh Claude runs on the fixed commit, each 8 or more, no new medium finding. | Not met | Scores 8, 8 and 8.5, but each run reports new findings of medium or higher: Done on a shared draft closes both promises (high, friday-tara; also nudge-tara); the undated invite loses its draft link after each pulse (medium, friday-tara); once the note to Aditi is sent, nothing shows it or follows it up on deadline day (medium, friday-meera); a rewritten date without "by" is never caught again (medium, nudge-tara). The hand-typed bundle is carried as a known limit. |
| G. Smoke checklist on the owner's account | Not met (owner-only) | Not run. |
| H. Republish and share the sample Home, or remove the link | Not met (owner-only) | The README link is unchanged. |
| I. LICENSE and privacy policy URL | Not met (owner-only) | `--profile directory` refuses: LICENSE_MISSING, PRIVACY_URL_MISSING. |

## Do the skills, the engine and Home agree?

| What | Skill text | Engine | Home | Verdict |
|---|---|---|---|---|
| Done versus Sent it on a draft that keeps two promises | shared/home.md: Sent it marks the draft sent and closes its promise | `sent_promise` reads any draft with `done_at` as sent and closes every id in `commitment_ids` | Done on a promise row also writes the draft's id; the row then reads "Marked sent" | Disagree in meaning (finding 1) |
| A reply stops a nudge or a second chase | owed-kinds: search mail since `sent_on` (a date), in the note's thread or an email that names the company and speaks to the ask | Only the note's own thread, only after the Sent it tap | Shows what the engine stored | Partly. The skill counts from the day, the engine from the tap. The skill also counts other threads. A reply Claude finds cannot change the row or the push. |
| A partial reply | Answers only the asks it names; with `answered`, thank first | `answered_others`, by full company name | "Aditi answered on Kestrel Pay and Orbit Treasury on 26 Oct, not this one" | Agree, for full names only (finding 13) |
| An LP's reply and the day it names | lp_call: by the day named, or in five working days; "the AGM is not an answer" | `_named_day`, `CALL_WORDS`, `follow_on` | The LP row is the engine's text | Agree on the rule. The engine reads "about the call" much wider than the skill (finding 7). |
| When the note to the partner is written | owed-kinds: "two or more things", drafts and decisions | One draft plus one decision is enough | n/a | Partly. engine.md and BUILD_LOG say "two or more drafts". |
| An unsent note to the partner | owed-kinds: it waits until the user sends it | Dropped after three working days; a fresh one, with a new id, the morning after | Shows whichever is in Home | Disagree (finding 4) |
| Quiet deals in a draft to a colleague | safety rule 6: never | The holder note names them | Shows the draft | Disagree (finding 3) |
| A date a waiting draft promised, now passed | owed-kinds redate: Instinct's own date moves; one the user or a source set stays, with one line that owns the delay | The context always says "the next working day is in its place, as Instinct's suggestion" | Shows that context as "Before you send" | Disagree (finding 8) |
| An undated promise that rides in a waiting draft | morning-brief 6.6, owed-kinds: one line keeps it | The morning's `drafts` links the row; every later build drops the link | "No date", with Done and Snooze only, after the first pulse | Disagree across runs (finding 5) |
| Which builds write `owed.json` | morning-brief 6: "Only the morning brief and setup builds write it"; pulse 5: read `narrow` entries on any run | Every build writes it; other runs list only `narrow` | n/a | Disagree in the text (low) |
| Tap times as instants | n/a | `_local_marks` | `laterThan`, `dayOf` | Agree |
| Friday reaches Monday | pulse 5, morning-brief 5, connectors.md | `prep_end`, `tomorrow_meetings`, the card's `before` | "Monday:" names open their prep | Agree |
| Late work on Today | BUILD_LOG: a row or one line | `late_fold` | Renders it | Agree, but it can break the item cap (finding 12) |
| Money reaches the phone weekly | BUILD_LOG: once in every week it leads | A seven-day window that drifts | n/a | Disagree from the fourth week (finding 9) |
| What the reader owes you | One line, never when someone is copied | `they_owe`, never with `cc` | n/a | Agree |
| A nudge narrows within the hour | pulse step 5 | `narrow` on any run | `liveRow` | Agree |
| A Pipeline step saved again | engine.md `actions` | `resaved` | `pendingStepTap` with `laterThan` | Agree |
| The draft shape Home reads | shared/home.md lists the draft fields | Writes `kind`, `holds`, `commitment_ids`, `first_made_at` | Reads `kind`, `holds`, `commitment_ids` | Partly: home.md lists none of the new fields |
| `people_partial` with no directory | connectors.md: read wide this once | Accepts it silently | n/a | Partly (finding 11) |
| Guard words and Artifact reads | TRUST.md, safety.md | `guard.py` | n/a | Agree |

## Findings, worst first

All probe commands run from `/tmp/r12-council-scripts` (for example `cd /tmp/r12-council-scripts && python3 probe_done_shared.py`).

1. **Done on one promise closes every promise its draft keeps, as if sent (high, new in round twelve).** The friday-tara run found it first, and nudge-tara found it the other way round. I reproduced it.
   - Evidence: `python3 probe_done_shared.py`.
     - On Fri 23 the CFO email to Rahul (`dr_k_e9eab86816`) also carries the undated dinner invite (`commitment_ids: ['k_e9eab86816', 'k_76e229ee1b']`).
     - At 07:05 Tara taps Done on the invite. As Home's `markRowDone` does, this writes the row, the promise and the draft id.
     - At 07:28: `Intro two CFO candidates | status: done | sent flag: True`, and the CFO row has left Today. Nothing was sent.
     - The other way round, Done on the CFO row marks the invite "Marked sent" (nudge-tara finding 2).
   - Cause:
     - Home's `markRowDone` adds the draft's id whenever the row's draft keeps a promise (`closesRow`).
     - The engine's `sent_promise` reads any draft with `done_at` as sent and closes every promise in `_promise_ids`.
     - Home's `sentNow` cannot tell Done from Sent it.
     - The undated-promise feature made shared drafts common.
   - Fix:
     - Done writes only its own row and promise.
     - Sent it writes a separate sent mark, and `sent_promise` requires it.
     - A draft closes on Done only when every promise it keeps is closed.
     - Never show "Marked sent" after Done.
     - Pin Done on each of two promises that share a draft, on the replay and in Home QA.

2. **A reply that lands before you tap Sent it is never a reply (medium, the rest of condition J).**
   - Evidence, asks: `python3 probe_j_asks.py before_tap`.
     - Tara's note goes out. Aditi answers in its thread at Thu 22 15:00: "Yes, let's help Orbit Treasury and Kestrel Pay hire now. Nimbus Collect I will intro myself." Tara taps Sent it at 19:00.
     - Output: `nudges drafted on: ['Thu 29 06']`, and every ask shows `replied: None`.
     - The push: `Nudge Aditi on Kestrel, Nimbus and Orbit: no reply since 22 Oct. Note ready`.
     - Today: `Your 22 Oct note to Aditi: no answer yet on Kestrel Pay, Nimbus Collect and Orbit Treasury, 5 working days. Nudge ready`.
   - Evidence, next morning: `python3 probe_j_asks.py next_morning 30`. Reply Thu 22 18:00, tap Fri 23 08:00. Output: a nudge on `Fri 30 06`, saying `no reply since 23 Oct`.
   - Evidence, money: `python3 probe_j_lp.py before_tap`.
     - Peter answers Thu 22 16:00: "The wire goes out on Wednesday." Vikram taps Sent it on Fri 23 09:00.
     - Output: `second notes drafted: ['Fri 30 Oct']`, `chased Peter on 23 Oct, no reply in 5 working days`, context `No reply since you wrote on 23 Oct`.
     - By Fri 30 the seven-day read no longer holds the reply, so Claude's own search "since chased_on" misses it too.
   - Cause:
     - "Since the note went" means since the tap. For asks: `since_ = parse_dt(last_["at"])`, then `when_ > since_`. For chases: `when_ > at_`.
     - Sending from Gmail first and tapping later is the normal order whenever drafts are saved in Gmail.
     - The build writes "no reply" and the push before the morning's own mail check, and nothing lets Claude correct them.
   - Fix:
     - Count a reply from the note's real send time. Use the user's own message in that thread when the read holds it (the engine already finds it to set the note's `url`). Otherwise use the start of the tap's day, as the skill already does.
     - Let the morning pass the replies it found (an input to `drafts`, or `--replies`), so the row and the push change.
     - Pin both orders, for an ask and for a chase.

3. **The note to the partner names a deal you marked quiet (medium, safety rule 6).**
   - Evidence: `python3 probe_holder.py quiet`.
     - Sable Fraud AI is marked quiet (Home shows `quiet: True`).
     - Output: holder decisions `['Sable Fraud AI']`. The draft to Aditi is `Your view on 2 founder emails and Sable Fraud AI`, and its body names Sable (render `holder-quiet`).
     - Home's "Mark quiet" toast promises "Kept out of the copied brief, pushes and pre-reads".
   - Cause: `_owed` builds the holder's `decisions` from every signal and its `items` from every waiting draft, with no `_touches_quiet` check. owed-kinds `holder` says nothing about quiet deals.
   - Fix: leave quiet deals out of every draft to a colleague, the holder note first. Say so in owed-kinds and safety rule 6. Pin it with a deal marked quiet in Home and in the CRM.

4. **The note to the partner is drafted again after she answered, is replaced every few days, and never shows it went (medium, new in round twelve).**
   - Evidence, answered: `python3 probe_holder3.py` (faithful replay).
     - Meera sends the note Thu 22 10:00. Aditi replies in its thread at 14:00: "Rivulet: we pass, say it kindly. Trellis: pricing is fine at 40 bps. Sable: I will call Rhea today."
     - Output: `Tue 27 Oct 06:29 new holder ['2026-10-27']`, a second draft `Your view on 2 founder emails`.
     - The Rivulet row still says "check the firm's view with Aditi". Home shows "Note to Aditi ready, under Ready for you" again (render `holder-again`).
   - Evidence, unsent: `python3 probe_holder2.py 6`.
     - New notes, each with a new id, on Thu 22, Wed 28 and Tue 3 Nov. No note at all on Tue 27, Mon 2 and Fri 6.
     - In an account whose Gmail can create drafts, each new id is another Gmail draft that Instinct can never remove.
   - Evidence, no narrowing: `python3 probe_holder4.py`. Rivulet's draft is marked sent Thu 22 10:00. On Fri 23 and Mon 26 the waiting note still `names Rivulet: True`, with both drafts in `holds`.
   - The friday-meera run adds: once the note is sent, nothing says "Asked Aditi at 07:10", the hero still says "decide today", and nothing follows up on deadline day.
   - Cause:
     - The holder branch of `_owed` checks only when a note was sent (three working days), never the partner's reply.
     - `_snapshots` drops an unsent note after three working days, in the same build where `_owed` still sees it.
     - The id carries the date (`dr_hold_<name>_<date>`).
     - owed-kinds says the note "waits in Home and Gmail drafts until the user sends it".
   - Fix:
     - Before writing a new note, look for the partner's reply in the note's thread since it went, as for asks.
     - When a reply is found, the held drafts say "Aditi replied on 22 Oct". When not, they say "Asked Aditi on 22 Oct".
     - Keep one id per partner, rewritten in place. Narrow the note when a held draft is sent.
     - Make engine.md, owed-kinds and BUILD_LOG agree on the threshold and on an unsent note. Pin it.

5. **An undated promise loses its draft after the first check (medium, new in round twelve).** The friday-tara run found it first. I reproduced it.
   - Evidence: `python3 probe_undated_link.py`.
     - "Invite Rahul to the founders dinner": `Fri 23 06:28 daily ... 'dr_k_e9eab86816'`, then `Fri 23 07:28 pulse ... None`, and the same at 08:28 and 09:28.
     - The row then reads "No date" with Done and Snooze only. The one safe tap (Sent it) is gone, and Done is left (finding 1).
   - Cause: `brief.py` builds undated promise rows without `draft`. Only the morning's `drafts` command links them.
   - Fix: link undated rows from `drafts_by_commitment`, as dated rows are. Fix finding 1 first.

6. **A reply is read as promising a day it does not promise (medium-low).**
   - Evidence: `python3 probe_j_lp.py paid_last_friday`.
     - Peter writes in the chase's thread: "We paid it last Friday. Please check with your bank."
     - Today and the LPs tab say `Peter replied on 26 Oct, saying it goes on 30 Oct`.
     - On Mon 2 Nov: `Peter said it would go on 30 Oct, still unpaid`. The second note's context: `They said the money would go on 30 Oct and it has not come`.
     - He said it went, not that it will go.
   - Evidence: `python3 probe_j_lp.py monday_next_week`. "Thanks for Monday's call. The wire will go next week." Output: `saying it goes on 02 Nov`. The follow-up comes Tue 3 Nov, not after next week.
   - Cause: `_named_day` takes the first weekday word it finds, allows "last" and possessives, and always moves the day forward.
   - Fix:
     - Skip a day after "last", "yesterday", a possessive, or a past-tense verb (paid, sent, went).
     - Prefer the day after a wire word.
     - When unsure, store no day and say only "Peter replied on 26 Oct". Pin both.

7. **Any LP email that says "fund" counts as an answer to the chase (medium-low).**
   - Evidence: `python3 probe_j_lp.py agm_fund`.
     - Peter writes: "Quick one: is the Fund II annual meeting in December again this year?"
     - Output: `Peter replied on 27 Oct`. The second note moves from Thu 29 to `Tue 03 Nov`. Its context says `They replied on 27 Oct and the money has not come`.
     - The round-twelve AGM pin passes only because its email avoids the word "fund".
   - Cause: `CALL_WORDS` includes `funds?`, `funding`, `amount` and `pay`. Almost every LP email says "fund".
   - Fix: outside the chase's own thread, require a payment word (wire, transfer, payment, remit, paid, the call, the amount), and drop bare "fund". Pin the AGM email that names the fund.

8. **Dates in waiting drafts: invented ones put in, real ones missed (medium-low).**
   - Evidence, holder note: `python3 probe_holder2.py 6` (faithful replay).
     - On Mon 26 the holder note is listed for `redate`. Its context says `It said "by Fri 23 Oct", which has passed: the next working day is in its place, as Instinct's suggestion`.
     - The rewrite says `Sable Fraud AI: term sheet from Monsoon Arc Ventures, decide Tue 27 Oct`. That is another fund's deadline, and no source holds Tue 27.
   - Evidence, past facts: `_stale_words` on a draft written 22 Oct and read 23 Oct.
     - "The data room was closed until 20 Oct" gives `['until 20 Oct']`.
     - "We held the slot until 15 Oct" gives `['until 15 Oct']`.
     - "As promised before 21 Oct, here is the deck" gives `['before 21 Oct']`.
     - Each would be listed for a redate of a past fact.
   - The nudge-tara run adds the other side:
     - A rewrite that dropped "by" ("I will introduce you Thu 29 Oct", read on Thu 29) is never caught again.
     - "The next working day" can be the very day the user reads it.
     - "I will send it by Friday" is never caught either (my probe: `[]`).
   - Cause:
     - `PROMISED_DATE` flags any date before today after "by", "before" or "until", even one already past when the draft was written. It only knows those lead words.
     - The rewrite loop treats the holder note like a founder draft.
     - The redate context always says "as Instinct's suggestion". owed-kinds says a date the user or a source set stays, with one line that owns the delay.
   - Fix:
     - Flag dates on or after the day the draft was written, with or without a lead word, weekdays included.
     - Never list a holder note for a rewrite. Rebuild it instead.
     - Word the context by who set the date (from `old_context`), and never pick today. Pin each case.

9. **The weekly money push drifts a day a week, then skips a week (low-medium).**
   - Evidence: `python3 probe_money.py`, then the push days.
     - The unpaid call leads Today every weekday morning.
     - Money pushes go out Wed 28 Oct, Thu 5 Nov, Fri 13 Nov, then Wed 25 Nov.
     - Week 47 (16 to 20 Nov): `leads 5 mornings; money pushed 0`.
   - Cause: `named_7d` uses `when >= now - 7 days`, so the same weekday a week later still counts as named. Monday and Tuesday are skipped. The round-twelve pin stops at Mon 9 Nov.
   - Fix: count by date ("not pushed in the last six days"), and pin every week to Mon 23 Nov.

10. **The replay harness writes drafts the way no real run does (low-medium, QA).**
    - Evidence: `python3 probe_harness.py`.
      - To Fri 13 Nov, Home's drafts differ on 196 of Meera's runs between `_replay_windowed` and a write over the build's own output.
      - On Tue 27 the harness holds two holder notes. A real run holds none.
      - Aditi, Tara and Vikram match.
    - Cause:
      - `_replay_windowed` lays the morning's drafts over the previous run's Home. So drafts the build pruned come back on any morning that writes a draft.
      - It also skips what `cmd_drafts` carries on a rewrite (`kind`, `holds` and `first_made_at`), so a rewritten holder note loses its kind.
      - The round-twelve holder pin runs on this harness.
    - Other pin gaps:
      - Done on a shared draft (finding 1).
      - Every reply pin taps Sent it before the reply (finding 2).
      - A quiet deal in an internal draft (finding 3).
      - Undated rows after a pulse (finding 5).
      - The weekly-money pin ends Mon 9 Nov (finding 9).
      - `people_partial` (finding 11).
      - The item cap with the late line (finding 12).
      - The "said yes" variant of M.
    - Fix: write drafts in the harness with `cmd_drafts`' own row logic, over the build's output. Re-run rounds eleven and twelve on it, and add the pins above.

11. **A partial people read on a Home with no directory still drops warm paths, silently (low, the rest of condition P).**
    - Evidence: `python3 probe_pp.py`. With the directory: `Nimbus paths: [('Aditi', 'Raj Malhotra')]`. Without it: `Nimbus paths: [] | warnings: []`.
    - Cause: connectors.md tells Claude to read wide when Home has no `snap/directory`, but the engine accepts `people_partial` anyway and says nothing.
    - Fix: when `people_partial` meets a Home with no directory, warn in the run row (or keep the last known paths). Pin both cases.

12. **The late-work line can take Today over its item cap (low).**
    - Evidence: `python3 probe_month.py`.
      - Aditi: `over cap 14 [('Thu 05 Nov 06', 6), ...]` against a cap of 5.
      - On Thu 5 Nov, Today holds five rows plus "2 promises more than a week late".
      - The other six members never go over. No Today goes over its word budget for anyone.
    - Cause: the fold row is added after the cap trim, and the last trim checks words only.
    - Fix: count the fold against the cap by dropping the last line that can wait.

13. **A partial reply in short names reads as a full reply (low).**
    - Evidence: `python3 probe_j_asks.py short_partial`.
      - Aditi writes "Yes on Orbit. Let me think about the other two."
      - All three asks show `Aditi replied on 26 Oct: read it, then answer here`.
      - No nudge is ever written for Kestrel or Nimbus, and a "replied" ask offers no nudge.
    - Cause: the match is on the full company name ("orbit treasury").
    - Fix: also match a company's own first word when no other ask shares it. Pin "Yes on Orbit" and "Kestrel yes".

14. **After a reply, Today says "read it" with nothing to read (low).**
    - The nudge-tara run found it, and my `partial-today` render agrees.
    - The Orbit and Kestrel rows say "Aditi replied on 26 Oct: read it, then answer here", with only the founder-update chip. Portfolio's rows have "The reply".
    - Fix: carry `reply_url` on the brief's ask rows.

15. **Lines and docs that read wrong (low).**
    - On the morning a single ask's partial nudge is written, its row says "...not this one. Nudge Aditi. Divya Raman asked on 13 Oct. Nudge ready" (render `partial-today`).
    - Date fields still use the browser's format ("10/26/2026" on an Indian user's Home), carried from round nine.
    - morning-brief step 6 says only morning and setup builds write `owed.json`. Pulse step 5 reads `narrow` entries from it on every run, and the engine writes it on every build. engine.md also says "in setup and daily mode".
    - shared/home.md's draft shape lists none of `kind`, `holds` or `commitment_ids`, though Home reads them.
    - The engine counts a reply only in the note's own thread. owed-kinds also counts an email that names the company. A comment in `brief.py` says "in its thread or naming the company".
    - The late-work line always ends "Drafts are under Ready for you" without checking that each promise has one. A promise that is not an email gets none. (Code reading; on the golden data every folded promise had its draft.)

16. **Carried: an unsent nudge is written again 30 days on (low).** `python3 probe_day31.py`: written Thu 29 Oct, then again Mon 30 Nov under the same id. In a Gmail-draft account that is a second Gmail draft.

17. **Carried: the README sample link is private and an old build** (owner-only, or remove the line).

18. **Carried: the guard fails open when the transcript cannot be read** (by design; the canary still denies).

19. **Carried: a CRM field change can fire the CRM's own automations** (disclosed in TRUST.md).

20. **Process: no real-account smoke test, no dogfood, no LICENSE, no privacy URL** (owner-only). The hand-typed bundle stays a known limit (friday-meera: 68 KB a morning).

## What held up well

- **The guard.**
  - 718 of 718 in the suite, the round-eleven guard pin, and my 352 probes in four transcript layouts with no mismatch.
  - Artifact reads that save files deny. Verb-nouns at either end or alone deny; plurals at the end read.
  - Sends, state writes, other Homes, web, memory and scheduling deny. Normal sessions are untouched.
  - TRUST.md, safety.md and the guard's comment say exactly this.
- **Money.** A sent chase is remembered to Mon 23 Nov, both ways, for Vikram and the solo GP. Never a first note again, never a third. "Chased Peter" every morning. A paid call never reads "no touch".
- **Pipeline.** Two steps four days apart are each applied at the next check, with local and UTC stamps, and Home says "saving" in between.
- **Asks.**
  - A tap after the nudge narrows it within the hour.
  - Today and Portfolio agree after "Aditi said yes", in both themes at both widths.
  - A partial reply in full names gives the right row and a nudge that thanks first.
  - An email that only names a company is not a reply.
- **Records that last.** A step request after a blank met log stays to day 34. No "Draft coming" on a tap a run answered. A pitch you answered stays answered. Times compare as instants everywhere I looked.
- **Friday sees Monday.** Today names Monday's meetings, each opens its prep, and Monday's partner card says which deadlines pass before the room meets.
- **A month of runs for all seven.** No Today over its word budget, never more than four pushes a day, no push ending in an ellipsis.
- **Home.**
  - 545 of 545.
  - 48 QA colour states and my 48 renders: 0 contrast fails, lowest 3.24 (a mark), no overflow at 380 or 1440, no script errors.
  - The new pointers are clear: "Note to Aditi ready, under Ready for you", "Marked sent 22 Oct", "You replied 22 Oct: waiting on them".
- **The Claude runs.** They say the round-eleven findings they checked are fixed, and friday-meera found nothing sent or made up.

## Go or no-go

**No-go for real testers on 0.7.5.** It is a go when all of these are done:

- **Q.** Done never closes another promise.
  - Done marks only its own row and promise. Only Sent it marks a draft sent.
  - Home never shows "Marked sent" after Done.
  - Undated rows keep their draft at every run.
  - Pin Done on each of two promises that share a draft, on the replay and in Home QA.
- **R.** A reply counts from when the note really went: the user's own message in its thread, else the start of the tap's day. This holds for asks and for chases.
  - When the morning finds an answer the engine missed, the row and the push change too.
  - Pin the reply-before-Sent-it order for both. (This is the rest of J.)
- **S.** No draft to a colleague names a quiet deal. Pin it with a deal marked quiet in Home and in the CRM.
- **T.** The note to the partner:
  - checks for her answer before another note is written;
  - shows that it went;
  - keeps one id per partner, and never goes to a rewrite;
  - narrows when a held draft is sent.
  - engine.md, owed-kinds and BUILD_LOG agree on when it is written and what happens to an unsent one.
- **U.** Reading mail and dates:
  - No past or possessive day becomes a promised day.
  - Outside the chase's thread, a reply needs a payment word, not just "fund".
  - Only dates on or after the draft's day count as missed, with or without "by".
  - The redate context says who set the date, and never picks today.
  - Pin "paid last Friday", "Monday's call ... next week", the AGM email that names the fund, "closed until 20 Oct" and "introduce you Thu 29 Oct".
- **V.** The money push reaches the phone in every week the call leads, to Mon 23 Nov. Pin it.
- **W.** The harness writes drafts as a real run does, and rounds eleven and twelve are re-run on it. Add these pins:
  - `people_partial` with and without a directory, with a warning;
  - "said yes" after the nudge;
  - Today's item cap with the late line;
  - short-name partial replies.
- **F.** Fresh Claude runs on the fixed commit, each 8 or more with no new medium finding.
- **G, H, I.** Owner-only, as before.

## Owner-only steps

- **Smoke test:** `evals/smoke-checklist.md` on the owner's account, sections 1 to 8, plus three new checks:
  - send a note from Gmail, get a reply, then tap Sent it (condition R);
  - mark a deal quiet and read every draft to a colleague (condition S);
  - tap Done on one promise whose draft carries two (condition Q).
- **Dogfood:** three days in section 6's table, with one chase marked sent, one Pipeline step changed twice, and one note to a partner sent and answered.
- **License:** a LICENSE file, or `license` in `plugin.json`.
- **Privacy:** publish a privacy policy and set `privacyPolicyUrl`.
- **Sample Home:** republish from this build and share it, or take the line out of README.
- **Repository:** make `github.com/theanthill-ai/instinct-vc` real and reachable for testers.
- **Automatic approval:** on the test account, for "Instinct" and "Instinct weekend".
