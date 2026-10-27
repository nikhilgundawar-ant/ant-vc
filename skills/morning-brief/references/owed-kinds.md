# Owed entries: the kinds ant. finishes, and the rewrites

Read once before drafting, from the morning brief's step 6. Step 6's items 1, 2 and 6 to 8 still apply to every entry here: sources only, slots, one email per person, Gmail, `owed-drafts.json`.

## Work ant. finishes itself

### `kind: "letter"`

The quarterly LP letter, written as `<plugin root>/skills/lp-watch/SKILL.md` step 4 says, from the entry's `inputs` (the fund's figures, each portfolio company's latest month against plan, the flags, each with its source). Every number comes from those inputs or a source you name beside it; the partner's commentary and anything they do not hold is a bracketed gap. It goes as a draft to the person it was promised to (`to_name`), subject "<the entry's `quarter`> LP letter: draft for your review" ("Q3 2026 LP letter: draft for your review").

Run `python3 -I -S instinct-engine/instinct.py letter-check --letter <the letter as markdown>`: it lists any missing section and any line that names paid-in capital (or contributed capital); take those out, since the letter gives committed and called only.

### `kind: "lp_call"`

An LP you own still owes money on a capital call two weeks on: a short, polite note to its contact with the amount and the call date from the entry, and an offer to resend the wire details. Never mention other LPs, penalties or default terms. With `again`, a second, shorter note that refers to the first (sent on `chased_on`). Keep its `action_ids`. There is never a third note.

- Without `replied_on`, the first note had no reply in five working days: first search the user's mail for an answer from the LP's contact since the chase went (your message in its thread, else `chased_on`), in the chase's thread or about the money (the wire, the payment, the amount). When there is one, write nothing: put `{"replied": {"on", "by", "url"}}` under the entry's `id` in `owed-drafts.json`, with no body, and add a warning to the run. An email about something else (the AGM, even one that names the fund) is not an answer. A day they name for what already happened ("we paid it last Friday") is not a day they promise.
- With `replied_on`, they answered, and the money has not come: by the day they named (`promised`), or in five working days. Refer to their reply in one line ("You mentioned the wire would go on 28 Oct; it has not reached us yet") and offer to resend the details. Never sound like a demand. With `says_paid`, they said it was already paid and eight working days have passed with no money: never ask when to expect it. Say the payment has not reached the fund's account yet, ask for the transfer reference or date so both sides can trace it, and offer the wire details to check against.

### `kind: "ask"`

A founder's ask, finished, as `note_kind` says:

- `board`: the ask carries a cash `warning`, so the note goes to the board partner in `to` first: name the flag, ask whether the firm should help now, and say who could help if they agree (the `path`, or the team).
- `contact`: to the contact you know (`path.colleague` is "You"), asking whether they would take an introduction.
- `colleague`: to the colleague who knows the contact, asking them to make it.
- `team`: to the firm members in `to` (a comma list), naming the founder, the company and the ask, and asking who knows someone who fits. A team note goes to the whole firm, so it leaves any cash flag or runway figure out. A solo GP gets no team note: with no path there is no entry.

An entry with `items` carries several asks for the same person: one note, a short paragraph per ask, the cash warnings first; keep its `action_ids` and `note_kinds` so every ask's row shows "Draft ready". Never write to the founder or the contact in a colleague's name. Keep the entry's `action_id` and `note_kind` on the draft: they are how the ask's row shows "Draft ready", then who was asked once it is sent.

### `kind: "ask_nudge"`

A note the user sent about one or more founder asks (`items`) had no reply in five working days.

1. First search the user's mail for a reply from `to` since `sent_on`: in the note's thread, or an email that answers one of the asks in `items` (it names that company and speaks to the ask). An email that only names the company about something else (a board pack) is not a reply. A reply that answers some asks answers only those: write the nudge for the rest, and thank them for the answered one in its first line. With `answered`, ant. already found that reply (`companies`, on `on`): open with one line of thanks for those ("Thanks on Orbit Treasury and Kestrel Pay"), then ask only about the asks in `items`. Count from when the note really went (your message in its thread), not from when it was marked sent: a reply can land in between. When every ask in `items` is answered, write no nudge: put `{"replied": {"on": "<the reply's time>", "by": "<their first name>", "url": "<the thread>"}}` under the entry's `id` in `owed-drafts.json` instead, with no body, so the rows and the push say they replied, and add a warning to the run ("Aditi replied on 27 Oct: no nudge written"). A reply that only says the answer will follow ("let me think about these and come back to you") is not an answer: write no nudge yet, and put the same `replied` record with `"defers": true` and the reply's words in `"text"`. ant. then writes one nudge five working days after that reply, saying they promised to come back.
2. Otherwise write one short nudge to `to` (`to_name`) in the same thread: subject "Re: " and the entry's `re` when it has one. Say when you wrote (`sent_on`), give each ask its own line, and ask nothing new ("A quick yes or no on each is plenty").
3. Keep its `id`, `action_ids` and `note_kind` "nudge": every ask the note carried then shows the nudge, and the nudge is written once. When the draft stays in Home, `context` says to send it as a reply to that note.

### `kind: "holder"`

Two or more things the user owes wait on one partner's view (`to_name`, who sponsors those deals): drafts in Home (`items`: the company, what was promised and to whom, when it is due, `overdue`) and any decision due within two working days on those deals (`decisions`: the company, what is happening, `deadline`). One short internal note to that partner:

