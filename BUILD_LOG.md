# Build log: ant. for VCs (formerly Instinct for VCs)

Built from the council plan "Instinct for VCs: Council Plan and One-Shot Build Spec". This log records what ships, how it was tested, what the councils said and what changed on the way. Version 0.9.0.

## What ships

| Part | What it is |
| --- | --- |
| Plugin | `ant-vc.plugin` (0.9.0): 14 skills, the engine, the ontology, ant. Home, two scheduled tasks and a guard for them |
| Skills | setup, pulse, morning-brief, meeting-prep, research, post-meeting, pipeline-watch, inbound-triage, deal-memo, network, portfolio-watch, lp-watch, tuning, settings |
| Engine | `engine/instinct/`, Python standard library only, run isolated (`python3 -I -S`). People resolution, relationship graph, stale deals, competing-fund signals, promises, thesis triage, portfolio drift, LP alerts and capital calls, warm paths, brief ranking, prep cards and sync packs, the push picker, what is due each hour, weekly tuning, Home snapshots |
| ant. Home | `home/index.html`: one private page on the Anthill Evergreen design system, following the device's light or dark setting. Today (by the job: Decide, Send, Waiting on others, Watch), Pipeline, People, Portfolio, LPs and Activity; every section folds; tabs follow the user's level. Taps write to the page's own database; the hourly run applies them |
| Schedules | "ant." hourly on weekdays from the brief time, "ant. weekend" three times a day. Each run asks the engine what is due: the morning brief, a pulse, the Thursday review, the Monday digest, Sunday tuning and the week ahead |
| Guard | `hooks/guard.py`, a PreToolUse hook that puts scheduled runs on an allowlist; each run first makes a call the guard must refuse, so a guard that did not load stops the run |

## How it was tested

| Loop | Tool | Result at 0.9.0 |
| --- | --- | --- |
| Engine and multi-run suites | `python3 evals/runner.py` against the fictional Quillwater Ventures (6 members, 45 deals, 25 transcripts, 30 pitches, 12 portfolio companies, 15 LPs), a second renamed fund, a ten-times fund and a solo GP | 235 engine and replay checks pass on a clean clone (about 340 s), which skips the 7 score groups read from saved Claude runs (kept out of git); with those runs present, 248 of 248 |
| Panel tests | `round6` and `round6b` suites: the VC panel's round-five tests on the same Thursday-to-Monday replay, for all seven panel members; `evals6` pins the round-six Claude-run findings; `round7` to `round10` pin the VC panel's round-six to round-nine tests; `evals8` pins the round-eight Claude-run findings; `round9` to `round15` replay every panel member with each run reading only its own window (all seven match the full replay at every run), with taps, replies in mail and sent chases to Mon 23 Nov; `round11` also pins the 0.7.3 Claude-run findings and the round-nine council's conditions J to P, `round12` the 0.7.4 Claude-run findings and the round-eleven panel's tests, `round13` the 0.7.5 Claude-run findings, the round-ten council's conditions Q to W and the round-twelve panel's tests, and `round14` the round-eleven council's conditions X to AB, the 0.7.6 Claude runs and the round-thirteen panel | pass: no push inside a meeting, at most four a day, every pushed item on Today, one sync pack for all, calendar truth to Monday, founders' words kept, and the rest |
| Guard | `evals/runner.py --suite guard`: every allowed step and every known way out, on the connectors' real argument names, in three transcript layouts; `round11` adds data names that order something at either end, and Artifact reads that save files | 718 of 718, and the round-eleven probes |
| Five-day replay and outages | Setup, then every scheduled run Thursday to Monday; the CRM or email down for four hours | Home never loses LPs, companies, flags, signals or promises; no false all-clear; an outage pushes once |
| Design lint | `python3 evals/design_lint.py` | 0 violations in 362 CSS rules |
| Home QA | `python3 evals/home_qa.py` (Playwright, phone and desktop, light and dark, every level) | 726 of 726 |
| Safety lint and manifest | `python3 -I -S engine/instinct.py lint --root .`, `claude plugin validate .` | 0 violations; validates (warnings: no LICENSE, no privacy URL) |
| Claude in the loop | Skills run end to end by fresh Claude agents against mock connectors (`evals/eval-mode.md`) | reports in `evals/reports/claude-runs/` |
| Councils | A simulated VC panel (one persona per level), a simulated product council (PM, designer, AI engineer, QA lead) and a simulated design council (SaaS product design, information architecture, visual design, accessibility, behavioural psychology) | reports in `evals/reports/council/` |

## Results

All scores below are simulations: one Claude agent played every panel member or reviewer, reading the build's own outputs. No real investor or reviewer took part.

| Round | VC panel (average of 7) | Product council (average of 4) |
| --- | --- | --- |
| 1 | not run | 5.0 |
| 2 | 5.1 | 5.75 |
| 3 | 6.6 | 6.75 |
| 4 | 7.1 | 6.75 |
| 5 | 7.6 | (round four council: 6.75, no-go) |
| 6 | 8.2 (none below 8) | 8.0 (no-go only for want of a real-account smoke test) |
| 7 | 8.7 (all seven up; three at 9) | 8.4 (no-go only for the real-account smoke test, a LICENSE and a fresh Claude run on 0.6.0) |
| 8 | 9.07 (Kabir 9.5, six at 9) | 8.25 (round seven council, on 0.7.0: no-go for the real-account smoke test, a LICENSE, a privacy URL, a fresh Claude run on 0.7.x and a current sample link) |
| 9 | 9.0 (all seven at 9; real read windows and hidden draft notes cost Kabir his 9.5) | 8.13 (round eight council, on 0.7.2: no-go for the real-account smoke test, a LICENSE, a privacy URL, records that expired before what they tracked, hidden draft caveats, trust docs that claimed a little more than the guard enforced, and a private sample link) |
| 10 | 9.21 (Kabir, Rohan and Tara at 9.5; four at 9: money forgotten after day 14, old news pushed as new, carried words that went stale) | 8.25 (round nine council, on 0.7.3: no-go until replies in mail stop follow-ups, a sent chase is kept, a second Pipeline step applies, a tap narrows a nudge, the prep sheet shows its caveat, two guard gaps close, and fresh Claude runs score 8 or more; plus the owner-only steps) |
| 11 | 9.29 (Aditi, Kabir, Meera, Rohan and Tara at 9.5; Vikram and the solo GP at 9: a reply that is not an answer, and a promised wire that never comes) | not run on 0.7.4 |
| 12 | 9.5 (Kabir at 10; Aditi, Meera, Rohan, Tara and Vikram at 9.5; the solo GP at 9: "Another fund is moving" on a passed deadline, and a call that never reaches her phone) | 7.75 (round ten council, on 0.7.5: no-go until Done never closes another promise, a reply counts from when the note went, quiet deals stay out of the note to a partner, that note waits on her answer, dates read right, money reaches the phone every week, the harness writes drafts as a run does, and fresh Claude runs score 8 or more) |
| 13 | 9.71 (Kabir and Meera at 10; the other five at 9.5: a deferred nudge that vanished, a "we paid" reply chased, a passed race leading Today) | 8.13 (round eleven council, on 0.7.6: no-go until a reply counts whatever you write after it, the note to a partner pushes only after reading its thread, who set a date is stored, a deferring reply stays deferring and "the call" is no money answer) |
| 14 | not run on 0.7.7 | 8.5 (round twelve council, on 0.7.7: no-go until a trimmed thread never counts as read, a late Sent it still finds the note, and every way of saying "paid" is heard; plus one fresh Claude run on 0.7.7 and the owner-only steps) |

