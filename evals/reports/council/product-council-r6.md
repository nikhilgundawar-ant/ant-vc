# Instinct for VCs: product council, round six

Written by the Claude agent that played the council (saved here by the lead session, which received it as text). **Simulated council:** one Claude agent played a product manager, a UI/UX designer (Anthill Evergreen), an AI engineer for safety and security, and a QA lead. No real person took part. Reviewed 23 Oct 2026 against commit 81c3e95 (version 0.6.0, round seven). The repo was not changed. Every run and probe used a scratch copy at `/tmp/product-council-r6/repo`.

This round is judged against the round-five report (average 8.0): its bugs, its top five fixes, and go/no-go conditions 1 to 16.

## Scores

| Reviewer | R5 | R6 | In one line |
|---|---|---|---|
| PM | 8 | 8.5 | Asks are finished, the LP letter and met-log ship, and both open guard-policy questions are answered. Still gated on the real-account smoke test and a LICENSE. |
| Designer | 8 | 8.5 | 0 contrast fails across 403 states (was 388), lint 0. The met-log card is clean and honest. The README "sample Home" link still opens an older build. |
| AI engineer | 8 | 8.5 | The read-word residual is closed and pinned, config writes are locked to bounded tuned fields, and ~130 fresh probes got nothing out. The fail-open is unchanged by design. New: the tightened reads can over-refuse a real CRM or Carta read. |
| QA lead | 8 | 8 | Every sim re-ran green (133, 574, 403, 0, 0) and screenshots are from the committed page. But the smoke test is still unrun, LICENSE still blocks the directory, and no fresh Claude run used the 0.6.0 skills. |

**Average: 8.4** (round five: 8.0). Still a last-mile no-go, for the same reason as round five: nobody has walked on the floor once on a real account.

## What I re-ran in the scratch copy

- `python3 evals/runner.py`: **133/133** in 59s. The guard suite inside it is **574/574**.
- `python3 evals/runner.py --suite guard`: **574/574** on its own.
- `python3 evals/home_qa.py` (Playwright, phone and desktop, light and dark, every level): **403/403**.
- `python3 evals/design_lint.py`: **0 violations in 214 CSS rules**.
- `python3 -I -S engine/instinct.py lint --root .`: **0 violations**.
- `claude plugin validate .`: passes with warnings. Under `--profile directory` it still **refuses the plugin for a missing LICENSE**. Privacy URL is still a warning.
- My own guard probe harness: ~130 calls through `hooks/guard.py` with its real stdin shape (`{"transcript_path","cwd","tool_name","tool_input"}`), transcript carrying `[instinct-scheduled-run]`, in scheduled and normal sessions. All targets were placeholder hosts and dummy files in the scratch folder.

## Verified fixed since round five

Each re-checked with evidence. The round-five top-five fixes and residual risks:

- **R5 fix 2 and risk 1: replace allow-by-read-word (medium, latent).** Done and pinned. `READ_WORDS` is gone. On Gmail, Google Calendar, Google Drive, Granola, Slack and Notion a read passes only by exact known name (`KNOWN_READS`). On every other server a read must start or end with a read verb (`STRICT_READ`) and carry no join or flip word (`JOINS_AND_FLIPS`). My probes: `get_and_send`, `get_and_delete`, `describe_then_post`, `status_flip`, `check_out`, `view_as` all deny; the suite pins `get_and_blast`, `describe_and_email`, `status_flip`, `check_out`, `view_as`, `get_then_post`. Condition 14 is met.
- **R5 fix 4 and risk 3: snap/config write policy (low).** Done. `config_verdict` lets a scheduled run change `snap/config` only through `update` of the tuned fields (`weights`, `today_items`, `dwell_scale`, `tuned_at`/`updated_at`), with bounds (weights 0 to 5, Today 3 to 15, dwell 0.5 to 3). I confirmed deny for: `set` on config, `str_replace` on config, any `home_url` or `level`, out-of-range values, a poisoned `file_path`, and the same through `batch`. Allowed: a real `tune` merge inline or via `file_path`.
- **R5 fix 5: harden the fail-open at the skill layer.** Done. `skills/pulse/SKILL.md` step 0 now says the canary is the run's very first tool call, and "anything else (an error, no output, or another tool already called before it)" is treated as guard-off. This is skill discipline, not a guard guarantee, but it closes the "skipped step 0" gap the round-five report named.
- **Guard escape chain (carried closed).** Re-probed: `curl`, non-isolated Python, `sort -o`, `date -f`, env prefix, command substitution all deny; isolated engine `check` allows. SQL: `http_post`, a second statement, `SELECT ... INTO` deny; a plain `SELECT` allows. Calendar: `attendees`, `attendeeEmails`, another `calendarId`, `eventType`, `sendUpdates`, `visibility public`, an extra `conferenceData` key, and Notion Calendar with attendees all deny; a plain hold allows.
- **New features are safe.**
  - *Founder-ask drafts from warm paths:* a draft, never sent. Goes to the known contact, the colleague who knows them, or the team. Safe.
  - *LP letter draft:* `_letter_inputs` draws only from portfolio companies, their KPIs and fund figures. Quiet pipeline deals are structurally excluded (safety rule 6 holds). No invented numbers (rule 5).
  - *One-tap meeting log that moves a stage:* Home offers only the next active stage, so it can never move a deal to passed or closed; `pending_actions` refuses a `next_step` whose stage reads pass/clos/lost/won/dead/portfolio. `met` sets last contact, `stage` moves the deal. Both ride a normal CRM field write, which the guard allows (the disclosed field-level limit).
  - *next_step payload `met` and `stage`:* verified above; the `met-log-380.png` card reads "Saved. Goes to your CRM at the next check", honest that it is not instant.