- One line per item, the late ones first: the company, what the user owes and to whom, and the date ("Rivulet Payments: our feedback to Omkar, 4 days late"). Then each decision with its day ("Sable Systems: another fund is moving, decide by Fri 23 Oct").
- Ask for their view on each in a line or two ("A line on each is plenty"), and offer ten minutes today instead.
- Subject "Your view on <n> founder emails" (or "... and <company>'s decision" when there is one).
- Give no view of the user's own, quote no draft, and add no fact the entry does not hold. The note goes to a colleague only: never copy the founders, and never name a deal the user marked quiet (safety rule 6; the entry already leaves them out).
- Keep its `id` and `kind`. Like every draft, it waits in Home and Gmail drafts until the user sends it; the drafts it names stay as they are.
- With `rebuild`, the note is already waiting in Home and what it asks about changed (a draft it named was sent, or a new one waits): rewrite it under the same `id` for the `items` and `decisions` the entry gives now, with a subject that names only those. There is one note per partner at a time; once it is sent, none follows in the three working days after it went, and nothing it named is asked again, answered or not. A later note (a new `id`) names only drafts the sent one did not.

### `kind: "narrow"`

A nudge still waiting names asks that moved on since (`dropped`: another way in was tapped or sent, they answered, the intro was made or the ask was closed). Rewrite it under its `id` for the `items` left only, the same way as a nudge, and keep the `action_ids` the entry gives.

With `promises`, it is an email that keeps several promises to one person, one of them closed since by Done on its row (`dropped`: settled another way, say in person). Rewrite it under its `id` for the `promises` left only: take out every line of the dropped one, keep the rest word for word, and change the subject when it names only the dropped promise. Keep the `commitment_id` and `commitment_ids` the entry gives, never the dropped ones. With `received`, the reader already sent what the email asks them for (the user tapped Got it): take out the line that asks for it, and change nothing else.

## A draft already waiting: `reslot`, `refresh`, `redate`

Rewrite it under its own `id`, keeping its ids (`commitment_id`, `commitment_ids`, `inbound_id`, `question_id`, `action_id`, `action_ids`, `note_kind`, `note_kinds`) and its subject, unless the subject reads as a task. Any rewrite may also carry:

- `words`: days in the body that have come or gone; replace them as `redate` says, whatever the entry's kind.
- `they_owe`: what the reader owes the user, late or due; ask for it in one line ("Could you also share the fraud loss benchmarks when you have them?"). Never in an email that copies someone else.
- `also_promises`: a promise with no date to the same person ("Invite Rahul to the founders dinner"); add one line that keeps it, and keep `commitment_ids`. Open `context` by naming both ("One email for two promises: the CFO intro and the dinner invite"), since each promise's row shows it.

- Keep a line only when a source holds it (the draft's `source_url`, the meeting notes, the user's own words) or the old `context` (`old_context`) says ant. suggested it; drop or mark anything else.
- Keep what `old_context` asked the user to do (fill in the lines, attach something, check with someone), then add this rewrite's check after it. When the entry names a `holder`, say to check the firm's view with them.
- Replace "today", "tomorrow" and "this week" with dates, in the lines you keep and in `context`, since the draft is read on a later day. When the day it named has come or gone (an old "this week" read on a Friday), offer a date two working days out, never the day the draft is read, keep its lead word ("by Mon 2 Nov"), and say once in `context` that the date is ant.'s suggestion; or drop the time ("as soon as you tell me"). Never put a date no source holds without saying so.
- A time today or earlier is never left in a draft.

By kind:

- `redate`: the draft names a day (`words`) that no longer reads right since it was written on `made_on`: a relative day ("this week", written last week), a date it promised that has passed ("by Tue 27 Oct" or "I will introduce you Thu 29 Oct", read on Fri 30), or today's date for something the reader must answer first ("Tell me who ..., and I will introduce you Thu 29 Oct", read that morning). Put dates in their place as above, and change nothing else. A promised date that has passed never stays in the body, whoever set it: it gets a new one two working days out, with its lead word, marked once in `context` as ant.'s suggestion. When the user or a source set it (`set_by: "you"`; ant. stores who set each draft's dates), add one line that owns the delay ("I am sorry this is late"). Only a date that was still ahead when the draft was written counts: a past fact ("the data room was closed until 20 Oct") is never listed.
- `reslot`: the times it offered are today or earlier, too short notice. Keep the email and offer two new times (not in `avoid_slots`).
- `refresh`: you met on `met_on` (`met_title`) after it was written.
  - With notes (`notes_url`), read them and rewrite the draft to match what was said; drop any line the meeting made untrue ("when we meet today").
  - Without notes, keep the draft, open with one line that names the meeting by its date and claims nothing about what was said ("Good to see you on 22 Oct."), and in `context` ask the user to check it still stands, or to tap Done if it was settled in the room.
  - Say "good to see you" only to the people in `met_with`: on an introduction to two people, greet the other one as before.
  - With `named_only`, the meeting was with people the draft names (`met_with`), not with its reader: keep the greeting, check the lines about them against the notes when there are any, and without notes keep the draft and say in `context` to check it still stands.
  - When the entry carries `old_slots`, offer two new times too.
