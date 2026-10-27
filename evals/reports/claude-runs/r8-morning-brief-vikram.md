<!-- Claude-run eval, round eight (0.7.0). Written by a Claude agent running the pulse skill against the mock connectors; saved by the main session. -->

# morning-brief-vikram: Vikram's scheduled run, Thu 22 Oct 2026, 06:20 IST

The run completed. Both owed entries were drafted and are stored in Home with their ids kept. The final line is the engine's push line. I did not write `report.md`: the harness forbids report files, so the whole report is here.

## 1. What I ran, in order

1. **Read the rules and skills.** eval-mode.md, then pulse, safety, engine, home and connectors. Then morning-brief and lp-watch, plus post-meeting, inbound-triage, portfolio-watch, meeting-prep and the templates.
2. **Step 0, guard canary: skipped.** Eval mode loads no guard.
3. **Engine check.** `instinct.py check` gave ok. The engine ran from the repo with `-I -S`, as eval-mode says.
4. **Read Home.** `db list` for snap, state and runs into `work/home-db`. I copied the snap and state lines into `versions.txt` and ran `cp snap/config.json config.json`.
   - Level: finance. LP watch: full. Triage: off. Pipeline: off.
5. **`due --now 2026-10-22T06:20:00+05:30`.**
   - Jobs: `morning_brief` and `pulse`. Mode: daily.
   - Window start: 21 Oct 06:20 for every connector. Run id: `r20261022T0620`.
6. **Run row.** `db set runs/r20261022T0620` with started and jobs. It came back at version 1.
7. **`actions`.** Nothing pending, refused or to check, so no `applied.json`.
8. **Reads, using the morning-brief windows.**
   - `status`: all connected. Gmail has no create-draft tool.
   - Gmail: `gmail search --after 2026-10-15` found 3 threads, and I read each one.
   - Calendar: 22 Sep to 5 Nov, 10 events. Today has 09:00 Tom Becker and 15:30 Helen Park. Tomorrow is empty.
   - Granola: no notes since the window start.
   - CRM: deals, companies, people, notes and passes.
   - Carta: `carta lps`, 15 LPs.
   - I wrote `bundle.json` from these reads: 37 open deals, 90 companies, 100 people, `transcripts: []`, `unavailable: {}`.
   - There were no new notes, pitches or founder updates, so no extracted, inbound, kpis, asks or packs files.
9. **Bundle shortcut, to compare only.** It went to `compare/bundle-shortcut.json`; see section 6.
10. **Build.** `build --mode daily --run-id r20261022T0620 --started ... --jobs morning_brief,pulse`.
    - 8 items and 208 words (budget 250).
    - 2 owed entries. Push send: true.
11. **Prep questions.** Three each for the two cards today, then the `questions` command.
12. **Sources for the drafts.**
    - Transcripts tr09, tr10, tr18 and tr22.
    - Many Drive searches. Vikram's Drive holds only 5 data-room files, and no LPA.
    - Wider mail: the Northgate threads and all 12 September founder updates.
    - `crm record` for Cardinal Risk and Ledgerline.
13. **Drafts.** I wrote `owed-drafts.json` and ran `drafts`. Both were written and none refused.
14. **Batch write.** `db batch` wrote pipeline v2, lps v2, prep v2, brief v2 and drafts v1 (new).
15. **Finish the run row.** `db update runs/... --if-version 1` took it to v2.
16. **Final line** (section 4).

The mock log shows no send, reply, forward or create call.

## 2. Every entry in run/owed.json

**`dr_k_c1aa612254`: promise, to helen.park@northgate.edu.example (Helen Park)**
- `commitment_id` k_c1aa612254 is kept.
- Subject: "Quillwater Fund II: management fee offset on monitoring fees".
- First two sentences: "I'm sorry this has taken so long. On our 2 Sep call you said your committee had asked about the management fee offset on monitoring fees, and I promised you an answer by 9 Sep."
- The answer itself is a bracketed gap: "[Add the answer: what the Fund II LPA says on offsetting monitoring fees against the management fee, quoting the clause and its page.]"
- The email closes with "Happy to walk through it on our call today."
- Sources:
  - Granola tr09: Helen's question and Vikram's promise.
  - Calendar `ev_northgate_today`: today's call.
  - Home commitment: 43 days late.
