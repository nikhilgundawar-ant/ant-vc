---
name: settings
description: Changes, pauses or turns off ant. for VCs. Use when the user says "turn off ant.", "pause ant.", "resume ant.", "wipe my ant. data", "change my brief time", "I'm a principal now", "edit my thesis", "show the whole pipeline", "check ant.", "pin ant." or "ant. settings".
metadata:
  version: "0.8.0"
---

# ant. settings

Small changes, made at once, confirmed in one line. Only turning ant. off asks first.

Plugin root: `${CLAUDE_PLUGIN_ROOT}`. If that is not a real path, use the folder two levels above this skill's base directory. Follow `<plugin root>/shared/safety.md` throughout.

## Load

1. Copy the engine (`<plugin root>/shared/engine.md`).
2. Find the Home link from memory, a scheduled task's prompt, or the Artifact list ("ant. Home"). If there is none, say "ant. is not set up yet. Say 'set up ant.' to start." and stop.
3. Read `snap/config` into `./home-db` as `<plugin root>/shared/home.md` describes. If it is wrapped as `{"data": ..., "version": ...}`, use `data` and keep the version for the write.
4. Find this session's scheduling tools (search your tools for "scheduled task" or "trigger"). List the user's scheduled tasks and keep the two named exactly "ant." and "ant. weekend". Tasks with older ant. names (from version 0.1, such as "ant. morning brief" or "ant. pulse") are replaced: delete them and create the two current ones from `schedules`.

## Changes

Write the changed config back to `snap/config` with its version pinned, then say what changed in one line. Settings, setup and tuning are the only writers of `snap/config`.

| The user says | Change |
| --- | --- |
| Brief time (for example "brief at 6:30") | Set `brief_time`. Run `schedules --config config.json` and update both tasks' cron with the new entries: the hourly runs follow the brief time. |
| Level (for example "I'm a principal now") | Set `level` and `level_label`. Load that profile's `today_items`, `brief_words`, `weights`, `modules`, `pipeline_scope` and `opens_on` from `ontology/profiles.json`. The two tasks stay; each run reads the new level and does what it has. |
| Thesis | Take their words. Update `thesis` and set `confirmed: true`. |
| "Show the whole pipeline" or "only my deals" | Set `pipeline_scope` to `full` or `own`. |
| "Send my brief to Slack" | ant. does not post anywhere. Say Home's Copy brief button copies a plain version (quiet deals left out) to paste into Slack or anywhere else. |
| "Check ant." or "is ant. running?" | Read the newest `runs` rows. Say when the last run finished, what it did and any warning. If none finished in the last two working hours, check that both tasks exist, are on and approve automatically, and say which is not. |
| "Fewer items" or "more items" | Move `today_items` by 2 within the profile limits. |
| "Pin ant." | Pin the Home artifact with the Artifact tool. |

After a change that affects the brief, run a pulse build so Home reflects it now (as the `pulse` skill describes, steps 3 to 6).

## Pause and resume

- Pause: turn off every ant. scheduled task with the scheduling tool's update action. If the tool cannot pause a task, delete the tasks and save their names and schedules into `snap/config.paused_tasks`. Say "ant. is paused. Say 'resume ant.' to start again."
- Resume: turn the tasks back on, or recreate them from `paused_tasks` (or from `schedules` if that list is missing). Then run one pulse.

## Turn off and wipe

Ask once with AskUserQuestion: "Turn off ant. and wipe its data? This deletes your ant. scheduled tasks and everything in ant. Home. Your email, calendar, notes and CRM are not touched." Options: "Turn off and wipe", "Just pause", "Cancel".

On "Turn off and wipe":

1. Delete every ant. scheduled task.
2. List each Home collection (`snap`, `state`, `ratings`, `runs`) with ArtifactData and delete every document in batches.
3. Delete the ant. note from memory if one exists.
4. Ask whether to delete the ant. Home page too. Delete it with the Artifact tool only if they say yes.
5. Confirm in one line what was removed, and that nothing in their own tools changed.

Never touch the user's mail, calendar, notes, CRM or files in any of these steps.
