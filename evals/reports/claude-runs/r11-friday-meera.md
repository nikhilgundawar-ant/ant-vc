<!-- Claude-run eval, round eleven. Written by a Claude agent running the pulse skill against the mock connectors on a clean clone at be80587 (0.7.4), writing bundle.json by hand in one Write call; saved by the main session (the agent could not write files). -->

# Eval report: friday-meera (round 11)

- Plugin: instinct-vc 0.7.4 (`.claude-plugin/plugin.json`; the pulse and morning-brief skills are 0.7.4; engine `check` says 0.7.4)
- Commit: `be80587 Round eleven: Sent it wherever a draft shows, replies stop follow-ups, money kept while unpaid, taps that hold; version 0.7.4`
- `git status --short`: clean before (right after checkout) and clean after.
  - Everything I wrote is under the ignored `evals/runs/friday-meera/`.
  - Python wrote ignored bytecode caches. `engine/instinct/__pycache__/` and most of `evals/__pycache__/` came from the seeding step. My QA import added `evals/__pycache__/home_qa.cpython-313.pyc`.
  - I never wrote to `/home/claude/instinct-vc`. Its `BUILD_LOG.md` shows a change at 07:38 UTC, during this eval, from another process.
- Member: `meera` (Meera Iyer, Associate, Quillwater Ventures, Asia/Kolkata)
- Run: Fri 23 Oct 2026, 06:29 IST.
  - Run id `r20261023T0629`, jobs `morning_brief` and `pulse`, build mode `daily`.
  - Then the next pulse, `r20261023T0729` (job `pulse`, mode `pulse`).
- Skill: `skills/pulse/SKILL.md` steps 1 to 7, plus `skills/morning-brief/SKILL.md` steps 5 to 7 and `references/owed-kinds.md`, and the shared docs they name.
- Final line at 06:29: `Sable Fraud AI: term sheet from Monsoon Arc Ventures, decide today`
- Final line at 07:29: `Review ready: Trellis Banking API: Saffron Peak Capital wants to lead`

Eval-mode adjustments:

- **Guard:** skipped pulse step 0. No guard loads in eval mode.
- **Engine:** ran it from the clone, isolated (`python3 -I -S <clone>/engine/instinct.py`), from a work folder under the run folder. I did not copy it.
- **Run time:** passed `--now 2026-10-23T06:29:00+05:30` to `due`. I passed the run's start to `actions`, as the skill says.
- **Home reads and writes:** used the mock `db` commands for every one.
- **Home link:** took it from `artifact list`. The mock's `schedule list` is empty, so no task prompt carried it.
- **Drafts:** called `status` once. Gmail has no create-draft tool. So every draft stayed in Home (`in_gmail` false), and I made no `drafting` mark.
- **Applying marks:** the mock clock is fixed, so I stamped them 06:31, 06:32 and 06:33.
- **No user prompts:** no question to the user came up, and no connector card.
- **One probe outside the skill:** `slack search`, to see whether the mock has Slack. It does not.
- **Next-hour check only:**
  - I subclassed `evals/home_qa.QA` so its constructor never calls `demo.build`, which reads `evals/cases/`.
  - I passed `snap=`, `state=`, `runs=`, `when=` and `member=` myself.
  - A small script put the page's own state writes into the mock store, as the page's database would.
  - In the 07:29 pulse I copied the 14 founder threads from the 06:29 reads. I did not read each thread again. The 7-day search showed the same threads and dates, and no mail had arrived.

## 1. What I ran, in order

1. **Setup:** clone at `be80587`, clean.
   - `seed_eval.py friday meera` gave 14 snapshots, 14 runs, 6 drafts and 3 taps (`ns_d_rivulet_2026-10-22`, `ns_d_halo_2026-10-22`, `ns_d_sable_2026-10-22`).
   - I read eval-mode.md, the round-ten report, both skills, owed-kinds.md and the shared docs.
   - I opened no answer file.
