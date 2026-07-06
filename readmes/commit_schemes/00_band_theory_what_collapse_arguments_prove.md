# 00 Band theory: what a collapse argument actually proves

## The question

When someone argues "the optimal strategy for this scheme is computable offline from the peek data,
so every competent agent converges to it and the scores collapse," or the sibling form "everything
committed at time T could equally have been committed later with identical information, so the
commit never binds," what has that argument actually established about the band, and what has it
left completely open? This file is the reference frame the other seven analyses cite, so the process
below has to end in a criterion they can apply.

## Background (terms defined)

- **Peek data**, the train and validation split, features and labels, fully available to the agent
  at agent time. It seeds a smart decider. The only permitted ignorance is of the test stream (which
  cases arrive, in what order). This is a hard constraint from the task owner; see the folder README.
- **The band (the product)**, the dispersion of scores across REAL student rollouts of VARYING
  strength at a fixed budget. Not the dispersion of a portfolio of strategies we imagine (direction
  doc section 4). The band is measured, never computed.
- **Student**, a large language model coding agent. It does not predict; it writes a Python `Policy`
  that trains a model and is driven by the grader (direction doc section 12, section 20). Its
  "strength" is whatever produces a higher score, defined only by the score (direction doc section 2).
- **Agent time (the session)**, the period the student works before shipping its artifact.
  **Grade time**, when the grader runs and drives the shipped policy; grade-time compute is bounded
  only by the platform's time cap.
- **Bounded agent**, an agent whose decision quality at any moment is a function of the compute it
  has ALREADY SPENT, not only of the data available to it. Session computation generates
  information: experiment results on peek data, debugged code, insights that fire late. "All peek
  data is present at minute zero" therefore does not mean "all conclusions from peek data are
  present at minute zero."
- **Final-state grading**, grading only the shipped artifact. **Checkpoint grading**, grading
  intermediate commits made along the session.
- **LEVELS**, the number of statistically distinguishable score tiers across runs, the `n_levels`
  statistic of `rank_resolution` in `sdk/hor_utils/noise.py`. The most important metric. A wide
  spread with 1 to 2 levels is a weak task (CLAUDE.md).
- **Resolution**, achievable score range divided by the grading noise floor: how many levels the
  test set can support at all. Capped by the rarest class, not total rows (direction doc section 18).
- **Ceiling**, the top attainable score under the scheme, the score reached by an agent that both
  finds the offline-computable optimum and has the compute to finish computing it.
- **Dominance / collapse argument**, a claim that one move (usually the offline-computable optimum)
  is best for essentially every case, so all competent agents land on it and scores pack.
  **Precomputability argument**, the temporal variant: a claim that some committed state is a pure
  function of peek data, so when it was committed does not matter.
- **Skill ladder**, the working formalization this file develops. The ordered set of distinct-scoring
  RUNGS between the naive move and the optimum, together with the DISCOVERABILITY of each rung (how
  hard it is for an agent to find) and its COMPUTE COST (how long it takes to build once found). A
  tall, multi-rung, hard-to-climb ladder spreads agents; a one-rung or easy-to-climb ladder stacks
  them.
- **Delta\***, the resolution gap: the seed-blocked analysis-of-variance threshold below which two
  scores are one level (folder README, direction doc section 22c). Two rungs closer than Delta\* are
  not two rungs.

## The process

**R1 [PROVEN], the covtype record versus the computability-implies-collapse implication.**
On covtype, a near-optimal per-row policy was computable offline from peek data (direction doc
section 22, folder README). Real students nevertheless banded 0.675 to 0.848, about 3 levels. The
premise "optimum computable" held while the predicted collapse did not happen, so the implication
"optimum computable, therefore scores collapse" is false in general. What computability does pin is
the top of the ladder, for an agent that finds the optimum and has the compute to finish computing
it. It says nothing about how many agents reach that top or how the rest distribute below it.

**R2 [ARGUMENT], the owner's challenge, worked through for agents of varying strength.**
"We want to differentiate strong from weak, who says all agents are strong?" Nobody does. Follow
what a collapse argument actually asserts: it names the attractor that STRONG agents converge to.
The band, however, is measured across agents of VARYING strength. The argument is therefore silent
about where weaker agents land, unless it separately shows the attractor is EASY to reach. So a
dominance claim without a discoverability claim describes the strong-agent fixed point and stops
there; concluding collapse would additionally require the weak agents to arrive at that same fixed
point, which the claim never shows. Call this the first idealization: idealized strength.

