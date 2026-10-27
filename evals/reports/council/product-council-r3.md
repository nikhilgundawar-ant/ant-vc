# Instinct for VCs: product council, round three

Written by the Claude agent that played the council (saved here by the lead session, which received it as text). **Simulated council:** one model played a product manager, a UI/UX designer, an AI engineer and a QA lead. No real person reviewed the build. Reviewed 23 Oct 2026 against commit 6ebd923 (version 0.3.0). The repo stayed clean; all reviewer outputs went to a scratch folder.

## Scores

| Reviewer | Round two | Round three | In one line |
|---|---|---|---|
| PM | 6 | 7 | Most round-two asks shipped and every pack reads like a real product. But go now depends on a real-account smoke test nobody has run, and four push cases still drop. |
| Designer | 7 | 8 | Hero grammar, contrast, 40px targets and the stall banner are fixed, and a fresh run confirms it. What is left is copy polish and one crowded hero. |
| AI engineer | 5 | 6 | The guard is now a real allowlist and blocks every round-two probe. But it misses two invite paths in the live schemas, turns itself off on some transcript layouts, and does not limit Write, Edit or Bash. |
| QA lead | 5 | 6 | The evidence now reproduces from the commit. But the mock still offers a Gmail tool the real account lacks, and the Claude-run scores predate the round-three skills. |

**Average: 6.75** (round two: 5.75).

## Verified fixed since round two

