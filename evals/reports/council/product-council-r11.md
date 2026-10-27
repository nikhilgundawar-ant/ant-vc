<!-- Product council, round eleven. Written by one Claude agent playing all four members on a clean clone at caa70d3 (0.7.6). Simulated: no real reviewer took part. -->

**This is a simulated council. No real reviewer took part.** One Claude agent played all four members.

# Instinct for VCs: product council, round eleven

The members are a product manager, a product designer (Anthill Evergreen), an AI engineer (prompting, tool safety, the guard) and a QA lead. I reviewed commit caa70d3 (version 0.7.6, the build's "round thirteen") in a fresh clone at `/tmp/r13-council`. I judged it against round ten (`evals/reports/council/product-council-r10.md`: average 7.75, no-go on 0.7.5) and its conditions Q to W and F.

- The runner and Home QA rewrote 61 tracked files. I ran `git checkout -- .` at the end, and the clone ended clean (`nothing to commit, working tree clean`).
- My scripts, outputs and renders are in `/tmp/r13-council-scripts/`. This report is also at `/tmp/r13-council-report.md`.
- I did not touch `/home/claude/instinct-vc`.

## What I read and ran

- Read: the round-ten report; "Round thirteen: what changed" in BUILD_LOG.md; TRUST.md, README.md; `shared/safety.md`, `shared/home.md`, `shared/engine.md`; the pulse and morning-brief skills; `references/owed-kinds.md`; `hooks/guard.py` (unchanged since 0.7.5); the diff `947db4c..caa70d3` (88 files, +3290, -233).
- Ran on the clean clone:
  - `python3 evals/runner.py`: **211 of 211 pass**, 7 Claude-run rows skipped (no saved runs), 771 s on a loaded machine. This includes rounds eleven and twelve, now replayed on the new harness.
  - `--suite round12`: 19 of 19. `--suite round13`: 18 of 18. `--suite guard`: 718 of 718.
  - `python3 evals/home_qa.py`: **565 of 565**. Page hash matches (7e755edf2ead). 48 colour states, 0 fails, lowest 3.24 (a mark).
  - `design_lint.py`: 219 rules, 0 violations. `engine lint`: ok. `claude plugin validate .`: passes with warnings; `--profile directory` refuses (LICENSE_MISSING, PRIVACY_URL_MISSING).
- My own probes (`/tmp/r13-council-scripts/p_*.py`):
  - 284 guard probes (71 calls in four transcript layouts: prompt as a string, meta rows first, prompt in text blocks, a normal session). 0 unexpected.
  - Long replays with `_replay_windowed` and the hooks `_sent_it`, `_mark_sent`, `_mail`, `_tap_done`, to Mon 23 Nov: replies before Sent it, replies followed by the user's own message, the note to the partner (one draft left, in Gmail, answered before Sent it, the 14:00 push), a quiet deal set by a Home tap, LP emails, redates.
  - All seven members, no taps, every run to Mon 23 Nov (352 runs each): item cap, word budget, pushes a day, cut pushes, repeated morning pushes.
  - Unit probes of `_named_day`, `CALL_WORDS`, `_stale_words`, `_sent_step`.
  - 16 renders of four new states (holder one left, reply then thanks, step sent, Done on a shared email), light and dark, 380 and 1440: 0 contrast fails, lowest 3.24 light and 3.80 dark, 0 px overflow, no script errors (only blocked font requests).
- The three Claude-run evals on 0.7.6 (condition F): **not available.** At the end of my run, `friday-meera`, `friday-tara` and `nudge-tara` had working folders but no `evals/runs/<run>/report.md`.

## Scores

| Member | R10 | R11 | Why, in one line |
|---|---|---|---|
| PM | 7.5 | 8.0 | Q, S, V and W are met, and the high finding is gone: Done never closes another promise. But a reply is still lost when you answer it before tapping Sent it, a push says "no word from Aditi" after she replied, and the note to Aditi still asks about a draft you already sent. |
| Designer | 8.0 | 8.5 | Every new state is clean in both themes at both widths. "Asked Aditi at 07:10", "Sent 23 Oct: send term sheet markup" and "Intro two CFO candidates is marked done: take its lines out" are clear. But Ready for you keeps a stale note to Aditi, and one founder email keeps a passed date Instinct chose, with an apology. |
| AI engineer | 8.0 | 8.0 | The guard holds (718 plus 284 probes), and quiet deals stay home. But who set a date is read from free text, a rebuild asks Claude to edit a Gmail draft it must never edit, the skill never tells Claude about replies that put off their answer, and "the call" counts as an answer about money. |
| QA lead | 7.5 | 8.0 | 211, 19, 18, 718 and 565 are green, the harness now writes drafts as a run does, and most round-ten pin gaps are closed. But the pins choose the easy orders: a decision keeps the note at two lines, the reply is the last message in its thread, and the 14:00 push is tested only with no reply. |

**Average: 8.13** (round ten: 7.75).

## Round-ten conditions

| Condition | Verdict | Evidence |
|---|---|---|
| Q. Done never closes another promise; only Sent it marks sent; no "Marked sent" after Done; undated rows keep their draft; pins | Met | round13 pin: Done on each of two promises in `dr_k_e9eab86816` leaves the other open, not sent, with the draft, narrowed to it. Undated row keeps `dr_k_e9eab86816` at Fri 23 06 to 09. Home QA `shared-done`. My render: "Intro two CFO candidates is marked done: take its lines out", no "Marked sent". |
| R. A reply counts from when the note really went, for asks and chases; a reply the morning finds changes the row and push; pins | Partly met | Pinned orders pass (reply Thu 15:00, tap 19:00; Peter Thu 16:00, tap Fri 09:00; `_apply_found_replies`). But when the user writes again in the thread after the reply, the reply is lost (finding 1). |
| S. No draft to a colleague names a quiet deal; pin in Home and in the CRM | Met | round13 pin (CRM flag). My probe with a Home "Mark quiet" tap (`p_quiet_home.py`): holder decisions `[]`, "Sable" in no colleague draft, no push names it. |
| T. The note to the partner checks her answer, shows it went, one id, no rewrite, narrows when a held draft is sent; docs agree | Partly met | Answer checked, one id (`dr_hold_aditi_rao`), never listed as a redate, "Asked Aditi at 07:00" and "Aditi replied at 11:05" in Home QA. But it does not narrow when one draft is left (finding 3), its 14:00 push ignores a reply that came before Sent it (finding 2), and a rebuild of a Gmail copy contradicts the skill (finding 5). |
| U. Days and words read right; redate context by who set it, never today; pins | Partly met | The five named pins pass. But `set_by` is guessed from free text and misreads (finding 4), "the call" counts as money (finding 7), and future dates after "see you on" or "meet on" are never caught (finding 10). |
| V. Money reaches the phone every week the call leads, to Mon 23 Nov | Met | round13 pin, Vikram and the solo GP: every week with 3 or more mornings on Today has a push (weeks 44 to 47: 5 mornings, 1 push). |
| W. Harness writes drafts as a run; rounds eleven and twelve re-run; four pins | Met | `_replay_windowed` writes with `cli.draft_rows` over the build's output and runs the pulse rewrites. round11 and round12 pass in the full runner. Pins for `people_partial`, "said yes", the item cap and short-name replies pass. My month runs: 0 over cap, 0 over budget, for all seven. |
| F. Fresh Claude runs on the fixed commit, each 8 or more, no new medium | Not met (not available) | No report.md existed in the three run folders when I finished. |
| G. Smoke checklist on the owner's account | Owner-only, not met | Not run. |
| H. Republish and share the sample Home, or remove the link | Owner-only, not met | README link unchanged. |
| I. LICENSE and privacy policy URL | Owner-only, not met | `--profile directory`: LICENSE_MISSING, PRIVACY_URL_MISSING. |

## Do the skills, the engine and Home agree?

| What | Skill text | Engine | Home | Verdict |
|---|---|---|---|---|
| Done versus Sent it | home.md: Sent it marks `sent`; Done marks `closed_by: "done"` | `_was_sent` | `markSent`, `markRowDone`, `sentAt` | Agree. An old mark with no `closed_by` reads as sent on both sides. |
| When a note went | owed-kinds: your message in its thread, else the tap's day | `_went_at`: the user's latest message from 3 days before the tap to 12 hours after | n/a | Disagree in one order (finding 1). The latest message can be a later one. |
| A reply that puts off its answer | Not in any skill | `DEFER_WORDS`, nudged after 5 working days | "the answer is to follow" | Disagree (finding 6) |
| The note to a partner, waiting | owed-kinds: rebuilt in place when what it names changes | No rebuild once fewer than two things are left | Shows the old note | Disagree (finding 3) |
| Rebuild of a note in Gmail | morning-brief 6.7: never edit a draft in Gmail | Lists `rebuild` whatever `in_gmail` | n/a | Disagree (finding 5) |
| "No word from Aditi" push | BUILD_LOG: due today and no reply by 14:00 | Only when the note was sent today, and only mail this run read | n/a | Disagree (findings 2 and 8) |
| Who set a passed date | owed-kinds: `set_by` from the old context | A regex for "Instinct's suggestion" in free text | Shows the context | Partly (finding 4) |
| Quiet deals in colleague drafts | safety rule 6, owed-kinds holder | `_touches_quiet` on items and decisions | n/a | Agree |
| A step you marked sent | home.md `step_went` | `_sent_step` in snapshots, decisions and prep | "Sent 23 Oct: ...", prep "Set the next step", partner line "none set" | Agree (matching is loose, finding 9) |
| Today's item cap | home.md `cap`, `can_wait`, `fold_rows` | `late_fold`, `show_pushed` | Renders the engine's rows | Agree |
| Which builds write `owed.json` | morning-brief 6, pulse 5, engine.md: every build; others list only `narrow` and holder `rebuild` | Same | n/a | Agree (round ten's low is fixed) |
| Draft shape | home.md lists `commitment_ids`, `asks_for`, `first_made_at`, `kind`, `holds`, `decisions`, `replied` | Writes them | Reads them | Agree |
| A reply about money | owed-kinds: the wire, the payment, the amount; not the AGM | `CALL_WORDS` adds "the call" and "pay" | n/a | Partly (finding 7) |
| Guard words and Artifact reads | TRUST.md, safety.md | `guard.py`, unchanged | n/a | Agree |

## Findings, worst first

All commands run from `/tmp/r13-council-scripts` (for example `cd /tmp/r13-council-scripts && python3 p_thanks_order.py full`). No finding is high.

1. **A reply is lost when you write again in the thread before tapping Sent it (medium, the rest of condition R).**
   - Evidence: `python3 p_thanks_order.py full`. Tara's note goes Thu 09:00. Aditi answers 11:00: "Yes, let's help Orbit Treasury and Kestrel Pay hire now. Nimbus Collect I will intro myself." Tara writes "Thanks Aditi, will do" at 11:30, and taps Sent it at 18:00.
     - Output: `nudges on ['Thu 29 06']`, every ask `replied: None`, `went_at: 2026-10-22T11:30:00+05:30`.
     - Push: `Nudge Aditi on Kestrel, Nimbus and Orbit: no reply since 22 Oct. Note ready`. Render `thanks-order`: "no answer yet on Kestrel Pay, Nimbus Collect and Orbit Treasury, 5 working days".
   - `python3 p_thanks_order.py trimmed` (the bundle rule in engine.md: the latest message, plus your own only when someone wrote after it): the same result. Aditi's reply is not even in the bundle.
   - Cause: `_went_at` takes the user's *latest* message in the window, so a thank-you after the reply becomes "when the note went". It is then stored as `went_at`. The same function serves chases.
   - Fix: take the user's earliest message in the window (or the one whose text matches the draft), never one after a reply from the recipient. In engine.md, keep the latest message from each other participant since the user's note. Pin "reply, then your thank-you, then Sent it" for an ask and a chase.

2. **"No word from Aditi yet, decide today" goes to the phone after she replied (medium, new).**
   - Evidence: `python3 p_holder_before_tap.py`. Meera sends the note from Gmail Thu 10:00. Aditi replies in its thread Thu 14:00. Meera taps Sent it Fri 07:30.
     - Output: `Fri 23 14 holder:dr_hold_aditi_rao:d_sable Sable Fraud AI: no word from Aditi yet, decide today`. The note's `replied` is `None` at Fri 07 and Fri 14, and is found only at `Mon 26 06`.
   - Cause: the holder reply search reads only this run's mail. The pulse after the tap reads the hours since the last run, so Thursday's reply is not in it. The push has no mail check before it goes.
   - Fix: when a holder note is marked sent, the pulse reads that note's thread (as it reads a week of founder threads), or the 14:00 push waits for a run that read mail since `went_at`. Pin this order.

3. **The note to a partner keeps asking about a draft you already sent (medium, the rest of condition T).**
   - Evidence: `python3 p_holder_one_left.py`. After Sable's deadline passes, the note names two drafts with no decision (Sat 24 09 rebuild). Meera marks Rivulet's draft sent Mon 26 07:05.
     - Output: every run to Tue 27 08 has `owed []` and Home `holds ['dr_k_454489f888', 'dr_k_a4b63d1828']`, subject `Your view on 2 founder emails`.
     - Render `holder-one-left`: Ready for you shows "Draft: Your view on 2 founder emails", and the Trellis row says "Note to Aditi ready, under Ready for you".
   - Cause: `_owed` skips the holder when `len(waiting_) + len(decide_) < 2`, before the rebuild check, so a waiting note is never rebuilt or dropped. `_snapshots` and Home's `draftClosed` drop it only when every held draft is closed. The round13 pin passes only because Sable's decision keeps the count at two.
   - Fix: when a waiting note falls below two things, rebuild it for the one left or drop it (and say so on that row). Pin "two drafts, no decision, one sent".

4. **Who set a passed date is guessed from free text, and Instinct's own date is kept with an apology (medium-low).**
   - Evidence: `python3 p_setby.py`. A draft whose context says "The three questions are Instinct's suggestions" and whose body says "by Tue 27 Oct" gets `set_by instinct` on Wed 28. The same draft with "You promised this on 20 Oct" gets `you`. The plural matches the regex.
   - Evidence: `python3 p_tara_redate.py`. Mon 26: Tara's CFO email said "this week", and the redate put in "by Wed 28 Oct" (Instinct's choice). The engine's own context for that rewrite says only "a date is in its place now". On Thu 29: `redate you ['by Wed 28 Oct']`, context "the date stays, with one line that owns the delay". The founder email keeps a passed date Instinct chose. Render `thanks-order` shows that line under "Before you send".
   - Cause: `ours_ = re.search(r"Instinct's suggestion", context)`. Whether a later run sees the phrase depends on Claude's wording, and the engine's own "this week" context never says it.
   - Fix: store `date_set_by` on the draft row in `draft_rows` from the redate entry (and from the promise's due date at first write). Never infer it from prose. Pin both cases.

5. **A rebuild of the note to a partner asks Claude to edit a Gmail draft (medium-low).**
   - Evidence: `python3 p_holder_gmail.py`. With the note `in_gmail: true`, Rivulet's draft sent Fri 23 07:05: `Fri 23 07 pulse dr_hold_aditi_rao True ['Trellis Banking API']`.
   - Cause: the holder branch of `_owed` has no `in_gmail` check, unlike `narrow` for nudges and promises. morning-brief 6.7 says never edit a draft already in Gmail, and owed-kinds says rewrite it under the same id. Claude must break one rule, or leave a stale Gmail draft beside a new one.
   - Fix: for a note in Gmail, do not rebuild. Show "Your Gmail draft to Aditi still names Rivulet: take that line out" in Home, as `closedInDraft` does for promises.

6. **The skill does not know a reply that puts off its answer (medium-low, text against engine).**
   - Evidence (code and text reading): the engine marks "Let me think about these and come back to you" as `defers` and lists a nudge five working days later (round13 pin: nudge on Mon 02). owed-kinds `ask_nudge` step 1 tells Claude to search for a reply since `sent_on` and, finding one, write no nudge and put `replied`. No skill mentions a deferring reply. `_apply_found_replies` then stores `replied` without `defers`, which turns off the put-off nudge.
   - Fix: owed-kinds: "A reply that only says the answer will follow is not an answer: write the nudge, and say they promised to come back." Keep `defers` in `_apply_found_replies` when the stored reply had it.

7. **"Thanks for the call yesterday" counts as an answer about money (low-medium).**
   - Evidence: `python3 p_lp_call_words.py "Thanks for the call yesterday. See you at the AGM in December."` (outside the chase thread): Peter "replied on 27 Oct", and the second note moves from Fri 30 to `Tue 03 06`. The AGM-only email still gets Fri 30. `p_units.py`: "Happy to pay a visit when I am in Bangalore." also matches.
   - Cause: `CALL_WORDS` added "the call" and keeps "pay". Both are common outside money.
   - Fix: require "capital call", "the call notice" or a payment word near the amount, and use "paid", "payment" rather than bare "pay". Pin both emails.

8. **The 14:00 follow-up push fires only when the note was sent that same day (low).**
   - Evidence: `python3 p_holder_follow.py 2026-10-22T10:00:00+05:30` (sent Thu, Sable due Fri): no `holder:` push on Fri. Sent Fri 07:30: `Fri 23 14 ... no word from Aditi yet, decide today`.
   - Cause: `at_h.astimezone(now.tzinfo).date() != now.date()` skips every note sent before the deadline day, which is the usual case.
   - Fix: follow any sent, unanswered note whose decision is due today. Fix finding 2 first.

9. **A sent step can match the wrong deal or a later step (low).**
   - Evidence: `python3 p_units.py`. `sent_steps {"|send term sheet markup": ...}` (no company) matches another company's "Send term sheet markup". `"c_atlas|share feedback"` matches "Share feedback after the partner meeting on 6 Nov".
   - Cause: an empty company key matches every deal, and words of 12 or more characters match by substring either way.
   - Fix: skip a sent step with no company. Match only when the CRM step was already set when the promise was sent.

10. **A missed future date after "see you" or "meet on" is never caught (low).**
    - Evidence: `p_units.py`, a draft of Wed 28 read Fri 30: "I will see you on Thu 29 Oct", "Happy to meet on Thu 29 Oct", "Looking forward to Thursday 29 Oct" all give `[]`. "I will send the deck on Thu 29 Oct" gives `['Thu 29 Oct']`.
    - Cause: `BACK_CUE` treats "see you" and "meet on" as past, and "looking forward" is not an `AHEAD_CUE`.
    - Fix: read "see you" and "meet on" as past only with a past verb. Add "look forward". Pin the three lines.

11. **The guard refuses a real Granola read (low, safe).** `mcp__Granola__search_meetings` is denied in all three scheduled layouts. It is not in `KNOWN_READS`. Denying is the safe failure, but the pulse loses a read this account offers. Add it after checking its arguments.

12. **Small lines.** `lowerFirst` and `_lower_first` keep "A call with Rhea" capitalised after "Sent 23 Oct:". After Done on one promise, "Before you send" still carries the old context ("Also carries your promise of 15 Oct...") until the next check.

13. **Carried:** the README sample link is private and old (owner-only); the guard fails open when the transcript cannot be read (by design, the canary still denies); a CRM field change can fire the CRM's own automations (in TRUST.md); the hand-typed bundle; no real-account smoke test, dogfood, LICENSE or privacy URL.

## What held up well

- **Done is never Sent it.** Pinned both ways, in the engine and in Home QA. My render shows "is marked done: take its lines out" and no "Marked sent". The undated promise keeps its email at every run.
- **Replies before Sent it**, in the pinned order, for asks and chases. A reply the morning finds changes the ask, its row and the push.
- **Quiet deals.** Set in the CRM or by a Home tap, no note to a colleague names one, and no push does.
- **The note to a partner** keeps one id, is never redated as if it were a founder email, waits on her answer, and Home says "Asked Aditi at 07:00" and "Aditi replied at 11:05".
- **Money every week**, to Mon 23 Nov, for Vikram and the solo GP.
- **A month for all seven:** 0 runs over the item cap, 0 over the word budget, never more than four pushes a day, no push ending in an ellipsis, no morning push repeated two days running.
- **The guard:** 718 of 718 and my 284 probes, with no mismatch.
- **The harness** now writes drafts with `cmd_drafts`' own rows and runs the pulse rewrites, so rounds eleven to thirteen test what a real run writes.
- **Home:** 565 of 565, and my 16 renders: 0 contrast fails, no overflow, no script errors. "Sent 23 Oct: send term sheet markup. Add the next step" is the right line on Pipeline.

## Go or no-go

**No-go for real testers on 0.7.6.** It is a go when all of these are done:

- **X.** A reply counts whatever you write after it. "When the note went" is your note, never a later message of yours. The bundle keeps the recipient's reply even when you wrote last. Pin "reply, your thank-you, then Sent it" for an ask and a chase. (Finding 1.)
- **Y.** The note to a partner:
  - never pushes "no word from Aditi" without a mail read that covers the time since it went, and follows any sent note, not only one sent that day;
  - is rebuilt or dropped when fewer than two things are left;
  - is never rebuilt in Gmail; Home says what to take out instead.
  - Pin each. (Findings 2, 3, 5, 8.)
- **Z.** Who set a date is a stored field, never read from prose. A date Instinct chose is never kept with an apology. Pin the plural "suggestions" case and "this week" then a passed date. (Finding 4.)
- **AA.** The skill and the engine agree on a reply that defers, and `_apply_found_replies` keeps `defers`. (Finding 6.)
- **AB.** "The call" and "pay" alone are no answer about money. Pin "Thanks for the call yesterday". (Finding 7.)
- **F.** Fresh Claude runs on the fixed commit, each 8 or more, with no new medium finding. (Not available this round.)
- **G, H, I.** Owner-only, as before.

Findings 9 to 12 are low and need not block testers.

## Owner-only steps

- **Smoke test:** `evals/smoke-checklist.md` on the owner's account, sections 1 to 8, plus:
  - send a note from Gmail, get a reply, write "thanks", then tap Sent it (condition X);
  - send the note to a partner from Gmail, have her reply, tap Sent it the next morning, and watch the 14:00 push (Y);
  - with Gmail drafts on, send one of two drafts the note names and read the Gmail draft (Y).
- **Dogfood:** three days, with one note to a partner sent and answered, and one email redated twice.
- **License:** a LICENSE file, or `license` in `plugin.json`.
- **Privacy:** publish a privacy policy and set `privacyPolicyUrl`.
- **Sample Home:** republish from this build and share it, or take the line out of README.
- **Repository:** make `github.com/theanthill-ai/instinct-vc` real and reachable, with the marketplace install line the validator asks for.
- **Automatic approval:** on the test account, for "Instinct" and "Instinct weekend".
