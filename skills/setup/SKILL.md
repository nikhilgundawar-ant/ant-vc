---
name: setup
description: Sets up ant. for VCs end to end. Use when the user says "set up ant.", "install ant.", "set this up" about the ant-vc plugin or its GitHub link, "onboard me to ant.", or "continue ant. setup". Connects their tools, builds their private ant. Home, confirms three things, schedules two hourly loops and delivers the first brief.
metadata:
  version: "0.9.0"
---

# Set up ant. for VCs

Goal: the user connects their tools, answers three quick questions and approves two scheduled tasks. Everything else happens on its own, and the first brief lands in this conversation in about 10 minutes.

Plugin root: `${CLAUDE_PLUGIN_ROOT}`. If that is not a real path, use the folder two levels above this skill's base directory. Read `<plugin root>/shared/safety.md` now and follow it throughout.

## 0. Say what will happen

Send one short message before any tool call:

"Setting up ant. I'll check your tools, build your private ant. Home and send your first brief in about 10 minutes. You'll connect your tools, confirm three things and approve two scheduled checks.

What it does with your data: it reads your mail, calendar, notes and CRM to prepare your day. It drafts and proposes; nothing is sent, changed or deleted without your tap. What it builds lives in a private page in your Claude account that only you can open. Anthill runs no server, so nothing goes to Anthill. Say 'turn off ant.' any time to stop it and wipe its data."

If the user asks what ant. can and cannot do, show `<plugin root>/TRUST.md` as it is.

## 1. Prepare

1. Copy the engine and the page into a work folder as `<plugin root>/shared/engine.md` describes, and run `check`.
2. Get the current time and time zone with the current-time tool.
3. Resuming? Look for an artifact titled "ant. Home" (Artifact `list`) and scheduled tasks named "ant." or "ant. weekend". If Home exists, read its `snap/config`: steps whose results are there are done. Say "Picking up where we left off." and continue from the first step not done. Never publish a second Home.

## 2. Connect tools

1. List the user's connectors (ListConnectors). Map them to the categories in `<plugin root>/shared/connectors.md`.
2. Required: email and calendar. Recommended: meeting notes, CRM, Drive. Optional: Slack (read only), company data, Carta, DocSend.
3. If everything required and recommended is already connected, go to item 5 below. Otherwise search the registry (SearchMcpRegistry) with each missing category's keywords, then show all the matches in one SuggestConnectors call. Say: "Tap Connect on the tools you use and skip the rest. Each one asks you to sign in once."
4. Right after the cards, ask one AskUserQuestion: "Tell me when you're done connecting" with options "Done (Recommended)" and "Skip the rest for now". Check the connectors again after the answer. If email or calendar is still missing, say ant. needs both and stop here.
5. A connector that is connected but off in this chat: tell the user to switch it on in this chat's connector menu.
6. Look at the email connector's tools and say which way drafts will go, in one line. A tool that creates drafts: "Drafts will wait in your Gmail drafts." None: "Your Gmail connector can't save drafts, so drafts wait in ant. Home, one tap from a filled-in Gmail message." Nothing to save: every run looks at the tools again, so connecting a draft tool later just works.
7. When the CRM is a Google Sheet, say in one line: "Your CRM is a Google Sheet. ant. reads it and suggests changes, and you paste them in: it cannot write to a sheet." Set `crm_system` to `"sheet"` in the bundle's `crm.system`.

## 3. Read their world

Gather within the Setup windows in `<plugin root>/shared/connectors.md`. Keep to the caps there; setup is meant to take minutes.

