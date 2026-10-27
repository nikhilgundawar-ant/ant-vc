# Instinct for VCs: product council, round seven

**This is a simulated council. No real reviewer took part.** One Claude agent played all four members: a product manager, a product designer (Anthill Evergreen), an AI engineer (prompting, tool safety, the guard) and a QA lead. Reviewed 23 Oct 2026 against commit 4ff0548 (version 0.7.0, the build's "round eight"). The repository was not changed. Every run and probe used a scratch copy at `/tmp/council-r7/repo`.

Judged against the round-six report (average 8.4, a last-mile no-go) and its conditions 1 to 19.

## What I read and ran

Read: the round-six council report; BUILD_LOG.md (including "Round eight: what changed"), README.md, TRUST.md, CLAUDE.md, the smoke checklist; the full diff `81c3e95..4ff0548` (it includes 2b5f57b, the guard change for CRM and fund-data reads); every skill (`skills/*/SKILL.md`), the shared docs (`shared/*.md`), `hooks/guard.py`, `hooks/hooks.json`, `schedules.json`, `home/index.html`; and the Claude-run Friday eval on 0.6.0 (`r7-friday-meera.md`).

Ran in the scratch copy:
- `python3 evals/runner.py`: **142/142** in 60s (guard suite inside it 607/607).
- `python3 evals/runner.py --suite guard`: **607/607**.
- `python3 evals/home_qa.py` (Playwright, phone and desktop, light and dark, every level, the new met-log and ask states): **428/428**. Screenshots are from the committed page (`qa.json` page hash `1457cbc5b5fe` matches `home/index.html`).
- `python3 evals/design_lint.py`: **0 violations in 214 CSS rules**. Contrast: 48 states, **0 fails**, global min 3.24.
- `python3 -I -S engine/instinct.py lint --root .`: **0 violations**.
- `claude plugin validate .`: passes with warnings; `--profile directory` still **refuses for LICENSE_MISSING**, privacy URL still a warning.
- My own guard probes: ~70 fresh calls through `hooks/guard.py` with its real stdin shape, in scheduled and normal sessions, all against placeholder hosts and dummy files. Focus: the new data-server and CRM read rule, the fail-open, the classic escape chains.

## Scores

| Member | R6 | R7 | Why, in one line |
|---|---|---|---|
| PM | 8.5 | 8.5 | The met-log, finished-and-followed asks, and cost-to-miss ranking are real and honest; but TRUST.md now overstates the guard, and the gating items (smoke test, LICENSE, fresh 0.7.0 run) are all unchanged. |
| Designer | 8.5 | 8.5 | 0 contrast fails across 48 states, lint 0, 428/428; the met-log form and the asked/requested/nudge/made states are clean and honest; the guard-off banner is clear; the README sample-Home (condition 19) is still an unverified external link. |
| AI engineer | 8.5 | 8.0 | The read-word closure and config lock still hold and ~70 fresh probes were clean, but 2b5f57b turned the data-server rule into a denylist that now passes outbound and money-movement Carta tool names, and TRUST.md claims more than the guard enforces. |
| QA lead | 8.0 | 8.0 | 142/607/428 all green and the round-eight met-log and ask states are covered, but the suite pins only a few data-server denials and missed the outbound-name gap, no real-account smoke test has run, and no fresh Claude run used the 0.7.0 skills. |

**Average: 8.25** (round six: 8.4). A last-mile no-go again, and down slightly: the product's features are better, but the safety floor took a hole this round.

## Round-six fixes and conditions: what was done

Each re-checked with evidence.

- **Condition 17 and R6 fix 2 (Carta read over-refusal).** Partly met, by a method the condition warned against. Carta and company-data reads now pass: round six denied `mcp__Carta__carta-capital-accounts` and `pitchbook-company-profile`; round seven allows both (I ran the round-six guard and the round-seven guard side by side). The smoke read-coverage line now names Carta and the company-data connectors (verified in the diff), and the suite pins `carta-capital-accounts`, `pitchbook-company-profile`, `harmonic-enrich-company` allow and `carta-issue-shares`, `carta-exercise-options`, `pitchbook-export-list`, `affinity-view-as` deny. **But** the condition said "a refused read there is a name to add to `KNOWN_READS`, never a reason to loosen the rule." The implementer loosened the rule: on PitchBook/Harmonic/Crunchbase/Carta a tool now passes if its name merely lacks a listed write or fund-admin verb. That is the regression in finding 1.
- **R6 fix 1 / condition 16 (real-account smoke test).** Not done. Zero real scheduled runs. Owner-account only.
- **R6 fix 3 / condition 15 (LICENSE and privacy URL).** Not done. `--profile directory` still refuses `LICENSE_MISSING`; no LICENSE file, no `license` key, no `privacyPolicyUrl`. Owner-account choice.
- **R6 fix 4 / condition 18 (fresh Claude run).** Done on 0.6.0, not on 0.7.0. The Friday run (`r7-friday-meera.md`) exercised the 0.6.0 pulse end to end and found 11 real issues. Round eight answered them (below). But 0.7.0 itself has had no fresh end-to-end Claude run.
- **R6 fix 5 / condition 19 (republish README sample Home).** Not evidenced. README.md was not touched since round six; the link is the same external artifact (`.../8SzHVyrLnoTVkSiaGSxXZW`), which I cannot verify from the repo.
- **The Friday eval's findings were answered well.** Verified in the code, not just the changelog:
  - *Stage date (item 1, the most material).* `_applied_stage_moves` in `cli.py` now sets `stage_entered_dt` to the meeting day for a stage moved from Home's met log, even when the CRM keeps no stage date. Halo now shows day 1, not day 13. Round-eight suite confirms (`days in the new stage {'Rivulet Payments': 1, 'Halo Reconcile': 1}`).
  - *Headline count (section 6).* A single `_things()` helper now feeds both the brief headline and the run row, so "N things for today" and `items` agree.
  - *Reslot wording (item 5).* The skill and `engine.md` now say "times are today or earlier", not "have passed".
  - *Time-picking rules (item 6).* Morning-brief step 6.2 now sets them: two 30-minute slots, working days, 10:00 to 18:00, 30 minutes clear, within seven working days.
  - *Subject rule (item 7).* Step 6.1 now says the subject names the company and the thing, never the task line.
  - *Refresh with no notes (items 2, 3).* Step 6.5 now handles it: keep the draft, open with a line that claims nothing, ask the user to check.
  - *current_due (item 10) and one CRM call (item 9).* Pulse step 3 now checks `current` and `current_due`, and applies several fields in one call with one applying mark.
  - *LP list read at every level (item 11).* Morning-brief step 2 and `connectors.md` now read the LP list only when LP watch is on.
- **New features are honest.** The met-log card reads "Saved. Goes to your CRM at the next check" and, with no step, "Saved: the meeting and the stage go to your CRM at the next check. Add the next step when you have it." The ask row cycles asked -> "Asked <name>"/"Asked the team" -> "Nudge" (after five quiet working days) -> "Intro made". A solo GP gets no team-note button. These are covered by new round-eight Playwright scenarios (`met-prefill`, `ask-nudge`, `ask-requested`).

## New bugs and risks, most severe first

1. **The data-server read rule is now a denylist that passes outbound and money-movement tool names (medium, new, a floor regression).** Commit 2b5f57b fixed the Carta over-refusal by making any tool on PitchBook/Harmonic/Crunchbase/Carta pass as a read when its name carries no word in `WRITE_WORDS | JOINS_AND_FLIPS | DATA_WRITE`. That verb set misses outbound and money verbs. Reproduction (scheduled transcript, scratch guard):
   - `mcp__Carta__carta-email-capital-call` -> **allowed** ("email" is in no list).
   - `mcp__Carta__carta-remit-distribution`, `carta-payout-fees`, `carta-disburse-capital`, `carta-release-funds`, `carta-settle-account`, `carta-recall-distribution`, `carta-acknowledge-call` -> **allowed** ("remit", "payout", "disburse", "release", "settle", "recall", "acknowledge" are in no list).
   - For contrast, the money verbs that *are* covered deny correctly: `carta-issue-shares`, `carta-wire-distribution`, `carta-distribute-capital`, `carta-exercise-options` all deny.
   The round-six guard denied every one of these, including the legit reads. This is not a live leak: no skill calls these tools, and the LP-watch skill only reads Carta. It is a weakening of the exact floor the product sells ("everything else is blocked, including sending ... even if an email asks for it"), for the induced case the guard exists to catch. Carta is a fund-admin platform where capital calls, distributions and LP emails are core, so a matching real tool is plausible. Fix: on those four connectors, require a read to also start or end with a read verb or be a known read name, or extend `DATA_WRITE` with email/send/remit/payout/disburse/release/settle/recall/dispatch/acknowledge/escrow/countersign/finalize/initiate; and pin denials for `carta-email-capital-call` and `carta-remit-distribution`.
2. **TRUST.md and safety.md overstate what the guard enforces (medium, new, honesty).** TRUST.md says the guard allows "on company and fund data connectors ... any tool that changes nothing." The guard cannot tell whether a tool changes anything; it checks the name against a fixed verb list. `carta-email-capital-call` changes something and the guard passes it. The one-screen trust note is the document a tester reads to decide whether to turn Instinct on, so the sentence should say what the guard actually does (allows a data-connector tool whose name carries no known write verb), not "any tool that changes nothing." This travels with finding 1.
3. **Fails open when the transcript cannot be read (high if it happens, by design, not attacker-controllable).** With `transcript_path` missing, empty, absent or a directory, every call is allowed, `send_message` included. I reproduced all four; a readable scheduled transcript denies `send_message`. The runtime sets the path, not tool content, so an injected email cannot force it. Caught only by the canary (pulse step 0, hardened to be the run's first call). Unchanged from round five; carried.
4. **A CRM field change can fire the CRM's own automations (medium, fully disclosed).** The guard cannot tell one field, record or value from another; the met-log writes `stage` and `last_contact` through a generic CRM update, which can set off a server-side rule. Stated in TRUST.md, README, safety.md and BUILD_LOG. A disclosed limit.
5. **The real-account smoke test has never run (process risk).** Zero real scheduled runs, zero dogfood. Every number here is from sims and mocks.
6. **No fresh Claude run used the 0.7.0 skills (process).** The only fresh end-to-end Claude run was the 0.6.0 Friday pulse. The 0.7.0 skills (met-log prefill, the ask-state cycle, the board-partner-first cash ask, the colleague-call draft) are covered by the engine and Playwright suites but not by a fresh Claude run.
7. **README "sample Instinct Home" is still an unverified external link (carried).** Unchanged since round six; I cannot verify the live artifact from the repo, and the solo-view partner-wording item is unconfirmed.

## Top five fixes, ranked

1. **Close the data-server read gap (finding 1).** Require a data-connector read to also start or end with a read verb or be a known read name, or extend `DATA_WRITE` with the outbound and money verbs above. Pin `carta-email-capital-call` and `carta-remit-distribution` as denials in the guard suite so this cannot regress green.
2. **Make TRUST.md and safety.md say what the guard enforces (finding 2).** On data connectors, "a tool whose name carries no known write verb", not "any tool that changes nothing."
3. **Run the smoke checklist once on the owner's account.** It is the single gating action; it moves conditions 1, 2, 4, 6 and 16, and it is the only way to confirm a real Carta or company-data read is not refused and that no real mutating tool name slips through.
4. **Add a LICENSE file and a `privacyPolicyUrl`** so the plugin clears the directory profile.
5. **Re-run setup and a scheduled pulse end to end with a fresh Claude on the 0.7.0 skill text.** Confirm the met-log prefill, the ask-state cycle, the board-partner-first cash ask and the colleague-call draft behave as the suites assume.

## Go or no-go

**No-go for five friendly VCs on 0.7.0.** Still a last-mile no-go, but down from round six, and for a new reason as well as the carried ones. The product itself got better and stayed honest: the met-log is one honest tap, asks are finished and show who was asked, and the Friday eval's eleven findings were answered in the code. But the guard floor took a hole this round. Fixing the Carta over-refusal by switching to a denylist now lets outbound and money-movement Carta tool names through, and TRUST.md claims more than the guard delivers. That is the opposite of what condition 17 asked for ("never a reason to loosen the rule"). Close finding 1, align the trust docs, then run the smoke checklist; with those done, and a LICENSE and a fresh 0.7.0 run, this is a go.

### Conditions, each with status and evidence

1. **Zero outbound in a real scheduled session: partly met, now weakened.** Sims and my ~70 fresh probes are clean for Gmail/Slack/Drive/Notion/web/shell, but finding 1 means the guard no longer guarantees "zero outbound" for a data-connector email tool name. No real run.
2. **Seven-meeting day, one heads-up each, board-eve line: partly met.** Pinned by sims at real run minutes; no real busy-day run.
3. **Create-draft tool confirmed per tester or docs say so: met.** Setup, README, TRUST and delivery match; the draft shape carries `in_gmail`.
4. **Three days of dogfood: not met.** Never run. *(Owner's real account only.)*
5. **Stall banner, Platform link, screenshots and packs from a committed build: met.** 428/428; screenshots carry the committed page hash; the guard-off, stall and Sheet-CRM states render.
6. **One-screen trust note, tested once: partly met, with a new gap.** TRUST.md is accurate except the data-connector line, which now overstates the guard (finding 2). The live walk-through is untested on a real account.
7. **Guard coverage closed and re-probed on real schemas: partly met.** The round-five read-word residual stays closed and re-probed, but the round-seven data-server change opened a new gap (finding 1).
8. **Push drops fixed and pinned at real run minutes: met.** round4/5/7/8 green.
9. **Claude-run evals against a Gmail with no create-draft tool: met (on 0.6.0).** The Friday run had no create_draft and drafted none to Gmail.
10. **Escape chain and paths closed, canary in every scheduled run: met.** Re-probed by me: curl, non-isolated Python, engine overwrite, command substitution, clobber redirect, SQL http_post, SQL second statement, calendar invite all deny; the canary denies in a scheduled session; pulse step 0 runs it first.
11. **Sheet-CRM approvals work or are not offered: met.** The met-log sheet path shows Copy and writes nothing.
12. **Pulse replies follow the level, analyst's Today leads with their own work: met.** Suite green.
13. **Setup and pulse re-run by Claude on the final skill text: not met for 0.7.0.** The last fresh run was 0.6.0.
14. **Replace allow-by-read-word, pinned: met.** `KNOWN_READS` + `STRICT_READ`/`JOINS_AND_FLIPS`; suite pins `get_and_blast`, `status_flip`, `check_out`, `view_as`, `get_then_post`.
15. **Add a LICENSE and a privacy policy URL: not met.** Directory refuses `LICENSE_MISSING`; privacy URL still a warning. *(Owner's choice: the LICENSE and the privacy-policy URL can only be set by the owner.)*
16. **Run the smoke checklist once on a real account: not met.** *(Owner's real account only; it subsumes 1, 2, 4 and 6.)*
17. **Add Carta's and the fund-data reads to `KNOWN_READS`, name Carta in the smoke line, pin it: partly met, wrong method.** Carta reads pass, the smoke line names Carta and company-data, and the suite pins the allow and several denials. But the rule was loosened into a denylist rather than Carta's read names added to the allowlist, which is what created finding 1. Re-open as condition 20.
18. **Re-run setup and a scheduled pulse end to end with a fresh Claude on the 0.6.0 skill text: met.** The Friday run did exactly this and found 11 issues, all addressed in 0.7.0. Rolls forward to condition 21 for 0.7.0.
19. **Republish the README sample Home with the View-as switcher, remove partner wording from the solo view: not met / not verifiable.** README unchanged; the link is an external artifact I cannot check from the repo.

New conditions:

20. **Close the data-server read gap and align the trust docs.** On PitchBook/Harmonic/Crunchbase/Carta, require a read to also start or end with a read verb or be a known read name (or extend `DATA_WRITE` with email/send/remit/payout/disburse/release/settle/recall/dispatch/acknowledge/escrow/countersign/finalize/initiate). Pin `carta-email-capital-call` and `carta-remit-distribution` as denials. Change TRUST.md and safety.md to describe what the guard enforces (a name with no known write verb), not "any tool that changes nothing."
21. **Re-run setup and a scheduled pulse end to end with a fresh Claude on the 0.7.0 skill text**, covering the met-log prefill, the ask-state cycle, the board-partner-first cash ask and the colleague-call draft.
