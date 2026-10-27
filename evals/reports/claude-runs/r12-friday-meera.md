<!-- Claude-run eval, round twelve. Written by a Claude agent running the pulse skill against the mock connectors on a clean clone at 947db4c (0.7.5), writing bundle.json by hand in one Write call. The Write tool refused to save evals/runs/friday-meera/report.md ("subagents should return findings as text"), so this returned text is the report; saved by the main session. -->

# Eval report: friday-meera (round 12)

- Plugin: instinct-vc 0.7.5 (`.claude-plugin/plugin.json`; the pulse and morning-brief skills are 0.7.5; engine `check` says 0.7.5)
- Commit: `947db4c Round twelve: a note to the partner the work waits on, replies that answer, times true at every hour, Friday sees Monday; version 0.7.5`
- `git status --short`: clean before (right after checkout) and clean after.
  - Everything I wrote is under the ignored `evals/runs/friday-meera/` in DIR (`/tmp/claude-0/-home-claude/f41ebfd9-0635-5201-96ea-278169523f82/scratchpad/evals-r12/friday-meera`).
  - Python wrote ignored bytecode caches: `engine/instinct/__pycache__/` and `evals/__pycache__/`.
  - I never wrote to `/home/claude/instinct-vc`. Its status is clean, at the same commit.
  - The report file itself could not be saved: the Write tool refused it.
- Member: `meera` (Meera Iyer, Associate, Quillwater Ventures, Asia/Kolkata)
- Run: Fri 23 Oct 2026, 06:29 IST.
  - Run id `r20261023T0629`, jobs `morning_brief` and `pulse`, build mode `daily`.
  - Then the next pulse, `r20261023T0729` (job `pulse`, mode `pulse`).
- Skill: `skills/pulse/SKILL.md` steps 1 to 7, plus `skills/morning-brief/SKILL.md` steps 5 to 7 and `references/owed-kinds.md`, and the shared docs they name.
- Final line at 06:29: `Sable Fraud AI: term sheet from Monsoon Arc Ventures, decide today`
- Final line at 07:29: `Review ready: Trellis Banking API: Saffron Peak Capital wants to lead`

Eval-mode adjustments:

- **Guard:** skipped pulse step 0. No guard loads in eval mode.
- **Engine:** ran it from the clone, isolated (`python3 -I -S <clone>/engine/instinct.py`), from work folders under the run folder. I did not copy it.
- **Run time:** passed `--now 2026-10-23T06:29:00+05:30` to `due` (and `07:29` for the next pulse). I passed each run's start to `actions`, as the skill says.
- **Home reads and writes:** used the mock `db` commands for every one.
- **Home link:** from `artifact list`. The mock's `schedule list` now shows the two tasks, but not their prompts, so no prompt carried the link.
- **Drafts:** `status` lists no create-draft tool for Gmail. So every draft stayed in Home (`in_gmail` false), and I made no `drafting` mark.
- **Applying marks:** the mock clock is fixed, so I stamped them 06:31 to 06:33 and 07:31 to 07:33.
- **No user prompts:** no question to the user came up, and no connector card.
- **One probe outside the skill:** `slack search`. It returns nothing, as eval-mode says.
- **Next-hour check only:**
  - I used `evals/home_qa.QA` as it is. No subclass was needed: passing `snap=` no longer builds the demo Homes.
  - I passed `snap=`, `state=`, `runs=`, `when=` and `member=` myself, from `evals/runs/friday-meera/db/`.
  - A small script put the page's own state writes into the mock store with `db update`, as the page's database would.
  - In the 07:29 pulse, a script copied the read's version lines into `versions.txt` and picked the founder threads by Home's deal domains. A real run would paste the lines and pick by eye. I still read every thread again.
- **Eval-side checks, not part of any run:** a field-by-field check of each bundle against the saved tool output, the shortcut comparison, and one build from a stale CRM read.

## 1. What I ran, in order

