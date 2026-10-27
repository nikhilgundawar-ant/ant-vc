<!-- Claude-run eval, round eight (0.7.0). Written by a Claude agent running the pulse skill against the mock connectors; saved by the main session. -->

# morning-brief-tara: Tara's scheduled run, Thu 22 Oct 2026, 06:28 IST

Tara's run worked end to end. All three open founder asks got a draft that Home will show as "Draft ready", every owed entry got a draft with its ids kept, and the run ends with "Intro two CFO candidates: Rahul (Tallyfin), 1 day late". One real engine bug changed the outcome. Nimbus Collect lost its warm path (Aditi knows Raj Malhotra at Fable Bank), so its note went to the whole team instead of to Aditi.

Files:
- Work folder: /home/claude/instinct-vc/evals/runs/morning-brief-tara/work/ (bundle.json, run/, questions.json, owed-drafts.json)
- Mock Home: /home/claude/instinct-vc/evals/runs/morning-brief-tara/db/
- Call log: mock_log.jsonl. It shows no send, reply or forward attempt.

I could not write report.md: the harness blocked it. So the whole report is here.

## 1. What I ran, in order

1. **Guard canary (step 0): skipped.** Eval mode loads no guard.
2. **`status`:** all connectors are up. Gmail has no create_draft tool. It has update_draft, which does not count.
3. **Read Home:**
   - `db list` for snap, state and runs, into ./home-db.
   - I pasted the snap and state lines into home-db/versions.txt.
   - I copied home-db/snap/config.json to config.json.
   - The engine's `check` returned ok. I ran the engine from the repo, as eval mode says.
4. **`due --now 2026-10-22T06:28:00+05:30`:**
   - run true, jobs morning_brief and pulse, mode daily.
   - Every window starts 2026-10-21T06:28.
   - Run id r20261022T0628.
5. **Run row:** `db set runs/r20261022T0628` with started and jobs. It came back as version 1.
6. **`actions`:** nothing pending, refused or to check by hand, so there was no applied.json.
7. **Reading, using the Morning brief windows:**
   - Gmail after 15 Oct: 4 threads, each read in full.
   - Calendar, 22 Sep to 5 Nov: 6 events. Today has Tallyfin at 11:00 and Founder community at 14:30. Nothing tomorrow.
   - Granola since 21 Oct: nothing new.
   - CRM: deals, companies, people, passes and notes.
   - There were no new pitches, no founder updates and no replies to tracked promises. So there were no extracted, inbound, kpis, asks or packs files.
8. **bundle.json:**
   - 4 threads, 6 events, and an empty transcripts list.
   - 37 open deals and 5 notes.
   - 84 companies: the open-deal ones, the portfolio ones, and the companies CRM people work at. I left out the 6 passed ones.
   - 100 people and 20 passes.
   - No LPs (LP watch is off) and no KPIs.
   - A small helper script built it from the saved mock reads. A real guarded run would have to type it out with the Write tool.
9. **`build`:** mode daily, run id r20261022T0628, started 06:28, jobs morning_brief and pulse. It gave 5 owed entries, 191 words and no warnings.
10. **Side builds, never written to Home:**
    - a literal bundle with 49 companies;
    - the `bundle` shortcut, with now reset to 06:28;
    - my bundle plus one extra thread (th0343).
11. **`questions`:** 3 for each of today's two cards. Both were written.
12. **Source reads for the drafts:**
    - Threads th0343, th0344, upd_orbit, upd_kestrel, upd_nimbus, upd_tallyfin, th0366, th0272, th0274 and others.
    - Gmail searches, and Drive searches. Drive holds only deal data rooms.
    - CRM records P-170, P-173, P-180, P-181, P-179, P-105, P-101, P-103 and the four companies.
13. **Drafts:** I wrote owed-drafts.json and ran `drafts --out run`: 5 written, 0 refused. All have in_gmail false. There are no drafting marks, because there is no create-draft tool.
14. **`db batch`:** pipeline v2, asks v2, prep v2, drafts v1 (new), brief v2.
15. **Run row finished:** `db update runs/r20261022T0628 --file run/home/run.json --if-version 1`. It is now version 2.
16. **Self-check:** I read Home back and matched each draft to its ask and owed entry.

## 2. Every entry in run/owed.json

