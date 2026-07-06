# Small-chunk information release

## The question

Does releasing feature information in small increments create a band, and does it rescue a global
shared budget by making stream-order luck negligible?

Concretely: instead of "buy feature j and receive its exact value for a fixed price," a purchase
returns a NOISY reading of the value; buying the same feature again returns a fresh independent
reading; averaging several readings refines the estimate. Optionally a cheap COARSE tier returns
only a bucket (e.g. which quartile the value falls in) and finer tiers cost more. Every purchase
draws one unit from the budget pool.

Two sub-questions to separate, because they are answered differently:

- **(Band)** Does the noisy-reading mechanic add distinguishable skill rungs between a naive agent
  and an optimal one, so real students of varying strength land at different scores?
- **(Luck)** Does chunking a shared budget into many small purchases reduce the variance a fixed
  policy shows across stream seeds, so measured LEVELS go up even if no new strategy rung is added?

A prior analysis concluded KILL. The task owner rejected that as overclaimed. This file critiques
that memo and rebuilds the analysis under the folder's corrected frame (see the folder README and
file `00_band_theory_what_collapse_arguments_prove.md`).

## Background (terms defined)

**The discrete world (covtype).** The world already built and measured: 7-class Forest CoverType,
52 features, per-case budget, sequential reveal, mediated grader. A purchase returns the feature's
EXACT value. Real students banded from balanced accuracy **0.675 to 0.848, about 3 levels**
(0.68 / 0.74 / 0.84), over a noise floor near 0.058, rarest test class about 295 instances. The
winning per-row move was **masking-XGBoost + greedy value-of-information**: train a predictor on
random feature subsets so it accepts any partial observation, then at test time greedily buy the
feature with the highest expected uncertainty reduction. Strong agents DID find this; the reference
oracle validates at 0.741 and the top real run reached 0.848. This is the reference point everything
below is measured against, because it is a discrete-buy world that BANDED WITH RESOLUTION, even
though its near-optimal per-row policy was computable offline from peek data.

**The small-chunk world.** Same task, but a purchase of feature j returns `x_ij + e`, where `e` is a
fresh independent draw from a fully disclosed noise model (Gaussian, mean 0, known standard deviation
`sigma_j`). Buying j again gives another independent draw. Averaging `m` reads gives an estimate with
posterior standard deviation `sigma_j / sqrt(m)`. The noise model is disclosed at agent time (the
hard constraint: no knowledge is withheld from the peek; only the test stream is unknown). An
optional COARSE tier returns a bucketed value (e.g. quartile) cheaply; finer tiers cost more.

**The averaging attack.** Buy `K` noisy reads of j, average them, drive the posterior standard
deviation to `sigma_j / sqrt(K)`; pick `K` large enough that the estimate is effectively exact. This
recovers the discrete world's exact value at `K` times the cost. The **break-even K** is the
smallest K whose averaged estimate is decision-adequate.

**Posterior / partial posterior.** After `m` reads of j, the agent holds a Gaussian belief over the
true value, not the value itself. Acting on a **partial posterior** means predicting (or deciding the
next purchase) while still uncertain, rather than paying to remove the uncertainty first.

**Named methods** (allocating noisy measurements optimally is a studied problem):
- **Chernoff sequential design of experiments** (1959): choose which noisy measurement to take next
  to discriminate hypotheses (here, classes) fastest; asymptotically optimal sampling proportions.
- **Track-and-Stop** (Garivier and Kaufmann 2016): a best-arm-identification rule that tracks the
  optimal sampling proportions and stops when a confidence statistic crosses a threshold; the modern
  form of Chernoff's idea.
- **Greedy expected information gain / knowledge gradient**: buy the measurement with the largest
  one-step expected reduction in posterior uncertainty (or expected improvement in predicted label
  probability). The direct generalization of covtype's greedy value-of-information to noisy reads:
  the candidate set becomes "sample feature j one more time" and the score is expected uncertainty
  reduction per unit cost.
- **EDDI** (Ma et al. 2019): the active-feature-acquisition method covtype's greedy buyer descends
  from: value-of-information by imputation-sampling under a shared predictor.
