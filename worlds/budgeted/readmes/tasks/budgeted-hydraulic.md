# budgeted-hydraulic: band-resolution record

**Verdict: CEILING: gap test says endpoints indistinct; one cheap sensor solves it so the budget never binds**

## Band

- Eval: `f7318a3b-91ea-4456-a086-4d43bd449468`; 5 runs, 5 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.9910, 0.9910, 0.9910, 0.9910, 0.9940.
- Band (worst to best): 0.9910 to 0.9940.
- Width (spread): 0.0030.

## Noise floor (this row's calculation)

- Metric: balanced-acc.
- Test: 497 rows across 3 classes. per-class 111 / 275 / 111
- Rarest test class (0 = 111 rows) caps resolution (recall SE ~ sqrt(p(1-p)/111)).
- sigma_abs = 0.005095.
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.01441.

## Gap test (the ceiling-safe verdict)

- Band saturates near the ceiling, so Method B (#band_supports) is invalid; the gap test decides.
- Gap test: gap = 0.0030, sigma_gap = 0.0029, ratio = 1.02, p_le0 = 0.392.

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- ceiling; gap test P(gap<=0) = 0.392.
- CEILING: gap test says endpoints indistinct; one cheap sensor solves it so the budget never binds

## Links

- Task: https://horizon.bespokelabs.ai/tasks/2935f9b4-ea7f-4127-8b73-b91a7d4d6f24
- Eval: https://horizon.bespokelabs.ai/evaluations/f7318a3b-91ea-4456-a086-4d43bd449468
- Analysis (strategy, human-authored, updated independently): `../analysis/budgeted-hydraulic/STRATEGY.md`
- Source JSON: `../analysis/budgeted-hydraulic/band_supports.json`
