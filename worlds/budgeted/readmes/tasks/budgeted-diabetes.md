# budgeted-diabetes: band-resolution record

**Verdict: NARROW band; readmission learnable from the cheap groups, expensive labs inert, converge ~0.62**

## Band

- Eval: `9f3883e9-5b3a-4e42-94a7-f170450101dd`; 4 runs, 4 non-degenerate, 1 failed / excluded.
- Scores sorted: 0.6139, 0.6143, 0.6165, 0.6202.
- Band (worst to best): 0.6139 to 0.6202 (+1 fail).
- Width (spread): 0.0063.

## Noise floor (this row's calculation)

- Metric: balanced-acc.
- Test: 12000 rows across 2 classes. per-class 1367 / 10633
- Rarest test class (0 = 1367 rows) caps resolution (recall SE ~ sqrt(p(1-p)/1367)).
- sigma_abs = 0.006961.
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.01969.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.0063/0.01969 = **1.32**. endpoints ~0 LSDs apart.
- #observed = 1 (the tiers the runs actually occupy).
- Gap test: gap = 0.0063, sigma_gap = 0.0042, ratio = 1.53, p_le0 = 0.055.

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 1.32.
- NARROW band; readmission learnable from the cheap groups, expensive labs inert, converge ~0.62

## Links

- Task: https://horizon.bespokelabs.ai/tasks/bb7097fc-2984-4b74-8088-e200de4373f3
- Eval: https://horizon.bespokelabs.ai/evaluations/9f3883e9-5b3a-4e42-94a7-f170450101dd
- Analysis (strategy, human-authored, updated independently): `../analysis/budgeted-diabetes/STRATEGY.md`
- Source JSON: `../analysis/budgeted-diabetes/band_supports.json`
