# ARCHIVED — consolidated into noam_worlds

This repo has been merged into the multi-world monorepo **noam_worlds**
(`git@github.com:PolaraProject/noam_worlds.git`) as of 2026-07-09.

- World(s) moved: **budgeted, label_budget, drift** (now under `worlds/<world>/` in noam_worlds).
- Do ALL new work in noam_worlds. Do NOT push tasks from here.
- This repo is kept FROZEN as a reversibility backup: the gitignored `.horizon-local/task_ids.json`,
  `.rollouts/`, full git history, and the original band records live here.
- Platform task ids are unchanged; noam_worlds re-homes each task to its existing id on push (push-on-demand).
