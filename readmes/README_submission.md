# Budgeted-acquisition tasks: submission set

One row per built task with its student score **band**. The product is the band, never the mean (see
`../CLAUDE.md`). Two numbers describe a band, and the second is the one that decides:

- **spread** = band width (max − min of the non-degenerate runs).
- **#band_supports** = how many statistically-distinguishable tiers the band CAN hold =
  `1 + spread / LSD`, with `LSD = z·√2·σ` (z=2) and σ the test-set resampling std of balanced accuracy,
  capped by the RAREST test class. It is the number of resolvable levels BETWEEN the lowest and highest
  run (the endpoint distance in LSD units). **The submit decision uses #band_supports only.**

The `#obs / #supports` column shows **#observed / #band_supports**. #observed (`rank_resolution`) is
where the runs LANDED (contrast only); #band_supports (`resolution`) is the capacity that decides. A
HIGH #band_supports with LOW #observed is a WIDE band with clustered occupancy (empty middle tiers), it
is NOT convergence; a LOW #band_supports IS a narrow / converged band.

**Decision rule:** `#band_supports ≥ 3` = SUBMIT-viable; `≤ 2` = REJECT (band inside noise). A band
saturated at the ceiling (best ≈ 1.0) invalidates the capacity formula, there the **gap test**
`P(gap≤0)` decides (near 0 = endpoints genuinely distinct, high = indistinct).

Every number is produced by [`../scratch/analysis/band_resolution.py`](../scratch/analysis/band_resolution.py)
(it decodes each run's `predictions_b64`, reconstructs the graded test labels via `DataView`, and
resamples the test set, no policy replay). Each row links to its full record under
[`readmes/tasks/`](tasks/).

## Master table

Per-row **budget** in parentheses (the difficulty lever; a per-case acquisition budget, except
label-budget where it is a total label budget L). Partial rows note runs that failed with no working
policy (score 0, excluded from the band as a bonus floor).

