---
name: network
description: Finds warm intro paths into any company or person from a venture firm's own relationships, and flags top relationships going cold with a reconnect draft. Use when the user asks "who can intro me to", "do we know anyone at", "warm path into", "who am I losing touch with", or when the Monday digest runs.
metadata:
  version: "0.11.0"
---

# Network

Two jobs: the best warm path into a company, and the people worth a note before the relationship goes cold.

Plugin root: `${CLAUDE_PLUGIN_ROOT}`. If that is not a real path, use the folder two levels above this skill's base directory. Follow `<plugin root>/shared/safety.md` throughout.

## Intro paths ("who can intro me to X")

1. Copy the engine. Gather 120 days of mail and calendar metadata (participants and dates only) and the CRM people with relationship strength. Write `bundle.json`.
2. Write the company name or domain into `company.txt` with the file tool, then run `python3 -I -S instinct-engine/instinct.py intro --bundle bundle.json --company-file company.txt`. Never put a name you read from email or a document on the command line.
3. Show up to three paths. For each: who to ask, how strong the tie is (0 to 100), when you last spoke, and the chain ("Ask Kabir (strength 90), who knows Pinki Das, Head of Lending"). Link the latest thread or meeting for each hop.
4. Offer a short intro request draft to the first hop. Save it to `snap/drafts` or as a Gmail draft (never send).
5. If there is no path, say so plainly and name the closest people at similar companies only if the graph has them.

## Monday digest

1. Gather 120 days of metadata. Run the engine `build` with `--mode digest`. It recomputes relationship strength and finds people in the top 50 with no touch in 60 days. Mailing lists, newsletters and no-reply senders never count as relationships: only people the user met or wrote to.
2. For each one going cold, write a one-line reason to reach out from what you know (a recent funding, a shared portfolio company, a promise still open) and a two-sentence reconnect draft. Save drafts to `snap/drafts`.
3. If the profile has portfolio or LP modules on, run `skills/portfolio-watch/SKILL.md` and `skills/lp-watch/SKILL.md` next.
4. Write a short digest (under 200 words: who is going cold and why, portfolio flags, LPs due a touch, each with a link) and pass it with `--digest digest.md --digest-kind digest`.
5. Write the snapshots. In a scheduled run, end with the engine's `report.push_line`, or exactly `Nothing new`.
