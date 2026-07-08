# budgeted-covtype: band-resolution record

**Verdict: WIDE band, endpoints ~7 LSD apart; the test resolves it despite the rarest class holding 266 rows**

## Band

- Eval: `babd012a-4ae2-4349-99cb-a030db3f4491`; 5 runs, 5 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.6754, 0.6861, 0.7386, 0.8356, 0.8476.
- Band (worst to best): 0.6754 to 0.8476.
- Width (spread): 0.1722.

## Noise floor (this row's calculation)

- Metric: balanced-acc.
- Test: 2066 rows across 7 classes. per-class 266 / 300 / 300 / 300 / 300 / 300 / 300
- Rarest test class (0 = 266 rows) caps resolution (recall SE ~ sqrt(p(1-p)/266)).
- sigma_abs = 0.008619 (stratified block-bootstrap on the median run).
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.02438.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.1722/0.02438 = **8.06**. endpoints ~7 LSDs apart.
- #observed = 3 (the tiers the runs actually occupy).
- Gap test: gap = 0.1722, sigma_gap = 0.0110, ratio = 15.64, p_le0 = 0.000.

## Driver: per-class recall (weak -> strong)

| run | score | c0 | c1 | c2 | c3 | c4 | c5 | c6 |
|---|---|---|---|---|---|---|---|---|
| 3 | 0.675 | 0.74 | 0.89 | 0.61 | 0.44 | 0.63 | 0.61 | 0.80 |
| 4 | 0.686 | 0.67 | 0.78 | 0.78 | 0.85 | 0.59 | 0.78 | 0.35 |
| 1 | 0.739 | 0.85 | 0.95 | 0.68 | 0.50 | 0.72 | 0.58 | 0.89 |
| 2 | 0.836 | 0.73 | 0.95 | 0.88 | 0.78 | 0.79 | 0.85 | 0.87 |
| 5 | 0.848 | 0.73 | 0.97 | 0.86 | 0.74 | 0.85 | 0.88 | 0.91 |

- recall delta (best - worst): c0 -0.01, c1 +0.08, c2 +0.24, c3 +0.30, c4 +0.23, c5 +0.26, c6 +0.11

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 8.06.
- WIDE band, endpoints ~7 LSD apart; the test resolves it despite the rarest class holding 266 rows

## Links

- Task: https://horizon.bespokelabs.ai/tasks/4de1e511-7738-4889-bed3-a0a532b051e5
- Eval: https://horizon.bespokelabs.ai/evaluations/babd012a-4ae2-4349-99cb-a030db3f4491
- Analysis (strategy, human-authored, updated independently): `../analysis/budgeted-covtype/STRATEGY.md`
- Source JSON: `../analysis/budgeted-covtype/band_supports.json`
