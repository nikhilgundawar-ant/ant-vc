# ant. Home and its database

ant. Home is one private artifact page. Its database holds what the user sees. Every run reads it first and writes fresh snapshots last. The page and the runs never write the same document, so they never overwrite each other.

| Collection / document | Written by | Holds |
| --- | --- | --- |
| `snap/config` | Setup and settings; the Sunday tuning merges in only its tuned fields | Level, firm, time zone, brief time, modules, weights, Home link, `tuned_at` |
| `snap/brief` | ant. runs | Today: hero card, sections, meetings, tomorrow, connectors that failed, the copyable brief; `cap` and `can_wait` keep Today at its item cap when a pushed line is put back, and the line for promises more than a week late carries `fold_rows` |
| `snap/prep` | ant. runs | Prep cards by meeting id |
| `snap/pipeline` | ant. runs | Deals with stage, days in stage, owner, team, stale reasons, competing-fund flags, quiet marks; `step_went` when the CRM's next step is a promise you marked sent (the row says "Sent 23 Oct", never "Next:") |
| `snap/people` | ant. runs | Top relationships and who is going cold |
| `snap/portfolio` | ant. runs | KPI table, flags, board prep, KPI history |
| `snap/asks` | ant. runs | Founder asks, open and done |
| `snap/lps` | ant. runs | LPs, last touch, re-up windows, called and unfunded capital, owners, alerts (yours and your team's), fund summary |
| `snap/commitments` | ant. runs | Every commitment found, with status (and `sent` when Sent it closed it); `sent_steps`, what Sent it closed by company and words, kept 90 days |
| `snap/inbound` | ant. runs | Inbound triage results for 14 days |
| `snap/digests` | ant. runs | The latest weekly review, pre-read, week ahead and Monday digest |
| `snap/drafts` | ant. runs, through the build's `--drafts` | Follow-up and reply drafts with a Copy button |
| `snap/proposals` | ant. runs, through the build's `--proposals` | CRM changes proposed, approved, applied (in full or in part), failed or to check |
| `snap/scorecard` | Tuning | Weekly scores and the change note |
| `snap/review` | ant. runs | People who might be the same person |
| `snap/research` | ant. Home itself (opened in the Claude desktop app) and the research skill in chat | Empathy maps by attendee: `{"people": {"<email or name>": {"name", "headline", "says", "thinks", "does", "feels", "company", "points": [3 lines], "source_url", "read_at", "drive_url"?, "auto"?}}, "tried": {"<key>": "<when a read failed>"}}`. Home shows a person's map on every prep card that has them. Scheduled runs never write it |
| `state/items` | The page only | Snoozes and done marks: `{"items": {"<id>": {"snoozed_until": "", "done_at": "", "sent"?: true, "closed_by"?: "done", "t"?: "<title>", "g"?: "<row id>", "at"?: "", "undone"?: "", "uc"?: ""}}}`. `t`, `g` and `at` let Activity list each tap (one entry per row id `g`); a tap undone from Activity clears its marks and keeps `undone` (when) and `uc` (what it was). Sent it marks a draft `sent`; Done on a row marks `closed_by: "done"` and never marks a draft that keeps another open promise, so only a sent draft closes the promises it keeps |
| `state/actions` | The page only | Approvals and next steps: `{"items": {"<id>": {"type": "", "status": "approved", "payload": {}, "at": ""}}}`. Types the pulse applies with a tool: `crm_update`, `next_step`, `calendar_hold`, `draft`. Types the engine applies itself: `merge`, `keep_apart`, `quiet`, `skip`. A withdrawn tap has status `withdrawn` (and `withdrawn_at`). `t` is a short title for Activity. Undo of an applied CRM change is `rv_<action id>` with type `revert` and `{"of": "<action id>"}`: the engine turns it into a `crm_update` that puts each field back while the record still holds what ant. wrote (notes stay). Undo of an applied next step is a new `next_step` under `rv_<action id>` with the old step as `text` and the step ant. wrote as `current`. A met log's id names its meeting, `ns_<deal id>_<met date>`, and the step added after a log saved without one is `nss_<deal id>_<met date>`. |
| `snap/connectors` | Setup and each check | The connectors the last check could use: `{"checked_at", "items": [{"name", "category", "ok"}]}`. Home's Settings shows them |
| `state/settings` | The page, setup and settings | `{"items": {"auto_apply": true, "access": {"email": "drafts|read|off", "calendar": "holds|read|off", "notes": "read|off", "crm": "update|read|off", "drive": "save|read|off", "chat": "read|off", "data": "read|off"}}}`. `access` is what ant. may do with each kind of tool (Home, Settings); the engine refuses CRM and calendar changes set to read only, and a check skips a kind set to off. `auto_apply`: CRM changes and own-calendar holds a run proposes apply without a tap (the engine's `actions` lists them as pending with `auto: true`); a skipped or withdrawn one never does |
| `ratings/<id>` | The page only | One rating per tap: `{"item_id", "kind", "group", "value": "useful|not_useful|wrong", "at"}`. The Friday score is a rating with kind `weekly_score` and a value from 0 to 10. |
| `runs/<id>` | ant. runs | One row per scheduled run: `started`, `jobs`, `applying`, then `finished`, counts, warnings and the push |

Runs never write `state/*` or `ratings/*` (tuning may delete old ratings). In a scheduled run a guard blocks those writes, and any tool that sends, shares or deletes.

## Shapes the page reads

- A proposal in `snap/proposals.items`: `{"type": "crm_update", "status": "proposed|approved|applied|failed|check", "title": "next step from the 15 Oct call", "record": {"type": "deal", "id": "<CRM id>", "name": "<company>"}, "fields": [{"field": "next_step", "current": "...", "proposed": "..."}], "source_label": "Meeting notes", "source_url": "<link>"}`. A calendar hold: `{"type": "calendar_hold", "status": "proposed", "title": "", "event": {"title": "", "start": "", "end": ""}, "attendees": [], "source_label": "", "source_url": ""}`. A hold invites nobody: it sits on the user's own calendar.
- Fields a CRM proposal may change: `stage`, `next_step`, `next_step_due`, `note`, `notes`, `round`, `amount`, `last_contact`. The engine refuses anything else.
- A draft in `snap/drafts.items`: `{"to_name", "to", "cc"?, "subject", "body", "context": "<one line on why, and what to check before it goes>", "source_label", "source_url", "in_gmail": true|false, "gmail_url"?, "commitment_id"?, "inbound_id"?, "question_id"?, "action_id"?, "action_ids"?, "note_kind"?, "note_kinds"?, "slots"?}`, plus what the drafts command adds: `commitment_ids` (every promise one email keeps), `asks_for` (what the reader owes the user that the email asks for), `first_made_at`, and for a note to a partner `kind: "holder"` with `holds` (the drafts it asks about), `decisions` and, once they answer, `replied`. `slots` is the ISO start of each time the draft offers. `note_kind` says who a founder ask's note goes to (`board`, `contact`, `colleague`, `team`, or `nudge` for a nudge); `to` may then be a comma list. A note that carries several asks lists every ask's tap in `action_ids`, with each ask's kind in `note_kinds`. A draft can carry two ids: one email to one person. A draft with `commitment_id` shows as "Draft ready" on that promise's row, one with `inbound_id` as "Reply ready" on that pitch, one with `question_id` as "Reply ready" on that founder's waiting question, and one written for a tap carries that tap's `action_id` (its id is `dr_<action id>`), so the tapped row shows "Draft ready". A draft that leaves bracketed lines to fill shows "Fill in N lines" instead, and its `context` shows under its buttons. A founder ask's later notes have their own taps, `<ask row id>_intro` ("<partner> said yes: draft the intro ask") and `<ask row id>_team` ("Ask the team instead", "<partner> said yes: ask the team"), and a note's one nudge is `<that note's tap>_nudge` (written by the morning brief, never from a tap), so a new note never takes the id of one already marked sent. "The same person" means the same single address in `to` or `cc`; a team note never merges with a one-to-one draft, and a draft that keeps a promise (`commitment_id`) is never rewritten to fit another one in. An introduction goes to both people: one in `to`, the other in `cc`. When `in_gmail` is false, Home's "Open in Gmail" opens a new Gmail message already filled in (with `cc` when there is one), ready to send.
- A prep card's `questions`: exactly three short questions, each ending with a question mark. A partner sync card has `kind: "partner"` and a `decisions` list instead of a deal.

## Read

Use the ArtifactData tool with the Home link from the scheduled task's prompt or `snap/config`. Save the documents as files in the work folder, so the engine can read them as `./home-db` from inside `instinct-work`. Give `out_dir` as an absolute path: run `cd instinct-work && pwd` once and use `<that path>/home-db`. A tool may resolve a relative path from somewhere else, and in a scheduled run the guard refuses a read saved outside the work folder.

1. `ArtifactData` action `list`, collection `snap`, `query` `{"limit": 100}`, `out_dir` = `<work folder>/home-db`.
2. Same for `state`.
3. Runs: action `query` (only a query can be ordered), collection `runs`, `query` `{"order_by": {"field": "started", "direction": "desc"}, "limit": 60}`, `out_dir` = `<work folder>/home-db`.
4. Ratings only for tuning: `list` collection `ratings`, paging with `query.cursor` until there is no `next_cursor`.

The saved files hold each document's body (some tools save `{"data": ..., "version": ...}` instead; the engine reads either). Its version is in the read's result, one line per document (`"brief"  8810 bytes  version 3  "<path>"`). Copy the result lines of the `snap` and `state` reads into `./home-db/versions.txt` exactly as shown, and pass `--versions ./home-db/versions.txt` to the build: every write to a document that exists needs its version, and a write without one is refused.

Pass `--home ./home-db` to the engine. If a read fails, say so in the run row and stop the run: building without Home would overwrite what the user sees with less.

## Write

1. At the start of a scheduled run, create its row: `ArtifactData` `set` on `runs/<run_id>` with `{"started": "<started>", "jobs": [...]}` (both from the `due` command). Keep the version the result returns.
2. Before each tool call that applies an approval, `update` the row with `{"applying": {"<action id>": "<now>"}}`, pinned to the version you hold. Before each draft you save to Gmail, do the same with `{"drafting": {"<owed id>": "<now>"}}`. Updates merge nested maps, so each mark adds one key. One mark per approval, even when one CRM call applies several of its fields. The marks stay on the row: the result goes to `snap/proposals` through the build's `--applied`, and a mark whose action has no result there tells the next run not to repeat that call (the CRM or Gmail may already hold it).
3. The engine writes `OUT/home/batch.json`: entries with `op`, `collection`, `doc_id`, `file_path` and, when the document already exists, `if_version`. Documents that did not change are left out. Call `ArtifactData` action `batch` once per batch with those writes. If a write fails with a version conflict, read that one document again, take its new version, and write it again once. Never pass `force`.
4. Finish the row: `update` `runs/<run_id>` with `file_path` set to `<work folder>/OUT/home/run.json`, an absolute path like the reads' `out_dir` (pinned to your version). It holds `finished`, counts, warnings, connectors that failed, the push line and the push key, which stop the next run pushing the same thing.

Every `file_path` and `out_dir` you give ArtifactData is an absolute path inside the work folder (the batch's paths already are). In a scheduled run the guard refuses one anywhere else.

## Create once

`state/items` and `state/actions` belong to the page. Setup creates each as `{"items": {}}` only if it does not exist yet; a later setup never overwrites them.

## Size and limits

- Each document stays under 256 KiB; the engine trims the oldest entries first.
- The store holds 25,000 documents. Tuning deletes ratings older than 60 days and runs beyond the newest 200.
- The page is private to its owner. Database rules give read and write to the owner only. Never change them.