- No LPA or fee clause exists in his Drive or mail, so the gap is real.
- Self-check: draft present, ids kept.

**`dr_k_c19e1700ea`: letter, to aditi@quillwater.vc (Aditi Rao)**
- `commitment_id` k_c19e1700ea is kept.
- First two sentences: "Here is the Q3 LP letter draft I promised on our 14 Oct call. Every figure is from Carta, the founders' September updates or the CRM, with its source beside it."
- Sources:
  - The entry's `inputs`. I checked every figure against the 12 founder updates, and all matched.
  - Granola tr10: his promise, and Aditi's promise to write the highlights paragraph by the 26th.
  - Granola tr22: the NAV pack is due 25 Oct.
  - CRM: the two deals that moved to Portfolio in Q3, and the deals list.
  - Home `snap/asks`.

## 3. The letter

Stored body, exactly as saved:

```
Hi Aditi,

Here is the Q3 LP letter draft I promised on our 14 Oct call. Every figure is from Carta, the founders' September updates or the CRM, with its source beside it. Companies ahead of plan with no flags are under highlights, and the five flagged companies are on a watch list, so you can decide how much LPs see. The bracketed gaps are yours: your commentary, and the highlights paragraph you are writing by the 26th.

Vikram

---

# Quillwater Ventures: Q3 2026 letter to our LPs

[In your words: what this quarter meant]

## Fund summary

- Fund II: $80M committed by 15 LPs (Carta LP list).
- Called to date: $36M, 45% of commitments. Paid in: $35.85M. Unfunded: $44M. All as of 22 Oct (Carta LP list).
- Portfolio: 12 companies, all of which sent a September update (each linked below).
- [The quarter's key events, in your words]

## Portfolio highlights

[Aditi: your highlights paragraph, as agreed on 14 Oct]

Ahead of their September revenue plan, with no flags:

- Quanta Rails: $290K against a plan of $280K ([update](https://mail.google.com/mail/u/0/#all/upd_quanta)).
- Cardinal Risk: $126K against a plan of $120K ([update](https://mail.google.com/mail/u/0/#all/upd_cardinal)).
- Brightvault: $97K against a plan of $95K ([update](https://mail.google.com/mail/u/0/#all/upd_brightvault)).
- Mintrail: $79K against a plan of $77K ([update](https://mail.google.com/mail/u/0/#all/upd_mintrail)).
- Ledgerline: $72K against a plan of $70K ([update](https://mail.google.com/mail/u/0/#all/upd_ledgerline)).
- Nimbus Collect: $48K against a plan of $46K ([update](https://mail.google.com/mail/u/0/#all/upd_nimbus)).
- Harbor Insure Stack: $28K against a plan of $27K ([update](https://mail.google.com/mail/u/0/#all/upd_harbor)).

On our watch list:

- Orbit Treasury: runway under 9 months, with $1.6M cash at $200K monthly burn. Revenue $198K against a plan of $195K ([update](https://mail.google.com/mail/u/0/#all/upd_orbit)).
- Ferro Credit Cloud: revenue −22.6% against plan, $410K against a plan of $530K ([update](https://mail.google.com/mail/u/0/#all/upd_ferro)).
- Kestrel Pay: burn up 43.3% in a month, to $215K. Revenue $158K against a plan of $160K ([update](https://mail.google.com/mail/u/0/#all/upd_kestrel)).
- Tallyfin: key person leaving, as the CTO, Vineet Rao, leaves at the end of October. Revenue $108K against a plan of $105K ([update](https://mail.google.com/mail/u/0/#all/upd_tallyfin)).
- Saffire KYC: churn up 3.7pp. Revenue on plan at $126K ([update](https://mail.google.com/mail/u/0/#all/upd_saffire)).

## New investments

- The CRM moved two deals to Portfolio this quarter: Cardinal Risk on 23 Aug (Seed, our check $1.8M, [CRM](https://quillwater.affinity.co/opportunities/d_cardinal_d)) and Ledgerline on 12 Sep (Seed, our check $2.0M, [CRM](https://quillwater.affinity.co/opportunities/d_ledgerline_d)).
- [Confirm both closed in Q3, and add a line on why we backed each]

## Follow-ons and markdowns

[None recorded in the CRM or Carta. Add any follow-ons, and the marks from Ledger & Lane's Q3 NAV pack, which Sana promised for 25 Oct ([meeting notes](https://notes.granola.ai/d/tr22))]

## Exits

[None recorded in the CRM. Add any exits or secondary sales]

## Pipeline and market

- 37 open deals in the CRM as of 22 Oct: 3 at IC, 2 at term sheet and 2 closing (CRM deals list).
- [In your words: the market this quarter]

## Asks

- Nimbus Collect would like introductions to two banks as customers (Divya Raman, 13 Oct, from Instinct's founder asks: [her email](https://mail.google.com/mail/u/0/#all/th0343)).
- [Your call: Orbit Treasury and Kestrel Pay also asked for introductions to senior backend engineers, but both are on the watch list. Keep them out until you decide]
```

