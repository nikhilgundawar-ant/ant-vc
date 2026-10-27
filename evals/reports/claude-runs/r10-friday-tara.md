<!-- Claude-run eval, round ten. Written by a Claude agent running the pulse skill against the mock connectors on a clean clone at a023dd2; saved by the main session (the agent could not write files). -->

# Eval report: friday-tara (round 10)

The morning run did the right work: Tara's tap was honoured, the right drafts are ready, and nothing was lost an hour later. The serious problem is in Home itself. Once a draft sits on a row or the hero, the page gives her no way to say she sent it. That breaks the "asks followed after sending" loop this release is built around. Score: 7 out of 10.

- Plugin version: 0.7.3 (plugin.json, both skills and `engine/instinct.py check` agree)
- Commit: `a023dd2 Round ten: one nudge per note, drafts say what they need, money and asks followed after sending; version 0.7.3`
- `git status --short`: clean at checkout and at the end (`evals/runs/` is git-ignored)
- Member: `tara`, Tara Menon, Head of Platform (level `platform`), Quillwater Ventures
- Run: Fri 23 Oct 2026, 06:28 Asia/Kolkata, run id `r20261023T0628`; the `weekday` task in `schedules.json`
- Skill: `pulse`, jobs `morning_brief` and `pulse` (so morning-brief steps 6 and 7 apply)

Eval-mode adjustments:
- Skipped pulse step 0 (no guard loads in eval mode).
- Ran the engine from the clone instead of copying it.
- Passed `--now 2026-10-23T06:28:00+05:30` to `due`.
- Used the mock `db` commands for every Home read and write; the runs read was `db list`, not an ordered query.
- Used the mock `bundle` shortcut, then set its `now` to Fri 06:28 and trimmed it to the morning-brief windows with a helper script.

## 1. What I ran, in order

Setup: clone, checkout, clean tree; read `evals/eval-mode.md`; `seed_eval.py friday tara` gave 14 snapshots, 14 runs, 3 drafts and one tap (`t_3461c2ec2f_team`); read every skill, the five shared docs and `templates/pass-note.md`.

1. `mock status`: all connected; Gmail has no `create_draft`, so drafts stay in Home (`in_gmail: false`).
2. Step 0 skipped (eval mode).
3. Step 1, load: `db list` for `snap`, `state`, `runs` into `<abs>/home-db` (14 snapshots, 2 state docs, 14 runs); `versions.txt` and `config.json` written. Config: level `platform`, `opens_on: portfolio`, triage, pipeline and LP watch off, portfolio `asks`.
4. Home held one approved tap (`t_3461c2ec2f_team`), the 22 Oct note to Aditi marked done at Thu 10:00, and drafts for the CFO candidates (Rahul) and the guest list (Fatima).
5. Step 2: `due` gave `morning_brief, pulse`, daily build, window from Thu 19:28, run id `r20261023T0628`; run row created.
6. Step 3: one pending tap. No reply from Aditi in mail; Orbit's ask read from `upd_orbit`; Vikram Rao (Orbit CEO) and Vikram Nair (firm CFO) told apart. Wrote `drafts.json` (the team note) and `applied.json`.
7. Step 4: the `bundle` shortcut returned Thursday 07:00 and the whole world; trimmed to the morning windows (3 threads, 5 events, no notes, CRM partial, 20 passes; no `lps`).
8. Step 5: `build --mode daily ... --applied applied.json --drafts drafts.json`. Hero "Send the founder guest list" (Fatima, due today); 9 items, 221 words; push "Send the founder guest list: Fatima (Talentbridge), due today. Draft ready"; `owed` 1 entry; batch of 7 documents.
9. Morning-brief step 6: one entry, a refresh of `dr_k_e9eab86816`; `drafts` wrote it, refused none.
10. Step 7: brief checked (hero states a fact, every line sourced, 221 of 350 words).
11. Step 6: `db batch` (brief, pipeline, portfolio, proposals, directory, drafts, asks to version 2); run row finished with `pushed: true`, `push_key: daily:2026-10-23`.
12. Final line: **Send the founder guest list: Fatima (Talentbridge), due today. Draft ready**

22 mock calls; none sent, drafted in Gmail, wrote to the CRM or added a calendar hold.

## 2. The pending taps

`t_3461c2ec2f_team`, "Aditi said yes: ask the team" on Orbit Treasury, tapped Thu 18:40, following the board note to Aditi (Thu 10:00). Applied by pulse step 3 rule 1 as a team note to all colleagues saying who was asked and when; the runway flag left out (the whole firm reads it); "Vikram Nair" in full since the founder is Vikram Rao; id `dr_t_3461c2ec2f_team`, `note_kind: team`.

- To: aditi, kabir, meera, rohan, vikram (all @quillwater.vc). Subject: "Orbit Treasury: intros to senior backend engineers".
- Body: "Hi all, Vikram Rao at Orbit Treasury asked in their September update for introductions to senior backend engineers, to help them make two hires this quarter. I asked Aditi about it on 22 Oct and she agreed we should help. Do you know someone who fits? Send me names and I will make the introductions. Tara"
- Context: Aditi's yes is not in your mail (you marked it in Home on 22 Oct at 18:40), so check she agreed before you send. Orbit's runway flag is left out, since the whole firm reads this.

## 3. The owed entry and its draft

`dr_k_e9eab86816`, a refresh of "Intro two CFO candidates" (due 21 Oct, 2 days late), written before the 22 Oct "Tallyfin: hiring" meeting with Rahul, which has no notes. Kept the draft, opened with one line naming the meeting, kept the old check and added the refresh check; the old "this week" became Tue 27 Oct, marked as Instinct's suggestion.

