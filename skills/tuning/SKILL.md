---
name: tuning
description: Tunes ant. for one user every Sunday from their ratings, edits and Friday score, moving ranking weights, brief length and stale thresholds in the direction they point, and writes the weekly scorecard. Use when a scheduled task runs ant-vc tuning, or the user says "tune ant.", "show my ant. scorecard" or "why did you change my brief".
metadata:
  version: "0.10.0"
---

# Weekly tuning

Small, explained changes. The user always sees what changed and why, in one line at the top of Monday's brief. In the schedule, tuning runs inside the Sunday evening run, before the week ahead; the user can also ask for it.

Plugin root: `${CLAUDE_PLUGIN_ROOT}`. If that is not a real path, use the folder two levels above this skill's base directory. Follow `<plugin root>/shared/safety.md` throughout.

## 1. Load

Copy the engine and read Home into `./home-db`, including `ratings`.

## 2. Tune

```bash
python3 -I -S instinct-engine/instinct.py tune --config config.json --home ./home-db --out tuned
```

The engine reads only the ratings since the last tuning (`tuned_at` in the config), so each tap counts once. It raises a group's weight when the user rates it useful and lowers it when they rate it not useful or wrong, by at most 15% a week, within fixed limits, and never moves a weight against what the ratings say. It trims Today by one item when more than 30% of items were noise, adds one when less than 8% were, and slows stale-deal nudges when stale items were rated too early. With fewer than three new ratings for a group, nothing changes for it.

## 3. Scorecard

Write `snap/scorecard`:

```json
{"week": "2026-W43", "overall": <weekly_score from the tune output, or null>, "catches": <items marked "caught something">,
 "prep_on_time": "<prep cards delivered before meetings / external meetings>", "commitments_closed": "<closed on time / due>",
 "crm_clean": "<proposals applied without edits / applied>", "noise": "<not useful or wrong / rated>", "change_note": "<engine note>",
 "history": [<last 8 weeks>]}
```

## 4. Save and clean up

1. Merge `tuned/config-update.json` into `snap/config` with ArtifactData `update` and its `file_path`, as an absolute path inside the work folder (pin the version), then write the scorecard. Only the tuned fields change: the weights, items in Today, the stale-deal pace and `tuned_at`. In a scheduled run the guard refuses any other change to the settings, which belong to setup and the settings skill.
2. Delete ratings older than 60 days and `runs` rows beyond the newest 200 (ArtifactData delete).
3. Run by hand: end with the change note as the final line, or `No changes this week`. Inside the Sunday run: put the change note at the top of the week ahead and let the pulse end the run.
