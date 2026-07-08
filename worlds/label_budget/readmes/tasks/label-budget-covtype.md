# label-budget-covtype: band-resolution record

**Verdict: ELIMINATED (strategy homogeneity, NOT band).** The band is viable and resolvable (#band_supports 6.82, well past the ≥3 rule), but all five students wrote the identical recipe, so the task is eliminated on strategy homogeneity, not on the band.

## Band

- eval `03bdb135-2c06-4dd3-bd13-b3c813daee88`, 5 runs, 0 failed, 5 non-degenerate.
- scores sorted: [0.550, 0.623, 0.625, 0.631, 0.636].
- band 0.550 → 0.636, width 0.086.

## Noise floor

- metric: balanced accuracy.
- n_test 56250 rows, 7 classes (natural covtype imbalance; per-class 266 / 1986 / 20509 / 27428 / 1681 / 3461 / 919).
- rarest class 0 = 266 rows caps σ (levels are limited by the rarest class).
- σ_abs 0.0052 (stratified bootstrap).
- LSD 0.0148.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.086/0.0148 = **6.82**. This is the endpoint distance: the lowest run (0.550) and the highest (0.636) are ~5.8 LSDs apart, i.e. a **WIDE** band.
- gap check confirms the endpoints are genuinely distinct: ratio 14.5, p_le0 0.0.
- #observed = **2**: the runs occupy only 2 tiers. Four runs are clustered high near ~0.63, one run sits far below at 0.55, and the ~5 tiers between them are EMPTY. This is a wide band with TOP-HEAVY / clustered occupancy.
- This is explicitly **NOT convergence.** A high #band_supports is the opposite of converged; the width is real, the middle is just empty.

## Why eliminated (strategy, not band)

The band passes the ≥3 rule, so on band mechanics alone it would SUBMIT. It is eliminated on STRATEGY HOMOGENEITY instead. A separate analysis of the 5 submitted solutions found all five wrote the same recipe:

standardize features → KMeans diversity seed → class-weight-balanced tree model → uncertainty + inverse-frequency rare-class boost + greedy/KMeans diversity downselect → batched rounds → strong/ensemble final model.

The four top runs are trim variants of that one recipe. The low run (0.55) is the SAME recipe with an over-aggressive rare-class quota, i.e. a bug in the recipe, not a different strategy. So there is no genuine strategy diversity: the wide band is one weak variant sitting below a pack, not a skill ladder. Because every student converges on the same strategy, the task is eliminated.

Salvage of this scheme is being pursued separately: sharpen rare-class starvation via `pool_per_class` and remove the hint-telegraphed recipe so students must find the strategy rather than copy it.

## Links

- task: https://horizon.bespokelabs.ai/tasks/33da8224-530b-4641-a61a-7f1a1655b823
- eval: https://horizon.bespokelabs.ai/evaluations/03bdb135-2c06-4dd3-bd13-b3c813daee88
- data: `scratch/analysis/03bdb135/band_supports.json`
