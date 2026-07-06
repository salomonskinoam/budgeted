# budgeted-hydraulic: band-resolution record

**Verdict: REJECT (ceiling).** The band saturates near 1.0, so Method B (#band_supports = 1 + width/LSD) is invalid here: near the ceiling the score is bounded and σ shrinks, which makes the tier count blow up meaninglessly. The gap test decides instead, and it says the endpoints are indistinct.

## Band

- eval `f7318a3b-91ea-4456-a086-4d43bd449468`, 5 runs with preds, 0 failed, 5 non-degenerate.
- scores sorted: 0.991, 0.991, 0.991, 0.991, 0.994
- band 0.991 -> 0.994, width 0.003, sitting right on the 1.0 ceiling (mid 0.992).

## Noise floor + ceiling

- metric: balanced accuracy over 497 test rows, 3 classes; per-class 111 / 275 / 111, rarest class = 0 at 111.
- Why Method B is invalid at the ceiling: the score is bounded at 1.0, so σ collapses toward 0 as runs pile against the ceiling; width/LSD then inflates and #band_supports reports an arbitrarily large tier count that means nothing.
- σ_abs 0.0051 is reported for the record, but #band_supports is NOT computed (`band_supports`: null, `ceiling`: true).

## Gap test (the ceiling-safe verdict)

- gap 0.003, σ_gap 0.0029, ratio 1.02.
- **p_le0 0.392**: the best<->worst ordering REVERSES on 39% of bootstrap resamples. Endpoints indistinct.
- #observed 1.

## Verdict

REJECT. The budget never binds: one cheap sensor already solves the pump fault, so the task saturates at ~0.99. The band is at the 1.0 ceiling and its whole width sits inside noise, best and worst differ by 0.003 with a 39% reversal rate. No resolvable spread, no levels.

## Links

- task https://horizon.bespokelabs.ai/tasks/2935f9b4-ea7f-4127-8b73-b91a7d4d6f24
- eval https://horizon.bespokelabs.ai/evaluations/f7318a3b-91ea-4456-a086-4d43bd449468
- `scratch/analysis/f7318a3b/band_supports.json`
