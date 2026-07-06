# budgeted-unsw: band-resolution record

**Verdict: REJECT** (#band_supports = 1.49)

## Band

- Eval: `27615e12-de7e-4b29-8ef7-900fe5870d0e` (5 runs with preds, 0 failed, 5 non-degenerate).
- Scores sorted: 0.7222, 0.7310, 0.7312, 0.7317, 0.7325.
- Band: 0.722 -> 0.733.
- Width (max - min): 0.010.

## Noise floor

- Metric: balanced accuracy.
- Test set: 4500 rows, 6 classes.
- Per-class counts: {0: 1056, 1: 435, 2: 798, 3: 251, 4: 293, 5: 1667}. Rarest class = 3 with 251 rows; it caps the resolvable noise (sigma).
- sigma_abs = 0.0075 (stratified bootstrap).
- LSD = z * sqrt(2) * sigma_abs, z=2 -> 0.0212.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.010/0.0212 = 1.49.
- Endpoints are only ~0.5 LSD apart (width 0.010 < LSD 0.0212), so lowest and highest runs sit within noise: a NARROW / converged band.
- #observed = 2 tiers occupied.
- Gap test: gap 0.0103, sigma_gap 0.005, ratio 2.04, p(<=0) 0.017.

## Verdict

#band_supports = 1.49 is below 3 (<=2 rule) -> REJECT. The band lies inside the noise floor; the spread does not resolve into distinguishable levels.

## Links

- Task: https://horizon.bespokelabs.ai/tasks/f8cc010b-53f1-4745-9481-146ff721bb50
- Eval: https://horizon.bespokelabs.ai/evaluations/27615e12-de7e-4b29-8ef7-900fe5870d0e
- Source JSON: `scratch/analysis/27615e12/band_supports.json`
