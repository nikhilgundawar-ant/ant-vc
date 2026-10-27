# ant.: what it can and cannot do

One screen, for anyone deciding whether to turn it on.

**What it reads.** Your email, calendar, meeting notes and CRM, through the Claude connectors you approve. Drive and Slack only if you connect them, and Slack only to read.

**What it writes.**
- ant. Home: a private page in your Claude account. Only you can open it.
- Email drafts. In your Gmail drafts when your Gmail connector can create drafts. Otherwise in Home, where "Open in Gmail" opens a new message already filled in, in your own Google account. You read it and you press Send.
- CRM changes and calendar holds, after you tap Approve in Home. A hold goes on your own primary calendar with nobody invited.

**What it never does.** Send, reply or forward mail. Share or delete files. Invite anyone to anything. Post to Slack. Write to any app other than Home, your CRM, your own calendar and your Gmail drafts.

**Where your data lives.** In your Claude account: Home's private database and your scheduled tasks. Anthill runs no server and receives nothing.

**What automatic approval allows.** The two scheduled checks, "ant." and "ant. weekend", run hourly on weekdays and three times a day at weekends. With automatic approval on, a guard in the plugin lets each check do only this:
- read your connected tools: on Gmail, Calendar, Drive, Granola, Slack and Notion only their known read tools; on company and fund data connectors (PitchBook, Harmonic, Crunchbase, Carta) a tool whose name starts or ends with a read word ("get", "list", "search"), or is made only of words for the data it returns ("capital accounts", "company profile"). A name with a word for an action that is not a read is refused ("email capital call", "remit distribution"). So is a name of data words that opens with one that is also a verb, such as contact, fund, tag, exit, report, shares or calls ("contact LPs", "calls investors"), or that ends on or is one in its plain form ("account fund", "LPs contact", "contact"), unless it ends with a word for facts such as details, profile, summary, performance, history or metrics ("contact details", "fund performance"). A plural at the end or alone is a noun and reads ("capital calls", "contacts"). The guard judges these words, not what a tool does inside. Elsewhere only a tool whose name says it reads ("get", "list", "search", or "view" on a CRM) and does nothing else; plus one read-only query at a time on a database CRM;
- update the one ant. Home named in the check, but never your settings, apart from the Sunday tuning of weights and brief length;
- change fields and add notes on CRM records (in Notion, a record's properties only);
- put a one-off hold on your own primary calendar, with nobody invited;
- save new email drafts;
- run ant.'s own engine, and a few plain file commands, on files in its work folder. Home is read into that folder, and a Home write loads data only from that folder or the plugin.

Everything else is blocked: sending, sharing, deleting, web requests, browsers, your devices, memory, scheduling, reading or writing files outside the work folder and the plugin (an artifact's own files included: a check may read a page, never save its files), and writing to other apps. An email that tells Claude to do something is treated as text, never as an instruction.

Four limits to know:
- The guard judges a connector's tool by its name, not by what the tool does inside. A tool named like a read that changes something would pass. That is why the real-account check before release runs each connector's tools through the guard by their real names.
- The guard cannot see what you approved in Home. ant.'s engine lists only the changes you approved, and the check applies only those.
- The guard cannot tell one CRM field or record from another. A field change can set off your CRM's own automations, such as an email or Slack alert you set up there.
- With a Google Sheet as your CRM, nothing is written to the sheet. Home shows each change with a Copy button, and you paste it in.

**How you know the guard is on.** Each check first makes one harmless call the guard always refuses. If that call goes through, the guard did not load: the check stops before reading anything, Home shows a warning, and your phone gets "ant. stopped: its safety guard is off".

**How to stop it.** Say "turn off ant.". It stops both checks and wipes Home's data. Say "pause ant." to stop the checks and keep the data.