- To: rahul@tallyfin.com. Subject: "Tallyfin: two CFO candidates".
- Body: "Hi Rahul, Good to see you at our hiring catch-up on Thursday. As promised, two CFO candidates for Tallyfin: George Thomas and Swati Kulkarni. Both are in our network. Tell me who you would like to meet first, and I will introduce you by Tue 27 Oct. Tara"
- Context: promised 15 Oct, due 21 Oct; names from the two CRM people tagged CFO candidate; check each is open to a move; written before the 22 Oct meeting, which has no notes: check it still stands, or tap Done if it was settled in the room; 27 Oct is Instinct's suggestion in place of "this week".

## 4. Next-run check

Rendered in the real page with Playwright (QA harness skeleton and mock runtime), phone width, no script errors.

- Push: "Send the founder guest list: Fatima (Talentbridge), due today. Draft ready" (74 characters).
- Home opens on Portfolio (config `opens_on: portfolio`, and "due today" is not urgent): hero "A founder asks · Orbit Treasury: introductions to senior engineers..." with "Team note ready. Runway under 9 months: Aditi said yes on 22 Oct..." and Open draft, Copy, the founder update, then "Before you send".
- Today: hero "Send the founder guest list" with Open draft, Done, Snooze and "Before you send"; no meetings; next up the overdue CFO intro (Draft ready), Orbit (Team note ready), Tallyfin key person, Rahul's CTO job description (4 days late); Founders need shows Nimbus "Asked Aditi for the intro" and Kestrel "Asked Aditi" with its own "Aditi said yes: ask the team". Ready for you is not shown: all three drafts sit on rows.
- The 07:28 pulse (rebuilt in a separate folder): "Nothing new"; every row, draft, ask and proposal unchanged; nothing lost.

## 5. Findings, worst first

1. **No way to mark a draft sent once it sits on a row or the hero (Home, high; eval harness).** Ready for you skips drafts shown on rows, and its "Sent it" is the only one. Rows offer Done, Open in Gmail and Copy draft; Done marks the row and its promise, never the draft. Simulated: Done on the hero and the Orbit row empties the hero ("Handled"), brings both sent drafts back under Ready for you, and the next run closes the Orbit ask with only the board note on record, so its nudge never comes. The seed, the replay and `home_qa` write the sent mark straight into `state/items`, so QA never caught it. Fix: "Sent it" beside Open in Gmail wherever a draft shows, writing `done_at` on the draft id; keep the ask open ("Asked the team on 23 Oct"); have `home_qa` and the seed use that button.
2. **A refresh says "which has no notes" when an earlier run already read them (engine).** The met meeting's notes are looked up only in this run's bundle, and a morning brief reads notes only since the last run, so notes a 12:28 pulse read are missing next morning. Fix: also find notes for that meeting in Home (`snap/commitments` items with its `event_id`, and their `source_url`).
3. **Done on the hero leaves "Nothing urgent right now" above an urgent item, and the Portfolio hero ignores Done (Home).** Fix: promote the next visible item in `ranked_ids`; apply `isHidden` to the Portfolio hero.
4. **The push names Today's hero, but Tara's Home opens on Portfolio (Home).** Fix: open on Today when the latest run pushed the brief's hero that day, or count "due today" as urgent.
5. **Today's hero draft is not checked after meetings with the people it names (engine).** The guest list was written Thu 06:28; Tara met those founders at 14:30. The refresh test looks only for meetings with the recipient. Fix: flag a waiting draft when a meeting after it was written included people its body names, or at least add a check line to its context.
6. **The refresh rules collide on an old "this week" (skill text).** Read on Friday, "this week" means today, and any later date is a new promise no source holds. Fix: "offer the next working day and mark it as Instinct's suggestion, or drop the time", and use a date in the opener ("Good to see you on 22 Oct").
7. **Drafts to someone who owes the user do not ask for it (engine).** The CFO email to Rahul does not ask for the CTO job description he owes; "Invite Rahul to the founders dinner" never gets a draft ("invite" is not an email verb). Fix: add `they_owe` to an entry so the draft asks in one line; count "invite" as an email verb.
8. **Unclear whether a team note includes the partner who already agreed (skill text).** Fix: say so in pulse step 3 rule 1.
9. **"Runway under 9 months: Aditi said yes on 22 Oct" reads as if Aditi approved the runway (Home and engine copy).** "No warm path found yet" also stays after "Team note ready". Fix: "Aditi said yes on 22 Oct. Runway under 9 months"; drop the warm-path line once a team note is ready.
10. **The `bundle` shortcut returns Thursday 07:00 and the whole world (eval harness).** Fix: `bundle --now --mode`, reusing the replay's window.
11. **Thursday's seeded Home contradicts its own state (eval harness).** The seed adds the 10:00 "Sent it" after the last build. Fix: apply each tap at its time, through the page's own actions.
12. **The session scratchpad is shared (eval harness).** Fix: give each eval agent its own scratch folder.

## 6. Score: 7 out of 10 (as Tara)

What went right: the Orbit team note from last night's tap is ready, to the right five people, Vikram Nair in full, no runway figure, and it says Aditi's yes is not in mail; the CFO email names Thursday's meeting and asks her to check it; the push names a real deadline with a draft ready; Kestrel offers its own "Aditi said yes"; nothing lost an hour later. What lets her down: she lands on Portfolio, not the guest list the push named; the guest list was drafted before the meetings that shaped it; and once she sends the notes, Home gives her no "Sent it", only Done, which empties the hero and closes the Orbit ask.
