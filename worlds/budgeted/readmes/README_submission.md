# Budgeted-acquisition (per-row feature budget): submission set

One row per built task with its student score **band**. The product is the band, never the mean (see
`../../../CLAUDE.md`). Two numbers describe a band, and the second decides:

- **spread** = band width (max − min of the non-degenerate runs).
- **#band_supports** = how many statistically-distinguishable tiers the band CAN hold =
  `1 + spread / LSD`, with `LSD = z·√2·σ` (z=2) and σ the test-set resampling std of balanced accuracy,
  capped by the RAREST test class. **The submit decision uses #band_supports only.**

The `#obs / #supports` column shows **#observed / #band_supports**. #observed (`rank_resolution`) is
where the runs LANDED (contrast only); #band_supports (`resolution`) is the capacity that decides.

**Decision rule:** `#band_supports ≥ 3` = SUBMIT-viable; `≤ 2` = REJECT (band inside noise). A band
saturated at the ceiling (best ≈ 1.0) invalidates the capacity formula, there the **gap test** `P(gap≤0)`
decides. Sibling world: label-budget active learning (`../../label_budget/readmes/README_submission.md`).

Every number is produced by [`../../../scratch/analysis/band_resolution.py`](../../../scratch/analysis/band_resolution.py)
(it decodes each run's `predictions_b64`, reconstructs the graded test labels via `DataView`, and
resamples the test set, no policy replay). Each row links to its full record under [`tasks/`](tasks/).

## Master table

Per-row **budget** in parentheses (the per-case acquisition budget). Partial rows note runs that failed
with no working policy (score 0, excluded from the band as a bonus floor).

