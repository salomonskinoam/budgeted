# budgeted-diabetes: band-resolution record

**Verdict: REJECT** (#band_supports = 1.32)

A NARROW, converged band. The two endpoints sit ~0.3 LSD apart (width < LSD), so the whole spread is inside noise.

## Band

- Eval: `9f3883e9-5b3a-4e42-94a7-f170450101dd`
- Scores sorted: 0.6139, 0.6143, 0.6165, 0.6202
- Band: 0.6139 → 0.6202
- Width: 0.0063 (max − min of observed scores)
- Excluded: 1 run FAILED (no policy produced, score 0), dropped from the band.

## Noise floor

- Metric: balanced accuracy.
- Test set: 12000 rows, 2 classes. Per-class counts: 0 → 1367, 1 → 10633.
- Rarest class count 1367 caps σ (resolution ceiling).
- σ_abs (stratified bootstrap): 0.0070.
- LSD = z·√2·σ_abs (z=2) = 0.0197.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.0063/0.0197 = 1.32.
- Endpoints only ~0.3 LSD apart → NARROW / converged, no resolvable tiers between lowest and highest run.
- #observed = 1.
- Gap test (top run vs pack): gap 0.0063, σ_gap 0.0042, ratio 1.53, p(≤0) 0.055. The single high point (0.6202) is not a clean outlier.

## Verdict

#band_supports 1.32 ≤ 2 ⇒ REJECT. Readmission is learnable from the cheap feature groups alone, so the expensive labs are inert and every policy converges to ~0.62. Width < LSD: the band is noise, not signal.

## Links

- Task: https://horizon.bespokelabs.ai/tasks/bb7097fc-2984-4b74-8088-e200de4373f3
- Eval: https://horizon.bespokelabs.ai/evaluations/9f3883e9-5b3a-4e42-94a7-f170450101dd
- Data: `scratch/analysis/9f3883e9/band_supports.json`
