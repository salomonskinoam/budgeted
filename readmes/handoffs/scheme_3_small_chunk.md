# Handoff: scheme 3, small-chunk information release (first pick)

**Roadmap 08 item 3. Status: NOT BUILT.** Promote-to-pre-test. Design:
`../commit_schemes/02_small_chunk_information_release.md` (step 7 has the probes).

## The idea

A purchase returns a NOISY reading of a feature value (true value + a fresh Gaussian draw of known std);
buying again gives an independent draw, averaging refines. Acting on partial posteriors adds MIDDLE rungs
the discrete world has no room for, and the luck-smoothing shrinks the noise floor.

## Why it is the highest-value first pick

Its seed-variance measurement directly measures **Delta-star, the DENOMINATOR of #band_supports** (run one
probe at 5 seeds under both the noisy and the discrete scheme, compare the resampling residual). That
number recalibrates the resolution accounting for EVERY other scheme. Small-chunking is also the general
first-pick-luck mitigation the whole falsifier battery leans on (`../commit_schemes/07_...` test 3).

## What to build

- A noisy-mediator drive loop: a buy of feature j returns `true + N(0, sigma)`; a running posterior in the
  probes averages repeats. Add the noise mechanic to a drive loop (extend `worlds/budgeted/drive.py` or a
  new world), one shared masking-robust predictor across probes.
- A five-probe ladder at matched total budget (random allocator, fixed per-row sample count, greedy
  expected-information-gain, sequential-testing stop rule, offline Monte-Carlo-planned allocation).
- The decisive seed-variance comparison (noisy vs discrete) and the averaging-attack degeneracy probe
  (compute the break-even number of reads, buy exactly that many, play the discrete world).

## Make-or-break

Does an "ALIVE REGIME" exist on real data, a price-and-noise setting where fully recovering a value costs
MORE than the budget, so partial-posterior play is forced? If the break-even read count is always either
trivially cheap or unaffordable (no middle), the scheme degenerates. The degeneracy probe is the cheapest
test of this, run it first.

Judge results with `band_method.md`, and reuse the measured Delta-star to sharpen every other scheme's
#band_supports.
