<!-- Claude-run eval, round ten. Written by a Claude agent running the pulse skill against the mock connectors on a clean clone at a023dd2; saved by the main session (the agent could not write files). -->

# Eval report: nudge-tara (round 10)

- Plugin version: 0.7.3 (pulse and morning-brief SKILL.md metadata)
- Commit: `a023dd2 Round ten: one nudge per note, drafts say what they need, money and asks followed after sending; version 0.7.3`
- `git status --short`: clean at the start and at the end. Only ignored files exist (`__pycache__/`, `evals/runs/`). No tracked file edited.
- Member: Tara Menon (`tara`), Head of Platform, level `platform`
- Run: the scheduled "Instinct" weekday run on Thu 29 Oct 2026 at 06:28 Asia/Kolkata, run id `r20261029T0628`
- Skill: `skills/pulse/SKILL.md`, jobs `morning_brief` and `pulse`, so morning-brief steps 6 and 7 apply too
- Home link from the scheduled prompt: `https://claude.ai/artifact/mock-instinct-home`

Eval-mode adjustments (all allowed by the brief):
- Skipped pulse step 0 (no guard loads in eval mode).
- Ran the engine from the clone instead of copying it. Work folder: `evals/runs/nudge-tara/work/`.
- Passed `--now 2026-10-29T06:28:00+05:30` to `due`, and set the bundle's `now` to the run time.
- Every Home read and write used the mock `db` commands; `db list --collection runs` stands in for the ordered `query`.
- Every connector read went through `mock_connectors.py --as tara` with `INSTINCT_RUN=nudge-tara`. No real app tool. No answer files opened.
- Built `bundle.json` by hand from the window reads (not the `bundle` shortcut, which returns the whole mailbox).

## 1. What I ran, in order

