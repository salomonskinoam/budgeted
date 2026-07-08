# budgeted-derma: band-resolution record

**Verdict: real spread, but the rarest test class = 4 rows buries it; unresolvable at any run count**

## Band

- Eval: `0dd9f969-ebd5-44ef-b891-aeeccfcd6502`; 5 runs, 5 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.9307, 0.9426, 0.9426, 0.9426, 0.9459.
- Band (worst to best): 0.9307 to 0.9459.
- Width (spread): 0.0152.

## Noise floor (this row's calculation)

- Metric: balanced-acc.
- Test: 83 rows across 6 classes. per-class 16 / 11 / 12 / 4 / 26 / 14
- Rarest test class (3 = 4 rows) caps resolution (recall SE ~ sqrt(p(1-p)/4)).
- sigma_abs = 0.025706.
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.07271.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.0152/0.07271 = **1.21**. endpoints ~0 LSDs apart.
- #observed = 1 (the tiers the runs actually occupy).
- Gap test: gap = 0.0152, sigma_gap = 0.0227, ratio = 0.67, p_le0 = 0.278.

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 1.21.
- real spread, but the rarest test class = 4 rows buries it; unresolvable at any run count

## Links

- Task: https://horizon.bespokelabs.ai/tasks/1a019b65-bfed-4779-8e00-e3982d3c7a51
- Eval: https://horizon.bespokelabs.ai/evaluations/0dd9f969-ebd5-44ef-b891-aeeccfcd6502
- Analysis (strategy, human-authored, updated independently): `../analysis/budgeted-derma/STRATEGY.md`
- Source JSON: `../analysis/budgeted-derma/band_supports.json`