- **Evidence current.** Screenshots carry the committed page hash (`92e321cdc55d...`), and I re-ran Playwright against it. BUILD_LOG, TRUST.md, shared/safety.md, shared/home.md and the smoke checklist are all at 0.6.0 and describe the new rules correctly.

## Bugs and risks reproduced, most severe first

1. **The tightened reads over-refuse a real CRM or Carta read (medium, new, availability not security).** `STRICT_READ` dropped "view", "status", "info", "check", "lookup"-style words and refuses any read whose name does not start or end with a read verb. Real read-only tool names that now deny: `affinity-view-records`, `affinity-field-values`, `hubspot-batch-read-objects` ("batch" is a write word), `carta-capital-accounts`, `harmonic-enrich-company`, `pitchbook-company-profile`. For scheduled runs the ones that bite are the CRM (if it is Affinity or HubSpot with a non-verb read name) and **Carta**, which the Monday digest and LP watch read for the LP view. The smoke checklist's read-coverage line names the six whitelisted servers and "the CRM's own read tools", but **not Carta or the Fund-data connector**. Steps: feed the guard a scheduled transcript and `mcp__Carta__capital-accounts` with `{}`; it denies. Effect is not a leak: the run continues, Home keeps what it knew, and the blocked call is named in the run row. But the LP view can go stale with a blocked-call note. Fix: add Carta's real read tools to `KNOWN_READS` (or at least to the smoke read-coverage line), and have the smoke test list the real CRM read tools and add any refused name to `KNOWN_READS` rather than loosen the rule.
2. **Fails open when the transcript cannot be read (high if it happens, by design, not attacker-controllable).** With `transcript_path` missing, empty, absent or unreadable, every call is allowed, `send_message` included. I reproduced all four. The path is set by the runtime, not by tool content, so an injected email cannot force it. It is caught only by the canary, now hardened at the skill layer (step 0 must be first). Unchanged from round five; carried.
3. **A CRM field change can fire the CRM's own automations (medium, fully disclosed).** The guard cannot tell one field, record or value from another. The new met-log writes `stage` and `last_contact` through a generic CRM update, so a field change could set off a server-side email or Slack alert the user built. Stated in TRUST.md, README, safety.md and BUILD_LOG. A disclosed limit, not a defect.
4. **The real-account smoke test has never been run (process risk).** Zero real scheduled runs, zero dogfood. The guard-inside-a-real-run, busy-day, three-day and turn-off checks are written (and expanded this round with the draft-reslot, founder-question and met-log probes) but unexecuted. Every number here is from sims and mocks.
5. **The directory refuses the plugin for a missing LICENSE (ship-blocking for submission).** `claude plugin validate .` passes by default, but `--profile directory` refuses it: `LICENSE_MISSING`. No LICENSE file, and `plugin.json` has no `license` key. `privacyPolicyUrl` is still a warning. Side-load works; a marketplace install does not. Unchanged from round five; carried.
6. **No fresh Claude-in-the-loop run used the 0.6.0 skills (process).** The last end-to-end Claude runs (`r6-setup-meera`, `r6-pulse-aditi`) were on the 0.5.0 skill text. The 0.6.0 skills (reslot drafts, the founder-question reply, the met-log apply path) are covered by the engine suites but not by a fresh Claude run. Condition 13 for this version is open.
7. **Warm-path strength is one-way (low, quality not safety).** Relationship strength counts inbound email, so a frequent cold sender can rank as a "warm path" for a founder-ask intro draft. Nothing is sent, so the risk is a wrong suggested intermediary, not a leak.
8. **README "sample Instinct Home" link still opens an older build (carried from the VC panel).** The link is the one each tester would forward. It has no "View as" switcher, so a reader cannot see the seven role views. I cannot verify the live artifact from the repo; it is an external published page. Process item.
9. **`snap/config/<sub>` writes are allowed (very low).** A scheduled run can `set` a document under `snap/config/x`; the page never reads it, so it is harmless. Noted for completeness.

## Top five fixes, ranked

