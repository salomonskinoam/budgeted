# 04 Instrument installation

## The question

Two-tier economics on the mediated grader. INSTALLING an instrument (a group of features) costs a
large one-time amount from a single global pool shared across the whole test stream. Once an
instrument is installed, READING any feature in it, on any later test row, is free or cheap. Features
whose instrument was never installed are unreadable (or cost full price every time). An installed
instrument can optionally be resold back to the pool at a loss (a haircut).

Does this two-tier structure create a skill ladder with resolvable rungs across real students of
varying strength, or does it collapse to a single answer that is both computable at agent time and
cheap enough that agents of every strength actually reach it? If it collapses, what is the smallest
honest change that restores a ladder?

## Background (terms defined)

- **The world.** `worlds/budgeted/`. A student (an LLM coding agent) ships a `Policy` class. At
  grade time a mediated grader (`verify.py`) drives the policy row by row over a hidden test stream:
  for each row it runs `select_next -> reveal -> predict`, enforcing the economics grader-side and
  never transmitting labels. Peek data (train and validation features AND labels) is fully available
  at agent time.
- **covtype.** Forest CoverType (`make_data_covtype.py`): 581k rows subsampled to 250k, 54 features,
  7 tree-cover classes. The 54 features are 10 quantitative terrain features (Elevation plus 9 other
  cartographic), 4 wilderness-area binary indicators, and 40 soil-type binary indicators. Features
  are anonymized and column-permuted; Elevation (the dominant single predictor) is priced into the
  expensive tier so it is not a free lunch. Classes are populous (rarest test class ~270), which is
  why covtype was chosen over dermatology (direction doc section 18): it has resolution.
- **Instrument.** A named feature group offered as one purchasable unit. Proposed groups:
  `I_elev = {Elevation}`, `I_terrain = {the 9 other cartographic features}`, `I_wild = {the 4
  wilderness binaries}` shipped FREE as an always-readable situation signal, and the 40 soil
  indicators split into ~5 groups of 8 by elevation-band correlation. So ~7 purchasable instruments.
- **Install pool `P`.** One scalar budget for the whole stream. `install_cost(g)` is charged once
  when instrument `g` is installed; `read_cost` is charged (or waived) per feature read on a row.
  `install_cost(g) ~ read_cost * M_breakeven`, so installing pays off only if the instrument is read
  on at least `M_breakeven` rows. `P ~ 0.6 * (sum of all install costs)`, so installing everything
  is not affordable (this is the tightness knob).
- **Resale.** `{"act":"resell","inst":g}` refunds `install_cost(g) * (1 - haircut)`, haircut ~0.4.
- **Seeded mixture.** Evaluation reruns the shipped policy under 5 fixed stream seeds; the reported
  score is the mean over seeds, and levels are counted by a seed-blocked analysis of variance (SDK
  `rank_resolution`, `n_levels`). For this scheme, seed `s` draws a per-deployment class mixture
  `theta_s` (Dirichlet over the 7 classes, with a per-class floor so resolution survives) and samples
  the 2100-row stream from the peek-known test pool, shuffled by `s`. Production framing: each seed
  is a different **deployment site** with a different mix of arriving cases.
- **Balanced accuracy (bAcc).** The world's standard metric: the unweighted mean over classes of
  per-class recall, `bAcc = (1/K) * sum_c recall_c`, where `recall_c` is the fraction of arriving
  class-`c` rows predicted correctly.
- **Fixed panel.** One feature subset applied identically to every test row; the object of the
  fixed-panel-selection subtask studied in direction doc sections 16 and 19.
- **Masking-robust predictor.** A predictor trained (via random-masking augmentation on peek data)
  to predict from any feature subset. Building one is the standard first engineering step in this
  world.