1. **Setup:** clone at `947db4c`, clean.
   - `seed_eval.py friday meera` gave 14 snapshots, 14 runs, 7 drafts and 3 taps (`ns_d_rivulet_2026-10-22`, `ns_d_halo_2026-10-22`, `ns_d_sable_2026-10-22`).
   - I read eval-mode.md, the round-eleven report, both skills, owed-kinds.md and the shared docs. I opened no answer file.
2. **`status`:** nine connectors connected. The mock clock reads Fri 23 Oct 06:29. Gmail has no `create_draft`.
3. **Home link:** `schedule list` (two tasks, no prompt text), then `artifact list` (`mock-instinct-home`).
4. **`db list`** for snap, state and runs, into `work/home-db`:
   - 14 snap documents, all at version 1.
   - 3 approved `next_step` taps, stamped Thu 20:45. `state/items` is empty.
   - 14 run rows. The last is Thu 19:29, "Nothing new".
   - I wrote `versions.txt` (16 lines) and copied `config.json` (associate, 450 words, 12 items, triage `own`, LP watch off).
5. **Engine `check`:** ok, 0.7.5.
6. **`due`:** jobs `morning_brief, pulse`, mode `daily`, every window from Thu 19:29, run id `r20261023T0629`. I created the run row (version 1).
7. **`actions`:** 3 pending, none refused, none to check by hand.
   - I re-read each deal with `crm record`. All three were open, and each step matched its payload.
   - I applied each tap after its own applying mark (row versions 2, 3 and 4), then read all three back.
   - I wrote `applied.json`.
8. **Reads, by the Morning brief row:**
   - Gmail since 16 Oct: 19 threads, each read in full. The latest is Wed 21 Oct 20:00. A search since 22 Oct returns nothing.
   - Calendar, 23 Sep to 6 Nov: 18 events. None on Friday. The next is the Mon 26 Oct 10:00 partner meeting.
   - Granola since 22 Oct: nothing. Thursday's meetings have no notes.
   - CRM: 45 deals (37 open), 90 companies, 100 people, 13 notes and 20 passes.
   - Compared with Home's `snap/pipeline`: the same 37 open deals. Only my three writes differ.
   - For the drafts: 5 Drive searches (nothing), and the two transcripts the drafts came from (`tr05`, `tr15`).
9. **`bundle.json`:** written by hand in one Write call (67,615 bytes):
   - 19 threads, 18 events, `transcripts: []`;
   - the 37 open deals and their 13 notes;
   - 49 companies (open deals and portfolio, `companies_partial`) and their 53 people (`people_partial`);
   - 20 passes.
