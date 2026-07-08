# Handoff: how a band is judged (#band_supports)

**The decision metric is #band_supports**, how many resolvable tiers the band holds BETWEEN its lowest
and highest run. Everything else (mean, std, #observed) is contrast at most.

## Definitions (do not conflate, this was a recurring error)

- **#band_supports** = `1 + spread / LSD`, `LSD = z·√2·σ` (z=2), σ = test-set resampling std of balanced
  accuracy, **capped by the rarest test class**. It is the endpoint distance in LSD units. HIGH
  #band_supports = the lowest and highest runs are FAR APART = a WIDE band; it is NEVER "converged".
- **#observed** = `rank_resolution.n_levels` = how many tiers the runs actually OCCUPY. A high
  #band_supports with low #observed = a wide band with clustered/top-heavy occupancy (empty middle
  tiers), NOT convergence. A LOW #band_supports (<=2) IS a narrow / converged band.
- The grader is deterministic, so the only noise is **test-set resampling**; near the ceiling (best ~1.0)
  Method B is invalid and the **gap test** `paired_gap_sigma.p_le0` decides.

**Decision rule:** `#band_supports >= 3` = SUBMIT-viable; `<= 2` = REJECT; ceiling -> gap test.

## The tooling (source of truth)

- **`../scratch/analysis/band_resolution.py`** computes the numbers from each run's stored
  `predictions_b64` (no policy replay, no hosted probe): decode preds -> reconstruct the graded test labels
  via `DataView` -> `block_bootstrap_sigma` (stratified by class) -> `resolution` (#band_supports) /
  `rank_resolution` (#observed) / `paired_gap_sigma` (gap) -> `scratch/analysis/<eval8>/band_supports.json`.
- **`--emit`** then RENDERS the per-row record and UPSERTS the master-table row via the SDK-owned
  **`sdk/hor_utils/band_report.py`** (it owns the record/row format + an invariant validator; the analyst
  authors only the verdict line + narrative in `band_resolution.py`'s `REPORT_META`). Records and the table
  are GENERATED, not hand-transcribed, do not edit them by hand, re-run with `--emit`.
- The end-to-end workflow is codified in the **`horizon-band-verdict`** skill
  (`sdk/plugins/hor/skills/horizon-band-verdict/`).
- SDK kernel: `sdk/hor_utils/{noise,resolution}.py`; method: `sdk/methodology/noise_floor.md` §11-14.

## Current submission set

| task | #obs / #band_supports | submit |
|---|---|---|
| budgeted-covtype | 3 / **8.06** | **YES** (real-data flagship) |
| budgeted-tep | 3 / **9.14** | **YES** (anonymized TEP, accepted) |
| budgeted-thyroid | 3 / 2.57 | NO (below bar; 73-row rarest class) |
| budgeted-unsw | 2 / 1.49 | NO (narrow) |
| budgeted-diabetes | 1 / 1.32 | NO (narrow) |
| budgeted-derma | 1 / 1.21 | NO (4-row test class -> unresolvable) |
| budgeted-hydraulic | 1 / ceiling | NO (gap p_le0 0.39) |
| label-budget-covtype | 2 / **6.82** | NO (band viable, eliminated on STRATEGY, not band) |
| label-budget-covtype-open | 4 / **7.82** | **YES** (salvage of the row above: real code-legible skill gradient) |

Full table + records live PER-WORLD under `worlds/<world>/readmes/README_submission.md` +
`worlds/<world>/readmes/tasks/<task>.md` (worlds: budgeted, label_budget). `band_resolution.py` routes
each task to its world's paths; `--validate` checks every world. **Three ship:** covtype, tep,
label-budget-covtype-open.

**The label-budget lesson (carry into every scheme):** a band can have HIGH #band_supports and still be a
bad task if the students converge on ONE strategy. Pair the band check with a strategy-diversity check
(what did the submitted solutions actually do). See `scheme_2_label_budget.md`.
