# budgeted-tep: band-resolution record

**Verdict: SUBMIT (#band_supports 9.14).** tep is synthetic + anonymized Tennessee Eastman Process
(a 22-fault process-control benchmark). Its band clears the bar with room to spare and the owner accepts
it for tasks, so it ships. It also doubles as the end-to-end proof of the mediated-acquisition pipeline
(grader drives the student `Policy` under a per-case budget).

## Band

Eval `4d68f219`, 3 runs produced predictions, 2 runs FAILED (no working policy, score 0).

Scores sorted (non-degenerate): **0.6516 · 0.7962 · 0.824**.
- Band: **0.652 → 0.824**, width **0.172**.
- #observed = **3** (all three successes occupy distinct tiers).

**Excluded: 2 failed runs (score 0).** They produced no policy (`errored=0`, a real failure mode, not
infra). Zero is a bonus floor, not the operating floor, the band is measured across the three runs
that actually operated, so the failed pair is excluded from width/#band_supports.

## Noise floor (this row's calculation)

- Metric: **balanced accuracy** over the hidden test split.
- Test set: **2381 rows across 22 fault classes**.
- Class counts are near-uniform (`per_class_counts`): 21 classes at 108 rows, one at 113. The
  **rarest class = 108 rows**, and balanced accuracy is a mean of per-class recalls, so the rarest
  class caps how finely σ resolves.
- **σ_abs = 0.00749**, a stratified bootstrap on the operating run (0.7962), resampling within class so
  the per-class recall variance (dominated by the 108-row classes) sets the scale.
- **LSD = z·√2·σ_abs = 2·√2·0.00749 = 0.0212.** Two scores are distinguishable when farther apart
  than one LSD.

## #band_supports vs #observed

- **#band_supports = 1 + width/LSD = 1 + 0.172/0.0212 = 9.14.**
- Endpoints are ~**8 LSDs apart** (0.172/0.0212 ≈ 8.1): the lowest and highest operating runs sit far
  apart, a **WIDE** band, not converged.
- **#observed = 3**, the runs cluster into 3 occupied tiers inside that wide interval. High
  #band_supports with low #observed = wide band, clustered occupancy, not convergence.
- Gap test on the endpoints: gap 0.1724, σ_gap 0.0086, **ratio 20.1**, P(gap≤0)=0, the spread is real,
  not test noise.

## Verdict

#band_supports 9.14 ≥ 3 ⇒ **SUBMIT**. The band is wide (endpoints ~8 LSDs apart) and the spread is
statistically real (gap test P(gap≤0)=0). tep is a synthetic + anonymized process-control benchmark;
the owner accepts it for tasks, so it ships. It also serves as the end-to-end proof that the mediated
per-case acquisition loop grades correctly and separates policies.

## Links

- Task: https://horizon.bespokelabs.ai/tasks/36abdac8-4edd-4304-a48c-53933cd34f62
- Eval: https://horizon.bespokelabs.ai/evaluations/4d68f219-12f4-4f79-b61c-ee118052f610
- Numbers: `scratch/analysis/4d68f219/band_supports.json`