- **The corrected frame (folder README, file 00).** Two owner corrections, and every step below
  obeys both. First, strength: nobody says all agents are strong; a dominance claim describes the
  strong-agent fixed point and kills only if the dominant move is also EASY to discover (file 00,
  steps R2 and R8). Second, bounded computation: agents are computationally bounded and computation
  generates information, so "computable at agent time" kills only if the computation is also FAST,
  finishable by weak agents before the point where the scheme samples their climb; "could have
  computed it" does not mean "would have" (file 00, steps R3 and R8). A precomputability claim that
  fails either axis is only a CEILING statement: it locates the top of the ladder and says nothing
  about the band below it. covtype itself banded 0.675 to 0.848 (about 3 levels) under a per-row
  policy whose near-optimum was offline-computable; much of that band was engineering rungs, agents
  failing to convert session compute into a working policy at all (file 00, step R5).
- **Delta\*.** The seed-blocked resolution gap: the analysis-of-variance threshold below which two
  scores count as one level. Two rungs closer than Delta\* are not two rungs.
- **Tags.** [PROVEN] = mathematical reduction or working exploit; [ARGUMENT] = heuristic backed by
  this world's evidence; [CONJECTURE] = needs a pre-test.

## The process

### Part A: what task does the install mechanic actually pose?

**S1 [PROVEN].** Suppose `read_cost = 0` for installed instruments (the "free reads" tier). On any
row, reading an installed feature costs nothing, and a masking-robust predictor at inference never
does worse with more features revealed. So on every row the rational `predict` reads everything the
installed set exposes. The installed set `S` is then one observation window applied identically to
all 2100 rows, with no per-row acquisition decision left inside it. That is, by definition, a fixed
panel: the install mechanic under free reads poses the fixed-panel-selection task.

**S2 [PROVEN].** Now ask where the top of that task sits. The peek data gives the joint distribution
of features and label, and the stream is sampled from the peek-known test pool. For any candidate
panel `S` with `sum_{g in S} install_cost(g) <= P`, the expected score is a function of the peek
distribution and the arrival mixture only, estimable offline by scoring the masking predictor on
peek validation rows masked to `features(S)`. Taking the argmax over affordable `S` is therefore an
agent-time computation. This locates the CEILING: an agent that runs this computation has its full
install decision in hand before row one arrives. By the corrected frame this is not yet a kill; the
next two steps test the two axes that decide whether it is.

**S3 [ARGUMENT].** Axis one, is the ceiling computation FAST, and axis two, is it EASY to discover?
Count it out. There are ~7 purchasable instruments, so 2^7 = 128 subsets, of which a few dozen
(order 35) are affordable under `P`. Scoring one subset is one masked validation pass of an
already-built masking predictor: seconds. The whole enumeration is minutes of compute. Fast: yes.
Discoverable: enumerating affordable feature-group subsets against a validation set is a textbook
recipe (exhaustive small search or forward selection) fitting one obvious code pattern, the two
strongest discoverability proxies we have (file 00, step R11a and R11b). So, for any agent that
already has a working masking predictor and a working driven policy, the precomputability claim of
S2 survives the bounded-computation correction on both axes: this part of the ladder is one easy,
fast rung. The claim does NOT extend below that prerequisite: building the masking predictor and a
policy that survives the mediated grader at all is the engineering climb, which is neither easy nor
fast, and it is where covtype's native rungs live (file 00, step R5). So the honest statement is:
above the engineering rungs, panel choice by enumeration is a single cheap step; the ceiling is
reached by every agent that clears the prerequisites, not by every agent.

**S4 [ARGUMENT].** What ladder does that leave below the ceiling? Agents that do not run the
enumeration can still install badly: install only the single dominant instrument (elevation) and
stop, or install greedily by unit predictive value and burn the pool on redundant soil groups. Those
are real distinct behaviors, so whether they are distinct RUNGS comes down to one number, the regret
spread across affordable panels: if bad panels score far below the best affordable panel (more than
Delta\* apart), weak-panel agents land visibly lower; if several affordable panels tie near the
ceiling, the behaviors exist but the scores pack.

