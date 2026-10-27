<!-- VC panel, round ten. Written by one Claude agent playing all seven personas on a clean clone at a023dd2 (0.7.3); saved by the main session. Simulated: no real investor took part. -->

# Instinct for VCs: VC panel, round ten

**This is a simulated panel. No real investor took part.** One Claude agent played all seven: six people at the fictional Quillwater Ventures (Aditi Rao, Partner; Kabir Shah, Principal; Meera Iyer, Associate; Rohan Das, Analyst; Tara Menon, Head of Platform; Vikram Nair, CFO and IR) and a solo GP running a $30M fund alone.

## What I read and ran

- **Read, in order:** my round-nine report (`evals/reports/council/vc-panel-r9.md`), whose "Reaching 9.5 or 10" tests are this round's bar; "Round ten: what changed" in `BUILD_LOG.md`; `git diff 070b9d8 a023dd2` for `engine/`, `skills/`, `shared/`, `home/`, `evals/demo.py`, `evals/replay.py` and `evals/home_qa.py` (30 files, 1,341 lines added, 266 removed); the seven packs from `python3 evals/panel_pack.py --out evals/runs/council/briefs-r10`.
- **Fresh clone** at a023dd2 (0.7.3). The runner and Home QA rewrite tracked outputs; they were copied out and restored with `git checkout`, so the clone holds no tracked edits.
- **Suites:** `python3 evals/runner.py`: 158 of 158 deterministic checks (7 Claude-run score rows skipped in a clean clone), 156.5 s. `--suite round10` 15 of 15; `round9` 10 of 10; `guard` 718 of 718. `design_lint.py` 0 violations in 216 CSS rules. `home_qa.py` 477 of 477, `page_sha256` matching `home/index.html`.
- **My own replays, beyond the suite,** all with `replay._replay_windowed` (each run reads only its own window):
  - all seven against `replay._week`, Thu 22 to Mon 26, run by run (hero, Today rows, push, each ask's path and warning, met-log prompts);
  - all seven to Fri 30 with no taps; Aditi also to Mon 9 Nov;
  - Vikram and the solo GP: "Sent it" on the capital-call chase at Thu 22 10:00, to Mon 9 Nov (Vikram also to Fri 13 Nov), with variants (the sent email also in their mail; the second note also sent Thu 29 10:00);
  - Tara to Mon 9 Nov: "Sent it" on her ask notes Thu 22 10:00, then (a) Aditi's intro email Mon 26 12:00, (b) Aditi quiet, (c) quiet and the nudge sent Thu 29 10:00, (d) quiet and "Aditi said yes: ask the team" on Orbit Thu 29 10:00, (e) quiet and "Ask the team instead" on Nimbus Thu 29 10:00;
  - Meera: her 22 Oct met logs saved Thu 19:05; variant A never adds a step (to Mon 9 Nov), variant B adds Halo's step Fri 23 10:00;
  - probes: Aditi "Sent it" on a promise draft and nothing else; Rohan "Sent it" on 19 pitch replies; a words scan and a push scan for all seven to Mon 9 Nov;
  - 25 replayed Homes rendered in the real `home/index.html` with the QA harness, each row opened in turn.
- **Drafts in the replay come from `evals/demo.py`, not Claude.** "Demo only" marks wording that only the demo gets wrong.
- The three Claude-run evals on 0.7.3 were not available when this panel finished, so none is cited.

## In short

- **Round ten closes almost every round-nine test inside the week those tests cover (Thu 22 to Fri 30):**
  - Real read windows now match the pack at every run for all seven: 0 of 48 runs differ for each member (round nine: 6 to 44).
  - Every draft's note shows on the hero and on its row, as "Before you send: ...". A draft with blanks shows "Fill in 3 lines" and "check the firm's view with Aditi". Meera's Monday push says "3 lines to fill".
  - Vikram's chase reads "chased Peter on 22 Oct" from Fri 23. A shorter second note is ready on Thu 29.
  - Tara's one email gets one nudge: "3 founder asks wait on Aditi", one draft, one push. The partner's yes is an explicit tap ("Aditi said yes: ask the team"). No "Draft coming" chip sticks.
  - Late work stays: Aditi's paragraph is on Today every morning to Fri 30, Vikram sees "Aditi Rao owes you" from Tue 27, and Meera's step request lasts to Mon 9 Nov as "2 next steps to add".
- **What keeps four of seven at 9 shows in the second week, which no suite reaches:**
  - **Money forgets.** On Mon 9 Nov, 18 days after "Sent it", Vikram's hero says "no touch in 113 days", and every weekday to Fri 13 Nov the morning drafts the first chase again, even with the sent email in his mail. The same happens to the solo GP.
  - **Old news is pushed as news.** When a founder's email leaves the morning's 7-day read, its competing-fund signal gets a new id, and the next pulse pushes it: 9 such pushes across 5 members by Mon 9 Nov (4 by Fri 30).
  - **Carried signals lose true words.** "From Arjun's email, shared by the deal team" on Aditi's own deal; "next: partner meeting Monday by 26 Oct" on Thu 29; and a broken hero, "term sheet from Bluepeak Partners Decision by 05 Nov.", on 56 of Aditi's 200 runs to Mon 9 Nov.
  - **The 7-day keep has an edge.** Aditi's Arjun intro (9 days late, two rival funds) leaves Today on Thu 29 and Fri 30. Her paragraph, and Vikram's wait on it, leave from Tue 3 Nov.
  - Smaller: Meera's Pipeline hero reads "saffron Peak Capital" from Sat 24. A nudge draft still bumps an ask that went to the team. Aditi is told to "check with the board partner before sourcing" about her own boards.
- **Scores: average 9.21** (round nine: 9.0). Kabir, Rohan and Tara reach 9.5. Aditi, Meera, Vikram and the solo GP hold at 9.

### Round-nine tests on this build

| Round-nine test | Verdict | Evidence |
|---|---|---|
| 1. The real windows match the pack | Met | 0 of 48 runs differ for each of the seven. Vikram Thu 07:20: "09:00 Ledger & Lane Fund Services: You owe: sign off on the capital account statements". Aditi Sat 24 09:24 hero keeps Gravity Payouts and "Two other funds with offers". Kabir Thu 07:28: one row, with Vertex Card Issuing. Rohan Fri 13:25: "15:00 Ruplink: Revisit condition met: AA licence granted in September". Meera's Lattice keeps "you already write to them" to Mon 26 |
| 2. What a draft needs reaches the user | Met | Kabir Fri 07:00: hero and Lumen row show "check it still stands, or tap Done if it was settled in the room". Meera Fri 06:29: "Draft has 3 lines to fill: check the firm's view with Aditi", chip "Fill in 3 lines". Meera Mon 06:29 push: "Omkar, 7 days late. 3 lines to fill". Vikram Thu 07:00 hero: "found no fee offset clause. Add it before you send" |
| 3. Money and asks after sending | Partly met | Asks: met (Thu 29 06:28 one nudge for Nimbus, Orbit and Kestrel, with a draft; Orbit offers "Aditi said yes: ask the team"; no "Draft coming" after the team note is sent). Money: met to Fri 6 Nov; not met after: Mon 9 Nov 06:20 says "no touch in 113 days" and drafts the first chase again. Same for the solo GP |
| 4. Nothing late vanishes | Met as written | Aditi's paragraph is a row every morning Tue 27 to Fri 30. Vikram: "Aditi Rao owes you" from Tue 27. Meera variant A, Fri 30: "Halo Reconcile: met 22 Oct, add the next step". Edge: both paragraph lines are gone from Tue 3 Nov, and Aditi's Arjun intro is off Today on Thu 29 and Fri 30 |
| 5. Words at every hour | Mostly met | 0 pushes end in "…" for all seven to Mon 9 Nov. Rohan Thu 29 15:25: "Review ready: Bharat Risk Labs: 13 days in screening (usually 7). Next: Screening memo". Letter row: "Draft ready: fill in 5 lines, check the figures, then send it". But Meera's Pipeline hero reads "saffron Peak Capital" |
| 6. QA shows what the user sees | Met | `met-step-380.png` shows "Halo Reconcile: met 22 Oct, add the next step" with an empty field and Save. QA "no-draft-coming" passes |

## Scores

| Persona | Level | R9 | R10 | Why, in one line |
|---|---|---|---|---|
| Aditi Rao | Partner | 9 | 9 | Her first week is now right, but her Thu 29 and Tue 3 Nov heroes are stale or broken, and her most contested late promise drops off Today. |
| Kabir Shah | Principal | 9 | 9.5 | Every round-nine test of his is met. Left: one week-old Lumen push (twice) and a stale carried row. |
| Meera Iyer | Associate | 9 | 9 | Her met-log and blank-draft loops are right end to end, but her Pipeline hero lowercases a fund for 16 days and two week-old signals come back as pushes. |
| Rohan Das | Analyst | 9 | 9.5 | Heads-ups keep the verdict on real windows and no push is cut. Left: a stale Vaultline push and row. |
| Tara Menon | Platform | 9 | 9.5 | One nudge per note, an explicit "Aditi said yes", no stuck chips, asks remembered to Mon 9 Nov. Left: the nudge draft does not narrow when an ask moves on. |
| Vikram Nair | CFO and IR | 9 | 9 | The chase is followed for two weeks, then forgotten: from Mon 9 Nov the first chase is drafted again every morning. |
| Solo GP | $30M, alone | 9 | 9 | Same money loop as Vikram, plus a stale push on Mon 9 Nov. |

Average 9.21 (round nine: 9.0); Quillwater's six 9.25. Three up half a point, four held, none down.

## Each persona

### Aditi Rao, Partner (9, held)

Better since round nine: the Sat 24 hero keeps Gravity Payouts and "Two other funds with offers"; the Arjun intro row shows its refresh note; the markup adds "Attach the markup before you send"; "Write the portfolio highlights paragraph" is a row every morning Tue 27 to Fri 30; the Mon 26 Solace met log fills in "Partner vote" with no date; no line is only "Arjun wrote on 20 Oct.".

Still costs time or trust:
- Thu 29 and Fri 30 06:24 hero: "Gravity Payouts: two other funds with offers. IC, next: partner meeting Monday by 26 Oct. From Arjun's email, shared by the deal team." She leads Gravity, the email was to her, the step is three days past, and the 31 Oct deadline is not in the hero.
- The same mornings, "Intro Arjun to Raj Malhotra at Fable Bank" (9 and 10 days late) is on no Today row: the keep-on-Today rule covers promises 1 to 7 days late. It returns Mon 2 Nov.
- Fri 23 09:24 and 11:24: the Arjun row loses "Two other funds with offers" (2 of 66 runs).
- From Tue 3 Nov (8 days late) the paragraph is on no row and in no push.
- Tue 3 Nov 08:00 hero: "Atlas Settlement: term sheet from Bluepeak Partners / term sheet from Bluepeak Partners Decision by 05 Nov." (56 of 200 runs, Tue 3 to Sun 8 Nov). Mon 9 Nov 07:24 pushes "their deadline passed 05 Nov".
- Her Portfolio's founder asks: Orbit says "check with the board partner before sourcing", Kestrel "check with Vikram before sourcing". She is the board partner.
- Four met-log forms stay open Fri 23 midday to Wed 28.

For 9.5 or 10: carried signals keep the founder's dated words and a live date; no hero is a fragment; a promise with a rival, or one a colleague waits on, stays on Today until Done; founder asks treat her as the board partner.

### Kabir Shah, Principal (9.5, up from 9)

Better: real windows match the pack on every run; one row with the company; he now sees each draft's check on the hero and the Lumen row; the demo's Fri 23 reslot is clear of his partner meeting.

Still costs: Thu 29 07:28 push "Lumen Ledger: two other funds in diligence" (Maya wrote on 21 Oct; new item id once the email left the 7-day read; again Mon 9 Nov); Thu 29 and Fri 30 row "...next: cohort analysis review by 26 Oct. From Maya's email, shared by the deal team"; "Deal: next step was due 15 Oct" without naming the deal; three met-log forms open Fri 23 to Thu 29.

For 10: carried signals keep their id and words; a folded deal fact names the deal; old met logs fold into one line.

### Meera Iyer, Associate (9, held)

Better: "Draft has 3 lines to fill: check the firm's view with Aditi" with the "Fill in 3 lines" chip and the full "Before you send"; the Mon 26 push says "3 lines to fill"; the headline counts meetings to log and steps to add; the step request lasts to Mon 9 Nov; Lattice keeps "you already write to them" to Mon 26; the Sable draft says its questions are Instinct's suggestions.

Still costs:
- Her Pipeline hero lowercases a fund: "Trellis Banking API: saffron Peak Capital wants to lead" from Sat 24 (172 of 200 runs); the Thu 5 Nov push too. Cause: `_lower` in `cli.py` lowercases the first letter of the signal.
- Week-old signals come back as pushes (Wed 28, Thu 29, Mon 9 Nov).
- Fri 30, 13 runs: "Their deadline 23 Oct has passed. term sheet from Monsoon Arc Ventures Decision by 23 Oct."
- Carried rows on her own deals say "shared by the deal team" with past "next ... by" dates.
- First run only: the pricing draft has no holder (Aditi appears from the next run).

For 9.5: names keep their capitals; carried signals keep their id and words; the holder on the first run too.

### Rohan Das, Analyst (9.5, up from 9)

Better: heads-ups keep the verdict on real windows ("Met our bar: two marketplaces live on payouts..."); rows keep who wrote and the company; the review push is never cut.

Still costs: Thu 29 07:25 push "Vaultline: the round is oversubscribed" (Tanvi wrote on 21 Oct; again Mon 9 Nov); a carried row with a past "next ... by"; a replay probe where, after "Sent it" on 19 pitch replies, Tue 10 and Wed 11 Nov draft 18 and 19 replies again (the Monday digest reads 120 days of mail and a pitch dropped after 14 days counts as new: `seen_at` resets; the engine has no guard on the pitch's own date).

For 10: no stale pushes; carried rows that are true; an answered pitch stays answered.

### Tara Menon, Head of Platform (9.5, up from 9)

Better: one nudge per note, one draft, one push; the partner's yes is her tap; after the team note is sent, "Asked the team on 29 Oct ... Aditi said yes on 29 Oct" with no stale "check with Aditi"; no "Draft coming" after a follow-up is sent; asks followed to the end ("Nudged Aditi on 29 Oct, still no reply: raise it with Aditi directly"); her Portfolio hero says where asks stand.

Still costs:
- The nudge draft does not follow its asks: after Nimbus went to the team (variant e), the hero says "2 founder asks wait on Aditi", but the nudge's "Before you send" and body still bump Nimbus. The same after Orbit's "Aditi said yes".
- Thu 29 06:28, the run that writes the nudge: Today says "Nudge Aditi" beside "Draft ready"; Portfolio says "Nudge ready".
- Wed 4 Nov push (variant a): "Still open: Aditi: 2 asks, no reply since 22 Oct".

For 10: a waiting nudge is rewritten when one of its asks moves on; first-run rows say "Nudge ready"; repeat pushes keep "Nudge Aditi on ...".

### Vikram Nair, CFO and IR (9, held)

Better: the fee-offset hero says what is missing; the Ledger & Lane push keeps the firm's name; the letter row says "Draft ready: fill in 5 lines, check the figures, then send it"; the chase is followed ("chased Peter on 22 Oct" from Fri 23; a shorter second note Thu 29); "Aditi Rao owes you" from Tue 27; Ferro's revenue miss said once in the letter.

Still costs:
- From day 18 the chase is forgotten: Mon 9 Nov hero "Called on 05 Oct, 35 days ago; no touch in 113 days. Draft ready", over "No reply since you wrote on 22 Oct: a second, shorter note". Cause: Home prunes a sent draft 14 days after "Sent it", and nothing else remembers the chase (asks got a `notes` record this round; capital calls did not). Every weekday Mon 9 to Fri 13 Nov the morning asks for the first chase again; with a Gmail tool, a new Gmail draft to an LP each morning. With the second note also sent, Mon 9 Nov drafts the first note again labelled "Second note ready": a third note to an LP.
- Thu 29 06:20 hero: "...The morning brief drafts a second note. Second note ready".
- Fri 30: "chased again Peter on 29 Oct".
- Aditi's paragraph leaves his Today from Tue 3 Nov while his letter still has 5 lines to fill.

For 9.5: a sent chase remembered for the life of the call (never a first note again, never a third); the run that writes a note says so plainly; a colleague's late work for him stays until done.

### Solo GP (9, held)

Better: the Sat 24 hero keeps Gravity and the rival; Kestrel's ask says "weigh the hires against the burn before sourcing"; the chase is followed from Fri 23 with a second note Thu 29; at most ten drafts go to Gmail a morning, pitch replies last.

Still costs: Mon 9 Nov "no touch in 113 days. Draft ready" and the first $60K chase drafted again; Thu 29 "The morning brief drafts a second note. Second note ready"; Mon 9 Nov push "Gravity Payouts: two other funds with offers, their deadline passed 31 Oct"; Thursday still writes 25 drafts into Home (grouped well).

For 9.5: money remembered for the life of the call; no pushes of old or passed news.

## Top five changes

1. **Remember what was sent for as long as what it tracks is open** (Vikram and the solo GP most; also Rohan and Aditi). Give capital calls the record asks got this round (`notes`): who was chased, when, which note; never a first chase after one was sent, never a third. Do the same for a promise's sent draft and a pitch reply, so a draft pruned at 14 days never comes back. Judge a pitch's age by its email date, not by when Home first saw it. Run the money and ask tests to Fri 13 Nov.
2. **Carried signals keep their identity and their words** (Kabir, Meera, Rohan, Aditi, the solo GP). Keep the same item id when the founder's email leaves the 7-day read; keep the founder's dated quote from Home; never "shared by the deal team" on the user's own deal; drop a past "next ... by" date or say "was due"; fix the "term sheet from Bluepeak Partners Decision by 05 Nov." fragment.
3. **Late work stays until done when it matters** (Aditi, Vikram). A promise with a rival, or one a colleague waits on, keeps its place past 7 days, or joins one line ("3 promises more than a week late"); the colleague who waits sees it as long.
4. **Drafts follow what changed** (Tara, Vikram, Meera). Rewrite or narrow a waiting nudge when one of its asks moves on. The run that writes a draft says so on its row ("Nudge ready", "Second note ready", never with "The morning brief drafts a second note"), and the holder on the first run.
5. **Words true for the reader** (Meera, Aditi, Tara). Never lowercase a name; in a partner's Home, founder asks treat her as the board partner ("Runway under 9 months: your call before anyone sources"); "chased Peter again on 29 Oct"; repeat nudge pushes keep "Nudge Aditi on ..."; fold met logs older than two working days into one row.

## Reaching 9.5 or 10: tests on the same replay

1. **Money is remembered for the life of the call.** Vikram, windowed, "Sent it" on the chase Thu 22 10:00, run to Fri 13 Nov, with and without the sent email in his mail: every Peregrine line from Fri 23 says "chased Peter on 22 Oct" (today Mon 9 Nov says "no touch in 113 days"); no morning after Thu 22 drafts `dr_l_cbd6326c5a` again (today 5 mornings, Mon 9 to Fri 13 Nov); Thu 29 reads "chased Peter on 22 Oct, no reply in 5 working days. Second note ready: check the amount, then send it" without "The morning brief drafts a second note". Second note also sent Thu 29 10:00: Fri 30 reads "chased Peter again on 29 Oct", and no later morning drafts any chase. The same for the solo GP's $60K.
2. **Old news is not pushed as news.** All seven, windowed to Mon 9 Nov: no push keyed `item:` names a signal Home first showed more than two days earlier (today 9: Kabir Thu 29 07:28 and Mon 9 Nov 07:28; Meera Wed 28 07:29, Thu 29 07:29 and Mon 9 Nov 07:29; Rohan Thu 29 07:25 and Mon 9 Nov 07:25; Aditi and the solo GP Mon 9 Nov 07:24).
3. **Carried signals keep true words.** Aditi Thu 29 06:24 hero keeps Arjun's dated words and "decide by 31 Oct", without "partner meeting Monday by 26 Oct" or "shared by the deal team"; Aditi Tue 3 Nov 07:24 hero is a whole sentence; Kabir Thu 29 06:28, Meera Wed 28 06:29 and Rohan Thu 29 06:25: no "shared by the deal team" on their own deals and no "next: ... by" a past date; Meera Fri 30 07:29: no "term sheet from Monsoon Arc Ventures Decision by 23 Oct."
4. **Late work stays until done.** Aditi to Mon 9 Nov: "Write the portfolio highlights paragraph" on Today every morning until Done (today gone from Tue 3 Nov); Vikram: "Aditi Rao owes you: write the portfolio highlights paragraph" every morning; Aditi Thu 29 and Fri 30 06:24: the Arjun intro on Today with "Two other funds with offers"; Aditi Fri 23 09:24 and 11:24: the Arjun row keeps the rival.
5. **A nudge follows its asks.** Tara, "Ask the team instead" on Nimbus Thu 29 10:00, note sent 15:00: from Fri 30 06:28 the nudge's "Before you send" and body name Kestrel Pay and Orbit Treasury only; the same after "Aditi said yes: ask the team" on Orbit (Nimbus and Kestrel only); Thu 29 06:28 the Today row ends "Nudge ready"; Wed 4 Nov 06:28 push reads "Still open: Nudge Aditi on Orbit and Kestrel: no reply since 22 Oct. Note ready".
6. **Names and first runs.** Meera's Pipeline hero from Sat 24 09:29 reads "Saffron Peak Capital"; Meera Thu 22 06:29 (setup) names the holder; Kabir Mon 26 06:28 folded line names the deal ("Cobalt AA: next step was due 15 Oct").
7. **A partner is treated as the board partner.** Aditi's Portfolio, Thu 22 07:00: the Orbit and Kestrel asks say the call is hers.
8. **Answered stays answered.** Rohan, "Sent it" on all 19 pitch replies Thu 22 10:00, windowed to Wed 11 Nov: no morning drafts a reply to those founders (today 18 on Tue 10 Nov, 19 on Wed 11 Nov). Aditi, "Sent it" on the markup draft Fri 23 10:00 and no Done: no new markup draft after the prune (today one every morning Mon 9 to Fri 13 Nov, in a replay where the sent email is not in her mail).
9. **Met logs do not sit for a week** (a suggestion). After two working days the unlogged meetings fold into one row ("Log 3 meetings from 22 Oct") with the forms inside, and the headline counts it once.
