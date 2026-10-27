# Morning brief, run by Claude in eval mode (round three)

Written by the Claude agent that ran the eval (saved here by the lead session, which received it as text). Members: rohan (Analyst) and aditi (Partner). The mock Home was set up the morning before (Wed 21 Oct 06:51) with that day's snapshots and run row; now is Thu 22 Oct 07:00.

## Result

- Nothing failed, nothing was sent (0 send attempts in either mock log), and every engine and mock command exited 0.
- Score: the Claude-written brief leads with the right five, 9 of 10 (round two: 6 of 10). The runner now passes 69 of 69.
- Heroes: Rohan "Market map of AA players. Promised to Kabir Shah, due today" (232 of 500 words). Aditi "Review the board deck. Promised to Vikram Rao (Orbit Treasury), due today. You meet them tomorrow" (200 of 200 words at build, 204 after the drafts command).
- Commitments read from the new notes: 2 of 2 accepted by the checker for each member.
- Drafts saved to the mock Gmail: Rohan 11 (a merged follow-up to Rhea at Paysa Labs; call replies to Rupee Rails, Sutra Compliance, Tessera Settle; a confirmation to Ruplink; asks for more to Vantage Wealth OS and Cloudmint Insure; kind passes to Zorro Pay, Ledgerly, Glowkart and Moneyminute; none to the flagged Snackbox). Aditi 4 (Varun Khanna follow-up, the Fable Bank intro with Raj's address from the CRM, the Atlas term sheet markup with a bracketed gap and an attach note, the co-op bank deck to Mohan Kulkarni).

## What the agent decided on its own

- Took the pass log from the bundle shortcut: no mock command returned it.
- Re-flagged two pitches (Prana Collections, Paperplane AP) that the seeded setup had not flagged, so Prana dropped from "book a call" to "ask for more". (Cause: the eval seed did not carry the injection flags. Fixed in the seed.)

## Problems it found in the skill text

1. `shared/connectors.md` requires the pass log but never says where it lives.
2. Several drafts can target one person (follow-up, pitch reply, owed email), and "never edit a draft already in Gmail" blocks merging; the draft shape says `commitment_id` or `inbound_id`, not both.
3. Step 3 implies a reply to every new pitch; the engine caps pitch replies at three and skips flagged pitches; inbound triage has no flagged exception.
4. The morning-brief build command has no `--packs`.
5. "No two lines say the same thing" only says how to fix hero duplicates.
6. Step 8 shows `run/brief.md`, which is out of date once the drafts step runs.
7. The Morning brief row leaves out CRM people, which an intro needs.
8. `due` returns `morning_brief` and `pulse`, but the skill hardcodes `--jobs morning_brief`.

## Engine output that looked wrong

1. The `drafts` command adds "draft ready" to meeting lines but does not re-render the brief text, the shareable text, the word count or `run/brief.md`.
2. The word budget counts only ranked lines, not the hero or the meeting lines.
3. Beacon Credit Rails appears both in the partner sync line and in Next up.
4. Both heroes are promises due today; the level reminders in the skill say otherwise.
5. Minor: "$310K annualised revenue" earns no revenue signal; a run by hand records `pushed: true`; the Atlas prep card uses another address for Ishaan than the invite; Prana's quote is cut mid-phrase.