2. **`status`:** all nine connectors are connected. The mock clock reads Fri 23 Oct 06:29. Gmail has no `create_draft`.
3. **Home link:** from `artifact list` (`mock-instinct-home`).
4. **`db list`** for snap, state and runs, into `work/home-db`:
   - 14 snap documents, all at version 1.
   - 3 approved `next_step` taps, stamped Thu 20:45. `state/items` is empty.
   - 14 run rows. The last is Thu 19:29, "Nothing new".
   - I wrote `versions.txt` (16 lines) and copied `config.json` (associate, 450 words, 12 items, triage `own`, LP watch off).
5. **Engine `check`:** ok.
6. **`due`:** jobs `morning_brief, pulse`, mode `daily`, every window from Thu 19:29, run id `r20261023T0629`. I created the run row (version 1).
7. **`actions`:** 3 pending, none refused, none to check by hand.
   - I re-read each deal with `crm record`. All three were open, and each step matched its payload.
   - I applied each tap after its own applying mark (row versions 2, 3 and 4), then read it back.
   - I wrote `applied.json`.
8. **Reads, by the Morning brief row:**
   - Gmail since 16 Oct: 19 threads, each read in full. The latest is Wed 21 Oct 20:00, so nothing arrived after the window start.
   - Calendar, 23 Sep to 6 Nov: 18 events. None on Friday or Saturday. The next is the Mon 26 Oct 10:00 partner meeting.
   - Granola since 22 Oct: nothing. Thursday's three meetings have no notes.
   - CRM: 45 deals (37 open), 90 companies, 100 people, 13 notes and 20 passes.
   - Drive searches for the drafts' sources: nothing.
9. **`bundle.json`:** Home's 37 open deals and the CRM's 37 are the same set. I wrote the bundle by hand in one Write call (65,922 bytes). It holds:
   - the 37 open deals and their 13 notes;
   - the 49 companies of open deals and the portfolio (`companies_partial`), and their 53 people (`people_partial`);
   - 20 passes, 19 threads, 18 events and `transcripts: []`.
