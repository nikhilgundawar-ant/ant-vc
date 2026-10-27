---
name: post-meeting
description: Turns a finished meeting's notes or transcript into a post-meeting pack for a venture investor: a three-line summary, decisions, every commitment with owner and due date, proposed CRM updates and a follow-up email draft. Use when the user says "process my last call", "what did we agree", "follow up on my meeting with", or when the pulse finds new meeting notes.
metadata:
  version: "0.7.8"
---

# Post-meeting pack

Promises made in meetings are where deals are won and trust is lost. This skill catches every promise, in both directions, and nothing that is not a promise.

Plugin root: `${CLAUDE_PLUGIN_ROOT}`. If that is not a real path, use the folder two levels above this skill's base directory. Follow `<plugin root>/shared/safety.md` throughout.

## 1. Find the meeting

The meeting the user named, or every meeting whose notes arrived since the last run. Read the full transcript with the notes tool. If only a summary exists, work from the summary and say so.

## 2. Load

Copy the engine and read Home (`skills/pulse/SKILL.md` step 1).

## 3. Extract commitments

Read every line. A commitment is a specific promise, made by a person in the meeting, to do something for someone else, now or by a date. Extract it when all of these hold:

- the speaker commits to an action: "I'll send", "we'll share", "I will intro you", "you'll have it by", "let me get you", or promises their own deliverable without "I": "the audit report will be with you by Wednesday";
- the person who owes it is a meeting participant (usually the speaker; "I'll" means the speaker);
- it is about the future.

Promises between colleagues count too (the engine marks them internal). A promise with no named recipient ("I'll have the NAV pack ready by the 25th") is owed to the person the speaker was answering, or to the meeting's lead from the other side.

Do not extract:

- past actions: "I sent the deck last week";
- hypotheticals and conditions: "if we move to term sheet, we'd want..", "we'd want a board seat if we lead";
- vague intentions with no action: "we should catch up sometime";
- promises by someone not in the meeting: "our counsel will send comments" (Arvind is not a participant);
- questions and requests alone. When someone asks "can you send X?" and the other answers "yes, tonight", the commitment is the answer, owed by the person who answered;
- sign-offs and plans for a group: "speak Thursday", "see you Monday", "the partners vote next week".

For each commitment write one JSON object:

```json
{"transcript_id": "<notes id>", "owed_by": "<full name>", "owed_to": "<full name>", "what": "<verb first, under 12 words>",
 "due": "<YYYY-MM-DD or null>", "quote": "<the transcript line, copied word for word>"}
```

`owed_to` is one person. When a promise goes to two people, name the one who asked for it, else the most senior person on that side.

The verb in `what` is the promised act, in the words a person would use: "Send the cap table", "Intro Arjun to Raj", "Answer the fee offset question". ant. drafts an email for a promise whose `what` starts with send, share, intro, introduce, forward, reply, answer, follow up, confirm, email, invite, connect, set up a call, schedule or book; any other verb ("Review the deck", "Model the scenarios") is work the user does, so it gets a line, not a draft.

Turn relative dates into calendar dates from the meeting's date. Weeks run Monday to Sunday.

| Said | Due |
| --- | --- |
| "today", "tonight", "after this call" | the meeting day |
| "tomorrow" | the next day |
| "by Friday" (any weekday) | the first Friday after the meeting day |
| "next Friday" (next plus a weekday) | that weekday in the following week |
| "this week" | the Friday of the meeting's week, or of the following week if the meeting is on a weekend |
| "next week" | the Friday of the following week |
| "by the 9th", "before the 21st" | that day of the month (the next month if it has passed) |
| "end of the month" | the last day of that month |
| "after the Monday partner meeting" | that event's date |

If no date was said, or the time words describe an event rather than the action ("I'll invite you to the dinner next month"), `due` is null.

Save the list as `extracted.json` (a JSON list of these objects) and check it:

```bash
python3 -I -S instinct-engine/instinct.py validate-commitments --bundle bundle.json --extracted extracted.json
```

Fix or drop anything rejected. Never change a quote to make it pass; the quote must be a real line.

## 4. Summarise

Three lines: what happened, what was decided, what happens next. Plain words, numbers kept exact. Portfolio news heard in the meeting (someone key leaving, runway, a new raise) leads the summary, so portfolio watch can pick it up.

## 5. Propose CRM updates

Only for an open deal (a stage that `ontology/stages.json` marks active; never portfolio or passed), only when the meeting is newer than the CRM's last update for that deal, and only these fields: `stage`, `next_step`, `next_step_due`, `note`, `last_contact`. Propose `note` only for a decision or a number worth keeping. Show each as field, current value, proposed value. Save one proposal per deal to `snap/proposals` with status `proposed`, in the shape `shared/home.md` gives. Never write to the CRM here; the user approves in Home or chat and the next pulse applies it.

## 6. Draft the follow-up

A short email from the user to the external attendees: thanks in one line, then "What we each agreed" listing both sides' commitments with dates, then the next step. Under 120 words. Leave out promises between colleagues (the engine marks them `internal`) and anything about other deals, funds or the firm's internal views: the founder reads this email. If a Gmail tool that creates drafts exists, mark the draft on the run row first (`shared/home.md`, Write step 2, `drafting`, in a scheduled run), then save it there; otherwise it goes to `snap/drafts` with `in_gmail` false. In chat, show it in the message compose card when available.

## 7. Write and report

Run the engine `build` with `--extracted extracted.json` and write the snapshots. In a scheduled run, add the pack to `packs.json` (`skills/pulse/SKILL.md` step 4) so the push says the follow-up is ready, once. In chat, show the summary, the commitments as a checklist with owners and dates, the CRM proposals with Apply, Edit and Skip, and the draft.
