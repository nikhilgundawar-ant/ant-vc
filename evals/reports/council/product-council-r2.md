# Instinct for VCs: product council, round two

Written by the Claude agent that played the council (saved here by the lead session, which received it as text). **Simulated council:** one model played a product manager, a UI/UX designer, an AI engineer and a QA lead. No real person reviewed the build. Reviewed 23 Oct 2026, 00:20 to 00:45 IST, against the uncommitted build after fix round two.

## Scores

| Reviewer | Round one | Round two | In one line |
|---|---|---|---|
| PM | 5 | 6 | Most round-two asks shipped, but emails waiting in Gmail drafts cannot work on this account's Gmail connector, and heads-ups still drop meetings on busy days. |
| Designer | 7 | 7 | Evergreen applied with care in both themes and the contrast scan is a real method, but crowded first screens, near-invisible selected states and some misleading links and words. |
| AI engineer | 4 | 5 | Round-one data-loss bugs fixed and pinned by tests, but the new push picker breaks its own rules, the guard has large holes, and two platform contracts are still assumed. |
| QA lead | 4 | 5 | Coverage is real, but two tests assert the bug, a scorer can vanish without failing, and the mocks offer a Gmail tool the real connector lacks. |

**Average: 5.75** (round one: 5.0).

## Verified fixed since round one

Pulse no longer wipes views (replays 214/214 and 212/212, outage replays pass); promises kept and trimmed newest-first; tuning counts each rating once; approvals apply only what Home showed and are marked applying; heroes state a fact for every level; tabs follow the level; founder asks show; every row carries a status word; meetings at :30 get a heads-up; setup has two scheduled tasks and three questions.

## Bugs and risks reproduced

1. **Push picker:** the cap of four counted prep and board-eve pushes, so a busy day lost heads-ups (15:00 Gravity, a 17:30 call) and the board-eve line; one prep per run, so two meetings in one band lost one heads-up (Kabir's 12:00 pack); decision and stale ids carried today's date, so the same decision repeated two mornings; a deadline day lost to the three-day rule; board-eve never checked in week-ahead or review runs (a Monday board gets no Sunday push); passed deadlines still read "decide by"; the band was measured from the bundle's time, not the run's start; deferral kept one line and looked back three runs.
2. **Drafts:** this account's Gmail connector has no create-draft tool (only update, send, reply, list, get, delete), and the guard denies `update_draft`, so drafts can never be in Gmail here while the README promises it; drafting is not idempotent if a run stops before the batch write; pitch replies were drafted after the founder meeting; the drafts command did not re-render the brief text.
3. **Guard:** a denylist of verbs. In a scheduled session it allowed WebFetch, Bash with curl, Slack canvas create and update, Drive create and update, Notion create pages, Confluence create page, Chrome navigate and device bash.
4. **Platform contracts:** runs are read with `list` plus `order_by`, which the schema allows only on `query`; whether saved files carry their version is untested.
5. **Home:** a false "No check since" banner at weekends and before a late brief; two different "last check" times on one screen; the Platform hero's Open goes to another company's update; crowded heroes (four-part kicker, six controls); long hero statements; "This week" for a deadline tomorrow; "Open" as a status word; "0 days"; selected states nearly invisible (tab pill 1.13:1, pressed chip 1.06:1); the Appearance control stretched; "draft ready" under a meeting is not tappable; 32px header targets.
6. **QA:** two tests encoded the bug (four pushes for six meetings; rotation compared daily-changing ids); `score_llm_brief` vanished silently when its files were missing; `qa.json` held a partial run; the solo screenshot predated the quota; the replay never acts (no taps, no Sent mail).

## Top five fixes, ranked

1. Guard allowlist for scheduled runs, and honest trust copy.
2. Push picker rebuilt as a priority queue, with tests that compare line text.
3. Gmail drafts made real or honest, and idempotent.
4. Platform contracts pinned by a real smoke test; runs read with `query`.
5. Trust fixes on Home: stall banner tied to the schedule, one "last check" time, the Platform hero link, the hero grammar.

## Go or no-go

No-go for that build. Go for five friendly VCs once all six are true:

1. The guard is an allowlist, and a probe allows zero outbound tools inside a real scheduled session.
2. On a seven-meeting test day, every external meeting gets one heads-up and the board-eve line goes out.
3. A create-draft tool is confirmed on each tester's Gmail; if not, the README, setup and Home all say so.
4. Three days of dogfood on the owner's own accounts: hourly updates, "Nothing new" stays silent, pushes per day logged, minutes and tokens per run measured, the brief lands by its stated time.
5. The stall banner and the Platform link are fixed, and screenshots and packs are regenerated from a committed build.
6. Each tester gets a one-screen trust note: what it reads, where data lives, what automatic approval allows, and "turn off Instinct", tested once.
