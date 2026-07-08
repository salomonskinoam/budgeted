# budgeted-derma: band-resolution record

**Verdict: REJECT (resolution floor).** #band_supports = **1.21**.

The spread is real, but it sits inside a noise floor set by a 4-instance test
class. The band cannot be resolved at any run count.

## Band

- eval: `0dd9f969-ebd5-44ef-b891-aeeccfcd6502`
- scores sorted: 0.9307, 0.9426, 0.9426, 0.9426, 0.9459
- band: 0.931 → 0.946
- width: 0.015

## Noise floor (capped by a 4-row class)

- metric: balanced accuracy
- n_test = 83, 6 classes
- rarest test class = **4 rows**. A 4-row recall has SE ≈ √(p(1−p)/4) ≈ 0.18.
- that lone 4-row class dominates σ_abs: σ_abs = **0.0257** (huge for a 0.94 score).
- LSD = z·√2·σ_abs (z=2) = **0.0727**.

This is a RESOLUTION cap, not a lack of structure. The band endpoints reflect
real differences between runs, but the per-class recall of a 4-instance class is
so noisy that it inflates σ_abs, and LSD swallows the whole 0.015-wide band.

## #band_supports vs #observed

- #band_supports = 1 + width/LSD = 1 + 0.015 / 0.0727 = **1.21**.
- endpoints are only ~0.2 LSD apart → unresolvable.
- #observed = **1** (all 5 runs are one indistinguishable tier).
- gap test: gap 0.0152, σ_gap 0.0227, ratio 0.67, P(≤0) = 0.278.

## Verdict

**REJECT (resolution floor).** The structure is real, but a 4-instance test
class makes the band unresolvable at ANY N. More runs do not help: the floor is
set by class size, not by sample count. This is exactly the failure mode covtype
was built to avoid (a populous rarest class keeps σ_abs small enough that real
spread resolves into LEVELS).

## Links

- task: https://horizon.bespokelabs.ai/tasks/1a019b65-bfed-4779-8e00-e3982d3c7a51
- eval: https://horizon.bespokelabs.ai/evaluations/0dd9f969-ebd5-44ef-b891-aeeccfcd6502
- data: `scratch/analysis/0dd9f969/band_supports.json`
