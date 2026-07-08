# Handoff: scheme 3, small-chunk information release

**Roadmap 08 item 3. Status: DROPPED (2026-07-07, owner decision). Do not build.** Design (kept for
the record) lives on branch `roadmap/commit-schemes`: `readmes/commit_schemes/02_small_chunk_information_release.md`
(read with `git show roadmap/commit-schemes:readmes/commit_schemes/02_small_chunk_information_release.md`).

## Why dropped

The scheme's own design doc argues PROMOTE, but under the current frame the case collapses:

1. **The strong argument isn't available in the form we would build.** Two arguments back the scheme.
   The band argument ("noise adds middle skill rungs") is tagged CONJECTURE in the doc, the pre-test's
   job, not a guarantee. The strong argument is luck-smoothing: many tiny purchases self-average,
   shrink the seed-noise floor (Delta-star), and let smaller skill gaps resolve into more levels. But
   that benefit **only exists for a global shared budget pool**. On a per-row budget there is no
   cross-row order-luck to smooth, so the strong argument evaporates. The doc concedes this in step 5:
   per-row small-chunk "does not manufacture rungs beyond covtype's ladder."

2. **Marginal upside over what already ships.** Discrete covtype already bands at 8.06 / 3 levels (a
   flagship). The per-row noisy version's only remaining pitch is a couple of *conjectured* rungs on a
   substrate that already resolves 3. High effort to maybe nudge an already-good task.

3. **Extremely hard to tune, and the window may not exist.** The alive regime needs noise-per-feature,
   prices, and budget co-tuned so pinning a value costs more than the whole budget yet reads stay
   useful, and it must hold across heterogeneous rows. The doc's Alternatives section concedes that if
   covtype's row-difficulty does not translate into read-value heterogeneity, "the precision game
   degenerates even though the feature-routing game did not." A multi-dimensional search for a
   possibly-empty window.

4. **The sold "measures the noise floor every verdict depends on" value is overstated.** Every existing
   verdict depends on the *discrete* seed noise, already measured from stored predictions by
   `band_resolution.py`. The noisy-world number only matters if we use small-chunk. Circular, not
   independent infrastructure.

**Revisit only if** we ever build the global-pool-plus-commit form, where the luck-smoothing (its one
strong argument) would actually earn its keep. Not before.

## Original idea (for the record)

## The idea

A purchase returns a NOISY reading of a feature value (true value + a fresh Gaussian draw of known std);
buying again gives an independent draw, averaging refines. Acting on partial posteriors adds MIDDLE rungs
the discrete world has no room for, and the luck-smoothing shrinks the noise floor.

## Why it is the highest-value first pick

Its seed-variance measurement directly measures **Delta-star, the DENOMINATOR of #band_supports** (run one
probe at 5 seeds under both the noisy and the discrete scheme, compare the resampling residual). That
number recalibrates the resolution accounting for EVERY other scheme. Small-chunking is also the general
first-pick-luck mitigation the whole falsifier battery leans on (`../../commit_schemes/07_...` test 3).

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
