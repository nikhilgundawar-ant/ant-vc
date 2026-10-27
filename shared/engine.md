# The ant. engine

The engine is the deterministic core under every ant. skill. It resolves people, ranks the brief, watches the pipeline, scores inbound, checks commitments, flags portfolio and LP risk, decides what each scheduled run should do and writes ant. Home snapshots. It is plain Python 3.9 or later with no packages to install.

## Find it

The plugin root is `${CLAUDE_PLUGIN_ROOT}`. If that text still looks like a variable and not a real path, the plugin root is the folder two levels above the skill's base directory (shown when the skill loaded). The engine is `<plugin root>/engine/instinct.py`.

Work in a fresh folder in the session's working directory, never inside the plugin root. Copy the engine there once per session:

```bash
mkdir -p instinct-work && cd instinct-work
cp -r "<plugin root>/engine" ./instinct-engine && cp -r "<plugin root>/ontology" ./ontology && cp "<plugin root>/schedules.json" .
python3 -I -S instinct-engine/instinct.py check
```

Setup also needs the page: `cp -r "<plugin root>/home" ./home`. Run every later command from inside `instinct-work` (start each shell command with `cd instinct-work &&` if your shell does not keep the folder).

`check` prints `"ok": true` when Python and the copied files are in place. If the copy fails because the plugin files are not readable, say so in one line and continue without the engine: rank by judgment and mark the brief "built without the engine". Never download the engine from anywhere else.

Always run the engine isolated, `python3 -I -S instinct-engine/instinct.py ...`, from inside `instinct-work`: no site packages and no environment variables reach it. In a scheduled run the guard holds you to this shape:

