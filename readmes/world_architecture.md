# Handoff: world architecture (how to build a task)

The mediated-grading framework is SHARED in the `sdk` submodule under **`sdk/mediated/`** (imported by
every world; nothing shared world-to-world). A concrete world keeps only its scheme surface. Reuse this,
do not rebuild it.

## The shared framework, `sdk/mediated/`

- `data_view.py` (DataView: `drop_features` / `cost_overrides` / `test_per_class` / `pool_per_class`,
  config-driven HOSTED transforms at setup time, a reshape is a config edit + re-push, never a rebuild).
- `setup_data.py`, `prehook.py` (build-time data vendoring + student-view projection).
- `harness.py` (sandbox spawn as the `model` user + line-JSON transport + scoring + `predictions_b64`).
- `verify_suite.py` (the pytest entry every task's `verify_file()` points to; imports the world's drive loop).
- `world_base.py` (`MediatedWorld` base: grade orchestration, artifact gate, paths, Dockerfile hooks).
- `prompt_builder.py`, `config_world.py`, `active.py`, `paths.py`, `objective.py`.
- `Dockerfile` (ONE shared template; tokens `{{TASK_NAME}}` + `{{WORLD_SLUG}}`).

## A concrete world, `worlds/<slug>/`

- `world.py` DECLARATIVE only: `policy_methods`, `projection_spec`, `meta_extras`, `prompt_template`.
  Kept LIGHT (no numpy) so the orchestration Python that imports `tasks_def` needs no ML deps.
- `drive.py` the grade-time drive loop (numpy/sklearn), imported ONLY by `verify_suite` under the grader
  venv. This is the ONE file that encodes the scheme's protocol.
- `policy_runner.py` STANDALONE sandbox subprocess (it runs as `model`, cannot import `/root/src`, so it
  duplicates the ~10 lines of stdlib transport by necessity).
- `data/<npz>` the committed dataset.

Existing worlds: `worlds/budgeted/` (feature acquisition, `select_next`/`predict`, per-row budget);
`worlds/label_budget/` (active learning, `select_queries`/`predict`, buy training labels).

## Add a task

`tasks_def/configs/<name>.py` (CONFIG: n_classes, budget, npz_name, view, hints) +
`tasks_def/<name>.py` (construct the world) + import in `tasks_def/__init__.py` + boilerplate dir
`tasks/<name>/` (task.yaml placeholder, 2-line grader.py, setup.sh -> `sdk.mediated.prehook`, solution.sh
baseline oracle, src/venvs, tests) + `sdk create`. Both venvs (model + grader) carry the full package set
with torch pinned CPU. `HorTask.materialize` has a generic `dockerfile_substitutions()` hook.

## Status: committed and stable

The shared `sdk/mediated` framework + the thin `worlds/budgeted` + `worlds/label_budget` are COMMITTED and
behavior-preserving (budgeted-covtype regression 4/4 tests, balanced accuracy reproduced; label-budget
built + salvaged). `sdk` is a git SUBMODULE: changes there are committed INSIDE the submodule, then the
pointer is bumped in the parent (as the `refactor(budgeted)` and sdk band-report commits already did).
Build new worlds on top of this.

## Conventions (from `../CLAUDE.md`, do not violate)

- Report **spread + #band_supports** (see `band_method.md`); mean/std are irrelevant.
- **No heavy local compute** (training, sweeps, replay, big dataset builds/loads) without explicit
  approval; default HOSTED (throwaway task validation). Listeners/pollers always OK.
- **Gate every student eval run through the user**; default `--runs 5`, model `biggie-max-polara`, agent
  `meteor`, machine `e2-custom-16-32768`; surface the eval + task links.
- **600s platform grade cap is the ONLY timeout** (no shorter grader watchdog). Single-file deliverable.
- Build/validation logs: read `tasks/<task>/.validation/<build_id>/output.txt`, never the terminal summary.
