# Instinct for VCs: product council, round four

Written by the Claude agent that played the council (saved here by the lead session, which received it as text). **Simulated council:** one Claude agent played a product manager, a UI/UX designer, an AI engineer and a QA lead. No real person took part. Reviewed 23 Oct 2026 against commit 0c68ca6 (version 0.4.0). The repo was not changed; all runs used a scratch copy.

## Scores

| Reviewer | Round three | Round four | In one line |
|---|---|---|---|
| PM | 7 | 7 | Most eval findings are fixed. But the real-account test still has not been run, a Sheet CRM can never apply an approval, and partners get pitch replies mid-day. |
| Designer | 8 | 7 | Contrast, targets and QA hold. The analyst's Today regressed: 18 rows, 8 marked Urgent, 7 on deals a colleague leads. |
| AI engineer | 6 | 6 | Every round-three guard gap is closed on the real schemas. But three allowed steps run any code, two connector calls still write out, and the guard fails open without a transcript. |
| QA lead | 6 | 7 | Evidence reproduces and the mock is honest now. But the smoke checklist is blank and stale, BUILD_LOG is stale, and no Claude run used the 0.4.0 skills. |

**Average: 6.75** (round three: 6.75).

## Verified fixed since round three

- **Round-three guard gaps.** The guard suite (283/283) denies these on real argument names: `attendees`, `attendeeEmails`, Notion Calendar attendees and rooms, out-of-office events, other Google calendars, Notion data-source and template writes, another page's ArtifactData, and writes to the plugin or engine copy. A meta row before the prompt no longer turns the guard off.
- **Pushes.** The four round-three drops are fixed and pinned at each person's real run minute. A brief run by hand stops the scheduled one.
- **Drafts.** One email per person. A mark before every Gmail save, none for Home-only drafts. "Open in Gmail" carries `authuser`. Setup tells each tester where drafts go. The mock Gmail has no create-draft tool, and its reads print version lines.
- **Claude-run evals.** Five runs found 46 numbered issues. A sample re-checked: LP owners and called capital survive a pulse; a colleague's LP tap is refused once; "Set up a call with Kabir" needs Kabir on the meeting; each connector reads from its last good run; the CRM's pass log shape no longer crashes `triage`; `drafts_in_gmail` is gone; a Friday setup says "Mon 07:00".
- **Copy.** "revoked since" is now "revoked at". No push is cut mid-phrase.
- **Re-run here.** Runner 103/103. Home QA 343/343. Design lint 0 violations in 213 rules. `claude plugin validate .` passes, still warning that there is no LICENSE and no privacy URL.

## Bugs and risks reproduced

1. **Guard escape: three allowed steps run any code (high).** Write a file holding one line of Python in the work folder, `sort -o<user site-packages>/usercustomize.py` it, then run the engine as usual: all three pass and the engine runs the planted file. Cause: the shell check skips paths joined to a flag (`sort -o/path`, `mv --target-directory=/path`).
2. **Writing to another app passes (medium to high).** `mcp__Claude_Docs__batch` creates or edits a doc, because "batch" is on the guard's read-word list. Any tool named only with read words passes (`resolve_issue`).
3. **Network calls from the database (medium).** On `execute_sql`, `SELECT net.http_post(...)`, `SELECT dblink_connect(...)` and `SELECT delete_deal(5)` pass.
4. **Fails open without a transcript (high if it happens, unverified).** With `transcript_path` empty or missing, `send_message` is allowed.
5. **Files outside the documented work folder (medium).** Write and Edit pass anywhere in the session folder (`.claude/settings.json`, `CLAUDE.md`, `.mcp.json`, `.bashrc` when the session runs in the home folder). Read and Grep pass anywhere outside a short secrets list. `date -f<credentials file>` passes.
6. **Holds beyond "your own primary calendar" (low to medium).** Notion Calendar accepts another calendar id and daily recurrence.
7. **CRM writes are not limited by record or field (medium to low, half disclosed).** A field change can fire the CRM's own email or Slack automations.
8. **A Sheet CRM never applies an approval (medium).** README offers a Google Sheet as a CRM, but the guard blocks Sheets and Drive writes, so every Approve ends "Not done".
9. **Pulse pitch replies ignore the level (medium to low).** Pulse step 4 drafts a reply to every pitch on non-morning runs; the engine and the morning brief reply only for levels that triage.
10. **Analyst Today regressed (medium to low).** 18 rows, 8 Urgent, 7 led by a colleague, from shared CRM notes; the evals5 test checks only the hero and the push.
11. **Evidence gaps (low to medium).** The smoke checklist has no probes for `attendeeEmails`, Notion Calendar or another page, and its "30 to 90 minutes" line fails a correct heads-up sent 96 minutes ahead. BUILD_LOG is stale. The five Claude runs used the 0.3.0 skill text. The mock ignores version pins on `db set` and `db update`, and `crm update` changes nothing.
12. **Smaller (low).** The paying-customer fix drops the signal for "40 paying customers and 1,200 users". Triage reads the company site and connectors.md falls back to web search, both blocked in scheduled runs. Setup still says the guard lets runs "apply what you approved". The LPs hero says "Every LP you own is in touch" above a $150K overdue capital call.

## Top five fixes, ranked

1. **Close the escape and the new paths**: `python3 -I -S` for the engine; check every path in a command, including after `-o`, `-f` and `--x=`; keep Write, Edit, redirects, Read and Grep inside the work folder and the plugin; treat `batch` and `resolve` as writes or list read tools per known server; block `execute_sql` in scheduled runs; keep Notion holds on the default calendar with no recurrence; pin each with a guard test.
2. **Make a dead guard visible**: the pulse's first step makes one harmless call the guard must block. If that call runs, stop, write "guard off" to the run row and push it.
3. **Run the smoke checklist on the owner's account** with these probes and the canary call. Fix the heads-up line, then three days of dogfood.
4. **Fix the product gaps**: Sheet CRM (a scoped write, or Copy instead of Approve, said at setup); pulse pitch replies only for levels that triage; colleagues' races off the analyst's Today.
5. **Make the words exact and the evidence current**: TRUST.md, README, safety.md and setup say exactly what the guard allows, CRM automations included; update BUILD_LOG; re-run setup and pulse as Claude evals on the final skills.

## Go or no-go

**No-go for five friendly VCs on 0.4.0.** The product is close, but the guard is not yet a real floor.

1. Zero outbound tools in a real scheduled session: **not met** (escape chain, Docs batch, SQL; no real-session probe).
2. Seven-meeting day, one heads-up each, board-eve line sent: **partly met** (tests pass at real run minutes; no real busy day run).
3. Create-draft tool confirmed per tester, or README, setup and Home say so: **met**.
4. Three days of dogfood: **not met**.
5. Stall banner, Platform link, screenshots and packs from a committed build: **met**.
6. One-screen trust note, tested once: **partly met** (it overstates the guard's scope; "turn off Instinct" untested).
7. Guard coverage closed and re-probed on real schemas: **partly met** (round-three paths closed; new ones open).
8. Push drops fixed and pinned at real run minutes: **met**.
9. Claude-run evals against a Gmail with no create-draft tool: **met** for five skills; the 0.4.0 edits are pinned only by engine tests.

New conditions: 10. the escape chain and paths 2 to 7 closed and pinned by tests, with the canary call in every scheduled run; 11. Sheet-CRM approvals work, or are not offered; 12. pulse replies follow the level, and the analyst's Today leads with their own work; 13. setup and pulse re-run by Claude on the final skill text.