- **Offline Monte-Carlo rollout**: fit class-conditional feature distributions from peek data, then
  simulate (roll out) many hypothetical read sequences to plan the whole sample budget over a finite
  horizon, rather than deciding one read at a time.

**Levels / n_levels / Delta\*.** LEVELS = number of statistically distinguishable score tiers across
runs (`rank_resolution` `n_levels` in `sdk/hor_utils/noise.py`), the folder's most important metric.
Mechanically, a true score gap between two policies is resolvable into separate levels only if it
exceeds the seed noise. **Delta\*** is the seed-blocked analysis-of-variance (ANOVA) resolution gap
(roughly: t-threshold x pooled residual standard deviation x sqrt(2/S) for S seeds). Levels are
approximately (achievable score range) / Delta\*. Two ways to raise levels: widen true gaps
(add strategy rungs), or shrink Delta\* (reduce seed noise). Small-chunking targets the second.

**Seed noise vs skill difference.** The grader reruns the shipped policy under 5 fixed stream seeds
and averages. **Seed noise** is the run-to-run variation of ONE policy caused by the random draw of
which cases arrive, in what order, and (here) which noise realizations are returned. **Skill
difference** is the deterministic gap between two DIFFERENT policies' expected scores. Seed averaging
shrinks seed noise; it does not shrink skill differences. The two are kept strictly separate below.

**Bounded computation and front-loading** (owner correction, file 00 and direction readme §22b).
Agents are COMPUTATIONALLY BOUNDED, and computation generates information: "a peek-calibrated agent
computes X offline" is a kill argument only if computing X is also FAST and EASY; "could have
computed it" does not establish "would have." Separately, the **front-loading principle**: the
grade-time cap does not care when compute is spent, so any mid-stream improvement that needs only
compute is dominated by doing the work in `__init__` before the stream; the only things that resist
front-loading are STREAM-REVEALED resources (values the grader hands over during the stream).

## The process

### 1. Sorting the predecessor's claims by epistemic status

The memo asserted one verdict (KILL) from five claims of very different strength. Sorted:

- **The averaging attack exists and reduces the market to the discrete world at Kx cost.**
  [PROVEN] as an AVAILABLE strategy. It is a real, computable exploit, and (unlike the planning
  methods below) computing the break-even K IS fast and easy: a closed-form function of the
  disclosed `sigma_j` and the prices. Two things the claim is NOT: it is not proven that agents
  PLAY it (that depends on the price regime, step 6), and it is a statement about the CEILING (the
  best play), not about the band (the spread of all plays). Step 2 works out what a ceiling
  reduction does and does not imply.
- **Allocating noisy reads is Chernoff / Track-and-Stop; the remaining finite-horizon planning room
  "is solvable by offline Monte-Carlo rollout because peek hands the agent the generative model."**
  Split this. [PROVEN]: the near-optimal rules exist, and peek does supply the generative model, so
  everything here is in principle front-loadable into `__init__` (no stream-revealed resource is
  needed to BUILD the rule). [ARGUMENT, previously mis-tagged as if proven]: the leap from
  "solvable" to "solved by agents" idealizes computation. Under the bounded-computation correction,
  offline-computable kills only when the computation is fast and easy; calibrating a
  Track-and-Stop rule and running Monte-Carlo rollouts are several insights deep AND real compute
  (step 4). [CONJECTURE]: that real agents of varying strength actually reach these rules. This is
  exactly the shape the folder README forbids treating as a kill: covtype's near-optimal per-row
  policy was ALSO offline-computable, and covtype banded.
- **"Per-sample noise washes out over 2100 rows x 5 seeds, producing a cluster of good agents."**
  [ARGUMENT], and a confused one. Washing out the noise DRAW is the luck-smoothing virtue (step 5),
  not evidence of packing. It says nothing about the deterministic allocation-skill gaps between
  policies, which do not wash out (step 3). The "cluster of good agents, low stragglers, wrong band
  shape" conclusion does not follow from noise-averaging, and it also assumes the good cluster is
  populated, an all-agents-strong premise.
- **"Composition with the global pool makes the collapse HARDER (divisible measurements convexify
  the per-row value)."** [ARGUMENT] about the CEILING policy only. A cleaner shadow price means the
  BEST agent converges cleanly; it is silent on the spread of sub-optimal agents. And convexifying /
  smoothing is the SAME mechanism the memo elsewhere praised as "kills first-pick luck." Scored once
  as a vice and once as a virtue; step 5 works out which it is under the levels statistic.
