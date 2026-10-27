<!-- Claude-run eval, round eleven. Written by a Claude agent running the pulse skill against the mock connectors on a clean clone at be80587 (0.7.4), writing bundle.json by hand in one Write call; saved by the main session (the agent could not write files). -->

# Eval report: nudge-tara (round 11)

I score 0.7.4 at **8 out of 10 as Tara**, up from 7. Seven of the eight round-ten findings are fixed or half fixed, and number 4 is half fixed. Two medium problems remain:
- **The hero's draft promises a date that has passed.** It says "by Tue 27 Oct" on Thu 29 Oct, and Instinct picked that date itself.
- **Home goes stale after Sent it.** Today's grouped row and the Portfolio hero keep saying "Nudge ready" for up to an hour.

- **Plugin version:** 0.7.4 (plugin.json, pulse and morning-brief SKILL.md metadata, engine `check`)
- **Commit:** `be80587 Round eleven: Sent it wherever a draft shows, replies stop follow-ups, money kept while unpaid, taps that hold; version 0.7.4`
- **`git status --short`:** empty before the run and empty after. Only ignored paths were written (`evals/runs/`, `__pycache__/`). No tracked file was edited.
- **Member:** Tara Menon (`tara`), Head of Platform, level `platform`. Her config opens Home on Portfolio.
- **Run:** the scheduled "Instinct" weekday run on Thu 29 Oct 2026 at 06:28 Asia/Kolkata (run id `r20261029T0628`), then the 07:28 pulse (run id `r20261029T0728`).
- **Skill:** `skills/pulse/SKILL.md` with jobs `morning_brief` and `pulse`. Also `skills/morning-brief/SKILL.md` steps 5 to 8 and `references/owed-kinds.md`.
- **Home link** from the scheduled prompt: `https://claude.ai/artifact/mock-instinct-home`.

**Eval-mode adjustments:**
- I skipped pulse step 0, because no guard loads in eval mode.
- I ran the engine from the clone, isolated (`python3 -I -S <DIR>/engine/instinct.py`), instead of copying it. The work folders were `evals/runs/nudge-tara/work/` and `work0728/`.
- I passed `--now 2026-10-29T06:28:00+05:30` to `due`, and `07:28` for the next run. `actions` got the run's start time, as the skill says.
- Every Home read and write used the mock `db` commands. `db list` stood in for the ordered runs query.
- Every connector read went through `mock_connectors.py --as tara` with `INSTINCT_RUN=nudge-tara`. I called no real app tool and opened no answer file.
- I wrote `bundle.json` by hand, in one Write call, from my own window reads.
- To test the next hour I played Tara's page. I wrote her three taps to `state/items` and `state/actions` with mock `db update`, exactly as the QA harness recorded the page's writes. A run never writes state, so this stood in for the page.
- No AskUserQuestion or connector-card moment came up.

## 1. What I ran, in order

**The 06:28 run:**
1. **Setup.** Cloned, checked out `be80587`, tree clean. `seed_eval.py nudge tara` gave 14 snapshots, 76 runs (last 60 kept) and 3 drafts.
2. **Reading.** `eval-mode.md` first, then the pulse and morning-brief skills, `owed-kinds.md`, `shared/home.md`, `engine.md`, `connectors.md`, `safety.md`, `delivery.md`, the round-eleven build log and the round-ten report.
3. **`status`.** All connectors connected. Gmail has `update_draft` but no create-draft tool, so drafts stay in Home (`in_gmail` false). The mock clock read 29 Oct 06:28.
4. **Finding Home.** `schedule list` was empty. `artifact list` gave the Home link.
5. **`engine check`.** Ok, engine 0.7.4.
6. **Reading Home.** 14 snap documents (all version 1), 2 state documents, 60 runs. I wrote `versions.txt` from the 16 result lines and copied `config.json`. What Home held:
   - the 22 Oct note to Aditi (`dr_t_1d7b287123`, three asks), marked sent 22 Oct 10:00;
   - Nimbus already reading "Intro made on 26 Oct";
   - an empty `state/actions`;
   - two waiting promise drafts, to Rahul and to Fatima.
