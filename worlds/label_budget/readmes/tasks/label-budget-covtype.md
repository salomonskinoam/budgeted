# label-budget-covtype: band-resolution record

**Verdict: band VIABLE (wide, endpoints ~6 LSD apart), but ELIMINATED on strategy homogeneity (all 5 students wrote one recipe), not on the band**

## Band

- Eval: `03bdb135-2c06-4dd3-bd13-b3c813daee88`; 5 runs, 5 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.5496, 0.6232, 0.6250, 0.6312, 0.6358.
- Band (worst to best): 0.5496 to 0.6358.
- Width (spread): 0.0862.

## Noise floor (this row's calculation)

- Metric: balanced-acc.
- Test: 56250 rows across 7 classes. per-class 266 / 1986 / 20509 / 27428 / 1681 / 3461 / 919
- Rarest test class (0 = 266 rows) caps resolution (recall SE ~ sqrt(p(1-p)/266)).
- sigma_abs = 0.005242.
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.01483.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.0862/0.01483 = **6.82**. endpoints ~6 LSDs apart.
- #observed = 2 (the tiers the runs actually occupy).
- Gap test: gap = 0.0862, sigma_gap = 0.0060, ratio = 14.47, p_le0 = 0.000.

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 6.82.
- band VIABLE (wide, endpoints ~6 LSD apart), but ELIMINATED on strategy homogeneity (all 5 students wrote one recipe), not on the band

## Links

- Task: https://horizon.bespokelabs.ai/tasks/33da8224-530b-4641-a61a-7f1a1655b823
- Eval: https://horizon.bespokelabs.ai/evaluations/03bdb135-2c06-4dd3-bd13-b3c813daee88
- Analysis (strategy, human-authored, updated independently): `../analysis/label-budget-covtype/STRATEGY.md`
- Source JSON: `../analysis/label-budget-covtype/band_supports.json`