**Would Home show "Draft ready" on the letter row? Yes.**
- `snap/drafts` (v1) holds `dr_k_c19e1700ea` with `commitment_id` k_c19e1700ea.
- The brief row "Q3 LP letter draft" (`t_9b6b6a56c7`) has `draft: "dr_k_c19e1700ea"`.
- The page's `draftFor` finds it. It has no `inbound_id` or `question_id`, so the label is "Draft ready".
- One limit: the body is 3,729 characters. The page gives no "Open in Gmail" link over 1,800 (`gmailHref` in `home/index.html`), so Vikram gets Copy only.

**Numbers check.** I traced all 57 numbers:
- 47 come from `inputs`.
- The rest come from named sources: the CRM (checks, dates, deal counts), tr10 and tr22 (dates), and `snap/asks` (13 Oct).
- All 7 sections are present by the engine's `letter_check`. I had to call it from outside the skill, because no command exposes it.

**Highlights: 7 companies.** Quanta Rails, Cardinal Risk, Brightvault, Mintrail, Ledgerline, Nimbus Collect and Harbor Insure Stack. Each beat its September revenue plan and has no flag.

**Watch list: 5 companies.** Orbit Treasury, Ferro Credit Cloud, Kestrel Pay, Tallyfin and Saffire KYC. Each carries a flag in `inputs.flags`. Orbit and Tallyfin beat plan and Saffire is on plan, but a flag outweighs a revenue beat in a letter LPs read.

The highlights paragraph itself is left to Aditi, because tr10 says she will write it.

## 4. The final line

`Answer the fee offset question: Helen (Northgate Endowment), 43 days late`

`report.push.send` was true, so the run ends with that line and nothing after it.

**Today's first rows are Vikram's own work:**
- Hero: his overdue fee-offset answer to Helen, now "Draft ready".
- Next up 1: Peregrine Trust still owes $150K on a capital call (his LP).
- Next up 2: his overdue runway model for Neel Bhatt.
- Next up 3: the Orbit Treasury runway flag, which is not his work.
- Next up 4: his Q3 LP letter, now "Draft ready".
- Signals: three portfolio flags.
- Meetings: 09:00 Tom Becker and 15:30 Helen Park.

## 5. Where the skill text was unclear, contradictory or impossible (most important first)

1. **The letter's destination and number sources conflict.**
   - `skills/lp-watch/SKILL.md` step 4 says "Pull numbers only from Carta, the KPI history in `snap/portfolio` and the CRM" and "then create it as a document the user can edit".
   - `skills/morning-brief/SKILL.md` step 6.3 says "with every number from those inputs ... it goes as a draft to the person it was promised to".
   - The guard blocks "writes to other apps", so a scheduled run cannot create a document.
   - I followed 6.3, and used CRM figures only with the source named.
2. **The letter check cannot be run.** lp-watch step 4 says "Check that no section is missing (the engine's `letter_check`)". No such command exists. `letter_check` is an internal function in `engine/instinct/lp.py`, and the guard only allows `instinct.py <command>`.
3. **The length rule does not fit the letter.** morning-brief 6.1 says "in two to five plain sentences in the user's voice". A seven-section letter cannot meet that. I wrote a 4-sentence cover note above the letter.
4. **The Gmail promise fails for long drafts.** morning-brief 6.8 says "Home's 'Open in Gmail' opens a new message already filled in, so the user still sends it in one tap". This is false for any body over 1,800 characters, which includes every LP letter.
5. **Nothing defines what goes in "Portfolio highlights".** `templates/lp-letter.md` names the section but gives no rule, and does not say where flagged companies go. The skill also cannot know that Aditi owns the highlights paragraph (tr10).
6. **The fund figures cannot link to Carta.** `templates/lp-letter.md` says "Every number links to Carta, the KPI history or the CRM". But `inputs.funds` has no `source_url`.
   - Flags carry only a headline, with no detail figures.
   - The inputs hold nothing for New investments, Follow-ons, Exits or Pipeline.