7. **`due`.** Run true, jobs `morning_brief, pulse`, mode daily, window 28 Oct 19:28 (Drive and LPs 28 Oct 06:28), run id `r20261029T0628`.
8. **Run row** created (version 1).
9. **`actions`.** Nothing pending, refused or to check by hand.
10. **Morning-brief reads:**
    - Mail, 7 days: 2 threads, Tara's sent 22 Oct note and Aditi's 26 Oct Nimbus intro.
    - Five searches for a reply from Aditi (Kestrel, Orbit, Aditi, "Founder asks", Nimbus): none.
    - Calendar, 29 Sep to 12 Nov: 4 events, none today or tomorrow.
    - Notes since 28 Oct: none.
    - CRM: deals, companies, people, passes, notes.
11. **CRM against Home.** The same 37 open deals; stage names differ only in capitals. None closed.
12. **`bundle.json` by hand:**
    - 2 threads; the 602-character note was cut to 596 by dropping the sign-off;
    - 4 events and `transcripts: []`;
    - 37 open deals, 49 companies (12 portfolio, 37 pipeline) and 53 people at those companies;
    - 13 notes and 20 passes;
    - `people_partial` and `companies_partial` true, and no `lps` (LP watch is off).

    A check against the reads found no mismatch.
13. **Nothing new to process.** No new notes, pitches or founder updates, so no `extracted`, `inbound`, `kpis`, `asks` or `packs`.
14. **Build (daily).** 8 items, 183 of 350 words, no warnings. Hero "Intro two CFO candidates", 8 days late. Push "Nudge Aditi on Kestrel Pay and Orbit Treasury: no reply since 22 Oct". `owed.json` had 1 entry.
15. **No prep cards,** since there are no meetings today or tomorrow, so no `questions`.
16. **Drafting.** I read the asks' sources (`upd_kestrel`, `upd_orbit`) and six of Tara's threads for her voice, then wrote the nudge into `owed-drafts.json`. With no Gmail create tool there was no drafting mark.
17. **`drafts`.** Wrote `dr_t_1d7b287123_nudge`, refused nothing, and printed the push line "...no reply since 22 Oct. Note ready". The Today row and both heroes switched to "Nudge ready".
18. **Brief check (step 7).**
    - The hero states a fact, and every line has a link.
    - Tara's overdue promises sit above what she waits on.
    - Nothing repeats, and the word count is within the budget.
    - I also checked why the hero's draft was not listed for a rewrite (finding 1).
19. **`db batch`.** Pipeline, people, directory, drafts, brief, asks and portfolio, all to version 2. I finished the run row from `run/home/run.json` (version 2).
20. **Final line:** `Nudge Aditi on Kestrel Pay and Orbit Treasury: no reply since 22 Oct. Note ready` (80 characters).

That was 35 mock calls, and 52 with everything after. None sent mail, saved a Gmail draft, made a calendar hold, wrote to the CRM or made a schedule.

**Bundle comparison, done separately.** I ran `bundle --out compare/bundle_shortcut.json --now 2026-10-29T06:28:00+05:30 --mode daily --after 2026-10-28T19:28:00+05:30`, then built from it against the same pre-run Home.
- **The same:** 2 threads, 4 events, 0 transcripts, 13 notes and 20 passes. Both builds gave the same `brief.md`, the same owed entry, the same push (before `drafts`), and the same pipeline, people, commitments and LPs.
- **Different:** the shortcut reads wider than the Morning brief row.
  - All 45 deals (6 passed, 2 portfolio), 90 companies and 100 people, with no partial flags.
  - The 15 LPs, though Tara's LP watch is off.
  - KPI history for 12 companies, two empathy maps, and firm and thesis.
  - The note kept at 602 characters, plus `snippet` and a message `to`.
- **The only effect:** my partial read rewrote `snap/directory` with the same people in another order, one extra write. Nothing that matters for Tara.

## 2. The pending taps

