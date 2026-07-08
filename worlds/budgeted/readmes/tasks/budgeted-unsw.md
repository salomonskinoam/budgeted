# budgeted-unsw: band-resolution record

**Verdict: NARROW band, endpoints < 1 LSD apart (inside noise)**

## Band

- Eval: `27615e12-de7e-4b29-8ef7-900fe5870d0e`; 5 runs, 5 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.7222, 0.7310, 0.7312, 0.7317, 0.7325.
- Band (worst to best): 0.7222 to 0.7325.
- Width (spread): 0.0103.

## Noise floor (this row's calculation)

- Metric: balanced-acc.
- Test: 4500 rows across 6 classes. per-class 1056 / 435 / 798 / 251 / 293 / 1667
- Rarest test class (3 = 251 rows) caps resolution (recall SE ~ sqrt(p(1-p)/251)).
- sigma_abs = 0.007486.
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.02117.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.0103/0.02117 = **1.49**. endpoints ~0 LSDs apart.
- #observed = 2 (the tiers the runs actually occupy).
- Gap test: gap = 0.0103, sigma_gap = 0.0050, ratio = 2.04, p_le0 = 0.017.

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 1.49.
- NARROW band, endpoints < 1 LSD apart (inside noise)

## Links

- Task: https://horizon.bespokelabs.ai/tasks/f8cc010b-53f1-4745-9481-146ff721bb50
- Eval: https://horizon.bespokelabs.ai/evaluations/27615e12-de7e-4b29-8ef7-900fe5870d0e
- Analysis (strategy, human-authored, updated independently): `../analysis/budgeted-unsw/STRATEGY.md`
- Source JSON: `../analysis/budgeted-unsw/band_supports.json`
