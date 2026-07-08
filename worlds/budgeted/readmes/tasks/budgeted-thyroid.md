# budgeted-thyroid: band-resolution record

**Verdict: below the 3-tier bar (73-row rarest class inflates sigma); drop-TSH salvage TIGHTER, it failed**

## Eval: orig

### Band

- Eval: `6fcbf032-d5ef-4b13-9040-1fbc44a7a1ca` (orig); 5 runs, 5 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.7472, 0.7984, 0.7999, 0.8029, 0.8448.
- Band (worst to best): 0.7472 to 0.8448.
- Width (spread): 0.0976.

### Noise floor (this row's calculation)

- Metric: balanced-acc.
- Test: 3428 rows across 3 classes. per-class 3178 / 177 / 73
- Rarest test class (2 = 73 rows) caps resolution (recall SE ~ sqrt(p(1-p)/73)).
- sigma_abs = 0.022038.
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.06233.

### #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.0976/0.06233 = **2.57**. endpoints ~2 LSDs apart.
- #observed = 3 (the tiers the runs actually occupy).
- Gap test: gap = 0.0976, sigma_gap = 0.0234, ratio = 4.18, p_le0 = 0.000.

## Eval: drop-TSH

### Band

- Eval: `32c9a8ca-6045-4629-a27c-a01e13f656b7` (drop-TSH); 5 runs, 5 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.7282, 0.7360, 0.7417, 0.7454, 0.7479.
- Band (worst to best): 0.7282 to 0.7479.
- Width (spread): 0.0197.

### Noise floor (this row's calculation)

- Metric: balanced-acc.
- Test: 3428 rows across 3 classes. per-class 3178 / 177 / 73
- Rarest test class (2 = 73 rows) caps resolution (recall SE ~ sqrt(p(1-p)/73)).
- sigma_abs = 0.014397.
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.04072.

### #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.0197/0.04072 = **1.48**. endpoints ~0 LSDs apart.
- #observed = 1 (the tiers the runs actually occupy).
- Gap test: gap = 0.0197, sigma_gap = 0.0148, ratio = 1.33, p_le0 = 0.102.

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- orig: #band_supports = 2.57.
- drop-TSH: #band_supports = 1.48.
- below the 3-tier bar (73-row rarest class inflates sigma); drop-TSH salvage TIGHTER, it failed

## Why the drop-TSH salvage failed

The drop-TSH salvage TIGHTENED the band (0.098 -> 0.020 width, #band_supports 2.57 -> 1.48), it did not widen it. Removing TSH removed the one discriminative axis, collapsing the endpoints. Confirms the design bible: no cost/feature knob manufactures the heterogeneity this data lacks (both variants REJECT).

## Links

- Task: https://horizon.bespokelabs.ai/tasks/c69cfa04-5416-486c-b25a-0b345eea4d98
- Eval (orig): https://horizon.bespokelabs.ai/evaluations/6fcbf032-d5ef-4b13-9040-1fbc44a7a1ca
- Eval (drop-TSH): https://horizon.bespokelabs.ai/evaluations/32c9a8ca-6045-4629-a27c-a01e13f656b7
- Analysis (strategy, human-authored, updated independently): `../analysis/budgeted-thyroid/STRATEGY.md`
- Source JSON: `../analysis/budgeted-thyroid/band_supports.json`
