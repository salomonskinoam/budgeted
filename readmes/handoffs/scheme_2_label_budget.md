# Handoff: scheme 2, label budget / active learning (first pick)

**Roadmap 08 item 2. Status: BUILT and run, ELIMINATED on strategy homogeneity, SALVAGE in progress.**
Design: `../commit_schemes/03_train_label_budget.md`. Build: `worlds/label_budget/{world,drive,policy_runner}.py`,
task `tasks/label-budget-covtype/`, config `tasks_def/configs/label_budget_covtype.py`.

## The scheme

The student gets the training FEATURES unlabeled plus a total label budget L. The grader drives one
active-learning session: round by round the policy names pool rows, the grader reveals those labels
charging the shared pool, the policy trains, then predicts the whole (held-out) test set in one batched
call. Every label (train + test) stays grader-side. This is a global LABEL budget, the one form of
"global budget" that does not collapse (purchased labels are the resource front-loading cannot reach).

## Result (eval `03bdb135`, L=2000, 5 runs)

Band 0.550 -> 0.636, **#band_supports 6.82** (a WIDE, resolvable band; endpoints ~6 LSD apart, gap
p_le0 0.0), but **#observed 2** (top-heavy). **ELIMINATED, not on the band, on STRATEGY HOMOGENEITY:**
all 5 students wrote the identical recipe (standardize -> KMeans diversity seed -> class-weight-balanced
tree -> uncertainty + inverse-frequency rare-class boost + greedy/KMeans diversity -> ensemble final
model). The low run (0.55) is the same recipe with an over-aggressive rare-class quota, a bug, not a
different strategy. Record: `../tasks/label-budget-covtype.md`.

**Root cause:** the config hints TELEGRAPHED the recipe (they named uncertainty / coreset / rare-class /
spend-curve), and covtype is redundant enough that the recipe pays off uniformly. Zero discovery gap.

## Salvage in progress (a parallel chat holds these config edits)

`tasks_def/configs/label_budget_covtype.py` now: **L lowered to 1500** (each pick counts more),
**`pool_per_class`** sharpening rare-class starvation (2 dominant anon classes stay huge, the other 5
capped to 1000 rows so naive labeling almost never reaches them while a rare-class hunter can), and
**`hints: []`** (no recipe handout, strategy must be discovered). A `label_budget_covtype_open` variant
also exists. Goal: force real strategy diversity.

## Next action

Re-run 5 student evals on the salvage config, then judge with BOTH:
1. `band_method.md` (#band_supports), and
2. a **strategy-diversity check** (pull the 5 solutions via `horizon rollouts pull`, tabulate what each
   did, as in the record). A high #band_supports is NOT enough; the recipe must actually differ across
   students. If it still converges, the scheme is dead on covtype, consider a less-redundant dataset
   (03 Alternatives: Sensorless Drive, Letter Recognition) or accept elimination.

Note: item 6 (paid revision, `../commit_schemes/06_paid_revision.md`) is contingent on this scheme
passing its dominance gate; it has no content until label budget bands with real strategy diversity.
