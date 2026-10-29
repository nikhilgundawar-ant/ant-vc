# ant. for VCs

A proactive chief of staff for your fund, inside the Claude app. Private to you.

1. In the Claude app, paste this repository's link and say "Install ant.". Tap Accept on the plugin card.
2. Connect your tools when asked: email and calendar, plus meeting notes and your CRM if you use them. Each asks you to sign in once.
3. Answer three quick questions: your role, your thesis, your brief time.
4. Approve two scheduled checks, "ant." and "ant. weekend". Switch on automatic approval for them so they run on their own.

Your first brief arrives in about 10 minutes. Then: a morning brief, prep before each meeting, follow-ups after, and at most four pushes a day, never in a meeting.

**See it first:** a [sample ant. Home](https://claude.ai/artifact/8SzHVyrLnoTVkSiaGSxXZW) for Quillwater Ventures, a fictional fund, with a view for each role: partner, principal, associate, analyst, platform, CFO and a solo GP.

## What it does with your data

- **Reads:** your email, calendar, meeting notes and CRM (a Google Sheet or Notion database works as a CRM; with a sheet, ant. suggests changes and you paste them in), through the connectors you approve.
- **Writes:** email drafts (in your Gmail drafts when your Gmail connector can create them, otherwise in Home, one tap from a filled-in Gmail message), and CRM changes from your notes (automatically, with Undo, or after your Approve if you turn automatic mode off). Nothing is sent, shared or deleted without your tap.
- **Guard:** the hourly checks run on an allowlist. They may read your tools, update the one ant. Home named in the check, change CRM fields and notes, put one-off holds on your own calendar with nobody invited, save new drafts and run ant.'s own engine on files in its work folder. Everything else is blocked, including sending, web requests, your devices, other files and writing to other apps, even if an email asks for it. The guard judges each connector tool by its name, not by what the tool does inside, so the real-account check runs every connector's tools through it first. The guard cannot see your approvals: the engine lists only the changes you approved, and the checks apply only those. A CRM field change can set off your CRM's own automations, such as an email or Slack alert you set up there. Each check first makes one call the guard must refuse; if that call goes through, the check stops before reading anything and Home says so.
- **Keeps:** everything it builds lives in ant. Home, a private page in your Claude account that only you can open. Anthill runs no server, so nothing goes to Anthill.
- **Stops:** say "turn off ant." to stop the checks and wipe its data.

The one-screen version, for anyone deciding whether to turn it on: [Privacy and trust](TRUST.md).

How ant. Home reads:

- **Today** starts with your day as four pills with counts (Meetings, Decisions, Threads, Waiting on others), then the one thing that matters most, your schedule, and sections by what you do: Decisions, Threads, Waiting on others, Watch and Done today. Every row has a done circle on the left and its actions as pills on the right (under the line on a phone); meeting notes open in a side panel with a TL;DR.
- **Side panels everywhere.** Tap any row, deal, pitch, person, portfolio company or LP: a TL;DR (and for a decision, a recommendation and why), each line citing a vertical timeline where every event links to its source; the draft, editable, with your team a tap away to copy in, sent from Home after you confirm the recipients; a founder's 360 (empathy map, career, track record, company, market, competitors, deck and model); and a PDF of the panel.
- **Reminders.** A floating Ask button and a bell on every screen. Add "chase Atlas tomorrow at 5pm"; ant. finds what bears on it at every check and briefs you when it is due.
- **Ask** answers as a lead line, points, tables and charts, with Quick, Balanced, Thorough or your own model and effort.
- **Every section folds.** Tap its title. A folded section still shows its count, how many lines are urgent and its top line. Focus folds everything but the top line and your schedule.
- **Activity** (the clock at the top) lists every tap for 90 days, by day and kind, with Undo. A change still waiting is withdrawn. A CRM change already made is put back at the next check. A sent email cannot be unsent.
- **Research runs by itself.** Each time you open Home in the Claude desktop app, it reads the public LinkedIn profiles of the people in today's and tomorrow's external meetings, in the app's browser, and adds an empathy map to each prep card and a Google Doc to Drive.
- **Ask** (the search icon, or press /) works on every screen: matches in your data as you type, and answers to questions about your deals, people, portfolio and LPs.
- **Automatic mode** (on from setup): CRM changes from your notes and holds on your own calendar apply at the next check, with Undo in Activity. Emails are never sent for you.
- Home follows your device's light or dark setting until you pick one. Help sets the theme, Comfortable or Compact text, and keyboard shortcuts.

## Install

- In the Claude app: download `ant-vc.plugin` from the latest release, open it, and tap Accept. Then say "set up ant.".
- In Claude Code:

```
/plugin marketplace add nikhilgundawar-ant/ant-vc
/plugin install ant-vc@anthill
```

Built by Anthill AI. MIT license. Privacy: [PRIVACY.md](PRIVACY.md). Claude: read CLAUDE.md to install.
