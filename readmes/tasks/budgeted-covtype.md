# budgeted-covtype: band-resolution record

**Verdict: SUBMIT.** #band_supports = 8.06 (a wide band whose endpoints sit ~7 LSDs apart).

## Band

- Eval: `babd012a-4ae2-4349-99cb-a030db3f4491`, 5 runs, 5 non-degenerate, 0 failed / 0 excluded.
- Scores sorted: 0.6754, 0.6861, 0.7386, 0.8356, 0.8476.
- Band (worst to best): 0.6754 to 0.8476.
- Width: 0.1722.

## Noise floor (this row's calculation)

- Metric: balanced accuracy.
- Test: 2066 rows across 7 classes (balanced to 300/class via `test_per_class`; class 0 has only 266).
- The rarest test class (class 0, 266 rows) caps resolution: per-class recall SE about
  sqrt(p(1-p)/266), so the noisiest recall term sets the resampling floor.
- sigma_abs measured by stratified block-bootstrap on the median run (op = 0.7386): sigma_abs = 0.008619.
- LSD = z * sqrt(2) * sigma_abs, z = 2: LSD = 0.02438.

## #band_supports vs #observed

- #band_supports = 1 + width / LSD = 1 + 0.1722 / 0.02438 = 8.06.
  Endpoints are about 7 LSDs apart, so this is a WIDE band (endpoints far apart, not converged).
- #observed = 3 (the tiers the 5 runs actually occupy).
- Gap test: gap = 0.1722, sigma_gap = 0.011, ratio = 15.64, p_le0 = 0.0.
- Interpretation: a wide band (endpoints ~7 LSDs apart) with clustered occupancy across 3 tiers,
  the low pair (0.675, 0.686), a mid point (0.739), and the high pair (0.836, 0.848), leaving
  empty middle tiers. Wide and resolvable, not converged.

## Verdict (from #band_supports only)

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT.
- #band_supports = 8.06.
- Conclusion: SUBMIT. The test resolves the endpoints (~7 LSDs apart) despite the rarest class
  holding only 266 rows.

## Links

- Task: https://horizon.bespokelabs.ai/tasks/4de1e511-7738-4889-bed3-a0a532b051e5
- Eval: https://horizon.bespokelabs.ai/evaluations/babd012a-4ae2-4349-99cb-a030db3f4491
- Source JSON: `scratch/analysis/babd012a/band_supports.json`