**R3 [ARGUMENT], the file 01 instance, worked through for computationally bounded agents.**
File 01 (agent-time commits) argued: at agent time all knowledge (peek) is present at minute zero
and nothing new arrives during the session, so any state committed early could have been committed
late with identical information, hence early locks never bind. The owner's rebuttal: "if it could
have, it does not mean it would." Trace where the argument goes wrong: it treats an agent's
information as a function of DATA AVAILABLE, but for a bounded agent it is a function of COMPUTE
SPENT. Computation performed during the session generates information (experiment results on peek
data, debugged code, late-firing insights), so an agent forced to commit at minute 10 commits from a
genuinely poorer information state than the same agent at minute 90, with identical peek data on
disk the whole time. "The commit is a pure function of peek" is therefore an unbounded-agent ceiling
statement twice over: it idealizes knowledge (R2) and computation (this step, the second
idealization). A precomputability claim earns force only when the computation is also CHEAP, fast
enough that even weak agents finish it before the commit point. "Computable AND fast" is the exact
mirror of the "dominant AND easy" requirement derived in R8: one collapses the insight axis, the
other collapses the time axis, and a claim needs the relevant axis collapsed, not merely the
endpoint named.

**R4 [ARGUMENT], the empirical split across the per-row acquisition datasets, and the variable that
explains it.** The record splits cleanly into two groups:

- Buried, 1 to 2 levels: UNSW-NB15, thyroid, hydraulic, diabetes. These failed the acquisition gate
  (direction doc section 16, 19): a single fixed panel already reaches the ceiling (thyroid: the
  thyroid stimulating hormone lab alone gives 0.80; hydraulic: a budget-5 fixed panel equals the
  full 0.997). The data is easy or its feature relevance is global, so a crude competent move
  already sits at the ceiling, the ladder collapses to about ONE rung, and every competent agent
  lands on it.
- Banded: covtype (0.675 to 0.848, about 3 levels) and the Tennessee Eastman Process (TEP) scaffold
  (fail, fail, 0.65, 0.80, 0.82). Here the ceiling sits FAR above the lowest competent rung, and
  real agents occupied distinct rungs.

Both groups had computable near-optima, so computability does not separate them. What separates
them is the vertical gap between the lowest competent rung and the ceiling, and the number of
discoverable rungs inside that gap: ladder height and rung count.

**R5 [ARGUMENT], reading the TEP spread rung by rung.** Take the five TEP outcomes in order: fail
and fail are agents that never got a working driven policy at all; 0.65 is a crude but working
predictor plus policy; 0.80 and 0.82 are decent-to-good ones. Only the topmost rung is "capture the
adaptive routing headroom" that needs the data's heterogeneity (direction doc section 17, 19). The
rungs beneath it (train a masking-robust predictor, get a policy running under the mediated grader
at all, produce a sensible ordering rather than random) are ENGINEERING rungs that exist on any hard
task. Note what the failing and crude agents lacked: not peek data, which they had in full, but
session compute converted into a working artifact. The engineering rungs are R3's bounded-computation
point showing up empirically. This is why covtype bands even with an offline-computable routing
optimum: the routing top may be flat and computable, but the climb up to a competent working policy
is itself multi-runged when the task is hard enough that a crude attempt lands well below the
ceiling.

**R6 [ARGUMENT], where a scheme reads a bounded agent's score.** If compute converts to information
(R3), an agent's position on the ladder is a trajectory over the session, not a point, and it can
keep rising during grade-time compute within the platform's time cap. A scheme chooses where on
that trajectory the score is read:

- **Final-state grading** samples the TOP of each agent's climb at shipping time. Differences in
  climb speed still show up, as different tops reached within the same session length (R5).
- **Checkpoint grading** samples the trajectory itself, so it grades climbing SPEED directly.
  Caution from the section 22a memo: session speed is contaminated by environment noise (installs,
  tool latency) that is orthogonal to stream seeds and not averaged out by them. The trajectory is
  real signal about a bounded agent; the current measurement of it is noisy. Those are different
  facts, and a scheme file must keep them apart.
