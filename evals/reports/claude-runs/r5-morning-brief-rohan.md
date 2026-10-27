# Morning brief eval: rohan (Analyst), Thu 22 Oct 2026 06:25 IST

Written by the Claude agent that ran the eval (saved here by the lead session, which received it as text).

## What I ran

The scheduled-run steps in morning-brief, pulse, inbound-triage, post-meeting and shared/*. Every call went through `mock_connectors.py --as rohan` with `INSTINCT_RUN=morning-brief-rohan`; the engine ran from the repo.

1. Load: read snap, state and runs; wrote config.json from the wrapped config.
2. Due and approvals: `due --now 2026-10-22T06:25:00+05:30` gave jobs morning_brief and pulse, mode daily, window from 21 Oct 06:25, run id r20261022T0625. Created the run row. Nothing pending.
3. Reads: mail 7 days (34 threads), calendar 30 days back to tomorrow (13 events), notes since the window start (tr16 only), CRM (open deals, companies, people, notes, pass log), LPs (15).
4. tr16 (Paysa catch-up, 21 Oct): two validated promises due Fri 23 Oct (Rhea sends the payout volumes; Rohan sets up a call with Kabir); a CRM proposal on d_paysa; follow-up fu_tr16 to Rhea; a pack line.
5. Nine new pitches: calls for Rupee Rails (100) and Paysa (96, revisit met); ask for more for Cloudmint and Vantage (65); passes for Zorro Pay and Ledgerly (geography) and Glowkart, Snackbox and Moneyminute (25). Snackbox flagged for hidden instructions; check-injection agreed. Re-read the 16 older pitches: no new injections.
6. Build: 8 items, 233 words (budget 500).
7. Prep and drafts: three questions each for the Paysa and Ruplink cards. owed.json held 20 pitch replies; all 20 drafted, kept in Home (`in_gmail` false).
8. Write: the batch wrote 8 docs; the run row finished. `due` at 07:25 returns only pulse.

## Result

- Push: "Market map of AA players: Kabir, due today" (42 characters).
- Top five, in Home's order: the market map promise (hero); 11:00 Paysa Labs (back and met our bar; looks done: set up a call with Kabir); Vaultline (the round is oversubscribed); Ruplink is back (call booked for 23 Oct 15:00); Inbound: Rupee Rails (book a call).
- No colleague's deal above Rohan's own work. Paysa and Ruplink never say "book a call".
- 21 drafts in Home, none in Gmail, no blanks, each to a named person by first name: three call offers with six distinct slots, five asks for more, twelve kind passes, one follow-up to Rhea. No reply to Paysa (met and booked), Ruplink (booked) or the three flagged pitches.

## Problems, most important first

1. "Looks done" from the wrong call. `done_by_calendar` matched "I'll set up a call with Kabir this week" to the 11:00 call with Rhea, though Kabir is not invited. The 11:00 row says "Looks done" and owed.json drops the email. Expected: when a promise names a third person, the event must include them.
2. Flagged pitch never quoted. safety.md rule 3 says to quote it "in one line for the user"; the brief skips passes, so Snackbox (a pass) shows nowhere in the brief. Expected: a brief line for each newly flagged pitch.
3. Replies drafted in two places: pulse step 4 drafts replies "into drafts.json", and morning-brief step 6 drafts the same replies from owed.json. Expected: on a morning brief, replies wait for step 6.
4. `missing` holds reasons, not facts: for Cloudmint, Vantage, Kavach and Tilt, `missing` is a reason ("Adjacent to thesis: insurtech"), not the facts the score lacked.
5. Slot window missing: call offers need two slots from the calendar, but the Morning brief row reads only to tomorrow. Expected: 14 days ahead for call slots.
6. The engine over-reads traction: Vantage's reasons say "paying customers", but the email says only "200 advisors on the platform".
7. No place in Home for the post-meeting summary: `--packs` holds only a line.
8. Tooling: the mock prints no version lines; `status` says 07:00; `build` has no `--now`; the bundle shortcut ignores windows.
9. Not a defect: the engine puts Vaultline (allocation held only until next week) above the inbound, which is right.
10. Minor: Sutra reads "book a call" though thread th0239 shows an earlier exchange with Manish; the engine's "already talking" check reads only the calendar.

## Files

Scored: `evals/runs/morning-brief/rohan.json`. Work: `instinct-work/` (bundle, inbound, extracted, proposals, drafts, questions, owed drafts, run/, pack-tr16.md). Home after the run: `db/`.
