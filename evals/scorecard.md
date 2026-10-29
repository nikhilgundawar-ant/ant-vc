# ant. for VCs: eval scorecard

Run at 29 Oct 2026 14:05. Golden fund: Quillwater Ventures (fictional).

**235 of 235 checks pass.** 7 Claude-run scores skipped: no saved run.

| Suite | Check | Result | Threshold | Pass |
| --- | --- | --- | --- | --- |
| resolution | true merges | 15/15 | >= 95% | yes |
| resolution | false merges | 0 | 0 | yes |
| resolution | initial-only pairs sent to review | 1/1 | all | yes |
| setup | level inferred | 6/6 | 6/6 | yes |
| pipeline | stale deals exact per owner | 4/4 | all | yes |
| pipeline | fresh deals not flagged | 0 false | 0 | yes |
| pipeline | competing-fund signals caught | 8/8 | all | yes |
| pipeline | false competing signals | 0 | 0 | yes |
| pipeline | deadlines read correctly | 8/8 | all | yes |
| meetings | true commitments accepted by the checker | 60/60 | all | yes |
| meetings | due dates kept | 60/60 | all | yes |
| meetings | non-participant and invented quotes rejected | 2/2 | all | yes |
| triage | thesis decisions agree (engine) | 30/30 | >= 85% | yes |
| triage | pass log re-surfaced | Paysa Labs, Ruplink | Paysa Labs, Ruplink | yes |
| safety | injected instructions detected | 3/3, 0 false | all, 0 false | yes |
| portfolio | KPI drift flags exact | 5/5, 0 false | 5/5, 0 false | yes |
| portfolio | board prep found 3 days ahead | Orbit Treasury | Orbit Treasury | yes |
| lp | an LP you meet today is not marked overdue | lp_northgate | lp_northgate | yes |
| lp | LP alerts exact | 3/3, 0 false | 4/4, 0 false | yes |
| lp | an LP behind on a capital call is flagged with the amount | $150K still due on the capital call of 05 Oct, 17 days ago | Peregrine Trust, $150K | yes |
| lp | fund summary: committed, called, unfunded | Fund II: 80000000, 45% called, 44000000 unfunded | Fund II: $80M, 45%, $44M | yes |
| lp | one owner per LP: a colleague's LP stays off your Today | Aditi: 0 LP lines, 4 with the team; Vikram: 3 his | Aditi 0 lines, Banyan with Vikram | yes |
| lp | letter checklist | complete and missing detected | both | yes |
| network | a founder's intro ask shows who in the firm can make it | Raj Malhotra Fable Bank Aditi | Raj Malhotra, Fable Bank, via Aditi | yes |
| network | intro paths correct | 20/20 | >= 90% | yes |
| network | relationships going cold | 4/4, 0 false | 4/4, 0 false | yes |
| brief | top-5 matches what each person should see first | 24/30 | >= 80% (24/30) | yes |
| brief | word budget and item count per level | 6/6 | 6/6 | yes |
| meetings | prep cards complete with linked sources | 16/16 | all | yes |
| schedules | two scheduled tasks per level | 7/7 | all | yes |
| schedules | each run does what is due, one at a time | 14/14 | all | yes |
| tuning | changes follow the ratings | 5/5 | 5/5 | yes |
| safety | source, quiet and memo checks | 3/3 | 3/3 | yes |
| safety | injection cases | 50/50 | all | yes |
| homedb | snapshot sizes, batches and version pins | max 62 KiB, 17 docs | <= 256 KiB, pins kept | yes |
| actions | Home taps flow back through the engine | 6/6 | all | yes |
| safety | no send tools in skills | 0 violations | 0 | yes |
| plugin | skills well-formed | 14/14 | all | yes |
| design | design lint (tokens, radii, spacing, type, mark) | 0 drift | 0 | yes |
| replay | 5 days of runs keep Home whole (aditi) | 214/214 | all | yes |
| replay | 5 days of runs keep Home whole (vikram) | 212/212 | all | yes |
| outage | crm down for 4 hours: Home holds and says so once | 217/217 | all | yes |
| outage | email down for 4 hours: Home holds and says so once | 217/217 | all | yes |
| quiet | a quiet deal stays in the user's own Home | 5/5 | all | yes |
| text | text from email cannot carry links or markup | 5/5 | all | yes |
| forged | only approvals that match a shown proposal are applied | 4/4 | all | yes |
| trim | big documents keep the newest items under 240 KiB | 4/4 | all | yes |
| push | six meetings: one heads-up each, never one twice | 3 pushes, 6 meetings covered | 6 covered, no repeats, at most 4 others | yes |
| tuning8 | eight Sundays: each rating counts once, never against its sign | 3/3 | all | yes |
| fund2 | a second fund with other names and CRM labels | 4/4 | all | yes |
| guard | scheduled runs: only reads, Home, approved changes, drafts and the engine | 718/718 | all | yes |
| round2 | morning push names a different item each day | t_498a67cc66 / t_ee4d26d476 / t_133a6cb737 | three different | yes |
| round2 | prep pushes first, the sync folds in; the review waits for a free run | prep:ev_atlas_today + ['prep:ev_partner_sync'], then None, None, None | prep with the sync folded in, then nothing while busy | yes |
| round2 | owed emails are drafted and linked to their promise | 3 owed, linked True, batch True | all | yes |
| round2 | analyst: a reply per new pitch, passes too, none flagged or to founders already met | 19 replies: call, more_info, pass | 1 to 20, includes pass, none flagged, none met | yes |
| round2 | a deal you meet today is never stale for no contact | not stale | no contact reason | yes |
| round2 | their deadline before our next step is flagged | Their deadline 23 Oct is before your next step 24 Oct | Their deadline 23 Oct is before your next step 24 Oct | yes |
| round2 | partner sync decision pack, quiet deals left out | Gravity Payouts, Atlas Settlement, Beacon Credit Rails, Ironwood Compliance | Gravity and Atlas; quiet one out | yes |
| round2 | board tomorrow: the open promise pushes the evening before | Orbit Treasury board tomorrow 10:00. You promised to review the board deck by 22 Oct | Orbit Treasury board tomorrow | yes |
| round2 | pass-log returns lead with the verdict; Platform leads with asks | Revisit condition met: AA licence granted in Septe | Kestrel Pay: introductions to senior engineers, two hires this quarter | verdict first; asks first | yes |
| round6 | no push inside a meeting or in the 15 minutes before one | 0 of 51 | 0 | yes |
| round6 | at most four pushes a day, every member, Thursday to Monday | 0 days over | 0 | yes |
| round6 | every pushed item is on that run's Today | 0 hidden | 0 | yes |
| round6 | one sync pack for every attendee; rows name lead, partner, round and amount | 12 rows, same, Sterling AA in | same rows for all three, every field filled | yes |
| round6 | heads-ups say how late a promise is; Thursday names Kabir's Kite checklist | 0 'promised by' lines; Share the diligence checklist: Siddharth (Kite Pay), 2 days late. Draft ready | 0; the checklist, N days late | yes |
| round6 | calendar truth to Monday: no stale, no 'confirm the slot', Gravity not stale | 0 found | 0 | yes |
| round6 | an analyst's Today: one grey colleague line, after their own work | ok | ok | yes |
| round6 | owners keep the founder's words: Vaultline 'until next week', Trellis 'our Series A' | Vaultline True, Trellis True | True, True | yes |
| round6 | Lumen's agenda carries Maya's Q3 deck, not Vertex | You owe: send the cohort analysis questions (overdue) / Watch: two other funds in diligence / They owe: send the updated deck with Q3 numbers (13 days late) | Q3 deck, no tech diligence | yes |
| round6 | Vikram's Q3 letter on Today Thu and Fri, in Friday's line, already drafted | Today Thu+Fri; Fri: Due today: sign off on the capital account statements and Q3 LP letter draft; drafted True | Thu+Fri; the letter; True | yes |
| round6 | every founder ask on Tara's Today: a path or 'none found', and a draft to make | 2 asks, 0 incomplete | all complete | yes |
| round6 | clean words, one slot per draft, reasons on pitches, a solo GP's own world | 0 cut, 0 empty, 0 repeated slots, 0 unexplained calls, solo: 0 team meetings, $30M | 0, 0, 0, 0, 0 team meetings, $30M | yes |
| round3 | seven meetings: every one gets a heads-up, and the board-eve line goes out | 7 of 7 covered, board-eve sent | 7 of 7, sent | yes |
| round3 | no morning line repeats word for word on the next morning | 0 repeats | 0 | yes |
| round3 | deadline day wins the morning push | Sable Fraud AI: term sheet from Monsoon Arc Ventures, decide today | Sable Fraud AI | yes |
| round3 | a Monday board: board-eve on Sunday; Monday opens with the morning line | Sun 17:24 Orbit Treasury board tomorrow 10:00. You promised to review the board deck by 22 Oct; Mon 06:24 Intro Arjun to Raj Malhotra at Fable Bank: Gravity Payouts, 6 days late | board tomorrow Sunday, morning line Monday | yes |
| round3 | a run by hand records no push | False | False | yes |
| evals6 | sync pack: rivals, then votes, stalled last and not counted as decisions | 3 rivals, 5 votes, 3 stalled; finding: Decide on Sable Fraud AI by 23 Oct, and 7 more | ordered; finding counts decisions only; stage kept beside another fund's term sheet | yes |
| evals6 | pitch facts keep every place the founder names | Seed, $3M, treasury management, Delaware and Bangalore | ends 'Delaware and Bangalore' | yes |
| evals6 | a prep card shows the invite's address, not a merged alias | abhishek.joshi@sablefraud.ai | abhishek.joshi@sablefraud.ai | yes |
| evals6 | a founder's unanswered question: a line with their words and a drafted answer | Copperleaf Collect: Debashish asked on 13 Oct, no reply yet | "If we get to a term sheet with you, what would the timeline look like?" | owed ['debashish@copperleaf.in'] | stale rows 0 | Debashish asked on 13 Oct; the exact quote; one answer owed; no 'no contact' row | yes |
| evals6 | the question stays through a pulse and goes once Meera answers | kept True, gone True, row asked False | kept, then gone | yes |
| evals6 | setup's line is shown in chat, not pushed | pushed False, shown_in_chat True | False, True | yes |
| evals6 | a pitch from a founder you already write to: in touch, no cold reply | in_touch: Score 90: you already write to them: answer in your thread. Pre-seed, $1M, KYC for cooperative banks, Pune; replies 0 | in_touch; 0 replies | yes |
| evals6 | your own reply inside the pitch thread counts as in touch | in_touch True; replies 0 | True; 0 | yes |
| round10 | the windowed week matches the full replay for all seven: hero, Today and push at every run | 0 runs differ | 0 | yes |
| round10 | a draft with blanks says how many lines and who holds the view; its push never says only 'Draft ready' | Fri row:  Draft has 3 lines to fill: check the firm's view with Aditi; Mon push: Share feedback after the partner meeting: Omkar, 7 days late. 3 lines to fill; Fri refresh note: ines before you send. Check the firm's view with Aditi before you send | 3 lines to fill, Aditi; no 'Draft ready'; keeps 'Fill in the 3 lines' | yes |
| round10 | the hero's and rows' drafts carry what to check; the holder regex is whole | Kabir hero: True; rows: 1; Vikram: True; no backspace: True | True; 1+; True; True | yes |
| round10 | Meera's feedback and pricing promises name the partner who holds the firm's view | Omkar: Aditi Rao; Neha: Aditi Rao | Aditi Rao; Aditi Rao | yes |
| round10 | a sent capital-call chase reads 'chased Peter on 22 Oct', a second note comes after five quiet working days | vikram: chased True, second ['dr_l_cbd6326c5a_2'], 'no touch' after 0; solo: chased True, second ['dr_l_cbd6326c5a_2'], 'no touch' after 0 | True, one _2 draft, 0 for both | yes |
| round10 | one note to Aditi with no reply: one nudge drafted for its asks, one row on Today, one push | nudges 1 for [2] asks; group rows 1; single rows 0; nudge pushes ['Nudge Aditi on Kestrel Pay and Orbit Treasury: no reply since 22 Oct. Note ready'] | 1 for 2; 1; 0; 1 push | yes |
| round10 | eighteen days on (Mon 9 Nov), the asks still know who was asked, stay on Today and are never asked again | notes kept ['Kestrel Pay', 'Nimbus Collect', 'Orbit Treasury']; on Today ['Kestrel Pay', 'Orbit Treasury']; first notes again 0 | Orbit and Kestrel; both; 0 | yes |
| round10 | a young ask with its note sent is never drafted again, however long the reply takes | first notes again on [] | none | yes |
| round10 | a tap applied on 22 Oct is not offered again on day 29 or day 31 | day 29 pending []; day 31 pending [] | []; [] | yes |
| round10 | a waiting nudge chases nothing once a later note went out or the intro was made | open False; later note True; made True | False; True; True | yes |
| round10 | late work stays: Aditi's paragraph and Vikram's wait on it every morning to Fri 30; Halo's step request lasts | Aditi missing []; Vikram missing []; Fri 30 Halo asks True; headline: 11 things for today, 6 urgent, 2 next steps to add | none; none; True; next steps to add | yes |
| round10 | no push ends in an ellipsis and no line is only who wrote and when, on real windows to Fri 30 | 0 cut pushes; 0 bare quotes | 0; 0 | yes |
| round10 | the letter row says Draft ready on its first run; a met log never offers a past date; moves keep the name's capital | letter: raft ready: fill in 5 lines, check the figures, then send it; Solace due ''; moves [] | Draft ready ... check the figures; '' or later; no lowercased company | yes |
| round10 | the letter's inputs hold no paid-in figure, and letter-check flags one | paid keys []; flagged ['Fund II: $80M, 45% called. Paid in: $35.85M']; complete False | []; one line; False | yes |
| round10 | a promise due Monday is drafted by Friday; a team note names a colleague in full when the founder shares the name | Ember drafted by Fri: True; team to_name: Aditi, Kabir, Meera, Rohan and Vikram Nair | True; ...Vikram Nair... | yes |
| round9 | a windowed week keeps the warm path, and the intro shows as made by Mon 13:28 | path lost at 0 runs; made at Mon 12:28; Mon 13:28: Intro made on 26 Oct. Divya Raman asked on 13 Oct. Warm path | 0; Mon 12:28; Intro made on 26 Oct | yes |
| round9 | Aditi's and Vikram's windowed weeks keep every path, board partner and morning line of the full replay | 0 differences | 0 | yes |
| round9 | asks stay on Today until made or closed; Thu 29 asks for a nudge; no push names a waiting ask | 0 mornings missing; nudges Thu 29: 1; bad pushes: 0 | 0; 1; 0 | yes |
| round9 | 'Yes, ask the team' gets its own tap and note; once sent, the row says the team was asked | tap pending True; linked dr_t_3461c2ec2f_team; after: Asked the team | True; dr_t_3461c2ec2f_team; Asked the team | yes |
| round9 | after a blank-step met log: Today asks for the step daily; no Pipeline reads the old step; Aditi dates the move | blank ['Halo Reconcile', 'Rivulet Payments']; runs without the ask 0; old step shown 0; Aditi's Halo days {'Fri 23': 1, 'Tue 27': 5, 'Thu 29': 7} | Halo and Rivulet; 0; 0; Fri 1, Tue 5, Thu 7 | yes |
| round9 | the capital call is drafted before the brief, the hero says Draft ready, and the solo GP keeps the row | chase notes 1; heroes [True, True]; solo mornings without it [] | 1; [True, True]; [] | yes |
| round9 | nothing due vanishes: Aditi's Monday chore, Vikram's fee offset; pushes record only what they name | chore missing at []; fee offset 1; unnamed subjects 0 | []; 1 or more; 0 | yes |
| round9 | words stay true: dated quote, met pitches off inbound, first call, today's review count, the call named, the board's question | Tanvi wrote on 21 Oct: "Our ; inbound 0; Paysa First meeting; Nothing new; 12:00 Beacon Credit Rails: Term sheet, day 5; Orbit [True, True] | dated; 0; First meeting; no stale count; the call; runway with hiring | yes |
| round9 | the solo sample speaks for one person: every deal hers, no partner words, no colleague | owners ['aditi@quillwater.vc']; 0 lines | her alone; 0 | yes |
| round9 | the headline counts meetings to log; a refresh with no notes asks you to check it | 11 things for today, 5 urgent, 4 meetings to log; 13 refreshes, 13 ask to check | names the meetings to log; all | yes |
| round8 | real runs keep the links: every ask note keeps its tap, and Sent it moves the row on | 1 of 1 kept; Mon requested:Asked Aditi, requested:Asked Aditi for the intro; next Fri nudge:Nudge | all kept; asked the team or a colleague, then a nudge | yes |
| round8 | heads-ups name what you owe: Helen's fee offset at 14:20, Orbit's deck or runway on Friday | 15:30 Northgate Endowment: You owe them: answer the fee offset question, 43 days late / 10:00 Orbit Treasury: You owe them: review the board deck, 1 day late | fee offset; deck or runway | yes |
| round8 | late founder promises on contested deals beat chores: Aditi's Monday push, Meera's Monday hero | Intro Arjun to Raj Malhotra at Fable Bank: Gravity Payouts, 6 days late. Draft ready / hero: Share feedback after the partner meeting | the Atlas markup or another late founder promise; Omkar's feedback | yes |
| round8 | the CFO's list: own late work first on Monday; no Overdue weeks before a window; Friday's letter in Next up | Mon first: Answer the fee offset question; far Overdue 0; letter at 1 | a promise of his; 0; in Next up, above LP touches | yes |
| round8 | words survive the budget: Tanvi's 'until next week', the sync's 'with yours' | 0 Vaultline, 0 sync | 0, 0 | yes |
| round8 | no hour offered twice to one person across the team; a call with Kabir copies him in | 0 clashes; Kabir copied on 3 of 3 | 0; all | yes |
| round8 | refreshed drafts greet only who was there and drop lines the meeting made untrue | 0 found | 0 | yes |
| round8 | one tap clears the team's Pipeline; 'Move to Closing' is a real move | 3 of 3 pending; stale for Aditi: none; days in the new stage {'Rivulet Payments': 1, 'Halo Reconcile': 1}; Closing pending True | 3 of 3; none; 1 day each; True | yes |
| round8 | asks addressed and words clean: firm addresses, the board partner first, the path in the dinner heads-up, no team words solo | to True; board-first 2; dinner: 14:30 Founder community: Divya needs two banks as customers: Aditi knows Raj Malhotra; 0 'intro to'; solo 0 | True; 2; names Aditi knows Raj; 0; 0 | yes |
| evals8 | a warm path holds when the read never saw the colleague; one note per colleague; the card agrees | path True; card agrees True; notes to Aditi 1 with 3 asks | True; True; 1 with 3 | yes |
| evals8 | an ask under a meeting line shows its note is ready | 1 linked | 1 or more | yes |
| evals8 | finance: letter row says draft ready; LP touches above soft flags; a chase note for the unpaid call; full letter inputs | row: : fill in 5 lines, check the figures, then send it; chase notes 1; LP rows at [0, 4], soft flags at []; inputs True | Draft ready; 1; LP first; True | yes |
| evals8 | letter-check lists a letter's missing sections | complete True | True | yes |
| round7 | what a push named stays on Today until the day ends | 0 dropped | 0 | yes |
| round7 | open drafts offer only times ahead, each time to one person | 0 dead, 0 double | 0, 0 | yes |
| round7 | drafts follow meetings; a drafted pass is said, not 'book a first meeting or pass' | Kite draft mentions 22 Oct: True; 0 stale pass rows | True; 0 | yes |
| round7 | pass replies say the deciding reason: geography for Zorro Pay and Ledgerly, D2C in capitals | geography True, 0 sector reasons for in-thesis companies, D2C True | True, 0, True | yes |
| round7 | own work first: Vikram's Monday line is his late work; Kabir's own promise above Rohan's | Vikram: Answer the fee offset question: Helen (Northgate Endowment), 47 days late. 1 line to fill; Kabir: own at 0, waiting at 1 | a promise of his; own first | yes |
| round7 | a founder meeting gets a one-tap log; once logged, the partner's Pipeline is calendar-true | Meera's prompts: Halo Reconcile, Rivulet Payments, Sable Fraud AI; stale for Aditi after: none | all three; none | yes |
| round7 | clean words: plurals, quotes, 'You owe:' case, no raw invite titles, a real week ahead | 0 found | 0 | yes |
| round7 | every founder ask has a note ready the first morning; the dinner line names Nimbus's path | 3 of 3 drafted; dinner: They asked: an introduction to two banks as customers. Path: Aditi knows Raj Malhotra | all; a path | yes |
| round7 | the Q3 letter is drafted from the figures; Friday's push and row agree | draft True; agree True | True; True | yes |
| round7 | Today at most 12 things; a pitch warning shows one morning; no partner words for a solo GP | 0 over, 0 repeated warnings, 0 partner words | 0, 0, 0 | yes |
| round4 | two meetings in the first morning band: both get a heads-up | prep:r4-a0, prep:r4-a1 | prep:r4-a0, prep:r4-a1 | yes |
| round4 | a first meeting with someone new gets a heads-up | 11:00 Newco Labs: First meeting with Priya Nair · then 12:00 Beacon Credit Rails | First meeting with Priya Nair | yes |
| round4 | the morning line names a promise due that day | Due today: send the term sheet markup and share the co-op bank partnership deck | due today | yes |
| round4 | no heads-up repeats that morning's line | 0 repeats | 0 | yes |
| round4 | a brief by hand stops that morning's scheduled brief | pulse | pulse only | yes |
| round4 | one email per person; no outcome drafted before the meeting that decides it | pm_ev_atlas | pm_ev_atlas only | yes |
| shared | a competing fund shared to the CRM reaches every partner's sync pack | aditi: Atlas Settlement, Beacon Credit Rails, Gravity Payouts, Ironwood Compliance, Prism Lending OS, Rivulet Payments, Sable Fraud AI, Solace Treasury, Sterling AA, Trellis Banking API, Vertex Card Issuing; kabir: Atlas Settlement, Beacon Credit Rails, Gravity Payouts, Ironwood Compliance, Kite Pay, Lumen Ledger, Rivulet Payments, Sable Fraud AI, Solace Treasury, Sterling AA, Trellis Banking API, Vertex Card Issuing | Sable and Trellis in both packs | yes |
| round5 | a heads-up never repeats the subject of that morning's line | 10:00 Sable Fraud AI: Term sheet from Monsoon Arc Ventures · then 12:00 Partner sync | the term sheet, not the reference questions | yes |
| round5 | no 'confirm the slot' before the booked meeting itself | 16:30 Halo Reconcile: Next step today: second meeting, after 12 days in first meeting | no 'confirm the second meeting slot' | yes |
| round5 | an analyst's hero and morning lines are their own work | hero: Market map of AA players; 0 colleague lines | own work, 0 colleague lines | yes |
| round5 | Thursday's sync pack: every vote, term sheet and rival | Beacon Credit Rails, Gravity Payouts, Ironwood Compliance, Sable Fraud AI, Solace Treasury (12 rows) | Beacon Credit Rails, Gravity Payouts, Ironwood Compliance, Sable Fraud AI, Solace Treasury | yes |
| round5 | Monday's pack: Sable's passed deadline is said as passed | Term sheet from Monsoon Arc Ventures, their deadline passed 23 Oct | their deadline passed 23 Oct | yes |
| round5 | no line or draft for an outcome before the meeting that decides it | 0 found | 0 | yes |
| round5 | every push fits one line, none cut mid-phrase | 0 cut | 0 | yes |
| evals5 | a pulse keeps LP owners, called capital and the call still due | Aditi's team LPs 4; Vikram's call alerts 1; Fund II 45% called | Banyan with Vikram, Peregrine's call kept, Fund II 45% | yes |
| evals5 | a draft tap for a colleague's LP is refused once and shown as Not done | refused ['l_banyan_draft'], then 0; Home row refused: Banyan Family Office is Vikram's LP: the note is theirs to write. | refused, then nothing; a refused row | yes |
| evals5 | a promise naming a third person needs that person on the meeting | Set up a call with Kabir: None | not looks done | yes |
| evals5 | a connector busy last hour reads from its last good run | notes from 06:24, email from 09:24 | notes 06:24, email 09:24 | yes |
| evals5 | no second offer to share a competing fund already shared | 3 offered, 0 again on the next pulse | 0 again | yes |
| evals5 | the build never changes Home in place: new warnings are written | Home untouched True, asks changed True | untouched, changed | yes |
| evals5 | pitches: flagged ones always shown, ask-for-more asks for facts, users are not payers | flagged shown 3, asks 5 (0 quoting a reason), Vantage signals none | 3 flagged shown, 0 reasons quoted, no paying customers | yes |
| evals5 | every level's brief fits its word budget | 0 over | 0 | yes |
| evals5 | setup: levels with evidence only; next brief after a Friday is Monday | ['finance', 'partner']; Mon 07:00 | finance and partner; Mon 07:00 | yes |
| evals5 | a follow-up from the morning's notes pushes on the next run when the day has room | tara 07:28 Follow-up ready: Talentbridge, 2 promises captured | aditi 07:24 Nothing new | Tara: Follow-up ready; Aditi: held | yes |
| round11 | a reply in mail stops the nudge: no nudge drafted or pushed, and the ask says who replied | nudges on []; nudge pushes 0; replied ['Kestrel Pay', 'Nimbus Collect', 'Orbit Treasury']; rows saying so 3 | none; 0; the asks; 1+ | yes |
| round11 | a reply from the LP holds the second chase until the day he named has passed unpaid, then it is written | second notes on ['Thu 29']; Tue 27: on 22 Oct, Peter replied on 26 Oct, saying it goes on 28 Oct; Thu 29: 8 Oct, still unpaid. Second note ready: check the amount, then send it | Thu 29 only; Tue 27 'Peter replied on 26 Oct, saying it goes on 28 Oct'; Thu 29 'said it would go on 28 Oct, still unpaid' | yes |
| round11 | a sent chase is remembered to Mon 23 Nov: never a first note again, never a third, 'chased Peter' every morning | vikram: first again 0, third 0, line True; vikram both: first again 0, third 0, line True; solo: first again 0, third 0, line True; solo both: first again 0, third 0, line True | 0, 0, True for all four | yes |
| round11 | a Pipeline step saved again after the last was applied is pending; an old tap is never pending, even without --now | re-saved ['ns_d_trellis']; same tap []; a 2-month-old tap with no --now [] | ['ns_d_trellis']; []; [] | yes |
| round11 | 'Ask the team instead' after the nudge was written narrows it: by Fri 30 the nudge names Orbit and Kestrel only | Thu 29 nudge ['Kestrel', 'Nimbus', 'Orbit']; Fri 30 rewrite ['Kestrel', 'Orbit'] (1); Thu 11:28 Nimbus row ['Team note coming'] in group False | all three; Kestrel and Orbit (1); Team note coming, not in the group | yes |
| round11 | the run that writes the nudge says it is ready: row, push and ask hero | row Nudge ready; push Nudge Aditi on Kestrel, Nimbus and Orbit: no reply since 22 Oct. Note ready; hero draft True | Nudge ready; ...Note ready; True | yes |
| round11 | late work stays: Aditi's paragraph and Vikram's wait on it to Mon 9 Nov, her contested Arjun intro while the race runs | paragraph missing []; Arjun missing []; Vikram missing [] | none; none; none | yes |
| round11 | no push names old news as new, and fund names keep their capitals, to Mon 9 Nov | 0 old-news pushes; 0 lowercased names | 0; 0 | yes |
| round11 | a deal left out of a full CRM read stays in Home, and the run warns | kept True; warned True | True; True | yes |
| round11 | a narrow read keeps company descriptions and pass ids; People's days are counted from today | description kept True; pass ids 20 of 20; wrong day counts 0 | True; all; 0 | yes |
| round11 | a Friday preps Monday's meetings | Monday cards on Fri 23: ['Monday partner meeting'] | 1+ | yes |
| round11 | the guest list is checked after Tara met its guests; the CFO draft's old 'this week' becomes a date | guest list rewrite: Written before your 22 Oct meeting with Divya, Pooja and Karthik, whom it names:; Mon CFO body has 'this week': False (True) | 'Written before your 22 Oct meeting with ...'; False (True) | yes |
| round11 | Sent it on a promise's draft keeps the promise: no new draft after the prune, no row after | redrafted []; on Today [] | none; none | yes |
| round11 | a pitch answered on Thu 22 is never answered again, to Wed 11 Nov | 19 answered; again on [] | N; none | yes |
| round11 | in a partner's Home a cash warning never tells her to check with a colleague on her own boards | warnings ['Runway under 9 months: decide whether to help hire before anyone starts looking', 'Burn up 43.3% in a month: decide whether to help hire before anyone starts looking'] | no 'check with' naming someone else, or 'your call' | yes |
| round11 | the guard refuses order-like data names at either end and Artifact reads that save files | wrongly allowed []; wrongly refused []; file-saving reads allowed 0; plain read and list True | []; []; 0; True | yes |
| scale | ten times the golden fund: fast, small, still names the deal | 0.7s, 239 KiB max | < 10s, < 240 KiB | yes |
| round12 | a pulse that sends no deals keeps every deal's CRM stage label | changed [] | [] | yes |
| round12 | on a Friday Today names Monday's meetings with their prep, Monday's card leads with what the room decides, and its questions outlast the day's pulses | tomorrow [('Monday', 'Monday partner meeting', True)]; finding Decide on Gravity Payouts by 31 Oct, and 10 more; Sable: Deadline 23 Oct passes before this meeting: decide by then w; questions at 08:29 3 | [('Monday', ..., True)]; not Sable first; 'passes before this meeting'; 3 | yes |
| round12 | Sent it on a pitch reply closes the pitch: no 'book a call' row after it | back on []; answered ['i_0e2115836d'] | []; the pitch | yes |
| round12 | a promised date that has passed reads as stale, a date looked back on never does | ['by Tue 27 Oct']; [] | ['by Tue 27 Oct']; [] | yes |
| round12 | a note marked sent at 01:45 in Mumbai counts on that day, not the day before in UTC | notes on ['2026-10-23']; Nimbus Collect: an introduction to two banks as customers Asked Aditi  | ['2026-10-23']; 'on 23 Oct' | yes |
| round12 | an email that only names a company is not a reply; a reply that answers one ask leaves the others to their nudge | board pack: replied [], nudge ['Kestrel Pay', 'Nimbus Collect', 'Orbit Treasury']; partial: replied ['Orbit Treasury'], nudge ['Kestrel Pay', 'Nimbus Collect'] | [], all three; ['Orbit Treasury'], Kestrel and Nimbus | yes |
| round12 | an email from the LP about something else is not an answer: the second note comes on day five | second notes ['Thu 29']; Thu 29 king days. Second note ready: check the amount, then send it | ['Thu 29']; no 'replied' | yes |
| round12 | an unpaid call that leads Today reaches the phone at least once in every week it leads | weeks [('2026-43', 0, 1), ('2026-44', 1, 5), ('2026-45', 1, 5), ('2026-46', 0, 1)] | each week it leads 3+ mornings: 1+ | yes |
| round12 | the undated invite to Rahul rides in the draft already waiting for him | [('dr_k_e9eab86816', 'refresh', ['Invite Rahul to the founders dinner'])] | the CFO draft, with 'Invite Rahul...' | yes |
| round12 | every promise more than a week late is on Today on Mon 9 Nov, as a row or in one line | 6 late; fold: 3 promises more than a week late: send the term sheet markup (17 days late); share the co-op bank partnership deck | none missing | yes |
| round12 | no entry that copies a third person carries what the founder owes | [] | [] | yes |
| round12 | a pitch reply unsent for a week has left Ready for you by Mon 9 Nov | 0 older than a week | 0 | yes |
| round12 | a pitch once seen 'in touch' never flips back to 'book a call' | flipped [] | [] | yes |
| round12 | a colleague's promise to you offers Got it, and a folded deal fact names the deal | waiting rows with done 6 of 6; bare 'Deal:' rows [] | all; [] | yes |
| round12 | the run that writes one ask's nudge points its row at it and its push says Note ready | draft dr_t_nimbus_team_nudge; push Still open: Nimbus Collect: nudge the team, no reply since 29 Oct. Note ready | the nudge; '... Note ready' | yes |
| round12 | a tap after the nudge was written narrows it at the next check, not the next morning | [('dr_t_1d7b287123_nudge', ['Kestrel Pay', 'Orbit Treasury'])]; rewritten ['dr_t_1d7b287123_nudge'] | the nudge, without Nimbus; rewritten at 10:28 | yes |
| round12 | one note to the partner whose view two drafts wait on: their lines and the decision near, written once, and gone once both drafts are sent | notes [('Thu 22 06', 'Aditi Rao')]; items ['Rivulet Payments', 'Trellis Banking API']; decisions ['Sable Fraud AI']; in Home 'Your view on 2 founder emails and Sable Fraud AI' holds 2; after both sent [] | one note to Aditi Rao; Rivulet and Trellis; Sable; holds 2; [] | yes |
| round12 | a reply on some of a note's asks: the rest still wait, their row says what came, and the nudge thanks first | Nimbus answered_others ['Kestrel Pay', 'Orbit Treasury']; nudge items ['Nimbus Collect']; answered ['Kestrel Pay', 'Orbit Treasury']; context 'Aditi answered on Kestrel Pay and Orbit Treasury on 26 Oct, not on Nimbus Collect: one sho'; row 'Asked Aditi for the intro on 22 Oct: Aditi answered on Kestrel Pay and Orbit Treasury on 26 Oct, not this one.'; body 'Hi Aditi,\n\nThanks on Kestrel Pay and Orbit Treasury. And Nimbus Collec' | Kestrel and Orbit; [Nimbus]; 'Aditi answered on ...'; no 'no reply'; 'Thanks on ...' | yes |
| round12 | a chased call, once paid, never reads 'no touch': the chase marked sent was a touch | 'no touch' after the wire on []; last touch 2026-10-22 | []; 2026-10-22 or later | yes |
| round13 | Done on one of two promises sharing an email leaves the other open with that email, which is rewritten for it | shared dr_k_e9eab86816 ['k_e9eab86816', 'k_76e229ee1b']; after Done on each: [('open', False, 'dr_k_e9eab86816', [['k_76e229ee1b']], ['k_76e229ee1b']), ('open', False, 'dr_k_e9eab86816', [['k_e9eab86816']], ['k_e9eab86816'])] | open, not sent, draft kept, narrowed to the other | yes |
| round13 | an undated promise that rides in an email keeps that email on its row at every run | [('Fri 23 06', 'dr_k_e9eab86816'), ('Fri 23 07', 'dr_k_e9eab86816'), ('Fri 23 08', 'dr_k_e9eab86816'), ('Fri 23 09', 'dr_k_e9eab86816')] | the draft at every run | yes |
| round13 | a reply that lands before Sent it is a reply, for an ask and for a chase | ask nudges on []; replied ['Kestrel Pay', 'Nimbus Collect', 'Orbit Treasury']; Vikram Mon 26: 'Peregrine Trust owes $150K on a capital call Called on 05 Oct, 21 days ago; chased Peter on 23 Oct, Peter replied on 22 Oct, saying it goes ' | []; all three; 'Peter replied on 22 Oct' | yes |
| round13 | a reply the morning found changes the ask, its row and the push | ask replied t_k 2026-10-27T11:00:00+05:30; row 'Aditi replied on 27 Oct: read it, then answer here'; push 'Kestrel Pay: Aditi replied on 27 Oct'; ['asks', 'push:Kestrel Pay: Aditi replied on 27 Oct'] | t_k; 'Aditi replied on 27 Oct' | yes |
| round13 | a deal marked quiet is in no note to a colleague | holder decisions []; 'Sable' in its text: False | []; False | yes |
| round13 | the note to a partner: no other note once answered or while it waits on her; a held draft sent narrows it; one id | answered: new notes [], replied kept True; unanswered: new notes []; narrowed at Fri 23 07: [['Trellis Banking API']]; ids ['dr_hold_aditi_rao'] | [], True; [] or a later note for new drafts only; [Trellis]; one id | yes |
| round13 | a decision whose deadline passed leaves the note to a partner in one rebuild, subject and all | rebuilt on ['Sat 24 09']; subject 'Your view on 2 founder emails'; decisions [] | once, Sat 24 09; no 'Sable'; [] | yes |
| round13 | no past day is a promised one; 'fund' alone is no answer; only dates still ahead when written go stale | paid last Friday None; Monday's call, next week 2026-11-06; AGM naming the fund counts False; closed until 20 Oct []; introduce you Thu 29 Oct on Fri 30 ['Thu 29 Oct'], on Thu 29 ['Thu 29 Oct'] | None; 06 Nov; False; []; ['Thu 29 Oct'] both | yes |
| round13 | an unpaid call on Today reaches the phone in every week it is there on three mornings or more, for a team or one person | {'vikram': [('2026-43', 2, 1), ('2026-44', 5, 1), ('2026-45', 5, 1), ('2026-46', 5, 1), ('2026-47', 5, 1), ('2026-48', 1, 0)], 'solo': [('2026-43', 2, 0), ('2026-44', 5, 1), ('2026-45', 5, 1), ('2026-46', 5, 1), ('2026-47', 5, 1), ('2026-48', 1, 0)]} | no week with 3+ mornings and no push | yes |
| round13 | a narrow people read on a Home with no directory warns; with one it does not | no directory: ["People were read only at today's companies, and Home has no directory yet: warm paths through anyone else are missing until a wide read. Read people and companies wide on the next run."]; with: [] | a warning; none | yes |
| round13 | 'Aditi said yes: ask the team' after the nudge was written narrows it at the next check | [['Kestrel Pay', 'Nimbus Collect']] | the nudge without Orbit | yes |
| round13 | Today never goes over its item cap, the late-work line included | cap 5; over on [] | [] | yes |
| round13 | 'Yes on Orbit. Let me think about the other two.': Orbit is answered, the others wait, and no line says 'no reply' | {'Nimbus Collect': (False, True), 'Orbit Treasury': (True, False), 'Kestrel Pay': (False, True)}; nudge [['Kestrel Pay', 'Nimbus Collect']]; push 'Aditi answered on Orbit Treasury; Kestrel Pay and Nimbus Collect still wait. Note ready' | Orbit replied; Kestrel and Nimbus answered_others; nudge on those two; no 'no reply' | yes |
| round13 | a reply that puts off its answer is nudged five working days on | nudges on ['Mon 02 06'] | one, by Tue 3 Nov, none before Mon 2 | yes |
| round13 | a reply that left Home is not written again, and a wide read never brings back a pitch older than two weeks | Harborline written again on []; old pitches back on Mon 9 Nov: [] | []; [] | yes |
| round13 | a passed deadline is never 'Another fund is moving' | [] | [] | yes |
| round13 | the Friday trim keeps the race once, and a review push never leads with a passed race unflagged | Arjun's row without the race on []; unflagged Atlas pushes [] | []; [] | yes |
| round13 | after Sent it, the CRM's old step never reads as the next step | [] | [] | yes |
| round14 | a reply counts even when you wrote again in the thread before Sent it | nudges []; replied ['Kestrel Pay', 'Nimbus Collect', 'Orbit Treasury'] | []; all three | yes |
| round14 | no 'no word from Aditi' push after she replied, even when Sent it came the next morning | [] | [] | yes |
| round14 | a note sent the day before its decision, unanswered, is followed at 14:00 on the deadline day | [('Fri 23 14', 'Sable Fraud AI: no word from Aditi yet, decide today')] | one, Fri 23 14 | yes |
| round14 | with two drafts and no decision, sending one rebuilds the note for the one left | holds ['dr_k_a4b63d1828']; subject 'Your view on 1 founder email' | one hold; 'Your view on 1 founder email' | yes |
| round14 | a note to a partner saved in Gmail is never rebuilt | rebuilds [] | [] | yes |
| round14 | a date ant. put in a draft is stored as its own and moves again when it passes, never kept | [('Mon 26 06', 'instinct', ['this week']), ('Thu 29 06', 'instinct', ['by Wed 28 Oct'])] | later redates set_by instinct | yes |
| round14 | a reply the morning found that puts off its answer keeps 'defers' | {'on': '2026-10-27T11:00:00+05:30', 'by': 'Aditi', 'defers': True, 'tap': 't_k'} | defers True | yes |
| round14 | 'the call' and 'pay a visit' are no answer about money; a wire or a payment is | {'Thanks for the call yesterday. See you at the AGM in December.': False, 'Happy to pay a visit when I am in Bangalore.': False, 'The wire goes out on Wednesday.': True, 'We will pay the capital call this week.': True} | False, False, True, True | yes |
| round14 | Sent it as the page writes it keeps the promise sent, and its step in sent_steps | sent [True]; steps {'c_atlas|send term sheet markup': '2026-10-23'} | True; the markup | yes |
| round14 | a CRM read that drops round and raise keeps what Home knew, and the run warns | Trellis Series A 6000000; ["This run's CRM read left out round on 37 deals, raise_usd on 37 deals: Home kept what it knew. Send every field on the next read."] | Series A, 6000000; a warning | yes |
| round14 | the nudge after a reply that put off its answer stays until it is sent | [('Mon 02 07', True), ('Mon 02 08', True), ('Mon 02 09', True)] ... [('Wed 04 06', True), ('Wed 04 07', True)] | True at every run | yes |
| round14 | 'We paid it last Friday' gets no second chase in five working days, and says to check the account | second notes []; Mon 2 Nov: 'Peregrine Trust owes $150K on a capital call Called on 05 Oct, 28 days ago; chased Peter on 22 Oct, Peter says it was paid (26 Oct): check the account' | []; 'says it was paid' | yes |
| round15 | a thread trimmed to your thank-you is no read: no 'no word from Aditi' push | [] | [] | yes |
| round15 | a Sent it tap four days after the note still finds the note, so Thursday's reply counts | nudges []; replied ['Kestrel Pay', 'Nimbus Collect', 'Orbit Treasury'] | []; all three | yes |
| round15 | 'payment was made', 'already been paid' and 'the wire went out' read as paid; a visit does not | {'Payment was made last Friday.': True, 'It has already been paid, on Friday.': True, 'The wire went out on Friday.': True, 'We paid it last Friday.': True, 'I paid a visit to your office.': False, 'We have not paid it yet.': False, 'It was great to see you.': False} | {'Payment was made last Friday.': True, 'It has already been paid, on Friday.': True, 'The wire went out on Friday.': True, 'We paid it last Friday.': True, 'I paid a visit to your office.': False, 'We have not paid it yet.': False, 'It was great to see you.': False} | yes |
| round16 | an applied CRM change is put back: same record, stage from Diligence to First meeting, the note left alone | [{"field": "stage", "current": "Diligence", "proposed": "First meeting"}] | one field reversed | yes |
| round16 | a change never applied, a note only, an unknown change and a withdrawn tap are not put back | refused ['rv_p2', 'rv_p3', 'rv_zz']; pending ['rv_p1'] | rv_p2, rv_p3, rv_zz refused; rv_w ignored | yes |
| round16 | a reversal applied once is never offered again | [] | [] | yes |
| round16 | a Sheet CRM says to change it back by hand | [{"id": "rv_p1", "type": "revert", "why": "Your CRM is a Google Sheet, which ant. cannot write to. Copy the change from  | refused | yes |
| round17 | automatic mode applies a proposed CRM change and an own-calendar hold untapped, marked auto | pending ['p1', 'p3'] | p1, p3 | yes |
| round17 | a skipped change, a hand-copied one and an applied one stay put; an invite or an unknown field is still refused | refused ['p4', 'p7']; engine ['p2'] | p4, p7 refused; p2 skipped | yes |
| round17 | with automatic mode off or never set, nothing applies without a tap | [] [] | [] [] | yes |
| round18 | a CRM and calendar set to read only in Settings take no change, tapped or automatic, and say why | pending []; refused ['ns', 'p1', 'p2'] | none; ns, p1, p2 | yes |
| round18 | set back to update, they apply | ['ns', 'p1', 'p2'] | ns, p1, p2 | yes |
| llm | commitments read from meeting notes | skipped | - | skipped |
| llm | inbound triage agrees with partner judgment | skipped | - | skipped |
| llm | memo claims linked to a source | skipped | - | skipped |
| llm | Claude-written brief leads with the right five | skipped | - | skipped |
| llm | prep cards: who, three questions, source | skipped | - | skipped |
| llm | KPIs read from founder updates | skipped | - | skipped |
| llm | scheduled pulse applies only what was shown, safely | skipped | - | skipped |
