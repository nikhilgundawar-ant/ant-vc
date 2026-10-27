# How ant. matches people across tools

The same person shows up as an email sender, a calendar guest, a meeting-notes attendee and a CRM record. ant. merges these into one person only when it is sure. The engine applies these rules in order (`engine/instinct/resolve.py`).

| Rule | Example | Confidence | Result |
| --- | --- | --- | --- |
| Same email address (Gmail dots and `+tags` ignored) | `sid.menon@gmail.com` and `sidmenon@gmail.com` | 1.00 | Merge |
| Same CRM record id | Two observations both tagged `crm_id: P-102` | 1.00 | Merge |
| Same full name, same work domain | "Maya Chen" at `lumenledger.com` twice | 0.95 | Merge |
| Nickname or short form of the first name, same last name, same work domain | "Sid Menon" and "Siddharth Menon" at `kitepay.in` | 0.85 | Merge |
| Same name (or nickname), one personal and one work address, seen in the same meeting or thread | `siddharth.m@gmail.com` and `sid@kitepay.in` on one invite | 0.82 | Merge |
| Initial plus last name, same work domain | "S. Menon" and "Siddharth Menon" at `kitepay.in` | 0.75 | Needs review |
| Same name, one personal and one work address, never seen together | "Arjun Rao" at `gmail.com` and at `orbit.in` | 0.60 | Needs review |
| Same name, two different work domains | "Rahul Sharma" at `fable.in` and at `tallyfin.com` | 0.40 | Keep separate |

Rules that always hold:

- Below 0.80 ant. never merges. It writes a `needs_review` row and asks once, in the next brief, with both records side by side.
- A CRM record id anchors the person. A merge never changes a CRM id.
- Two different work addresses at the same company with incompatible first names are never merged, even through a chain of other matches.
- Firm colleagues (the user's own domain) are matched by email only.
