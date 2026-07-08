# budgeted-tep: band-resolution record

**Verdict: WIDE band, endpoints ~8 LSD apart (synthetic + anonymized Tennessee Eastman Process, 22 faults; accepted for tasks)**

## Band

- Eval: `4d68f219-12f4-4f79-b61c-ee118052f610`; 3 runs, 3 non-degenerate, 2 failed / excluded.
- Scores sorted: 0.6516, 0.7962, 0.8240.
- Band (worst to best): 0.6516 to 0.8240 (+2 fail).
- Width (spread): 0.1724.

## Noise floor (this row's calculation)

- Metric: balanced-acc.
- Test: 2381 rows across 22 classes. per-class 108 / 108 / 108 / 108 / 108 / 108 / 108 / 108 / 108 / 108 / 108 / 113 / 108 / 108 / 108 / 108 / 108 / 108 / 108 / 108 / 108 / 108
- Rarest test class (0 = 108 rows) caps resolution (recall SE ~ sqrt(p(1-p)/108)).
- sigma_abs = 0.007490.
- LSD = z*sqrt(2)*sigma_abs (z=2) = 0.02118.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.1724/0.02118 = **9.14**. endpoints ~8 LSDs apart.
- #observed = 3 (the tiers the runs actually occupy).
- Gap test: gap = 0.1724, sigma_gap = 0.0086, ratio = 20.12, p_le0 = 0.000.

## Verdict

- Rule: #band_supports >= 3 = SUBMIT-viable; <= 2 = REJECT (at the ceiling, the gap test decides).
- #band_supports = 9.14.
- WIDE band, endpoints ~8 LSD apart (synthetic + anonymized Tennessee Eastman Process, 22 faults; accepted for tasks)

## Links

- Task: https://horizon.bespokelabs.ai/tasks/36abdac8-4edd-4304-a48c-53933cd34f62
- Eval: https://horizon.bespokelabs.ai/evaluations/4d68f219-12f4-4f79-b61c-ee118052f610
- Analysis (strategy, human-authored, updated independently): `../analysis/budgeted-tep/STRATEGY.md`
- Source JSON: `../analysis/budgeted-tep/band_supports.json`
