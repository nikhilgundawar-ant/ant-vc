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
- **Writes:** email drafts (in your Gmail drafts when your Gmail connector can create them, otherwise in Home, one tap from a filled-in Gmail message), and the changes you approve in ant. Home. Nothing is sent, shared, changed or deleted without your tap.
- **Guard:** the hourly checks run on an allowlist. They may read your tools, update the one ant. Home named in the check, change CRM fields and notes, put one-off holds on your own calendar with nobody invited, save new drafts and run ant.'s own engine on files in its work folder. Everything else is blocked, including sending, web requests, your devices, other files and writing to other apps, even if an email asks for it. The guard judges each connector tool by its name, not by what the tool does inside, so the real-account check runs every connector's tools through it first. The guard cannot see your approvals: the engine lists only the changes you approved, and the checks apply only those. A CRM field change can set off your CRM's own automations, such as an email or Slack alert you set up there. Each check first makes one call the guard must refuse; if that call goes through, the check stops before reading anything and Home says so.
- **Keeps:** everything it builds lives in ant. Home, a private page in your Claude account that only you can open. Anthill runs no server, so nothing goes to Anthill.
- **Stops:** say "turn off ant." to stop the checks and wipe its data.

The one-screen version, for anyone deciding whether to turn it on: [Privacy and trust](TRUST.md).

Home opens in light mode. The switch in its header turns on dark mode, and Home remembers your choice.

## Install

- In the Claude app: download `ant-vc.plugin` from the latest release, open it, and tap Accept. Then say "set up ant.".
- In Claude Code:

```
/plugin marketplace add nikhilgundawar-ant/ant-vc
/plugin install ant-vc@anthill
```

Built by Anthill AI. MIT license. Privacy: [PRIVACY.md](PRIVACY.md). Claude: read CLAUDE.md to install.