| task (budget) | metric | band | spread | #obs / #supports | verdict (from #band_supports) | submit | links |
|---|---|---|---|---|---|---|---|
| budgeted-covtype (6) | balanced-acc | 0.675–0.848 | **0.172** | 3 / **8.06** | WIDE band, endpoints ~7 LSD apart; the test resolves it despite the rarest class holding 266 rows | **YES** | [task](https://horizon.bespokelabs.ai/tasks/4de1e511-7738-4889-bed3-a0a532b051e5) · [eval](https://horizon.bespokelabs.ai/evaluations/babd012a-4ae2-4349-99cb-a030db3f4491) · [record](tasks/budgeted-covtype.md) |
| budgeted-tep (15) | balanced-acc | 0.652–0.824 (+2 fail) | 0.172 | 3 / **9.14** | WIDE band, endpoints ~8 LSD apart (synthetic + anonymized Tennessee Eastman Process, 22 faults; accepted for tasks) | **YES** | [task](https://horizon.bespokelabs.ai/tasks/36abdac8-4edd-4304-a48c-53933cd34f62) · [eval](https://horizon.bespokelabs.ai/evaluations/4d68f219-12f4-4f79-b61c-ee118052f610) · [record](tasks/budgeted-tep.md) |
| budgeted-unsw (2) | balanced-acc | 0.722–0.733 | 0.010 | 2 / 1.49 | NARROW band, endpoints < 1 LSD apart (inside noise) | NO | [task](https://horizon.bespokelabs.ai/tasks/f8cc010b-53f1-4745-9481-146ff721bb50) · [eval](https://horizon.bespokelabs.ai/evaluations/27615e12-de7e-4b29-8ef7-900fe5870d0e) · [record](tasks/budgeted-unsw.md) |
| budgeted-thyroid (3) | balanced-acc | 0.747–0.845 | 0.098 | 3 / 2.57 | below the 3-tier bar (73-row rarest class inflates σ); drop-TSH salvage TIGHTER (1.48), it failed | NO | [task](https://horizon.bespokelabs.ai/tasks/c69cfa04-5416-486c-b25a-0b345eea4d98) · [orig](https://horizon.bespokelabs.ai/evaluations/6fcbf032-d5ef-4b13-9040-1fbc44a7a1ca) · [drop-TSH](https://horizon.bespokelabs.ai/evaluations/32c9a8ca-6045-4629-a27c-a01e13f656b7) · [record](tasks/budgeted-thyroid.md) |
| budgeted-hydraulic (3) | balanced-acc | 0.991–0.994 | 0.003 | 1 / ceiling | CEILING: gap test P(gap≤0)=0.39, endpoints indistinct; one cheap sensor solves it so the budget never binds | NO | [task](https://horizon.bespokelabs.ai/tasks/2935f9b4-ea7f-4127-8b73-b91a7d4d6f24) · [eval](https://horizon.bespokelabs.ai/evaluations/f7318a3b-91ea-4456-a086-4d43bd449468) · [record](tasks/budgeted-hydraulic.md) |
| budgeted-diabetes (3) | balanced-acc | 0.614–0.620 (+1 fail) | 0.006 | 1 / 1.32 | NARROW band; readmission learnable from the cheap groups, expensive labs inert, converge ~0.62 | NO | [task](https://horizon.bespokelabs.ai/tasks/bb7097fc-2984-4b74-8088-e200de4373f3) · [eval](https://horizon.bespokelabs.ai/evaluations/9f3883e9-5b3a-4e42-94a7-f170450101dd) · [record](tasks/budgeted-diabetes.md) |
| budgeted-derma (6) | balanced-acc | 0.931–0.946 | 0.015 | 1 / 1.21 | real spread, but the rarest test class = **4 rows** (recall SE ≈ 0.18) buries it; unresolvable at ANY run count | NO | [task](https://horizon.bespokelabs.ai/tasks/1a019b65-bfed-4779-8e00-e3982d3c7a51) · [eval](https://horizon.bespokelabs.ai/evaluations/0dd9f969-ebd5-44ef-b891-aeeccfcd6502) · [record](tasks/budgeted-derma.md) |

**Reading the verdicts.** Two tasks clear `#band_supports ≥ 3` and ship: covtype (8.06) and tep (9.14,
synthetic + anonymized TEP, accepted for tasks). The rest REJECT: unsw / diabetes have endpoints inside
a single LSD; thyroid (2.57) sits just under the bar and its drop-TSH salvage tightened rather than
widened it; hydraulic saturates at the ceiling; derma has real structure but a 4-instance test class
makes it unresolvable at any N (the reason covtype, with a populous rarest class, is the keeper).

## Salvage sweep: real students on the offline-eliminated datasets

The offline acquisition-spread gate (`../../../readmes/README_general_direction.md` §16–§19) rejected 5
datasets, but that gate only tested *acquisition* spread; it never measured whether real LLM students
spread. So we built each as a task and ran 5 real student evals to **bury or salvage empirically**. Per
dataset the **budget** was the tightest value where acquisition could still matter: UNSW 2, Hydraulic 3,
Thyroid 3, Diabetes 3, Derma 6, CoverType 6.

**Result: the gate held, and covtype salvaged.** All five offline-gate rejects returned bands whose
#band_supports is ≤ 2 (or ceiling-indistinct), buried, and the reason is dataset-specific but the same
shape (no per-case decision to get right, so everyone converges). The one dataset with genuine
heterogeneous relevance AND the resolution to measure it, **covtype**, produced #band_supports 8.06. The
empirical sweep confirms the design bible: a band needs both heterogeneity (§17) and resolution (§18),
and no cost/budget knob manufactures either where the data lacks it (thyroid's drop-TSH salvage proves it).

**Caveat (§21).** Even covtype's band comes from a **per-row / memoryless** budget, the acquisition
optimization is identical every case, a near-dominated space. The non-dominated escape is the
commit-mode program; the label-budget world is its first built scheme (see the sibling submission table).

## Methodology (how a band is judged)

Viability is the SDK's noise-floor method (`../../../sdk/methodology/noise_floor.md` §11–14;
`../../../sdk/hor_utils/{noise,resolution}.py`). The grader is deterministic, so the only noise is
**test-set resampling**. For each eval, `../../../scratch/analysis/band_resolution.py`:

1. decodes every run's per-row test predictions from the stored `predictions_b64` (no policy replay);
2. reconstructs the graded test labels exactly (`DataView(cfg).apply` on the committed npz);
3. measures **σ_abs** = `block_bootstrap_sigma` (stratified by class) on the median run, then
   **#band_supports** = `resolution`, **#observed** = `rank_resolution`, and the ceiling-safe **gap test**.

It writes `scratch/analysis/<eval8>/band_supports.json` per eval (the source of truth each record
transcribes), so the numbers are reproducible and never hand-recomputed. Records + this table are
GENERATED by `band_resolution.py --emit`; do not hand-edit rows, re-emit.

## Notes
- Reference: oracle (masking-XGBoost + greedy eddi) validates at balanced accuracy **0.741**; noop ~0.045.
- **budgeted-tep** is synthetic + anonymized TEP (22 faults); covtype remains the real-data flagship.
- Batch: `0067d7a3-4134-40d9-a4eb-c29faeeb24fe`.