**dr_k_e9eab86816**
- Kind: promise (commitment k_e9eab86816). No note_kind.
- To: rahul@tallyfin.com. Cc: george.thomas@gmail.com and swati.kulkarni@gmail.com.
- First two sentences: "As promised on our 15 Oct call, here are the two CFO candidates: George Thomas and Swati Kulkarni, both copied here. Sorry this is a day later than I said."
- Gap kept: "[Add one line on each candidate's background.]"
- Sources:
  - tr08 (the promise and the CFO search)
  - CRM P-180 and P-181 (both titled "CFO candidate", with Tara's ties)
  - P-105 (Rahul is CEO)
  - th0272 and th0274 (Tara's last emails with each candidate)
  - the 11:00 event

**dr_k_45c5b75374**
- Kind: promise (commitment k_45c5b75374). No note_kind.
- To: fatima@talentbridge.in.
- First two sentences: "As promised when we met on 16 Oct, here is the founder guest list for the November dinner: [add the guest list]. Please count in Rahul Sharma from Tallyfin too, as I promised him an invite."
- It also asks for her venue shortlist, which was due 20 Oct.
- Sources:
  - tr21 (both promises)
  - tr08 (the dinner invite promised to Rahul)
  - Drive and Gmail searches found no guest list, so the gap is real.

**dr_t_742d2f63d5**
- Kind: ask (Nimbus Collect). action_id t_742d2f63d5, note_kind team.
- To: aditi@, kabir@, meera@, rohan@ and vikram@quillwater.vc.
- First two sentences: "Divya Raman at Nimbus Collect has asked us for introductions to two banks as customers, first on 29 Sep and again on 13 Oct. Who knows someone at a bank who would take a call about their collections software?"
- It also names, from the CRM, Aditi's link to Raj Malhotra (Fable Bank) and Kabir's to Pinki Das (Pinnacle Small Finance Bank). It says Tara owes Divya a shortlist and sees her at 14:30.
- Sources:
  - th0343 and th0344
  - CRM c_nimbus, P-170 (Aditi, 49) and P-173 (Kabir, 28)
  - the 14:30 event
  - the members list in snap/config

**dr_t_41253d13e2**
- Kind: ask (Kestrel Pay). action_id t_41253d13e2, note_kind board.
- To: aditi@quillwater.vc.
- First two sentences: "Kestrel's September update asks us for intros to senior backend engineers for two roles this quarter. The same update puts monthly burn at $215K, up from $150K in August, a rise of 43.3% in a month."
- It then asks whether to help now, and says Tara will ask the team if Aditi agrees.
- Sources:
  - upd_kestrel
  - Home's KPI history for August (kpi_kestrel_2026-08)
  - the burn flag
  - P-103

**dr_t_4dd54f8e1f**
- Kind: ask (Orbit Treasury). action_id t_4dd54f8e1f, note_kind board.
- To: aditi@quillwater.vc.
- First two sentences: "Orbit's September update asks us for intros to senior backend engineers to hire two this quarter. The same update shows $1.60M in the bank and $200K monthly burn, which puts their runway under 9 months."
- It names "Vikram Rao" in full, because the firm's CFO is also called Vikram.
- Sources:
  - upd_orbit
  - the runway flag
  - P-101

## 3. The ask rows

All three open asks would show "Draft ready".

- **Why it works:** the "Founders need" card uses each ask's item_id as the row id. Home then finds the draft whose action_id equals that id, and no done mark sits on it.
- **Nimbus Collect (t_742d2f63d5):** "Draft ready". It is a team note to the five firm members, by address, as owed.json said.
  - But owed said "team" only because this run lost the warm path (see 6.1).
  - Yesterday Home showed "Aditi knows Raj Malhotra at Fable Bank".
  - The shortcut bundle gives note_kind "colleague", to Aditi.
- **Orbit Treasury (t_4dd54f8e1f):** "Draft ready". It is a board note to aditi@quillwater.vc. That matches the cash warning ("Runway under 9 months"), which names Aditi Rao as the person to tell.
- **Kestrel Pay (t_41253d13e2):** "Draft ready". It is a board note to aditi@quillwater.vc. That matches the cash warning (burn up 43.3%), which also names Aditi Rao.
- **Where it shows:**
  - Orbit and Kestrel also have rows on Today, which show "Draft ready".
  - Nimbus has no Today row today. It is folded into the 14:30 meeting line, which shows no draft badge.

The two promise drafts kept their commitment_ids. The hero and the guest-list row link to them.

## 4. The final line

Intro two CFO candidates: Rahul (Tallyfin), 1 day late

## 5. Where the skill text was unclear, contradictory or impossible to follow

1. **shared/connectors.md, Morning brief row, leaves out people's companies.**
   - It says: "Open deals and their companies, portfolio companies, the pass log, the LP list when LP watch is on, and CRM people (all of them: prep cards and intros need their titles)".
   - It never says to include the companies those people work at.
   - Read literally (49 companies), Fatima's line loses "(Talentbridge)". The engine also cannot tell that Raj Malhotra works at a bank.
   - I included those companies (84 in total).
2. **skills/morning-brief/SKILL.md step 6.6 and skills/pulse/SKILL.md step 3 pull against each other.**
   - Step 6.6 says: "One email per person".
   - Pulse step 3 says: "If snap/drafts already holds a draft to the same person ... rewrite that one under its id rather than adding a second".
   - Today three drafts go to Aditi: two board notes and the team note. The engine set no "also" or "join" on them.
   - A draft carries only one action_id. So merging them would leave an ask row without "Draft ready". I kept them separate.
3. **skills/morning-brief/SKILL.md step 6.1 does not fit an intro of two candidates.**
   - It says: "An introduction goes to both people: to is one, cc the other."
   - That does not cover one founder and two candidates, and the owed entry had no cc.
   - Its own example gap, "[add the two names]", also pulls against "the names from People or the CRM".
   - I named the only two CFO candidates in the CRM and copied both. The draft's context asks Tara to confirm they are the right two, and that they are happy to be copied together.
4. **skills/morning-brief/SKILL.md step 7 asks for something it gives no way to do.**
   - It says: "If the hero already covers a point, drop the duplicate line."
   - Yet it also says to report problems "rather than reordering by hand", and gives no way to remove a line from engine output.
   - The 11:00 meeting line repeats the hero. I left it.
5. **shared/safety.md's guard rules make the bundle heavy to write.** The guard allows Bash only for the engine and plain file commands. So a morning brief bundle (100 people, 84 companies, 37 deals, 20 passes) has to be typed out with the Write tool. That is heavy and easy to get wrong.
6. **Minor:** slots for a draft that offers no times is not specified. I used an empty list.

## 6. What went wrong or looked wrong

1. **The Nimbus warm path vanished (engine).**
   - Cause: the engine counts a colleague's CRM relationship strength only if that colleague shows up as a person in the bundle's mail, calendar or notes. It never adds firm members from the config as people.
   - Tara's 7 days of mail and 30 days of calendar never include Aditi.
   - Because the morning brief reads CRM people, brief.py recomputes the ask paths, and the path is lost.
   - Proof: adding the single thread th0343, which has Aditi on it, brings back note_kind "colleague" (Raj Malhotra, Fable Bank).
   - Effect on Home: the batch overwrote Home's asks with paths set to null, so the row will now say "No warm path found: ask your team".
   - The hourly pulses read no CRM people, so they keep the path. The run that reads the most loses it.
2. **The prep card and the asks document now disagree.** The 14:30 card still says "Aditi knows Raj Malhotra". prep.py reads Home's old asks before brief.py recomputes them.
3. **A prep question seed has a grammar slip:** "What would make the an introduction to two banks as customers easiest for you?" It comes from engine/instinct/prep.py line 259.
4. **Ask dates in the seeded Home do not match their sources.**
   - Orbit says "asked on 05 Oct", but upd_orbit is dated 11 Oct.
   - Kestrel says 06 Oct, but upd_kestrel is dated 08 Oct.
   - This changes the "asked on" text. Asks also drop off Today after 21 days, so they leave early.
5. **No linking line between Aditi's three drafts.** The engine marked none of them with "also".
6. **Meeting lines never show "Draft ready" for an ask note.** The engine links only promise and question drafts to them.
7. **The hero is repeated** in the 11:00 meeting line.
8. **The run row's "finished" equals "started" (06:28).** The engine stamps the bundle's "now", not the real finish time.
9. **The hero is marked as a breach for a late promise.** shared/delivery.md keeps "Breach" for figures past a threshold. This is minor, since Home styles late heroes as urgent anyway.
10. **Eval harness problems:**
    - The `bundle` shortcut is far wider than the morning brief window: 45 threads back to 29 Jun, all deals, LPs and KPIs, and its "now" is 07:00. Comparing against it hides issue 1.
    - Mock Gmail search ignores participants. "George" found nothing, and "venue" matched "revenue".
11. **Most mail is placeholder text.** So two drafts keep honest gaps: the candidates' backgrounds and the guest list.

## Brief check (morning-brief step 7)

- The hero states a fact.
- Every line has a source.
- The late promise sits above the lines where Tara is waiting on others.
- 191 of 350 words.
- No questions were asked of the user, and no connector cards were needed.