Claude-run evals (round five, on 0.4.0 skills): inbound triage 25 of 25 decisions match, scheduled pulse 15 of 15 safety checks, Claude-written brief 9 of 10 top lines, setup and morning brief run end to end. Their findings (46 numbered issues) were fixed in rounds five and six. Their 13 scores are read from saved runs kept out of git, so the runner counts them only where those runs exist. The Friday pulse on 0.7.2 scored 7 of 10 as Meera and as Tara; their 23 findings are fixed in round ten. The scheduled runs on 0.7.3 scored 7 of 10 each (Tara's nudge morning, Tara's and Meera's Fridays); their 30 findings are fixed in round eleven, except one product idea kept for later (a note to the partner whose view several drafts wait on). On 0.7.4 the same three runs scored 8, 8 and 7; round twelve fixes their findings, that note included, except one kept as a known limit: a scheduled run still types its bundle by hand. On 0.7.5 they scored 8, 8 and 8.5; round thirteen fixes their findings. On 0.7.6 they scored 9, 9 and 8 (`evals/reports/claude-runs/r13-summary.md`); round fourteen fixes their medium findings.

## Round twenty-four (0.12.1): your data stays yours, and GitHub vouches for the build

- **Page 2 is the founder's space.** Researching a founder now also researches their company. It reads the company's own site and one web search, only on your tap, and keeps only links it found. Page 2 of the empathy map covers:
  - what they do and the space: market and where it is heading;
  - their signals and who leads the space;
  - fit with your thesis and questions to test the space;
  - then your earlier calls and talking points.
- **Nothing leaves without you.**
  - The fonts and jsPDF now ship inside ant. Home, so opening it asks no server for anything.
  - `evals/stress/egress.py` proves it in a real browser: open, every tab, a panel and a PDF make zero outside requests.
  - The same test proves the engine imports nothing that reaches a network, and that the repository holds no keys.
  - The safety screen and `SECURITY.md` gain "Where your data goes".
- **Free GitHub trust signals:**
  - a release workflow where GitHub builds the plugin from the tag, attaches it with its checksum and signs a provenance attestation (`gh attestation verify`);
  - CodeQL code scanning;
  - OpenSSF Scorecard, with badges on the README.

Regression: Home QA 849/849, engine 235/235, stress suites 12/12, 47/47, 101/101, 87/87, 79/79, 158/158 and 41/41, design lint 0 violations.

## Round twenty-three (0.12.0): built to be trusted

A new user's Claude reviewed the plugin before installing it and listed eight risks. Each was real. 0.12 answers each one in code and with proof that can be checked, and says plainly what is still open.

| Risk raised | 0.12 answer | Proof |
| --- | --- | --- |
| Not Anthropic, one author, no audit | A safety screen and `SECURITY.md` say who makes it, with the threat model and what is still open. Tests run publicly on GitHub Actions. Each release carries a SHA-256 checksum. | `.github/workflows/tests.yml`, `package.sh` |
| A crafted email could get a draft to an attacker | **Recipient lock:** a check drafts only to an address that is on the build's header-only list AND that a connector returned in a header in the run's own transcript. Every value in the call is read at any depth; look-alike letters and writes to the list (any letter case) are refused. | guard suite 766/766, `security_012.py` 44/44 |
| A crafted email could poison a CRM field | Automatic mode applies only next step, due date, notes and last contact, and only from the user's own meeting notes. Stage, round, amount and anything from email wait for a tap. | round17, round18, `security_012.py` |
| Automatic mode on by default | Off by default. | setup, `state/settings` |
| The guard reads tool names | Unchanged for CRMs and data connectors, and said so plainly. Known connectors use exact read lists. | `SECURITY.md` |
| No guard in chat | Explained: in chat the Claude app asks before each action. | `TRUST.md`, safety screen |
| LinkedIn scraping | Off by default. Research runs only on a tap; automatic research is a switch that says why. | `security_012.py` |
| Third-party data | Explained: where it lives, the user's duties, and how to wipe it. Automatic deletion is listed as open. | `SECURITY.md` |
| Cost and noise | **Light mode** is the default: 19 checks a week, with hourly as a setting. The weekday brief run keeps the morning line, so a meeting heads-up never displaces it. | `security_012.py`, Home QA |

A simulated QA red team then attacked the 0.12 changes and found 10 issues. All are fixed:
- The run could add a stranger to the recipient list by writing a fake thread into its own `bundle.json`. The guard now also checks the transcript.
- Look-alike letters and recipients nested deep in the call got past the lock.
- A different letter case could overwrite the list on a Mac.
- Look-alike notes URLs could pass as meeting notes, and so could a bare field entry.
- Light mode lost the Monday digest for early briefs.
- A double tap went through the safety screen to the row behind it.
- Home said "Applies by itself" while the CRM was set to read only.
- A read-only viewer saw switches that did nothing.
- The switch order differed between Help and the safety screen.

Regression: Home QA 849/849, engine runner 235/235 (7 Claude-run evals skipped), stress suites 41/41, 44/44, 79/79, 87/87, 101/101 and 158/158, design lint 0 violations, safety lint clean, plugin validate passed.

## Round twenty-two (0.11.1): a QA council stress-tests every piece (simulated)

Five simulated QA specialists each wrote a stress file under `evals/stress/` and reported findings to the developers. The coordinator fixed every one, re-ran all suites, then sent the build back for a second round. Round 2 found 9 more issues; all are fixed.

| Suite | Round 1 start | Now |
| --- | --- | --- |
| `engine_fuzz.py` (engine with hostile bundles) | 20/41 | 41/41 |
| `panels_send.py` (panels, drafts, sending) | 50/66 | 79/79 |
| `data_security.py` (hostile data, links, scale) | 52/61 | 75/75 |
| `a11y_layout.py` (keyboard, contrast, touch, widths) | 58/77 | 79/79 |
| `reminders_ask_pdf.py` (reminders, Ask, PDF, Settings) | 114/141 | 158/158 |

What was fixed:
- **Sending.** A second Send during a slow send, or after closing and reopening the panel, no longer emails twice: there is one lock per draft. A sent draft never stays in the box. A failure after the panel closed shows a toast. "Name <email>" and Outlook's "Last, First <email>" read right, and text that is not an address is named in the confirm. Open in Gmail carries the edits. Deal, person and pitch sends are recorded.
- **Learning.** Right and Not right write one rating per tap, not two. Draft edits name their record.
- **Engine.** KPI, LP and summary fields of the wrong type no longer crash. Timelines sort by the real instant. Shards stay under 220 KB measured in UTF-8. Only http(s) links are kept. Name matching uses word boundaries. The safety lint exempts only Home's Gmail manifest line.
- **Reminders.** 24-hour times and minutes are read, 12 means noon, and "30% off" is not a time. Times are right across clock changes, and a time already past rolls on. A failed brief tries once. Drop has Undo, and the bell sheet refreshes.
- **Ask and PDF.** Code blocks show. Escaped pipes and split numbered lists render right. Chart gaps are gaps, many bars lie flat, and a cut is named. PDFs keep accented names, include the source link and save once on a double tap.
- **Access.** Focus never falls to the page body after Approve or Send, and never lands on an older toast's Undo. Touch targets are 44px on phones. Contrast is fixed for the TL;DR note and negative bars. The toast clears the floating buttons. Long pasted links wrap. Reduced motion stops smooth scrolls.
- **Data.** Timelines sort across time zones. Date-only events keep their day and year. A bad reminder date no longer blanks the tab. A capped timeline says "latest 24 of N".

Regression after the fixes: Home QA 849/849, engine runner 235/235 (7 Claude-run evals skipped, as before), design lint 0 violations, plugin validate passed, safety lint clean.

## Round twenty-one (0.11.0): a side panel for everything, sending from Home, reminders

What the owner asked, and what shipped:

- **Every row opens a side panel** (Today's Decisions, Threads, Waiting and Watch; Pipeline deals and pitches; People; Portfolio; LPs; prep attendees):
  - status;
  - a TL;DR and, for a decision, a recommendation with reasons; every line cites a numbered timeline event, and a line or reason with no matching event is dropped;
  - the actions; the draft; what only this kind has; a vertical timeline newest first (five, then Show all), each event with its platform and link; details.
  - The footer holds the main action (Send, Approve), then the record's link and PDF.
  - A summary that names none of the record's people or companies warns, and the main action reads "Send anyway".
- **Engine timelines:** `snap/timeline_0..3`, built from mail, meetings, notes, promises, CRM stage moves, passes, founder updates, LP calls, pitches and files shared, merged across runs, 14 events, 180 days. Every event has its link.
- **Drafts you edit and send from Home:**
  - To, Cc with your firm's people as chips, Subject, Draft.
  - Send shows the recipients and waits for Send now; then Gmail `send_message`, once, as you, in Verdana, in the thread when there is one.
  - Claude never sends: the safety lint allows only Home's capability manifest.
  - A draft for what someone owes you is written on the spot as a reminder.
- **Founder 360:** empathy map (what they say and do cites LinkedIn; what they think and feel is marked ant.'s read), career, track record, company, website, market, competitors (links only from the pages read), and the deck and model shared by email.
- **PDF:** every side panel; empathy maps go to Drive as two-page PDFs named date, person, company.
- **Ask:** Quick, Balanced, Thorough or Custom (model and effort); answers as a lead line, points, tables and SVG charts.
- **Reminders:** a floating Ask button and a bell, a Reminders place on the left, due reminders on Today with a brief. The engine writes what bears on each one (`snap/reminders`); the pulse adds what it finds in mail and calendar.
- **Settings:** access levels as icons, as Claude shows connector permissions, with the level's words under them.
- **Was it right?** The owner asked whether Useful / Not useful added value. As built before, only a little: weekly tuning moved how high each kind of line ranks, and nothing more. Now:
  - Right call? sits under the recommendation, and Not right asks what was off.
  - The vote keeps the text it judged and is scoped to the record and kind of line.
  - Recommendations and drafts read the user's notes and the edits they made before sending; the factual TL;DR never does.
  - Settings lists what ant. learned, with Remove. Checks read 180 days of it.

Council (simulated, five roles): round one 6.5 / 6 / 7 / 7 / 6, round two 8.5 / 8 / 8.5 / 8 / 8, round three 9 / 8.5 / 8.5 / 9 / 8.5. Round three's last five fixes were applied after it and not re-scored:

- portfolio numbers against plan;
- one rule for unsourced reasons;
- Send anyway;
- no pointer sections;
- phone Remind layout.

The council's view is that 9.5 now depends on real use: Gmail sending, PDF saving on phones, the summary guard on real data, whether notes visibly change drafts, real fonts and screen readers. Those checks are in `evals/smoke-checklist.md`.

## Round twenty: Deals by stage as a table, and the council pushed further

- **Deals by stage is one table.** Columns: Company, Stage, In stage (day x of y with a bar), Status, Next step, Lead, Round.
  - Every column has a filter under its header: a search box for company, a select for each of the others.
  - Every header sorts; the active one shows its arrow and `aria-sort`.
  - Quick chips: Needs a look, Mine, Clear filters.
  - A company opens its deal in the side panel: status, what the other fund did, the next-step form, Copy for partners, Mark quiet, the rating and Open in CRM.
  - On a phone: company search, one Filters button (with the number of filters on), a Clear button and a Sort by select. The table keeps Company (with stage, day and status under it) and Next step.
  - Red is used once a row: Competing. Days over and overdue steps are bold ink. "On track" is a quiet dash; a missing step reads "Set a step".
- **Today:** the top line has one way to finish (Sent it with a draft, Done without). Agenda red is for overdue only. Pills stack on the right from 380px cards. A row drops a status tag the line already says. One label for a ready draft: "Draft ready". The day line shows "3 of 9 cleared".

Council (simulated): round three 8 / 7.5 / 8 / 8 / 7.5, round four 8.5 / 8.5 / 8.5 / 8.5 / 8, round five 9 / 9 / 9 / 9 / 8.5. Its last two fixes were applied after that round and not re-scored: the cleared count now counts what you can clear yourself (Decisions, Threads, Watch and the top line; not Waiting), it is a live region, and on a phone the date drops from that line so Focus stays on it. What the council says only real use can settle: a phone check of swipe, Undo and the panel; a VoiceOver pass; headings judged with Raleway loaded; three days of dogfood.

## Round nineteen (0.10.0): rows like the owner's own app

The owner shared their personal app as the reference. What came over:

- **Count pills.** Meetings, Decisions, Threads and Waiting on others are one line of pills with a count each, in place of four stat cards. The count turns red when something in it is urgent. An empty section takes no pill. On a phone the strip is one line ("Waiting" for short).
- **Sections renamed** to match: Decide is Decisions, Send is Threads.
- **Row anatomy.** A done circle on the left (Done, Sent it, Got it, Close ask, or Seen on a line with nothing to finish). Then the line. Its actions are pills of one size: stacked on the right when the card has room (a container query at 560px), two to a line under the text when it does not. At most two action pills plus Later. More goes in the details, which the title opens, with the rating.
- **Swipe on a phone.** Right finishes the row, as the circle does. Left snoozes it until tomorrow. The row tints past the threshold, and the Undo toast follows.
- **Meeting notes in a side panel.** A notes chip opens a right-hand panel on a laptop and a bottom sheet on a phone. It shows the TL;DR, the promises from the meeting, and the notes with times. "Open in Granola" (or the notes app's name) is the main button.
  - The TL;DR is the notes app's own summary when there is one. Otherwise Claude writes it on open and Home keeps it in `state/tldr`.
  - The engine writes `snap/notes`: 30 days, merged across runs, capped at 150k characters.
  - Prep and the partner pack open as side panels too. Notes opened from them have Back.
- **Ask and search** read the notes: the TL;DR, the promises and the first lines.

Council (simulated, five roles): round one scored 6.5 / 6 / 6 / 7 / 6. Fixed after that round:

- one row pattern;
- sans fallback for headings;
- outlined pills of one width;
- one-line strip;
- swipe feedback;
- even footer;
- neutral circle.

Round two scored 7.5 / 7.5 / 7.5 / 7.5 / 7, and its remaining fixes were applied: Copy moves into the details when Gmail is one tap away, one pill colour, no icons in side pills, even footer on a laptop.

Still open, by choice:

- CRM proposals keep Approve and Skip with no circle, since a check mark must never mean "write to the CRM".
- The hero keeps Sent it and Done side by side.
- The agenda keeps its colour cues.

Checks: Home QA 755/755, engine 235/235 (7 skipped), lint 0.

## Round sixteen: the ant. Home redesign

The owner asked for a Home a partner can read in seconds: the day in logical sections, every section folding, an Activity log with Undo, LinkedIn research on the people they meet, and calmer type. A simulated design council (five roles, one Claude agent) audited 0.7.8 and then reviewed each of three build rounds.

| Round | Product design | Information architecture | Visual | Accessibility | Behavioural |
| --- | --- | --- | --- | --- | --- |
| Audit of 0.7.8 | 6 | 5 | 7 | 6 | 5 |
| Round 1 | 7 | 7.5 | 7.5 | 8 | 6.5 |
| Round 2 | 8 | 8 | 8 | 8.5 | 7.5 |
| Round 3 | 8.5 | 8.5 | 8.5 | 8.5 | 8 |
| Round 4 (0.9.0: Ask, research by itself, automatic mode) | 8.5 | 8.5 | 8.5 | 8.5 | 8.5 |
| Round 5 | 9 | 9 | 8.5 | 8.5 | 9 |
| Round 6 | 9.5 | 9 | 9 | 8.5 | 9 |
| Round 7 | 9.5 | 9 | 9 | 9 | 9.5 |
| Round 8 | 9.5 | 9 | 9 | 9.5 | 9.5 |
| Round 9 | 9.5 | 9.5 | 9.5 | 9.5 | 9.5 |

Rounds 6 and 7 fixed the round-five and round-six findings: every tab fits a 320px screen and no focused control hides under the tab bar (both pinned for every level), the research banner no longer widens a phone page (pinned for every level at 320 and 380 px), research messages sit under the top line, the Decide badge counts only what needs you, and focus stays on the tab you tapped.

### 0.9.0: ant. works by itself

- **Ask** on every screen (a tab, the search icon and /): instant matches from Home's data, and answers from Claude on the user's own account, from a compact copy of Home's data.
- **Research by itself.** With Home open in the Claude desktop app, it reads today's and tomorrow's external attendees on LinkedIn in the app's browser (navigate, page text and find, then the profile by its own link; it never clicks or types), writes an empathy map with Claude, keeps it in `snap/research` and saves a Google Doc to the research folder in Drive. At most five people per opening, each once a month; a sign-in wall stops it with one line.
- **Automatic mode** (`state/settings` `auto_apply`, on from setup): CRM changes from the user's notes and holds on their own calendar apply at the next check, with Undo in Activity and a recap on Today. Emails never send by themselves. Pinned in the `round17` suite.
- **Checked on the owner's laptop (28 Oct):** the Claude app's browser read a LinkedIn search and a profile while signed in; `find` returns each profile link with its address, so Home opens the profile by its link and never clicks. Google Drive found the research folder by name and saved an HTML Doc there; its link comes back as `viewUrl`. Still to watch on a real Home: the browser and Drive answering through the page's own connector calls rather than Claude's.
- **Settings** (the gear at the foot of the rail, or Help on a phone): each kind of tool with what is connected (`snap/connectors`, written by setup and each check), what ant. may do with it (`state/settings` `access`: read and save drafts, read and add holds, read and update, read only, off), and Add a tool: a search over the tools VCs use, where Connect opens Claude's connector page and a new tool starts read only. The engine refuses CRM and calendar changes set to read only (`round18` suite).

- **Today by the job.** A day strip (meetings, Decide, Send, Waiting on others), the one thing, the schedule, then Decide, Send, Waiting on others, Watch and Done today. On desktop, what you do sits on the left and what you watch on the right.
- **Every section folds** and remembers it per device. A folded section keeps its count, its urgent count and its top line. Focus folds everything but the top line and the schedule. Long lists show five rows, tables eight.
- **One row grammar.** Every row is closed until tapped, then shows one line of actions; snooze times and rating sit behind Later and Rate; sources show inside the open row. A draft has one button set everywhere: Open in Gmail, Sent it, Copy.
- **Activity** lists every tap for 90 days by day and kind, with Undo. A waiting change is withdrawn; an applied CRM change gets a `revert` action that the engine turns into a reverse `crm_update` (pinned in the `round16` suite); a sent email is only unmarked.
- **Research** (new skill): empathy maps from public LinkedIn profiles, read in the Claude app's browser only when the user asks in chat, saved to `snap/research` and a PDF in Drive. Home shows each map on every prep card with that person. Scheduled checks never open a browser.
- **Comfort.** 15px body with a Compact switch, the theme follows the device, a custom select, labelled form fields at 40px, the diamond only for High, Urgent and Breach, labels under the rail icons, a focus trap and inert page under sheets, arrow, Home and End keys on the tabs, shortcuts off on touch screens.
- **Known gaps.** Date fields follow the browser's format. Research cannot start from the page itself: Home copies the request for Claude. Some engine-written lines ("And 9 more, with yours") are long on a phone.

## Round fifteen: what changed

From the round-twelve product council (8.5, `evals/reports/council/product-council-r12.md`, conditions AC to AE). Pinned in the `round15` suite.

- **A thread counts as read only when it holds your note.** A thread trimmed to your later thank-you never triggers "no word from Aditi". engine.md and connectors.md now say the same: keep every message from your note on, for an ask, a chase or a note to a partner.
- **A late Sent it still finds the note.** ant. looks back two weeks for your note, and never takes a thank-you after their reply as the note.
- **Every way of saying it was paid** ("payment was made", "it has already been paid", "the wire went out") reads as paid. "I paid a visit" is no answer about money.
- **Small lines.** No double full stop in Ready for you. A deferred answer the morning finds says "the answer is to follow". The last "Instinct" words in templates and docs say ant.
- **License.** MIT, in LICENSE and plugin.json.

## Round fourteen: what changed

From the round-eleven product council (8.13, no-go, `evals/reports/council/product-council-r11.md`, conditions X to AB), the round-thirteen VC panel (9.71, `evals/reports/council/vc-panel-r13.md`) and the Claude runs on 0.7.6 (9, 9, 8). Pinned in the `round14` suite (12 checks). The product is now called **ant.**: the page header shows the Anthill mark and a bold Nunito "ant." wordmark, and every word the user reads says ant. (the plugin id `ant-vc` and the scheduled-run marker stay, so nothing breaks).

- **A reply counts whatever you write after it.** When the note went is your first message in its thread, never a later thank-you.
- **The note to a partner.** "No word from Aditi yet, decide today" goes out only after a run read the note's whole thread, for any sent note, not only one sent that day. A waiting note is rebuilt down to the one draft left. A note saved in Gmail is never rewritten; Home says which line to take out.
- **Who set a date is stored on the draft**, never read from its words. A promised date that has passed never stays in a draft, whoever set it; one you set also gets a line that owns the delay.
- **Replies.** A reply that puts off its answer stays deferring, and its nudge stays under Ready for you until sent. "We paid it last Friday" reads "says it was paid: check the account", with no chase for eight working days. "The call" and "pay a visit" are no answer about money.
- **Honest drafts on every card.** The hero, Ready for you and the prep sheet say which lines to take out of an email whose promise you closed. After Sent it, an LP hero no longer says "no touch in 96 days".
- **Records hold.** Sent it on the page keeps the promise marked sent, so its CRM step reads as sent. A CRM read that leaves out a deal's round or raise keeps what Home knew, and the run warns.

## Round thirteen: what changed

From the round-ten product council (7.75, no-go, `evals/reports/council/product-council-r10.md`, conditions Q to W), the round-twelve VC panel (9.5, `evals/reports/council/vc-panel-r12.md`) and three scheduled-run Claude evals on 0.7.5 (`evals/reports/claude-runs/r12-*.md`: Meera's Friday 8, Tara's Friday 8, Tara's nudge morning 8.5). Their tests are pinned in the `round13` suite (18 checks, replays to Mon 23 Nov) and in Home QA (20 more checks).

- **Done is never Sent it.** Done closes one row and its promise, and says "Marked done". It closes an email only when no other open promise rides in it. Only Sent it marks an email sent. When one promise in a shared email is closed, the email says which lines to take out, and the morning rewrites it for the promise left. An undated promise keeps its email on its row at every run.
- **A reply counts from when the note really went.** That is your own message in its thread, or else the start of the day before the tap. So a reply that lands before Sent it still counts, for asks and for chases. When the morning finds a reply the engine missed, the ask, its row and the push change too. A reply that puts off its answer ("let me think and come back to you") is followed up five working days later. A partial reply never reads "no reply", even when it names a company by its first word.
- **The note to a partner.** It never names a deal marked quiet. There is one id per partner, rebuilt in place while it waits, with a subject that names only what it holds. Once it is sent, no other note follows for three working days, and nothing it named is asked again, answered or not. Home keeps the sent note while a draft it names waits, so those rows say "Asked Aditi at 07:10" and then "Aditi replied". When a decision it named is due today and she has not replied by 14:00, the push says "no word from Aditi yet, decide today".
- **Dates and words read right.** "Paid last Friday" and "Monday's call" are never promised days. "Fund" alone is not an answer about money. Only a date still ahead when a draft was written can go stale. A date Instinct chose moves two working days out, as its suggestion; one you or a founder set stays, with one line that owns the delay.
- **Money reaches the phone every week.** An unpaid call on Today reaches the phone at least once in every Monday-to-Friday week, counted by calendar day, for a team and for a solo GP, to Mon 23 Nov.
- **Today keeps its cap.** The line for promises more than a week late counts against it. When a line due today, or one a push named, is put back, the line that matters least gives way, and a week-late promise joins the late line rather than vanishing.
- **Old news stays gone.** A passed deadline is never "Another fund is moving": the kicker and the review push say their deadline passed. A late promise whose race row the cap took off Today names the race again. A reply that left Home is not written again. A wide read never brings back a pitch older than two weeks. After Sent it, the CRM's old step reads "Sent 23 Oct: send term sheet markup" on Pipeline and in prep for 90 days, never "Next:".
- **Eval harness.** The replays write drafts as the drafts command does, over the build's own output, and in every run write what a pulse writes (rewrites of moved-on nudges and emails, and rebuilt partner notes). A narrow people read on a Home with no directory warns.

## Round twelve: what changed

From the round-eleven VC panel (9.29, `evals/reports/council/vc-panel-r11.md`) and three scheduled-run Claude evals on 0.7.4 (`evals/reports/claude-runs/r11-*.md`: Tara's nudge morning 8, Tara's Friday 8, Meera's Friday 7). Their tests are pinned in the `round12` suite (19 checks, replays to Mon 23 Nov) and in Home QA (31 more checks).

- **A note to the partner the work waits on.** When two or more of your drafts wait on one partner's view (Rivulet's feedback, Trellis's pricing view), the morning writes one short internal note to that partner. It has one line per draft, the late ones first, and any decision due within two working days on their deals ("Sable Fraud AI: term sheet from Monsoon Arc Ventures, decide by Fri 23 Oct"). It comes first among the drafts under Ready for you, and each draft it names says "Note to Aditi ready". It leaves once those drafts are sent. One note at a time, and none in the three working days after one was sent.
- **A reply is a reply only when it answers.** A reply counts only in the note's own thread. One that names some of the note's asks answers only those. The rest say "Aditi answered on Kestrel Pay and Orbit Treasury on 26 Oct, not this one", never "no reply", and their nudge thanks her for the two first. An LP's email about something else is not an answer. One that names a day for the wire is followed up after that day ("said it would go on 28 Oct, still unpaid"). A note to an LP that you marked sent counts as a touch, so a chased call, once paid, never reads "no touch in 110 days".
- **Times true at every hour.** Home compares a tap's time with a run's as instants. So a step saved in UTC after a +05:30 run shows as saving, and a note marked sent at 01:45 in Mumbai counts on that day. A date gone by reads "was due", never "by".
- **Friday sees Monday.** On a Friday, Today names Monday's meetings and each opens its prep. Monday's partner card leads with what the room decides. It says when a deadline passes before the meeting, and it keeps the morning's questions through the day's pulses.
- **Late work never goes silent.** Every promise more than a week late is on Today, as a row or in one line ("3 promises more than a week late"). A colleague's promise to you clears with Got it. Ready for you says how late a promise's draft is.
- **Pitches.** Sent it on a pitch reply closes the pitch, and the Pitches list says "You replied". A pitch once in touch never flips back to "book a call". A pitch reply unsent for a week leaves Ready for you.
- **Drafts stay honest.** A date a waiting draft promised is rewritten once it passes: as Instinct's suggestion, or with one line that owns the delay when the user set it. An undated promise to the same person ("Invite Rahul to the founders dinner") rides in the draft already waiting for him, and Sent it closes both. A rewrite asks for what the reader owes the user, unless it copies a third person.
- **What leads reaches the phone.** An unpaid call that leads Today reaches the phone at least once in every week it leads. The run that writes one ask's nudge points its row at it, and the push says "Note ready". A tap after a nudge was written narrows it at the next check. A push that named a row opens Home on Today with that row open.
- **Nothing lost in a narrow read.** A pulse that sends no deals keeps every deal's CRM stage label. A deal fact folded into one line names its deal. When a CRM read still holds what a tap just changed, the run warns.
- **Eval harness.** The mock serves Slack search, the seeded weekday task and the eval's own world, and `seed_eval` seeds them. A draft marked sent in the mock Home is in the sent mail from that moment, so a reply test can run end to end.

## Round eleven: what changed

From the round-ten VC panel (9.21, `evals/reports/council/vc-panel-r10.md`), the round-nine product council (8.25, no-go, `evals/reports/council/product-council-r9.md`, conditions J to P) and three scheduled-run Claude evals on 0.7.3 (`evals/reports/claude-runs/r10-*.md`). Their tests are pinned in the `round11` suite (16 checks, replays to Mon 23 Nov) and in Home QA (37 more checks).

- **"Sent it" wherever a draft shows.** The hero, every row, Ready for you and the prep sheet offer Sent it beside Open in Gmail. It marks the draft sent, and closes a promise with it; an ask stays open and says who was asked. On an ask, the closing tap reads "Close ask", so Done can never close one by mistake. Done or Sent it on the hero steps the next line up; the Portfolio hero moves on too. When the morning push named the hero, Home opens on Today.
- **A reply stops a follow-up.** Before a nudge or a second chase, Instinct looks in the mail it read for an answer from that person since the note went. If there is one, the ask says "Aditi replied on 26 Oct: read it, then answer here", the LP line says Peter replied, and nothing is drafted or pushed. The morning brief says the same for its own drafts.
- **Money is remembered while the call is unpaid.** A sent chase lives on the LP's record, not on its draft: "chased Peter (again) on ..." every morning to Mon 23 Nov, never a first chase again, never a third.
- **Taps hold.** A Pipeline step saved again after the last one was applied waits for the next check, and the row says so. An answered tap never reads "Draft coming", even after its draft leaves Home. A tap on an ask after its nudge was written rewrites the nudge for the asks still waiting. The pulse passes the run's own time to `actions`.
- **Drafts written after the build say so.** The run that writes a nudge or a note turns its row, the ask hero and the push to "ready" ("...: no reply since 22 Oct. Note ready"). A waiting draft that says "this week" or "tomorrow" from an earlier day is rewritten with dates; one written before a meeting with the people it names is checked; notes an earlier run read count. A draft to someone who owes the user asks for it in one line, and "invite" counts as an email.
- **Old news stays old.** A signal that leaves the 7-day mail read keeps its id and says when it began; an old race repeats as "Still open", never as a new breach. Fund names keep their capitals. Aditi's contested intro stays on Today while the race runs, and the hero names the rival's promise.
- **Nothing silently lost.** A deal Home shows open that a full CRM read leaves out stays, and the run warns. A narrow read keeps company descriptions and pass ids. People counts days from today. A Friday preps Monday's meetings. A pitch answered once is never answered again. Old unlogged meetings fold into one line ("Log 3 meetings from ...").
- **Guard.** A data name that orders something at either end, or alone, is refused unless it ends with what it returns (`shares` and `calls` added); an Artifact read that saves a file (`path`, `paths`, `out_dir`) is refused, and a plain read and list pass. TRUST.md and safety.md say exactly that.
- **Eval harness.** The mock serves the mail a seeded Home depends on and the eval's own clock; `bundle --now --mode --after` reads as that run would; seeded taps happen at their times, after the day's last check.

## Round ten: what changed

From the round-nine VC panel (9.0, `evals/reports/council/vc-panel-r9.md`), the round-eight product council (8.13, no-go, `evals/reports/council/product-council-r8.md`) and two Friday Claude-run evals on 0.7.2 (`evals/reports/claude-runs/r9-friday-*.md`). The panel's tests for 9.5 are pinned in the `round10` suite and in Home QA.

- **One nudge per note.** Asks that went out in one email wait on one reply. After five quiet working days the morning drafts one short nudge to that person, in the same thread, naming each ask still waiting; Today shows one row ("2 founder asks wait on Aditi") with the draft and "See each ask", and one push names it. Each ask keeps its own row on Portfolio. A nudge is written once; a waiting nudge goes once a later note is sent or the intro is made; a quiet nudge says the next way in ("ask the team instead", or raise it with the partner).
- **The partner's yes is the user's word.** After a note to the board partner, the button reads "Aditi said yes: ask the team" (or "...: draft the intro ask"), beside the nudge when one is ready. Once she was asked, the row drops "check with Aditi before sourcing"; once she said yes, it says so with the date.
- **What a draft needs.** A draft with blanks says "Fill in 3 lines" on its row and in its push, never only "Draft ready", and names who holds the firm's view ("check the firm's view with Aditi"). The letter's row and a capital call's say "Draft ready" on the run that writes them. A rewritten draft keeps what the old note asked of the user, carries the promise and its holder, keeps only lines a source holds, and marks Instinct's own suggestions.
- **Money after "Sent it".** A chased capital call reads "chased Peter on 22 Oct" and stops saying "no touch"; five quiet working days later the morning drafts one shorter second note.
- **Nothing late vanishes.** Your own promise up to a week late, and a colleague's late promise to you (one line), keep their place on Today. A step request after a blank met log stays until a step is set. On a Friday, promises due Monday and Tuesday are drafted.
- **Words.** No push ends in "...": a long line stops at its last whole clause. A trimmed quote keeps the speaker's first words, never only "Arjun wrote on 20 Oct". A met log never offers a past due date. Prep questions say they are Instinct's suggestions. A team note names the founder, the company and the ask only, and a colleague in full when the founder shares the name.
- **Guard and trust.** On data connectors a name of nouns that opens with one that is also a verb (contact, fund, tag, exit, report and others) is refused unless it ends with what it returns ("fund performance", "contact details"). ArtifactData reads save only into the work folder and writes load only from it or the plugin, by absolute path; the engine copy comes only from the plugin's `engine` folder. TRUST.md, safety.md and the README say exactly that, and that the guard judges a tool by its name. 718 probes pinned.
- **Skills.** The pulse's draft rules are an ordered list (a follow-on tap first, then the cash warning, the path, the team); a team note never merges with a one-to-one draft; a met log dates the stage from the meeting (the one extra field safety rule 7 allows); an empty step is null and a field already holding the value is "already". The morning brief writes nudges, caps Gmail drafts at ten a morning (pitch replies last), and may read people only at today's companies (`people_partial`), with Home keeping the rest. The letter's inputs carry no paid-in figure, and `letter-check` flags one.

## Round nine: what changed

From the round-eight VC panel (9.07, `evals/reports/council/vc-panel-r8.md`). Its ten tests for 9.5 are pinned in the `round9` suite and in Home QA.

- **The replay reads what a real run reads.** A new replay cuts each run's bundle to its row in `shared/connectors.md` (a morning brief reads 7 days of mail, a pulse the hours since the last run). On it, Tara's Nimbus row keeps "Aditi knows Raj Malhotra" every run from Thursday to the next Friday, and Aditi's intro email at Mon 12:00 shows as "Intro made on 26 Oct" at the next check.
- **Asks followed to the end.** An ask whose note went out stays on Today until the intro is made or you close it, however old the founder's ask; five quiet working days ask for a nudge on Today. After a board note, "Yes, ask the team" (or "Yes, draft the intro ask") is a tap with its own id, so its note never reuses the sent note's; after a quiet colleague, "Ask the team instead". No push names an ask that waits on someone else, and no push is cut mid-name. The meeting line and the heads-up say where an ask stands: "note to Aditi ready", "asked Aditi on 22 Oct", "intro made".
- **The step after a met log.** Saving with the step left blank, when the CRM's step was that meeting, clears it (`clear_step`), so no colleague reads "Next: Second meeting, 24 Oct". From the next check, Today asks for the step alone ("Halo Reconcile: met 22 Oct, add the next step") until one is set. Each log names its meeting, so next week's meeting with the same founder asks again. Every colleague's Home dates a stage move from the logged contact when the CRM keeps no stage date: Aditi's Pipeline reads "Second meeting, 1 day" on Friday.
- **Money drafted, nothing lost.** A capital call's row says "Draft ready: check the amount, then send it" once its chase note is in Home. A push records only the deals and companies its line names. A Monday chore due today stays on Today at every run.
- **Words true as days pass.** A founder's quote two days old says when it was written ("Tanvi wrote on 21 Oct"); a trimmed quote ends on an ellipsis inside its quotes. A met pitch with an open deal leaves the inbound list, returning passes included; "first call" maps to First meeting. A carried review says today's count. A heads-up with no news names the deal's step ("Founder call on terms"). With cash tight and a hiring ask, the board's question leads the card and the hero: "With 8.0 months left at $200K net burn a month, do we help them hire now, or wait?"
- **Finance and drafts.** The letter never sets paid-in beside called, and its watch list leads with the reason. A refreshed draft with no notes says so: "check it still stands, or tap Done if it was settled in the room". Feedback that only the sponsoring partner holds names them.
- **One person's fund.** The solo sample owns every deal; her Pipeline shows no owner initials or partner. The headline counts the meetings still to log.

## Round eight, part two: the Claude-run evals and the product council

Two fresh Claude agents ran Thursday's scheduled morning on the 0.7.0 skills, as Tara (Platform) and Vikram (CFO), against the mock connectors (`evals/reports/claude-runs/r8-morning-brief-*.md`). Every founder ask and the Q3 letter came out "Draft ready", with their ids kept. The product council's round seven (`evals/reports/council/product-council-r7.md`, 8.25) found one guard regression. What changed in 0.7.1:

- **Guard.** On Carta and the company-data connectors a read must name a read verb or only the data it returns (`capital_accounts`, `company_profile`); any other word is refused, so `carta-email-capital-call`, `carta-remit-distribution`, `payout`, `release` and `settle` names are blocked. TRUST.md and safety.md now say what the guard checks (the tool's name) and its limit (a read-named tool that changes something would pass). 652 guard probes pinned.
- **Warm paths hold.** Firm members always resolve as people, so a colleague's CRM relationships count on a morning when they wrote nothing to you: Nimbus's note goes to Aditi, who knows Raj Malhotra, not to the whole team. Ask paths are found before the prep cards, so the dinner card and the ask row agree.
- **One note per colleague.** Several asks for the same person go in one email, a paragraph each, cash warnings first, and every ask's row still shows "Draft ready". An ask under a meeting line shows its note is ready. With a cash warning the row says "No warm path found yet", never "ask your team".
- **Finance.** The quarterly letter is drafted with its quarter ("Q3 2026"), sources for the fund figures, the flag figures, the quarter's new investments and the pipeline by stage; `letter-check` lists missing sections; its row says "Draft ready: check the figures, then send it". A capital call unpaid for two weeks gets a polite chase note for the LP's owner. LP touches rank above the portfolio flags a CFO does not act on.
- **Skill text.** The letter goes as a draft to its owner (or a document when asked in chat); long drafts get Copy in Home; an introduction copies everyone it connects; `transcripts: []` means "read, nothing new"; CRM people come with their companies; the morning check owns step 7.
- **Small.** Demo asks dated from their founder updates; a prep question that read "make the an introduction"; subjects that name the company ("Rivulet Payments: our feedback"); the solo GP's calendar without "partner" titles; "Decision stage, day 3 of 7".

## Round eight: what changed

From the round-seven VC panel (8.7) and the Friday Claude-run eval on 0.6.0 (`evals/reports/claude-runs/r7-friday-meera.md`).

- **Ranked by what it costs to miss.** A heads-up names what you owe the people you are about to meet when it is late, even if the morning push named it ("15:30 Northgate Endowment: You owe them: answer the fee offset question, 43 days late"). A promise to a founder three or more days late while another fund is moving beats a chore due today, in the push and the hero, and says why ("Term sheet from Bluepeak Partners"); not on two mornings in three. An LP touch is Overdue only once its window is a month away. A Saturday deadline ranks as Friday's work in the list too.
- **Words survive a short Today.** "Raise it at the partner meeting" follows the founder's words, so a trimmed row keeps "until next week"; a row over the word budget keeps its first sentence; the sync line that names your own votes is never trimmed. Your own votes stay off Today after the sync decided them.
- **The met log is one honest tap.** It fills in from the meeting: the stage the invite names ("second meeting" moves a first-meeting deal on) and the CRM's step only while it is still ahead; Save with no step logs the meeting and the stage. A contact the CRM logged in the last five working days counts like a meeting in every colleague's Home. A stage moved from Home starts on the meeting day, even when the CRM keeps no stage date. "Move to Closing" is a move; only passed, lost, won and portfolio are refused.
- **Asks, finished and followed.** A cash warning sends the first note to the board partner; a team note goes to every colleague by address; the row then says who was asked ("Asked Aditi for the intro on 22 Oct", "Asked the team"), asks for a nudge after five quiet working days, and shows "Intro made" once the introduction is in your mail. A solo GP gets no team note and no team words. The dinner heads-up names the path: "Divya needs two banks as customers: Aditi knows Raj Malhotra". Asks read "an introduction to", never "intro to".
- **Drafts that hold for everyone in them.** A call with a colleague copies them in and asks the founder for times, so no hour of theirs is offered twice across the team. A refreshed draft greets only who was in the room, drops "when we meet today" once the meeting has happened, and keeps the waiting draft's own lines; without notes it says only that you met. An introduction copies the second person in, and a second email to them the same morning says the first is on its way. Pass replies say where we invest in a founder's words: "US companies with a team in India".
- **Skill text matches the engine.** The morning brief describes the letter, asks (by `note_kind`), refreshes (`met_with`, `notes_url`) and time rules (working hours, 30 minutes clear, seven working days); the pulse writes a stage with the CRM's own spelling and dates it; one applying mark per approval; the LP list is read only where LP watch is on; the run row counts what the headline counts.
- **Carried and cleaned.** A pipeline review held all Thursday goes out on Friday after the morning line. A met pitch with a deal leaves the inbound list. The solo GP's sample CRM speaks for one person.

## Round seven: what changed

From the round-six VC panel (8.2) and the round-five product council (8.0).

- **Guard.** On Gmail, Calendar, Drive, Granola, Slack and Notion, a read passes only by its known name. Elsewhere a read must start or end with a read verb and carry no second action: `get_and_send`, `check_out`, `status_flip` and `view_as` are refused. A scheduled run can no longer rewrite the settings: only the Sunday tuning's own fields merge into `snap/config`. The canary must be the run's first call.
- **Drafts true on the day.** Each draft records the times it offers. The next morning, a draft whose times are today or past gets two new ones, a draft written before a meeting with that person is brought up to date, and no time sits in two drafts. A cold reply to a founder you have since met is dropped.
- **Finished without a tap.** Each founder ask gets its note the first morning (to the contact you know, the colleague who knows them, or the team), and moves to "Intro requested" once you mark it sent. The quarterly LP letter is drafted from the KPI history and the LP list, gaps marked.
- **One tap after a founder meeting.** Ready for you offers "met <date>": the next step, the stage and the last contact go to the CRM at the next check, so colleagues' Pipelines stop calling the deal stale.
- **Pass replies** give the reason that decided the pass (an anti-pattern, then geography, then a round too late or large, then the sector). Acronyms keep their capitals.
- **Your own work first.** Your late promises rank above what a colleague owes you, and the morning line's "late" is your own promise or a founder waiting on you, never an LP touch window. A Saturday deadline reads "so today" on Friday, in the push and the row alike.
- **Pushed means kept.** What a push named stays on Today until the day ends. A heads-up never repeats what the board-eve line said the night before.
- **Sync.** Your own votes are named in the sync's agenda line ("with yours: ...") instead of repeated rows; a colleague's deal the sync covered stays off Today for the day; a non-partner's sync heads-up names their deals.
- **Words.** "1 meeting", no period after a closing quote, lower case after "You owe:", "Last met 20 Oct" instead of a raw invite title, a shared signal says where the deal stands, and every week-ahead line sums up the week.
- **Today stays short.** At most 12 lines for an analyst too; a pitch warning has its first morning on Today, then lives on the Pitches list; the colleagues' line never takes a place from your own work.

## Round six: what changed

From the round-four product council and the round-five VC panel.

- **Guard.** The engine runs isolated (`python3 -I -S`) from inside the work folder, so a planted module cannot run. The shell allows a short list of file commands, each with its own plain options; quoted heredocs only; every redirect and path checked. Write, Edit, Read and Grep stay in the work folder and the plugin. `batch`, `resolve` and many more verbs count as writes. A database read is one plain `SELECT`, with no comments, dollar quotes or quoted function names. Holds stay on the default calendar, one event, no repeat.
- **A dead guard is visible.** Each scheduled run first runs a canary the guard always refuses. If it runs, the run writes `guard_off` and stops; Home shows a warning and the phone gets one line.
- **Pushes fit the day.** At most four a day. None inside a meeting or the 15 minutes before one. A heads-up comes from the last free run 45 minutes or more ahead, folding into an earlier run when needed. Every pushed item is on Today. The morning line leads with your own work: a deadline today, then late promises; two promises due today share one line.
- **Calendar truth.** For five working days after a meeting, a deal is not stale and says "Met 22 Oct. Add the next step". A deal whose next step is due today or tomorrow is moving, not stale. "Confirm the slot" looks done once the meeting happened, however long ago.
- **Words.** Only a founder's own words go in quotes; a colleague's shared note is said as a summary. No cut text anywhere: long lines end on whole sentences. One row per company. Heads-ups say "8 days late".
- **Levels.** An analyst's colleague races are one grey line at the end of Today. Finance's own deliverables (the Q3 LP letter) rank like promises to founders, with "Instinct can draft it". A solo GP holds outcome promises until they decide, and replays on its own calendar and $30M fund.
- **Sync pack.** The same rows for everyone in the room, read from the CRM and shared notes only, each naming the lead, the sponsoring partner, the round and its size.
- **Sheet CRM.** Changes are suggestions with Copy change; nothing tries to write a sheet.
- **Founder asks.** Each names a warm path or says none was found, with a draft (to the contact, or to the team).
- **Evidence.** The mock enforces Home versions and keeps CRM changes; the smoke checklist carries the guard probes and the canary; this log is current.

## Round six, part two: what the Claude-run evals found

Two fresh Claude agents ran the 0.5.0 skills end to end against the mock connectors: setup for Meera (associate) and a scheduled pulse for Aditi (partner). Their 30 findings are in `evals/reports/claude-runs/r6-*.md`. What changed:

- **A founder waiting on you.** When a founder on your own deal asks a question and nothing from the firm goes back for two working days, Today says so in their words: "Copperleaf Collect: Debashish asked on 13 Oct, no reply yet", with the question quoted and an answer drafted (a gap where only you know the answer). It replaces "no contact in 9 days", stays through the hourly checks, and goes once anyone at the firm writes to them or meets them.
- **Already in touch.** A pitch from a founder you already write to (on another thread, or in the pitch itself) says "you already write to them" and gets no cold reply. The bundle keeps your own latest message in each thread so Instinct knows who answered last.
- **Sync pack.** Racing rivals first, then votes and term sheets; late-stage deals that stalled are their own list, last, and the "decide on" count leaves them out. The stage shows beside another fund's term sheet.
- **Promises.** "Feedback after Monday's partner meeting" is no longer closed by a booked meeting; only scheduling promises are.
- **Pitches.** Keyword hits next to the thesis are "adjacent", not a fit; onboarded users are not paying customers; a pitch from two places names both ("Delaware and Bangalore").
- **Pulse.** Carried signals keep the summary wording; ask paths, fund size, last met and prep history survive a narrow read; a heads-up never goes out before its card has questions; every handled tap, a Home draft included, goes in `applied.json`, with an "already set" shape; a next step is checked against what Home showed.
- **Setup.** Firm members include Platform and Finance with titles; the thesis reads the CRM's entry stage and check size; no LP data for a level without LPs; the closing says what is really there; its line is shown in chat, not counted as a push.
- **Small.** A prep card names the address on the invite, not an alias; refused taps name the deal and the change; the demo's Nimbus ask comes from a thread Aditi is on.

## Earlier rounds, in short

- Rounds one and two: seven scheduled tasks became two; pulses read only what changed and the engine carries the rest forward; Instinct posts nothing; approvals apply only what Home showed, marked before applying; memory holds only what the user confirmed.
- Round three: an allowlist guard; drafts kept honest when Gmail cannot create one; a schedule-aware Home.
- Round four: calendar-true heads-ups, shared sync packs, a Fund view.
- Round five: fixes from five Claude-run evals (LP data kept through pulses, level options with evidence, intro drafts to both people, word budgets).

## Known limits

- Every score is simulated. The real-account smoke test (`evals/smoke-checklist.md`) has not been run yet; it is the go condition for testers.
- Claude still writes the bundle by hand each run. A morning bundle may now carry only the people at today's companies (`people_partial`), with Home keeping the rest, but connector adapters would cut cost further.
- "Draft a note" from Home is written at the next hourly check, not at the tap.
- Instinct sees a reply only in the mail a run reads. An answer given on a call, in Slack or in the room needs the user's tap (Close ask, Done or Sent it) before follow-ups stop.
- The guard cannot tell one CRM field or record from another, and a field change can set off the CRM's own automations.
- A pipeline past about 450 live deals trims the oldest-contacted deals from Home (the CRM keeps them all).
