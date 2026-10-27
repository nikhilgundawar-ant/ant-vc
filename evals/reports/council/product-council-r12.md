<!-- Product council, round twelve. Written by one Claude agent playing all four members on a clean clone at 321fa95 (0.7.7). Simulated: no real reviewer took part. -->

**This is a simulated council. No real reviewer took part.** One Claude agent played all four members.

# ant. for VCs: product council, round twelve

The members are a product manager, a product designer (Anthill Evergreen), an AI engineer (prompting, tool safety, the guard) and a QA lead. I reviewed commit 321fa95 (version 0.7.7, the build's "round fourteen", the first build named ant.) in a fresh clone at `/tmp/r14-council`. I judged it against round eleven (`evals/reports/council/product-council-r11.md`: average 8.13, no-go on 0.7.6) and its conditions X to AB, F, G, H and I.

- The runner and Home QA rewrote 47 tracked files. I ran `git checkout -- .` at the end, and the clone ended clean (`nothing to commit, working tree clean`).
- My scripts, outputs and renders are in `/tmp/r14-council-scripts/`. This report is also at `/tmp/r14-council-report.md`.
- I did not touch `/home/claude/instinct-vc`.

## What I read and ran

- Read: the round-eleven report; "Round fourteen: what changed" in BUILD_LOG.md; TRUST.md, README.md, LICENSE, `.claude-plugin/plugin.json`; `shared/safety.md`, `shared/home.md`, `shared/engine.md`, `shared/connectors.md`; the pulse and morning-brief skills; `references/owed-kinds.md`; `hooks/guard.py`; the diff `caa70d3..321fa95` (125 files, +1053, -308; most of it the rename); `evals/reports/claude-runs/r13-summary.md`.
- Ran on the clean clone:
  - `python3 evals/runner.py`: **223 of 223 pass**, 7 Claude-run rows skipped (no saved runs in a clean clone), 328 s.
  - `--suite round13`: 18 of 18. `--suite round14`: 12 of 12. `--suite guard`: 718 of 718.
  - `python3 evals/home_qa.py`: **565 of 565**. Page hash 33991e944ccd (new page). 48 colour states, 0 fails, lowest 3.24 (a mark).
  - `design_lint.py`: 219 rules, 0 violations. `engine lint`: ok.
  - `claude plugin validate .`: passes with warnings. `--profile directory`: passes with one warning, PRIVACY_URL_MISSING. LICENSE_MISSING is gone.
- My own probes (`/tmp/r14-council-scripts/p_*.py`):
  - 302 guard probes (four transcript layouts, the round-eleven set plus 18 new calls). 0 real mismatches (see "What held up").
  - Every round-eleven probe, re-run on 0.7.7.
  - New long replays to Mon 23 Nov with `_replay_windowed` and the hooks `_sent_it`, `_mark_sent`, `_mail`: a reply then your thank-you then Sent it (whole thread and as the bundle rule trims it); a partner's reply before Sent it the next morning, with and without your thank-you; two held drafts and no decision, one sent; a note to a partner saved in Gmail; a Sent it tap four days late; "Thanks for the call yesterday"; three ways of saying "we paid".
  - A deferring reply found by the morning, through `_apply_found_replies` on a real Thursday brief.
  - All seven members, no taps, every run to Mon 23 Nov (352 runs each), plus a word scan of every push, brief, shareable brief and draft context for "Instinct", "Ant.", "ant.." and "..".
  - 20 renders of five states (the new header, a Gmail note to a partner after one held draft went, the note rebuilt to one, reply then thanks, "we paid"), light and dark, 380 and 1440.
- The Claude-run evals on 0.7.6 (condition F): 9, 9 and 8 (`r13-summary.md`). None was run on 0.7.7.

## Scores

| Member | R11 | R12 | Why, in one line |
|---|---|---|---|
| PM | 8.0 | 8.5 | The pinned orders now work: a thank-you no longer hides a reply, the note to a partner follows any sent note and shrinks to one, "we paid it" is checked, not chased. But a reply is still lost when the bundle is trimmed as engine.md says, or when you tap Sent it four days late, and "Payment was made last Friday" still gets a second chase. |
| Designer | 8.5 | 8.5 | The ant. header is clean and on brand in both themes at both widths, and every render passes contrast with no overflow. But Ready for you now reads "take its line out.. 2 drafts wait", and a deferring reply the morning finds shows "read it, then answer here" when there is nothing to answer. |
| AI engineer | 8.0 | 8.5 | The guard holds (718 plus 302), the date owner is stored, the skill now knows a deferring reply, and the Gmail note is never rewritten. But engine.md still tells Claude to trim threads to the last message, which contradicts connectors.md and undoes X and Y, and any thread with the subject counts as "read". |
| QA lead | 8.0 | 8.5 | 223, 18, 12, 718 and 565 are green, and round14 pins every order round eleven named. But the harness always hands the engine the whole thread, so no pin tests the bundle shape the docs ask for; no check catches "..", the header, or a late tap. |

**Average: 8.50** (round eleven: 8.13).

## Round-eleven conditions

| Condition | Verdict | Evidence |
|---|---|---|
| X. A reply counts whatever you write after it; "when the note went" is your note; the bundle keeps the reply when you wrote last; pins for an ask and a chase | Partly met | Fixed in the engine: `python3 p_thanks_order.py full` gives `nudges on []`, all three asks replied, `went_at 09:00`. round14 pin passes. But engine.md's bundle rule is unchanged, and with it the reply is lost (finding 1). A tap more than three days after the note also loses it (finding 2). No chase pin for this order. |
| Y. The note to a partner: no "no word" push without a read since it went, follows any sent note, rebuilt or dropped below two, never rebuilt in Gmail, Home says what to take out; pins | Partly met | Follows a note sent the day before: `p_holder_follow.py` gives `Fri 23 14 ... no word from Aditi yet`. Reply before Sent it: no push (`p_holder_before_tap.py`). Rebuilt to one: `Mon 26 07 ... 'Your view on 1 founder email'`. Gmail note: no rebuild after the tap, and Home says "Rivulet Payments: our feedback went: take its line out". But a trimmed thread counts as read, so the push still goes after her reply (finding 1), and the Home line ends in ".." (finding 4). |
| Z. Who set a date is stored; a date ant. chose is never kept with an apology; pins | Met (one low gap) | `date_set_by` is written by `draft_rows` on redate, refresh and reslot. `p_tara_redate.py`: Mon 26 and Thu 29 `set_by instinct`, context "as ant.'s suggestion", no apology. Plural "suggestions" now reads `you` (`p_setby.py`). Every passed date now moves, whoever set it. Gap: a date chosen at first write is not stored, and the prose regex is still the fallback (finding 7). |
| AA. Skill and engine agree on a deferring reply; `_apply_found_replies` keeps `defers` | Met (one low gap) | owed-kinds step 1 now says: no nudge yet, `replied` with `"defers": true` and `"text"`. `p_defer_found.py`: every ask keeps `defers: True`. round14 pin: the put-off nudge stays from Mon 02 to Wed 04. Gap: that morning's Today row and push say "read it, then answer here" (finding 5). |
| AB. "The call" and "pay" alone are no money answer; pin | Met (one low gap) | `p_lp_call_words.py "Thanks for the call yesterday..."`: second note `Fri 30 06`, as for any non-answer. `p_units.py`: "pay a visit" is `False`. Gap: past-tense "I paid a visit" still matches (finding 6). |
| F. Fresh Claude runs, each 8 or more, no new medium | Met on 0.7.6; a run on 0.7.7 is still needed | 0.7.6 runs: 9, 9, 8, each 8 or more. Their medium findings were fixed in 0.7.7, which also changed the canary's refusal words the pulse must match ("ant. guard is on") and much of the skill text. One fresh pulse run on 0.7.7 is still needed. |
| G. Smoke checklist on the owner's account | Owner-only, not met | Not run. The checklist was renamed but has no step for X or Y. |
| H. Republish and share the sample Home, or remove the link | Owner-only, not met | README now says "sample ant. Home" but still links the old private page, which says Instinct. |
| I. LICENSE and privacy policy URL | Owner-only, half done | MIT LICENSE added and `"license": "MIT"` in plugin.json; LICENSE_MISSING is gone. PRIVACY_URL_MISSING remains. |

## Do the skills, the engine and Home agree?

| What | Skill text | Engine | Home | Verdict |
|---|---|---|---|---|
| What a thread in the bundle holds | engine.md: the latest message, plus your own latest only when someone wrote after it. connectors.md: the whole thread of a sent note to a partner | Needs the reply itself to see it (`_went_at`, the ask and holder reply loops) | n/a | Disagree (finding 1) |
| When a note went | owed-kinds: your message in its thread | `_went_at`: your first message from 3 days before the tap to 12 hours after; else the day before the tap | n/a | Disagree for a late tap (finding 2) |
| "No word from Aditi" push | BUILD_LOG: only after a run read the note's whole thread | `read_h`: any thread with that subject in the bundle | n/a | Partly (finding 1) |
| The note to a partner, waiting, one draft left | owed-kinds: rebuilt in place | Rebuilt to one, unless in Gmail | "Your view on 1 founder email" | Agree |
| A note to a partner in Gmail | morning-brief: never edit a Gmail draft | Skips the rebuild | "... went: take its line out." | Agree (wording, finding 4) |
| Who set a date | owed-kinds: ant. stores who set each draft's dates | `date_set_by` on rewrites, else a prose regex | Shows the context | Mostly agree (finding 7) |
| A reply that defers | owed-kinds: `defers` and `text`, nudge five working days on | `DEFER_WORDS`, `defers` kept, `_nudge_moot` keeps the put-off nudge | Asks tab: "the answer is to follow" | Engine and Home agree; the morning's found-reply row disagrees (finding 5) |
| "We paid it" | owed-kinds: `says_paid`, eight working days, ask for the reference | `PAID_SAYS`, 8 working days | "Peter says it was paid (26 Oct): check the account" | Agree, but the words caught are narrow (finding 3) |
| A reply about money | owed-kinds: the wire, the payment, the amount | `CALL_WORDS` without "the call" or bare "pay" | n/a | Agree ("paid a visit" aside, finding 6) |
| Sent it on the page | home.md: `sent` when Sent it closed it | Keeps `c["sent"]` when the state says `sent` | `markSent` writes `sent` | Agree |
| Deal fields a read leaves out | Not in engine.md | `_carry_forward` keeps round, raise, stage_entered; warns at 3 or more | Shows what Home kept | Agree in behaviour; engine.md does not say it (low) |
| Draft shape | home.md lists the draft fields | Also writes `date_set_by` and `went_at` | Reads them | Partly: home.md does not list the two new fields (low) |
| Guard words | pulse step 0 and the smoke checklist: "ant. guard is on" | guard.py canary reason: "ant. guard is on: ..." | n/a | Agree |
| Quiet deals in colleague drafts | safety rule 6 | `_touches_quiet` | n/a | Agree |
| The name | Skills, TRUST, README, Home: ant. | Engine strings: ant. | Title "ant. Home", header "ant." | Agree, except `templates/brief.md` ("Instinct · 4 sources") and `ontology/resolution-rules.md` (finding 8) |

## Findings, worst first

All commands run from `/tmp/r14-council-scripts` (for example `cd /tmp/r14-council-scripts && python3 p_holder_thanks.py trimmed`). No finding is high.

1. **The documented bundle still loses a reply when you wrote last, and the partner push then goes after she replied (medium; the rest of X and Y).**
   - Evidence, ask: `python3 p_thanks_order.py trimmed` (the thread as engine.md says to write it: only the latest message, which is Tara's thank-you).
     - Output: `nudges on ['Thu 29 06']`, every ask `replied: None`, `went_at: 2026-10-22T11:30:00+05:30`.
     - Push: `Nudge Aditi on Kestrel, Nimbus and Orbit: no reply since 22 Oct. Note ready`.
   - Evidence, note to a partner: `python3 p_holder_thanks.py trimmed`. Meera's note Thu 10:00, Aditi's answer Thu 14:00, Meera's "Thanks Aditi" Thu 14:30, Sent it Fri 07:30.
     - Output: `[('Fri 23 14', 'Sable Fraud AI: no word from Aditi yet, decide today')]`, holder `replied None`.
     - The same thread in full (`p_holder_thanks.py full`): no push, replied 14:00.
   - Cause:
     - engine.md still says "the latest message of each thread, and the user's own latest message in it when someone wrote after it". connectors.md says the whole thread for a sent note to a partner. The two disagree, and nothing tells Claude to keep the reply in an ask or chase thread.
     - `read_h` is set by any thread with the note's subject, so a trimmed thread counts as "read".
     - A `went_at` worked out from a trimmed thread is stored and wins for ever (`known`), so a later full read cannot fix it.
     - The harness's `_holder_threads` and the round14 pins always pass the whole thread, so the pins never see this shape.
   - Fix: one rule in engine.md and connectors.md: for a sent ask, chase or note to a partner, keep every message since your note in its thread. Set `read_h` only when the thread holds your note (or a message at or before `went_at`). Store `went_at` only from a thread that holds your note. Pin both orders with the trimmed thread.

2. **A Sent it tap more than three days after the note loses the reply (medium-low, new).**
   - Evidence: `python3 p_late_tap.py 2026-10-26T09:00:00+05:30`. Tara's note Thu 22 09:00, Aditi answers all three Thu 11:00, Tara taps Sent it Mon 26 09:00.
     - Output: `nudges on ['Mon 02 06']`, every ask `replied: False`, `went_at: None`.
     - The same with the tap Fri 23 18:00 (`p_late_tap.py 2026-10-23T18:00:00+05:30`): `nudges on []`, all replied.
   - Cause: `_went_at` looks for your message only from three days before the tap. Past that it falls back to "the start of the day before the tap" (Sunday), so a Thursday reply is "before the note".
   - Fix: look back to the draft's `first_made_at` (a note cannot go before it was written), and fall back to that, not the day before the tap. Pin "note Thursday, reply Thursday, Sent it Monday".

3. **"Payment was made last Friday" still gets a second chase (medium-low; the round-thirteen panel's case, half fixed).**
   - Evidence: `python3 p_paid_variants.py "Payment was made last Friday. Please check with your bank."` and `"It has already been paid, on Friday."`:
     - Both: `second notes: ['Mon 02 06']`, row "Peter replied on 26 Oct, still unpaid. Second note ready".
     - `python3 p_paid_units.py`: `PAID_SAYS` is False for "It has already been paid", "Payment was made last Friday", "The wire went out on Friday" and "Our bank sent the money on Friday"; True for "I paid a visit to your office".
   - Cause: `PAID_SAYS` needs a pronoun right before the verb, allows only one of "already" or "been", and has no passive "payment was made" or "went out".
   - Fix: read the passive and "went out" forms, allow "already been", and require a money word near a bare "paid". Pin the four lines.

4. **Ready for you reads "take its line out.. 2 drafts wait" (low-medium, new in 0.7.7).**
   - Evidence: render `holder-gmail-went` (`python3 renders2.py`, all four renders): "To Aditi Rao. Rivulet Payments: our feedback went: take its line out.. 2 drafts wait on Aditi's view, and 1 decision is due".
   - Cause: `draftRow` adds `". " + closedInDraft(d).trim()` and then `". " + d.context`. `closedInDraft` already ends in a full stop. The same applies to a promise draft with a line marked done.
   - Also: "Rivulet Payments: our feedback went" has two colons, and a held draft closed by Done (not sent) is also said to have "went".
   - Fix: strip the trailing full stop before joining, or join with a space. Say "the Rivulet Payments email went" and count only sent drafts. Add a Home QA check for ".." in any row.

5. **A deferring reply the morning finds shows "read it, then answer here" (low).**
   - Evidence: `python3 p_defer_found.py`. Row: "3 founder asks wait on Aditi | Aditi replied on 28 Oct: read it, then answer here". Push: "3 founder asks wait on Aditi: Aditi replied on 28 Oct". Asks keep `defers: True`.
   - Cause: `_apply_found_replies` writes one line for every found reply. The engine's own path (`brief.py`) and Home's Asks tab say "the answer is to follow".
   - Fix: with `defers`, use the same line as `brief.py` ("Aditi replied on 28 Oct: the answer is to follow").

6. **"I paid a visit" still counts as money (low).** `p_paid_units.py`: `CALL_WORDS` and `PAID_SAYS` are both True. Outside the chase thread, it would close the chase and say "says it was paid". Fix with finding 3.

7. **A date ant. chooses at first write is not stored as its own (low).** `draft_rows` sets `date_set_by: "instinct"` only on a redate, refresh or reslot with words. A first draft whose date ant. picked (the "this week" rule in owed-kinds) relies on the prose regex `(Instinct|ant\.)'s suggestion\b`. If Claude words it differently, the later redate adds "I am sorry this is late" for a date the founder never saw. Fix: let the drafts file carry `date_set_by` from Claude, and store it at first write.

8. **Rename leftovers (low).**
   - `templates/brief.md` still ends "Instinct · 4 sources · found at 06:52". `ontology/resolution-rules.md` says "Instinct" three times. BUILD_LOG's "What ships" still says "Instinct Home".
   - My scan of a month for all seven found no "Instinct", "Ant." or "ant.." in any push, brief, shareable brief or draft context. One old ".." is in a prep line: Rohan, Thu 22 10, "$310K annualised revenue.. You owe them".
   - The scheduled tasks are now named "ant." and "ant. weekend". An existing install's tasks stay "Instinct". The skill triggers are "turn off ant." and the like; the smoke test should try "turn off ant" without the full stop.

9. **A second note to the same partner within three days can borrow the first note's reply (low).** Unit probe: two notes with the subject "Your view on 2 founder emails", Thu 10:00 and Fri 09:00, with Aditi's reply in between. `_went_at` for the second gives Thu 10:00, so it counts her reply to the first. Fix with finding 2: start from the second note's `first_made_at`.

10. **Small lines.**
    - "We have not paid it yet, it goes out Wednesday" names no day, because "paid" marks the sentence as past (`_named_day` gives None). The follow-up comes at five working days, not Thursday.
    - The new warning says "raise_usd on 37 deals", a field name, not words.
    - home.md does not list `date_set_by` or `went_at`. engine.md does not say that left-out deal fields are kept.
    - The smoke checklist has no step for X or Y.

11. **Carried from round eleven (low):** a sent step with no company matches every deal, and long words match by substring (`p_units.py`, unchanged). "See you on Thu 29 Oct", "meet on" and "looking forward to" still give `[]`. `mcp__Granola__search_meetings` is still refused (safe). The guard fails open when it cannot read the transcript (by design, the canary still denies). A CRM field change can set off the CRM's own automations (in TRUST.md). The bundle is still typed by hand.

## What held up well

- **A thank-you no longer hides a reply**, when the thread is whole. `_went_at` takes your first message, and the round14 pin passes.
- **The note to a partner:**
  - no "no word" push after a reply that came before Sent it;
  - a 14:00 push for any sent, unanswered note on its deadline day, not only one sent that day;
  - rebuilt to "Your view on 1 founder email" once one of two drafts went;
  - never rebuilt while it sits in Gmail.
- **Dates:** a passed date always moves. A date ant. put in is stored as ant.'s, and is never kept with an apology. The plural "suggestions" no longer misreads.
- **Money:**
  - "We paid it last Friday" reads "says it was paid: check the account", with no chase for eight working days.
  - "Thanks for the call yesterday" and "pay a visit" are no answer.
  - The money push still comes every week to Mon 23 Nov (round13 pin).
- **Records:** Sent it on the page keeps the promise `sent`, so its CRM step reads "Sent 23 Oct". A read that drops round and raise keeps them for 37 deals, and the run warns. A stage change still re-dates `stage_entered`, so the kept date is never wrong.
- **A month for all seven:** 0 runs over the item cap, 0 over the word budget, never more than four pushes a day, no push ending in an ellipsis, no morning push repeated two days running.
- **The guard:** 718 of 718 and 302 of my probes. The canary's refusal, "ant. guard is on: this scheduled check runs on its allowlist.", matches pulse step 0 and the smoke checklist. Three of my new probes sent a `draft_id` to `create_draft`. The guard allows them, as it should: it judges by the tool name, and `create_draft` makes a new draft.
- **Home and the header:** 565 of 565. My 20 renders: 0 contrast fails (lowest 3.24 light, 3.80 dark), 0 px overflow, no script errors (only the blocked font requests). The header shows the Anthill mark and "ant." in Nunito 800 at 22 px, ink on light and near-white on dark. On desktop the mark sits in the rail and the wordmark in the header. The page title is "ant. Home".
- **The rename:** no "Instinct", "Ant." or "ant.." in any user-facing string the engine or Home writes in a month of runs. Internal ids, paths and `[instinct-scheduled-run]` are unchanged, so nothing broke.
- **LICENSE:** MIT, with `"license": "MIT"` in plugin.json. The directory check no longer reports LICENSE_MISSING.

## Go or no-go

**No-go for real testers on 0.7.7.** It is a go when all of these are done:

- **AC.** One bundle rule for threads the engine checks for replies:
  - engine.md and connectors.md both say: for a sent ask, chase or note to a partner, keep every message since your note;
  - a thread counts as read for the 14:00 push only when it holds your note;
  - `went_at` is stored only from a thread that holds your note;
  - pin "reply, your thank-you, Sent it" with the trimmed thread, for an ask, a chase and a note to a partner. (Finding 1.)
- **AD.** When a note went looks back to when its draft was written, not three days. Pin "note Thursday, reply Thursday, Sent it Monday", and two notes to one partner with one subject. (Findings 2 and 9.)
- **AE.** "Payment was made last Friday", "It has already been paid" and "The wire went out on Friday" read as paid; "I paid a visit" is no money answer. Pin all four. (Findings 3 and 6.)
- **F.** One fresh Claude pulse run on 0.7.7, 8 or more, with no new medium finding. It must see "ant. guard is on" refuse the canary.
- **G, H, I.** Owner-only, below.

Findings 4, 5, 7, 8 and 10 are low. They need not block testers, but 4 and 5 are one-line fixes worth doing first, with a Home QA check for "..".

## Owner-only steps

- **Smoke test:** `evals/smoke-checklist.md` on the owner's account, sections 1 to 8, plus:
  - send an ask note from Gmail, get a reply, write "thanks", then tap Sent it (X and AC);
  - send a note, get a reply, and tap Sent it four days later (AD);
  - send the note to a partner from Gmail, have her reply, write "thanks", tap Sent it the next morning, and watch the 14:00 push (Y and AC);
  - with Gmail drafts on, send one of two drafts the note names, and read the Home line and the Gmail draft (Y);
  - say "turn off ant" without the full stop, and "pause ant.", and check that the settings skill runs.
- **Dogfood:** three days, with one note to a partner sent and answered, one email redated twice, and one LP "we paid" reply.
- **Privacy:** publish a privacy policy and set `privacyPolicyUrl` in plugin.json (the LICENSE is done).
- **Sample Home:** republish from 0.7.7, so it says ant., and share it, or take the line out of README.
- **Repository:** make `github.com/theanthill-ai/instinct-vc` real and reachable, with the marketplace install line the validator asks for.
- **Scheduled tasks:** on the test account, approve "ant." and "ant. weekend" with automatic approval. Remove any old "Instinct" tasks from earlier installs, so two sets do not run.