1. **Run the smoke checklist once on the owner's account.** It is the single gating action. It moves conditions 1, 2, 4, 6 and 16, and it is the only way to catch a real connector read the new rules refuse. Do the busy day and three days of dogfood.
2. **Close the read over-refusal for scheduled runs.** Add Carta's real read tools (and the CRM's) to `KNOWN_READS`, and name Carta and the Fund-data connector in the smoke read-coverage line. Pin a test with a real-shaped Carta read name so this cannot regress the other way.
3. **Add a LICENSE file and a `privacyPolicyUrl`** so the plugin clears the directory profile.
4. **Re-run setup and a scheduled pulse end to end with a fresh Claude on the 0.6.0 skill text.** Confirm the reslot drafts, the founder-question reply and the met-log apply path behave as the engine suites assume.
5. **Republish the README sample Home to the 0.6.0 demo with the View-as switcher**, and check its hash against `qa.json`. Remove partner wording from the solo view there.

## Go or no-go

**No-go for five friendly VCs on 0.6.0, but a last-mile no-go, as in round five.** The guard is a real floor and it is stronger than round five: the read-word residual is closed and pinned, config writes are locked to bounded tuned fields, and in ~130 fresh probes nothing outbound, write, delete, settings-rewrite, network or secret-read passed a scheduled session. The new features (finished asks, the LP letter, the met-log) are safe. What keeps this a no-go is unchanged: no real scheduled session has ever run, there is no LICENSE, and the tightened reads now need one real-account pass to prove they do not refuse a read the morning brief or LP watch needs. Run the smoke checklist; if it passes and the Carta read is covered, this is a go.

Conditions 1 to 16, each with evidence:

1. **Zero outbound tools in a real scheduled session: partly met.** Closed and pinned; ~130 fresh probes clean. No real scheduled session has run.
2. **Seven-meeting day, one heads-up each, board-eve line: partly met.** Pinned by round3/4/5/6/7 at real run minutes. No real busy-day run.
3. **Create-draft tool confirmed per tester, or the docs say so: met.** Setup, README and TRUST match; the draft shape carries `in_gmail`.
4. **Three days of dogfood: not met.** Never run.
5. **Stall banner, Platform link, screenshots and packs from a committed build: met.** Screenshots carry the committed page hash; I re-ran Playwright (403/403). The guard-off, stall and Sheet-CRM states render.
6. **One-screen trust note, tested once: partly met.** TRUST.md is accurate and updated for the new read rule and the config rule. "Turn off Instinct" and the live walk-through are untested on a real account.
7. **Guard coverage closed and re-probed on real schemas: met.** The read-word design risk (round-five residual) is now closed; re-probed by me and the suite.
8. **Push drops fixed and pinned at real run minutes: met.** round3/5/6/7 green; "pushed stays on Today" is pinned by round7.
9. **Claude-run evals against a Gmail with no create-draft tool: met (on 0.5.0).** `r6-setup-meera` and `r6-pulse-aditi` ran without a Gmail draft call. Not re-run on 0.6.0 (see condition 13).
10. **Escape chain and paths closed, canary in every scheduled run: met.** Verified above; the canary denies in a scheduled session and prints in a normal one; both prompts carry the marker; pulse step 0 runs it first.
11. **Sheet-CRM approvals work, or are not offered: met.** `pending_actions` refuses a Sheet-CRM `crm_update`/`next_step`; the met-log card shows "Copy change ... Paste it into your sheet" for a sheet.
12. **Pulse replies follow the level, analyst's Today leads with their own work: met.** `modules.triage` gates replies; analyst `today_items` is 12; round7 keeps the colleagues' line from taking an own-work place.
13. **Setup and pulse re-run by Claude on the final skill text: partly met.** The last Claude runs were on 0.5.0. The 0.6.0 skills are covered by the engine suites but not a fresh Claude run.
14. **Replace allow-by-read-word, pinned by a read-word-named side-effecting tool: met.** `KNOWN_READS` + `STRICT_READ`/`JOINS_AND_FLIPS`; suite pins `get_and_blast`, `describe_and_email`, `status_flip`, `check_out`, `view_as`, `get_then_post`.
15. **Add a LICENSE and a privacy policy URL: not met.** Still refused under `--profile directory`.
16. **Run the smoke checklist once on a real account: not met.** Still unrun; it subsumes 1, 2, 4 and 6.

New conditions:

17. Add Carta's (and the Fund-data connector's) real read tools to `KNOWN_READS`, and name Carta in the smoke read-coverage line, so a scheduled Monday digest or LP watch is not silently refused the LP reads it needs. Pin it.
18. Re-run setup and a scheduled pulse end to end with a fresh Claude on the 0.6.0 skill text (condition 13 for this version), covering the reslot draft, the founder-question reply and the met-log apply.
19. Republish the README "sample Instinct Home" to the 0.6.0 demo with the View-as switcher, and remove partner wording from the solo view there.
