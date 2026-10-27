# Morning brief eval: aditi (Partner), Thu 22 Oct 2026 06:24 IST

Written by the Claude agent that ran the eval (saved here by the lead session, which received it as text).

## What I ran

A scheduled run, as the pulse calls the morning brief. Every connector call used `evals/mock_connectors.py --as aditi` with `INSTINCT_RUN=morning-brief-aditi`. The engine ran from the repository.

1. Load: read Home (`db list` for snap, state and runs) and unwrapped config.json. The mock prints no version lines, so versions.txt was written as a JSON map from the stored versions.
2. Due: `due --now 2026-10-22T06:24:00+05:30` gave jobs morning_brief and pulse, daily mode, window from Wed 21 Oct 06:24, run id r20261022T0624. Created the run row.
3. Approvals: nothing pending.
4. Read: the bundle shortcut, cut to the Morning brief windows (mail 7 days; calendar 30 days back to the end of tomorrow; notes since the window start). CRM, pass log and LPs read in full. One new note (tr25, Solace Treasury). Seven new threads: no pitch, no founder update; one new signal (Bluepeak Partners sent Atlas a term sheet, decision by 5 Nov).
5. Post-meeting pack for tr25: two promises (Varun owes the final cap table by Thu 22 Oct; Aditi owes the partner vote outcome by Mon 26 Oct), a CRM proposal (next step due and last contact), a follow-up draft, and the pack line.
6. Build in daily mode: no warnings, nothing dropped.
7. Questions: 15, for Atlas 10:30, Partner sync 12:00, Gravity 15:00, Orbit board Fri 10:00 and Beacon Fri 12:00. All accepted.
8. Drafts: no create-draft tool, so all owed drafts went to Home. All accepted.
9. Wrote the batch (7 documents) and finished the run row. A `due` check at 07:24 returns only pulse, so the brief will not repeat.

## Result

- Hero: "You promised: Review the board deck. Promised to Vikram Rao (Orbit Treasury), due today. You meet them tomorrow."
- Top five, in Home's order: the hero; Orbit Treasury runway under 9 months; Decide on Beacon Credit Rails; Decide on Ironwood Compliance; Decide on Solace Treasury. The Bluepeak signal, the overdue Raj intro and the Gravity offers sit under their meetings on the agenda.
- Calendar: no contradiction. Two lines miss context: Beacon's founder call is already booked for Fri 12:00; Solace's line does not show that yesterday's call moved the vote to next week (that CRM change is proposed, not yet approved).
- Drafts (all in Home, none sent, no blanks): follow-up to Varun Khanna (Solace); the Raj intro to Arjun Khurana (the context line says to add Raj in cc); term sheet markup to Ishaan Verma (attach it); co-op bank deck to Mohan Kulkarni (attach it).
- Push: "Review the board deck: Vikram (Orbit Treasury), due today" (57 characters).

## Problems, most important first

1. Morning brief step 7: "Word count is within the level's budget". The engine reported 207 words against 200: its budget step ignores the header, meeting names, source labels and evidence line, which the reported count includes.
2. Post-meeting step 7 adds the pack to packs.json "so the push says the follow-up is ready, once". Daily mode ignores packs, so the Solace pack never pushes.
3. connectors.md: "CRM people for anyone the user owes an intro". Read literally, person ids changed and new prep cards lost titles. Read people in full every run.
4. The calendar window "today and tomorrow" is narrower than the engine's 7-day stale guard and 14-day booked check. No effect today.
5. Step 6: "It never lists ... a founder the user met or booked this week". The engine applies this only to pitches, so it listed promises to Ishaan and Arjun, whom Aditi meets today. The engine looks right; the line should say "a pitch founder".
6. Drafts have one `to` and no cc, so the user must add Raj to the intro by hand.
7. Engine bug: the build changes Home's stored founder asks in place, so a changed warning is never saved. Home still says "check with Kabir" for Orbit. The same happens to pitch "booked" marks and "looks done" marks on promises.
8. Minor: the mock read prints no version lines; packs.json `meeting_id` does not say which id to use; partner sync notes repeat the Gravity and Atlas deadlines; the engine's list of new breaches calls the Orbit runway flag new though it was yesterday's hero; the run row's `finished` time is the bundle's now, not the real finish time.

Work files: `work/` (bundle.json, extracted.json, proposals.json, drafts.json, owed-drafts.json, questions.json, run/). The mock Home: `db/`.
