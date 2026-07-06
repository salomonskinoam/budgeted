# 06 Test-time commits with paid revision

## The question

During the graded test stream the policy commits a prediction per row into a ledger, and may later pay
to revise a past row's committed prediction (or re-open a past row to buy more of its features). Does
this mechanic open a multi-rung, resolvable skill ladder that real students of varying strength occupy
at distinguishable scores, or does one easy move sit on top and pack the scores? Two candidate drivers
of honest revision value are examined, both missed by the predecessor memo this file replaces: an
information channel (does the accumulating stream teach the policy anything) and a computation channel
(agents are computationally bounded, so can grade-time compute alone make the late-stream model better
than the early-stream one). And is there any composition (per-seed deployment mixes, or the
label-budget scheme) under which revision becomes load-bearing rather than inert?

## Background (terms defined)

- **Peek data**, train and validation split, features and labels, fully available at agent time. It
  seeds a smart decider. The only permitted ignorance is of the test stream (folder README).
- **Test stream**, the graded sequence of test cases, revealed one row at a time. The policy is driven
  by the grader: per row it acquires features under a budget, then commits a prediction.
- **Per-seed stream composition (mixture)**, the permitted ignorance. Across the 5 grading seeds the
  cases are drawn from the SAME peek population, but their CLASS MIX and ARRIVAL ORDER vary per seed
  (Dirichlet mixes over peek-known cases, direction doc section 22a). Nothing about the generative
  distribution p(x given y) changes across seeds, only the label prior p(y) and the order.
- **Ledger**, the record mapping each past row to its committed prediction and its purchased feature
  set. The final ledger is graded.
- **Paid revision**, an action `{revise, target j, label k'}` that overwrites row j's committed
  prediction, charged a price `c_rev` from the shared pool or a small revision quota.
- **Rebuy / re-open**, an action `{rebuy, target j, feature m}` that buys more of a past row's features
  (paying the feature cost plus a re-opening fee), then allows a revise.
- **Refund**, getting money back for an already-revealed feature value. Analyzed separately (R1).
- **Pool P**, a shared budget balance carried across the stream (the global-budget mechanic, direction
  doc section 21). Revisions and rebuys draw from it.
- **Shadow-price rule**, the peek-calibrated optimal per-row policy under a pool: buy a feature while
  its marginal value exceeds a price calibrated offline from peek. The predecessor's baseline commit.
- **Balanced accuracy (bAcc)**, the covtype metric: mean of per-class recalls, so the score weights
  every class equally regardless of how many of each arrive. Invariant to the arrival mix (direction
  doc section 22b). Covtype test is 300 rows per class, 7 classes, 2100 rows, per-class standard error
  about 0.03.
- **Overall accuracy**, fraction of rows correct, arrival-weighted, NOT invariant to the mix.
- **Prior-shift / label-shift adaptation**, correcting a classifier's decision thresholds to a new
  class prior p(y) estimated from unlabeled data (Saerens expectation-maximization, black-box shift
  estimation). Moves overall accuracy under a shifted mix; moves bAcc by construction ~0.
- **Covariate shift**, p(x given y) differs between train and deployment. Would make a peek-trained
  conditional model miscalibrated. Not permitted here (composition varies, the population does not).
- **Self-training**, retraining on the model's own high-confidence predictions as pseudo-labels.
- **Label-budget scheme**, the sibling scheme the direction doc retains (section 22a): train FEATURES
  visible, train LABELS hidden and purchased per row from ONE global pool; active learning is the task,
  graded on the hidden test.
- **Delta\***, the seed-blocked analysis-of-variance resolution gap (folder README, direction doc
  section 22c). Two scores closer than Delta\* are one level. Levels below it are not levels.
- **Boundary effect**, a contribution to the score confined to a vanishing fraction of rows (for
  example the first k rows of an N-row stream), of order k/N, which shrinks as the stream lengthens.
- **Grade cap**, the platform's total time limit on a grading run (currently 600 seconds). It covers
  everything the shipped policy does at grade time: `Policy(data_dir)` construction (which loads peek
  and trains), plus being driven row by row over the test stream. The cap is total, it does not care
  WHEN inside the run compute is spent.