- **Grade-time compute** (the `train_at_grade` mode) extends the climb past shipping: it partially
  equalizes session-compute differences (everyone's code gets the cap's worth of compute) while
  preserving code-quality differences (the same cap runs better or worse code).

It follows that a collapse claim must state WHICH sample point it addresses. "The optimum is
computable from peek" can be true of the unbounded limit and false at every point where real,
bounded climbs are actually sampled.

**R7 [PROVEN], the dermatology case and the resolution cap.** Dermatology has the routing structure
(adaptive beats fixed, direction doc section 17) yet buried, because its rarest class has 7 test
instances, giving a balanced-accuracy standard error of about 0.035 and only about 2 levels
(direction doc section 18). The ladder rungs exist; the test set cannot resolve them. So
`LEVELS = min(rungs the real population occupies, resolution cap)`, and both factors must be large.
Either at 1 buries the task, for different reasons that must not be confused: a flat ladder is a
strategy-space problem, a low resolution cap is a data problem.

**R8 [ARGUMENT], assembling the rule.** Combine R2 and R3. A dominance or precomputability argument
concludes collapse only if the dominant move is reached by weak and strong agents alike, in time.
That holds exactly when the move is low-effort on BOTH axes: EASY to discover (no nontrivial insight
chain) and CHEAP to compute (finishable well within the session, or before the commit point the
argument is about). In that case the ladder has effectively one reachable rung, everyone lands on
it, and the argument is a legitimate falsifier. When the dominant move is hard on either axis
(behind several insights, gated by engineering a weak agent botches, or expensive enough that slow
agents commit before finishing it), the same argument only locates the top of the ladder: a
statement about the CEILING that says nothing about the band below it. Every collapse claim must
therefore be paired with a reachability claim about the dominant move, covering both
discoverability (R2) and compute cost at the sampled point (R3, R6).

**R9 [PROVEN], the operational form that already exists.** Gate 2 of the commit-gate battery
(direction doc section 22c) runs a textbook-simple rule and a strictly richer strategy through the
real grader as throwaway probes, and the gate kills only if `richer - simple <= Delta*`. That
comparison is R8's separation test made measurable: if the simple rule already ties the rich one,
the ladder is flat, the dominant move is trivially reachable, and collapse is real; if the rich rule
wins by more than the resolution gap, discoverable rungs exist and the bare dominance argument does
not kill. One honest caveat: the probe measures rung SEPARATION (score gap between strategies we
hand it), not rung REACHABILITY (neither the insight cost nor the session-compute cost of building
the richer strategy); reachability is covered by R10's empirical record and R11's proxies. The probe
reduces R8's separation half to something measurable before spending student runs.

**R10 [ARGUMENT], the track record of probe ladders as predictors.** Across this world's history,
when probe policies of differing sophistication separated by more than noise, real students banded;
when probes did not separate, students packed (folder README, direction doc section 16, 19). That
makes probe separation the best pre-student predictor available. A difficulty audit (is the winning
move a known recipe, does it fit one code pattern) and a recorded-rollout replay (did any past
rollout actually find the move) supplement it, but neither replaces running agents, because both
estimate reachability, which is exactly the quantity we have no clean way to pin (R11).

**R11 [CONJECTURE], how far reachability can be measured before students run.** Whether a rung is
reachable by the specific agents we grade is the crux of the whole framework, and we do not know how
to compute it a priori. Its two halves differ in measurability. The COMPUTE half is the more
measurable one: the winning strategy's build-and-train time can be wall-clocked on the task machine
and compared to the session and to any commit point, giving a real number for "fast" in R3's
"computable AND fast." The INSIGHT half has only weak proxies:
- (a) Was the winning strategy a known textbook recipe (forward selection, greedy
  value-of-information, Hyperband)? A textbook move is more discoverable, so it flattens the ladder.
- (b) Does the move fit in one obvious code pattern? A one-pattern move is more discoverable than
  one requiring several composed insights.
- (c) Did any real rollout in our history actually find it? This is the only direct evidence, and it
  is the strongest of the three, but it is sparse and specific to agents already run.
These proxies rank risk; they never conclude. The map from "a strong agent could compute this
offline" to "the agents we grade will actually all find it, and finish it, in time" is the gap the
whole band lives in, and it is empirical.

## The result

