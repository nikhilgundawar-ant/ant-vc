# Connectors: what to read from each tool

Tool names differ between accounts. Search your tools for the connector by name (for example with ToolSearch) and go by each tool's own description. These are the usual names.

| Need | Connector | Usual tools | What to read |
| --- | --- | --- | --- |
| Email | Gmail (or Microsoft 365) | `search_threads`, `get_thread`, and `create_draft` when the connector has it | Threads in the window: id, subject, date, participants, URL, and the latest message text. Full text only for threads with founders of open deals, LPs, portfolio updates and inbound pitches. |
| Calendar | Google Calendar | `list_events`, `search_events` | Events in the window with attendees and the event link. |
| Meeting notes | Granola, Zoom, Fathom, Fireflies, Otter | `list_meetings`, `get_meetings`, `get_meeting_transcript` | Meetings in the window; full transcripts for those the skill needs. |
| CRM | Affinity, Attio, HubSpot, Salesforce, Airtable, Notion | list, search, get record | Companies, people (with relationship strength when the CRM has it), deals with stage, stage date, owner, deal team, next step, last contact, notes. |
| Files | Google Drive, DocSend, Notion | `search_files`, `read_file_content` | Data room files, LP lists and founder updates named in a thread or deal. |
| Chat | Slack | `slack_search_public_and_private`, `slack_read_thread` | Founder asks and deal chatter. Read only. |
| Company data | PitchBook, Harmonic, Crunchbase | search, profile | Funding history, investors, sector, HQ for inbound and memos. Web search if none is connected. |
| Fund data | Carta | discover, fetch | LPs, commitments, capital accounts for the LP view. |

## Windows

`<window start>` is each connector's own start in the `windows` the `due` command returns (`email`, `calendar`, `notes`, `crm`, `drive`, `lps`): when the last finished run that read that connector began, at most three days back. A connector that was busy or down last hour is read again from its last good read, so nothing is skipped. `window_start` is the same for a run where every connector worked. A run by hand runs `due` just for this. A first build (Home has config but no brief yet) reads the Setup windows.

"Full text" in this table is what you read to extract commitments, pitches and KPIs. The bundle keeps less: the latest message of each thread, and the user's own latest message in it when someone wrote after it, each up to 600 characters.

| Run | Email | Calendar | Notes | CRM and other data |
| --- | --- | --- | --- | --- |
| Setup | 60 days, up to 150 threads with full text for founders, LPs and pitches | 90 days back, 14 ahead | 90 days listed; full transcripts for the 10 latest meetings with notes, internal ones included (promises between colleagues count) | Everything: companies, people, deals, pass log, LP list |
| Morning brief | 7 days | 30 days back to 14 days ahead, every event with its attendees (the agenda is today and tomorrow; the past tells which drafts predate a meeting, the rest shows booked calls and gives two free slots per call offer) | since the window start | Open deals and their companies, portfolio companies, the pass log, the LP list when LP watch is on, and CRM people at those companies and at the meetings of today and the next working day (a Friday reaches Monday), with their titles. Set `crm.people_partial: true` (and `crm.companies_partial: true` when you read only those companies): Home keeps everyone else from the last wide read (setup, the Monday digest), so the bundle stays small enough to write by hand. When Home has no `snap/directory` yet (the first morning after an update), read people and companies wide this once, with no partial flags, or warm paths are lost. Then compare with Home's `snap/pipeline`: a deal Home shows open that the CRM's open list lacks may have closed, so read its record and send it with its stage. The engine never closes a deal for being left out; it keeps it and warns. At a level with the pipeline off (`snap/config` modules: Platform, Finance), read deals as a pulse does (only those changed since the window start, with `crm.partial: true`), and companies and people only for the portfolio and the next working day's meetings: Home keeps the rest |
| Pulse | since the window start, plus 7 days of threads with founders of open deals (their domains are on the deals in Home's `snap/pipeline`), and the whole thread of each note the user sent that waits on an answer (a founder ask, a capital call chase, a note to a partner: drafts in `snap/drafts` marked sent with no `replied` yet), from the user's note on | today to the end of the next working day (a Friday reads to Monday) | since the window start | Deals changed since the window start, with `crm.partial: true`: the engine takes the rest from Home. If the CRM cannot filter by update time, compare its open deals with Home's `snap/pipeline` and send only the new ones and those whose stage (by meaning: "First Meeting" and "First meeting" are one stage), next step, its date or last contact (Home's `crm_last_contact`, the CRM's own value) differ, still with `crm.partial: true`; a deal Home shows open that the CRM no longer lists as open goes in with its record's stage |
| Weekend pulse | since the window start | today to Monday | since the window start | Deals changed since the window start (`crm.partial: true`) |
| Monday digest | 120 days, metadata only | 120 days back | none | People, portfolio companies, LP list |
| Thursday review, Sunday week ahead | 14 days with founders of open deals | 14 days back, 7 ahead | 14 days | Every open deal |
| Inbound triage, run by hand | 7 days (as setup reads) | 14 days ahead (for call slots) | none | Companies, deals, pass log |
| Portfolio watch or LP watch, run by hand | 45 days (75 on a first run) | 7 days ahead | 30 days | Portfolio companies, LPs |

Within any window, also read new pitches (for triage), new founder updates (for KPIs and asks) and any reply to a promise ant. is tracking.

The pass log is the CRM's record of companies the firm passed on: deals at a Passed (or Lost, Declined) stage with their note, or a list or view named for passes. Each entry needs the company, its domain, the date, the reason and, when the note gives one, the revisit trigger ("revisit if ..."). With a sheet or Notion as the CRM, it is the rows marked passed.

Leave out of the bundle what a run does not read: no `lps` key in a pulse, no `companies` when you read only deals. Home keeps those views as they were. Never send an empty list to mean "not read": an empty list means "read, and nothing there" (`"transcripts": []` when no new notes came in).

## When a connector is missing or fails

- Gmail and Google Calendar are required. Without them at setup, say so and stop after offering the Connect card.
- A connector that errors, is rate limited or was revoked during a run: add it to the bundle's `unavailable` (see `shared/engine.md`) and carry on. Home says so and keeps what it last knew; the push goes out once.
- Without a notes tool, skip post-meeting packs and say "Connect Granola or your notes tool to get post-meeting packs".
- A Google Sheet or a Notion database works as the CRM. Read one row per deal: company, stage, the date it entered the stage, owner, next step and its date, last contact and a link to the row. Map the column names once at setup and keep them in `snap/config` (`crm_system: "sheet"` or `"notion"`).
- Without any CRM, the ant. Home pipeline becomes the pipeline. Deals come from email and calendar, stages start at Inbound, and the user moves them with one tap.
- Without company data, use web search and mark the source, in setup and runs the user started only. Scheduled runs cannot reach the web: leave the field null.