- **`__init__` / construction time**, the phase before the first test row, where the policy has full
  peek and may train arbitrarily long within the cap. "Front-loading" = spending compute here.
- **Overlap compute**, processor time (CPU, central processing unit) available to a background thread
  of the policy WHILE the grader is driving rows (grader-side loop and inter-process overhead leave
  the policy's CPUs partly idle). This is the one compute front-loading does not reach, because
  spending that wall-clock in `__init__` instead would extend the run toward the cap.

## The process

**R1 [PROVEN], refunds.** A refund returns money for a feature value the policy has already read, and a
revealed value cannot be un-seen. If money comes back while the information is retained, the dominant
move is: buy every feature on every row, read all of it, then refund everything and keep the full
observation for free. That defeats the budget entirely and cannot be implemented honestly. So refunds
are excluded from every variant of this scheme; the predecessor memo's refund finding holds unchanged,
and it is the one part of that memo that is unconditionally correct.

**R2 [ARGUMENT], the scope of the predecessor's pool-fluctuation argument.** The predecessor argued:
the only new information mid-stream is the realized pool balance, of order 1/sqrt(N) in size, whose
content is which cases the seed front-loaded, which is seed luck erased by the seed mean. That claim
is true FOR THE POOL-BALANCE TRIGGER. Revision has other candidate triggers, above all whether the
policy's MODEL can honestly improve as the stream accumulates, and the predecessor never separated
these. Its vacuity claim ("the model is already as good as it will get before row one") presumes every
agent shipped the optimal model, the exact overreach the folder README forbids. So the pool-fluctuation
argument covers exactly one trigger, and the load-bearing question, honest mid-stream model
improvement, is still open at this point in the chain; R3 through R3c take it apart.

**R3 [PROVEN], what the stream tells the policy that peek does not.** Mid-stream the policy observes
purchased feature subsets, its own predictions, and its own confidences. It never observes a label
(labels are grader-only, never transmitted). The purchased feature subsets are a DEGRADED, PARTIAL
resample of a feature distribution peek already provided in FULL and WITH labels. So the one thing the
stream has that peek lacks is the realized mixture p(y) of this seed, nothing else. LIMIT of this
claim: it bounds what the stream TELLS the policy, it does NOT bound how good the policy's model can
become mid-stream. Agents are computationally bounded, and computation generates operational
information: a policy can keep refining its model ON PEEK ALONE during the stream (more boosting
rounds, calibration, ensembling, hyperparameter refinement) with zero new external input. An earlier
draft of this file, and the predecessor memo, conflated these two bounds; R3b and R3c carry the
computation channel separately.

**R3b [ARGUMENT], the computation channel and when compute can be spent.** A weak or rushed agent ships
an under-trained model; extra grade-time compute on peek honestly improves it, so its late-stream model
can genuinely beat its early-stream model, and revision could cash that on early rows. But the grade
cap is total and indifferent to WHEN compute is spent: any cycles spendable mid-stream are spendable in
`__init__` BEFORE the first commit. Front-loading the same compute yields the same final model while
improving EVERY commitment (not only the early rows one later pays `c_rev` to fix) and paying zero
revision fees. So train-later-and-revise is weakly dominated by train-in-`__init__`-and-never-revise,
as a property of the cap's structure, not of agent strength, with a single exception: overlap compute
(Background). Idle processor time during grader-driven rows is reachable only by a background trainer
running mid-stream, and a policy using it plus revision is not dominated by any front-loader. The
computation channel therefore reduces to one question: how much is overlap compute worth?

**R3c [ARGUMENT], sizing the overlap-compute exception (order arithmetic, not simulation).** On the 16
virtual-CPU grading machine a gradient-boosted tree on covtype-scale peek (tens of thousands of rows,
54 features) trains to near-convergence in tens of seconds. The 600 second cap, minus driving 2100
rows across 5 seeded passes (mostly grader-side overhead), leaves `__init__` headroom of minutes,
comfortably enough to converge the model class that wins on this data. The model a competent `__init__`
ships is therefore already near the compute-asymptote, and what overlap compute adds beyond it (more
rounds on a converged learner, marginal ensembling) is order 0.005 to 0.02 balanced accuracy, at or
below Delta\* (per-class standard error is about 0.03 on 300-per-class), and revision only cashes a
FRACTION of that sliver (the early rows), minus revision fees. A second, independent consideration:
building a thread-safe background trainer plus ledger-revision economics is strictly harder engineering
than training a fast learner to convergence in `__init__` (the textbook move). Agents capable of the
machinery are exactly those whose `__init__` model is already converged and who gain nothing from it;
agents whose models are under-trained do not build background trainers. Conclusion: the
compute-revision rung is both thinner than the resolution gap and without natural occupants (the
anti-correlated-rung case, file 00 open question 2).

**R4 [ARGUMENT], both channels on the base data and metric.** Information channel: the only novel
external signal is the mixture (R3), and balanced accuracy is invariant to the mixture (direction doc
section 22b), so mixture-driven moves (recalibrate thresholds to the realized prior, self-train, detect
the mix) buy nothing. Computation channel: front-loading dominates everything except overlap compute
(R3b), and the overlap sliver is at or below Delta\* with no natural occupants (R3c). Estimated
magnitude of honest mid-stream improvement on covtype-scale streams (2100 rows, purchased subsets
only): ~0 for bAcc from information, a sub-Delta\* sliver from computation. This reaches the
predecessor's conclusion for defensible reasons: not "the model is already optimal for all agents"
(false for bounded agents of varying strength), but "the stream's only external signal is
metric-neutralized, and the compute path to a better late model is dominated by spending the same
compute before the first commit."

**R5 [ARGUMENT], where the weak-agent rung is graded.** A weak agent's shipped model is genuinely
suboptimal; that is a real ladder rung (folder README), and the predecessor erased it by assuming
strength. But the fix for that rung lives at agent time (use peek better in the shipped code) or in
grade-time `__init__` (train longer before the stream, R3b), both of which precede the first
commitment. Data-wise the mid-stream agent has strictly less than peek (R3); compute-wise everything
but the overlap sliver is front-loadable (R3b, R3c). So the rung ("train a stronger partial-observation
predictor, and give it its compute before the stream") is already graded by plain per-row play, and the
revision mechanic adds nothing to it. Both missed angles are real as rungs; neither is a rung that
revision grades.

**R6 [ARGUMENT], the time-shape of revision value.** Suppose the late model IS better than the early
one. Only the rows committed BEFORE the model converged can be improved by revising them, and a model
that improves at all converges within the first stretch of the stream, so the improvable fraction is of
order k/N and shrinks as N grows; on the base scheme k is ~0 (R4). Even where mid-stream improvement is
real but fast, revision cashes only the early tail, while the free alternative (defer, do not commit
early) captures all of it. Revision is therefore structurally a boundary mechanic unless the model
keeps improving across the WHOLE stream. Two things satisfy that whole-stream condition: a background
trainer on overlap compute, whose total height R3c caps at a sub-Delta\* sliver, and bought labels,
which R9 to R11 analyze.

**R7 [ARGUMENT], the candidate optima and their discoverability.** Two candidate optima exist: (a)
commit correctly once and never revise (optimal when nothing improves later, the base case), and (b)
lazy-commit cheap then revise everything late with the best model (optimal when the late model is
better). Both are SINGLE moves, and both are EASY to discover ("get it right the first time" and
"wait, then fix it at the end" are the two obvious ideas). The `c_rev` knob does not open a multi-rung
interior between them, it interpolates between two collapse endpoints: raise `c_rev` and mass
end-revision becomes uneconomic, pushing everyone to (a); lower it and everyone reaches (b). File 00's
rule is that a dominance argument is a legitimate falsifier only when the dominant move is also easy;
here the dominant move is easy at BOTH endpoints, so the base scheme meets that condition.

**R8 [ARGUMENT], the combined chain for the base scheme.** On covtype with balanced accuracy and the
base data: the stream's only external signal is the mixture and the metric neutralizes it (R3, R4);
the computation channel exists but front-loading dominates it and its non-front-loadable remainder is
a sub-Delta\* sliver with no occupants (R3b, R3c); revision value is a vanishing boundary effect (R6);
and the two optima are easy single moves (R7). Every place a rung could stand is either flat, below
resolution, or unoccupied, so the base scheme's scores pack. The predecessor's conclusion is reached
again, now on corrected reasoning. Tag note: this step is [ARGUMENT], not [PROVEN], because the chain
contains the R3c order-arithmetic and the R3b dominance claim, which are heuristic, not reductions.

**R9 [ARGUMENT], what could make the late model materially better.** The scheme presupposes a late
model materially better than the early one. By R3 no unsupervised signal supplies that (peek already
dominates the unlabeled stream), and by R3b and R3c the computation channel is front-loadable down to
a sub-resolution sliver. What remains is a supervised signal peek lacks: a LABEL arriving mid-stream
that peek did not contain. The label-budget scheme (Background; direction doc section 22a) supplies
exactly that: it hides the train labels and sells them from a pool. Compose it at test time, one shared
pool funds BOTH buying labels (which improve the model) AND revising past predictions. Then the late
model is genuinely better than the early one, because it was trained on labels bought after the early
rows were committed. The coupling premise is satisfied for real, not assumed.

**R10 [ARGUMENT], revision value under the label-budget pairing.** The model improves across the WHOLE
stream as labels are bought (the learning curve from tens to hundreds of covtype labels is steep and
does not saturate within 2100 rows). So every early row was committed by a materially worse model, and
revising the early rows cashes the integral of the learning curve over the stream, not a shrinking tail
(contrast R6). Two agents that both buy labels online, one that never revises versus one that
re-predicts all past rows with the final model, differ by exactly that integral. This is the first form
in which revision does something plain per-row play does not.

**R11 [ARGUMENT], the tradeoff the pairing opens.** One pool funds two competing uses: more labels (a
better model, helping future rows and, via revision, past ones) versus spending on revisions (cashing
the current better model onto already-committed rows). There is no single best split:
spend-early-on-labels versus hold-reserve-to-revise versus adaptive-threshold schedules are distinct
policies with no dominant rule, which is the non-dominated rationing space the direction doc has been
chasing (section 21). This is the strongest form of the scheme, and the pairing intuition (buy labels
AND revise past predictions from one shared pool) is the correct one.

**R12 [CONJECTURE], what the pairing inherits and what it needs.** (a) It inherits the label-budget
scheme's own active-learning falsifier: random sampling is a strong baseline on covtype-like data, so
canonical acquisition strategies have to separate by more than seed noise or there is no band from the
label half either (direction doc section 22a). (b) It needs a NEW anti-batch forcing so it does not
collapse to offline batch active learning: mandatory per-row commit at arrival (a prediction may not
be deferred), plus a revision window or a rising revision price, so "buy all labels first, then predict
everything once at the end" is not available. Without the forcing, the dominant move is the batch
optimum (buy the best labels, predict everything at stream end), which erases the online structure and
makes revision unnecessary, exactly R7 endpoint (b) again. Both parts are pre-test conjectures, not
established facts, hence the tag.

**R13 [ARGUMENT], residual luck under the pairing.** The seed-blocked analysis of variance absorbs seed
MAIN effects (a seed that front-loads hard cases shifts every agent's score equally). The residual luck
is the INTERACTION: which labels a seed's early stream lets you buy. A seed that front-loads rare or
informative rows steepens the early learning curve and differentially rewards aggressive early
label-buying, an effect not absorbed by seed main effects. This is genuine residual luck that can
inflate apparent levels. It is bounded by a free situation signal that pins the mixture fast (direction
doc section 22a) and is exactly what commit-gate 3 (skill-identical replicates resolving to one level,
direction doc section 22c) is designed to catch. It is non-trivial for the pairing and has to be
measured, not argued away.

**R14 [ARGUMENT], ledger gaming and the knobs that close it.** Refunds are excluded (R1). Mass-revise
at stream end when the pool is known: closed by a rising revision price, a closed end-of-stream window
(no revision in the last k rows, or revision only within w rows of the original commit), or by drawing
revision from the SAME pool as label-buying so end-mass-revision has real opportunity cost against a
better model. Batch-optimize everything at the end, erasing the online structure: closed by mandatory
per-row commit at arrival plus the revision window (R12). Pool exposure has to avoid reflecting
correctness back to the policy (the running balance encodes cost spent, never whether a past prediction
was right), or it leaks labels. Every identified exploit has a known closing knob.

## The result

**KILL as a standalone scheme; SURVIVES only as a fix-first MODIFIER on the label-budget scheme.**

Standalone paid revision on covtype under balanced accuracy is dead (R8). The predecessor's KILL is
upheld, but its stated reason (the model is already optimal before row one) is wrong twice over: false
for varying-strength agents, and false for computationally bounded ones (grade-time compute can
honestly improve a shipped model with zero new information). It is replaced by a three-part argument:
the stream's only EXTERNAL signal is the mixture and the metric neutralizes it (R3, R4); the
COMPUTATION channel is real but the grade cap is indifferent to when compute is spent, so front-loading
`__init__` weakly dominates train-later-and-revise, and the non-front-loadable remainder (overlap
compute) is a sub-Delta\* sliver whose exploiting machinery is harder than the move that makes it
worthless (R3b, R3c); the weak-agent improvement rung lands before the first commit, where plain
per-row play already grades it (R5); revision value is a vanishing boundary effect (R6); and the two
optima are easy single moves so the ladder is flat (R7).

The one live form is the label-budget pairing: one shared pool funds both buying labels and revising
past predictions (R9). There, and only there, the late model is honestly better than the early one, so
revision cashes a non-vanishing learning-curve integral (R10) and a genuine labels-versus-revision
rationing tradeoff with no dominant rule appears (R11). It is not a standalone build: it inherits the
label-budget active-learning falsifier and needs anti-batch forcing (mandatory arrival-time commit plus
a revision window or rising price), and it carries a seed-by-strategy luck residual that has to be
bounded (R12, R13, R14). Route it as a modifier on the surviving label-budget scheme, gated on both
batteries, never as its own scheme.

**What would flip the standalone KILL.** A probe ladder on covtype under an ARRIVAL-WEIGHTED metric
(overall accuracy) with per-seed mixtures in which a stream-aware revising probe beats a
precomputed-schedule probe by more than Delta\* (commit-gate 1), AND a richer reviser beats the easy
commit-once baseline by more than Delta\* (commit-gate 2), with skill-identical replicates resolving to
one level (commit-gate 3). If the mixture-adaptation value under overall accuracy turned out both large
and hard to capture, the flat-ladder claim (R7) would fail. Current expectation (R6): under overall
accuracy the prior-shift correction is real but easy and pinned within about 30 to 100 rows, so
revision cashes it only on a boundary fraction and the probe gap stays below Delta\*.

Two further flips, both on the computation channel (R3b, R3c): (a) a measurement showing overlap
compute is LARGE on the real mediated grader (driving dominated by grader-side wall-clock, leaving the
policy's CPUs idle for most of the run) AND the winning model class on the data is genuinely
compute-starved at `__init__` (its learning curve still climbing when the stream must start), which
together would make mid-stream improvement a necessity rather than a scheduling choice; (b) a probe
showing a background-trainer-plus-reviser beating the best front-loaded never-reviser by more than
Delta\*. On covtype with gradient-boosted trees, (a) fails at the second conjunct (tens of seconds to
converge against minutes of headroom), which is why R3c stands; on a heavier data or model regime it
has to be re-checked, not assumed. Note the constraint: compute starvation may only ever come from data
and model scale, never from a grader-side watchdog under the platform cap (the cap is the platform's,
we never undercut it), and a run graded near the cap makes machine-load variance a score noise that
seeds do not block (the same environment-noise failure that killed checkpoint grading in the agent-time
scheme).

**What would flip the pairing to a build.** The pairing passing all five commit-gates (direction doc
section 22c) on covtype: the active-learning probes separating (random sampling NOT tying canonical
acquisition), the online-revising probe beating both the never-revise and the batch-at-end probes by
more than Delta\*, and gate 3 resolving skill-identical replicates to one level despite the R13
interaction.

## Alternatives (the pairing is the main one; three framings weaker)

- **Label-budget pairing (primary, R9 to R11).** Buy labels and revise past predictions from one pool,
  with mandatory arrival-time commit and a revision window. This is the strongest form and the only one
  where revision is load-bearing. Analyzed above; fix-first, double-gated.
- **Per-seed deployment mixtures plus overall accuracy (weaker).** Drop balanced accuracy for an
  arrival-weighted metric and vary the class mix per seed (the instrument-installation escape,
  direction doc section 22a). Then adapting to the realized prior helps the score, and revising early
  rows cashes it. But the adaptation is a textbook prior-shift correction (Saerens
  expectation-maximization), easy and pinned in tens of rows, so it is one easy rung and revision
  cashes it only on a boundary fraction (R6). Likely fails commit-gate 2. Kept only as the metric fix
  that makes the mixture visible; insufficient on its own.
- **Compute-starved regime (untested, constrained).** Pick data and a winning model class whose
  learning curve genuinely does not converge inside the `__init__` headroom the platform cap leaves,
  so a background trainer on overlap compute plus revision of early rows becomes a necessity, not a
  scheduling choice (the R3b dominance breaks by construction). Three hard caveats: starvation has to
  come from data and model scale only, never a grader-side watchdog (the platform cap is not ours to
  undercut); runs graded near the cap turn machine-load variance into score noise that seeds do not
  block; and the easy escape "ship a smaller, faster-converging model" may itself be the dominant easy
  move, re-flattening the ladder. Not pursued unless the overlap-compute measurement (open question 4)
  comes back large.
- **Rebuy / re-open past rows (weakest).** Re-opening a past row to buy more of its features, paying
  cost plus a re-opening fee, is just deferred per-row acquisition with a surcharge. Under the base
  data it inherits R3 to R7 unchanged (the extra features were buyable on that row when it arrived;
  buying them later at a premium is strictly worse). No independent value; drop it unless paired as in
  R9, where its only role is to let a newly informative feature be added to an early row after labels
  improved the model, a second-order effect on top of R10.

## Open questions (each worth a dedicated chat)

1. **Does the label-budget pairing actually pass its own active-learning falsifier on covtype?** The
   whole pairing rests on the label half banding. If random sampling ties canonical acquisition on
   covtype (a real risk, direction doc section 22a), revision has nothing to cash and the pairing dies
   with the label scheme. This has to be settled first, before any revision machinery.
2. **What revision-window width and price schedule maximize the labels-versus-revision non-dominance
   (R11) without reopening the batch-at-end exploit (R12)?** Too wide a window or too cheap a price
   restores the offline batch optimum; too narrow and revision becomes inert. There is a design
   interior to be found, and whether it is nonempty is a pre-test, not an argument.
3. **How large is the R13 seed-by-strategy interaction on covtype-scale streams, and does the free
   situation signal shrink it below Delta\*?** If which labels the seed front-loads differentially
   rewards a strategy by more than Delta\*, the levels are manufactured luck (commit-gate 3), and the
   pairing fails for the same reason instrument installation nearly did.
4. **How much overlap compute does the real mediated grader actually leave?** The R3c arithmetic
   assumes driving 2100 rows across 5 passes is mostly grader-side wall-clock with the policy's CPUs
   near idle, and that `__init__` headroom is minutes. Both are one cheap instrumented hosted
   validation run away (log processor utilization of the policy subprocess during driving, and
   wall-clock of each phase). If overlap compute comes back as a large fraction of the cap AND a
   realistic model class is still climbing at stream start, the compute-starved alternative stops
   being hypothetical and the R3b dominance needs the probe test, not the argument.