- **06:28: none.** The 22 Oct note was a morning-brief draft that Tara marked sent in `state/items`, not a tap.
- **07:28: one,** `t_3461c2ec2f_team`. This is "Aditi said yes: ask the team" on Orbit Treasury, tapped at 07:10.
  - I applied it with draft rule 1: a follow-on to a sent note, `note_kind` team.
  - There was no reply from Aditi in mail since `after.at` (06:45), so the draft's context says the yes is not in mail.
  - The draft stays in Home, so it needed no applying mark.
  - `applied.json` was `{"t_3461c2ec2f_team": {"status": "applied"}}`, and `snap/proposals` shows it applied at 07:28.
  - The engine also read two state marks: the nudge sent at 06:45, and Nimbus closed at 06:46.

## 3. The owed entries and their drafts

**One entry: `dr_t_1d7b287123_nudge`.**
- kind `ask_nudge`, `note_kind` nudge, `nudge_of` board;
- `note_draft` `dr_t_1d7b287123`, `sent_on` 2026-10-22;
- `re` "Founder asks: Kestrel Pay, Orbit Treasury, Nimbus Collect";
- `action_ids` `t_1d7b287123_nudge` and `t_3461c2ec2f_nudge`;
- items Kestrel Pay (Neel Bhatt), then Orbit Treasury (Vikram Rao), in the note's order.

Nimbus was left out, since the intro was made on 26 Oct. The engine's context: "No reply since you wrote on 22 Oct: one short nudge on Kestrel Pay and Orbit Treasury. Send it as a reply to your 22 Oct note, so the asks stay in view".

**The reply search (owed-kinds step 1).** The note's thread holds only Tara's message. Aditi's only mail since 22 Oct is the 26 Oct Nimbus intro, which answers neither Kestrel nor Orbit. So I wrote the nudge. Finding 5 is about the step's wording.

**The draft.** It stays in Home (`in_gmail` false). To aditi@quillwater.vc, subject "Re: Founder asks: Kestrel Pay, Orbit Treasury, Nimbus Collect":

```
Hi Aditi,

Thanks for introducing Divya to Raj at Fable Bank on 26 Oct. Two asks from my 22 Oct note still need your call:

1. Kestrel Pay: should we help Neel Bhatt hire two senior backend engineers now, with burn up 43.3% in a month?
2. Orbit Treasury: should we help Vikram Rao hire two senior backend engineers now, with runway under 9 months?

A quick yes or no on each is plenty.

Tara
```

Context: "No reply from Aditi on Kestrel Pay or Orbit Treasury since your 22 Oct note; her only mail since is the Nimbus intro on 26 Oct. Send this as a reply to your 22 Oct note, so the asks stay in view".

Every line comes from a source:
- the 26 Oct intro thread;
- the 22 Oct note;
- the founder updates of 8 and 11 Oct ("senior backend engineers", "the two roles");
- the two flags the note already named.

**Two drafts were already waiting and were not listed** (both from earlier runs):
- `dr_k_e9eab86816` to Rahul, the hero's draft: "...and I will introduce you by Tue 27 Oct." It is now Thu 29 Oct (finding 1).
- `dr_k_45c5b75374` to Fatima: it asks twice for the venue shortlist (finding 7).

## 4. Next-run check

**At 06:40 Tara taps the push.** I used the QA harness's `QA` class at `PHONE` (380 px). It loaded the documents from `evals/runs/nudge-tara/db/` (`{"data", "version"}`), with state passed as `{"items", "actions"}` maps and runs newest first.
- **Opening tab.** Home opens on Today: the hero is 8 days late, which overrides her Portfolio default. The live pill reads "06:28".
- **Hero.** "You promised · 8 days late: Intro two CFO candidates", with Open draft, Sent it, Done and its "Before you send" note. Its draft says "by Tue 27 Oct".
- **Next up, in order:**
  - the guest list for Fatima (Overdue, Draft ready);
  - "2 founder asks wait on Aditi: Your 22 Oct note to Aditi: no answer yet on Kestrel Pay and Orbit Treasury, 5 working days. Nudge ready", with two chips, Nudge ready and Draft ready;
  - the Tallyfin key person;
  - Rahul owes the CTO job description.