- **Guard is an allowlist.** All 23 outbound probes denied in a scheduled transcript (round two's 12 plus 11 more sends, shares and state writes); the same 23 pass untouched in a normal session. All 13 legitimate run calls pass.
- **Drafts are honest** in README, TRUST.md, delivery.md, morning-brief step 6.4 and Home ("Ready to send" or "In your Gmail drafts", a filled-in compose link). The QA check passes.
- **Drafting mark**: the run row is marked before each draft; the engine skips marked ids for two days.
- **One email** for a promise plus a pitch reply to the same person.
- **Reads**: runs from `query` ordered by `started`; versions.txt found automatically; every write to an existing document carries its version; `update` merges nested objects, so marks and taps do not overwrite each other.
- **Pushes**: the cap counts only found items; Kabir's 11:30 and 12:00 meetings each get a heads-up; a displaced review follows next run; board-eve goes out in a Sunday week-ahead run; Meera's Friday push names the deadline due that day; "Still open" repeats work; a run by hand records `pushed: false`.
- **Schedule**: across 1,200 configs the first run is always 31 to 44 minutes before the brief, never on :00 or :30, and the brief is due on it. `next_check_at` is right over the weekend. Home's stall banner reads it, and the header and banner show the same time.
- **Home**: hero grammar, 3:1 selected states (48 states, 0 fails), 40px header targets, analysts open on Mine with Inbound first, "Ready to send" in the prep sheet, Copy for partners, "Asked N days ago", "Today", "Pitches", and the Platform hero links to the ask's own thread.
- **Evals**: missing Claude runs show SKIP; partial QA runs write their own file; qa.json's page hash matches the commit; fresh Home QA 333 of 333; design lint 0 violations; packs regenerate byte-identical; `claude plugin validate .` passes with two directory warnings (no LICENSE, no privacy URL).

## Bugs and risks reproduced

1. **Guard: calendar invites still pass** (high). Only top-level `attendees`, `attendee_emails` and `guests` were checked. Google Calendar's `create_event` also takes `attendeeEmails`, and Notion Calendar nests attendees inside each event. Both were allowed in a scheduled run.
2. **Guard: writes TRUST.md says are blocked still pass** (medium to high): Notion `update-data-source` (schema change, `in_trash`), Notion `update-page` with `apply_template`, `notion-update-enabled-skills`, the device calendar, ArtifactData writes to an artifact other than Home, Write and Edit on any path (including the plugin's own files), and a CRM change with no approval in Home (the guard cannot know approvals; TRUST.md said it enforced them).
3. **Guard: fails open on some transcript layouts** (medium to high). Only the first user text row within 400 lines was checked for the marker. With one meta row first, all probes were allowed.
4. **Guard: shell and read rules match words, not commands** (medium). The Bash check scans text; read tools are recognised by a leading verb, so names like `outlook_email_search` or Carta's `discover` are denied.
5. **Push: a second meeting in the first morning band gets no heads-up** (medium). Daily mode returned the hero line before looking at other meetings in the band.
6. **Push: a first meeting with someone new gets no heads-up** (medium). Cards without a `finding` were skipped.
7. **Push: a Monday board wipes out Sunday's week-ahead line** (medium-low). The deferred week-ahead line never went out; the repo test stopped at Sunday 18:30.
8. **Brief: a partner's promises due today drop out of the brief and the push** (medium). Aditi's Friday markup and co-op deck promises ranked 8th and 9th behind two decisions.
9. **Drafts: two emails to one person** (low to medium). `_owed` checked for an existing draft only for pitch replies, not promises.
10. **Drafts: the drafting mark covers only owed emails** (low to medium). Post-meeting follow-ups and pitch replies saved to Gmail had no mark; on Home-only accounts a mark could hide an email for two days.
11. **Drafts: "Open in Gmail" opens the default Google account** (medium-low). No account hint in the compose link or the drafts fallback.
12. **A brief run by hand does not stop the scheduled one** (low). The by-hand run row recorded `["daily"]`, but `due` looks for `morning_brief`.
13. **Evals still test the Gmail path this account does not have** (medium). The mock offers a create-draft tool, packs say "(in Gmail drafts)", and the saved Claude runs predate the round-three skill edits.
14. **Smaller eval and doc gaps** (low). No QA check for Copy for partners; guard tests never use real schema keys; BUILD_LOG stale; Rohan's Home lacks the "draft ready" his pack shows.
15. **Copy and layout polish** (low). "Your CRM access was revoked since Thu 09:51" (and in the QA fixture that time is after the last check); Meera's hero finding packs four facts and a clipped quote; two pushes cut mid-phrase; analyst stale rows say the same thing twice.

## Top five fixes, ranked

1. **Close the guard and make TRUST.md exact**: a fixed event shape with no attendee field at any depth; Notion writes only to CRM record properties; ArtifactData pinned to the Home link; Write and Edit only in the work folder; Bash only for the engine and plain file commands; a scheduled run recognised from any user row. Then TRUST.md promises only what the guard enforces.
2. **Run the smoke checklist on the owner's account** and record the results, with probes for `attendeeEmails`, Notion Calendar and a foreign artifact link, and send probes aimed at the owner's own address.
3. **Fix the four push drops** with tests at each person's real run minute.
4. **Fix drafts**: one email per person across follow-ups and promises; mark every Gmail save and never Home-only drafts; the user's Google account in the compose link; setup tells each tester which draft path their Gmail takes.
5. **Make the evidence honest**: a mock Gmail with no create-draft tool, Claude-run evals re-run on the 0.3.0 skills, packs that show the real draft path, a test that the week-ahead line follows, BUILD_LOG up to date.

## Go or no-go

**No-go for five friendly VCs on this build.** The core is close; the guard gaps and the unrun smoke test stand in the way.

1. Guard allowlist with zero outbound tools in a real scheduled session: **not met** (two invite paths, fail-open detection, real-session probe not run).
2. Seven-meeting day, every external meeting one heads-up, board-eve sent: **partly met** (repo test passes; two drop cases remain; real busy day not run).
3. Create-draft tool confirmed per tester, or README, setup and Home say so: **partly met** (setup does not tell the tester).
4. Three days of dogfood: **needs the real-account smoke test**.
5. Stall banner and Platform link fixed, screenshots and packs from a committed build: **met**.
6. One-screen trust note, tested once: **partly met** (guard claims overstated; "turn off Instinct" untested on a real account).

New conditions: 7. guard coverage closed and re-probed on the real schemas; 8. the four push drops fixed and pinned by tests at real run minutes; 9. Claude-run evals re-run on the 0.3.0 skills against a mock Gmail with no create-draft tool.