- **VERDICT KILL-as-standalone.** [CONJECTURE] presented as settled. The evidence supports at most
  "the ceiling reduces to covtype's ceiling," which is a statement about the top rung, not the band.

The owner's objection holds: only the availability of the averaging attack is proven, and it bounds
the top, not the band. The two claims the KILL leaned on hardest (Track-and-Stop offline, Monte-Carlo
rollout) are, additionally, exactly the compute-idealizing pattern file 00 corrects.

### 2. What containment of the discrete world implies

[PROVEN] The small-chunk world CONTAINS the discrete world as a special case. Set `sigma_j = 0` (or,
equivalently, let one read be decision-adequate) and one purchase returns the exact value: this is
covtype exactly. So the small-chunk decision problem is a SUPERSET of covtype's. Any strategy
playable in covtype is playable here (read each chosen feature enough times and average), so the
achievable-score SET of the small-chunk world contains covtype's achievable-score set.

[ARGUMENT] Now place the predecessor's reduction inside this containment. "Optimal play reduces to
covtype's optimal play at Kx cost" says the two worlds share a CEILING. Covtype's ceiling sat on top
of a band of 0.675 to 0.848 with about 3 levels. For a world that shares that ceiling and strictly
contains that decision problem, the only route to FEWER levels than covtype's is that the added
mechanics actively COMPRESS the differences between agents (pack the sub-optimal plays toward the
ceiling). The memo never argued compression; it only exhibited the shared ceiling. So the proven
part of the reduction functions as a FLOOR on the scheme's quality, not a collapse. Step 3 examines
whether the added mechanics compress or spread.

[ARGUMENT] The containment also cuts the other way: the small-chunk FLOOR can sit LOWER than
covtype's, because there are new ways to waste a binding budget (re-reading a feature already known
well enough, refining an already-decisive row). Same ceiling, lower floor = a WIDER potential band.

[ARGUMENT] One more consequence, via the front-loading principle. In this scheme the RULE is
front-loadable (peek supplies everything needed to build it in `__init__`), but the DECISIONS are
not: each read's outcome is a stream-revealed resource, and the next allocation depends on the
realized posterior. So the skill expression sits on the correct side of the information boundary
(§22b): unlike agent-time commits, mid-stream behavior here is not dominated by precomputation. A
precomputable rule driving non-precomputable decisions is precisely covtype's situation, and covtype
banded.

### 3. The middle of the ladder: agents acting on partial posteriors

Between the naive agent (buy one noisy read, treat it as truth) and the exact-recovery agent (average
to the break-even K, recover the value, play covtype), there is a CONTINUUM of agents acting on
partial posteriors. The noisy mechanic opens a skill dimension the discrete world does not have,
because in covtype a bought value is exact and there is no "how sure am I of this reading" axis.
Distinct failure modes along that axis:

- **Ignore the noise model** (treat 1 read as truth). A naive rung with no covtype counterpart.
- **Over-sample easy rows** (keep refining values that were already decisive), starving the binding
  budget so hard rows get too few reads.
- **Under-sample ambiguous rows** (act on a reading still too noisy to decide), misclassifying
  exactly the boundary cases that carry the resolvable signal.
- **Mis-propagate posterior variance into the classifier** (feed the point estimate as if exact, or
  feed a mis-scaled uncertainty), degrading predictions in a graded way.
- **Fail to calibrate class-conditional distributions offline** despite having the peek, so the
  stopping decisions are miscalibrated. Under bounded computation this is an expected rung, not an
  anomaly: the calibration is available but neither fast nor obvious, so some agents skip it.

[ARGUMENT] Do these differences reach the score, or wash out? They change the ALLOCATION of a
binding budget, and mis-allocation lands on the resolvable subset: covtype's levels were capped by
the rarest class (about 295 instances) and by ambiguous boundary rows, and those are exactly the
rows where an extra read flips the prediction. An agent that squanders reads on easy rows has fewer
reads for the ambiguous ones and loses accuracy precisely where the metric can see it. The
predecessor's wash-out claim is about the NOISE DRAW (which does average away, step 5); the
deterministic policy-to-policy allocation gap survives seed averaging untouched.

