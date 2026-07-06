# 03 - Train-label budget (active learning as the task)

## The question

Ship the student the training FEATURES fully visible but hide the training LABELS. The student can
BUY labels one row at a time (or in batches) from a single shared label budget, through a mediated
reveal loop the grader drives. Whatever model the purchased labels produce is then graded on a hidden
test split. This is the classic active-learning setting turned into the task itself. Does it band, and
how? Concretely the owner asked seven things, answered in The process below: (1) is buying labels
one-by-one workably fast; (2) what the five evaluation seeds vary and whether the levels statistic
stays honest; (3) what the skill ladder looks like rung by rung and which real agents reach which rung;
(4) how it resists gaming; (5) whether covtype supplies the data structure active learning needs, with
alternatives; (6) the exact pre-test; (7) whether the "commit" framing is load-bearing or window
dressing.

## Background (terms defined)

- **The student.** An LLM coding agent. It writes a Python file (`solution.py`) defining a class. It
  never predicts by hand; its code trains a model and the model predicts. The graded artifact is the
  code plus the model that code produces.
- **Agent time (the session)** is the period the student works before shipping its artifact. **Grade
  time** is when the grader runs and drives the shipped artifact; grade-time compute is bounded only by
  the platform's time cap (currently 600 seconds).
- **Bounded agent** (file 00). An agent whose decision quality at any moment is a function of the
  compute it has ALREADY SPENT, not only of the data available to it. Computation generates
  information; "could have computed X" does not mean "would have computed X by then." Every rung
  judgment below therefore carries two effort axes: discoverability (insight) and compute cost.
- **Front-loading** (file 06 step R3b; direction doc section 22b). The grade cap is total and
  indifferent to WHEN compute is spent, so any grade-time work that needs only compute plus
  already-visible data can be moved into the artifact's construction phase (`__init__`), before any
  interaction begins. Mid-stream improvements that need only compute are therefore dominated by doing
  the same work up front. The only things front-loading does not reach are resources REVEALED
  mid-session.
- **Precomputed schedule versus stream-aware policy** (direction doc section 22c, gate 1). A
  precomputed schedule fixes all its decisions from data visible before the session; a stream-aware
  policy conditions decisions on what the session reveals. A scheme has real temporal structure only
  where stream-aware beats precomputed by more than noise.
- **Active learning.** The machine-learning subfield about choosing WHICH examples to get labeled when
  labels are scarce or expensive. You start with a large **pool** of unlabeled rows (features only), a
  **label budget** (how many labels you may buy), and an **acquisition rule** that picks which rows to
  label next. You label the picks, retrain, and repeat. The bet is that a good acquisition rule reaches
  higher accuracy per label than labeling random rows. Everything below is standard active-learning
  vocabulary.
- **Acquisition rule / query strategy.** The function that, given the current model and the pool, ranks
  unlabeled rows by "how much would labeling this help." The rungs of the skill ladder are different
  acquisition rules.
- **Uncertainty sampling.** Label the rows the current model is least sure about. "Least confident" =
  lowest top-class probability; **margin** = smallest gap between the top two class probabilities;
  **entropy** = highest predictive entropy over classes. All three are one-liners over the model's
  class-probability output.
- **Calibration.** Adjusting a model's probability outputs so a claimed 0.7 really means right 70% of
  the time (for example temperature scaling or Platt scaling). Uncertainty rules only mean something on
  calibrated probabilities.
- **Diversity / coreset sampling.** Ignore uncertainty; instead pick rows that COVER the feature space,
  so the labeled set is spread out rather than clustered. The **k-center-greedy coreset** (Sener and
  Savarese 2018) repeatedly picks the pool row farthest from everything already labeled. It consults
  features only, never labels or a model.
- **Hybrid (uncertainty + diversity).** Combine "the model is unsure here" with "and this row is not
  redundant with what I already picked." **BADGE** (Batch Active learning by Diverse Gradient
  Embeddings; Ash et al. 2020) is the canonical batch version: it embeds each row by its loss gradient
  (magnitude encodes uncertainty, direction encodes what part of the model it would move) and picks a
  diverse batch by k-means++ over those embeddings, so a batch of queries does not pile onto one
  confusing cluster.
