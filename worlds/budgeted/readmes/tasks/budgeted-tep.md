# budgeted-tep: band-resolution record

**Verdict: WIDE band, endpoints ~8 LSD apart (synthetic + anonymized Tennessee Eastman Process, 22 faults; accepted for tasks)**

## Band

- Eval: `4d68f219-12f4-4f79-b61c-ee118052f610`; 3 runs, 3 non-degenerate, 2 failed / excluded.
- Scores sorted: 0.6516, 0.7962, 0.8240.
- Band (worst to best): 0.6516 to 0.8240 (+2 fail).
- Width (spread): 0.1724.

## Noise floor (this row's calculation)

- Metric: balanced-acc.
- Test: 2381 rows across 22 classes. per-class 108 / 108 / 108 / 108 / 108 / 108 / 108 / 108 / 108 / 108 / 108 / 113 / 108 / 108 / 108 / 108 / 108 / 108 / 108 / 108 / 108 / 108
- Rarest test class (0 = 108 rows) caps resolution (recall SE ~ sqrt(p(1-p)/108)).
- sigma_abs = 0.007490 (stratified block-bootstrap on the median run).
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.02118.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.1724/0.02118 = **9.14**. endpoints ~8 LSDs apart.
- #observed = 3 (the tiers the runs actually occupy).
- Gap test: gap = 0.1724, sigma_gap = 0.0086, ratio = 20.12, p_le0 = 0.000.

## Driver: per-class recall (weak -> strong)

| run | score | c0 | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 | c9 | c10 | c11 | c12 | c13 | c14 | c15 | c16 | c17 | c18 | c19 | c20 | c21 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4 | 0.652 | 0.69 | 1.00 | 0.32 | 0.60 | 0.16 | 0.20 | 0.61 | 0.98 | 0.62 | 0.95 | 0.76 | 0.16 | 0.91 | 0.97 | 0.23 | 0.74 | 0.61 | 0.66 | 0.99 | 0.85 | 0.67 | 0.65 |
| 1 | 0.796 | 0.82 | 1.00 | 0.44 | 0.86 | 0.81 | 0.47 | 0.80 | 1.00 | 0.82 | 0.95 | 0.84 | 0.44 | 0.95 | 0.94 | 0.38 | 1.00 | 0.81 | 0.70 | 0.96 | 0.91 | 0.78 | 0.81 |
| 5 | 0.824 | 0.81 | 1.00 | 0.56 | 0.90 | 0.76 | 0.46 | 0.94 | 1.00 | 0.81 | 1.00 | 0.96 | 0.42 | 0.95 | 0.96 | 0.45 | 0.96 | 0.90 | 0.77 | 0.99 | 0.94 | 0.82 | 0.76 |

- recall delta (best - worst): c0 +0.12, c1 +0.00, c2 +0.24, c3 +0.30, c4 +0.60, c5 +0.26, c6 +0.32, c7 +0.02, c8 +0.20, c9 +0.05, c10 +0.20, c11 +0.26, c12 +0.05, c13 -0.01, c14 +0.22, c15 +0.22, c16 +0.29, c17 +0.11, c18 +0.00, c19 +0.08, c20 +0.16, c21 +0.11

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 9.14.
- WIDE band, endpoints ~8 LSD apart (synthetic + anonymized Tennessee Eastman Process, 22 faults; accepted for tasks)

## Links

- Task: https://horizon.bespokelabs.ai/tasks/36abdac8-4edd-4304-a48c-53933cd34f62
- Eval: https://horizon.bespokelabs.ai/evaluations/4d68f219-12f4-4f79-b61c-ee118052f610
- Analysis (strategy, human-authored, updated independently): `../analysis/budgeted-tep/STRATEGY.md`
- Source JSON: `../analysis/budgeted-tep/band_supports.json`