- **Below that:** Fatima owes venues, Invite Rahul (no date), and Nimbus ("Intro made on 26 Oct: tap Close ask").
- **The nudge row, opened:** Before you send, Open in Gmail, Sent it, Copy draft, See each ask and Snooze. Open in Gmail is a new message to Aditi with the "Re:" subject, the full body and Tara's authuser.
- **Phone checks pass:** no sideways scroll, one primary button, every control named, no text under 11.5 px, no script errors.
- **Portfolio at 06:42.**
  - The hero reads "Founder asks · one note: 2 founder asks wait on Aditi ... Nudge ready. 1 more open", with Open draft, Sent it and Copy.
  - The Kestrel and Orbit rows read "Nudge to Aditi ready, no reply since 22 Oct". Each offers Close ask, Open in Gmail, Sent it, Copy draft and "Aditi said yes: ask the team".
  - Nimbus offers Close ask.

**The taps:**
- **Sent it on the Today nudge row (06:45).** It writes only `dr_t_1d7b287123_nudge` done, and the toast says "Marked sent". The Portfolio rows then say "Nudged Aditi on 29 Oct". But the Today row still says "Nudge ready", and the Portfolio hero still says "Nudge ready. 1 more open" with only an Open button (finding 2).
- **Close ask on Nimbus (06:46).** It writes only `t_742d2f63d5`, and the row leaves. The hero's "1 more open", which meant Nimbus, stays (finding 2).
- **"Aditi said yes: ask the team" on Orbit (07:10).** It writes `t_3461c2ec2f_team`: draft, `note_kind` team, `next_of` the ask, `after.kind` board, nudged. Orbit then reads "Team note coming at the next check" and "Aditi said yes". Kestrel keeps "Nudged Aditi". Today still says both asks wait on Aditi.
- **Done on the hero (06:50, tried separately).** It writes the row, the promise and its draft. "Send the founder guest list" steps up as the hero.
- **Sent it on Fatima's row (06:55, tried separately).** It writes her draft, the promise and the row. The row leaves.
- **A note on my script.** My first Close ask try wrote nothing, because my locator hit the row itself, whose text says "tap Close ask". The real button works.

**The 07:28 pulse** ran with the first three taps in state:
- **`due` and `actions`.** Jobs `pulse`, window 06:28, run `r20261029T0728`. One pending tap, the Orbit team note.
- **Reads.** No mail since 06:28 and no reply from Aditi. No events today or Friday. No notes. No CRM changes. I wrote the bundle by hand: empty threads, events and transcripts, and `crm.partial` true with no deals.
- **Build** with `--applied` and `--drafts`: 8 items, 187 words, no warnings.
  - The push was "Nothing new", since a tap's draft is not news (by design).
  - The batch wrote brief, pipeline, portfolio, proposals, drafts and asks.
  - I finished the run row. Final line: `Nothing new`.
- **The team note,** `dr_t_3461c2ec2f_team`, goes to all five colleagues: "Aditi, Kabir, Meera, Rohan and Vikram Nair". Vikram Nair is named in full because the founder is Vikram Rao. Subject "Orbit Treasury: senior backend engineers":

```
Hi all,

Vikram Rao at Orbit Treasury asked us for introductions to senior backend engineers, for the two hires they want to make this quarter. I checked with Aditi first (my note of 22 Oct), and she agreed we should help. Do you know someone who fits? Reply to me and I will set up the introduction.

Tara
```

Context: "Aditi's yes comes from your tap at 07:10: it is not in your mail, so check she is happy for the team to be asked. Orbit's runway is left out, since this goes to the whole firm".

**Nothing was lost.** At 07:35 on the phone:
- The hero, Fatima's promise, both waiting items, the Tallyfin flag and the undated invite are all still there.
- Orbit reads "Team note ready ... Aditi said yes on 29 Oct", with Open in Gmail (all five in To), Sent it, Copy draft and Close ask. It is also the Portfolio hero.
- Kestrel reads "Nudged Aditi on 29 Oct" and still offers "Aditi said yes: ask the team".
- Nimbus is done, and both asks record the nudge as sent at 06:45.
- The grouped row is gone, as it should be. The phone checks pass.

