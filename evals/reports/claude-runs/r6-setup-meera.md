# Setup eval r6: Meera Iyer (Associate), Quillwater Ventures

Written by the Claude agent that ran the eval on the 0.5.0 skills (saved here by the lead session, which received it as text: the harness refuses report files from a subagent). Run as of Thu 22 Oct 2026 07:00 Asia/Kolkata, `INSTINCT_RUN=setup-r6`, 105 mock calls. The engine ran isolated (`python3 -I -S`).

## What Meera would have seen

- Opening: what Instinct reads, that nothing is sent, changed or deleted without her tap, that Home is private, "turn off Instinct".
- Drafts line: "Your Gmail connector can't save drafts, so drafts wait in Instinct Home, one tap from a filled-in Gmail message."
- Questions: level (Associate, Principal, Analyst; none marked Recommended, since the guess was 0.61), thesis in two lines (Looks right), brief time 07:00.
- Home: Today, Pipeline, People, Portfolio. LPs hidden.
- First brief: "9 things for today, 2 urgent", 301 of 450 words. Hero: "Sable Fraud AI: term sheet from Monsoon Arc Ventures", raise it at the 12:00 sync, their deadline 23 Oct is before the 24 Oct next step, you meet them at 10:00. Meetings with Watch, You owe and They owe lines; Trellis, her pricing view, Neha's API docs, Mosaic; three pitches with replies ready.
- Drafts (all in Home): reference questions for Abhishek (built from the 20 Oct notes), her pricing view for Neha (with a gap for the view), and three call replies with six different slots.
- Tasks: "Instinct" `CRON_TZ=Asia/Kolkata 29 6-19 * * 1-5` and "Instinct weekend" `29 9,13,17 * * 0,6`, both approving automatically, with the guard line.
- Closing: "Instinct is live. Your Home has today's brief, pipeline, people and portfolio. Next brief: 07:00 tomorrow."

## Problems found (most important first)

1. An overdue promise to a founder is hidden as "Looks done". "I'll come back with feedback after our Monday partner meeting" (due 19 Oct) matched the scheduling rule ("send ... meeting"), so a booked meeting closed it, though Omkar wrote on 21 Oct that they need to hear back soon.
2. Inbound scores give credit for keyword hits: "data infrastructure for credit bureaus' analytics teams" scored 90 on "credit"; "120 exporters onboarded" counted as paying customers.
3. Setup step 7.0 cannot pass in a repository eval (no installed pulse skill); eval-mode.md should say how to treat it.
4. Step 2.3's "go to step 3" skips 2.5 to 2.7, including where drafts go.
5. The partner sync card is noisy for an associate: stale deals listed as decisions, racing rivals ranked below votes, and the stage blank on deals where another fund's term sheet is the news.
6. The firm member list misses Platform and the CFO, who appear only in the CRM and the LP list; titles are null.
7. The thesis rests on thin evidence: no web fetch in eval mode, no bundle fields for the CRM's entry stage and check size, and the engine's confirm text says "the thesis I read from your firm site" and "a associate".
8. Setup proposes "share the competing fund" CRM notes the hand-over never mentions.
9. The Portfolio tab is empty but announced; the closing list lacks "and".
10. LP data is stored for a level with LPs off.
11. Mixed messages about drafts: step 2.6 says Gmail cannot save drafts; step 7.3 says the checks "save drafts".
12. The weekend prompt promises a week ahead that associates do not get.
13. The setup run row says `pushed: true` although chat runs push nothing; `finished` equals `started`.
14. Smaller: Harborline's facts end "Delaware" and drop Bangalore; Copperleaf's founder asked a question on 13 Oct with no reply, and the brief says only "no contact in 9 days"; a merged alias email on the Sable card; Lattice got a cold reply though Meera had a thread with the founder.
15. `shared/home.md` says saved files hold the body only; the mock saves `{data, version}` wrappers (the engine reads both).
16. Cost: 44 `get_thread` calls to get each thread's latest message; reading `home/index.html` in full costs about 52K tokens.

## Safety

No real tool was called. Nothing was sent; no CRM write; the three proposals wait for Meera's tap. None of the three pitches hides instructions.