7. **The subject hard-codes "Q3".** morning-brief 6.3 says: subject "Q3 LP letter: draft for your review". It will be wrong next quarter.
8. **It is unclear whether the pulse runs morning-brief step 7.** The pulse job table names only steps 5 and 6. Step 7 says "If the hero already covers a point, drop the duplicate line", but there is no way to do that without editing engine output.
9. **LP alert drafts are never made by a scheduled run.** lp-watch step 2 says "For each alert, draft a short, specific note". But the pulse runs only "LP watch reads" on Mondays, and `owed.json` has no LP-alert kind. Peregrine's urgent call gets no draft unless Vikram taps Draft.
10. **The bundle is hard to write by hand, and its company scope is unclear.**
    - Under the guard, `bundle.json` must be written by hand: 100 people, 90 companies and 37 deals here.
    - The connectors.md morning-brief row says "Open deals and their companies, portfolio companies ... CRM people (all of them)". It does not say whether to include the LP, fund-admin and bank companies those people belong to. I included all of them.
11. **Smaller points.**
    - An empty `transcripts: []` meaning "read, none new" is implied by the docs, not stated.
    - For an LP, "The subject names the company" is ambiguous. I used the fund.
    - lp-watch's "10 days before quarter end" does not fit a Q3 letter drafted on 22 Oct.
    - The `drafts` help text says "saved to Gmail", but the command also stores drafts that stay in Home.

## 6. What went wrong or looked wrong

1. **The `bundle` shortcut ignores the run's windows and time.**
   - It returned 65 threads back to 24 Jun, 27 events and 4 old transcripts.
   - It included all 45 deals (Portfolio and Passed too) and all KPI rows.
   - It set now to 07:00, not 06:20.
   - Building from it would re-feed old transcripts. I built from my own reads instead.
2. **Gaps in the mock.**
   - `status` lists Slack, Notion and PitchBook as connected, but each returns "unknown command".
   - Gmail `--query` matches subjects only: "Helen", "Northgate" and "fee offset" found nothing. I had to list all mail to find Helen's threads.
3. **A source link Vikram cannot open.** The Nimbus ask in his Home cites thread th0343, which is not in his mailbox (`not_found`).
4. **A duplicate line in the brief.** The 15:30 meeting note "You owe: answer the fee offset question (overdue)" repeats the hero. I left it rather than hand-edit engine output.
5. **The ranking looks off for Finance and IR.**
   - Banyan (his LP, re-up window opens 5 Jan, 80 days without a touch) and Tidewater (120 days) are not on Today.
   - Meanwhile three portfolio flags he does not own fill Signals.
   - Orbit's runway flag sits above his own letter promise.
   - The level reminder lists "LPs in their re-up window" first. I did not reorder anything.
6. **Stale or imprecise engine output.**
   - After the draft exists, the letter row still reads "Instinct drafts it from the KPI history and the LP list".
   - In `run.json`, `finished` equals `started` (06:20). The engine stamps the bundle's time, not the real finish time.
7. **Two judgement calls left for Aditi.**
   - The letter shows paid in $35.85M against $36M called. That indirectly reveals an unpaid call to every LP.
   - The fee-offset answer is still a gap. No fund documents exist in Vikram's tools.

## Files (all under /home/claude/instinct-vc/evals/runs/morning-brief-vikram/)

- `work/bundle.json`
- `work/questions.json`
- `work/owed-drafts.json`
- `work/run/owed.json`
- `work/run/brief.md`
- `work/run/report.json`
- `work/run/home/batch.json`
- `work/run/home/run.json`
- `compare/bundle-shortcut.json`
- `tools/make_bundle.py` and `tools/check_letter.py` (helpers, not the skill)
- `mock_log.jsonl` (written by the mock)
