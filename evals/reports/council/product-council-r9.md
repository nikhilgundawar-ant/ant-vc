<!-- Product council, round nine. Written by one Claude agent playing all four members on a clean clone at a023dd2 (0.7.3); saved by the main session. Simulated: no real reviewer took part. -->

**This is a simulated council. No real reviewer took part.**

# Instinct for VCs: product council, round nine

One Claude agent played all four members: a product manager, a product designer (Anthill Evergreen), an AI engineer (prompting, tool safety, the guard) and a QA lead. Reviewed: commit a023dd2 (version 0.7.3, the build's "round ten") on 23 Oct 2026, in a fresh clone; no tracked file changed. Judged against round eight (`evals/reports/council/product-council-r8.md`: average 8.13, no-go) and its conditions A to I.

## What I read and ran

- Read: the round-eight report; BUILD_LOG.md ("Round ten"), TRUST.md, README.md, the shared docs, the pulse, morning-brief, lp-watch and tuning skills, `evals/smoke-checklist.md`, `hooks/guard.py`; the full diff `070b9d8..a023dd2` (95 files).
- Ran in a scratch copy: `evals/runner.py` 158 of 158 (7 Claude-run rows skipped); `--suite guard` 718 of 718; `--suite round10` 15 of 15; `home_qa.py` 477 of 477 (page hash matches; contrast: 48 states, 0 fails, lowest 3.24 on a mark); `design_lint.py` 0 violations; `engine lint` 0; `claude plugin validate .` passes with warnings, and with `--profile directory` is refused (LICENSE_MISSING, PRIVACY_URL_MISSING). Runner and QA run twice with the same results.
- Probes and replays: 125 guard probes in three transcript layouts (375 calls); long replays with taps to Mon 23 Nov (Tara three ways, Vikram's LP tap to day 33, Meera's met logs and two Pipeline steps, Vikram's chase with and without the second note); two reply probes (Aditi answers Tara's note in its thread on Mon 26 Oct; Peter answers Vikram's chase the same day); Tara's Friday built with full people, `people_partial`, and `people_partial` on a Home with no directory; every push for all seven to Fri 30 Oct through a spy on `fit_line`; all seven, no taps, every run to Mon 23 Nov (352 runs each); five new Home states in light and dark at 380 and 1440 (20 scans, 0 fails, 0 px overflow).

## Scores

| Member | R8 | R9 | Why, in one line |
|---|---|---|---|
| PM | 8.0 | 8.0 | Round eight's list is mostly done and asks hold to the fourth week. But a partner's or LP's reply in mail is never seen, so Instinct pushes "no reply" and drafts a nudge or a second chase anyway; a sent chase is forgotten on day 15; a second Pipeline step silently waits a month. Still no real account. |
| Designer | 8.0 | 8.5 | New states are clean in both themes at both widths, and "Before you send" sits under the buttons on rows and heroes. But the prep sheet still shows Open in Gmail with no caveat, Today and Portfolio contradict each other after the partner's yes, a saved Pipeline step visibly disappears, and the sample page is stale. |
| AI engineer | 8.5 | 8.5 | The guard fixes asked for are in and pinned, and the skill text is ordered and exact. But the verb-noun rule looks only at a name's first word, the Artifact tool's read can save files anywhere, morning-brief 6.3 drafts follow-ups without checking mail for an answer, and `actions` takes today's date from Home's run rows. |
| QA lead | 8.0 | 8.0 | 158, 718, 15 and 477 green, and replays run to Mon 9 Nov. But the money pin stops at day 8 while the defect starts at day 15, the "one push" check misses the "Still open" repeats, the stage-move pin checks nothing, and the suites pass over six user-visible defects. No real account. |

**Average: 8.25** (round eight: 8.13).

## Round-eight conditions

| Condition | Verdict | Evidence |
|---|---|---|
| A. Asks keep their sent state; a tap never fires twice; replays to Mon 9 Nov and day 31 | Met | Asks keep `notes`; on a Tara replay to Mon 23 Nov all three asks keep who was asked, no first note again, the nudge written once. A Vikram tap applied once and never pending again through day 33. The same expiry pattern is back elsewhere (finding 2). |
| B. Show a draft's `context` wherever its buttons are; pin it | Partly met | Rows and heroes show "Before you send"; the prep sheet's "Ready to send" does not (finding 5). |
| C. Verb-like nouns; ArtifactData paths; pin; docs exact | Partly met | The listed names deny; every ArtifactData path probe denies. The rule checks only a name's first word (finding 7), and the Artifact read can save anywhere (finding 6); TRUST.md claims more. |
| D. Refreshes keep sourced lines; one met-log id scheme; headline; paid-in out of the letter | Partly met | Headline and paid-in met; refreshes in text. The Pipeline row still saves every step under `ns_<deal>` (finding 3). |
| E. Skill lines (stage date, ordered draft rules, team note, where Home is read) | Met | Pulse step 3, safety rule 7, `shared/home.md` and the shapes agree. |
| F. Re-run the Friday Claude evals on a clean checkout, plus a Write-only bundle; 8 or more | Not met yet | The three runs were on clean checkouts but had no report when the council finished. |
| G. Smoke checklist on the owner's account | Not met (owner-only) | The checklist has the three new checks; not run. |
| H. Republish and share the sample Home, or remove the link | Not met (owner-only) | The README link is private and an old build. |
| I. LICENSE and privacy policy URL | Not met (owner-only) | Neither; `--profile directory` refuses. |

## Round ten: do the engine, Home and the skills agree?

Agree: one nudge per note; one row and "See each ask"; the partner's yes; "Fill in N lines"; who holds the firm's view; stage date, `clear_step`, `already`; where a scheduled run reads Home; headline counts; paid-in; pushes never end in "...". Agree only on a guess: "no reply" after five working days (counted, never read from mail; finding 1). Agree to day 14 only: money after "Sent it" (finding 2) and "Draft coming" (finding 10). Disagree: which draft an ask shows when two wait (engine takes the nudge first; Home the last match in key order; finding 4). Partly: "Before you send" (not on the prep sheet), met-log and step ids (finding 3), `actions` and today's date (finding 8), `people_partial` (agrees, unpinned).

## Findings, worst first

1. **"No reply" is a guess from the calendar: an answer in mail is never read (medium).** An ask's state and a chase's quiet days count working days since the note was marked sent; after five, the morning drafts a nudge or a second chase, Today says "no reply in 5 working days" and a push says it. Probe: Aditi answers Tara's note in its thread on Mon 26 Oct 15:00 ("yes, let's help them hire now"); Thu 29 Oct still says "no reply", pushes the nudge and drafts it. Probe: Peter answers Vikram's chase on Mon 26 Oct ("The wire for the 5 Oct call goes out on Wednesday"); Thu 29 Oct drafts the second note. Fix: before calling a note quiet, look in the mail the run read for a message from its recipient since it was sent; if there is one, say "Aditi replied on 26 Oct" and draft nothing; say the same in morning-brief 6.3 for `ask_nudge` and `again`; pin both probes.
2. **A sent capital-call chase is forgotten after 14 days, and the first chase is drafted again every morning (medium, new in round ten's own feature).** The chase's sent state lives only on its draft, which the build drops 14 days after Sent it. Vikram's Mon 9 Nov hero reads "no touch in 113 days. Draft ready", and the first chase is written again on all 11 weekday mornings to Mon 23 Nov; with both notes sent, the re-written first chase would be a third note. The `round10` money pin runs only to day 8. Fix: keep the chase on the LP record; never a first chase once one was sent, never a third; pin to Mon 23 Nov both ways.
3. **A second step typed in the Pipeline row is dropped for a month, then lands (medium).** The Pipeline form saves every step under `ns_<deal>`; once the first is applied, its proposals row says applied for 30 days and `pending_actions` skips the tap. Replay: a second Trellis step typed Mon 26 Oct is applied Sun 22 Nov. On screen the toast says "Saved", and the row still shows the old step. Fix: a unique id per save, or treat a tap newer than its row's `applied_at` as new; pin two steps four days apart.
4. **After "Aditi said yes", Today still asks to nudge Aditi on that ask, and Today and Portfolio disagree (medium-low, new).** A nudge drafted before the tap stays (`_nudge_moot` counts only a later sent note), `ask_view` prefers the nudge, and Home's `draftFor` picks the last match in key order. If sent, the nudge asks for "a quick yes or no" on an ask Aditi already agreed to. Fix: a later tap takes the ask out of a waiting nudge (rewrite it for the rest, or drop it); engine and Home pick an ask's draft by one rule; pin on Today and Portfolio.
5. **The prep sheet shows Open in Gmail with no caveat (medium-low).** "Ready to send" in `openPrep` has no `context`: Aditi's Atlas sheet offers the markup draft without "Attach the markup before you send". Fix: the same "Before you send" line there; pin it.
6. **The guard lets the Artifact tool's read save files anywhere (medium-low, new class).** Any Artifact `list` or `read` passes; `out_dir`, `path` and `paths` are never checked, so a read can write `guard.py` into the plugin's hooks, `authorized_keys` into `/root/.ssh` or `settings.json` into `.claude`. Fix: in a scheduled run, allow `list`, and `read` only with no `path`, `paths` or `out_dir` (or an `out_dir` inside the work folder); pin the probes.
7. **Verb-like nouns still pass at the end of a name or alone (low-medium).** The rule checks only the first word: 36 names pass (`carta-contact`, `carta-fund`, `carta-account-fund`, `carta-lps-contact`, `pitchbook-companies-tag`, `carta-shares-documents`, ...). Not a live leak. Fix: refuse a verb-noun at either end and alone unless the name ends on an about-noun; add `shares` and `calls`; pin denials and reads; make TRUST.md say exactly that.
8. **`actions` takes today's date from Home's run rows (low).** Pulse step 3 passes no `--now`; without run rows a 33-day-old tap is pending again. Fix: pass `--now <started>`, fall back to the clock.
9. **A step request after a blank met log vanishes after 30 days (low).** It lasts only while the log's proposals row says applied. Fix: keep the request while the step is empty, or say "for a month".
10. **"Draft coming at the next check" comes back two weeks after the note was sent (low).** `tapAnswered` looks only in `snap/drafts`, which drops a sent draft after 14 days. Fix: a tap is answered once its proposals row says applied; pin at day 16.
11. **Pins that pass without testing their claim (low, QA).** The money pin ends at day 8; no reply-in-mail pin; "one push" misses weekly "Still open" repeats ("Still open: Aditi: 2 asks, no reply since 22 Oct"); the stage-move pin passes with `moves []`; the day-31 pin passes `now` the skill never passes; a nudge left unsent is written again on day 31; no pin for a second Pipeline step, a tap after a drafted nudge, the prep sheet's caveat or a sent note's tap after day 14; `people_partial` unpinned, and on a Home with no directory a partial read drops warm paths (fix: read people wide when `snap/directory` is missing).
12. **Lines that read wrong, and one Today over its budget (low).** The solo GP's Friday is 256 words against 250 (the must-keep loop adds a row after the budget trim and never trims again); "Still open: Aditi: 2 asks" reads as if Aditi asked twice; "The morning brief drafts a second note. Second note ready"; the group row and the Portfolio hero list the asks in different orders; the morning a nudge is drafted, the row still ends "Nudge Aditi"; `fit_line` cuts from the end, so a date can go first ("Next: Screening memo" without "was due 23 Oct"); `draft_gaps` counts "[sic]", "[EXTERNAL]" and "[cid:...]"; `letter-check` misses "contributed"; date fields use the browser's format.
13. **Carried: the README sample link is private and an old build** (owner-only, or remove the line).
14. **Carried: the guard fails open when the transcript cannot be read** (by design; the canary still denies).
15. **Carried: a CRM field change can fire the CRM's own automations** (disclosed).
16. **Process: no real-account smoke test, no dogfood, no LICENSE, no privacy URL** (owner-only).

## What held up well

Asks hold to the fourth week; old taps stay applied through day 33 on the skill's own call path; the guard floor is whole for everything round eight asked (13 listed names and 6 more deny, every ArtifactData path probe denies, the engine copy comes only from the plugin, shell escapes deny, normal sessions untouched); Home's new states pass contrast in both themes at both widths; engine, skills and Home agree on "Fill in N lines", the firm's view holder, "Questions Instinct suggests", the partner's yes and "Vikram Nair"; the letter never sees a paid-in figure; one fact, one line across 316 race rows; a month holds its limits (never more than four pushes a day, no Today over its item cap, no push ending in an ellipsis); late work stays to Fri 30 Oct.

## Go or no-go

**No-go for real testers on 0.7.3.** It is a go when all of these are done:

- **J.** Draft a nudge or a second chase, and say "no reply", only when the mail the run read holds no answer from that person since the note went out. Pin both reply probes.
- **K.** A capital-call chase keeps its sent record as long as the call is unpaid; never a first chase after one was sent, never a third. Pin to Mon 23 Nov with and without the second note.
- **L.** Each Pipeline save is applied at the next run, whatever was saved before. Pin two steps four days apart, on the replay and in Home QA.
- **M.** A later tap on an ask takes it out of a waiting nudge, and the engine and Home pick an ask's draft by one rule. Pin the yes-after-nudge replay on Today and Portfolio.
- **N.** "Before you send" on the prep sheet's drafts. Pin it.
- **O.** Fix findings 6 and 7, pin the probes, and make TRUST.md, safety.md and the guard's comment say exactly what is enforced.
- **P.** Fix findings 8, 9 and 10, and close the pin gaps in finding 11 (`--now` in pulse step 3; the step request until a step is set; no "Draft coming" on an answered tap; money, Pipeline and "Draft coming" pins past day 30; `people_partial` with and without a directory).
- **F.** Fresh Claude runs on the fixed commit, each scoring 8 or more with no new medium finding.
- **G, H, I.** Owner-only, as before.

## Owner-only steps

- Smoke test: `evals/smoke-checklist.md` on the owner's account, sections 1 to 8, plus one more: an Artifact `read` with `path` and an `out_dir` outside the work folder, to see whether the tool saves without a prompt.
- Dogfood: three days in section 6's table, with at least one chase marked sent and one Pipeline step changed twice.
- License: a LICENSE file, or `license` in `plugin.json`.
- Privacy: publish a privacy policy and set `privacyPolicyUrl`.
- Sample Home: republish from this build and share it, or take the line out of README.
- Repository: make `github.com/theanthill-ai/instinct-vc` real and reachable for testers.
- Automatic approval: on the test account, for "Instinct" and "Instinct weekend".