| task (budget) | metric | band | spread | #obs / #supports | verdict (from #band_supports) | submit | links |
|---|---|---|---|---|---|---|---|
| budgeted-covtype (6) | balanced-acc | 0.675–0.848 | **0.172** | 3 / **8.06** | WIDE band, endpoints ~7 LSD apart; the test resolves it despite the rarest class holding 266 rows | **YES** | [task](https://horizon.bespokelabs.ai/tasks/4de1e511-7738-4889-bed3-a0a532b051e5) · [eval](https://horizon.bespokelabs.ai/evaluations/babd012a-4ae2-4349-99cb-a030db3f4491) · [record](tasks/budgeted-covtype.md) |
| budgeted-tep (15) | balanced-acc | 0.652–0.824 (+2 fail) | 0.172 | 3 / **9.14** | WIDE band, endpoints ~8 LSD apart (synthetic + anonymized Tennessee Eastman Process, 22 faults; accepted for tasks) | **YES** | [task](https://horizon.bespokelabs.ai/tasks/36abdac8-4edd-4304-a48c-53933cd34f62) · [eval](https://horizon.bespokelabs.ai/evaluations/4d68f219-12f4-4f79-b61c-ee118052f610) · [record](tasks/budgeted-tep.md) |
| budgeted-unsw (2) | balanced-acc | 0.722–0.733 | 0.010 | 2 / 1.49 | NARROW band, endpoints < 1 LSD apart (inside noise) | NO | [task](https://horizon.bespokelabs.ai/tasks/f8cc010b-53f1-4745-9481-146ff721bb50) · [eval](https://horizon.bespokelabs.ai/evaluations/27615e12-de7e-4b29-8ef7-900fe5870d0e) · [record](tasks/budgeted-unsw.md) |
| budgeted-thyroid (3) | balanced-acc | 0.747–0.845 | 0.098 | 3 / 2.57 | below the 3-tier bar (73-row rarest class inflates σ); drop-TSH salvage TIGHTER (1.48), it failed | NO | [task](https://horizon.bespokelabs.ai/tasks/c69cfa04-5416-486c-b25a-0b345eea4d98) · [orig](https://horizon.bespokelabs.ai/evaluations/6fcbf032-d5ef-4b13-9040-1fbc44a7a1ca) · [drop-TSH](https://horizon.bespokelabs.ai/evaluations/32c9a8ca-6045-4629-a27c-a01e13f656b7) · [record](tasks/budgeted-thyroid.md) |
| budgeted-hydraulic (3) | balanced-acc | 0.991–0.994 | 0.003 | 1 / ceiling | CEILING: gap test P(gap≤0)=0.39, endpoints indistinct; one cheap sensor solves it so the budget never binds | NO | [task](https://horizon.bespokelabs.ai/tasks/2935f9b4-ea7f-4127-8b73-b91a7d4d6f24) · [eval](https://horizon.bespokelabs.ai/evaluations/f7318a3b-91ea-4456-a086-4d43bd449468) · [record](tasks/budgeted-hydraulic.md) |
| budgeted-diabetes (3) | balanced-acc | 0.614–0.620 (+1 fail) | 0.006 | 1 / 1.32 | NARROW band; readmission learnable from the cheap groups, expensive labs inert, converge ~0.62 | NO | [task](https://horizon.bespokelabs.ai/tasks/bb7097fc-2984-4b74-8088-e200de4373f3) · [eval](https://horizon.bespokelabs.ai/evaluations/9f3883e9-5b3a-4e42-94a7-f170450101dd) · [record](tasks/budgeted-diabetes.md) |
| budgeted-derma (6) | balanced-acc | 0.931–0.946 | 0.015 | 1 / 1.21 | real spread, but the rarest test class = **4 rows** (recall SE ≈ 0.18) buries it; unresolvable at ANY run count | NO | [task](https://horizon.bespokelabs.ai/tasks/1a019b65-bfed-4779-8e00-e3982d3c7a51) · [eval](https://horizon.bespokelabs.ai/evaluations/0dd9f969-ebd5-44ef-b891-aeeccfcd6502) · [record](tasks/budgeted-derma.md) |
| label-budget-covtype (L=2000) | balanced-acc | 0.550–0.636 | 0.086 | 2 / **6.82** | band VIABLE (wide, endpoints ~6 LSD apart), but ELIMINATED on **strategy homogeneity** (all 5 students wrote one recipe), not on the band | NO (strategy) | [task](https://horizon.bespokelabs.ai/tasks/33da8224-530b-4641-a61a-7f1a1655b823) · [eval](https://horizon.bespokelabs.ai/evaluations/03bdb135-2c06-4dd3-bd13-b3c813daee88) · [record](tasks/label-budget-covtype.md) |

**Reading the verdicts.** Two tasks clear `#band_supports ≥ 3` and ship: covtype (8.06) and tep (9.14,
synthetic + anonymized TEP, accepted for tasks). The rest are REJECT, and the corrected #band_supports shows WHY each is
narrow: unsw / diabetes have endpoints inside a single LSD; thyroid (2.57) sits just under the bar and
its drop-TSH salvage tightened rather than widened it; hydraulic saturates at the ceiling; derma has
real structure but a 4-instance test class makes it unresolvable at any N (the reason covtype, with a
populous rarest class, is the keeper). label-budget-covtype is the exception: its band IS resolvable
(6.82), but it is eliminated for a different reason, every student converged on the same acquisition
recipe, so there is no strategy diversity to grade.

## Correction note (this supersedes the old `levels` column)

The prior table reported `levels` = `rank_resolution.n_levels`, which is **#observed** (where the runs
happened to land), and used it as if it were the resolution capacity. That is the wrong metric for the
decision. The capacity is **#band_supports** (Method B, `../sdk/hor_utils/resolution.py`), the number of
tiers the band can hold between its endpoints. Every row above is now decided on #band_supports;
#observed is kept only as contrast. See each row's record for the full per-dataset noise methodology
(which class caps σ, the σ_abs → LSD → #band_supports arithmetic, and the ceiling handling).

## Salvage sweep: real students on the offline-eliminated datasets

The offline acquisition-spread gate (`README_general_direction.md` §16–§19) rejected 5 datasets, but
that gate only tested *acquisition* spread (adaptive vs fixed with a shared predictor); it never
measured whether real LLM students spread. So we built each as a task and ran 5 real student evals to
**bury or salvage empirically**. Per dataset the **budget** was the tightest value where acquisition
could still matter (below the cheapest fixed panel that already wins): UNSW 2, Hydraulic 3, Thyroid 3,
Diabetes 3, Derma 6, CoverType 6.

**Result: the gate held, and covtype salvaged.** All five offline-gate rejects returned bands whose
#band_supports is ≤ 2 (or ceiling-indistinct), buried, and the reason is dataset-specific but the same
shape (no per-case decision to get right, so everyone converges). The one dataset with genuine
heterogeneous relevance AND the resolution to measure it, **covtype**, produced #band_supports 8.06. So
the empirical sweep confirms the design bible: a band needs both heterogeneity (§17) and resolution
(§18), and no cost/budget knob manufactures either where the data lacks it (thyroid's drop-TSH salvage
is the proof).

**Caveat (`README_general_direction.md` §21).** Even covtype's band comes from a **per-row / memoryless**
budget, the acquisition optimization is identical every case, a near-dominated space. The label-budget
scheme was the attempt at a non-dominated space; its band resolved (6.82) but the students converged on
one strategy, so it too is eliminated (salvage in progress: sharpen rare-class starvation via
`pool_per_class`, remove the recipe-telegraphing hints).

## Methodology (how a band is judged, and where the numbers come from)

Viability is the SDK's noise-floor method (`../sdk/methodology/noise_floor.md` §11–14;
`../sdk/hor_utils/{noise,resolution}.py`). The grader is deterministic, so the only noise is
**test-set resampling**. For each eval, [`band_resolution.py`](../scratch/analysis/band_resolution.py):

1. decodes every run's per-row test predictions from the stored `predictions_b64` (no policy replay,
   no XGBoost, unlike the older `recover_analyze.py`);
2. reconstructs the graded test labels exactly (`DataView(cfg).apply` on the committed npz, aligned to
   the predictions; only covtype's `test_per_class` subsamples);
3. measures **σ_abs** = `block_bootstrap_sigma` (stratified by class) on the median run, then
   **#band_supports** = `resolution(scores, sigma_rel=σ_abs/mid)`, **#observed** = `rank_resolution`,
   and the ceiling-safe **gap test** = `paired_gap_sigma` (best vs worst).

It writes `scratch/analysis/<eval8>/band_supports.json` per eval (the source of truth each row record
transcribes), so the numbers are reproducible and never hand-recomputed.

## Notes
- Reference: oracle (masking-XGBoost + greedy eddi) validates at balanced accuracy **0.741**; noop ~0.045.
- **budgeted-tep** is synthetic + anonymized TEP (22 faults); it submits on its own band and also proves
  the mediated-acquisition pipeline end to end. covtype remains the real-data flagship
  (`README_general_direction.md` §17 / §19 / §20).
- Batch: `0067d7a3-4134-40d9-a4eb-c29faeeb24fe`.
