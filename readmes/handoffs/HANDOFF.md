# HANDOFF: budgeted world, current state and next work

**Start here for a new chat.** Read `../README_general_direction.md` §16–§22, `../README_submission.md`
(the submission set + band method), and `../commit_schemes/08_ordering_and_roadmap.md` (the scheme
roadmap). This doc is the current-state brief; it supersedes `global_budget_next.md`.

## Current submission set (decided on #band_supports)

Verdict rule: **#band_supports ≥ 3 = SUBMIT-viable, ≤ 2 = REJECT**; a ceiling-saturated band uses the
gap test instead. Full table + one durable record per row in `../README_submission.md` →
`../tasks/<task>.md`.

- **SHIP: budgeted-covtype (#band_supports 8.06)** and **budgeted-tep (9.14, anonymized TEP, accepted).**
- **BURIED (≤ 2 or ceiling):** unsw 1.49, thyroid 2.57, diabetes 1.32, derma 1.21 (4-row test class),
  hydraulic ceiling (gap p_le0 0.39).
- **label-budget-covtype: band resolves (6.82) but ELIMINATED on STRATEGY HOMOGENEITY** (all 5 students
  wrote one acquisition recipe), not on the band. Salvage in a separate chat (see below).

## Band methodology (THE metric, and the fix that just landed)

- The decision metric is **#band_supports** = how many resolvable tiers the band holds BETWEEN its
  lowest and highest run = `1 + spread/LSD`, `LSD = z·√2·σ` (z=2), σ = test-set resampling std of
  balanced accuracy, **capped by the rarest test class**. HIGH #band_supports = a WIDE band (endpoints
  far apart); it is NEVER "converged". **#observed** (`rank_resolution.n_levels`) = where the runs
  landed, kept only as contrast. A high #band_supports with low #observed = wide band, clustered
  occupancy, not convergence.
- Computed by **`../../scratch/analysis/band_resolution.py`** from each run's stored `predictions_b64`
  (decode → reconstruct the graded test labels via `DataView` → `block_bootstrap_sigma` stratified by
  class → `resolution` / `rank_resolution` / `paired_gap_sigma`). **No policy replay, no hosted probe**
  (this supersedes the old "Phase 6 hosted probe / recover_analyze.py" plan). Writes
  `scratch/analysis/<eval8>/band_supports.json`, the source of truth each row record transcribes.
- This corrected the entire submission table: the old `levels` column reported #observed as if it were
  capacity. Never report mean/std; report spread + #band_supports.

## Architecture (post-refactor, reuse, do not rebuild)

The mediated-grading framework is now SHARED in the `sdk` submodule under **`sdk/mediated/`** (imported
by every world; nothing shared world-to-world). A concrete world keeps only its scheme surface.

- **`sdk/mediated/`**: `data_view.py` (DataView: `drop_features` / `cost_overrides` / `test_per_class` /
  `pool_per_class`), `setup_data.py`, `prehook.py`, `harness.py` (sandbox spawn + JSON transport +
  scoring + `predictions_b64`), `verify_suite.py` (the pytest entry every task's `verify_file()` points
  to), `world_base.py` (`MediatedWorld` base), `prompt_builder.py`, `config_world.py`, `active.py`,
  `paths.py`, `objective.py`, `Dockerfile` (one shared template; tokens `{{TASK_NAME}}` + `{{WORLD_SLUG}}`).
- **A world = `worlds/<slug>/`**: `world.py` (DECLARATIVE only: `policy_methods`, `projection_spec`,
  `meta_extras`, `prompt_template`; kept light, no numpy, so the orchestration Python that imports
  `tasks_def` needs no ML deps), `drive.py` (the grade-time drive loop, numpy/sklearn, imported only by
  `verify_suite` under the grader venv), `policy_runner.py` (STANDALONE sandbox subprocess, cannot import
  `/root/src`), `data/<npz>`.
  - `worlds/budgeted/` = feature acquisition (`select_next`/`predict`, per-row budget).
  - `worlds/label_budget/` = active learning (`select_queries`/`predict`, buy training labels).
- **Register a task**: `tasks_def/configs/<name>.py` (CONFIG) + `tasks_def/<name>.py` (construct the
  world) + import in `tasks_def/__init__.py` + boilerplate dir `tasks/<name>/` + `sdk create`.
- **`HorTask.materialize`** gained a generic `dockerfile_substitutions()` hook.
- Both venvs (model + grader) now carry the full package set (torch pinned CPU) in every task's
  `src/venvs/{pyproject.toml,uv.lock}`.

