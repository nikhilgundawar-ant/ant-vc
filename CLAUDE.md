# Installing ant. for VCs (for Claude)

When a user shares this repository and asks to install or set it up:

1. Package the plugin from the repository root: `bash package.sh` (it zips everything except `.git`, `evals`, build notes and caches into `ant-vc.plugin`).
2. Copy `ant-vc.plugin` to `/tmp` and send it to the user with SendUserFile so the plugin card appears, and ask them to tap Accept.
3. When they accept, or say it is already installed, run the `setup` skill from this plugin.

If the app cannot show a plugin card, you may follow `skills/setup/SKILL.md` from this repository up to the first brief, but do not create the scheduled checks: their prompts call the plugin's `pulse` skill, which a fresh session only has when the plugin is installed. Say so, and offer to send the plugin card again. Read `shared/safety.md` before anything else: ant. never sends, deletes or changes anything without the user's tap.

For development:

- `python3 evals/runner.py` runs every engine check against the fictional golden fund, Quillwater Ventures, plus the multi-run suites in `evals/replay.py` (five days of runs, outages, quiet deals, forged approvals, push volume, eight weeks of tuning, a second fund and the scheduled-run guard).
- `python3 evals/design_lint.py` checks ant. Home against the Anthill Evergreen rules.
- `python3 evals/home_qa.py` clicks through ant. Home on phone and desktop with Playwright and saves screenshots to `evals/reports/home/`.
- `evals/eval-mode.md` explains how to run a skill end to end against mock connectors, so Claude's own reading is scored too.
- `python3 evals/demo.py` builds the demo Home data.
- `hooks/guard.py` is the PreToolUse guard for scheduled runs. Its marker, `[ant-vc-scheduled-run]`, is in both scheduled prompts in `schedules.json`; keep them in step.
- `claude plugin validate .` checks the manifest, skills and hooks.
- `evals/smoke-checklist.md` is the test only a real account can run: platform contracts, the guard inside a real scheduled run, drafts, a busy day and three days of dogfood. Run it before any tester installs ant.