- **Batch active learning.** Buying labels B rows at a time and retraining once per batch, instead of
  one row at a time. Fewer retrains, but the whole batch is chosen against a stale model, so the batch
  must actively avoid buying near-duplicates.
- **Cold start.** The pathology where, early on, the model is so bad that its uncertainty estimates are
  noise, so uncertainty sampling chases garbage and can LOSE to plain random sampling until enough
  labels accumulate. Well documented on large redundant data.
- **Budget scheduling.** How to spread the budget over the session: spend little early (when the model
  is a poor judge of what it does not know) and more late, or the reverse; and whether to STOP early
  when extra labels stop moving the model.
- **Semi-supervised add-ons.** Use the UNpurchased rows too: **self-training** (label them with the
  current model's confident guesses and train on those pseudo-labels) and **label propagation** (spread
  labels along the feature-space graph from bought rows to their unbought neighbors).
- **Balanced accuracy.** Mean per-class recall (each class weighted equally regardless of frequency).
  The metric this world grades on. Its resolution is capped by the RAREST class (a k-example class has
  recall standard error about sqrt(p(1-p)/k)).
- **The seed-blocked levels statistic.** Evaluation reruns the shipped policy under five fixed seeds.
  Score = mean over seeds. **Levels** = the number of statistically distinguishable score tiers,
  counted by an analysis of variance that BLOCKS on seed (treats the seed as a paired factor so the
  same seed's noise cancels when comparing two policies). The resolution gap is
  **Delta\*** = t-threshold x pooled residual standard deviation x sqrt(2 / S) with S seeds. Two
  policies are one level apart only if their mean gap exceeds Delta\*. Levels are the product; spread
  without levels is a weak task.
- **The existing mediated world.** `worlds/budgeted/verify.py` spawns the student policy as a
  sandboxed subprocess (dropped to the `model` user, no `/data_root` access) and drives a per-row
  select/reveal loop over line-JSON (one JSON object per line on the standard input/output pipe),
  enforcing a per-CASE feature budget and revealing only requested feature VALUES. This scheme
  retargets that machinery from "reveal a feature value at test time" to "reveal a label at training
  time."
- **DataView.** `worlds/budgeted/data_view.py`: config-driven, hosted transforms applied at setup time
  (drop features, override costs, `test_per_class` to balance the test split). A reshape is a config
  change plus a re-push, never a local data rebuild.
- **Covtype.** The Forest CoverType dataset: real, 7-class, about 130k usable rows after our
  subsample, natively imbalanced (two forest types dominate; Cottonwood/Willow is rare). The dataset
  on which the current per-row feature-acquisition task banded (0.675 to 0.848, about 3 levels).

## The process

**P1 [PROVEN].** The mechanism: `/data_agent` exposes the full train and validation FEATURE matrices
unlabeled plus meta (the label budget L); `/data_root` holds the train labels and the whole test
split. The student ships a Learner whose grade-time session is `select_queries(labeled_so_far,
budget_left) -> row_ids`; the grader reveals those rows' labels while the pool has budget, the student
calls `fit()`, and this repeats until the pool is exhausted or the student stops. The grader then
hands over the test FEATURES (features are not secret, only labels are) and reads back all test
predictions in one batched `predict()` call. A full grade is therefore ONE active-learning session
plus ONE batched test prediction per seed: the query loop runs at grade time, driven by the grader,
fresh per seed, once per seed rather than once per test row (part of owner question 1).

**P2 [PROVEN].** A line-JSON round trip over the stdin/stdout pipe costs microseconds; the current
world already runs thousands of them per grade without noticing. The only expensive operation in the
loop is the student REFITTING its model between queries. Buying labels one-by-one is therefore fast
on the wire, and "one by one is slow" holds only if the student also refits after every single label,
which is a strategy choice, not a protocol cost (rest of owner question 1).

**P3 [ARGUMENT].** Given P2, the protocol should expose refit frequency as strategy rather than fix
it. Propose a round-based reveal loop: each round the policy returns a LIST of row indices (a batch),
the grader returns that batch's labels (as many as the remaining pool covers), the policy refits or
does not, and asks again, until the pool is empty or the policy stops. Under that protocol:
- **Protocol-enforced (not the student's choice):** total labels revealed never exceeds L; the reveal
  returns labels ONLY for the requested, not-yet-bought rows and returns `min(requested, pool_left)`;
  a re-requested row is free (already owned) but buys nothing new; nothing but the label values rides
  back.
- **Strategy (the student's choice, part of the ladder):** the batch SIZE (large = fewer refits but a
  stale model chooses the whole batch; small = maximally adaptive but many refits), WHETHER to refit
  between rounds, the acquisition rule, and whether to stop early.
A fixed round structure (a mandatory K rounds of L/K each) is the safer fallback if smoke runs show
weak agents hanging on size-1 refit loops: it caps refits at K while leaving the acquisition rule as
the graded axis. Recommendation: leave batch size free but hint a sane default. The platform grade
cap stays the only timeout (per `CLAUDE.md`); a policy that refits itself past the cap is killed by
it and scores low, which is correct.

**P4 [ARGUMENT].** The current covtype task had to shrink its test split to 300 rows per class
(`test_per_class`) because the grader drives every test row one-at-a-time and 56k rows blew the 600s
cap. Under P1 the test pass is a single batched `predict()`, so the test split can be LARGE again,
and since levels are capped by the rarest class (direction doc section 18), a larger rarest class
lowers the noise floor. This scheme is therefore both cheaper to grade and higher-resolution than the
world already built.

**P5 [ARGUMENT].** The unlabeled pool is fixed and fully visible from the start, so unlike the
feature-acquisition world there is no "which cases arrive, in what order" axis for the seed to vary.
What remains for the seed: (a) the **test-split draw** (resample the graded test rows from a held-out
test pool per seed); (b) the seed handed to the student's own **stochastic training** (model
initialization, subsampling, tree-library `random_state`); (c) **tie-breaks** in acquisition (random
sampling consumes it directly; uncertainty ties break with it). Those three are the candidate seed
axes (owner question 2, first half).

**P6 [ARGUMENT].** The seed-blocked analysis of variance needs real within-run noise: it pools each
policy's variance across its five seed replicates as the residual, and calls two policies
distinguishable only when their gap beats that residual. If the only thing a seed changed were the
student's internal random number generator, a student that fixes its own seed would contribute zero
within-run variance, shrink the pooled residual, and manufacture false levels. Resampling the test
split per seed gives EVERY policy, deterministic or not, a nonzero within-run variance equal to
finite-test sampling error, which is real deployment noise and is correctly capped by the rarest
class. The five seeds are fixed and shared across policies, so policy A and policy B both see
test-draw number 3, preserving the paired `predictions_b64` comparison the grading toolkit's
rank-resolution test uses. The student-training seed layers on top as additional honest noise (a
deployed learner really is retrained with fresh randomness). So the test-split draw should be the
PRIMARY seed axis, and with it the levels statistic gets honest within-run noise (owner question 2,
second half).

**P7 [PROVEN].** Apply the bounded-computation correction (file 00 step R3; file 06 step R3b;
direction doc section 22b): grade-time compute is time-fungible, so anything a policy could do
mid-session with compute plus already-visible data is dominated by doing it in `__init__` before the
session starts. Now ask what in THIS scheme is reachable that way. The train labels live in
`/data_root` (700, invisible to the sandboxed `model` user), and the metered reveal is the only
channel through which a true label value ever reaches the student; front-loaded compute on the
agent-visible data yields only ESTIMATES of a label, and the quality of those estimates is exactly
the model quality being graded. Purchased labels are therefore precisely the mid-session resource
that front-loading cannot reach (section 22b names them as the example), so the policy's information
state genuinely grows during the session through spending, not computing. This is the sharpest
statement of what separates this scheme from compute-only schemes, where file 06's front-loading
argument collapses mid-stream adaptation into `__init__`: here the session's temporal structure is
anchored to an irreversible resource, not to compute.

**P8 [ARGUMENT].** The same correction cuts the other way, and honesty requires saying so. A
label-FREE acquisition schedule (coreset over the visible features, or any fixed ordering) is a pure
function of peek data, so it is fully front-loadable, all the way back to AGENT time: the student can
compute the entire purchase order during the session with its own compute and ship it as a literal
list of row indices. That is legitimate strategy, not gaming (no hidden information is touched). It
means the scheme's temporal structure is real ONLY for rules that condition on purchased labels, and
the pre-test must therefore include the stream-information gate (direction doc section 22c, gate 1)
instantiated as: best label-ADAPTIVE rule versus best PRECOMPUTED label-free schedule. If no adaptive
rule beats the best precomputed schedule by more than Delta\*, every purchase decision is
front-loadable and the reveal loop is decoration.

**P9 [ARGUMENT].** The ladder, lower half, each rung carrying BOTH effort axes (file 00 step R8):
discoverability (who finds it) and grade-time compute cost (who finishes it under the cap).
Magnitudes on covtype-scale data (7 classes, roughly 130k-row pool, native imbalance) are
[CONJECTURE] until the pre-test; the ordering and effort judgments are the argument.
- **(a) Broken loop.** Buys zero labels, mishandles the protocol, predicts a constant, or refits per
  single label with a slow learner and dies at the cap (at seconds per refit, thousands of refits do
  not fit in 600s, so size-1 batching with a tree learner is not merely inelegant but infeasible;
  this rung is partly a bounded-COMPUTE rung, not only a bounded-insight one). Score at or below
  chance balanced accuracy (about 1/7 = 0.14). Weak agents land here, and this floor tier separates
  agents who can drive the protocol at all.
- **(b) Random sampling.** Buy L uniformly random rows, fit once or in a few batches. Trivial to
  discover, trivial to compute, so nearly every agent reaches it; on large redundant tabular data it
  is a notoriously strong baseline. It is the reference rung.
- **(c) Uncertainty sampling (least-confident).** Fit on a small seed set, buy the rows the model is
  least sure about, refit, repeat. Discoverable by mid-strength agents (it is the first thing any
  agent that has heard "active learning" writes); compute is modest at sane batch sizes. Here sits
  the known pitfall: with a cold start on a large redundant pool, least-confident sampling chases the
  early model's noise and can UNDERPERFORM random until labels accumulate. For this task that pitfall
  is a feature: a naive uncertainty sampler landing below random creates a genuine rung between (a)
  and (b), widening the ladder. A mid agent that reaches for the obvious rule and gets burned is a
  distinguishable, honest tier.
- **(d) Margin / entropy with calibration.** Swap least-confident for margin or entropy and calibrate
  the probabilities. Discoverable by strong agents; compute near (c). Better behaved than
  least-confident, partly dodges the cold start; whether it clears Delta\* over random is an open
  magnitude question for the pre-test.

**P10 [ARGUMENT].** The ladder, upper half:
- **(e) Diversity / coreset sampling.** k-center-greedy over the visible features. Discoverable by
  strong agents. Compute: each pick scans pool distances, feasible at covtype scale for a few hundred
  picks, and per P8 the whole schedule is front-loadable into `__init__` or agent time, so its
  grade-time cost is near zero for an agent that notices that. It consults no model, so early-model
  noise has no channel to mislead it (the cold-start cure), and on an imbalanced pool it should cover
  rare-class regions that uniform sampling starves.
- **(f) Hybrid uncertainty plus diversity with batch de-duplication (BADGE-style).** Pick batches
  that are both uncertain and mutually diverse, so a batch does not dogpile one confusing cluster.
  Discoverable by strong agents only, and its compute is the heaviest on the ladder: per-round
  gradient embeddings plus k-means++ over a 100k-plus-row pool needs subsampling or careful
  engineering to fit the cap. High on both effort axes at once, which is what keeps it a rung rather
  than a freebie. The literature treats it as the robust cross-dataset winner; expected top of the
  deployable ladder.
- **(g) Budget scheduling.** Decide the SPEND CURVE: sparse early while the model is a poor judge of
  its own ignorance, dense once it is not, and stop early when marginal labels stop moving validation
  balanced accuracy. Cheap to compute, hard to discover and tune; per P7 the schedule is a genuine
  planning-under-scarcity decision, because early spend shapes the model that chooses later spend and
  no textbook gives the dominant curve. This is where strong agents most plausibly separate from each
  other.
- **(h) Semi-supervised add-ons.** Self-train on confident unbought rows, or propagate labels along
  the feature graph, stretching each purchased label further. Discoverable by strong agents; compute
  moderate (a propagation pass over the pool). Double-edged by nature: on clean well-separated
  regions it lifts balanced accuracy for free; under label noise or class overlap it amplifies errors
  and hurts. That two-sidedness is additional spread among strong agents, and per P7 it is also the
  honest "estimate substitute" for the non-front-loadable resource: how far estimates substitute for
  purchases is itself graded.

**P11 [ARGUMENT].** Assembling P9 and P10: the baseline (random) sits in the MIDDLE of this ladder,
with a floor rung and a cold-start rung below it and coreset, hybrid, scheduling, and semi-supervised
rungs above it, and the rungs differ on discoverability, on grade-time compute, or on both. The
active-learning literature's central empirical fact, that no acquisition rule dominates across
datasets and budgets, is the structural reason the upper rungs do not collapse onto one move. A
ladder with a strong baseline in the middle and effortful rungs on both sides is the shape that
banded on covtype in the feature world (folder README; file 00 step R4). This answers owner
question 3.

**P12 [PROVEN].** Gaming, the reveal channel: labels sit in `/data_root` (700), unreadable by the
sandboxed `model` user; the metered reveal returns `min(requested, pool_left)` labels for the
requested rows and nothing else, no index hints, no counts, no ordering side-channel. The student
cannot read the label store, cannot exceed L, and cannot learn a label it did not pay for. This is
the same isolation the current world already enforces for feature values (owner question 4, first
part).

**P13 [ARGUMENT].** Gaming, across seeds: if any written file carried purchased labels from one
seed's run to the next, a student could buy a disjoint L each seed and union them, defeating the
budget five-fold. Decision: each of the five evaluation runs is a fresh container and process, label
state is NOT shared across seeds, and labels are RE-PURCHASED each seed. That makes L a true
per-session cap and each seed an honest independent replicate, which the seed-blocked variance needs
anyway. The pool of candidate rows is identical each seed (features are fixed and public); only the
purchase ledger resets.

**P14 [PROVEN].** Gaming, distillation: the training-run-quota variant (direction doc section 22a)
was gameable because an auxiliary scoring endpoint returned predictions the student could distill
from, laundering the quota. This scheme has no such endpoint. The reveal returns only labels
explicitly bought from L, and the TEST labels never leave the grader at all (the grader computes the
score itself). There is nothing to distill: the metered resource is the labels themselves, and the
graded quantity never crosses the boundary. One adjacent guard: the meta shipped to the student must
not leak label information through summary statistics (no per-row or per-class label frequencies);
ship only the feature matrices and the budget (owner question 4, rest).

**P15 [ARGUMENT].** For acquisition rules to SEPARATE, the pool must punish uniform labeling. The
properties that do that: (a) **class imbalance with rare classes**, which random sampling starves in
proportion to their rarity while coreset or uncertainty rules seek them out, and balanced accuracy
weights exactly those classes up; (b) **many classes**, a long decision boundary where label
placement matters; (c) **heterogeneous density**, dense redundant regions where labels are wasted
next to sparse informative ones; (d) **label noise**, separating rules that over-trust uncertainty
from rules that hedge with diversity; (e) **non-uniform label costs** (some rows or classes need an
expensive expert label, others a cheap crowd label), which would turn cost-per-label into a SECOND
commit axis. Under balanced accuracy, (a) is the strongest lever.

**P16 [ARGUMENT].** Covtype against that list: it is 7-class with strong NATIVE imbalance and
heterogeneous density (the soil-type indicators partition the space), so (a), (b), (c) are present;
native imbalance is a feature here, not a defect. The current world balances the TEST split for
resolution (`test_per_class=300`), which we keep and can enlarge per P4. The missing piece is control
over the POOL's imbalance: a small new DataView option (`pool_per_class` or a class-subsample spec)
that shapes the unlabeled TRAINING pool so rare-class starvation is sharp. Like `test_per_class` it
is a config change plus re-push, no data rebuild. Label-cost heterogeneity (e) is likewise a
config-level cost vector fed to the reveal meter, if the second axis is wanted. This answers owner
question 5; concrete fallback datasets are in the Alternatives section, screened on the resolution
requirement (a populous rarest class, the lesson of the dermatology bury).

**P17 [ARGUMENT].** The pre-test (owner question 6), the commit gate of direction doc section 22c
instantiated for this scheme, all probes throwaway policies through the real grader via hosted
validation, never local, never student evals, cheapest killer first:
- **Gate 0, resolution floor (free arithmetic).** With the test balanced to N per class, the
  rarest-class standard error is sqrt(p(1-p)/N); require achievable-range over Delta\* of at least
  about 4, choosing N as large as the batched predict now affords.
- **Gate 1, stream information (per P8).** Best label-adaptive probe versus best precomputed
  label-free schedule (coreset as the precomputed champion), same predictor. The gate kills the
  scheme if adaptive minus precomputed is at most Delta\*: then every purchase decision is
  front-loadable and the reveal loop is decoration.
- **Gate 2, dominance ladder.** The canonical rungs as probes: random, least-confident, margin,
  coreset, BADGE-style hybrid, and a budget-scheduler, all sharing ONE ordinary predictor so only
  acquisition differs, five seeds each. The gate kills if best-rung minus random is at most Delta\*
  (monostrategy). The desirable outcome is rungs spanning several multiples of Delta\*, ideally with
  the cold-start uncertainty rung landing below random by more than Delta\* (a resolvable rung on
  the low side too).
- **Gate 3, luck.** K skill-identical replicates differing only in tie-breaks and internal seeds
  must resolve to ONE level across the five seeds; separation there means manufactured luck. The
  fully visible pool makes this unlikely (the first query is already informed by feature geometry,
  no blind first picks), but it is cheap to check.
- **Gate 4, budget binding.** Sweep L. Too large and even random reaches the full-label ceiling
  (ladder flattens); too small and no rule learns the rare classes (everything at the floor). Keep L
  in the window where rungs diverge by more than Delta\* AND the ceiling is learnable; report the
  score-versus-L curve per rung and set L where between-rung spread is widest.

**P18 [ARGUMENT].** Owner question 7, first the structure of the commitment. The reveal is not
undoable by any protocol (a label, once transmitted, is information the policy possesses), and the
meter only decrements, so every purchase is an irreversible spend; that much is [PROVEN] from the
mechanism. Take-backs here do not merely cost, they are absent from the mechanism entirely, a pure
monotone ratchet. The owner's working definition of commit-mode is "take-backs allowed but neither
easy nor cheap"; this scheme is the limiting case of that definition. The paid-revision analysis
(file 06; direction doc section 22a) killed refunds precisely because a revealed value is
un-refundable and buy-everything-refund-everything becomes dominant; a scheme that never offers a
take-back inherits none of that pathology. So the limiting case is not a problem; it is the honest
end of the owner's spectrum.

**P19 [ARGUMENT].** Owner question 7, second half: is the commitment load-bearing? Compare the plain
global budget that collapsed (direction doc section 22): there, a shared pool over an independent and
identically distributed (iid) arriving test stream self-averages, the optimal policy reduces to a
per-row rule with a peek-calibratable shadow price, and path dependence washes out. That collapse
needs exogenous random arrivals to average over. Here there are none: the pool is fixed and visible,
and the budget is spent over a sequence the student CHOOSES, where each purchase changes the model
that chooses the next purchase. The state (labeled set plus remaining pool) is endogenous and
path-dependent within a run, so the self-averaging step of the collapse argument has nothing to
average. P7 reaches the same point from the compute side: the resource that accrues mid-session is
one front-loading does not reach, so the session is not reducible to `__init__`. Both halves say the
commit structure is what blocks the known collapse routes. At the same time, the band's PRIMARY
source is that active learning is a non-dominated strategy space (P11); the commitment is the reason
that space does not collapse, rather than an extra bolt-on difficulty.

## The result

**KEEP, fix-first, gated on the P17 pre-test.** Of the surviving commit schemes this one is strongest
on infrastructure (it retargets the existing mediated drive loop from feature-value reveal to label
reveal, and per P4 it is cheaper to grade and higher-resolution than the world already built) and on
non-dominance (active learning is a field defined by the absence of a dominant acquisition rule,
P11). The ladder has resolvable rungs below the baseline (broken loop, cold-start uncertainty), at it
(random), and above it (coreset, hybrid, scheduling, semi-supervised), separated on both effort axes
file 00 requires, discoverability and grade-time compute. The commitment is a pure irreversible
ratchet, honestly labeled (P18), and purchased labels being the one resource front-loading does not
reach (P7) is the sharpest statement of why this scheme keeps genuine temporal structure where
compute-only schemes lost theirs.

**What would flip it to KILL.**
- **Gate 1 failing (the front-loading vacuity check, P8):** if no label-adaptive rule beats the best
  precomputed label-free schedule by more than Delta\*, the reveal loop is decoration and the scheme
  reduces to an agent-time computation, the collapse family of file 01.
- **Gate 2 failing (the binding check):** if at every L where the classes are learnable the best rung
  ties random within Delta\*, the scheme is monostrategy, the same death as
  PhysioNet/Diabetes/Thyroid on the feature-acquisition gate. This is the real empirical risk the
  literature warns about (random is a strong baseline on large redundant tabular pools).
- **Gate 0 failing:** range over Delta\* below about 4 even with the enlarged batched-predict test
  set.
All three are cheap to check hosted before any student run.

## Alternatives

- **If covtype's native imbalance separates too weakly:** add the `pool_per_class` DataView transform
  (P16) to sharpen rare-class starvation before abandoning the dataset. Reshape before reject.
- **If covtype fails the gates outright, screen (big, many-class, populous rarest class):**
  - **Sensorless Drive Diagnosis** (University of California Irvine repository): 11 classes, about
    58k rows, roughly balanced (about 5000 per class), so the rarest class is very populous. Strong
    resolution; screen whether its geometry rewards non-random labeling.
  - **Letter Recognition** (same repository): 26 classes, 20k rows, about 700 per class. Many classes
    give a long boundary where label placement matters.
  - **A multi-class network-intrusion set** (UNSW-NB15 or CIC-IDS as multi-class): many attack
    families, large, and label cost is genuinely heterogeneous in the domain (some labels need deep
    packet inspection), giving the second commit axis for free. Caveat: intrusion sets can be
    degenerate on the binary task, so screen the multi-class version only.
  - Fashion-MNIST flattened (10 classes, 70k rows) is the standard active-learning benchmark and
    works mechanically, but flattened pixels are a tabular monoculture (direction doc section 5);
    since this scheme grades acquisition rather than modeling that is tolerable, still keep it only
    as a sanity check, not a keeper.
- **Second commit axis (only if the single-axis band is thin):** per-class or per-row label COSTS
  (expensive expert versus cheap crowd labels), metered by the same reveal loop, turning the budget
  into an allocation-across-label-types problem. Config-level, no new infrastructure.

## Open questions (each worth a dedicated chat)

1. **Batch protocol final shape.** Free student batch size (with a hinted default) versus a fixed
   K-round structure that caps refits (P3). Decide after a smoke run shows whether weak agents
   actually hang on size-1 refit loops.
2. **Test-split resampling versus a fixed test set.** P6 recommends per-seed test resampling for an
   honest residual. Confirm the grading toolkit's paired rank-resolution test accepts shared-seed
   resampled test draws, or fall back to a fixed test set plus a mandatory stochastic-training seed
   (and verify every probe's residual is then nonzero).
3. **The compute envelope of the session.** Wall-clock the canonical rungs (especially the
   BADGE-style hybrid, the heaviest per P10) on the grading machine at the binding L, per file 00's
   measurable half of reachability: which rungs are "fast" in the R3 sense and which genuinely cost
   session or grade-time compute that weak agents will not finish under the cap.
4. **The label-cost second axis.** Build it now (richer band, more knobs to get wrong) or ship the
   single-axis label budget first and add cost heterogeneity only if the band is thin.
5. **How much do estimates substitute for purchases?** P7's non-front-loadable resource has a partial
   substitute: semi-supervised estimates from the visible features (P10 rung h). If the pool is so
   self-revealing that propagation nearly replaces purchasing, the budget stops binding from a new
   direction; the L-sweep (gate 4) should include a propagation-heavy probe to measure this.