10. **Extraction:** no notes, pitches or founder updates arrived since the window start. Nothing to extract.
11. **`build --mode daily --applied applied.json`:**
    - Hero: the Sable term sheet.
    - 12 items, 328 words (budget 450), no warnings.
    - Push: "Sable Fraud AI: term sheet from Monsoon Arc Ventures, decide today" (66 characters).
    - 3 owed entries, and one prep card (Monday's partner meeting), now also in `tomorrow` with a prep link.
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

- **Time:** about 12 minutes (09:21:42 to 09:33:30 UTC).
- **Connector calls:** 59.
  - 19 thread reads, 5 Drive searches, 2 transcripts, 6 CRM record reads and 3 CRM writes.
  - 4 run-row updates, 1 run-row read back and 1 batch.
- **Nothing outgoing:** no send, reply, forward, draft save or calendar call.

## 2. The pending taps

At 06:29:

1. **`ns_d_rivulet_2026-10-22`:** met 22 Oct, stage "Second meeting", `clear_step`, no text.
   - **CRM before:** First Meeting since 17 Oct, step "Second meeting" due 24 Oct, last contact 19 Oct.
   - **One call:** stage "Second Meeting" (the CRM's own option, as Sable shows), stage-entered 22 Oct, next step and due null, last contact 22 Oct.
   - **Result:** applied. Home then asks "Rivulet Payments: met 22 Oct, add the next step".
2. **`ns_d_halo_2026-10-22`:** the same shape. The CRM had First Meeting since 10 Oct. The same five fields. Applied, and Home asks for Halo's step.
3. **`ns_d_sable_2026-10-22`:** "Diligence kickoff", due 24 Oct, stage null.
   - The step and its date were already in the CRM.
   - **One call:** last contact from 21 Oct to 22 Oct.
   - **Result:** `{"status": "applied", "already": ["next_step", "next_step_due"]}`.

About the stage-entered date: the pulse text now names "an Affinity field" as one to write, and the record carries `stage_entered`. So I set it, as rounds ten and eleven did. Halo reads "Day 1 of 10", not day 13.

At 07:29 (taps Meera made at 07:10):

4. **`ns_d_ember_2026-10-21`** (met log saved as filled): step and due already held. **One call:** last contact 19 Oct to 21 Oct. Applied with `already`.
5. **`nss_d_rivulet_2026-10-22`:** "Partner meeting decision" by 26 Oct. The step was empty, as `current` said. Applied.
6. **`ns_d_halo`** (the Pipeline step, saved twice): the second save, "Insurer reference calls with Shreya" by 29 Oct. Applied.

After each build, Proposals shows every tap as "applied", with the `already` fields.

## 3. The owed entries and their drafts

The engine listed three entries, the same as round eleven. All three stay in Home. There was no holder entry, because Thursday's note to Aditi still waited in Home (one at a time).

1. **`dr_i_0e2115836d`, `reslot`.** The Harborline Treasury reply (score 93, call) offered Fri 23 Oct 10:00 and 11:00, which is today. `avoid_slots` was empty.
   - **Time zone:** the entry carries no time-zone hint. The pitch says "based in Delaware, US and Bangalore, India". So I used the overlap hours. 17:30 IST is 08:00 US Eastern (still daylight time until 1 Nov).
   - **Slots:** Mon 26 Oct 17:30 and Tue 27 Oct 17:30 IST. Both are free and clear of other events (Monday's only event ends at 11:00).
   - **To:** Elena Fischer (elena@harborline.co). **Subject:** "Re: Harborline Treasury".

   > Hi Elena,
   >
   > Thanks for sending Harborline Treasury our way. It fits what we back, and we would like to hear more. Would Mon 26 Oct at 17:30 IST (08:00 ET) or Tue 27 Oct at 17:30 IST (08:00 ET) work for a 30-minute call?
   >
   > Meera

   Context: "Inbound pitch, score 93: call. Slots from your calendar. The old times (Fri 23 Oct at 10:00 and 11:00 IST) were too short notice, so these are two new free ones. Harborline is in Delaware and Bangalore, so both suit IST and US Eastern: check them before you send"

2. **`dr_k_454489f888`, `refresh`.** "Share feedback after the partner meeting" to Omkar. It is 4 days late, and Aditi holds the firm's view.
   - **Why a refresh:** it was written before the 22 Oct "Rivulet Payments: follow-up", which has no notes.
   - **`they_owe`:** data room access, 4 days late. The draft already asks, so I kept its line.
   - **What I changed:** one dated greeting that claims nothing about the meeting. Drive and the notes hold no feedback, so the three bracketed lines stay.
   - **To:** Omkar Patil (omkar@rivuletpay.com). **Subject:** "Rivulet Payments: our feedback".

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
   - **`they_owe`:** the fraud loss benchmarks, promised for 21 Oct. The old draft thanked him for them ("you are sending over"). It now asks for them instead, in one line.
   - The three questions stay marked as Instinct's (the old context said so). The 20 Oct notes support the second ("false positives are down forty percent").
   - **To:** Abhishek Joshi (abhishek.joshi@sablefraud.ai). **Subject:** "Sable Fraud AI: reference questions for your customers".

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
   > Could you also share the fraud loss benchmarks when you have them?
   >
   > Meera

   Context: "You promised this on 20 Oct, due 22 Oct. The three questions are Instinct's suggestions, not from your notes: check them before you send. It was written before your 22 Oct references meeting, which has no notes: check it still stands, or tap Done if it was settled in the room. Abhishek's fraud loss benchmarks, promised for 21 Oct, have not come, so the note now asks for them"

Already waiting in Home, and rightly not owed again:

- **The note to Aditi** (`dr_hold_aditi_rao_2026-10-22`, written Thursday). Its lines are dated, so they still read true on Friday:

   > Hi Aditi,
   >
   > A few founder emails wait on your view before I send them:
   >
   > - Rivulet Payments: feedback after the partner meeting, for Omkar, was due Mon 19 Oct
   > - Trellis Banking API: our view on pricing, for Neha, due Fri 23 Oct
   > - Sable Fraud AI: term sheet from Monsoon Arc Ventures, decide by Fri 23 Oct
   >
   > A line on each is plenty, or ten minutes today if easier.
   >
   > Meera

- **Trellis pricing view:** a draft waits, and there was no meeting since.
- **NBFC list for Leena:** the draft was written after their meeting.
- **Copperleaf question:** a reply draft waits.
- **Halo's slot confirmation:** it looks done.
- **Lattice KYC:** she is already in touch.
- **Dhruv Data:** an ask for more, and associates draft replies only to calls.

Prep questions for Monday's partner meeting. They are Instinct's, from the card's seeds, for the top three decisions as step 5 says:

1. "Gravity Payouts: two other funds have offers and Arjun decides by 31 Oct; what would make ours the offer he takes?"
2. "Atlas Settlement: Bluepeak Partners has a term sheet out and Ishaan decides by 05 Nov; do we move first, or step back?"
3. "Kite Pay: Tamarind Capital wants to lead the $3M Seed; do we offer to co-lead, or follow?"

The card now leads with Gravity Payouts, and Sable reads "Deadline 23 Oct passes before this meeting: decide by then with Aditi". None of the three questions is about Meera's own deals (finding 4).

## Writing bundle.json by hand

- **Size:** 67,615 bytes (round eleven: 65,922). By part, roughly:
  - threads 11 KB, events 7 KB, companies 14 KB, people 12 KB;
  - deals 14 KB, notes 3 KB, passes 5 KB.
- **Time:** about 3.5 minutes for the one Write call (09:27:05 to 09:30:31 UTC).
- **Errors:** 0. I checked it afterwards, field by field, against the saved tool output. That check is eval-side: a scheduled run cannot make it.
- **The 07:29 pulse bundle:** 12,175 bytes, 0 errors.
  - 3 sent notes, 14 founder threads, 1 event, `transcripts: []`, and 3 changed deals with `crm.partial`.
  - I did not time it: my clock calls ran in the same message as the Write.

What was hard:

- **All or nothing.** One slip in 68 KB means writing it all again, and nothing in the run would catch it.
- **Copying is the whole job.** 37 deals, 49 companies, 53 people and 20 passes are typed back from tool output every weekday morning.
- **Small choices stay open.**
  - CRM notes carry a `date` the documented shape lacks. I left it out.
  - Sent mail comes back with no recipient names and a UTC stamp. I kept it as the tool gave it.
- **Quiet pulses repeat work.** The 07:29 bundle retyped the same 14 founder threads (about 8 KB of its 12 KB), all unchanged since 06:29.

Compared with the shortcut (`bundle --now 2026-10-23T06:29:00+05:30 --mode daily --after 2026-10-22T19:29:00+05:30`, 82,614 bytes):

- **It now matches a careful hand-written run.** Same 19 threads with the same messages, 18 events, 49 companies, 53 people, 37 deals, 13 notes and 20 passes, with both partial flags.
  - It applies the CRM changes this run recorded (Rivulet and Halo at Second Meeting, Sable's last contact 22 Oct).
  - It leaves LPs out, since LP watch is off.
- **What it adds:** thread snippets, note dates, `firm` (with a fund name and size the config lacks), `thesis` and a `fictional` tag. None of it changes the output.
- **The builds match:** the same `brief.md`, owed list, report, hero and push. Every snapshot is the same, except prep and drafts, which my `questions` and `drafts` commands changed after the build.

## 4. Next-run check

I rendered the real `home/index.html` with the harness's mock runtime at phone width (380 px). The documents came from `evals/runs/friday-meera/db/`. Screenshots are in `evals/runs/friday-meera/qa/` under DIR.

**Fri 07:05, after the morning run:**

- Home opens on Today. The header reads "Fri 23 Oct, 06:29".
- **Hero:** "Another fund is moving. Sable Fraud AI: term sheet from Monsoon Arc Ventures". It quotes Abhishek, "wrote on 21 Oct", and offers Open and Snooze. It does not point at the note to Aditi.
- **Today:** "No meetings today", then "Monday: 10:00 Monday partner meeting".
- **Next up (4):**
  - Rivulet feedback: Overdue, Fill in 3 lines, "Note to Aditi ready, under Ready for you".
  - Trellis pricing view: Due today, Fill in 3 lines, the same pointer.
  - Sable reference questions: Overdue, Draft ready.
  - Trellis competing fund: "Raise it at the 10:00 Monday partner meeting".
- **Signals:** Rivulet's round is filling up. **Commitments due:** 6.
- **Ready for you (5):** Rivulet's and Halo's "add the next step", Ember's "met 21 Oct", the note to Aditi, then the Harborline reply with its new times. On a phone the note to Aditi is about four screens down.
- **Pipeline:** Rivulet and Halo read "Day 1 of 10". Harborline's pitch reads "Book a call, Reply ready".
- The harness checks on Today and Pipeline all pass: no horizontal scroll, one primary button, every control named, no text under 11.5 px, no script errors.

**Taps at 07:10 and 07:12:**

- **Monday's prep from Today:** the "10:00 Monday partner meeting" link opens the card, with its 12 decisions and my three questions.
- **Sable row, opened:** "Before you send:" shows the whole context. Buttons: Done, Open in Gmail, Sent it, Copy draft, Snooze. **Sent it** marks the draft, the promise and the row ("Marked sent"), and the row leaves Today.
- **Sent it on the Harborline reply:** marks the draft. Pipeline's Pitches row now reads "You replied 23 Oct: waiting on them".
- **Sent it on the note to Aditi:** marks the note. The two rows stop pointing at it. They say nothing else.
- **Ember met log**, saved as filled (Customer calls by 26 Oct, still Second meeting): writes `ns_d_ember_2026-10-21`, its `current` matching the CRM.
- **Rivulet's step** ("Partner meeting decision", 26 Oct): writes `nss_d_rivulet_2026-10-22`.
- **Halo's step on Pipeline, saved twice:** "Insurer reference calls" by 28 Oct, then "with Shreya" by 29 Oct. One id, `ns_d_halo`, holds the second. The row reads "(saving to your CRM at the next check)", and Halo's Today prompt leaves.
- **Done on "Confirm the second meeting slot":** my first try clicked the row, since its text says "Tap Done to close it", and wrote nothing. At 07:12 I pressed the button itself: "Marked done", on the row and the promise.
- After the taps, Ready for you is empty. The harness checks pass again.

**The 07:29 pulse**, run by the same skill from a fresh work folder (43 connector calls, about 4 minutes):

- **`due`:** job `pulse`, mode `pulse`. Windows start at 06:29, except drive and lps, still at Thu 19:29 (finding 7).
- **`actions`:** 3 pending (Ember, Rivulet's step and Halo's second save). Each was re-read, marked and applied. I wrote `applied.json`.
- **Reads:**
  - Mail: the three notes Meera marked sent, each its own new thread, stamped 01:40 UTC. The 14 founder threads are unchanged.
  - Calendar to Monday: only Monday's meeting. Notes: none.
  - CRM compared with Home's pipeline: only Rivulet, Halo and Ember differ.
- **Build:** 12 items, 327 words, no warnings, nothing owed.
  - The hero is still Sable, "decide today".
  - Push: "Review ready: Trellis Banking API: Saffron Peak Capital wants to lead". This is Thursday's held review (finding 5).
  - `snap/prep` was unchanged, so it was not rewritten.
  - I wrote a batch of 6 documents and finished the run row (version 5).

**Fri 07:40, after the pulse:**

- **Nothing was lost:**
  - Monday's card still has its three questions.
  - Rivulet reads "Next: Partner meeting decision by 26 Oct". Halo reads "Next: Insurer reference calls with Shreya by 29 Oct". Ember reads "Next: Customer calls by 26 Oct".
  - Proposals shows all six taps applied.
  - The sent and done rows stay gone.
  - Harborline stays off Today. Its Pitches row still reads "You replied 23 Oct: waiting on them".
  - Stage names read right everywhere. "Copy for partners" on Sable copies "Sable Fraud AI (Second meeting, day 4): We have a term sheet from Monsoon Arc Ventures and need an answer by Friday. ..."
  - People reads "Today" for Abhishek (she wrote to him at 07:10), and "1 day" for Omkar and Shreya.
- **New on Today:** "Inbound worth a look" with Lattice KYC ("you already write to them: answer in your thread") and Dhruv Data. They fill the rows she cleared. Neither is new.
- **Unchanged after her note to Aditi:** the hero still says "decide today", and the two drafts still say "check the firm's view with Aditi". Nothing says she asked at 07:10 (finding 1).
- **A third Halo save at 07:40**, after the 07:29 apply: "Saved. Goes to your CRM at the next check", and the row at once reads "Insurer reference calls with Shreya and the CFO by 30 Oct (saving to your CRM at the next check)". `actions --now 08:29` lists `ns_d_halo` as pending, its `current` matching the CRM.
- The harness checks pass on Today, Pipeline and People, with no script errors.

## 5. Findings, worst first

1. **Medium (engine and Home): once the note to Aditi goes, nothing shows it, and nothing follows it up on deadline day.**
   - Meera sent it at 07:10. The 07:29 run read it in her sent mail.
   - At 07:40 the hero still says "Sable Fraud AI: term sheet from Monsoon Arc Ventures, decide today". The two drafts still say "check the firm's view with Aditi". Nothing reads "Asked Aditi at 07:10".
   - The engine uses the sent mark only to hold off a new note for three working days (`engine/instinct/cli.py`, "One note at a time"). A holder note has no nudge, even when a decision in it is due today.
   - Before sending, the hero names the very decision the note covers, yet does not point at the note. Only the two Next up rows do, and the note sits near the bottom of a long phone page, under three CRM forms.
   - **Fix:**
     - When a holder note is marked sent, its rows and any hero for a decision it names read "Asked Aditi 07:10: waiting on her view".
     - While the note waits, the hero points at it too ("Note to Aditi ready"), and the note leads Ready for you.
     - When a decision in a sent note is due today and no reply from the partner is in mail by mid-afternoon, push one line ("Sable: no word from Aditi yet, deadline today").
     - Add a QA check after Sent it on a holder note.
2. **Medium (skill text and engine, carried): the morning bundle is still typed by hand.**
   - **The cost:** 68 KB every weekday morning, about 3.5 minutes of copying, and nothing in the run can check it.
   - **Quiet pulses:** the 07:29 bundle retyped 14 unchanged founder threads (about 8 KB of 12 KB).
   - **The risk left:** a slip in a stage, a date or an email would pass silently. Finding 3 shows one way a stale value undoes a tap with no warning.
   - **Fix:**
     - Let the engine keep the 7-day founder threads from Home, so a pulse sends only threads with a message since the window start.
     - Have the build report per-list counts against Home's last read, and flag values that move backwards (a stage, a last contact).
     - Longer term, build the bundle from saved tool output.
3. **Low to medium (engine): a stale CRM read can undo a met log with no warning.**
   - The new warning (`cli.py`, near "this run's CRM read still shows the old next step") fires only when a tap set new step text and the read still shows the old text.
   - **Test:** I rebuilt 06:29 from my bundle with Rivulet's pre-tap values (First Meeting, "Second meeting" due 24 Oct, last contact 19 Oct) and the same `applied.json`.
     - No warning.
     - Pipeline shows Rivulet in First meeting, day 6, with the cleared step back.
     - Proposals says "applied", and the "add the next step" prompt is gone.
   - **Fix:** also warn when an applied tap's `clear_step` still shows the old step in the read, when its `stage` moved but the read shows the old stage, and when its `met` is later than the read's last contact.
4. **Low to medium (skill text): Monday's prep questions skip Meera's own deals.**
   - Step 5 says a partner card's questions ask for a decision on the top three. Those are Aditi's and Kabir's (Gravity, Atlas, Kite).
   - The card lists Meera's three in `yours` (Rivulet, Trellis, Sable). Today twice tells her to raise Trellis and Rivulet "at the 10:00 Monday partner meeting". No question covers them.
   - **Fix:** for levels below partner, write the questions about the deals in `yours` first (what to raise, and the decision she needs), or put them first in the card's `question_seeds`.
5. **Low to medium (engine and eval harness): the 07:29 push names a review this Home cannot show.**
   - "Review ready: Trellis Banking API: Saffron Peak Capital wants to lead" went out at 07:29, an hour after the morning push. It is Thursday's held review (`review:2026-10-22`), sent on the next working day by design (`pending_deferred` in `cli.py`).
   - The seeded Home has no `snap/digests`, although the seeded 15:29 row says a review was built. So the push leads to no review.
   - Even with the review there, the line repeats a Today row ("Raise it at the 10:00 Monday partner meeting").
   - **Fix:**
     - Seed `snap/digests` when a seeded run row says it wrote a review.
     - In the engine, carry a held review only when Home holds it, and skip the carry when its subject already leads Today.
6. **Low (Home): rows that wait on someone do not show that Meera just asked.**
   - Her Sable note asked for the benchmarks. "Abhishek Joshi owes you: share the fraud loss benchmarks" still reads "Waiting on them, 2 days late".
   - **Fix:** when a sent draft carried a `they_owe` ask, that row reads "You asked on 23 Oct".
7. **Low (engine, carried): the run row's `read` leaves out drive and lps.**
   - The bundle has no key for either, so their windows never move. At 07:29 and 08:29, `due` still starts both at Thu 19:29.
   - The five Drive searches for draft sources leave no trace.
   - **Fix:** let the bundle name what was read (`read: [...]`), and skip windows for modules that are off.
8. **Low (engine, carried): reslot entries carry no time-zone hint.**
   - I found "Delaware, US and Bangalore, India" in the pitch myself.
   - **Fix:** carry the pitch's or the company's `hq` on `reslot` and `inbound_reply` entries.
9. **Low (skill text, carried): whether the stage date is writable is still a guess.**
   - The pulse now names "an Affinity field", and the sheet example is gone.
   - Setup still records nothing in `snap/config`.
   - **Fix:** setup records whether the CRM's stage date is writable, and under which field.
10. **Low (engine wording): Monday's card says Sable's deadline three times.**
    - "Deadline 23 Oct passes before this meeting: decide by then with Aditi. Term sheet from Monsoon Arc Ventures, decide by 23 Oct. Their deadline 23 Oct is before your next step 24 Oct".
    - **Fix:** keep the first sentence, then the source.
11. **Low (eval harness): smaller gaps.**
    - `schedule list` shows the tasks but not their prompts, so the Home link cannot come from the prompt, as pulse step 1.2 says first. The cron shows no time zone.
    - Sent mail lands as one new thread per note, in UTC, with no recipient names. A reply sent inside the founder's thread is never tested.
    - `status` still reports 06:29 at 07:29, since the clock is fixed.
    - The harness has no helper to press a row's action by its exact label. "Done" also matches row text such as "Tap Done to close it", which cost me a first try.
    - Subagents cannot write `report.md`: the Write tool refuses report files, so the brief's "save it to report.md" step fails every time.
    - **Fix:** show the prompts, move `status` with `--now`, add one in-thread reply, add `QA.tap(row, "Done")` that matches a button's exact name, and have the main session save the returned report.

## 6. Score: 8 out of 10 (as Meera)

The morning works, and so does the hour after it:

- The push names the one thing that cannot wait.
- My Thursday met logs were in the CRM before I woke. Home asked only for the two missing steps.
- The note to Aditi was ready, and the two rows that wait on her pointed at it. Sending it was one tap to open it in Gmail and one to mark it sent.
- Monday's prep opens from Today on a Friday, and it survived the next check.
- The Harborline reply got real free times that suit Delaware and Bangalore. After Sent it, the pitch says I replied and stays off Today.
- Every step I saved, even three times, showed as saving and was in the CRM at the next check.
- Nothing was sent or made up.

It is not a 9 yet:

- After I sent the note to Aditi, Today looks exactly as before. Sable still says "decide today", with no sign the question is with her, and nothing chases her before the deadline.
- Monday's questions are about Aditi's and Kabir's deals, not the three I must raise.
- The second push, an hour after the first, said "Review ready" for a review I could not find.

Round eleven's bar for an 8 is met in full: Monday's prep kept and shown, the pitch closed by its reply, and a re-saved step reading as saving.

- **A 9** needs the sent note to show on the hero and rows ("Asked Aditi 07:10"), with one same-day follow-up when a decision in it is due today, and prep questions on my own deals.

## Round-eleven findings

| # | Round-eleven finding | Now |
| --- | --- | --- |
| 1 | Medium: Friday's prep for Monday never reached Meera | Fixed: "Monday: 10:00 Monday partner meeting" on Today opens the card, and the 07:29 pulse kept its questions |
| 2 | Medium: a re-saved Pipeline step showed the old step | Fixed: times compare as instants. A third save at 07:40 read "saving" at once, and 08:29 lists it |
| 3 | Medium: Monday's card led with a deadline that passes first | Fixed: it leads with Gravity Payouts, and Sable says its deadline passes before the meeting (the wording repeats, finding 10) |
| 4 | Medium: Sent it on a pitch reply did not close the pitch | Fixed: "You replied 23 Oct: waiting on them", and it stays off Today |
| 5 | Medium: a partial pulse garbled stage names | Fixed: names read right after 07:29, and Copy for partners reads "Second meeting, day 4" |
| 6 | Medium: the bundle shortcut ignored CRM changes and read wide | Fixed: it applies the changes, leaves LPs out, uses the morning sets, and builds the same Home |
| 7 | Medium: the morning bundle is typed by hand | Not fixed (finding 2) |
| 8 | Low to medium: nothing helped Meera ask Aditi | Partly: the note exists and the rows point at it. After sending, nothing shows it or follows it up (finding 1) |
| 9 | Low: the compare's "last contact" was unclear | Fixed: the text names `crm_last_contact` |
| 10 | Low: no warning when the CRM read contradicts an applied tap | Partly: it warns for new step text only, not a cleared step or a stage move (finding 3) |
| 11 | Low: refresh entries carried no `they_owe` | Fixed: both refreshes carried it, and the Sable draft now asks for the benchmarks |
| 12 | Low: the run row's `read` leaves out drive and lps | Not fixed (finding 7) |
| 13 | Low: the stage-entered date is a guess, and examples contradict setup | Partly: the sheet example is gone; setup still records nothing (finding 9) |
| 14 | Low: harness gaps | Mostly fixed: no demo build with `snap=`, Slack search exists, eval-mode says no Thursday mail is expected, tasks are listed. New gaps in finding 11 |

Files worth keeping (all under `/tmp/claude-0/-home-claude/f41ebfd9-0635-5201-96ea-278169523f82/scratchpad/evals-r12/friday-meera/evals/runs/friday-meera/`): `work/` (06:29 run: bundle.json, applied.json, questions.json, owed-drafts.json, run/), `work-0729/` (07:29 pulse), `evalcheck/` (shortcut bundle and build, stale-read build, QA scripts, page writes), `qa/` (phone screenshots), `db/` (the mock Home both runs left), `mock_log.jsonl` and `crm_changes.json`.
