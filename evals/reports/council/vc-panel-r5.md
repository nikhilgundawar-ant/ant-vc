# Instinct for VCs: VC panel, round five

Written by the Claude agent that played the panel (saved here by the lead session, which received it as text). **Simulated panel:** one model played all seven investors on the fictional Quillwater Ventures. No real investor took part. It read the round-five packs (evals/runs/council/briefs-r5), the screenshots and the diff from commit 6ebd923 to 0c68ca6, rebuilt round four's packs from 6ebd923 to compare, and replayed Thursday to Monday in a scratch copy. The replay's drafts come from `evals/demo.py` (hand-written examples and templates), not from Claude.

## Scores

| Persona | Level | R4 | R5 | Why, in one line |
|---|---|---|---|---|
| Aditi Rao | Partner | 7 | 8 | One 12-row sync pack for all; Friday and Monday lines name what is due. But Monday's push names a task Today hides, and Friday's 10:24 push lands mid-board. |
| Kabir Shah | Principal | 7.5 | 8 | The Lumen draft asks real questions from the data room. But a Vertex promise sits under the Lumen meeting. |
| Meera Iyer | Associate | 7.5 | 7.5 | Halo is right Thursday and her pitches get replies. Monday brings back "confirm the second meeting slot, 3 days late", with a draft. |
| Rohan Das | Analyst | 7.5 | 7.5 | 19 pitch replies ready the first morning, to named founders. But Today carries seven colleagues' races in red: "19 things, 8 urgent". |
| Tara Menon | Platform | 7 | 7.5 | The CFO draft names two candidates. Only 1 of 3 asks has a warm path; none has an intro draft. |
| Vikram Nair | CFO and IR | 6.5 | 7 | Fund II card and LP table land. His own Q3 LP letter, due Saturday, never reaches Today or a push. |
| Solo GP | $30M, alone | 6.5 | 7.5 | Own thesis, no partner pack, 18 replies grouped. Still a team calendar and an $80M fund in the replay. |

**Average: 7.6** (round four: 7.1). Quillwater's six: 7.6 (7.2). Five went up, two held, and none is above 8.

## Round-four asks and 9.5 criteria

| Item | Verdict | Evidence |
|---|---|---|
| Ask 1: drafts finish the job | Mostly | Lumen questions from Drive, Tara's names from the CRM, Vikram's and Meera's drafts say where Instinct looked, no vote-outcome draft. Meera gets a Monday draft for a meeting already held. |
| Ask 2: read the calendar | Partly | Thursday clean. Friday: Paysa "No next step set" after the call. Monday: Ruplink the same; Paysa and Halo Stale. |
| Ask 3: pushes carry news | Mostly | Every push names someone. Kabir's and Tara's heads-ups say "by 14 Oct" and "by 19 Oct", not "N days late". |
| Ask 4: one pack, team signals | Mostly | Same 12 rows for every attendee (the replay assumes owners tapped Share). Sterling AA: "8 days" for Aditi, "10" for others. |
| Ask 5: Fund and LP ownership | Yes | Fund II card; desktop table shows called, unfunded, owner. |
| C1 pack and Competing | Partly | Deals, owners, Sable and Trellis Competing yes. No sponsoring partner. |
| C2 morning line | Yes | 16 of 16 mornings with a due item. |
| C3 pushes | Partly | Aditi's 12:00 heads-up lands 6 minutes before Atlas; three pushes land inside meetings. |
| C4 calendar truth | Partly | Board review "looks done"; Sable "deadline passed" Monday; dinner titled. Paysa, Ruplink, Halo fail. |
| C5 sourceable blanks | Mostly | Cobalt notes sit in Granola; the draft says "Attach". |
| C6 pitches by 07:00 | Mostly | Rohan 19 replies; solo's Friday seven were under 24 hours old. Sutra and Lattice are skipped (already in a thread) but still say "book a call". |
| C7 Fund view, LP rows | Mostly | Phone rows drop unfunded. |
| C8 founder asks | Partly | Cash warning everywhere. One path, no intro draft, no progress state. |
| C9 heads-up lead | Yes | 61 to 100 minutes. |
| C10 clean words | Partly | Cut text; empty details (Banyan Risk Cloud, Glowkart); "Ishaan wrote" quoting a summary. |
| C11 demo, README, solo | Partly | Demo matches Thursday; no sample Home in README; solo thesis, no pack. |

## Still wrong, per persona

- **Aditi:** Monday's push opens a Today without the paragraph it names; six pushes Thursday; Friday's 10:24 lands inside the 10:00 to 12:00 board; Gravity shows Stale on its decision day; her Atlas line lost Ishaan's words to "shared to the CRM by the deal team"; pack questions are one template.
- **Kabir:** "Schedule tech diligence" (Vertex) sits under Maya's Lumen meeting, matched on "diligence", displacing Lumen's 13-days-late Q3 deck; no Thursday push names his late Kite checklist; Cobalt is still two rows.
- **Meera:** Monday's Halo draft "Following up as promised: confirm the second meeting slot"; Rivulet, Halo and Sable show Stale on Monday; two drafts are only "[Add it here.]"; Lattice says "book a call" with no draft and no reason; no partner named on her deals.
- **Rohan:** seven colleague rows, all Urgent (on Friday, Meera's Sable sits above his late market map); Vaultline lost "allocation until next week"; Coinvault and Glowkart show Stale with empty details; three call drafts offer the same Mon 11:00.
- **Tara:** two of three asks have no path; none has an intro draft or a state.
- **Vikram:** the Q3 letter is invisible all week while Monday pushes what Aditi owes him for it; phone LP rows lack unfunded.
- **Solo GP:** partner meetings on the agenda and an $80M fund; Monday's push is missing from Today; seven call drafts offer identical slots.

## Top five changes

1. **Pushes that fit the day (5 of 7):** none inside a meeting or in the 15 minutes before one; fold a later heads-up into the earlier run; at most four a day; every pushed item shows on Today.
2. **Clean words, real quotes (5 of 7):** quote marks only around founders' own text; no cut or empty details; one row per company.
3. **Calendar truth past the weekend (4 of 7):** for five working days after a meeting, no Stale, no "No next step set", no "confirm the slot" and no draft; offer a CRM update instead. "Looks done" never turns overdue.
4. **Own work first (4 of 7):** an analyst sees colleagues' races as one grey line; owners keep the founder's words and dates.
5. **Right line, right place, right weight (4 of 7):** attach items to meetings by company or person only; rank a CFO's own deliverable like a promise to a founder.

## Reaching 9.5: tests on the same replay

1. Both packs identical for every attendee, Sterling AA included; rows name owner, partner, round and amount.
2. No push inside a calendar event or in the 15 minutes before one; at most four per person on Thursday; every pushed item visible on Today.
3. Heads-ups on owed items say "N days late"; a Thursday push names Kabir's Kite checklist.
4. Through Monday, no Stale, "No next step set", "confirm the slot" or draft for Halo, Rivulet, Sable, Paysa, Ruplink or Prism; Gravity not Stale on Monday.
5. Rohan's Today has at most one colleague line, not Urgent, below his market map.
6. Vaultline keeps "until next week"; Trellis keeps "our Series A".
7. Lumen's agenda shows Maya's Q3 deck, never Vertex.
8. Vikram's Q3 letter on Today Thursday and Friday and in Friday's morning line, with a draft or "Instinct can draft it".
9. Each of Tara's asks has a path or "none found", an intro draft and a state.
10. Clean output and setup: zero "…" or empty details; no slot offered twice in a morning; a reason on every pitch without a draft; the README links a sample Home; the solo GP replays on its own calendar and fund.
