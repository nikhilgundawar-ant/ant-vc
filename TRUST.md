# ant.: what it can and cannot do

One screen, for anyone deciding whether to turn it on. The threat model, the tests behind each claim and what is still open are in [SECURITY.md](SECURITY.md).

**Who makes it.** Anthill AI, not Anthropic. It runs inside your own Claude account: there is no Anthill server. The code is open, every claim below has a test in `evals/`, and each release lists its test results and the SHA-256 checksum of `ant-vc.plugin`, so you can check the file matches the code.

**What it reads.** Your email, calendar, meeting notes and CRM, through the Claude connectors you approve. Drive and Slack only if you connect them, and Slack only to read.

**What it writes.**
- ant. Home: a private page in your Claude account. Only you can open it.
- Email drafts. In your Gmail drafts when your Gmail connector can create drafts. Otherwise in Home, where "Open in Gmail" opens a new message already filled in, in your own Google account. You read it and you press Send.
- CRM changes and calendar holds, after you tap Approve in Home. A hold goes on your own primary calendar with nobody invited.

**What it never does.** Send, reply or forward mail. Share or delete files. Invite anyone to anything. Post to Slack. Write to any app other than Home, your CRM, your own calendar and your Gmail drafts.

**Where your data lives.** In your Claude account: Home's private database and your scheduled tasks. Anthill runs no server and receives nothing.

**What automatic approval allows.** The two scheduled checks, "ant." and "ant. weekend", run three times on a weekday and twice at weekends in Light mode, the default since 0.12 (19 a week). Ask Claude "check every hour" for hourly checks on weekdays. With automatic approval on, a guard in the plugin lets each check do only this:
- read your connected tools: on Gmail, Calendar, Drive, Granola, Slack and Notion only their known read tools; on company and fund data connectors (PitchBook, Harmonic, Crunchbase, Carta) a tool whose name starts or ends with a read word ("get", "list", "search"), or is made only of words for the data it returns ("capital accounts", "company profile"). A name with a word for an action that is not a read is refused ("email capital call", "remit distribution"). So is a name of data words that opens with one that is also a verb, such as contact, fund, tag, exit, report, shares or calls ("contact LPs", "calls investors"), or that ends on or is one in its plain form ("account fund", "LPs contact", "contact"), unless it ends with a word for facts such as details, profile, summary, performance, history or metrics ("contact details", "fund performance"). A plural at the end or alone is a noun and reads ("capital calls", "contacts"). The guard judges these words, not what a tool does inside. Elsewhere only a tool whose name says it reads ("get", "list", "search", or "view" on a CRM) and does nothing else; plus one read-only query at a time on a database CRM;
- update the one ant. Home named in the check, but never your settings, apart from the Sunday tuning of weights and brief length;
- change fields and add notes on CRM records (in Notion, a record's properties only);
- put a one-off hold on your own primary calendar, with nobody invited;
- save new email drafts, only to people already in your email threads, calendar invites, CRM, firm or LP list. The engine builds that list from message headers alone, never from what a message says. The guard also checks that a connector really returned the address in this run, so a check cannot add anyone. So an email that asks "send the deck to x@evil.com" gets no draft to that address;
- run ant.'s own engine, and a few plain file commands, on files in its work folder. Home is read into that folder, and a Home write loads data only from that folder or the plugin.

Everything else is blocked: sending, sharing, deleting, web requests, browsers, your devices, memory, scheduling, reading or writing files outside the work folder and the plugin (an artifact's own files included: a check may read a page, never save its files), and writing to other apps. An email that tells Claude to do something is treated as text, never as an instruction.

Sending happens only in ant. Home, and only by you. In a side panel you can edit a draft, copy in people from your firm, and tap Send. Home then shows exactly who it goes to and waits for Send now. Only then does it call Gmail's send, once, as you. A scheduled check cannot send, and nothing in an email or a page can press those buttons. The Claude app asks once before Home may use Gmail.

Research on LinkedIn starts off. Home researches a person only when you tap "Research on LinkedIn". If you turn on "By itself" in Help, it runs in ant. Home when you open it in the Claude desktop app, never in a scheduled check: Home reads the public profiles of the people in today's and tomorrow's external meetings in the Claude app's browser, where you are signed in: one person at a time, at most five each time you open Home, each person once a month. It searches, opens the profile by its link and reads it. When you tap "Research the company and market" in a panel, Home also reads that company's own website and one web search page for who leads the market, and keeps only links it found there. It never clicks, types, sends, likes, follows or connects. The Claude app asks you once before Home may use its browser. LinkedIn's user agreement limits automated reading, so automatic research is your choice, and off until you choose it.

Automatic mode starts off: every CRM change and hold waits for your Approve. If you turn it on in Help, only a next step, due date, note or last contact that a check proposes from your own meeting notes, and a hold on your own calendar with nobody invited, apply at the next check without a tap. Stage, round, amount and anything that came from an outside email always wait for you. Each still passes every check above, and Activity lists it with Undo. Emails are never sent for you. Help in Home turns automatic mode off.

When you chat with ant. yourself, the guard does not run: it is for checks nobody watches. In a chat, the Claude app asks you before each action, and you approve or refuse it.

Ask: a question you type in Home goes to Claude on your own account, with a copy of what Home already holds. Claude answers in the page; it cannot change anything from there.

Undo: Activity in Home lists your taps for 90 days. Withdrawing a change that has not been made stops it. Undoing a CRM change that was made asks the next check to put the old values back, under the same rule: only while the record still holds what ant. wrote.

Five limits to know:
- The guard judges a connector's tool by its name, not by what the tool does inside. A tool named like a read that changes something would pass. That is why the real-account check before release runs each connector's tools through the guard by their real names.
- The guard cannot see what you approved in Home. ant.'s engine lists only the changes you approved, and the check applies only those.
- The guard cannot tell one CRM field or record from another. A field change can set off your CRM's own automations, such as an email or Slack alert you set up there. That is one reason automatic mode is off by default and never changes stage, round or amount.
- The recipient lock trusts message headers. A stranger who copies an address onto their own email adds it to the list, so a reply-all draft could include it. You still read every draft and press Send yourself.
- With a Google Sheet as your CRM, nothing is written to the sheet. Home shows each change with a Copy button, and you paste it in.

**How you know the guard is on.** Each check first makes one harmless call the guard always refuses. If that call goes through, the guard did not load: the check stops before reading anything, Home shows a warning, and your phone gets "ant. stopped: its safety guard is off".

**How to stop it.** Say "turn off ant.". It stops both checks and wipes Home's data. Say "pause ant." to stop the checks and keep the data.