10. **Extraction:** no notes, pitches or founder updates arrived since the window start, so there was nothing to extract.
11. **`build --mode daily --applied applied.json`:**
    - Hero: the Sable term sheet.
    - 12 items, 328 words (budget 450), no warnings.
    - Push: "Sable Fraud AI: term sheet from Monsoon Arc Ventures, decide today" (66 characters).
    - 3 owed entries, and one prep card (Monday's partner meeting).
12. **`questions`** for `ev_pm_next` (a Friday reaches Monday): written, none refused.
13. **Drafts:** I wrote `owed-drafts.json` (3 rewrites). `drafts` wrote 3, refused 0, and printed no `push_line`.
14. **Brief check (step 7), all passed:**
    - The hero states a fact.
    - Every line has a source.
    - Her overdue promises sit above what she waits on.
    - No line repeats another.
    - 328 of 450 words.
15. **`db batch`:** 7 documents (pipeline, people, proposals, directory, prep, drafts and brief), each now at version 2.
16. **Run row:** finished from `run/home/run.json` (version 5), with the three applying marks kept.

Totals:

- **Time:** about 13 minutes (07:36:50 to 07:49:44 UTC).
- **Connector calls:** 64, plus my one Slack probe.
  - 19 thread reads, 9 Drive searches, 6 CRM record reads and 3 CRM writes.
  - 4 run-row updates and 1 batch.
- **Nothing outgoing:** no send, reply, forward, draft-save or calendar call.

## 2. The pending taps

1. **`ns_d_rivulet_2026-10-22`:** met 22 Oct, stage "Second meeting", `clear_step`, no text.
   - **CRM before:** First Meeting since 17 Oct, step "Second meeting" due 24 Oct, last contact 19 Oct.
   - **One call:**
     - stage "Second Meeting" (the CRM's own option, as Sable shows);
     - stage-entered 22 Oct;
     - next step and due null;
     - last contact 22 Oct.
   - **Result:** applied. Home now asks "Rivulet Payments: met 22 Oct, add the next step".
2. **`ns_d_halo_2026-10-22`:** the same shape. The CRM had First Meeting since 10 Oct. The same five fields were written. Applied, and Home asks for Halo's step.
3. **`ns_d_sable_2026-10-22`:** "Diligence kickoff", due 24 Oct, stage null.
   - The step and its date were already in the CRM.
   - **One call:** last contact from 21 Oct to 22 Oct.
   - **Result:** `{"status": "applied", "already": ["next_step", "next_step_due"]}`.

About the stage-entered date:

- **Why I set it:** the Affinity record carries `stage_entered` as a plain field, and safety rule 7 allows that one extra field on a met log that moves a stage. Round ten made the same choice.
- **Still unclear:** the skill gives no way to know whether the field is writable (round-ten finding 7).
- **Why it matters:** writing it keeps colleagues' Pipelines honest. Left at 10 Oct, Halo would read 13 days in Second meeting.

After the build, Proposals shows all three as "applied", with Sable's two "already" fields.

## 3. The owed entries and their drafts

The engine listed the same three entries as round ten. All three stay in Home.

1. **`dr_i_0e2115836d`, `reslot`.** The Harborline Treasury reply (score 93, call) offered Fri 23 Oct 10:00 and 11:00, which is today. `avoid_slots` was empty.
   - **Time zone:** the entry carries no time-zone hint. The pitch says "based in Delaware, US and Bangalore, India". So I used step 6.2's overlap hours: 17:00 IST is 07:30 US Eastern.
   - **Slots:** Mon 26 Oct 17:00 and Tue 27 Oct 17:00 IST. Both are free and clear of other events.
   - **To:** Elena Fischer (elena@harborline.co).
   - **Subject:** "Re: Harborline Treasury".

   > Hi Elena,
   >
   > Thanks for sending Harborline Treasury our way. It fits what we back, and we would like to hear more. Would Mon 26 Oct at 17:00 IST (07:30 ET) or Tue 27 Oct at 17:00 IST (07:30 ET) work for a 30-minute call?
   >
   > Meera

   Context: "Inbound pitch, score 93: call. Slots from your calendar. The old times (Fri 23 Oct at 10:00 and 11:00) were too short notice, so these are two new free ones. Harborline is in Delaware and Bangalore, so both suit IST and US East: check them before you send"

2. **`dr_k_454489f888`, `refresh`.** "Share feedback after the partner meeting" to Omkar. It is 4 days late, and Aditi holds the firm's view.
   - **Why a refresh:** it was written before the 22 Oct "Rivulet Payments: follow-up", which has no notes.
   - **What I changed:** I kept the draft and its three bracketed lines. I added one greeting line that claims nothing about the meeting.
   - **To:** Omkar Patil (omkar@rivuletpay.com).
   - **Subject:** "Rivulet Payments: our feedback".

   > Hi Omkar,
   >
   > Good to see you on 22 Oct.
   >
   > As promised, here is the feedback after the partner meeting.
   >
   > [Where we landed, in one line]
   > [What we liked]
   > [What we would want to see next]
   >
   > Happy to talk it through.
   >
   > Could you also give data room access?
   >
   > Meera

   Context: "You promised this on 17 Oct, due 19 Oct. Instinct found no written feedback in your notes or Drive. Fill in the 3 lines before you send. Check the firm's view with Aditi, who sponsors the deal. It was written before your 22 Oct follow-up, which has no notes: check it still stands, or tap Done if it was settled in the room"

3. **`dr_k_48cf2d4ce7`, `refresh`.** "Send the reference questions" to Abhishek. It is 1 day late.
   - **Why a refresh:** it was written before the 22 Oct references meeting, which has no notes.
   - **To:** Abhishek Joshi (abhishek.joshi@sablefraud.ai).
   - **Subject:** "Sable Fraud AI: reference questions for your customers".

   > Hi Abhishek,
   >
   > Good to see you on 22 Oct.
   >
   > As promised, here are our reference questions so you can brief your customers:
   >
   > 1. How long did it take to go live with Sable?
   > 2. What change have you seen in false positives since launch?
   > 3. What would make you expand your use of Sable next year?
   >
   > Thanks for the fraud loss benchmarks you are sending over.
   >
   > Meera

   Context: "You promised this on 20 Oct, due 22 Oct. The three questions are Instinct's suggestions, not from your notes: check them before you send. It was written before your 22 Oct references meeting, which has no notes: check it still stands, or tap Done if it was settled in the room"

Rightly not owed:

- **Trellis pricing view:** a draft waits, and there was no meeting since.
- **NBFC list for Leena:** the draft was written after their meeting.
- **Copperleaf question:** a reply draft waits.
- **Halo's slot confirmation:** it looks done.
- **Lattice KYC:** she is already in touch.
- **Dhruv Data:** an ask for more, and associates draft replies only to calls.

Prep questions for Monday's partner meeting. They are Instinct's, built from the card's seeds:

1. "Sable Fraud AI: Monsoon Arc Ventures wanted our answer by Fri 23 Oct, before this meeting; did we give Abhishek one, and are we still in?"
2. "Gravity Payouts: two other funds have offers and Arjun decides by 31 Oct; what would make ours the offer he takes?"
3. "Atlas Settlement: Bluepeak Partners has a term sheet out and Ishaan decides by 05 Nov; do we move first, or step back?"

I worded the first so it is still true on Monday. The card's own seed asks "Do we move first, or step back?" about a 23 Oct deadline, three days before the meeting (finding 3).

## Writing bundle.json by hand

- **Size:** 65,922 bytes. Round ten's was 60,311 bytes. By part:
  - threads 10.8 KB, events 6.6 KB, companies 14.4 KB, people 11.8 KB;
  - deals 14.0 KB, notes 2.8 KB, passes 5.1 KB.
- **Time:** about 4 minutes for the one Write call (07:42:28 to 07:46:25 UTC), roughly 19,000 output tokens.
- **Errors:** 0. I checked it afterwards, field by field, against the saved tool results. That was an eval-side script: a scheduled run has no way to check it.
- **The 07:29 pulse bundle:** 9,327 bytes, with 0 errors.
  - It held 14 founder threads, 1 event and 3 changed deals with `crm.partial`.
  - Round ten's 07:29 bundle was 21,778 bytes.

What was hard:

- **All or nothing.** One slip in 66 KB means writing it all again, and nothing in the run would catch the slip.
- **Copying is the whole job.** 37 deals, 49 companies, 53 people and 20 passes are typed back from tool output every weekday morning.
- **The text leaves small choices open.**
  - CRM notes have a `date` that the documented shape lacks, so I left it out.
  - The pulse compare says "last contact", but Home keeps two such fields (finding 9).
- **Quiet pulses repeat work.** Every quiet pulse retypes the same 14 founder threads (about 8 KB), because the Pulse row reads 7 days of them each hour.

Compared with the shortcut (`bundle --now 2026-10-23T06:29:00+05:30 --mode daily --after 2026-10-22T19:29:00+05:30`, 129,935 bytes):

- **This difference matters.** The shortcut serves the CRM without the changes this run recorded:
  - Rivulet and Halo come back as First Meeting, with "Second meeting" due 24 Oct and last contact 19 Oct. Sable's last contact is 21 Oct.
  - A build from it shows both met logs undone on Pipeline: First meeting again, with the cleared step back.
  - That build also drops the two "add the next step" prompts, yet marks all three proposals "applied".
  - `crm record` and `crm deals` apply `crm_changes.json`. `bundle` does not.
- **This one matters a little.** The shortcut reads 15 LPs although Meera's LP watch is off, plus KPIs and empathy maps. So its run row says lps and drive were read, and the next run's windows differ.
- **It reads wider than the documented row:** all 90 companies, 100 people and 45 deals (passed and portfolio too), with no partial flags.
- **Threads and notes:** it keeps the other side's last message where Meera wrote last, plus snippets. Its notes keep `date`.
- **Otherwise the two builds match:** the same hero, push, 12 items, owed list and brief. Only the headline's "2 next steps to add" and the section order differ.

## 4. Next-run check

I rendered the real `home/index.html` with the harness's mock runtime, at phone width (380 px). The documents came from `evals/runs/friday-meera/db/`. Screenshots are in `evals/runs/friday-meera/qa/out/`.

**Fri 07:05, after the morning run:**

- Home opens on Today, since the push named the hero. The header reads "Fri 23 Oct, 06:29".
- **Hero:** "Another fund is moving. Sable Fraud AI: term sheet from Monsoon Arc Ventures". It quotes Abhishek, "wrote on 21 Oct", and offers Open and Snooze.
- **Today:**
  - "No meetings today."
  - Next up (4):
    - Rivulet feedback: Overdue, Fill in 3 lines.
    - Trellis pricing view: Due today, Fill in 3 lines.
    - Sable reference questions: Overdue, Draft ready.
    - Trellis competing fund: "Raise it at the 10:00 Monday partner meeting".
  - Signals: Rivulet's round is filling up.
  - Commitments due: 6.
  - Ready for you (4):
    - Rivulet's and Halo's "met 22 Oct, add the next step".
    - Ember's "met 21 Oct".
    - The Harborline draft, with its new times.
- Meera cannot open Monday's prep card anywhere in Home (finding 1).
- The harness checks on Today and Pipeline all pass: no horizontal scroll, one primary button, every control named, no text under 11.5 px, no script errors.

**Taps at 07:10, in one session:**

- **Opening the Sable row** shows the whole context under "Before you send:". Its buttons are Done, Open in Gmail, Sent it, Copy draft and Snooze.
- **Sent it on the Sable promise** marks the draft, the promise and the row done. The toast reads "Marked sent", and the row leaves Today.
- **Sent it on the Harborline draft** (in Ready for you) marks the draft only.
- **Done on "Confirm the second meeting slot"** marks the row and the promise.
- **The Ember met log**, saved as filled (Customer calls by 26 Oct, still Second meeting), writes `ns_d_ember_2026-10-21`. Its `current` matches the CRM.
- **Rivulet's step** ("Partner meeting decision", 26 Oct) writes `nss_d_rivulet_2026-10-22`.
- **Halo's step on Pipeline**, saved twice before a check: first "Insurer reference calls" by 28 Oct, then "with Shreya" by 29 Oct.
  - One id, `ns_d_halo`, holds the second save.
  - The row says "(saving to your CRM at the next check)".
  - Halo's prompt leaves Today.

**The 07:29 pulse**, run by the same skill from a fresh work folder:

- **`due`:** job `pulse`, mode `pulse`. Windows start at 06:29, except drive and lps, which still start at Thu 19:29 (finding 12).
- **`actions`:** 3 pending (Ember, Rivulet's step and Halo's second save). Each was re-read, marked and applied:
  - Ember: last contact set to 21 Oct. Its step and due were already there.
  - Rivulet and Halo: their steps set.
  - I wrote `applied.json`.
- **Reads:** no new mail or notes, and no event except Monday's meeting.
  - The CRM cannot filter by update time, so I compared its 37 open deals with Home's pipeline.
  - Only Rivulet, Halo and Ember differ. The bundle has `crm.partial`.
- **Build:** 12 items, 329 words, no warnings.
  - The hero is still Sable.
  - Push: "Review ready: Trellis Banking API: Saffron Peak Capital wants to lead". This is Thursday's held review.
  - `owed` is empty. By the pulse rule, no prep card needs questions.
  - I wrote a batch of 6 documents and finished the run row.

**Fri 07:40, after the pulse:**

- **Nothing was lost on deals:**
  - Rivulet reads "Next: Partner meeting decision by 26 Oct".
  - Halo reads "Next: Insurer reference calls with Shreya by 29 Oct".
  - Ember reads "Next: Customer calls by 26 Oct".
  - Proposals shows all six taps applied.
  - The sent and done rows stay gone.
  - People reads "1 day" for Abhishek, Omkar and Shreya.
- **Something was lost:** Monday's card came back with no questions (finding 1).
- **Something is wrong:** the pitch Meera had just answered is back on Today as "Inbound: Harborline Treasury. Score 93: book a call". Its Pipeline row reads "Book a call" (finding 4).
- **A third Halo save** at 07:40, after the last one was applied at 07:29:
  - The toast says "Saved. Goes to your CRM at the next check".
  - The row at once shows the old step, with no "saving" note (finding 2).
  - The engine is right. `actions --now 08:29` lists `ns_d_halo` as pending with the new text, so the 08:29 check applies it.
- The harness checks pass again, with no script errors.

## 5. Findings, worst first

1. **Medium (engine and Home): Friday's prep for Monday never reaches Meera.**
   - **The questions are wiped:** the 07:29 pulse wipes the questions the morning wrote. Home held them (snap/prep, version 2). The pulse build writes the card back with `questions: []`.
   - **Cause:** `_merge_card` in `cli.py` keeps written questions. But partner-meeting cards are built after that merge loop (`prep_by_meeting[m["id"]] = prep.partner_card(...)`), and nothing merges them.
   - **No rewrite comes:** by the pulse rule, no later run writes the questions again before Monday's brief.
   - **The card cannot be opened:** Today shows only today's meetings and `tomorrow`, which on a Friday is Saturday (empty). No row, no hero and no "Raise it at the 10:00 Monday partner meeting" line links to the card.
   - **Fix:**
     - Merge partner cards with Home's old card too, at least their questions.
     - On a Friday, let `tomorrow` hold the next working day, with a Prep link ("Monday: 10:00 Monday partner meeting").
     - Add a replay check that a Friday card keeps its questions through the next pulse.
2. **Medium (Home): a Pipeline step saved again after the last one was applied shows the old step for up to an hour, under a "Saved" toast.**
   - **Cause:** `pendingStepTap` compares the tap's `at` with the proposal's `applied_at` as text. The tap is in UTC ("2026-10-23T02:10:00.000Z"). The apply is in +05:30 ("2026-10-23T07:29:00+05:30").
   - **In India:** a re-save made less than five and a half hours after the apply looks already applied.
   - **West of UTC:** the same comparison would show every applied step as "saving" forever.
   - **Nothing is lost:** the engine parses the times and applies the step at the next check.
   - **Fix:**
     - Compare `Date.parse` values here, and wherever else the page compares times as text.
     - Add a QA check that mixes a page tap in UTC with a run time in +05:30.
3. **Medium (engine): Monday's card leads with a deadline that passes before the meeting.**
   - The card's finding reads "Decide on Sable Fraud AI by 23 Oct, and 10 more".
   - Its first agenda line is "Decide: Sable Fraud AI, by 23 Oct".
   - Its first seed ends "decides by 23 Oct. Do we move first, or step back?".
   - **Fix:**
     - On a card for a later day, label a decision whose deadline falls before the meeting: "Deadline 23 Oct passes before this meeting: decide today with Aditi". Keep it on Today.
     - Lead the card with the first decision still open in the room.
4. **Medium (engine and Home): "Sent it" on a pitch reply does not close the pitch.**
   - It marks only the draft.
   - At 07:29 the pitch comes back on Today as "Score 93: book a call". Its Pipeline row reads "Book a call".
   - **Fix:**
     - When a draft with an `inbound_id` is marked sent, the pitch reads "Replied on 23 Oct: offered Mon 26 and Tue 27 Oct".
     - It stays off Today until Elena answers.
     - The page's Sent it can also mark the pitch, as it marks a promise.
5. **Medium (engine): a partial pulse garbles stage names on deals it takes from Home.**
   - **What changes:** after 07:29, 21 of the 34 deals taken from Home read "Second_meeting", "First_meeting", "Partner_meeting" (for IC), "Term_sheet" or "Diligence" (for Due diligence).
   - **Where it shows:**
     - The Pipeline headers still read right.
     - "Copy for partners" on Sable now copies "Sable Fraud AI (Second_meeting, day 4): ...". She would paste that to her partners.
     - The Monday card's decisions list the same raw names.
     - A deal kept after a full read leaves it out gets the same label.
   - **Fix:** keep Home's stored display stage for deals the bundle does not send. Or map the key through the ontology's stage names.
6. **Medium (eval harness): the `bundle` shortcut ignores recorded CRM changes and reads wider than the rows.** The details are in the bundle section above.
   - **Fix:**
     - Apply `crm_changes.json` to `crm.deals` in `bundle`, as `crm deals` does.
     - Leave `lps` out when `modules.lp` is off.
     - In daily mode, cut people and companies to the morning row's sets, and set the partial flags.
     - Keep only the messages the thread rule asks for.
7. **Medium (skill text and engine): the morning bundle is still typed by hand.**
   - **The cost:** 66 KB every weekday morning, about 4 minutes of copying, and nothing in the run can check it.
   - **Quiet pulses:** each one retypes the same 14 founder threads (about 8 KB).
   - **The risk left:** the round-ten deal-drop risk is now guarded. But a slip in a stage, a date or an email would still pass silently.
   - **Fix:**
     - Let the engine keep the 7-day founder threads from Home, so a pulse sends only threads with a message since the window start.
     - Have the build report per-list counts against Home's last read, and flag values that move backwards (a stage, a last contact).
     - Longer term, build the bundle from saved tool output.
8. **Low to medium (product, carried from round ten): Today's hardest items still wait on Aditi, and nothing on Today helps Meera ask her.**
   - Sable must be decided today.
   - Rivulet's feedback is 4 days late, and Omkar says "the round is almost full".
   - Trellis's pricing view is due today, with Saffron Peak circling.
   - The only help is "Copy for partners", one deal at a time on Pipeline. The build log keeps this idea for later.
   - **Fix (as in round ten):** one short note to the holder. It lists each draft that waits on the firm's view, and the deadline today.
9. **Low (skill text): the pulse's CRM compare does not say which Home field "last contact" means.**
   - Home's pipeline row keeps two fields. `last_contact` counts meetings and mail. `crm_last_contact` is the CRM's own value.
   - Against `last_contact`, Ember's new CRM value (21 Oct, from her met log) looks unchanged and would be left out.
   - **Fix:** say "compare with `crm_last_contact`".
10. **Low (engine): there is no warning when the CRM read disagrees with a tap applied in the same run.**
    - In the shortcut build, Proposals said "applied" while Pipeline showed the step the tap had cleared.
    - **Fix:** warn when a deal in the bundle still holds a tap's `current` values after that tap is recorded applied.
11. **Low (engine and skill text): refresh entries carry no `they_owe`.**
    - The Sable draft still says "Thanks for the fraud loss benchmarks you are sending over". Home shows those benchmarks 2 days late.
    - **Fix:** carry `they_owe` on refresh, reslot and redate entries too. Then the rewrite asks plainly: "Could you also share the fraud loss benchmarks when you have them?".
12. **Low (engine): the run row's `read` leaves out drive and lps, because the bundle has no key for them.**
    - Drive searches for draft sources leave no trace.
    - With LP watch off, the lps window never moves. `due` at 07:29 still started both at Thu 19:29.
    - **Fix:** let the bundle name what was read (`read: [...]`). Skip windows for modules that are off.
13. **Low (skill text): the stage-entered date is still a guess, and the examples contradict setup.**
    - Round-ten finding 7 is unchanged.
    - The pulse names "a sheet column" as a writable stage date. But setup says Instinct "cannot write to a sheet".
    - **Fix:**
      - Setup records in snap/config whether the CRM's stage date is writable, and under which field.
      - Drop the sheet example.
14. **Low (eval harness): smaller gaps.**
    - **Answer file loaded:** `QA()` calls `demo.build` for seven members, which reads `evals/cases/commitments.json`. Following the brief literally loads an answer file. I subclassed it.
    - **No Slack:** `status` lists Slack as connected. But the mock has no Slack command, and the tool map has no Slack row.
    - **Old mail:** the mail still ends Wed 21 Oct 20:00, although three founder meetings happened on Thursday.
    - **No task:** `schedule list` is empty, although the story's weekday task is firing.
    - **Fix:**
      - Build demo snapshots only when `snap=` is not passed.
      - Add `slack search`.
      - Seed one Thursday thread per meeting, or say that none is expected.
      - Seed the weekday task.

## 6. Score: 7 out of 10 (as Meera)

The morning is right:

- The push names the one thing that cannot wait.
- My Thursday met logs were in the CRM before I woke. Home asked only for the two missing steps.
- The Harborline reply got real free times that suit both Delaware and Bangalore.
- The two drafts written before Thursday's meetings were refreshed honestly.
- Every tap I made was in the CRM by 07:29. "Sent it" closed a promise in one tap.
- Nothing was sent or made up.

It stays at 7 because the parts I lean on most still leave me alone with the work, or make me doubt the page:

- Three of my top items wait on Aditi, and nothing on Today helps me ask her.
- Monday's prep, which a Friday now writes, is nowhere I can open. An hour later it was gone.
- The pitch I had just answered asked me to book a call again.
- The Halo step I fixed showed the old text under a "Saved" toast. So I would have saved it a fourth time.

It is a better 7 than round ten. Three silent risks behind the scenes are fixed: a dropped deal, eroded company records, and "Today" on People.

- **An 8** needs three things: keep and show Monday's prep on Friday, close a pitch when its reply is sent, and make a re-saved step read as saving.
- **A 9** needs the note to Aditi.

## Round-ten findings

| # | Round-ten finding | Now |
| --- | --- | --- |
| 1 | High: a deal left out of a full read vanished | Fixed: kept with a warning (tested by leaving Mosaic out). Pulses now send only changed deals (9.3 KB, was 21.8 KB). The morning bundle is still typed by hand (finding 7), and kept deals lose their stage name (finding 5). |
| 2 | Medium: the morning brief's calendar range contradicted itself | Fixed |
| 3 | Medium: People said "Today" for people not touched today | Fixed (1 day, 3 days, 10 days) |
| 4 | Low to medium: narrow reads eroded the directory | Fixed (90 descriptions and 20 pass ids kept) |
| 5 | Low to medium: Friday prep stopped at Saturday | Partly fixed: the card and its questions are built, but Home cannot open them on Friday, and the next pulse wipes the questions (finding 1) |
| 6 | Low to medium: nothing helped Meera ask Aditi | Not fixed (kept for later in the build log) |
| 7 | Low: no way to know if the stage-entered date is writable | Not fixed |
| 8 | Low: the `already` example named one field | Fixed |
| 9 | Low: the slot rule ignored the founder's time zone | Fixed in the skill text. The engine's reslot entry still carries no zone hint. |
| 10 | Low: the seeded history did not add up | Partly fixed: taps are now stamped 20:45, and the clock reads Fri 06:29. But the mail still ends Wed, and Slack is listed but missing. |