- Who the user is: their email address and name from the mail or calendar profile.
- Firm: the user's email domain, the fund's name and its target size when the firm site, the LP list or the CRM says them (`firm.fund`, `firm.fund_size_usd`). Firm members are everyone at that domain who appears in mail, calendar, the CRM (deal owners and teams, relationship strengths) or as an LP owner in the LP list: the Head of Platform or the CFO may write little email. Titles from the CRM, email signatures or the firm site's team page when available.
- Mail, calendar, notes and CRM as listed.
- Thesis inputs: the firm website (fetch the domain's home page and its portfolio page), the CRM's portfolio companies with the round you first invested in and your check (`entry_stage`, `check_usd`) when the CRM has them, and the pass log (CRM notes or deals marked passed).

Write `bundle.json` in the shape in `<plugin root>/shared/engine.md`. Set `thesis` to your best draft from the website, investments and passes: sectors, sector keywords, stages, check range, geographies (as the regions the firm invests in, for example "india" or "us-india") and anti-patterns.

Then run:

```bash
python3 -I -S instinct-engine/instinct.py setup --bundle bundle.json --out setup-out --tz "<IANA zone>" --brief-time 07:00
```

## 4. Confirm three things

Ask all three at once with AskUserQuestion (or one plain message if that tool is missing). The tool shows at most four options a question and always lets the user type their own answer.

1. Level: "Which fits your work best?" Options: the levels in `level_guess.options` (two or three: the engine offers only levels the mail and calendar give evidence for), with their labels from `ontology/profiles.json`. Mark the first "(Recommended)" only when `level_guess.recommend` is true. The user can type another level (Partner, Principal, Associate, Analyst, Platform, Finance and IR, Solo GP).
2. Thesis: show the drafted thesis in two lines. Options: "Looks right (Recommended)", "Let me edit it".
3. Brief time: "07:00 (Recommended)", "06:30", "08:00", "09:00".

If they choose to edit the thesis, take their one-line edit. Write the answers into `setup-out/config.json`: `level`, `level_label`, `brief_time`, `thesis` with `"confirmed": true`. Load the matching profile's `today_items`, `brief_words`, `weights`, `modules`, `pipeline_scope` and `opens_on` into the config. Ask nothing else.

## 5. Publish ant. Home

1. Check this is the user's own conversation. Home holds their pipeline, LPs and promises; if this chat sits in a shared project, say Home will still be private to them, and carry on.
2. Read `./home/index.html` in full.
3. Publish it with the Artifact tool: `file_path` = that file, `icon` = "radar", `description` = "Your private ant. Home: today's brief and the views your level uses.", and capabilities:
   `{"db": {"rules": [{"path": "", "read": "owner", "write": "owner"}]}, "user": {}, "sample": {}, "mcp": {"servers": [{"server": "host:claude_browser", "tools": ["navigate", "get_page_text", "find", "computer"]}, {"server": "Google Drive", "tools": ["search_files", "create_file"]}]}}`
   `sample` lets Home answer questions about your data (Ask) on your own Claude account. `host:claude_browser` lets Home research the people you meet on LinkedIn in the Claude app's browser; Google Drive keeps each empathy map as a Doc. Leave the Google Drive entry out when Drive is not connected.
4. Put the returned link into `config.home_url`, then write `setup-out/config.json` to `snap/config` at once (ArtifactData `set`). If setup stops after this, the next "continue ant. setup" finds Home and its link.
5. Create `state/items` and `state/actions` as `{"items": {}}`, and `state/settings` as `{"items": {"auto_apply": true}}`, each only if it does not exist yet (a `get` first; never overwrite). With `auto_apply` on, CRM changes a run proposes from the user's own notes and holds on their own calendar apply at the next check without a tap, with Undo in Activity; Help in Home turns it off.

## 6. Build the first brief

1. Read meeting notes as step 3's window allows and extract commitments exactly as `skills/post-meeting/SKILL.md` step 3 describes. Save `extracted.json`.
2. Read inbound pitches from the last 7 days as `skills/inbound-triage/SKILL.md` step 2 describes. Save `inbound.json`.
3. Read founder updates from the last 60 days as `skills/portfolio-watch/SKILL.md` steps 2 and 4 describe. Save `kpis.json` and `asks.json`.
4. Read Home into `./home-db` (`shared/home.md`, Read), so the build knows the versions of what step 5 wrote. Then run:

```bash
python3 -I -S instinct-engine/instinct.py build --bundle bundle.json --config setup-out/config.json --home ./home-db --versions ./home-db/versions.txt --out run --mode setup \
  --extracted extracted.json --inbound inbound.json --kpis kpis.json --asks asks.json \
  --run-id r<now as YYYYMMDDTHHMM> --started <now, ISO with offset> --jobs setup,morning_brief
```

5. For each prep card in `run/home/snap__prep.json` for today and tomorrow, write three short questions from its `question_seeds`, history and deal, each ending with a question mark, and add them with the `questions` command (`skills/pulse/SKILL.md` step 5).
6. Create the run row (`<plugin root>/shared/home.md`, Write step 1), then draft what the user owes, as `skills/morning-brief/SKILL.md` step 6 describes, so the first brief already has its emails written.
7. Write the snapshots to ant. Home as `<plugin root>/shared/home.md` describes, then finish the run row from `run/home/run.json` (Write step 4). It tells the first scheduled check that today's brief is done.

## 7. Schedule the two checks

0. Check that the ant-vc `pulse` skill is in your skill list. If it is not, this setup is running from a copy of the repository: the scheduled checks would start in sessions without ant. Skip this step, say "Your Home and first brief are ready. The hourly checks need the ant. plugin installed: tap Accept on the plugin card, then say 'continue ant. setup'.", and go to step 8.
1. Run `python3 -I -S instinct-engine/instinct.py schedules --config setup-out/config.json`. It returns two tasks: "ant." (hourly on weekdays from the brief time) and "ant. weekend" (three times a day). Each run decides for itself what is due: the morning brief, the Thursday review, the Monday digest, Sunday tuning and the week ahead. If `home_url` is missing, go back to step 5; a task without the Home link cannot run.
2. Find this session's scheduling tool (search your tools for "scheduled task"; never use a session-only cron tool). Create both tasks with their `name`, `cron_expression`, `prompt` and `notifications`, and `initiation` set to `human_request` when the tool asks for it (the user asked for this setup). Set nothing else: the minute in the cron is deliberate, so keep it as given. Skip a task that already exists with the same name.
3. Read each result's approval setting. If runs will ask before acting, say in one line: "Your two ant. checks will pause for approval each time. To let them run on their own, open Scheduled tasks, pick 'ant.' and 'ant. weekend', and switch on Automatically approve. A guard then lets them only read your tools, update Home, change CRM fields and notes, hold time on your own calendar and keep drafts for you. Everything else is blocked, and they change only what you approved in Home." If they already approve automatically, say: "Your two ant. checks will run on their own. A guard lets them only read your tools, update Home, change CRM fields and notes, hold time on your own calendar and keep drafts for you. Everything else is blocked, and they change only what you approved in Home."

## 8. Remember only what they confirmed

If a memory tool is available, save one short note: ant. Home link, level, brief time and, when they confirmed it, the thesis in one line. Save nothing about people, deals or email content.

## 9. Hand over

Show the first brief in chat: the hero card, today's meetings and the top items, each line with its source link. Then one closing message:

"ant. is live. Your Home has today's brief and your <the level's other tabs, joined as a list: "pipeline, people and portfolio">. <When Home holds changes or drafts: "<n> drafts wait under Send and <m> CRM changes under Decide; nothing happens until you tap.">. <When no founder update was read: "Portfolio fills in as founder updates arrive.">. Next brief: <the build report's `next_brief`, such as "07:00 tomorrow" or "Mon 07:00">. I check in every hour on weekdays and three times a day at weekends. Say 'pin ant.' to keep Home in your sidebar, or 'turn off ant.' any time."

List only the tabs the user's level has, and leave out a sentence in angle brackets when it does not apply.

Then two more lines: "ant. works by itself: it drafts what you owe, applies CRM changes from your notes, and researches the people you meet. It never sends an email for you. Undo anything from Activity in Home." and, only when the Claude app's built-in browser is available, "Sign in to LinkedIn once in the Claude app's browser. Each time you open Home in the desktop app, it researches today's and tomorrow's meetings by itself. Press / on any screen to ask about your data."

## When things go wrong

- A connector errors mid-read: note which one, finish with the rest, and list it under "Not connected yet" in the closing message.
- The artifact or scheduling tool is missing in this session: finish everything else, then say which step needs the Claude app and how to resume ("continue ant. setup").
- Never retry a failed step more than once.