## 5. Findings, worst first

1. **The hero's own draft promises a date that has passed (medium; engine and skill text).**
   - The hero, "Intro two CFO candidates", opens a draft that says "I will introduce you by Tue 27 Oct". It is Thu 29 Oct.
   - Instinct suggested that date itself when it rewrote "this week" on 26 Oct. The draft's note still says "The new date is Instinct's suggestion".
   - `_stale_words` (`engine/instinct/cli.py`, about line 2178) only knows relative words: today, tomorrow, this week, next week. So no `redate` entry was listed.
   - Step 6.5 says "A time today or earlier is never left in a draft", but it only covers drafts the engine lists.
   - **Fix:** flag a named day before today in a waiting draft ("by Tue 27 Oct", "on 27 Oct") and list it as `redate`. When `old_context` says the date was Instinct's suggestion, offer the next working day again and say so. Add this case to the `redate` rules in owed-kinds.md.

2. **After Sent it, Today and the Portfolio hero still say "Nudge ready" (medium; Home).**
   - Each Portfolio row turns to "Nudged Aditi on 29 Oct" at once.
   - The Today row keeps its snapshot text ("...5 working days. Nudge ready", status "Nudge ready").
   - The Portfolio hero keeps "Nudge ready. 1 more open" with only an Open button. After Close ask on Nimbus, "1 more open" is wrong too.
   - After "Aditi said yes" on Orbit, Today still says both asks wait on Aditi.
   - This lasts until the next check, up to an hour, in the two places she looks first. She may think the tap failed and send the nudge twice.
   - **Fix:** in `home/index.html`, work out a grouped row's state (`it.group_asks`) with `askSent` and `draftFor`, as `asksCard` does for each ask.
     - Once the group's nudge is marked sent, show "Nudged Aditi on 29 Oct" and drop "Nudge ready".
     - Let the Portfolio hero step aside when its draft is marked sent, as the Today hero does.
     - Count "N more open" from the asks still showing.
     - Add the case to Home QA.

3. **Open in Gmail opens a new message, but the note says to reply in the 22 Oct thread (low; Home and engine).**
   - While the draft stays in Home it cannot be a real reply.
   - The row gives no link to the 22 Oct note: its source chip is a founder update. To follow the advice, she must find the note in Gmail, tap Reply and paste.
   - The row also shows two chips that say the same thing, "Nudge ready" and "Draft ready".
   - **Fix:** give the nudge the sent note's thread as a second link ("Your 22 Oct note"), so she can open it and reply with Copy draft. The thread is known from the mail read (`th_sent_...`) or the ask's `notes`. Drop the draft chip when the status already says ready.

4. **The push names a row, but Home opens on a different hero (low; Home).**
   - The push says "Nudge Aditi ... Note ready". Home opens on Today, whose hero is the Rahul promise, already pushed on 26 and 28 Oct.
   - The nudge is the second row of Next up, closed. It is on Today, as delivery.md asks, but she has to find it.
   - **Fix:** when the morning push names a Today row that is not the hero (`push_item` on the run row), open Today with that row expanded and in view.

5. **The reply test in owed-kinds reads too wide (low; skill text).**
   - `ask_nudge` step 1 counts mail from `to` "in the note's thread, or naming one of the companies" as a reply.
   - Read literally, Aditi's 26 Oct intro names Nimbus Collect, one of the note's companies, so it would stop the nudge for Kestrel and Orbit. The engine got this right: it marked only the Nimbus ask as replied.
   - **Fix:** say "naming one of the companies in `items`". Also say that mail answering another ask on the same note answers only that ask.

6. **An undated promise never joins the waiting email to the same person (low; engine).**
   - "Invite Rahul to the founders dinner" ("next month", so November) shows "No date" every day.
   - A draft to Rahul is already waiting. Fatima's guest-list draft says "I will add Rahul from Tallyfin once he confirms".
   - `owed.json` lists only dated promises, so the invite is never written.
   - **Fix:** when an undated promise that is an email by nature is owed to someone with a waiting draft, list it with `join` on that draft. Then one email to Rahul carries one line about the dinner.