**CAVEAT (uncommitted):** the `sdk/mediated` refactor (sdk submodule) + `worlds/budgeted` slimming +
`worlds/label_budget` are tested (budgeted-covtype regression 4/4 tests, balanced accuracy reproduced;
label-budget validated) but NOT yet committed. Commit the submodule first, then the parent, before
building on it. A parallel chat is editing `tasks_def/configs/label_budget_covtype*.py` (the salvage).

## Schemes tried (roadmap `08_ordering_and_roadmap.md`)

- **Per-row feature budget** (`worlds/budgeted`, the 8 `budgeted-*` tasks): memoryless / dominated, only
  covtype (heterogeneous + resolvable) bands. tep bands but is a scaffold-grade benchmark (accepted).
- **Label budget** (`worlds/label_budget`, roadmap item 2): built + run. Band resolves (6.82) but every
  student converges on one recipe (standardize → KMeans seed → balanced tree + uncertainty + rare-class
  boost + diversity → ensemble) → eliminated on strategy. **Salvage in a separate chat:** `pool_per_class`
  to sharpen rare-class starvation + remove the recipe-telegraphing hints so strategy must be discovered.
- **Plain global / incremental feature budget** (§21 proposed, **§22 REFUTED**): a shared feature-budget
  pool across rows **self-averages** to a per-row shadow-price rule calibratable from peek data, so it
  **collapses** (all competent agents converge again). It does NOT create a new scheme. **Do not build
  plain global budget as a standalone.** This refutation is WHY the `commit_schemes/` effort exists.

## THE DIRECTION: commit-mode tasks (§22), NOT plain global budget

§21 proposed a global/incremental budget; **§22 corrected it**: a plain shared pool over an iid stream
self-averages into a per-row shadow-price rule (calibratable from peek), so path dependence washes out
and it collapses. The real program is **commit-mode tasks**, STATE the policy interacts with whose
take-backs are costly (§22, §22a). "Global budget" only survives WRAPPED in a commit mechanism (a global
LABEL budget = the label-budget scheme; a shared pool funding paid revision). The full per-scheme
analyses live in **`../commit_schemes/`**; **`../commit_schemes/08_ordering_and_roadmap.md`** orders them
and is the real roadmap to follow.

Status against roadmap 08's ordering (do NOT re-derive; read 08):
1. **Transcript-replay pre-test** (item 1) — not run.
2. **Label-budget** (item 2) — BUILT + run (`worlds/label_budget`). Band resolves (6.82) but eliminated on
   STRATEGY HOMOGENEITY; SALVAGE in progress in another chat (`pool_per_class` + hints removed).
3. **Small-chunk information release** (item 3) — not built; highest cross-cutting value (it measures the
   noise floor / Delta-star the whole battery leans on).
4. **Paid-revision** (item 6) — contingent on label-budget passing its dominance gate.
5. **Instrument-installation** (item 4) — fix-first (inert as specified; needs a repair).
6. **TEP compounding** (item 5) — heaviest, scaffold-only.

**Next actionable:** the label-budget salvage (other chat), or start **small-chunk (item 3)** per the
roadmap. Begin any of them from `../commit_schemes/08_ordering_and_roadmap.md` (its Background section is
a self-contained bootstrap brief).

## Conventions (from `../../CLAUDE.md`, do not violate)

- Report **spread + #band_supports** (mean/std are irrelevant; #observed is contrast only).
- **No heavy local compute** (training, sweeps, replay, big dataset builds/loads) without explicit
  approval; default HOSTED (throwaway task validation). The noise analysis from stored `predictions_b64`
  is light and already approved. Listeners/pollers always OK.
- **Gate every student eval run through the user**; default `--runs 5`, model `biggie-max-polara`, agent
  `meteor`, machine `e2-custom-16-32768`; always surface the eval + task links.
- **600s platform grade cap is the ONLY timeout** (no shorter grader watchdog). Single-file deliverable.

## Reference (task_id · primary eval)

- budgeted-covtype `4de1e511-7738-4889-bed3-a0a532b051e5` · `babd012a-4ae2-4349-99cb-a030db3f4491` (SHIP)
- budgeted-tep `36abdac8-4edd-4304-a48c-53933cd34f62` · `4d68f219-12f4-4f79-b61c-ee118052f610` (SHIP)
- label-budget-covtype `33da8224-530b-4641-a61a-7f1a1655b823` · `03bdb135-2c06-4dd3-bd13-b3c813daee88` (parked)
- unsw `f8cc010b-…` · `27615e12-…`; thyroid `c69cfa04-…` · `6fcbf032-…`/`32c9a8ca-…`; hydraulic
  `2935f9b4-…` · `f7318a3b-…`; diabetes `bb7097fc-…` · `9f3883e9-…`; derma `1a019b65-…` · `0dd9f969-…`
  (all buried; eval links in `../README_submission.md`)
- mini_batch_id `0067d7a3-4134-40d9-a4eb-c29faeeb24fe`
