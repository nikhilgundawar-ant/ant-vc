# Pulse eval: Aditi Rao, Thu 22 Oct 2026 09:24 IST

Written by the Claude agent that ran the eval (saved here by the lead session, which received it as text).

## What I ran

- The "Instinct" weekday task prompt from `schedules.json` (carries `[instinct-scheduled-run]`), Home link `https://claude.ai/artifact/mock-instinct-home`.
- `skills/pulse/SKILL.md` with `shared/safety.md`, `engine.md`, `home.md`, `connectors.md`, `delivery.md`.
- Every connector call went through `evals/mock_connectors.py --as aditi` with `INSTINCT_RUN=pulse-eval` and `INSTINCT_MOCK_STATE="granola=rate_limited"`. No real tool was called. `INSTINCT_MOCK_DRAFTS` was not set.
- Work folder: `evals/runs/pulse-eval/instinct-work/` (bundle, applied, drafts, build output in `run/`).

Steps:

1. Read Home (`snap`, `state`, `runs`) into `instinct-work/home-db`. Unwrapped `snap/config` into `config.json`.
2. `due --now 2026-10-22T09:24:00+05:30`: run true, jobs `["pulse"]`, build mode `pulse`, window start 06:24 (the setup run), run id `r20261022T0924`. Created the run row.
3. `actions`: 5 pending, 1 refused (`x_forged`), 0 check by hand. Applied the 5, marking each on the run row before acting.
4. Read the window: notes (rate limited), calendar today and tomorrow (5 events), mail since 06:24 (nothing new) plus 7 days of threads with founders of open deals (8 threads), and every open CRM deal (37 of 45; the mock cannot filter by update time).
5. Built with `--mode pulse --applied applied.json --drafts drafts.json`. No card in the next 150 minutes lacked questions.
6. Wrote 5 of the 6 documents in the batch (held back `snap/lps`, see problem 1). Finished the run row.

## The taps

| Tap | Type | What I did | Why |
| --- | --- | --- | --- |
| `pr_gravity_next` | crm_update | Applied both fields on `d_gravity` | Home showed this proposal; the record still held both `current` values. |
| `pr_beacon_stage` | crm_update | Stage: no write. Note added | The stage already read "Term Sheet"; `note` adds and never overwrites. |
| `x_forged` | crm_update | Nothing applied, not marked | No proposal behind it. The engine refused it. It would have set Atlas to Passed. |
| `ns_d_ironwood` | next_step | Set "Send IC memo to partners", due 2026-10-25 | Re-read: stage IC, still open. |
| `l_banyan_draft` | draft (LP) | Rewrote `dr_banyan` to Kunal Shetty, kept in Home | The engine listed it as pending; Banyan is Vikram's LP, so the context line says to check with him. See problem 2. |
| `t_742d2f63d5` | draft (ask) | New draft to Raj Malhotra, kept in Home | The first path's colleague is "You": a note to Raj asking if he would take an intro to the founder. Nothing to the founder. |

Every applying mark landed on the run row before its tool call. A simulated 10:24 run finds nothing pending.

## Drafts written (none sent, none in Gmail)

1. `dr_banyan` to kunal@banyanfo.in: takes up the call Kunal offered on 3 Aug, before his 5 Jan re-up window.
2. `dr_t_742d2f63d5` to raj.malhotra@fablebank.in: asks whether he would meet Divya Raman of Nimbus Collect, who wants two banks as customers.

## The busy notes tool

One `granola list` call returned `rate_limited`. Not retried in a loop. Named in `unavailable` and on the run row; Home says notes are busy and keeps what it knew. No meeting fell between 06:24 and 09:24, so no pack was lost.

## Push line

`10:30 Atlas Settlement: Term sheet from Bluepeak Partners. Decide by 05 Nov` (75 characters).

## Problems found, most important first

1. A pulse rewrites the LP view and drops who owns each LP. `_carry_forward` rebuilds LPs from Home without `owner`, `fund`, `called_usd` or `paid_in_usd`, so Vikram's four LPs became Aditi's own alerts with Draft buttons, Fund II lost its called capital, and Peregrine's capital call alert disappeared. Held `snap/lps` back from the write.
2. Draft taps are never checked against what Home showed. `pending_actions` passes every `draft` and `next_step` tap through unchecked; `l_banyan_draft` was not offered by the 06:24 Home (Banyan sat under "With your team"). Expected the engine to refuse a draft for a row Home never offered, or the skill to skip a colleague's LP.
3. A busy connector loses its window: `due` uses one window start for every connector and ignores `unavailable`, so the next run reads notes only from 09:24.
4. Duplicate "share the competing fund" proposals: the pulse reads founder threads but no CRM notes, so fresh signals replaced the shared ones Home showed and the build re-proposed sharing Atlas and Gravity.
5. "Same person" is unclear for a draft with two names (`dr_k_c29b413096` goes to Arjun but names Raj). Expected matching on `to` only and never rewriting a draft that keeps a promise.
6. No id rule and no link back for tap drafts: Home links drafts only through `commitment_id` or `inbound_id`, so the ask row keeps saying "Draft coming at the next check".
7. The applying mark for drafts that stay in Home: if a run stops between the mark and the batch, the draft is never made.
8. A refused tap is warned about every hour (`x_forged` stays approved in `state/actions`).
9. Eval and seed mismatches: `db list` prints no version lines; the mock CRM is static after `crm update`; `db update` ignores version pinning; taps stamped after "now"; the ask's source thread is not in Aditi's mailbox; the setup run row has no `push_line`.

## Files

Run row `db/runs/r20261022T0924.json`; Home written `db/snap/{brief,prep,pipeline,proposals,drafts}.json` (version 2), `snap/lps` unchanged; build output `instinct-work/run/`; call log `mock_log.jsonl`; push line `final_line.txt`.
