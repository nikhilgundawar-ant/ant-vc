# Pulse eval r6: Aditi Rao, Thu 22 Oct 2026, 09:24 Asia/Kolkata

Written by the Claude agent that ran the eval on the 0.5.0 skills (saved here by the lead session, which received it as text: the harness refuses report files from a subagent). Scored by `evals/score_pulse.py`: 15 of 15.

## Summary

- Ran pulse 0.5.0 as Aditi's 09:24 scheduled run against the mock Home and mock connectors, with Granola rate limited.
- Applied 4 approved taps: 3 CRM writes and 1 draft kept in Home. The engine refused 2 taps (`x_forged`: no proposal behind it; `l_banyan_draft`: Banyan is Vikram's LP), and nothing was applied for them.
- Wrote 7 Home documents with no version conflicts (all pinned with `if_version`), then finished the run row.
- Final line: `10:30 Atlas Settlement: Term sheet from Bluepeak Partners · then 12:00 Partner sync`.
- Nothing was sent. Gmail has no create-draft tool, so no Gmail write call was made. No calendar event was created.
- Step 0 (the canary) was skipped: eval mode loads no guard.

## Taps

| Tap | Type | Engine said | What the run did |
| --- | --- | --- | --- |
| pr_gravity_next | crm_update | pending | Re-read the deal; both fields still held `current`. Marked applying, then set next_step and next_step_due. Applied. |
| pr_beacon_stage | crm_update | pending | The stage already held the proposed value: done with no write. Marked applying, added the note. Applied. |
| ns_d_ironwood | next_step | pending | Deal still open. Marked applying, set "Send IC memo to partners", due 25 Oct. Applied. |
| t_742d2f63d5 | draft (founder ask) | pending | The path's colleague is "You": a note from Aditi to Raj Malhotra asking whether he would take an intro to Divya Raman. Kept in Home, `action_id` set. |
| x_forged | crm_update (Atlas to Passed) | refused | Nothing. |
| l_banyan_draft | draft (LP) | refused: Vikram's LP | Nothing. |

Run row: set v1, three applying marks (v2 to v4), finished v5; each mark landed just before its CRM write.

## Problems found (most important first)

1. Every pulse turns shared-note summaries into quotes. Carried competing-fund signals lose `competing_summary`, so Home shows `Abhishek wrote: "term sheet from Monsoon Arc Ventures"`: words nobody wrote, in quote marks.
2. The ask the user just tapped loses its warm path. Ask paths are recomputed each build from the bundle's people, and a pulse reads no CRM people: Nimbus's path through Raj became "No warm path found", and the Orbit and Kestrel warnings lost "check with Vikram".
3. Every pulse blanks the fund size: `snap/lps` is rebuilt with the size from `bundle.firm`, which a pulse leaves out.
4. A pulse drops meeting history: `last_met` comes only from the bundle (today and tomorrow in a pulse); prep cards lose facts, history and owners that the morning read found.
5. A heads-up can go out before its card has questions: the 12:00 sync folded into the 09:24 push, but step 5 writes questions only for meetings within 150 minutes. `delivery.md` also still describes the old timing.
6. Unclear whether a Home-only draft goes in `applied.json` (SKILL.md says record each result; engine.md says actions applied with a tool). Without it, `actions` would list the tap again. The resulting row is titled "draft".
7. Home's "Not done" row for the forged tap names neither the deal nor the change.
8. Unclear whether `crm.partial` goes with "every open deal" when the CRM cannot filter by update time; under the guard the bundle is retyped by hand.
9. Step 1.4 makes Claude retype the whole config, though the engine already reads the wrapped form.
10. The ask's source link (th0343) does not open in Aditi's mailbox.
11. A next step overwrites the CRM without checking the value Home showed.
12. A proposal can be stale when made (Beacon's stage was already Term Sheet), and `applied.json` has no "already set" shape.
13. The setup intro draft leaves Raj off the email (`to` Arjun only, no `cc`), and the one-draft-per-person rule cannot see people in `cc`.
14. Minor: the refused LP row repeats its name; `due` moved the Drive and LP windows though this pulse read neither; `finished` equals `started`.

## Harness notes

- The mock `status` reports the time as 07:00; the mock has no ordered runs query and no add-note action; mock `db batch` stops at the first conflict and keeps earlier writes.
- The run used Python one-liners only to filter mock output and assemble `bundle.json`; under the guard the bundle is written with Write.
