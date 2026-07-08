# budgeted-thyroid: band-resolution record

**Verdict: REJECT** (both variants).
- ORIGINAL: #band_supports = 2.57 (< 3).
- DROP-TSH salvage: #band_supports = 1.48 (< 3).

Both 3-class, n_test 3428, rarest class 73 rows. No cost/feature knob manufactures heterogeneity the data lacks. The old README wrongly called the original "~1 level"; the correct #band_supports is 2.57 (close to but under the bar).

## Band (two evals)

| variant | eval | scores sorted | band | width |
|---|---|---|---|---|
| ORIGINAL | 6fcbf032 | 0.7472, 0.7984, 0.7999, 0.8029, 0.8448 | 0.747 → 0.845 | 0.098 |
| DROP-TSH | 32c9a8ca | 0.7282, 0.7360, 0.7417, 0.7454, 0.7479 | 0.728 → 0.748 | 0.020 |

## Noise floor

Metric: balanced accuracy. 3428 test rows / 3 classes; per-class 3178 / 177 / 73. The rarest class (73 rows) drives σ_abs.

- ORIGINAL: σ_abs = 0.022, LSD = z·√2·σ_abs (z=2) = 0.0623.
- DROP-TSH: σ_abs = 0.0144, LSD = 0.0407.

## #band_supports vs #observed

#band_supports = 1 + width/LSD.

- ORIGINAL: 1 + 0.098/0.0623 = 2.57 (corrects the old "~1"). #observed = 3. Even a 0.098-wide band only supports ~2.6 tiers because the 73-row rarest class inflates σ_abs. Endpoints sit ~1.6 LSD apart: wide-ish but not resolvable to 3 tiers. Gap test: gap 0.0976, σ_gap 0.0234, ratio 4.18, p(≤0) = 0.0.
- DROP-TSH: 1 + 0.020/0.0407 = 1.48. #observed = 1. Endpoints only ~0.5 LSD apart: narrow, converged. Gap test: gap 0.0197, σ_gap 0.0148, ratio 1.33, p(≤0) = 0.102.

Both narrow-ish; high #band_supports with low #observed would mean wide-and-clustered, but here #band_supports is itself low.

## Verdict

≤2 rule ⇒ both REJECT (2.57 and 1.48 both under 3). The drop-TSH salvage TIGHTENED the band (0.098 → 0.020 width, 2.57 → 1.48): removing TSH removed the one discriminative axis, collapsing the endpoints. Salvage failed. Confirms no cost/feature knob manufactures the heterogeneity this data lacks.

## Links

- Task: https://horizon.bespokelabs.ai/tasks/c69cfa04-5416-486c-b25a-0b345eea4d98
- Original eval: https://horizon.bespokelabs.ai/evaluations/6fcbf032-d5ef-4b13-9040-1fbc44a7a1ca
- Drop-TSH eval: https://horizon.bespokelabs.ai/evaluations/32c9a8ca-6045-4629-a27c-a01e13f656b7
- JSONs: `scratch/analysis/6fcbf032/band_supports.json`, `scratch/analysis/32c9a8ca/band_supports.json`
