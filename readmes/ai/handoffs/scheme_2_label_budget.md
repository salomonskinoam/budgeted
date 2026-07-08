# Handoff: scheme 2, label budget / active learning (first pick)

**Roadmap 08 item 2. Status: BUILT; first version ELIMINATED on strategy; OPEN salvage SHIPS.** The
`label-budget-covtype` reference (L=2000, hints on) was eliminated on strategy homogeneity, but the
salvage **`label-budget-covtype-open`** (hints stripped + `pool_per_class` rare-class starvation, L=1500)
now SUBMITs: **#band_supports 7.82, 4 tiers occupied, a real code-legible skill gradient.** All committed.
Design: `../../commit_schemes/03_train_label_budget.md`. Build: `worlds/label_budget/{world,drive,policy_runner}.py`,
tasks `tasks/label-budget-covtype{,-open}/`, configs `tasks_def/configs/label_budget_covtype{,_open}.py`.

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
different strategy. Record: `../../../worlds/label_budget/readmes/tasks/label-budget-covtype.md`.

**Root cause:** the config hints TELEGRAPHED the recipe (they named uncertainty / coreset / rare-class /
spend-curve), and covtype is redundant enough that the recipe pays off uniformly. Zero discovery gap.

## Salvage RESULT (label-budget-covtype-open, eval `303517c9`, L=1500)

The salvage worked. Config: **`hints: []`** (no recipe handout, strategy must be discovered) +
**`pool_per_class`** starving 5 classes to 1000 rows (2 dominant anon classes stay huge) so naive
labeling almost never reaches the rare ones. Result: band 0.499 -> 0.573, **#band_supports 7.82**,
**#observed 4** (vs the reference's 2), gap p_le0 0.0. The weak->strong axis is a genuine, code-legible
skill: ~92% of the band is rare-class recall (c1 +0.31, c6 +0.14), and each rank step maps to a concrete
code choice (full-pool scan + rarest-first selection + reweighting at the top; random-subsample /
60%-random / single-model at the bottom). Full driver table + code diff: `../../../worlds/label_budget/readmes/tasks/label-budget-covtype-open.md`.

**Shape (the honest caveat):** this is a SKILL GRADIENT within one recipe family, not strategy DIVERSITY.
Every student still wrote the standard active-learning recipe; they differ in execution quality on the
rare classes. That is a valid, resolvable RL reward signal (real skill, not seed luck, not one outlier),
and it SHIPS. It is not two genuinely-different strategies.

## Next action / open question

- The open variant SHIPS as-is (skill gradient). Decide whether that is enough, or whether to pursue true
  strategy DIVERSITY, which would need the deferred **label-cost second axis** (03 P15e: cheap vs expensive
  labels create a rationing tradeoff with no dominant rule) or a less-redundant dataset (03 Alternatives:
  Sensorless Drive, Letter Recognition).
- Item 6 (paid revision, `../../commit_schemes/06_paid_revision.md`) is unlocked in principle now that the
  label budget bands, but it targets strategy diversity, revisit only if pursuing the second axis.
- The label-budget scheme is otherwise DONE for this pass; the two remaining first picks are items 1 and 3.