1. Setup: clone, checkout `a023dd2`, clean tree.
2. Seed: `seed_eval.py nudge tara` gave 14 snapshots, 76 runs (last 60 kept) and 3 drafts.
3. Read the pulse and morning-brief skills, `shared/home.md`, `engine.md`, `connectors.md`, `safety.md`, `delivery.md`, post-meeting steps 3 to 7, inbound-triage steps 2 and 4, portfolio-watch steps 2 and 4, and every template.
4. Connector status: all connected; Gmail has no `create_draft`, so drafts stay in Home (`in_gmail` false).
5. Read Home: 14 snap docs, 2 state docs, 60 runs; `versions.txt` from the 16 result lines; `config.json` copied. One note, `dr_t_1d7b287123`, went to Aditi with three asks (Kestrel Pay and Orbit Treasury `board`, Nimbus Collect `colleague`), marked sent 22 Oct 10:00; Nimbus has `made_on` 26 Oct; `state/actions` empty.
6. `due --now 2026-10-29T06:28`: run true, jobs `morning_brief, pulse`, build mode daily, window 28 Oct 19:28, run id `r20261029T0628`.
7. Run row created (version 1).
8. `actions`: empty.
9. Morning-brief windows: no mail since 22 Oct (Tara's mail ends 21 Oct); a search for the sent note or a reply from Aditi found neither; read the asks' sources and six of Tara's threads for voice; 4 calendar events, none today or tomorrow; no notes; CRM 45 deals (37 open), 90 companies, 100 people, 20 passes.
10. Bundle by hand: `now` 06:28, no threads or transcripts, 4 events, 37 open deals, 49 companies, 53 people (`people_partial` and `companies_partial` true), 5 notes, 20 passes, no `lps`.
11. Build (daily): 8 items, 184 words; hero "Intro two CFO candidates", 8 days late; push "Nudge Aditi on Orbit Treasury and Kestrel Pay: no reply since 22 Oct"; `owed.json` with 1 entry.
12. No prep cards (no meetings today or tomorrow).
13. Drafted the nudge into `owed-drafts.json`; `drafts` wrote `dr_t_1d7b287123_nudge`, refused nothing.
14. Brief check: hero states a fact, every line sourced, 184 of 350 words, no warnings.
15. `db batch` (pipeline, portfolio, directory, asks, drafts, brief to version 2), run row finished (version 2).
16. Final line: `Nudge Aditi on Orbit Treasury and Kestrel Pay: no reply since 22 Oct`.

39 mock calls; none tried to send, save a Gmail draft or write to the CRM.

## 2. The pending taps

None. The 22 Oct note came from the morning brief, not a tap; its sent mark is in `state/items`.

## 3. The owed entry and its draft

- `dr_t_1d7b287123_nudge`: kind `ask_nudge`, `note_kind` nudge, `nudge_of` board, `sent_on` 2026-10-22, `re` "Founder asks: Kestrel Pay, Orbit Treasury, Nimbus Collect", items Kestrel Pay (Neel Bhatt) and Orbit Treasury (Vikram Rao), `action_ids` both nudge taps. Nimbus left out (intro made 26 Oct).
- Draft (stays in Home), to aditi@quillwater.vc, subject "Re: Founder asks: Kestrel Pay, Orbit Treasury, Nimbus Collect":

```
Hi Aditi,

Thanks for introducing Divya to Raj at Fable Bank on 26 Oct. On my note of 22 Oct, two asks still need your call:

1. Kestrel Pay: should we help Neel Bhatt hire two senior backend engineers now, given burn is up to $215K a month?
2. Orbit Treasury: should we help Vikram Rao hire two senior backend engineers now, given runway under 9 months?

A quick yes or no on each is plenty.

Tara
```

- Context: "Aditi made the Nimbus intro on 26 Oct but has not answered on Kestrel Pay or Orbit Treasury since your 22 Oct note: one short nudge. Send it as a reply in that thread so she has the note in view".

## 4. Next-run check

- Push: "Nudge Aditi on Orbit Treasury and Kestrel Pay: no reply since 22 Oct".
- Hero: "Intro two CFO candidates", 8 days late; its draft (written 23 Oct) still says "I will introduce you this week" (finding 5).
- Next up: the guest list (Draft ready); "2 founder asks wait on Aditi" with status "Nudge" and a "Draft ready" chip; Tallyfin key person; Rahul's CTO job description.
- The nudge row, opened: "Before you send" with the context, Open in Gmail (To, "Re:" subject and body filled in), Copy draft, See each ask, Snooze. No Sent it, no Done.
- Portfolio: hero "Founder asks · one note. 2 founder asks wait on Aditi... 1 more open" with Open draft; Orbit and Kestrel rows say "Nudge ready", each with Done, Open in Gmail, Copy draft and "Aditi said yes: ask the team".
- The 07:28 pulse: "Nothing new", nothing lost; Today and both heroes now say "Nudge ready".

## 5. Findings, worst first

1. **Home: Tara cannot mark the nudge, or the first note, as sent (high).** The engine learns a note went out only from `done_at` on the draft id; the page writes that only from "Sent it" in "Ready for you", which skips every draft shown on the hero or a row. Ask notes and nudges always show on rows, so there is no Sent it anywhere. The grouped row has no Done; on a Portfolio ask row, Done closes the ask itself. Fix: "Sent it" beside Open in Gmail wherever a draft shows; label the ask's closing tap "Close ask"; drive Sent it through the page in Home QA.
2. **"No reply" is claimed without reading mail (medium, latent).** Only working days are counted; a reply from Aditi by email would not stop the nudge. Fix: look in `threads` for a message from the note's `to` after it went; if found, say "Aditi replied on <date>" and list no nudge. Step 6.3 should say to search for a reply first.
3. **The morning push and the first hour of Today do not know the nudge is drafted (medium-low).** The push has no "Note ready"; Today says "Nudge" beside "Draft ready" until the next pulse. Fix: when `drafts` links a fresh nudge to a grouped row, switch the row and heroes to the ready form and rewrite the push line ("...: no reply since 22 Oct. Note ready").
4. **"The same thread" cannot be literal, and the entry does not name the note it follows (low).** Fix: add the note's draft id to the entry, keep the note's order, and have `context` say to send it as a reply when the draft stays in Home.
5. **Waiting drafts keep stale relative dates (low).** A draft from 23 Oct still says "this week" on 29 Oct. Fix: list a waiting draft for a rewrite when it says today, tomorrow or this week and was made on an earlier day or week.
6. **The grouped row describes the note wrongly (low).** "One note on 22 Oct for Orbit Treasury and Kestrel Pay": the note carried three asks. Fix: "Your 22 Oct note to Aditi: no answer yet on Orbit Treasury and Kestrel Pay (5 working days)".
7. **Working days counted by date (low).** The nudge comes on the morning of the fifth working day, before it ends. Fix: say so in `delivery.md`, or count from the note's time.
8. **Eval harness: the mock mailbox lacks mail the seeded Home depends on (low).** Aditi's 26 Oct intro and the 22 Oct note exist only in the replay's memory. Fix: serve the threads the replay injects.

## 6. Score: 7 out of 10 (as Tara)

The morning did its main job: one push named the right thing (two hiring asks with cash flags, five working days on the board partner), Nimbus was rightly left out, a short correct nudge sat one tap from Gmail, and Today was calm and accurate. Three things cost points: the push and the first hour of Today read as if she still has to write the nudge; once she sends it, Home gives her no way to say so, and the nearby Done would close her asks by mistake; and the hero's own draft still promises intros "this week" from a week ago.