[CONJECTURE] Whether these rungs are SEPARATED by more than Delta\* is the pre-test's job (step 7).
The prior: covtype already resolved a routing ladder (random / fixed / greedy) into about 3 levels;
adding an orthogonal allocation-of-precision ladder on the same substrate adds candidate rungs and
removes none.

### 4. Discoverability and compute cost of the rungs

The band lives in the GAP between a discoverable middle rung and a hard-to-reach top rung. Covtype's
evidence is the discoverability proxy: strong agents there found masking-XGBoost + greedy
value-of-information. Walking the ladder from that reference point:

- **The greedy expected-information-gain rung is highly discoverable and cheap to run** [ARGUMENT].
  It is the SAME argmax-value-of-information loop covtype's winners already wrote, with the
  candidate set changed from "buy unbought feature j" to "sample feature j once more" and the score
  changed to expected uncertainty reduction under a running posterior. An agent that found covtype's
  move extends it with modest effort (model the read as noisy, keep a posterior, keep the loop).
  A known code pattern with trivial per-decision compute.
- **The top rung is several insights deep AND compute-heavy** [ARGUMENT]. Track-and-Stop / Chernoff
  sampling proportions and finite-horizon Monte-Carlo rollout require: (a) recognizing the problem
  as sequential experiment design, (b) fitting the generative model offline, (c) implementing a
  stopping/allocation rule, (d) planning under a horizon, and then paying for rollouts at scale.
  The front-loading principle removes only the TIMING barrier (all of this fits in `__init__`); it
  does not remove the discovery barrier or the compute bill. Under bounded computation, "peek hands
  the agent the generative model" therefore establishes a high rung's existence, not its occupancy.

[ARGUMENT] That configuration (an easy middle rung, a hard top rung, a real gap between) is the
band-producing shape. The predecessor read the same facts as "residual planner-vs-greedy gap = same
peek-vs-eddi gap covtype already has, no NEW levels," but that gap is precisely the one the design
bible (§19) calls real algorithmic headroom where students spread: reproducing covtype's resolvable
gap is a PASS signature. And the small-chunk world adds a rung BELOW greedy (agents who ignore the
noise model), a rung the discrete world has no room for.

### 5. The owner's claim: what many small purchases do to seed variance

This is the (Luck) sub-question, separate from the band rungs. In a GLOBAL shared pool over a
stream, first-pick luck is the failure where a few large, lumpy early commitments (pure seed noise
in which cases arrive first) swing the final score. Small-chunking makes every purchase a tiny
increment, so a fixed policy's outcome depends on its AGGREGATE gathering behavior over many small
reads, which self-averages, rather than on a handful of pivotal lumps. Therefore the VARIANCE of a
fixed policy's score across seeds falls [ARGUMENT].