- the engine as above, and only these file commands: `cd`, `mkdir -p`, `cp` (`-r`), `ls`, `cat`, `head`, `tail`, `wc`, `date`, `echo` and `test`, with their plain options;
- every path inside `instinct-work` (reads may also use the plugin's files);
- files written with the Write tool or a quoted heredoc (`cat > bundle.json <<'EOF'`), never into `instinct-engine`, which changes only by copying from the plugin;
- no variables, command substitution, brace expansion, environment changes or background jobs. `2>&1` is fine.

## The bundle

Every command reads a bundle: one JSON file holding what you gathered from the user's tools. Write only the fields below. Keep message text short: the latest message of each thread, and the user's own latest message in it when someone wrote after it (so ant. knows who answered last), each at most 600 characters. One exception: a thread of a note the user sent (a founder ask, a capital call chase or a note to a partner, each a draft in `snap/drafts` marked sent) keeps every message from the user's note on, so a reply is never lost behind a later thank-you. Leave a list out, or null, when its tool was not read this run; Home keeps what it already knows.

```json
{
  "now": "2026-10-22T07:00:00+05:30",
  "tz": "Asia/Kolkata",
  "user": {"name": "Aditi Rao", "email": "aditi@firm.vc"},
  "firm": {"name": "Firm name", "domain": "firm.vc", "fund": "Fund II", "fund_size_usd": 0, "members": [{"name": "", "email": "", "title": ""}]},
  "thesis": {"sectors": [], "sector_keywords": [], "stages": [], "check_min_usd": 0, "check_max_usd": 0, "geographies": [], "anti_patterns": []},
  "unavailable": {"crm": "revoked"},
  "threads": [{"id": "", "subject": "", "date": "", "url": "", "participants": [{"name": "", "email": ""}],
               "messages": [{"from": {"name": "", "email": ""}, "date": "", "text": ""}], "labels": []}],
  "events": [{"id": "", "title": "", "start": "", "end": "", "url": "", "attendees": [{"name": "", "email": ""}]}],
  "transcripts": [{"id": "", "event_id": "", "title": "", "date": "", "url": "", "attendees": [{"name": "", "email": ""}],
                   "lines": [{"speaker": "", "text": ""}]}],
  "crm": {"system": "affinity", "companies": [{"id": "", "name": "", "domain": "", "status": "portfolio|pipeline|passed|lp|fund|other", "sectors": [], "hq": "", "url": "", "description": "",
                 "entry_stage": "<portfolio only: the round we first invested in>", "check_usd": 0}],
          "people": [{"id": "", "name": "", "email": "", "company_id": "", "title": "", "url": "", "strength_by_member": {"colleague@firm.vc": 60}}],
          "deals": [{"id": "", "company_id": "", "company_name": "", "stage": "", "stage_entered": "YYYY-MM-DD", "owner": "email", "team": ["email"],
                     "round": "", "raise_usd": 0, "next_step": "", "next_step_due": "YYYY-MM-DD", "last_contact": "YYYY-MM-DD", "quiet": false, "url": ""}],
          "notes": [{"id": "", "deal_id": "", "text": "", "url": ""}]},
  "passes": [{"id": "", "company": "", "domain": "", "date": "YYYY-MM-DD", "reason": "", "revisit_trigger": "", "by": "", "source_url": ""}],
  "lps": [{"id": "", "name": "", "fund": "", "commitment_usd": 0, "called_usd": 0, "paid_in_usd": 0, "last_call_date": "YYYY-MM-DD",
           "owner": "colleague@firm.vc", "reup_window_start": "", "reup_window_end": "", "contacts": [""], "last_touch": "", "source_url": ""}],
  "portfolio_kpis": {"<company id>": [{"month": "2026-09", "revenue_usd": 0, "plan_revenue_usd": 0, "burn_usd": 0, "cash_usd": 0, "churn_pct": 0,
                                       "departures": [{"name": "", "role": ""}], "source_url": ""}]},
  "empathy_maps": {"Person Name": "https://drive.google.com/..."}
}
```

Rules for the bundle:

- Every thread, event, transcript, deal and note carries the `url` that opens it. Without a URL a line cannot appear in any output.
- Dates are ISO 8601. Datetimes carry the UTC offset.
- Use CRM ids and stage names exactly as the CRM shows them. The engine maps stage names to its own stages.
- `team` lists everyone working a deal besides its owner, when the CRM has it. Associates see deals they work on.
- On each LP, `fund`, `called_usd`, `paid_in_usd`, `last_call_date` and `owner` are optional; copy them when the LP list or fund admin sheet has them. With called capital, the LPs tab shows called and unfunded per LP and per fund, and an LP that has not paid a call gets a line. With an owner, only that colleague gets the LP's lines and drafts; everyone else sees it under "With your team".
- `crm.partial: true` says the deals list holds only deals changed since the last run; the engine takes the rest from Home.
- `crm.people_partial: true` says the people list holds only the people this run needed (at open deals, the portfolio and the next two days' meetings); `crm.companies_partial: true` the same for companies. The engine adds everyone else from Home's directory, the last wide read, and keeps the directory whole.
- `user`, `firm` and `thesis` may be left out: the engine takes them from the config.
- `unavailable` names each connector this run could not use, keyed `email`, `calendar`, `notes`, `crm`, `drive` or `lps`, with `revoked`, `rate_limited`, `missing` or `error`. Home then says so and keeps what it last knew instead of showing an empty view.
- Never invent a field value. Leave it out or set it to null.

## Commands

| Command | What it does |
| --- | --- |
| `check` | Confirms Python and the plugin files. |
| `setup --bundle B --out DIR [--tz TZ] [--brief-time 07:00] [--level auto] [--home-url URL]` | Resolves people, guesses the level (`level_guess.options` are the three likeliest, `recommend` is true only when the guess is sure), suggests a thesis, writes `DIR/config.json` and `DIR/setup.json`. |
| `due --home HOMEDIR [--config C] [--weekend]` | What this scheduled run should do: `run` (false when another run is still going), `jobs`, `build_mode`, `window_start`, `windows` (each connector's own start: a connector busy or down last run reads from its last good run), `run_id` and `started`. |
| `build --bundle B --config C --out DIR [--home HOMEDIR] [--versions V] [--extracted E] [--inbound I] [--kpis K] [--asks A] [--packs P] [--proposals R] [--drafts D] [--digest MD --digest-kind K] [--applied P] [--run-id ID --started T --jobs J] [--mode M]` | Builds every view. Writes `DIR/report.json`, `DIR/brief.md`, `DIR/brief-shareable.md`, `DIR/home/batch.json`, `DIR/home/run.json` and, in setup and daily mode, `DIR/owed.json`. Modes: setup, daily, pulse, week_ahead, review, digest, weekend. |
| `questions --out DIR --questions Q` | Puts the prep questions you wrote (`{"<meeting id>": [three questions]}`) into the build's cards and adds `snap/prep` to the batch. |
| `drafts --out DIR --drafts D` | Puts the drafts you saved for `owed.json` into `snap/drafts`, links each to its promise row, the hero and its meeting line, and adds both documents to the batch. |
| `actions --home HOMEDIR --now ISO` | Approvals to apply with a tool (`pending`), ones refused because they match no shown proposal (`refused`), and ones a stopped run may already have applied (`check_by_hand`). `--now` is the run's start; without it, the clock. A tap older than 30 days is never pending, and a step saved again after its last one was applied is pending again. |
| `validate-commitments --bundle B --extracted E` | Checks extracted commitments against the transcripts. |
| `triage --inbound I --thesis T [--passes P]` | Scores inbound companies against the thesis and the pass log. |
| `check-injection --inbound I` or `--text-file F` | A second opinion on hidden instructions. Your own reading decides; this only adds hits. |
| `memo-check --memo M --sources S` | Fails any memo claim without a source or with a number its source does not contain. |
| `letter-check --letter F` | Lists the sections a draft LP letter (markdown) still lacks, and any line that names paid-in capital. |
| `intro --bundle B --company-file F` | Ranked warm intro paths. Write the company name into a file first; never put a name from email on the command line. |
| `schedules --config C` | The two scheduled tasks for this user. |
| `tune --config C --home HOMEDIR [--out DIR]` | Weekly tuning from the ratings since the last tuning. |
| `lint --root DIR` | Fails any skill text that calls a send, delete or change tool. |

Inputs:

- `--versions`: the versions of the documents the read saved, as the read's result lines pasted into a file (`shared/home.md`, Read). Without it the build looks for `versions.txt` in the Home folder. A document whose version is unknown is written without one, and the store refuses that write when the document exists.
- `--packs`: post-meeting packs written this run, `[{"meeting_id", "company", "line"}]`, so the push names the follow-up once.
- `--extracted`: commitments you read from transcripts, `{"transcript_id", "owed_by", "owed_to", "what", "due", "quote"}`. The quote is copied word for word from one transcript line. `due` is an ISO date when a date was said, else null.
- `--inbound`: companies you read from pitch emails, `{"name", "domain", "sector", "stage", "raise_usd", "hq", "traction", "team", "thread_id", "source_url", "from", "injection_flag", "injection_quote", "body", "revisit_check"}`. `revisit_check` is `{"met": true|false, "evidence"}` for a pass-log company whose pitch says whether the revisit condition is met, else null.
- `--kpis`: `{"<company id>": [one row per month, as in portfolio_kpis]}` for founder updates you read this run.
- `--asks`: founder asks you read this run, `[{"company", "company_id", "ask", "who", "kind": "intro|hiring|customer|advice|other", "date", "source_url"}]`. Each needs a source link.
- `--digest`: the markdown of a review, pre-read, week ahead or digest you wrote this run, with `--digest-kind review|preread|week_ahead|digest`. Home shows it for a day and a half (the review and pre-read for a week).
- `--applied`: the result of every pending action this run handled, a draft kept in Home included (without it, `actions` lists the tap again next hour): `{"<action id>": {"status": "applied"}}`; `{"status": "applied", "already": ["<field>"]}` when a field already held the proposed value; `{"status": "applied", "skipped": ["<field>"], "reason": "<one line>"}` when someone changed a field since; or `{"status": "failed", "reason": "<one line>"}`.
- `--proposals`: CRM changes and calendar holds you propose this run, `{"<id>": proposal}` in the shape in `shared/home.md`. Each needs a source link; fields outside the allowed set are refused.
- `--drafts`: drafts you wrote or saved this run, `{"<id>": draft}` in the shape in `shared/home.md`. Each needs a body and a source link. A draft under an existing id replaces it.

Outputs worth knowing:

- `owed.json` (every build; runs other than setup and daily list only `narrow` entries and a `holder` with `rebuild`): emails the user owes. `{"id", "kind": "promise", "commitment_id", "to", "to_name", "what", "due", "overdue", "quote", "context", "source_url"}` for a promise due within two working days or overdue that is an email by nature; `{"id", "kind": "question", "question_id", "deal_id", "to", "to_name", "company", "question", "asked_on", "subject", "context", "source_url"}` for a founder on the user's own deal whose question (quoted word for word) has waited two working days or more with nothing from the firm since and no meeting since (up to three); `{"id", "kind": "inbound_reply", "inbound_id", "to", "company", "decision", "missing", "context", "source_url"}` for each new pitch when the level triages everything (up to twenty: a company back with what we asked for first, then the oldest pitch first), and for strong pitches ("call") at levels that triage their own. Never one already drafted, being drafted by a run that stopped, one that looks done, a flagged pitch, a founder the user met or booked, or an outcome before the meeting that decides it. An entry with both ids is one email to one person; an entry with `join` reuses the id of a draft already waiting for that person. `{"id", "kind": "letter", "commitment_id", "quarter", "to", "to_name", "what", "due", "inputs": {"funds", "portfolio", "flags", "new_investments", "pipeline"}, ...}` is the quarterly LP letter to draft from those figures (`letter-check --letter <file>` lists any missing section); `{"id", "kind": "lp_call", "action_ids", "lp", "fund", "to", "to_name", "outstanding_usd", "call_date", ...}` is a capital call still unpaid after two weeks, for the LP's owner; `{"id", "kind": "ask", "action_id", "note_kind", "company", "ask", "who", "path", "warning", "to", "to_name", ...}` is a founder's ask to finish with a note to the board partner (`board`, when cash is tight), the contact (`contact`), the colleague who knows them (`colleague`) or the firm members (`team`, `to` a comma list); keep `action_id` and `note_kind` on the draft; several asks for the same person come as one entry with `items`, `action_ids` and `note_kinds`. `{"id", "kind": "ask_nudge", "action_ids", "note_kind": "nudge", "nudge_of", "to", "to_name", "sent_on", "re", "items", ...}` is one short nudge for a note about founder asks with no reply in five working days: one per note, naming each ask it carried that still waits. A promise to set up a call with a colleague carries `with` and `cc`: the email copies them in and asks the founder for times. A promise to introduce two people carries the second one in `cc`. An entry with `also` writes to someone another of today's emails reaches too: both stay, with one line that links them. `{"id", "kind": "reslot", "body", "old_slots", "avoid_slots", ...}` is a draft waiting in Home whose times are today or earlier, and `{"id", "kind": "refresh", "body", "met_on", "met_title", "met_with", "notes_url", ...}` one written before a meeting with that person (`met_with` is who was in the room; `notes_url` the notes, when there are any, from this run's read or an earlier one), or with `named_only` before a meeting with people its body names; `{"id", "kind": "redate", "body", "words", "made_on", ...}` one that names a day which has come or gone ("this week", written last week); `{"id", "kind": "narrow", "action_ids", "items", "dropped", "sent_on", ...}` a nudge still waiting whose asks partly moved on, to rewrite for the asks left; with `promises` and `commitment_ids`, an email that keeps several promises, one closed since by Done (`dropped`), to rewrite for the promises left. `{"id", "kind": "holder", "to", "to_name", "items", "decisions", "rebuild"?, ...}` is one internal note to the partner whose view two or more things the user owes wait on: drafts (`items`, each with its `draft` id, at least one) and any decision due within two working days on their deals (`decisions`). Quiet deals never appear in it. One note per partner, under one id: while it waits it is rebuilt in place (`rebuild`) when what it names changes, and it waits until sent; once sent, no other note follows in the three working days after it went, and what it named is never asked again, answered or not (her reply in its thread is kept as `replied` on the note): a later note, under a new id, names only new drafts. Home keeps a sent note while a draft it names waits (up to 45 days) and drops it once every one is sent. An `ask_nudge` with `answered` follows a reply that answered the note's other asks (`companies`, `on`): it thanks them for those and asks only about `items`. All are rewritten under their own id. A promise's entry may carry `they_owe`: what the reader owes the user, late or due, for one line asking for it. A rewrite of a promise's draft also carries the promise (`what`, `due`, `overdue`), who holds the firm's view (`holder`) and what the old note asked of the user (`old_context`). `avoid_slots` on any entry that offers times lists the times other open drafts already offer.
- Prep cards for a partner sync or IC (`kind: "partner"`): `decisions` (each deal to decide, with why now, its deadline and who leads it) and the promises inside the team. Quiet deals are left out of them.