**S5 [PROVEN for the reduction; ARGUMENT for the precedent].** Which of this world's two precedents
does the reduced task fall under? Section 16's finding: when a task reduces to picking one fixed
panel, real students packed on datasets with globally-dominant panels (the "feature selection
everyone converges to" failure). Section 19's finding: adaptive PER-ROW acquisition climbed above
the fixed-panel plateau exactly where feature relevance was heterogeneous across many classes (the
Tennessee Eastman Process result). The install scheme under free reads installs one panel for the
whole stream (S1), so per-row adaptivity, the thing that climbed in section 19, is not part of the
posed task; the section 19 escape route is structurally absent here. What remains is
fixed-panel-selection, section 16's object, plus the engineering climb underneath it. covtype's
native band (about 3 levels) already grades both of those. Combined with S3 (panel choice above the
engineering rungs is one easy fast step), the interim finding of Part A is: under a fixed effective
arrival mixture, the install mechanic (install costs, pool, resale, two tiers) adds no rung that
covtype does not already grade without it. The one remaining way the mechanic could earn its own
rung is if the arrival mixture is unknown until the stream runs AND changes which panel is best,
because then the install decision genuinely depends on reading the stream. The proposed source of
that unknown is the per-seed class mixture `theta_s`. Part B tests whether the metric lets it
matter.

### Part B: does the per-seed class mixture change the best panel under balanced accuracy?

**S6 [PROVEN].** Write the arrival mixture as class proportions `p = (p_1, ..., p_K)`. `recall_c`
is a within-class quantity: among the class-`c` rows that arrive, the fraction predicted correctly.
Its expectation depends on the panel and on WHICH class-`c` rows tend to arrive, but not on `p_c`
(HOW MANY arrive): changing `p` rescales the class buckets, not the expected fraction-correct
inside a bucket. Balanced accuracy weights every class `1/K` regardless of `p`. Therefore
`argmax_S bAcc(S)` is the same at every arrival mixture: the balanced-accuracy-optimal panel is
mixture-invariant.

**S7 [PROVEN], worked micro-example, verifiable by hand.** Three classes, two candidate panels.
Panel A is better for class 1; panel B is better for classes 2 and 3. Per-class recalls (the
inputs; any numbers with this shape work):

| | recall class 1 | recall class 2 | recall class 3 |
|---|---|---|---|
| Panel A | 0.90 | 0.50 | 0.50 |
| Panel B | 0.40 | 0.80 | 0.80 |

Balanced accuracy is the unweighted mean of each row:
- `bAcc(A) = (0.90 + 0.50 + 0.50) / 3 = 1.90 / 3 = 0.633`
- `bAcc(B) = (0.40 + 0.80 + 0.80) / 3 = 2.00 / 3 = 0.667`

The mixture never enters this computation, so panel B wins balanced accuracy under EVERY mixture,
by a fixed 0.033. Now compute overall (arrival-weighted) accuracy, `overall = sum_c p_c * recall_c`,
at two deployment sites:

Site 1, mixture `(0.10, 0.45, 0.45)` (classes 2 and 3 common):
- `overall(A) = 0.10*0.90 + 0.45*0.50 + 0.45*0.50 = 0.09 + 0.225 + 0.225 = 0.540`
- `overall(B) = 0.10*0.40 + 0.45*0.80 + 0.45*0.80 = 0.04 + 0.360 + 0.360 = 0.760`, B wins.

Site 2, mixture `(0.80, 0.10, 0.10)` (class 1 common):
- `overall(A) = 0.80*0.90 + 0.10*0.50 + 0.10*0.50 = 0.72 + 0.05 + 0.05 = 0.820`, A wins.
- `overall(B) = 0.80*0.40 + 0.10*0.80 + 0.10*0.80 = 0.32 + 0.08 + 0.08 = 0.480`

| metric | Site 1 optimum | Site 2 optimum |
|---|---|---|
| balanced accuracy | B | B (unchanged) |
| overall accuracy | B | A (flipped) |

The balanced-accuracy optimum is the same panel at both sites; the overall-accuracy optimum flips.

**S8 [PROVEN].** Apply S6 to the door Part A left open. The per-seed class mixture `theta_s` is
genuinely unknown until the stream reveals it, but by S6 it does not change which panel maximizes
balanced accuracy, so it does not change the optimal install decision. A stream-blind agent that
runs S3's enumeration once on peek and never reads the stream mixture loses nothing to an agent
that reads it perfectly. Under the world's standard metric, per-seed CLASS-mix variation cannot
make the install decision stream-dependent: the escape proposed for Part A is inert, and the task
remains the fixed-panel-selection task of S5, with the same easy fast top step.

### Part C: is there a mixture axis the metric does see? (within-class difficulty)

**S9 [PROVEN].** Return to S6's derivation: `recall_c` was independent of `p_c` but explicitly
dependent on WHICH class-`c` rows arrive. If this seed's class-2 rows are drawn mostly from an easy
region (near the class prototype, far from decision boundaries), `recall_c` is high; if mostly from
a hard boundary region, `recall_c` is lower, and lower by different amounts for different panels
(the boundary is resolved by some features and not others). So a per-seed mixture over WITHIN-CLASS
difficulty strata does move balanced accuracy, and can move which panel maximizes it, with the
metric unchanged. This is the one mixture axis balanced accuracy is not blind to.

**S10.** For difficulty mixtures to give the install mechanic a real rung, two conditions must hold:

- **(a) Early inferability from cheap signals.** The hard constraint forbids blind first
  commitments. If the only way to learn that this seed's class-2 rows are the hard kind is to first
  buy the expensive instrument that resolves them, the early install is a gamble, and score
  differences on it are luck. So the free situation signal (`I_wild` plus the cheap terrain tier)
  must correlate with the difficulty stratum well enough to read the mixture off the first tens of
  rows.
- **(b) Portfolio rotation, not escalation.** If "harder rows" only means "need more features
  generally," the same broad panel is best for every difficulty mix and hard mixes just lower every
  score uniformly; the argmax panel never moves and the situation of S8 returns. Rotation requires
  that different difficulty strata are resolved by DIFFERENT instruments: this seed's hard class-2
  rows separated by soil group X, another seed's hard class-5 rows needing soil group Y. That is the
  heterogeneous-relevance structure of sections 17 and 19 reappearing one level down, within
  classes.

**S11 [CONJECTURE].** Does covtype have (a) and (b)? For (b) there is a case each way. For rotation:
soil-type indicators are strongly class-specific (particular soil series co-occur with particular
cover types), so which soil group resolves a boundary can genuinely differ by which classes' hard
rows dominate the seed. Against rotation: Elevation is so dominant an axis that "hard rows" on
covtype may mostly mean "rows in the elevation-overlap band," which want more soil detail generally
rather than a different soil group; if difficulty is one-dimensional, it escalates and the
portfolio never turns over. Which one covtype does is not decidable by argument; it is what the
Part G pre-test measures. Condition (a) is a separate empirical unknown (does the free signal
predict difficulty, not just class) and is measured in the same pre-test.

### Part D: the other repair, keep class mixtures and change the metric

**S12 [ARGUMENT].** S7's arithmetic shows the overall-accuracy optimum flips with the class
mixture. So adopting arrival-weighted (overall) accuracy for this task family makes the per-seed
`theta_s` score-relevant directly: at a site where class 1 floods in, the class-1 panel wins, and a
policy must read the mixture off the free signal before committing its marginal installs. This is
the smallest change that makes the deployment-site framing real and re-opens the door S8 closed.

**S13 [ARGUMENT].** The price of S12, weighed. Cost one: it deviates from the world's standard
metric; overall accuracy on a skewed mixture rewards nailing frequent classes and tolerates
dropping rare ones, a different task from the balanced one the rest of the world grades. Cost two:
it re-opens a known gaming lane, install only the top-two-class panel and ignore minorities; the
per-seed mixtures must reweight minority classes across seeds (the Dirichlet per-class floor) so
that majority-only coverage is punished at some seeds rather than being one dominant easy move.
Benefit: unlike Part C it needs no conjecture about covtype's internal structure; the flip is
guaranteed by arithmetic, and only the SIZE of the induced regret spread remains to be measured.
Relative standing: Part D is the surer repair, Part C is the metric-preserving one. Both feed the
same pre-test (Part G), which measures the one quantity neither argument supplies, the regret
spread.

### Part E: the skill ladder of the full scheme, rung by rung

Each rung gets the two-axis audit (discoverable? fast?) and a judgment on whether adjacent rungs
would separate by more than Delta\*.

**S14 [ARGUMENT], portfolio choice quality.** Candidate behaviors from weak to strong: install the
single dominant instrument and stop; install greedily by unit value; enumerate affordable subsets
(S3); under a repaired scheme (C or D), enumerate per candidate mixture and condition the choice on
the mixture read. Under the unrepaired scheme, S3 showed the top of this rung is easy and fast for
any agent past the engineering climb, so among competent agents this rung is thin, and the spread
it does have is covtype's native fixed-selection spread, not the mechanic's. Under C or D the top
of the rung lengthens into a chain (build the mixture reader, map mixtures to portfolios, condition
the install), which is more insights and more code than one enumeration loop; weak agents
plausibly ship a mixture-blind panel and eat regret at off-distribution seeds. This rung widens
exactly if the pre-test shows wide mixture-conditional regret.

**S15 [ARGUMENT], install timing.** The behaviors: install everything planned at row 0, versus
stage installs as the mixture read firms up. Under balanced accuracy the mixture is irrelevant to
the choice (S8), so waiting buys nothing and costs degraded early rows; "install at row 0" is
dominant, AND it is trivially easy to discover and instant to compute, so by the corrected frame
this dominance claim is a legitimate kill of the rung (both axes low-effort): under the unrepaired
scheme the timing rung is flat. Under C or D, early install risks reading the mixture wrong and
late install wastes degraded rows plus free reads, a real tension with no obvious dominant point;
this is the one genuinely non-dominated tradeoff the scheme offers, and it exists only when the
mixture matters.

**S16 [ARGUMENT], resale usage.** Sell an instrument at the haircut to fund a better one once the
mixture reveals itself. With haircut ~0.4, the refund loss on a resell generally exceeds the
information value of the few rows over which the mixture read updates, so resale-probing (install
to peek, then sell) is dominated, and honest resale pays only in the rare seed where the early read
was badly wrong. A thin rung at best: keep the option, expect little separation from it.

**S17 [PROVEN for free reads; ARGUMENT otherwise], residual per-row game.** If reads are free once
installed, S1 already settled it: read everything installed, predict; that move is trivially easy
and instant, so the rung is legitimately dead, not just dominated-in-principle. If reads are cheap
but nonzero, a per-row subset choice over installed features returns, but section 21's finding
applies: per-row acquisition is memoryless with a single convergent best rule, so this rung is thin
at best. The scheme's value does not live here.

Ladder summary, reading forward from Parts A through D: unrepaired (free reads, balanced accuracy,
class mixtures), the mechanic's own rungs are S14-thin, S15-flat, S16-thin, S17-dead, and
everything that does band is covtype's inherited engineering and fixed-selection spread. Repaired
(C if it rotates, or D), S14 widens and S15 turns on, which is the scheme's whole case.

### Part F: luck, how fast is a mixture read, and what first-pick risk remains

**S18 [ARGUMENT].** The mixture (class mixture under D, difficulty mixture under C) must be read
off the free signal fast enough that few rows are wasted. Rough arithmetic: distinguishing mixtures
whose proportions differ by `delta` takes on the order of `1/delta^2` signal observations. The
Dirichlet seeds impose separations of tens of percent (`delta` ~ 0.2 to 0.3), giving ~15 to 30
rows, consistent with the predecessor memo's ~30-row figure. Over a 2100-row stream that is ~1.5
percent of rows degraded while the read completes. That fraction is the entire luck budget the
mixture machinery introduces.

**S19 [ARGUMENT].** Some install precedes a confident mixture read. This is safe if a near-universal
core exists (elevation plus the cheapest broad soil coverage) that is best-or-near-best under every
candidate mixture, so the first commitment is not a gamble and only the marginal, mixture-specific
install waits for the read. The residual luck is then the variance in exactly when (row 25 versus
row 40) the marginal install fires, times a small per-row score difference over that window: small,
and shrunk further by the 5-seed mean in the seed-blocked analysis. The condition to verify: the
core must be affordable within `P` and genuinely mixture-independent. The predecessor memo's caveat
stands, if the mixture-discriminating signal lives only in thin marginal soil bundles, the core is
thin and the first pick drifts toward a gamble; the pre-test must confirm the core is fat.

### Part G: the pre-test (hosted, no student evals)

**S20, construction, class-mixture variant (for D).** Train ONE masking-robust predictor from peek
(as sections 16 and 19 did). Enumerate every affordable portfolio (a few dozen, per S3). Enumerate
a grid of candidate class mixtures (at minimum the 5 seed mixtures; better, a denser Dirichlet
grid). For each portfolio-mixture pair, simulate the deployment: sample a stream from the peek-known
pool under the mixture, run the free-signal-driven install-then-predict loop with the shared
predictor, score under the candidate metric. Assemble the portfolio-regret matrix, rows =
portfolios, columns = mixtures, entries = score. Kill rule: if some single affordable portfolio
sits within Delta\* of the column-best in EVERY column, mixture never changes the answer, the
install rung is flat, and the variant dies. Survive only if the best portfolio rotates across
columns by more than Delta\*.

**S21, extension, within-class-difficulty variant (for C).** Replace the columns: for each class,
stratify its peek rows by difficulty (distance to the decision boundary under the full-feature
predictor, computed offline), and draw per-seed stratum mixtures. Recompute the matrix over
portfolio-difficulty-mixture pairs, same kill rule: a uniformly near-optimal portfolio means
escalation (S10b fails); rotation beyond Delta\* means the metric-preserving repair works. This
variant also needs the S10a check: regress the difficulty stratum on the free signal (`I_wild` plus
cheap terrain) on peek; if the free signal does not predict difficulty, early installs are blind
and the variant dies regardless of rotation.

**S22, cost and gating.** Both variants are throwaway policies through the real grader via hosted
validation, no student evals spent (heavy compute goes through a throwaway task's validation run
per the compute rules). This instantiates the commit-gate battery (direction doc section 22c): S20
and S21 are the dominance and vacuity probes; the resolution floor is already met by covtype's
populous classes (rarest test class ~270). One addition the bounded-computation correction asks
for: wall-clock the winning probe's build (mixture reader plus conditional enumeration) to confirm
the repaired scheme's top rung is NOT trivially fast, since if it turns out to be minutes of
obvious code, S14's widened rung thins again and the pre-test should say so.

## The result

**FIX-FIRST, gated on the Part G pre-test.** As specified (free reads, balanced accuracy, per-seed
class mixtures) the scheme collapses, and the collapse survives both owner corrections. The chain:
free reads reduce the mechanic to fixed-panel selection [PROVEN, S1]; the best affordable panel is
computable at agent time [PROVEN, S2] AND that computation is a few dozen masked validation passes
behind a textbook enumeration pattern, fast and easy for any agent past the engineering climb
[ARGUMENT, S3], so the precomputability claim here is a legitimate kill ingredient, not a bare
ceiling statement; the rungs below the ceiling are covtype's native engineering and
fixed-selection rungs, which the world grades already without the install mechanic [ARGUMENT,
S4-S5]; and the one proposed way to make the install decision stream-dependent, per-seed class
mixtures, moves nothing because the balanced-accuracy-optimal panel is arrival-mixture-invariant
[PROVEN, S6-S8, worked example S7]. The install economics, as specified, are inert decoration on a
task covtype already poses.

Two repairs are live, each gated on the pre-test:

- **D (surer):** switch this task family to arrival-weighted (overall) accuracy; S7's arithmetic
  guarantees the optimal panel flips with the class mixture, making the install decision genuinely
  stream-dependent. Requires the tight pool (union portfolio unaffordable) and per-seed minority
  reweighting so majority-only coverage is not one dominant easy move [S12-S13].
- **C (metric-preserving, conjectural):** keep balanced accuracy and drive seed variation with
  within-class difficulty mixtures, which the metric does see [PROVEN, S9], betting that covtype's
  soil structure makes the optimal portfolio rotate with difficulty rather than merely escalate,
  and that the free signal predicts difficulty early [CONJECTURE, S10-S11].

**What would flip this to BUILD:** the Part G regret matrix (variant D, or variant C passing both
S21 checks) showing no single affordable portfolio within Delta\* of best across all mixture
columns, i.e. genuine rotation beyond the noise gap; plus a fat, affordable, mixture-independent
core (S19) keeping first-pick luck inside the ~1.5 percent stream-degradation budget (S18); plus
the S22 wall-clock showing the mixture-conditional strategy is not itself a minutes-of-obvious-code
move.

**What would flip this to KILL outright:** a uniformly near-optimal affordable portfolio in BOTH
variants (no rotation under class mixtures with the arrival-weighted metric, and no rotation under
difficulty mixtures), meaning covtype has no heterogeneity the install mechanic can convert into
rungs and the scheme should be dropped rather than repaired.

**Engineering note (not a decision factor, per the owner):** mediated read-metering, an install
pool carried across rows instead of reset per row, resale accounting, and shipping `I_wild` as a
free always-readable tier are all small changes to the existing grader drive loop. Solvable
infrastructure; the verdict turns entirely on Part G.

## Alternatives

Covered inside the process as the two repairs: Part C (within-class difficulty mixtures, metric
unchanged) and Part D (class mixtures, arrival-weighted metric). They are not mutually exclusive;
the recommended path is to run S20 and S21 together and prefer whichever shows rotation, defaulting
to C if both pass, because C preserves the world's standard metric.

## Open questions

1. **Does covtype's difficulty ROTATE or ESCALATE the portfolio?** The single load-bearing unknown
   for the metric-preserving repair (C), resolvable only by S21. If Elevation dominance makes
   difficulty one-dimensional, escalation wins and C dies.
2. **Does the free wilderness signal predict within-class difficulty, or only class?** Condition
   S10a. A cheap peek-time regression answers it; worth its own probe before the full matrix.
3. **Is the near-universal core fat enough under a pool that also forbids the union portfolio?**
   S19's caveat: elevation plus cheap soil must be simultaneously affordable and
   mixture-independent, which depends on the exact `install_cost` and `P` calibration; co-design it
   with Part G.
4. **Under overall accuracy (D), does per-seed minority reweighting actually stop the
   top-two-class move from packing the band?** Needs its own dominance probe: install-the-majority-
   panel versus a mixture-tuned policy across the reweighted seeds.
5. **How slow does the mixture-conditional strategy have to be to hold S14's widened rung?** The
   S22 wall-clock gives the number; if the whole repaired optimum is minutes of textbook code, the
   repair buys less ladder than Parts C and D suggest, and the scheme may need a richer mixture
   space (more instruments, finer groups) to lengthen the insight chain.
