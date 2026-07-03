# Handoff: global/incremental budget (the next work) + current world state

**For a NEW chat.** This is the continuation brief for the `budgeted` world after the salvage sweep.
Read `../README_general_direction.md` §16–§21 and `../README_submission.md` first, then this.

## Where we are (state)

A working budgeted feature-acquisition world (`worlds/budgeted/`) with 8 deployed tasks. A student
ships a `Policy` class in `solution.py` (`__init__(data_dir)` / `select_next(observed, budget_left)`
/ `predict(observed)`); the **mediated grader** (`verify.py`) drives it per test row over a stdin/stdout
JSON pipe, enforcing a **per-row** budget, revealing only requested feature values, sandboxed as the
`model` user. Metric = balanced accuracy, `best_observed = 1`.

**Salvage sweep result (real student evals, 5 runs each):**
- **covtype (Forest CoverType) SALVAGED** — the one real, big, heterogeneous + resolvable dataset:
  band 0.675–0.848, spread 0.173, ~3 levels, top beats the 0.585 oracle. First non-scaffold task.
- **tep (scaffold)** reproduces its band under the single-file grader (fail·fail·0.65·0.80·0.82).
- **buried (packed, real students confirmed the offline gate):** unsw, thyroid, hydraulic, diabetes,
  derma. Thyroid drop-TSH salvage *tightened* the band (one-axis; no knob makes heterogeneity the data
  lacks). Full table + reasoning in `README_submission.md`.

## Key architecture already built (reuse, don't rebuild)

- **Mediated grader** — `worlds/budgeted/verify.py::run_mediated`. Per row: `send {"cmd":"row","budget":B}`
  (budget resets to B EACH ROW), loop `{"act":"buy","fid":j}` → reveal `{"val":x}` or refuse
  `{"val":null}`, until `{"act":"predict","label":k}`. Single-file contract enforced (`_enforce_single_file`
  deletes non-solution files). Emits per-run `predictions_b64`.
- **DataView** — `worlds/budgeted/data_view.py`. The one class that owns config-driven, HOSTED data
  transforms at `setup_data` time: `drop_features`, `cost_overrides`, `test_per_class` (balance/cap the
  test split). Any re-costing / feature-drop / test-resize is a **config edit + re-push, never a local
  rebuild**. Config key `view` in `tasks_def/configs/<task>.py`.
- **Per-task config** — `tasks_def/configs/budgeted_<ds>.py` (n_classes, budget, npz_name, hints, view);
  registered in `tasks_def/budgeted_<ds>.py` + `tasks_def/__init__.py`. Task dir `tasks/budgeted-<ds>/`
  is copied boilerplate (oracle `solution.sh` is dataset-generic).

## THE NEXT WORK: global / incremental budget (§21)

**Why.** The per-row budget is **memoryless** — every case gets a fresh B, so the acquisition
optimization is identical on every row and all competent agents converge to the one best per-row policy
(a **dominated** space → packing). Even covtype's band is modest for this reason. The dynamic that
creates real agent distinction is **early decisions constraining later ones**: give a policy a **shared
budget pool across all cases**, so spending now costs it later, forcing it to **ration** — spend on hard
cases, save on easy ones. There is no dominant rationing rule → a **non-dominated** space → different
allocation strategies separate scores. Expected to band far more robustly, and it is **data-light**
(any dataset with variable per-case difficulty supplies it, unlike per-row routing which needs scarce
heterogeneity).

**What to build.**
1. **Grader change (small):** `verify.py::run_mediated` already drives rows in sequence. Add a `budget_mode`
   (config): `"per_row"` (current) vs `"global"`. In global mode, initialize a running `pool = B_total`
   ONCE, do NOT reset per row; each buy depletes `pool`; a row ends when the policy predicts (it may buy
   0 features if it's rationing). Decide the row-order policy (fixed/shuffled — shuffle with a fixed seed
   so order isn't gameable; document it). Consider exposing remaining `pool` + `rows_left` to the policy
   per row (the protocol's `{"cmd":"row",...}` can carry them).
2. **Config:** `B_total` per task (e.g. `per_row_B * n_test`, then tighten). The budget is still THE
   lever — sweep/choose it so it genuinely binds across the stream.
3. **Prompt:** update `prompt_builder.py` to describe the shared-pool contract (still production framing,
   no grading language). The current template is per-case; global mode needs "a fixed total budget for
   the whole batch of cases; spend it where it matters most."
4. **Re-run covtype (and maybe tep) in global mode** and compare the band vs per-row. Success = wider
   spread / more levels than per-row.

**Watch:** the grader must not let global mode leak information across rows (e.g. the policy inferring
the test distribution from the pool). Keep row values revealed only on request, as now.

## Secondary / optional: rigorous n_levels (Phase 6)

`README_submission.md` reports **score-only** levels. The rigorous SDK metric (`rank_resolution` /
`paired_gap_sigma` in `sdk/hor_utils/noise.py`) needs each run's policy replayed on the fixed test set.
That replay is XGBoost-heavy → **MUST be hosted** (a throwaway task whose oracle re-runs recorded
policies and returns predictions, fusion's `recover_via_probe`), NEVER local. `scratch/analysis/
recover_analyze.py` does it locally and must NOT be used on this laptop. Only covtype + tep have real
spread worth the probe.

## Conventions (from CLAUDE.md — do not violate)

- **No heavy local compute** (training, sweeps, replay, dataset builds/loads > a few k rows). Requires
  explicit user approval; default HOSTED (throwaway task validation). Listeners/pollers are always OK.
- **Metric: LEVELS first** (`rank_resolution n_levels`), reported with spread. Mean is irrelevant.
- **Gate every eval run through the user**; default `--runs 5`. Model `biggie-max-polara`, agent
  `meteor`, machine `e2-custom-16-32768`. Always surface run + task links.
- **600s platform grade cap is the ONLY timeout** — never add a shorter grader watchdog.
- **Single-file deliverable**; grader deletes non-solution files.

## Reference (task_id · latest eval)

- budgeted-covtype `4de1e511-7738-4889-bed3-a0a532b051e5` · eval `babd012a-4ae2-4349-99cb-a030db3f4491` (SALVAGE)
- budgeted-tep `36abdac8-4edd-4304-a48c-53933cd34f62` · eval `4d68f219-...` (scaffold baseline)
- unsw `f8cc010b-...`, thyroid `c69cfa04-...`, hydraulic `2935f9b4-...`, diabetes `bb7097fc-...`,
  derma `1a019b65-...` (all buried; see `README_submission.md` for eval links)
- mini_batch_id `0067d7a3-4134-40d9-a4eb-c29faeeb24fe`
