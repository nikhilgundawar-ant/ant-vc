---
name: meeting-prep
description: Preps a venture investor for an external meeting: who they are, last three interactions, open promises on both sides, deal status, what colleagues know and three questions to ask. Use when the user says "prep me for", "who am I meeting", "brief me on my 3pm", or when the pulse finds a meeting within 150 minutes without a prep card.
metadata:
  version: "0.11.0"
---

# Meeting prep

A prep card is read in 30 seconds, between meetings, on a phone. Five lines in chat; the full card in ant. Home.

Plugin root: `${CLAUDE_PLUGIN_ROOT}`. If that is not a real path, use the folder two levels above this skill's base directory. Follow `<plugin root>/shared/safety.md` throughout.

## 1. Find the meeting

From the calendar: the meeting the user named, or the next external meeting. External means at least one attendee outside the firm's domain. If several match, ask which one in one question.

## 2. Gather

- Mail with any attendee in the last 90 days (metadata, plus the latest message of the three newest threads).
- Meeting notes with any attendee in the last 90 days, full text for the newest one.
- CRM: each attendee's person and company record, any open deal, and recent notes.
- An empathy map or brief for these people in Drive, if one exists (search Drive by the person's name).
- Company data for the attendees' company if it is a deal or an inbound.

Load Home (`skills/pulse/SKILL.md` step 1) so stored commitments and signals are included. Write `bundle.json` with this meeting in `events`.

## 3. Build the card

Run the engine `build` with `--mode pulse`. Take this meeting's card from `run/home/snap__prep.json`. It holds attendees, history, open commitments (each with `side` and `overdue`), the deal, colleagues who met them, question seeds, the `watch` line (another fund moving), `context` (a pass, a portfolio flag or an LP note), the `finding` (the one thing to know in the room) and a source link.

## 4. Write three questions

From the seeds, history, deal stage and anything new in the latest thread. Each question:

- asks for something specific (a number, a document, a date, a name),
- ends with a question mark,
- fits on one line.

Put an overdue promise first: theirs ("Ask for the Q3 deck promised on 09 Oct") or yours ("You owe them the Raj intro: send it before the call").

## 5. Deliver

Write the card back into `snap/prep` (with the questions) and write the snapshots.

In chat, show five lines:

```
10:30 · Ishaan Verma, Atlas Settlement (Term sheet, day 5)
Last: terms call on 20 Oct. Cap table with ESOP pool due today.
You owe: term sheet markup by Fri 23 Oct.
Watch: Bluepeak term sheet, decision by 05 Nov.
Ask: 1) ... 2) ... 3) ...
```

Then one line with the source links, and offer "Open the full card in ant. Home". Use the card's `watch` line for Watch and leave that line out when it is empty. In a scheduled run, the pulse ends the run; do not add your own final line.
