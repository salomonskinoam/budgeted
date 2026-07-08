# label-budget-covtype-open: band-resolution record

**Verdict: the open-ended (no-hints) + rare-class-starved salvage of label-budget-covtype: a WIDE band AND a real, code-legible skill gradient (rare-class recall c1/c6, p_le0=0)**

## Band

- Eval: `303517c9-82fd-4641-84a2-cb4f88e41606`; 5 runs, 5 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.4987, 0.5022, 0.5205, 0.5361, 0.5734.
- Band (worst to best): 0.4987 to 0.5734.
- Width (spread): 0.0748.

## Noise floor (this row's calculation)

- Metric: balanced-acc.
- Test: 56250 rows across 7 classes. per-class 266 / 1986 / 20509 / 27428 / 1681 / 3461 / 919
- Rarest test class (0 = 266 rows) caps resolution (recall SE ~ sqrt(p(1-p)/266)).
- sigma_abs = 0.003878.
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.01097.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.0748/0.01097 = **7.82**. endpoints ~7 LSDs apart.
- #observed = 4 (the tiers the runs actually occupy).
- Gap test: gap = 0.0748, sigma_gap = 0.0041, ratio = 18.35, p_le0 = 0.000.

## Driver: per-class recall (weak -> strong)

| run | score | c0 | c1 | c2 | c3 | c4 | c5 | c6 |
|---|---|---|---|---|---|---|---|---|
| 3 | 0.499 | 0.93 | 0.20 | 0.65 | 0.83 | 0.41 | 0.45 | 0.03 |
| 4 | 0.502 | 0.91 | 0.17 | 0.71 | 0.79 | 0.43 | 0.37 | 0.13 |
| 2 | 0.520 | 0.93 | 0.26 | 0.70 | 0.75 | 0.41 | 0.44 | 0.15 |
| 1 | 0.536 | 0.91 | 0.43 | 0.72 | 0.81 | 0.44 | 0.37 | 0.07 |
| 5 | 0.573 | 0.94 | 0.51 | 0.71 | 0.81 | 0.45 | 0.42 | 0.17 |

- recall delta (best - worst): c0 +0.00, c1 +0.31, c2 +0.06, c3 -0.02, c4 +0.05, c5 -0.03, c6 +0.14

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 7.82.
- the open-ended (no-hints) + rare-class-starved salvage of label-budget-covtype: a WIDE band AND a real, code-legible skill gradient (rare-class recall c1/c6, p_le0=0)

## Links

- Task: https://horizon.bespokelabs.ai/tasks/e9ee3601-21ce-4162-b868-ab424d7932cd
- Eval: https://horizon.bespokelabs.ai/evaluations/303517c9-82fd-4641-84a2-cb4f88e41606
- Analysis (strategy, human-authored, updated independently): `../analysis/label-budget-covtype-open/STRATEGY.md`
- Source JSON: `../analysis/label-budget-covtype-open/band_supports.json`
