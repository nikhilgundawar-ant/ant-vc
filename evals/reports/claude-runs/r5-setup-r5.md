# Setup eval r5: Vikram Nair (CFO and IR), Quillwater Ventures

Written by the Claude agent that ran the eval (saved here by the lead session, which received it as text).

Run: `INSTINCT_RUN=setup-r5`, member `vikram`, now Thu 22 Oct 2026 07:00 Asia/Kolkata. Skill: `skills/setup/SKILL.md` v0.3.0 plus `shared/safety.md`, `connectors.md`, `engine.md`, `home.md`, `delivery.md`, and the steps it borrows from post-meeting, inbound-triage, portfolio-watch, pulse and morning-brief.

Result: setup ran end to end with no errors. The first brief is in Home and both scheduled tasks exist. The mock log has 94 calls: no Gmail draft or send attempt, no CRM write, no calendar write.

## What it showed Vikram

- Opening: what Instinct reads, that nothing is sent, changed or deleted without his tap, that Home is private, and "turn off Instinct".
- Drafts: "Your Gmail connector can't save drafts, so drafts wait in Instinct Home, one tap from a filled-in Gmail message." Correct: the connector has no create-draft tool.
- Level: Finance and IR (Recommended, 77%), Partner, Principal. Evidence from mail: LP, NAV, capital call and audit subjects.
- Thesis and brief time questions, recommended answers taken.
- Scheduled tasks: "Instinct" `CRON_TZ=Asia/Kolkata 20 6-19 * * 1-5` and "Instinct weekend" `CRON_TZ=Asia/Kolkata 20 9,13,17 * * 0,6`. Both prompts match `schedules.json` and carry `[instinct-scheduled-run]`. Both approve automatically.
- First brief: hero is his promise to Helen Park, 43 days late, before their 15:30 meeting (Open draft). Then Peregrine's $150K capital call, Banyan's re-up window, his overdue Kestrel runway model and Orbit's runway. 211 of 250 words. Reads right for a CFO.
- LPs tab at setup: Capital call hero for Peregrine; Fund II with $80M committed, $36M called (45%), $44M unfunded, next re-up 05 Jan; Needs you: Peregrine, Banyan, Tidewater; owners in the table (You or Aditi).

## Problems found (most important first)

1. The LPs tab loses its money and owners at the first pulse, 20 minutes after setup. `shared/connectors.md`: "no `lps` key in a pulse ... Home keeps those views as they were." `_carry_forward` rebuilds LPs from `snap/lps` with only name, commitment, window, last touch and contacts; `snap/lps` does not store the owner email or `last_call_date`. In an offline 07:20 pulse, Fund II became "Fund" with called and unfunded null, Aditi's ownership was gone, and Peregrine's alert left the LPs hero and Today until the next morning brief.
2. `drafts_in_gmail` is wiped and never read: step 2.6 saves it in `setup-out/config.json`, but step 3's `setup` rewrites that file, and nothing reads the key.
3. The third level option is noise: Principal was offered with a score of 0 (a tie-break among zeros). Expected only levels with evidence. The thesis question also asks a CFO to confirm something none of his views use.
4. "Set nothing else" in step 7.2 breaks the real create-task tool, which requires `initiation`.
5. The transcript window ("the 10 latest external meetings") can skip promises made in internal meetings.
6. Status lines become founder asks: "Team: hiring two engineers this quarter" in eleven updates gave 11 identical asks ("Founders need 11").
7. The first verb of `what` silently decides whether a draft is written (`EMAILABLE`); the skill does not say so.
8. "Finish the job, then write it" is unclear for a deliverable (the Q3 LP letter): the draft is only a cover note.
9. Small text issues: no line for the auto-approval case in step 7.3; "Next brief: tomorrow" is wrong on a Friday or Saturday setup; step 5.3's description names a pipeline a CFO does not have; the engine wrote "Neel Bhatt owes you" for a promise owed to Aditi; Peregrine's line says "$150K" twice; the chat brief does not mark the runway promise as late; the push line repeats "Helen"; `safety.md` rule 9 saves the thesis but setup step 8 does not.
10. Mock gaps: no `artifact list` or `schedule list`, so the resume check cannot run; `db list` prints file paths, not version lines.

Data note: transcript tr09 has Vikram telling Helen "Fund II is 62 percent called" (2 Sep); the LP list shows 45% after the 5 Oct call. A fixture inconsistency.

## Files

All under `evals/runs/setup-r5/`: `instinct-work/` (bundle, extracted, inbound, kpis, asks, questions, owed drafts, setup-out, run, raw responses, the offline 07:20 pulse check), `db/` (the mock Home), `mock_log.jsonl`.
