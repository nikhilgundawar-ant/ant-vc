# Delivery: how ant. reaches the user

ant. prepares, drafts and proposes. The user taps to act. Nothing goes to another person without the user's own tap in their own app.

## Surfaces, in order

1. **ant. Home.** Always. Write the snapshots (see `shared/home.md`).
2. **Push alert.** In a scheduled run, the run's final line is the alert. Use the engine's `report.push_line` exactly: it is under 90 characters and names the one fact that matters. When `report.push.send` is false, the final line is exactly `Nothing new`, which stays silent.
3. **Chat cards.** When the user is present in chat, show drafts with the message compose card if one is available, CRM changes as a short diff with Apply, Edit and Skip, and meetings as a five-line prep card with a Prep me button.
4. **Drafts.** Every morning, each email the user owes is already written before the brief. When the user's Gmail connector can create drafts (a tool that makes a new draft, such as `create_draft`; a tool that only edits a draft already there does not count), it waits in Gmail drafts. When it cannot, it waits in Home, where "Open in Gmail" opens a new message already filled in. Either way the user reads it and sends it. ant. never sends mail.
5. **Copy brief.** Home's Copy brief button copies `brief-shareable.md`: plain text, no links from email, quiet deals left out. The user pastes it wherever they like. ant. posts nothing to Slack or any other channel.

## When a push goes out

The engine decides, so a busy day stays quiet:

- At most four pushes a day, and none inside a meeting or in the 15 minutes before one. The morning line, heads-ups, the board-eve line and a reconnect always go. A review, the week ahead, a follow-up pack or a new breach goes only while the day has room, counting the heads-ups still due that day; otherwise it waits in Home.
- Every meeting with a prep card gets one heads-up, from the last free run at least 45 minutes before it. When that run falls inside another meeting, or the day has more heads-ups than room, the heads-up folds into an earlier free run, and one line names each meeting it covers. A first meeting with someone new gets one too. A heads-up adds news: when the morning line already named that company, it brings the card's next fact. Nothing displaces it: when the morning brief, the week ahead or the Thursday review shares that run, the heads-up goes first and their line follows at the next free run.
- From 17:00, a portfolio board meeting tomorrow with a promise still open pushes once: "Orbit Treasury board tomorrow 10:00. You promised to review the board deck by 22 Oct".
- The morning line leads with the user's own work: a deadline today, then a late promise no push named in the last 72 hours. Two of their own promises due today share one line. Then anything due today, then the most urgent item no push named lately; when everything was named lately, the top item goes out as "Still open", with how late it is now. Whatever the line names is put on Today.
- A line that can wait never lands in a meeting or the 15 minutes before one; it goes at the next free run the same day, or stays in Home. One exception: a Thursday review held all Thursday goes on the next working day, at the first free run after the morning line.
- The Sunday week ahead sums up the week: meetings, decisions with their dates, promises already late. The Thursday review names its top deal, or the next one when that deal was pushed this week.
- Any other run pushes only something no earlier run has seen: a new breach, a post-meeting pack, or a connector the user must reconnect.
- A push always keeps the person or company and the date; it is the action that gets shortened. No line is cut mid-word, and none ends in "...": a long line ends at its last whole clause.
- A draft with lines to fill says so ("3 lines to fill"), never only "Draft ready".
- Notes that went out together are followed together: one note about three founder asks gets one nudge, one row on Today and one push. The nudge comes on the morning of the fifth working day after the note (days are counted by date, so a Thursday note is nudged the next Thursday), never when a reply from that person arrived first. A repeat push keeps its words ("Still open: Nudge Aditi on Orbit and Kestrel"). When a draft the push names is written after the build, the push says it is ready.
- A capital call you chased is remembered for the life of the call: never a first note again, never a third.
- Nothing is pushed twice in a week. A run the user asked for in chat pushes nothing.

## Words

- Plain sentences. Sentence case. No exclamation marks. No em dashes.
- Lead with the figure or the fact: "Atlas needs your markup by Friday", not "There is an update on Atlas".
- Every line carries its source: a link label in Home, a link in chat.
- Breach is only for a figure past its threshold, with the figure and a date: "Runway under 9 months: 8.0 months at $200K a month".
- Work items say Urgent, High, Medium or Low, or what they are: Overdue, Due today, Waiting on them, Stale, Competing.
