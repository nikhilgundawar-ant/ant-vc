<!-- Claude-run eval, round twelve. Written by a Claude agent running the pulse skill against the mock connectors on a clean clone at 947db4c (0.7.5), writing bundle.json by hand in one Write call. Saving this to evals/runs/friday-tara/report.md was refused (subagents return reports as text), so this returned text is the report; saved by the main session. -->

# Eval report: friday-tara (round 12)

The Friday morning run did the right work again, and all three things that let Tara down in round eleven are fixed:
- The dinner invite to Rahul now rides in the CFO email.
- "Sent it" says what happened at once.
- "Got it" clears what others owe her.

The hourly pulse no longer rewrites stage labels either. The worst new finding comes from the dinner-invite fix. Two promises now share one draft, and "Done" on either one closes both. One natural tap can make a late promise to a founder vanish from Home with nothing sent. Score: 8 out of 10.

- Plugin version: 0.7.5 (`plugin.json`, both skills' metadata, and `engine/instinct.py check` all say 0.7.5)
- Commit: `947db4c Round twelve: a note to the partner the work waits on, replies that answer, times true at every hour, Friday sees Monday; version 0.7.5`
- `git status --short`:
  - Clean after checkout, and clean at the end.
  - Python left two git-ignored `__pycache__` folders in the clone, in `engine/instinct/` and `evals/`, when I ran the engine and imported the QA harness from it. I removed them (finding 8).
  - Everything else I wrote is under `evals/runs/friday-tara/`, which git ignores.
- Member: `tara`, Tara Menon, Head of Platform (level `platform`), Quillwater Ventures
- Run: Fri 23 Oct 2026, 06:28 Asia/Kolkata, run id `r20261023T0628`, jobs `morning_brief` and `pulse`, build mode `daily`, every window from Thu 19:28
- Skill: `pulse` steps 1 to 7, with `morning-brief` steps 5 to 7 (and `references/owed-kinds.md`) for the `morning_brief` job

Eval-mode adjustments:
- Skipped pulse step 0 (no guard loads in eval mode).
- Ran the engine from the clone (`python3 -I -S <clone>/engine/instinct.py`) instead of copying it. Work folders: `evals/runs/friday-tara/work/` (06:28) and `work0728/` (07:28).
- Passed `--now 2026-10-23T06:28:00+05:30` to `due`, and `07:28` for the next run.
- Used the mock `db` commands for every Home read and write. The runs read was `db list`, not an ordered query.
- Every connector read went through `mock_connectors.py --as tara` with `INSTINCT_RUN=friday-tara`.
- Wrote each run's `bundle.json` by hand, in one Write call. I copied from compact prints of my own reads to keep my typing honest.
- No question for the user came up, and no connector cards were needed.
- Between the runs I played Tara. Her two "Sent it" taps at 07:05 went into `state/items` with `db update`, exactly as the page wrote them in the QA harness.

## 1. What I ran, in order

Setup:
- Cloned, checked out `947db4c`, confirmed a clean tree.
- `seed_eval.py friday tara`: 14 snapshots, 14 runs, 3 drafts, one tap (`t_3461c2ec2f_team`).
- Read `evals/eval-mode.md`, both skills, `owed-kinds.md` and the five shared docs. I read the round-eleven report only after my 06:28 run, so the run stayed fresh.

The 06:28 run:
1. Connectors:
   - `status`: all nine connected. Gmail lists no `create_draft`, so drafts stay in Home (`in_gmail: false`).
   - `schedule list` shows the two seeded tasks. `artifact list` finds Instinct Home.
2. Step 0 skipped (eval mode).
3. Step 1, load:
   - `db list` saved snap (14 docs), state (2) and runs (14) into `work/home-db`.
   - Wrote `versions.txt` from the 16 result lines, then copied the config.
   - Config: level `platform`, `opens_on: portfolio`. Pipeline, triage and LP watch are off. Portfolio is `asks`. Word budget 350.
4. Step 2: `due` gave `morning_brief, pulse`, a daily build, every window from Thu 19:28 and run id `r20261023T0628`. I created the run row (version 1).
5. Step 3: `actions` gave one pending tap, `t_3461c2ec2f_team` (section 2).
   - Searched mail since 22 Oct: all mail, then "aditi", "orbit", "yes", "hire" and "engineers". The only thread is Tara's own 10:00 note.
   - Read Orbit's founder update `upd_orbit` for the ask's own words.
   - Wrote `drafts.json` and `applied.json` (`applied`). There was no applying mark, because the draft stays in Home.
6. Step 4, the morning-brief windows:
   - Mail, 7 days: 4 threads, each read in full. They were Tara's sent note, a newsletter, Fatima on 16 Oct and Divya on 16 Oct. No pitches and no founder updates.
   - Calendar, 23 Sep to 6 Nov: 5 events, none today or Monday. On Thursday Tara met Rahul at 11:00, then Divya, Pooja and Karthik at 14:30.
   - Notes since Thu 19:28: none. For context only, I listed notes back to 15 Oct once (tr08, tr21). Nothing from that went in the bundle.
   - CRM: 45 deals, 37 of them open. They are the same 37 as in Home's `snap/pipeline`, with equal stages (by meaning), next steps, dates and last contact.
   - CRM, what I kept: 49 of 90 companies (open deals plus portfolio), 13 notes and the 20-entry pass log. Also 55 people: 53 at those companies, plus the two CRM people tagged "CFO candidate" whom the Rahul draft names. People and companies are marked partial.
   - No LP list (LP watch is off).
   - Drive, searched 5 times for what the drafts need (dinner, CFO, guest list, venue, Tallyfin): nothing.
7. Wrote `bundle.json` by hand: 55 KB.
8. Step 5, build (`--mode daily`, with `--applied` and `--drafts`):
   - 9 items, 216 words, no warnings, nothing dropped for lack of a source.
   - Push: "Send the founder guest list: Fatima (Talentbridge), due today. Draft ready" (74 characters).
   - `owed.json`: 2 refresh entries.
   - No prep cards (no meetings today or Monday), so no questions to write.
9. Morning-brief step 6: rewrote both waiting drafts (section 3). `drafts` wrote both, refused none and printed no new push line.
10. Morning-brief step 7, the brief check:
    - The hero states a fact.
    - Every line has a source.
    - The late CFO promise sits above what others owe Tara.
    - No line repeats another.
    - 216 of 350 words.
11. Step 6: `db batch` wrote 8 documents, each to version 2: pipeline, people, portfolio, proposals, directory, asks, drafts and brief. The run row finished at version 2, with `pushed: true` and `push_key: daily:2026-10-23`.
12. Step 7, final line: **Send the founder guest list: Fatima (Talentbridge), due today. Draft ready**

That was 35 mock calls. None sent mail, saved a Gmail draft, changed the CRM or made a calendar hold. The whole eval came to 52 calls: the 06:28 run, my one write of Tara's taps, the 07:28 run and three shortcut calls (one failed, since its output folder did not exist yet). None of them wrote outside Home.

Bundle comparison (afterwards, separately): `bundle --now 2026-10-23T06:28:00+05:30 --mode daily --after 2026-10-22T19:28:00+05:30`.
- What now matches: the partial flags, 49 companies, the 37 open deals, 13 notes, 20 passes, the latest message of each thread, and no LPs.
- What still differs from mine:
  - It cuts Tara's 602-character note at exactly 600 characters, mid-word ("...\n\nTa").
  - It adds `to` and `snippet` to messages, plus `firm` and `thesis`.
  - It leaves out the two CFO candidates I added. Both are in Home's directory anyway.
- Built against the same pre-run Home, both bundles gave the same brief, the same owed entries, the same push and the same documents. The portfolio KPI history differs only in key order. No difference matters.
- The 07:28 pulse shortcut (`--mode pulse --after 06:28`) now sends `partial: true`, as round eleven asked.
  - It counts the 2 portfolio and 6 passed deals as changed, and adds an empty `passes` list.
  - Its build matched mine document for document, so neither matters here.

## 2. The pending taps

`t_3461c2ec2f_team`, "Aditi said yes: ask the team" on Orbit Treasury:
- Tapped Thu 22 Oct 20:45, after the 19:28 check.
- `next_of: t_3461c2ec2f`, after the board note to Aditi Rao (Thu 10:00), with `after.kind: board`.
- Applied by pulse step 3 rule 1 as a team note (`note_kind: team`). Draft id `dr_t_3461c2ec2f_team`, with `action_id: t_3461c2ec2f_team`. Recorded `applied`.
- Aditi's yes is not in mail: the only thread since 22 Oct is Tara's own note. The context says so.
- Aditi is in `to`, since the partner who said yes is included.
- The runway flag is left out, because the whole firm reads the note.
- "Vikram Nair" is in full in `to_name`, because the founder is Vikram Rao.

- To: `aditi@quillwater.vc, kabir@quillwater.vc, meera@quillwater.vc, rohan@quillwater.vc, vikram@quillwater.vc` (to_name "Aditi, Kabir, Meera, Rohan, Vikram Nair")
- Subject: "Orbit Treasury: intros to senior backend engineers"
- Body:

```
Hi all,

Vikram Rao at Orbit Treasury asked in the September update (11 Oct) for introductions to senior backend engineers, to make two hires this quarter. I asked Aditi on 22 Oct, and she agreed we should help. Do you know someone who fits? Send me a name and I will make the introduction.

Tara
```

- Context: "Aditi's yes is your tap on Home: it is not in your mail, so check she is happy for the team to hear it before you send. This goes to the whole firm, so the runway flag is left out."
- Source: Founder update, `https://mail.google.com/mail/u/0/#all/upd_orbit`. Its words: "Ask: any intros to senior backend engineers would help us hire the two this quarter."

## 3. The owed entries and their drafts

### `dr_k_45c5b75374`: the guest list to Fatima (refresh, `named_only`)

The promise: "Send the founder guest list" (`k_45c5b75374`), due today.

Why it came back:
- Thursday's draft was written at 06:28.
- At 14:30 Tara met Divya, Pooja and Karthik ("Founder community: November dinner"), the three people it names. There are no notes from that meeting.
- The entry carried `they_owe`: Fatima's venue shortlist, 3 days late. The draft already asks for it.

What I did:
- Kept the draft word for word, as `owed-kinds.md` says for a named-only refresh with no notes.
- Kept the old context and added the check after it.
- The engine keeps `made_at` when the body is unchanged, but counts `updated_at` as "checked". So the draft will not come back on Monday.

- To: `fatima@talentbridge.in` (Fatima Sheikh)
- Subject: "November founder dinner: guest list"
- Body:

```
Hi Fatima,

As promised, the founder guest list for the November dinner so far:

1. Divya Raman, Nimbus Collect
2. Pooja Malhotra, Mintrail
3. Karthik Subramanian, Harbor Insure Stack

I will add Rahul from Tallyfin once he confirms. Could you send the venue shortlist when you have it?

Tara
```

- Context: "You promised this on 16 Oct, due 23 Oct. Guests from the 22 Oct dinner planning invite. It was written before your 22 Oct meeting with Divya, Pooja and Karthik, which has no notes: check the list still stands before you send."
- Source: Meeting notes, `https://notes.granola.ai/d/tr21`

### `dr_k_e9eab86816`: two CFO candidates to Rahul (refresh, with the dinner invite folded in)

The promise: "Intro two CFO candidates" (`k_e9eab86816`), due 21 Oct, 2 days late.

Why it came back:
- Tara met Rahul at 11:00 on Thursday ("Tallyfin: hiring"). There are no notes.
- The entry now carries:
  - `words: ["this week"]`.
  - `they_owe`: the CTO job description, 4 days late.
  - `also_promises`: "Invite Rahul to the founders dinner" (`k_76e229ee1b`, made 15 Oct, no date).
  - `commitment_ids` for both promises.

What I did:
- Opened with "Good to see you on 22 Oct." and claimed nothing about what was said.
- Replaced Thursday's "this week" with Mon 26 Oct, the next working day, and marked it as Instinct's suggestion.
- Added one line that keeps the dinner promise. "November" is sourced from the "November dinner" invite and Fatima's thread.
- Kept the ask for the job description Rahul owes, and the CRM's two "CFO candidate" names.
- Kept `commitment_ids` on the draft, so both promise rows show "Draft ready".

- To: `rahul@tallyfin.com` (Rahul Sharma)
- Subject: "Tallyfin: two CFO candidates"
- Body:

```
Hi Rahul,

Good to see you on 22 Oct.

As promised, two CFO candidates for Tallyfin: George Thomas and Swati Kulkarni. Both are in our network. Tell me who you would like to meet first, and I will introduce you by Mon 26 Oct.

I would love you to join our founders dinner in November too.

Could you also send the CTO job description when you have it?

Tara
```

- Context: "You promised this on 15 Oct, due 21 Oct. Names from your CRM: the two people tagged CFO candidate. Check each is open to a move before you send. It was written before your 22 Oct meeting, which has no notes: check it still stands, or tap Done if it was settled in the room. Mon 26 Oct is Instinct's suggestion in place of "this week". It also keeps your 15 Oct promise to invite Rahul to the founders dinner."
- Source: Meeting notes, `https://notes.granola.ai/d/tr08`

## 4. Next-run check

How I tested:
- Rendered the Home my run left in the real `home/index.html`, using `evals/home_qa.py` `QA`. I used a copy of `db/` taken right after 06:28.
- Settings: phone width (`PHONE`, 380 px), clock Fri 07:05, member `tara`, state from `db/state`, the last three runs. The harness wrote its files inside my run folder.
- Each tap ran in a fresh page. I decoded each "Open in Gmail" link's `to`, `su` and `body`.
- The common checks passed every time: 125 checks in 25 page states. They cover sideways scroll, one primary button, named controls, text size of at least 11.5 px and script errors.

Opening Home at 07:05:
- It opens on Today, because the push named the hero. Tara's own `opens_on` is Portfolio.
- Hero: "You promised · Send the founder guest list", "Promised to Fatima Sheikh (Talentbridge), due today".
- Hero buttons: Open draft, Sent it, Done, with "Before you send" under them.
- Open draft opens a filled-in Gmail message as `authuser` tara: to Fatima, with the subject and body above.
- Today's list:
  - "No meetings today".
  - Next up: the CFO intro (Overdue, Draft ready), Orbit (Aditi said yes, Draft ready), Tallyfin key person (High), Rahul owes the CTO job description (Waiting on them).
  - Commitments due: Fatima owes the venue shortlist (Waiting on them), Invite Rahul (No date, Draft ready).
  - Founders need: Nimbus (Asked Aditi for the intro), Kestrel (Asked Aditi).
  - Then the Friday score question and Copy brief.
- Portfolio:
  - The hero is Orbit ("Team note ready ... 2 more open"), with Open draft, Sent it and Copy.
  - Then the three asks and five flags: Orbit runway (8.0 months at $200K a month), Ferro revenue 22.6% under plan, Kestrel burn up 43.3%, Tallyfin's CTO leaving, Saffire churn up 3.7 points.

The taps at 07:05 (what the page wrote, and what it showed):
- **Sent it on the hero**: writes `dr_k_45c5b75374`, `k_45c5b75374` and `t_3c090578ee`. The CFO intro steps up as hero, with its draft and checks. Done on the hero writes the same three.
- **Sent it on the CFO row**: writes the draft, both promises (`k_e9eab86816`, `k_76e229ee1b`) and the row. The invite row leaves too, which is right for one email that keeps two promises.
- **Sent it on the invite row**: writes the same draft and both promises. Both rows leave.
- **Done on the invite row**: writes `t_0ddf7373ca`, `k_76e229ee1b` and the shared draft `dr_k_e9eab86816`.
  - The CFO row turns "Overdue · Marked sent 23 Oct", with only Done and Snooze. Tara never sent it.
  - The toast says only "Marked done", with Undo (finding 1).
- **Done on the CFO row**: writes the draft, `k_e9eab86816` and `t_a1afa2bb60`. The invite row at once reads "No date · Marked sent 23 Oct", though no invite went out (finding 1).
- **Orbit row on Today**:
  - Buttons: Close ask, Open in Gmail (all five addresses as a comma list), Sent it, Copy draft and Snooze. "Before you send" shows.
  - Sent it writes only `dr_t_3461c2ec2f_team`.
  - At once, Today's row and the Portfolio row both read "Asked the team on 23 Oct", and the Portfolio hero steps to Nimbus.
  - Sent it on the Portfolio hero does the same.
- **Close ask**:
  - On Kestrel it writes only `t_1d7b287123`. The row leaves, and the hero's "2 more open" becomes "1 more open".
  - On Orbit, the Portfolio hero's own ask, it writes only `t_3461c2ec2f`. Nimbus steps up as "Asked Aditi for the intro on 22 Oct. Divya Raman asked on 13 Oct. 1 more open".
- **Got it**:
  - On "Fatima owes you" it writes `t_79319786ad` and `k_079b94f3db`. On "Rahul owes you" it writes `t_8856f8e461` and `k_083e944f33`. Each row leaves.
  - Both drafts still ask for the thing just received (finding 3).
- **"Aditi said yes: ask the team" on Kestrel**: writes the action `t_1d7b287123_team` (a team note, with `next_of` and `after` set to Aditi at 22 Oct 10:00). The row reads "Team note coming at the next check".
- **Prep sheet**: there is none to open. Tara has no meetings today or Monday, so Sent it in the prep sheet could not be tried on this Home.

Then, as Tara at 07:05, I made the two taps her push and Home point to: Sent it on the guest list (the hero) and Sent it on the Orbit team note. I wrote the page's own writes into `state/items` (version 2), and the mock served both notes as sent mail.

The 07:28 pulse, run for real in `work0728/`:
- `due` gave `pulse`, with a window from 06:28.
  - The `drive` and `lps` windows stay at Thu 19:28, because Tara's runs never read those connectors. That is harmless.
- `actions` had nothing pending. The team-note tap stays applied, so it is not drafted again.
- Mail since 06:28 held Tara's two sent notes. There was nothing from founders of open deals in 7 days, no events to Monday, no notes and no changed deals.
- I wrote the bundle by hand: the two threads, `events: []`, `transcripts: []` and `crm: {partial: true, deals: []}`.
- Result: "Nothing new", 8 items, 205 words.
  - The guest-list promise closed, and the CFO intro is the hero.
  - Orbit reads "Asked the team on 23 Oct", with its note stored at 07:06 IST.
  - The asks hero moved to Nimbus.
- The batch wrote brief, pipeline, people, portfolio, commitments and asks. Drafts were unchanged.
- Stage labels: 0 of 37 changed. The only change in `snap/pipeline` was a `from_home` mark on each deal.

Rendered again at 07:35:
- Today:
  - The hero is the CFO intro (2 days late), with Open draft, Sent it and Done.
  - Orbit reads "Asked the team", with only Close ask.
  - Kestrel and Nimbus still read "Asked Aditi".
- Lost: the invite row no longer shows "Draft ready", Open in Gmail or Sent it, only Done and Snooze (finding 2). The draft is still in Home and still keeps both promises.
- Sent it on the CFO hero now writes the draft and both promises.
- Done on the CFO hero writes the draft and the CFO promise.
- Done on the invite row now writes only the invite. So the same tap on that row means two different things before and after the first pulse.

Dry builds (never written to Home):
- **Done on the invite at 07:05, with no sent mail** (a real account, where Done sends nothing): at 07:28 the CFO intro, 2 days late, closes as done and leaves Home.
- **Done on the CFO intro at 07:05**: at 07:28 the dinner invite closes as `done, sent: true`.
- **Orbit's Sent it stamped `2026-10-22T20:00:00.000Z`** (01:30 IST on 23 Oct): it reads "Asked the team on 23 Oct" and is stored as 01:30+05:30. Round eleven's UTC finding is fixed.
- **The morning build with only the 12 portfolio companies, 15 people and no deals**: the same brief, owed entries and documents as the full read. Only the `from_home` marks in `snap/pipeline` differ (finding 4).

## 5. Findings, worst first

1. **"Done" on one of two promises that share a draft closes both (high; Home and engine).**
   - The problem:
     - The morning folded the undated dinner invite into the CFO email (`commitment_ids`).
     - On a promise row, the page's Done also writes the row's draft id.
     - The engine (`engine/instinct/cli.py` lines 538 to 549, `sent_promise`) reads any draft with a `done_at` as sent, and closes every promise it keeps.
   - What happened:
     - Done on "Invite Rahul to the founders dinner" at 07:05 (say Tara asked him in person) wrote the CFO email's id.
     - The CFO row turned "Marked sent 23 Oct" and lost its draft. At 07:28 the CFO intro, 2 days late, closed and left Home. Nothing was sent.
     - The other way round, Done on the CFO intro closed the dinner invite as sent. Its own context invites that tap: "tap Done if it was settled in the room".
     - The toast's Undo only says "Marked done", so Tara has no clue that the other promise went too.
   - Why it matters: one natural tap makes a late promise to a founder vanish. A chief of staff must never fail this way.
   - Fix:
     - Home: Done writes only its own row and promise, never a draft that keeps another open promise.
     - Engine: close a draft's other promises only on a send. Have Sent it write a send mark (say `sent: true`) that Done does not, and let `sent_promise` require it.
     - Add a replay check: Done on each of two promises that share a draft leaves the other one open, with its draft.

2. **The dinner invite loses its draft link after every pulse (medium; engine).**
   - The problem: `engine/instinct/brief.py` builds undated promise rows (lines 444 to 454) without `draft`. Dated ones get it from `drafts_by_commitment` (line 439). Only the morning's `drafts` command links the undated row.
   - What happened: at 07:05 the row said "Draft ready", with Open in Gmail and Sent it. After the 07:28 pulse it says "No date", with only Done and Snooze, though the draft still keeps the promise.
   - Side effect: finding 1's first path exists only between the morning brief and the first pulse, so Done on that row behaves differently by the hour.
   - Fix: set `draft` on undated rows from `drafts_by_commitment`, as for dated ones. Fix finding 1 first, so Done stays safe.

3. **After "Got it", the drafts still ask for what Tara just got (low to medium; Home and engine).**
   - The problem:
     - Got it on Fatima's venue shortlist leaves the guest-list email asking "Could you send the venue shortlist when you have it?".
     - Got it on Rahul's job description leaves the CFO email asking for it.
   - Fix:
     - Record which line of a draft asks for a `they_owe` promise: its commitment id and the sentence.
     - When that promise is marked Got it, Home drops the line from Open in Gmail and Copy, or shows "Take out the line asking for the venue shortlist" under "Before you send".
     - The next morning's rewrite drops it for good.

4. **The morning brief makes a level with no pipeline hand-type the whole pipeline (low to medium; skill text).**
   - The problem: the Morning brief row in `shared/connectors.md` reads every open deal, with its company and people, at every level. For Tara (pipeline off), that was 37 deals, 37 companies and 40 people. They made up about 35 KB of the 55 KB bundle, typed in one Write call in a scheduled run.
   - Evidence: a dry build with only the portfolio companies and their people, and no deals, gave the same brief, owed entries and documents.
   - Fix: when `modules.pipeline` is off, read deals as the pulse does (`crm.partial: true`, changed ones only). Read companies and people only for the portfolio and the next working day's meetings.

5. **The 50 KB directory is still rewritten when nothing in it changed (low; engine).**
   - Round eleven's finding 11 stands. The 06:28 batch rewrote `snap/directory` to version 2.
   - Every person, company and pass was the same. Only `as_of` and the order of `people` changed.
   - Fix: sort the directory's lists by id, and skip the write when only `as_of` differs.

6. **A shared draft's context reads oddly on its second row (low; skill text).**
   - The problem: the invite row's "Before you send" shows the CFO email's context, which opens "You promised this on 15 Oct, due 21 Oct. Names from your CRM...". That wording is mine, because the rewrite rules say to keep the old context first.
   - Also: step 6's field list for `owed-drafts.json` leaves out `commitment_ids`, which `owed-kinds.md` says to keep. The `drafts` command copes either way.
   - Fix:
     - In `owed-kinds.md`, say that a draft keeping two promises opens its context by naming both ("One email for two promises: the CFO intro and the dinner invite").
     - Add `commitment_ids` to the field list in morning-brief step 6.

7. **The bundle shortcut is close to the documented shape, with small quirks left (low; eval harness).**
   - It cuts at exactly 600 characters, mid-word.
   - It adds `to`, `snippet`, `firm` and `thesis`.
   - In a pulse, it counts passed and portfolio deals as changed, and sends `passes: []`, an empty list that means "read, and nothing there".
   - Neither run's output changed.
   - Fix: cut at the last whole word, compare only open deals, and leave `passes` out of a pulse.

8. **Running the engine from the clone writes bytecode into it (low; eval harness).**
   - `python3 -I -S engine/instinct.py`, and importing `evals/home_qa.py`, wrote `engine/instinct/__pycache__/` and `evals/__pycache__/`. They are git-ignored, but they sit outside the run folder, where eval mode says not to write. I removed them.
   - Fix: say `python3 -B -I -S` in `eval-mode.md`, and set `sys.dont_write_bytecode = True` at the top of `home_qa.py`.

## 6. Score: 8 out of 10 (as Tara)

What went right:
- The push named the one thing due today, with a draft ready, and Home opened right on it.
- The guest list is clean, and it tells me what to check: it was written before I met the three founders it names.
- The CFO email greets Rahul for Thursday's meeting, gives a real date and asks for the job description he owes. It finally invites him to the dinner too, so nothing is left to my memory.
- The Orbit team note went to the right five people. It leaves out the runway figure and says Aditi's yes is not in my mail.
- Sent it works wherever I see a draft, and the page says "Asked the team on 23 Oct" the moment I tap.
- Got it clears what others owe me.
- An hour later nothing I care about was lost, and the dates are right.

What lets me down:
- Say I tap Done on the dinner invite because I asked Rahul in person. My late CFO intro disappears, and Home says I sent an email I never sent.
- Done on the CFO intro quietly closes the dinner invite.
- After the first hourly check, the invite row no longer shows its draft.
- When I tap Got it, my drafts still ask for the thing I just got.

All three of round eleven's letdowns are fixed, which would make this a 9. Finding 1 takes it back to 8. With one tap on the very row the fix created, I can lose a late promise.

## Round-eleven findings

| # | Round-eleven finding | Status | Note |
| --- | --- | --- | --- |
| 1 | Every hourly pulse rewrites the deal stage labels | Fixed | The 07:28 pulse sent `deals: []` with `partial: true`, and 0 of 37 labels changed. The pulse shortcut now sends `partial: true` |
| 2 | After Sent it, old words stay until the next run | Fixed | Today's row and the Portfolio row say "Asked the team on 23 Oct" at once, and the Portfolio hero steps aside |
| 3 | A row for something owed to Tara cannot be cleared | Fixed | "Got it" writes the row and the promise. New: drafts still ask for it (finding 3) |
| 4 | The dinner invite is nobody's draft | Fixed, with new bugs | Folded into the CFO email with `commitment_ids`. New: Done closes both promises (finding 1), and the link goes after a pulse (finding 2) |
| 5 | Tap dates are read in UTC | Fixed | A 01:30 IST tap reads "Asked the team on 23 Oct" |
| 6 | After Close ask, the next hero loses its state | Fixed | Nimbus steps up with "Asked Aditi for the intro on 22 Oct" |
| 7 | Two gaps in the connectors rows | Fixed | Stages are compared by meaning, and on a Friday the morning row reaches Monday |
| 8 | A refresh entry does not mark the stale day | Fixed | Rahul's entry carried `words: ["this week"]` |
| 9 | The seeded draft asks for the shortlist twice | Fixed | It asks once |
| 10 | The bundle shortcut does not keep the documented shape | Partly | Partial flags, open deals, latest messages and no LPs. Small quirks are left (finding 7) |
| 11 | A partial morning read rewrites the directory | Not fixed | Rewritten with no real change (finding 5) |

Files from this eval (all under `/tmp/claude-0/-home-claude/f41ebfd9-0635-5201-96ea-278169523f82/scratchpad/evals-r12/friday-tara/evals/runs/friday-tara/`): `work/` (the 06:28 run: bundle, drafts, owed-drafts, build output), `work0728/` (the 07:28 run), `db_after_0628/` and `db_after_0728/` (Home after each run), `dry_*` (the four dry builds), `compare/` (shortcut bundles and builds), `qa/` (screenshots and tap results), `mock_log.jsonl` (all 52 mock calls).