7. **A seeded waiting draft asks for the same thing twice (low; eval harness).**
   - Fatima's draft says "Could you send the venue shortlist when you have it?" and then "Could you also send a shortlist of venues when you have it?".
   - The second line comes from `_ask_owed` in `evals/demo.py`. It looks for "a shortlist of venues" word for word and misses "the venue shortlist".
   - The engine lists no rewrite, so the doubled line reaches Tara's Home.
   - **Fix:** in `_ask_owed`, skip the line when the body already asks for the same thing (by its key nouns, or any "Could you ... send" line). The engine could also flag two lines in a waiting draft that ask for one thing.

8. **The bundle shortcut reads more than a real morning run (low; eval harness).**
   - It reads all deals, people and companies with no partial flags, LPs with LP watch off, KPI history and empathy maps, and keeps a 602-character message.
   - Nothing changed for Tara this time.
   - **Fix:** cut `bundle --mode daily` to the Morning brief row of `shared/connectors.md`.

9. **A Sent it tap leaves no sent mail in the mock mailbox (low; eval harness).**
   - After Tara "sent" the nudge at 06:45, the 07:28 read had no sent message. A real account would have one.
   - It did not matter here, but a reply test after a nudge cannot run end to end.
   - **Fix:** when a seed or QA tap marks a draft sent, add that message to `world_extra.json`, as the seed does for the 22 Oct note.

## 6. Score: 8 out of 10 (as Tara)

**The morning did its main job well:**
- One push named the right thing, in the note's order, and said the nudge was ready. Nimbus was rightly left out because the intro was made.
- The nudge was short, correct and sourced.
- Every tap I would make held: Sent it, Close ask, Done and "Aditi said yes".
- The next hour drafted the team note to the right five people. It left the runway out and said honestly that the yes is not in mail. Nothing was lost.

**Two things cost points:**
- My top card's draft still promises an intro "by Tue 27 Oct", two days ago, and Instinct picked that date.
- Right after I send the nudge, the Today row and the Portfolio hero still tell me a nudge is ready, for up to an hour.

**Smaller things:** Open in Gmail does not open the thread I am told to reply in, and the push lands me on a different hero.

## Round-ten findings

| # | Round-ten finding | Now | Note |
| --- | --- | --- | --- |
| 1 | No way to mark the nudge or the first note sent; Done closes the ask | Fixed | Sent it is on the Today row, each Portfolio row and the Portfolio hero. The ask's tap reads Close ask and writes only the ask. New gap: the row and hero stay "Nudge ready" after Sent it (finding 2) |
| 2 | "No reply" claimed without reading mail | Fixed | owed-kinds step 1 searches first. The engine keeps `replied` on each ask and kept the Nimbus intro to Nimbus. The wording is still too wide (finding 5) |
| 3 | The push and the first hour of Today do not know the nudge is drafted | Fixed | `drafts` rewrote the push to "...Note ready" and turned the row and both heroes to "Nudge ready" |
| 4 | "The same thread" cannot be literal; the entry does not name its note | Partly | The entry has `note_draft`, keeps the note's order, and its context says to reply. Open in Gmail still opens a new message, with no link to the note (finding 3) |
| 5 | Waiting drafts keep stale relative dates | Partly | "this week" became "by Tue 27 Oct" on 26 Oct. That date is now stale and nothing rewrites it (finding 1) |
| 6 | The grouped row describes the note wrongly | Fixed | "Your 22 Oct note to Aditi: no answer yet on Kestrel Pay and Orbit Treasury, 5 working days" |
| 7 | Working days counted by date | Fixed (documented) | delivery.md says a Thursday note is nudged the next Thursday, and the nudge came on Thu 29 Oct |
| 8 | The mock mailbox lacks mail the seeded Home depends on | Fixed | The mock served the 22 Oct note and the 26 Oct intro, and `status` reports the eval clock |

New this round: finding 3's missing link to the note, and findings 2 and 4 to 9.