Now connect that to the metric. Levels are approximately (score range) / Delta\*, and Delta\* is
proportional to the seed noise. Shrinking seed noise shrinks Delta\*, which makes SMALLER true gaps
resolvable, which RAISES measured n_levels, even if the scheme adds no new strategy rung at all
[ARGUMENT]. Luck-smoothing is therefore not a mere "nice modifier on someone else's scheme"; it is a
direct intervention on the denominator of the most important metric. This is plausibly the strongest
single argument for the scheme, and the memo compressed it into one dismissive line ("keep only as a
luck-smoothing modifier") because it was reasoning about mean-convergence of the OPTIMAL policy
rather than about the levels statistic.

Honest scoping: this virtue is specifically a GLOBAL-pool virtue. Under a per-row (memoryless)
budget there is no cross-row order-luck to smooth, so only the step-3 within-row uncertainty rungs
remain. So the owner's claim lands as stated: small-chunk rescues the global pool from first-pick
luck, and the rescue operates through seed-variance / measurability rather than by manufacturing
strategy rungs by itself. The predecessor was right that per-row small-chunk alone does not
manufacture rungs beyond covtype's ladder, but buried the levels-via-Delta\* mechanism that makes
the luck claim decision-relevant. Both effects (step-3 rungs within a row, step-5 luck-smoothing
across rows) point the same way: more resolvable levels.

### 6. Degenerate corners and the alive regime

Three corners defeat the scheme; naming them defines the regime to design for [ARGUMENT throughout]:

- **Noise too small** (`sigma_j` so small one read is decision-adequate): reduces to covtype
  exactly. Not fatal (covtype's ~3 levels are retained) but the step-3 upside is lost. Avoid.
- **Noise too large** (even affordable averaging never makes readings decision-useful): buying is
  worthless, informative purchases never bind the budget, scores fall toward the free-feature
  baseline. A dead corner; must be designed away.
- **Prices that make the averaging attack the obvious best play** (break-even K cheap relative to
  budget). This is the one corner the bounded-computation correction does NOT soften: computing K
  is a closed-form, fast-and-easy calculation from the disclosed noise model and prices, so
  expecting most competent agents to find it is legitimate here. They buy exactly K reads and pack
  at the discrete-world ceiling: the small-chunk analogue of covtype's "one cheap feature tops the
  score" degeneracy falsifier. Must be priced away.

**The alive regime.** Budget and noise set so that FULLY recovering even a few features would
exhaust the pool, forcing the agent to act on partial posteriors and to allocate reads UNEQUALLY:
pour refinement into rows/features where extra precision flips the decision, spend one cheap read
where it does not. Formally, the sample budget must bind against the cost of certainty
(`sigma_j / sqrt(K)` reaches decision-usefulness only at a K whose total cost exceeds the budget).
This is the precision-space form of the binding falsifier (direction readme §5) and the
heterogeneity requirement (§17): the VALUE OF A READ must be HETEROGENEOUS across rows (easy rows
decisive after one read, hard rows needing many). Small-chunk converts covtype's "which feature is
decisive" heterogeneity into "how much precision is decisive" heterogeneity, and covtype already has
row-level difficulty heterogeneity (easy vs ambiguous cover types), so the substrate exists. The
coarse-to-fine tier is a knob on the same axis (cheap bucket first, pay for resolution only where
the bucket is ambiguous).

### 7. The pre-test

Throwaway probes through the real grader via hosted validation; no student evals. All probes share
ONE masking-robust predictor (as the §16 acquisition gate does) so spread is attributable to
allocation, not modeling. Budgets matched on TOTAL cost, with the noisy read priced so that covtype
is the `sigma -> 0` special case at equal budget. Run on covtype, hosted.

Probe ladder, at matched budget:
1. **Random allocator**: spend reads uniformly at random over features/rows.
2. **Fixed per-row sample count**: buy covtype's fixed-best panel, read each feature a fixed `m`
   times, average.
3. **Greedy expected information gain**: the covtype EDDI-style loop over the candidate "sample j
   once more," argmax expected uncertainty reduction per cost.
4. **Sequential-testing rule**: per-feature stopping (keep sampling j until the posterior standard
   deviation drops below a threshold, or j's value-of-information drops below its price); a
   Track-and-Stop-style rule.
5. **Offline-planned allocation**: Monte-Carlo rollout using peek-fitted class-conditional
   distributions; the compute-heavy top rung.

Read: probes 3 to 5 separating from 1 and 2 by more than Delta\* means the uncertainty-management
ladder is real. Packing means the noisy mechanic added no rung over covtype's discrete ladder
(covtype's ~3 levels are still inherited; packing here is not by itself fatal).

Seed-variance measurement (the step-5 / owner claim; the most decisive single test): run ONE probe
(probe 3) at 5 seeds under BOTH the small-chunk noisy scheme and covtype's discrete scheme at
matched budget; compare per-run seed noise (block-bootstrap sigma / the ANOVA residual). Smaller
seed sigma under small-chunk confirms luck-smoothing, shrinks Delta\*, and makes smaller true gaps
resolvable.

Degeneracy probe: the averaging-attack buyer (compute break-even K, buy exactly K, play covtype).
If it dominates probes 3 to 5 by more than Delta\*, the price/noise regime is in the third corner of
step 6 and must be re-priced before any student eval.

## The result

**PROMOTE TO PRE-TEST. Do not kill.** The predecessor's KILL rests on a proven statement about the
CEILING (the averaging attack reduces optimal play to covtype's optimal play) treated as if it were
a statement about the band, plus two compute-idealizing claims ("Track-and-Stop offline,"
"solvable by Monte-Carlo rollout") that the bounded-computation correction re-tags as high rungs
rather than collapses. Under the corrected frame: the small-chunk world CONTAINS covtype, which
banded at about 3 levels, so absent a positive compression argument (which the memo never gave) its
levels are at least covtype's (step 2); it plausibly ADDS uncertainty-management rungs the discrete
world has no room for (step 3); its top rung is several insights deep and compute-heavy while its
middle rung is one step from covtype's winning move, the band-producing shape (step 4); and its
luck-smoothing lowers Delta\* and thereby RAISES measured levels for a global pool (step 5), the
argument the predecessor buried and the one the owner is pointing at. The order-luck-killing claim
is valid, and the skill expression sits on the correct side of the information boundary because
each read is a stream-revealed resource that resists front-loading (step 2).

**What would flip it to KILL.** The step-7 pre-test showing the noisy mechanic COMPRESSES the agent
spread below covtype's at matched budget, specifically ALL of: the greedy / sequential / planned
probes packing within Delta\* of the fixed and random probes (no new rung), AND the measured seed
variance failing to fall below the discrete world's (no luck-smoothing), AND no price/noise regime
avoiding the three corners of step 6. Equally fatal on its own: a demonstration that the alive
regime of step 6 does not exist on real data (the break-even K is always either trivially cheap or
unaffordably expensive, with no middle), because then every configuration lands in a dead corner.

## Alternatives

- **The metric.** Balanced accuracy weights rare classes heavily, which is what gave covtype its
  resolution, and it does NOT decouple the score from the scheme's test-time uncertainty the way it
  does for pure arrival-mixture schemes (§22b), because here the uncertainty lives in PRECISION
  spent per row, not in which classes arrive. So balanced accuracy is fine for the per-row form.
  For the global-pool form, confirm the levels statistic is computed on per-run predictions (not
  just scores) so the Delta\*-shrink of step 5 is actually measured.
- **The data.** If covtype's row-difficulty heterogeneity turns out too weak to make read-value
  heterogeneous (every row decided by one read of the same feature), the precision game degenerates
  even though the feature-routing game did not. The fallback substrate is the same one the design
  bible points at for the routing band: a bigger many-class differential dataset (the Tennessee
  Eastman scaffold, or a real fault-diagnosis set), where per-class decisive features AND per-row
  difficulty both vary.
- **Coarse-to-fine only.** If the additive-noise form proves too easy to average away at any
  affordable price, the tiered form (cheap bucket, pay for resolution) may bind more naturally,
  because averaging repeated bucket reads of the same value adds nothing once the bucket is known;
  refinement requires paying up a tier. Worth pre-testing as a separate mechanic if the Gaussian
  form degenerates.

## Open questions

1. **Does the alive regime of step 6 exist on real data?** Is there a noise/price setting where the
   break-even K is neither trivially cheap nor unaffordable, so partial-posterior play is forced?
   This is the make-or-break empirical question and the averaging-attack degeneracy probe is the
   cheapest test of it.
2. **How much does Delta\* actually shrink under small-chunking?** The step-5 argument is
   directional; the magnitude (and hence how many extra levels luck-smoothing buys) is unknown
   until the 5-seed measurement runs. If the shrink is marginal, small-chunk is a weak modifier; if
   large, it is the main event.
3. **Composition with the global pool.** Step 5 argues small-chunk RESCUES the global pool by
   smoothing order-luck, directly contradicting the predecessor's "makes collapse harder." Both are
   currently arguments; a global-pool pre-test (small-chunk reads drawn from one shared reservoir
   over the stream, 5 seeds) would settle whether the pool bands with small-chunk where it collapsed
   without. This is the highest-value follow-up because it tests the owner's original motivation
   directly.
4. **Where does the compute bill actually bite?** The top rung's Monte-Carlo rollout must fit the
   grade-time cap even when front-loaded into `__init__`. If it does not fit, the top rung drops to
   the sequential-testing rule and the ladder shortens by one; worth measuring in the step-7 probe.
5. **Does the tiered (coarse-to-fine) form dominate the additive-noise form?** Different degeneracy
   profiles; possibly one bands where the other does not.
