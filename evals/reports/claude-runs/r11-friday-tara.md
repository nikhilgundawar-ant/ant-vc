<!-- Claude-run eval, round eleven. Written by a Claude agent running the pulse skill against the mock connectors on a clean clone at be80587 (0.7.4), writing bundle.json by hand in one Write call; saved by the main session (the agent could not write files). -->

# Eval report: friday-tara (round 11)

The morning run did the right work, and the big gap from round ten is closed. Home opened on the item the push named. Every draft was ready, sourced and honest about what to check. "Sent it" worked wherever a draft showed. The next run kept everything. What still lets Tara down is smaller: words that go stale after a tap, rows she cannot clear, and a dinner invite nobody drafts. The worst new finding is hidden from her: every hourly pulse rewrites the firm's deal stage labels. Score: 8 out of 10.

- Plugin version: 0.7.4 (plugin.json, both skills' metadata, and `engine/instinct.py check` all say 0.7.4)
- Commit: `be80587 Round eleven: Sent it wherever a draft shows, replies stop follow-ups, money kept while unpaid, taps that hold; version 0.7.4`
- `git status --short`: clean at checkout and clean at the end (`evals/runs/` is git-ignored)
- Member: `tara`, Tara Menon, Head of Platform (level `platform`), Quillwater Ventures
- Run: Fri 23 Oct 2026, 06:28 Asia/Kolkata, run id `r20261023T0628`, jobs `morning_brief` and `pulse`, build mode `daily`, window from Thu 19:28
- Skill: `pulse` steps 1 to 7, with `morning-brief` steps 5 to 7 for the `morning_brief` job

Eval-mode adjustments:
- Skipped pulse step 0 (no guard loads in eval mode).
- Ran the engine from the clone (`python3 -I -S <clone>/engine/instinct.py`) instead of copying it. Work folder: `evals/runs/friday-tara/work/`.
- Passed `--now 2026-10-23T06:28:00+05:30` to `due` (and `--now 2026-10-23T07:28:00+05:30` for the next run).
- Used the mock `db` commands for every Home read and write. The runs read was `db list`, not an ordered query.
- Every connector read went through `mock_connectors.py --as tara` with `INSTINCT_RUN=friday-tara`.
- Wrote `bundle.json` by hand, in one Write call. Separately, outside the run, a script checked it against the raw reads: every deal, company, person, note, pass and event matched. (A scheduled run could not run that script. It was only there to keep my typing honest.)
- No question for the user came up, and no connector cards were needed.

## 1. What I ran, in order

Setup:
- Cloned, checked out `be80587`, confirmed a clean tree.
- `seed_eval.py friday tara`: 14 snapshots, 14 runs, 3 drafts, one tap (`t_3461c2ec2f_team`).
- Read `evals/eval-mode.md`, the round-ten report, both skills, `owed-kinds.md` and the five shared docs.

The run:
1. `status`: all nine connectors connected. Gmail lists no `create_draft`, so drafts stay in Home (`in_gmail: false`).
2. Step 0 skipped (eval mode).
3. Step 1, load:
   - `artifact list` found Instinct Home.
   - `db list` saved snap (14 docs), state (2) and runs (14) into `work/home-db`.
   - Wrote `versions.txt` from the 16 result lines, then copied the config.
   - Config: level `platform`, `opens_on: portfolio`. Pipeline, triage and LP watch are off. Portfolio is `asks`. Word budget 350.
4. Step 2: `due` gave `morning_brief, pulse`, a daily build, a window from Thu 19:28 for every connector and run id `r20261023T0628`. I created the run row (version 1).
5. Step 3: `actions` gave one pending tap, `t_3461c2ec2f_team` (section 2).
   - Read Orbit's founder update `upd_orbit` for the ask's own words.
   - Searched mail since 22 Oct. The only thread was Tara's own 10:00 note. Aditi has not replied.
   - Checked CRM people: Vikram Rao is Orbit's CEO, and Vikram Nair is the firm's CFO.
   - Wrote `drafts.json` (the team note) and `applied.json` (`applied`). There was no applying mark, because the draft stays in Home.
6. Step 4, the morning-brief windows:
   - Mail, 7 days: 4 threads, all read in full. They were Tara's sent note, a newsletter, Fatima on 16 Oct and Divya on 16 Oct.
   - Calendar, 23 Sep to 6 Nov: 5 events. None is today or Monday.
   - Notes since Thu 19:28: none. Thursday's two meetings have no notes. For context only, I also listed notes back to 14 Oct once.
   - CRM: 45 deals, 37 of them open. That matches the 37 in Home, so no closed-deal records were needed. I kept 49 of 90 companies (open deals plus portfolio), 53 of 100 people (at those companies, with no meetings today or Monday), 13 notes and the 20-entry pass log.
   - No LPs (LP watch is off) and no Drive.
   - Nothing new to extract: no notes, pitches or founder updates.
7. Wrote `bundle.json` by hand, in one Write call, with people and companies marked partial.
8. Step 5, build (`--mode daily`, with `--applied` and `--drafts`):
   - 9 items, 216 words, no warnings, nothing dropped for lack of a source.
   - Push: "Send the founder guest list: Fatima (Talentbridge), due today. Draft ready" (74 characters).
   - `owed.json`: 2 refresh entries.
   - No prep cards (no meetings today or Monday), so no questions to write.
9. Morning-brief step 6:
   - Read `tr21` and `tr08`, the notes both drafts cite.
   - Rewrote both drafts (section 3).
   - `drafts` wrote both and refused none. It printed no new push line.
10. Morning-brief step 7, the brief check:
    - The hero states a fact.
    - Every line has a source.
    - The overdue CFO promise sits above what others owe Tara.
    - No line repeats another.
    - 216 of 350 words.
11. Step 6: `db batch` wrote 8 documents, each to version 2: pipeline, people, portfolio, proposals, directory, asks, drafts and brief. The run row finished at version 2, with `pushed: true` and `push_key: daily:2026-10-23`.
12. Step 7, final line: **Send the founder guest list: Fatima (Talentbridge), due today. Draft ready**

That was 25 mock calls. None sent mail, saved a Gmail draft, changed the CRM or made a calendar hold. The 07:28 run and two shortcut calls later brought the log to 39 calls, and none of those wrote outside Home either.

Bundle comparison (afterwards, separately): `bundle --now 2026-10-23T06:28:00+05:30 --mode daily --after 2026-10-22T19:28:00+05:30`.
- The shortcut differs from mine in these ways:
  - It keeps both messages of the Fatima and Divya threads.
  - It keeps the 602-character note whole (the bundle rule is 600).
  - It adds 15 LPs, though LP watch is off.
  - It adds old `portfolio_kpis`, `firm` and `thesis`.
  - It sends the whole CRM (90 companies, all 45 deals including passed and portfolio ones, 100 people) with no partial flags.
- I built both against the same pre-run Home. The result was the same brief, the same owed entries field for field, the same push and the same documents. The one exception: my partial read also rewrote `snap/directory`, which was unchanged apart from its `as_of`.
- No difference matters for this Friday run. One matters for a pulse: the pulse shortcut sends every deal with no partial flag, and that hides finding 1.

## 2. The pending taps

`t_3461c2ec2f_team`, "Aditi said yes: ask the team" on Orbit Treasury:
- Tapped Thu 22 Oct 20:45, after the 19:28 check.
- `next_of: t_3461c2ec2f`, after the board note to Aditi Rao (Thu 10:00).
- Applied by pulse step 3 rule 1 as a team note (`note_kind: team`).
- Draft id `dr_t_3461c2ec2f_team`, with `action_id: t_3461c2ec2f_team`.
- Recorded `applied`. Proposals shows it applied at 06:28.
- Aditi is in `to`, since the skill now says the partner who said yes is included.
- The runway flag is left out, because the whole firm reads the note.
- "Vikram Nair" is in full in `to_name`, because the founder is Vikram Rao.

- To: `aditi@quillwater.vc, kabir@quillwater.vc, meera@quillwater.vc, rohan@quillwater.vc, vikram@quillwater.vc` (to_name "Aditi, Kabir, Meera, Rohan and Vikram Nair")
- Subject: "Orbit Treasury: intros to senior backend engineers"
- Body:

```
Hi all,

Vikram Rao at Orbit Treasury asked in their September update for introductions to senior backend engineers, to help them make two hires this quarter. I asked Aditi about it on 22 Oct, and she agreed we should help. Do you know someone who fits? Send me names and I will make the introductions.

Tara
```

- Context: "Aditi's yes is not in your mail: you marked it in Home on 22 Oct at 20:45, so check she agreed before you send. Orbit's runway flag is left out, since the whole firm reads this."
- Source: Founder update, `https://mail.google.com/mail/u/0/#all/upd_orbit`

## 3. The owed entries and their drafts

### `dr_k_45c5b75374`: the guest list to Fatima (refresh, `named_only`)

The promise: "Send the founder guest list" (`k_45c5b75374`), due today.

Why it came back: Thursday's draft was written at 06:28. At 14:30 Tara met Divya, Pooja and Karthik ("Founder community: November dinner"), the three people it names. There are no notes from that meeting.

What I did:
- Kept the greeting and the list.
- Removed a repeated line. Thursday's seeded draft asked for the venue shortlist twice (finding 9).
- Kept "I will add Rahul from Tallyfin once he confirms", since Tara's own 15 Oct words promise him an invite. Context now says he is not invited yet.
- Kept the old checks and added the refresh check.

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

- Context: "You promised this on 16 Oct, due 23 Oct. Guests from the 22 Oct dinner planning invite. Written before your 22 Oct meeting with Divya, Pooja and Karthik, whom it names, which has no notes: check it still stands. Rahul is not invited yet: your 15 Oct promise to invite him is still open."
- Source: Meeting notes, `https://notes.granola.ai/d/tr21`

### `dr_k_e9eab86816`: two CFO candidates to Rahul (refresh)

The promise: "Intro two CFO candidates" (`k_e9eab86816`), due 21 Oct, 2 days late.

Why it came back: Tara met Rahul at 11:00 on Thursday ("Tallyfin: hiring"). There are no notes.

What I did:
- Opened with "Good to see you on 22 Oct." and claimed nothing about what was said.
- Replaced Thursday's "this week" with Mon 26 Oct, the next working day, and marked it as Instinct's suggestion.
- Kept the ask for the CTO job description Rahul owes.
- The names are the two CRM people tagged "CFO candidate".

- To: `rahul@tallyfin.com` (Rahul Sharma)
- Subject: "Tallyfin: two CFO candidates"
- Body:

```
Hi Rahul,

Good to see you on 22 Oct. As promised, two CFO candidates for Tallyfin: George Thomas and Swati Kulkarni. Both are in our network. Tell me who you would like to meet first, and I will introduce you by Mon 26 Oct.

Could you also send the CTO job description when you have it?

Tara
```

- Context: "You promised this on 15 Oct, due 21 Oct. Names from your CRM: the two people tagged CFO candidate. Check each is open to a move before you send. Written before your 22 Oct meeting, which has no notes: check it still stands, or tap Done if it was settled in the room. Mon 26 Oct is Instinct's suggestion in place of "this week"."
- Source: Meeting notes, `https://notes.granola.ai/d/tr08`

## 4. Next-run check

How I tested:
- Rendered the Home my run left (a copy of `db/` taken right after 06:28) in the real `home/index.html`, using `evals/home_qa.py` `QA`.
- Phone width (`PHONE`, 380 px), clock Fri 07:05, member `tara`, state from `db/state`, the last three runs.
- Each tap ran in a fresh page.
- The harness's common checks passed in every scenario: no sideways scroll, one primary button, every control named, no text under 11.5 px, no script errors.

Opening Home:
- It opens on Today (tabs: Today, People, Portfolio).
- Hero: "You promised · Send the founder guest list", "Promised to Fatima Sheikh (Talentbridge), due today".
- Hero buttons: Open draft, Sent it, Done, with "Before you send" under them.
- Open draft opens a filled-in Gmail message: to Fatima, the subject and the body above, as `authuser` tara.
- Today's list:
  - "No meetings today".
  - Next up: the CFO intro (Overdue, Draft ready), Orbit (Aditi said yes, Draft ready), Tallyfin key person (High), Rahul owes the CTO job description (Waiting on them).
  - Commitments due: Fatima owes the venue shortlist (Waiting on them), Invite Rahul (No date).
  - Founders need: Nimbus (Asked Aditi for the intro), Kestrel (Asked Aditi).
  - Then the Friday score question.
  - No "Ready for you" section, since every draft sits on a row or the hero.

The taps:
- **Sent it on the hero**: marks the draft, the promise and the row sent (`dr_k_45c5b75374`, `k_45c5b75374`, `t_3c090578ee`). The CFO intro steps up as hero, with its own draft and checks.
- **Done on the hero**: writes the same three ids. The CFO intro steps up.
- **Orbit row on Today**:
  - Buttons: Close ask, Open in Gmail (all five addresses as a comma list), Sent it, Copy draft and Snooze. "Before you send" shows.
  - Sent it writes only `dr_t_3461c2ec2f_team`.
  - Afterwards the Today row still says "Team note ready".
  - On Portfolio the same ask now reads "Asked the team on 23 Oct", but the Portfolio hero above it still says "Team note ready" with only an Open button (finding 2).
- **Sent it on the Portfolio hero**: the same single write, and the same stale hero.
- **CFO row**:
  - Buttons: Done, Open in Gmail, Sent it, Copy draft.
  - Sent it writes the draft, the promise and the row (`t_a1afa2bb60`), and the row leaves.
  - Rahul's CTO job description row and the invite row stay.
- **Portfolio**:
  - The hero is Orbit, with Open draft, Sent it and Copy.
  - Kestrel offers Close ask and "Aditi said yes: ask the team".
  - Nimbus offers Close ask.
- **Close ask**:
  - On Kestrel it writes only `t_1d7b287123`, and the row leaves.
  - On Orbit, the hero's own ask, it writes only `t_3461c2ec2f`. Orbit leaves Portfolio and Today, and the hero steps to Nimbus. The new hero's line drops "Asked Aditi for the intro on 22 Oct" (finding 6).
- **Done on a row**: "Invite Rahul to the founders dinner" writes its row and promise, then leaves. The two "owes you" rows offer only Snooze (finding 3).
- **Prep sheet**: there is none to open. Tara has no meetings today or Monday, so Sent it in the prep sheet could not be tried on this Home.

The 07:28 pulse, run for real in its own work folder:
- `due` gave `pulse`, with a window from 06:28.
- `actions` had nothing pending. The team-note tap is recorded as applied, so it is not drafted again.
- No new mail, events or notes, and no changed deals. (Comparing deals by hand flagged 21 stage "changes" that were only upper and lower case.)
- I wrote the bundle by hand and built it.
- Result: "Nothing new", 9 items, 216 words. The batch wrote brief and pipeline only. Drafts, asks and commitments were unchanged.
- Rendered again at 07:35: Home and every tap gave the same result as at 07:05 (tap times aside).
- One hidden change: every deal stage label in `snap/pipeline` degraded (finding 1).

The 07:28 build with Tara's two most likely taps folded in (Sent it on the guest list and on the Orbit note at 07:05). This was a dry build and was not written:
- The CFO intro becomes the hero.
- Orbit reads "Asked the team on 23 Oct", and its notes gain the team note.
- The Portfolio hero moves on to Nimbus.
- The guest-list promise closes.
- The push stays quiet.
- The same tap made at 01:30 IST reads "Asked the team on 22 Oct" (finding 5).

## 5. Findings, worst first

1. **Every hourly pulse rewrites the firm's deal stage labels (medium; engine and eval harness).**
   - The problem: `engine/instinct/cli.py` line 142 rebuilds each deal it takes from Home with `"stage": d.get("stage_key") or d.get("stage")`. The engine's key replaces the CRM's label.
   - What happened: at 07:28, 24 of 37 deals changed in `snap/pipeline`. "IC" became "Partner_meeting", "Due diligence" became "Diligence", "Term sheet" became "Term_sheet" and "First meeting" became "First_meeting".
   - Who sees it: the morning's full read puts the labels back, so from the second run of each day they are wrong. Tara does not see this, because her Pipeline tab is off. Partners and associates do: the prep card's stage line and the partner line they copy into chat both print it.
   - Why the harness missed it: the pulse shortcut sends all 45 deals with no partial flag, so replays never take this path.
   - Fix:
     - Rebuild with `d.get("stage") or d.get("stage_key")`.
     - Keep the CRM's own label in `snap/pipeline`.
     - Make the pulse shortcut send only changed deals with `partial: true`.
     - Add a replay check where a pulse sends `deals: []`.
2. **After Sent it, the run's old words stay until the next run (medium; Home).**
   - The problem: once the Orbit note is marked sent, the Portfolio row says "Asked the team on 23 Oct". But the Portfolio hero above it keeps "Team note ready. Aditi said yes on 22 Oct..." with only an Open button, and Today's row also still says "Team note ready".
   - Why it matters: once the 10-second toast is gone, Tara cannot tell at a glance that her tap took.
   - Fix: when a draft is marked sent, build the ask's line from the page's own sent mark everywhere (Today's row and the asks hero), as the Portfolio row already does. Or step the hero aside, as Close ask does.
3. **A row for something owed to Tara cannot be cleared by hand (low to medium; engine and Home).**
   - The problem: Fatima's venue shortlist (3 days late) and Rahul's CTO job description (4 days late) offer only Snooze. If the shortlist comes on WhatsApp or in person, the row stays on Today, overdue, until a reply shows up in mail.
   - Fix: offer "Got it" on these rows, writing the commitment's id, as Done does on Tara's own promises.
4. **The dinner invite to Rahul is still nobody's draft (low to medium; engine).**
   - The problem: the promise has no date, so it never enters `owed.json`. Its row offers Done and Snooze, but no "Draft a note". Meanwhile the guest list tells Fatima "I will add Rahul from Tallyfin once he confirms". I flagged this by hand in the guest list's context.
   - Fix: fold an undated email-type promise into the waiting draft to the same person. The CFO email to Rahul is the natural place, as one email per person. Or offer "Draft a note" on the row. Count "invite" as an email verb.
5. **Tap dates are read in UTC (low; engine).**
   - The problem: the page writes `done_at` in UTC ("2026-10-23T01:35:00.000Z"), and `engine/instinct/brief.py` takes `at.date()` and `fmt_short_date(at)` without the user's time zone. A Sent it at 01:30 IST on 23 Oct reads "Asked the team on 22 Oct", and the five-working-day nudge clock starts a day early.
   - Fix: convert to the time zone in `snap/config` before taking the date.
6. **After Close ask on the Portfolio hero's ask, the next hero loses its state (low; Home).**
   - The problem: Nimbus steps up as "Divya Raman asked on 13 Oct. 1 more open", without the "Asked Aditi for the intro on 22 Oct" that its own row shows.
   - Fix: build the stepped-up hero's line from that row's own line.
7. **Two small gaps in the connectors rows (low; skill text).**
   - The pulse row says to compare open deals with Home's `snap/pipeline` by stage. But Home stores the engine's casing ("First meeting") where the CRM says "First Meeting", so a literal comparison flags 21 false changes. Fix: say "compare stages by meaning, ignoring case", or let the engine compare.
   - The morning-brief row reads CRM people "at today's and tomorrow's meetings". On a Friday that should be the next working day (Monday), as step 5 says for prep cards.
8. **A refresh entry does not mark the stale day in its body (low; engine).**
   - The problem: the CFO draft still said "this week" from Thursday. The entry was `refresh` with no `words`, so the run had to spot the stale day itself. `owed-kinds.md` does say to do so.
   - Fix: add `words` to a refresh entry whose body names a day that has come or gone, as a `redate` entry has.
9. **The seeded guest-list draft asks for the venue shortlist twice (low; eval harness).**
   - The problem: `evals/demo.py` `_ask_owed` looks for "a shortlist of venues" and misses the reworded "the venue shortlist". A real Thursday run would not write this. Friday's rewrite removed it.
   - Fix: match the ask by its key words, or skip when the body already asks.
10. **The bundle shortcut does not keep the documented bundle shape (low; eval harness).**
    - The problem: it keeps every message of a thread and a 602-character message. It includes LPs with LP watch off and old `portfolio_kpis`. It sends the whole CRM with no partial flags in the morning, and every deal with no partial flag in a pulse.
    - Friday's output did not change, but it hides finding 1.
    - Fix: shape the shortcut by the rows in `shared/connectors.md`.
11. **A partial morning read rewrites the 50 KB directory when only its date changed (low; engine).**
    - Fix: skip the write when `snap/directory` is unchanged apart from `as_of`.

## 6. Score: 8 out of 10 (as Tara)

What went right:
- The push named the one thing due today, with a draft ready, and Home opened right on it.
- The guest list is clean, and it tells me what to check: it was written before I met the three founders, and Rahul is not invited yet.
- The CFO email greets Rahul for Thursday's meeting, gives a real date and asks for the job description he owes.
- The Orbit team note went to the right five people, left out the runway figure and says Aditi's yes is not in my mail.
- Sent it works wherever I see a draft. The next run turns it into "Asked the team on 23 Oct". Nothing was lost an hour later.

What lets me down:
- After I send the Orbit note, the hero still says "Team note ready" for up to an hour.
- I cannot clear "Fatima owes you" when the shortlist arrives on WhatsApp.
- Inviting Rahul to the dinner is still left to my memory, while my own guest list tells Fatima I will add him.

The stage-label bug does not touch my Home, so it does not cost my score. It is still the worst product finding.

## Round-ten findings

| # | Round-ten finding | Status | Note |
| --- | --- | --- | --- |
| 1 | No way to mark a draft sent on a row or the hero | Fixed | Sent it on the hero, Today rows and Portfolio rows. It writes the draft id (and the promise's), never the ask's. The ask stays open as "Asked the team on 23 Oct". The prep sheet was not testable (no meetings) |
| 2 | Refresh says "which has no notes" when an earlier run read them | Not exercised | Thursday's meetings truly have no notes. Home now keeps a notes map by meeting in `snap/commitments` |
| 3 | Done on the hero leaves "Nothing urgent"; the Portfolio hero ignores Done | Fixed | The next line steps up, and Close ask moves the Portfolio hero on. New: old words after Sent it (finding 2) |
| 4 | Push names Today's hero, but Home opens on Portfolio | Fixed | A pushed hero opens Today |
| 5 | Hero draft not checked after meetings with people it names | Fixed | The guest list came back as a `named_only` refresh with a check |
| 6 | Refresh rules collide on an old "this week" | Fixed | Skill text now says next working day, marked as Instinct's suggestion. The engine still does not flag it (finding 8) |
| 7 | Drafts to someone who owes the user do not ask; the invite is never drafted | Partly | Drafts now ask. The invite is still never drafted (finding 4) |
| 8 | Unclear whether a team note includes the partner who agreed | Fixed | Pulse step 3 rule 1 says so |
| 9 | Runway copy reads as Aditi's approval; the warm-path line stays | Fixed | "Aditi said yes on 22 Oct. Runway under 9 months", and no warm-path line on Orbit |
| 10 | Bundle shortcut returns Thursday 07:00 and the whole world | Partly | It now takes `--now`, `--mode` and `--after`, but still sends the whole CRM, LPs and every deal in a pulse (finding 10) |
| 11 | Seeded Home contradicts its own state | Fixed | Taps sit at their times. New: a duplicated ask in a seeded draft (finding 9) |
| 12 | Shared scratchpad | Fixed | This eval had its own clone and run folder |