**Operative criterion (this is what the other seven files cite).** A collapse, dominance, or
precomputability argument kills a scheme's band ONLY when it is paired with a reachability claim
that the dominant, offline-computable move is the lowest-effort competent move on BOTH axes: easy to
DISCOVER (no nontrivial insight chain, R2, R8) and fast to COMPUTE (finishable by weak agents before
the point where the scheme samples the climb, R3, R6). A computability claim alone proves only where
the ceiling is; it says nothing about the band below it, and "could have been computed earlier" says
nothing about whether bounded agents would have. Concretely, to defend a scheme against such an
argument, show all three:

1. **A multi-rung ladder with the dominant move not easy**, verified by a probe ladder through the
   real grader: a strictly richer strategy beats a textbook-simple one by more than Delta\* (direction
   doc section 22c gate 2). This is the direct test of R8's separation half via R9.
2. **The dominant move is not trivially fast**, or the scheme's sample point (final state, checkpoint,
   grade-time, R6) sits where bounded agents genuinely differ in how far they have climbed. Wall-clock
   the winning computation against the session and the commit points (R11's measurable half).
3. **Resolution to see the rungs**: achievable range over Delta\* at least about 4, and the rarest
   class supports it (direction doc section 22c gate 0, section 18). Ladder rungs the test cannot
   resolve are not levels (R7).

If a scheme has only one reachable rung (easy AND fast), or the rungs are below the resolution
floor, the band collapses regardless of whether the optimum is computable. If it has several
reachable-in-principle rungs the test can resolve, and reaching them costs real insight or real
session compute, the band survives regardless of whether the top rung is computable.

**What evidence would flip this.** Either direction of the probe-to-student link breaking:
- A scheme whose probe ladder SEPARATES (rich beats simple by more than Delta\*) yet real students
  still PACK. This would show probe separation is not sufficient, and the operative criterion needs a
  reachability term the probe does not capture.
- A scheme whose probes do NOT separate yet real students BAND. This would break probe separation as a
  predictor entirely.
Neither has been observed in this world to date; the record (section 16, 19) is one-directional in
support. A single clean instance of either flips the criterion.

## Alternatives (when the pitfall is the data or the metric, not the argument)

- **Resolution is the pitfall, not the ladder (data).** Dermatology proves a real ladder can bury on a
  rarest-class floor alone (R7). When a dominance argument seems to bite, first check it is not
  actually the resolution cap doing the burying; the fix there is bigger, populous-class data (direction
  doc section 18), not a richer scheme.
- **The metric decouples the skilled axis (metric).** Balanced accuracy can flatten a ladder by making
  the score invariant to the very thing a scheme varies. It weights all classes equally regardless of
  arrival mix, so any scheme whose test-time uncertainty is "which cases arrive" scores identically
  across the axis it means to grade (direction doc section 22b, 22a instrument-installation). Before
  trusting a ladder, confirm the metric couples to the skilled axis; if it does not, the ladder is real
  but invisible, and the fix is an arrival-weighted metric, not a richer scheme.

## Open questions (each worth a dedicated chat)

1. **Can rung reachability be measured better than the R11 proxies without a full student eval?**
   For example a cheap "weak-agent" probe tier (a deliberately under-resourced policy) that estimates
   where the low rungs sit, turning the one-directional section 16 and 19 record into a two-sided
   calibration.
2. **Can a ladder's rungs be anti-correlated with agent strength?** Direction doc section 2 insists
   skill is defined only by score, which admits a scheme where a strong agent over-engineers and lands
   below a crude one. If such an inversion exists, "richer beats simpler" (R9) mis-predicts the band.
   Worth a targeted probe.
3. **Do the engineering rungs (R5) persist as agents improve?** Much of the TEP and covtype spread was
   agents failing to get a working policy at all. That rung may erode as agents get more capable at the
   mediated-grader harness, shrinking the band over time even with the data fixed. If the band leans on
   engineering difficulty rather than routing difficulty, it has a shelf life, and schemes should be
   judged on the rungs that survive stronger agents.
4. **Can the temporal climb (R6) be probed cheaply?** For example time-boxed probe tiers: the same
   probe-building process cut off at different compute budgets, scored through the real grader, to
   estimate how much of the band is compute conversion versus insight. If score keeps rising with the
   box, commit points placed inside the rise genuinely bind bounded agents; if it saturates fast, the
   computation is "fast" in R3's sense and precomputability arguments regain force at that sample
   point.
