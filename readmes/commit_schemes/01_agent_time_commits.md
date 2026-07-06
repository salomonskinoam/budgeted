# 01. Agent-time commits

## The question

Can a commitment the student makes *during its own working session* (before any test row is
revealed) create a band? Three variants:

- **(i) Early lock-in.** The student is made to fix some state early in the session (a feature panel,
  a predictor architecture, a hyperparameter set) that constrains what runs at test time; later
  changes are capped or priced.
- **(ii) Graded intermediate commits.** The harness snapshots the deliverable at wall-clock marks
  during the session and aggregates the snapshot scores (weighted mean, or area under a
  quality-vs-time curve), instead of grading only the final artifact.
- **(iii) Append-only or K-rewrite deliverables.** The deliverable may only grow (each write is a
  superset of the last) or may be edited at most K times.

## Background (terms defined)

- **The student.** A large language model (LLM) coding agent. It writes `solution.py`, which trains
  a model and ships a `Policy` class. The agent never predicts itself; it writes code (see
  `README_general_direction.md` §12). All runs use the **same model and same agent type**, so raw
  capability is nominally fixed across runs; what varies is the session realization.
- **Bounded agent.** An agent whose useful state is produced by computation over time: experiments
  run on peek data, code written and debugged, insights that fire mid-session. For a bounded agent,
  its solution state at hour one and at hour three differ materially even though no external
  information arrived in between. Every real student is bounded.
- **The deliverable / `solution.py`.** In the built world (`worlds/budgeted/`, design bible §20) the
  student ships a `Policy` with `__init__(data_dir)` (trains on fully-observed data),
  `select_next(observed, budget_left) -> feat_id | None`, and `predict(observed) -> int`. There is
  no predictions file; the grader **drives** the policy.
- **Agent time vs test time.** Agent time is the working session in which the agent writes and runs
  `solution.py`. Test time is grade time, when the mediated grader runs the shipped policy against a
  test stream. This memo is about commitments made at agent time.
- **Peek data.** Train and validation features *and labels*, fully available to the agent throughout
  the session. A hard owner constraint (§22): peek is always fully available; the only permitted
  ignorance is of the test stream (which cases arrive, in what order), revealed only at grade time.
- **Mediated grader.** `verify.py` spawns the policy sandboxed and, per test row, runs
  select -> reveal -> predict under a per-row acquisition budget; labels stay grader-only. Metric =
  balanced accuracy (mean of per-class recalls); `best_observed = 1`.
- **The 5-seed protocol.** Evaluation reruns the shipped policy under 5 fixed stream seeds; score =
  mean over seeds; **levels** (the count of statistically distinguishable score tiers, the scoring
  library's `n_levels`) are counted by a seed-blocked analysis of variance. The **band** (the
  product) is the spread of levels across real rollouts of varying strength.
- **Session noise.** Per-session random events not attributable to skill: install failures,
  tool-call latency and outages, unlucky exploration order. One run = one session; there is no
  second draw of the same session.
- **covtype.** The one dataset in the sweep that banded with resolution: balanced accuracy
  0.675-0.848, spread 0.173, about 3 levels over a noise floor near 0.058 (eval
  `babd012a-4ae2-4349-99cb-a030db3f4491`, 5 runs). The reference case for "computable-from-peek does
  not imply collapse."
- **Tennessee Eastman Process (TEP) scaffold eval.** The 5-run eval on the anonymized TEP task
  (design bible §20), the other recorded source of full agent transcripts.
- **Transcript.** The recorded tool log of a run: every file write and edit with wall-clock
  timestamps, from which the state of `solution.py` (and the rest of `/workdir`) at any session
  time t can be reconstructed by replaying edits up to t.
- **Prior analyses.** Two earlier treatments of this question exist. The first (recorded in
  `../README_general_direction.md` §22a) rested on a *collapse-by-strength* argument; the second on
  an *information-vacuum* argument. The owner rejected both. Steps 1 and 2 below examine each,
  because what exactly failed in them determines what remains to analyze.

## The process

**1. The collapse-by-strength argument, examined.** The first prior analysis reasoned: a commit made
before any test row is a pure function of peek; competent agents compute the same near-optimal
function; therefore identical commits; therefore collapse. Every link quantifies over *competent*
agents. But the band is the spread of a population of varying strength across the whole skill
ladder, not the gap among agents at the top rung, and this world has a direct counterexample: the
base task's per-row policy is also a pure function of peek (masking-XGBoost plus greedy
value-of-information acquisition is computable offline), yet covtype banded, 0.675-0.848 at about 3
levels. So "the optimal commit is computable from peek" does not, by itself, predict packed scores.
The argument is invalid for the purpose it was used for. [PROVEN invalid, by counterexample]

**2. The information-vacuum argument, examined.** The second prior analysis reasoned: no external
information arrives during the session (peek is all present at the start; the stream is never shown),
so any state committed early could have been committed late with identical information; therefore
early locks are vacuous and revisions are informed by nothing new. Trace the hidden premise: "could
have been committed late" implies "is equivalent to committing late" only for an agent that can
evaluate the whole peek-to-policy computation instantly, at any moment. That is a **computationally
unbounded** agent. The argument idealizes computation exactly as argument 1 idealized strength, one
level deeper. For a **bounded** agent, computation during the session *generates* information:
experiment results on peek data, debugged code, late-firing insights. A weak agent's state at hour
one is materially different from its state at hour three with zero external information arriving.
So for real agents the session is not an information vacuum, early locks do bind, and they bind
*differently* for weak and strong runs, which is the very spread the band wants to measure. What
survives is a ceiling statement only: in the limit of unbounded computation, agent-time commit
structure carries no signal. The ceiling says where the signal must come from (differences in how
far along the computation each run is at each moment) and warns that the signal shrinks as agents
get faster. It decides nothing about today's agents. [ARGUMENT, valid only as an unbounded-agent
ceiling]

**3. What remains for variants (i) and (ii).** For bounded agents an early lock (i) binds: the
agent locks whatever its computation has produced so far, and a slower or weaker run locks worse
state. Checkpoint aggregation (ii) grades the same underlying quantity continuously: the quality of
intermediate computation states. So both variants rest on the same three-part question, and none of
its parts is decidable from the armchair:
  - **(a) Do session trajectories differ by skill in a way the snapshot or locked-state score
    captures?** Mechanism for yes: final solutions cluster (most runs eventually converge near
    masking-XGBoost plus greedy acquisition), while mid-session states differ far more; if better
    runs pass through better intermediate states earlier, snapshots resolve pairs of runs that
    final-only grading ties, adding graded rungs.
  - **(b) How much of the trajectory spread is skill versus session noise?** Both readings are
    honest. Noise side: model and agent type are fixed, so when-a-run-got-good is substantially a
    realization of installs, latencies, and exploration luck, and the 5 stream seeds do not average
    it (step 5). Skill side: across runs of one model, some trajectories are genuinely better
    organized (read the data first, test early, do not thrash); fewer steps to strength is
    efficiency, which a reinforcement-learning trainer legitimately wants to reward, and insight
    timing is partly systematic exploration, not coin flips. Position: a mixture, split unknown a
    priori, measurable (step 6).
  - **(c) Is it gameable?** Examined next (step 4). [ARGUMENT]

**4. The gaming surface.** These findings stand on their own, independent of steps 1 and 2.
  - **Scratch-space laundering.** Suppose only the text of `solution.py` is snapshotted. The agent
    then iterates in `/workdir/*.pkl` and other files while `solution.py` stays a thin constant
    loader; every snapshot is the same trivial text and carries no signal. File-level snapshotting
    is defeated outright. [PROVEN] *Fix:* snapshot the **whole workdir** and score each snapshot by
    **executable behavior** (drive its policy through the mediated grader), so the model artifacts
    are inside the snapshot. *Residual cost:* several grader executions per run, and mid-session
    snapshots are often not runnable (half-written file, model still training). Zero-scoring a
    mid-training snapshot penalizes exactly the runs doing real work; last-good-state scoring
    rewards writing early and stalling. The fix closes the laundering hole and opens a
    scorer-validity question with no obviously right answer (see Open questions).
  - **Shadowing.** Suppose append-only is enforced on the *text* of a Python file (superset-prefix
    check). Later definitions shadow earlier ones, so appending a brand-new `Policy` class rewrites
    the file's behavior while passing the check; the constraint binds on nothing behavioral.
    K-rewrite caps are routed around the same way (append a dispatch layer). Any (iii)-style
    constraint must bind on behavior, and no cheap behavioral append-only check is known. [PROVEN]
  - **Precompute-then-commit-once.** The old form ("do all work internally, write the final file
    once, every snapshot equals the final") over-credits the agent: a bounded LLM agent's real work
    (training a model, running experiments) happens through tool calls in the filesystem, which
    whole-workdir snapshots capture. What remains is a milder game, delaying writes to graded
    locations, and whole-workdir plus behavior scoring shrinks the ungraded space to the agent's
    context window. An erosion, not a defeat. [ARGUMENT, softened by boundedness]
  - **Checkpoint-timing games.** Dumping best-so-far just before each mark requires knowing the
    marks. Under the mandatory production framing the student is never told it is graded, let alone
    when; the marks are hidden and this game has nothing to aim at. [ARGUMENT, defused]

**5. What the 5 seeds average, and what they leave untouched.** The seeds vary the test stream. An
agent-time snapshot is fixed before any stream is seen, so re-scoring it under 5 streams averages
stream randomness in the policy's behavior, exactly as in the base task; that part is sound. The
seeds never re-run the **session**: each run is one realization of installs, latencies, and
exploration order, and every checkpoint score inherits that single draw un-averaged. Session noise
therefore lands in the between-run variance of the seed-blocked analysis, where the levels statistic
counts it as signal. This is a mechanical fact about the protocol, independent of agent boundedness.
Its consequence for variants (i) and (ii): levels added by checkpoint grading are real only to the
extent the trajectory spread is skill (step 3b), and the protocol has no internal way to tell the
two apart; only an out-of-band check can (the rank-correlation readout in step 6). [PROVEN]

**6. The transcript-replay pre-test.** The recorded evals already contain what is needed: covtype
eval `babd012a-4ae2-4349-99cb-a030db3f4491` (5 runs) and the TEP scaffold eval (5 runs), each with
full transcripts including every file edit with wall-clock timestamps. Procedure:
  1. For each run, parse the transcript tool log; replay edits in order to reconstruct the full
     `/workdir` state (not just `solution.py`, per step 4's laundering result) at marks
     T = 25/50/75/100 percent of that run's session length. Tiny local text work, no data loading,
     no approval-gated compute.
  2. Record non-runnable snapshots (mid-edit, model not yet trained) as such; that is data, not an
     error.
  3. Score every runnable snapshot through the **real mediated grader, hosted, as throwaway
     validation runs** (the sanctioned offload pattern; no student evaluation runs spent). About 5
     runs x 4 marks x 2 datasets, roughly 40 gradings. Output: quality(run, mark).
  4. Readouts, mapped to step 3's three parts:
     - **Separation (3a):** compute levels over the 5 finals (covtype known, about 3) and over the
       5 checkpoint aggregates (area under quality-vs-time, and a weighted mean). Does the aggregate
       resolve a pair of runs that the finals tie?
     - **Skill versus noise (3b):** rank-correlate quality(run, early mark) with quality(run,
       final) within each dataset. High correlation: early state predicts final skill, the
       trajectory spread is skill-ordered. Near-zero or negative: the mid-session ordering is
       timing/noise-driven, and any levels the aggregate adds are manufactured luck.
     - **Gameability baseline (3c):** count runs whose `solution.py` reaches near-final behavior
       early and then stops changing (natural commit-once incidence), and compare whole-workdir
       scoring against `solution.py`-text scoring (how much signal laundering would have destroyed).
  5. Decision rule, stated in advance:
     - **KEEP (escalate, not build):** the aggregate resolves at least one final-tie on at least
       one dataset, AND the early-vs-final rank correlation is clearly positive, AND natural
       commit-once incidence is low. Then variants (i)/(ii) graduate to a larger transcript set
       (5 runs is a smell test, far too few for the levels statistic) before any build decision.
     - **KILL:** checkpoint scores are near-identical across runs at every mark (no mid-session
       spread to grade), OR the aggregate adds no resolution over finals, OR it adds resolution but
       the early-vs-final correlation is near zero or negative (the added levels are session luck).
  One caveat cuts both ways: the recorded runs were produced with no checkpoint rule, so they show
  *natural* iteration. That is the right thing to measure for (ii), which grades natural behavior
  silently, but it under-tests (i), where a forced lock would change behavior; a KEEP outcome
  supports (ii) directly and (i) only suggestively. [CONJECTURE, resolvable now]

**7. Variant (iii) under bounded agents.** Bounded agents write incrementally as a matter of course,
so for them append-only is not vacuous-by-idealization; it genuinely binds. Ask what it binds *on*:
the constraint prices rewriting existing text, so what it mostly punishes is **refactoring**, and
refactoring avoidance is not a skill this world wants to grade (the graded product is the policy's
test-stream behavior, not the tidiness of how its source accreted). On its own terms, then, it is an
annoyance tax orthogonal to the band. And the tax is not even collectible: the shadowing exploit
(step 4) lets any agent that notices it rewrite behavior freely, so text-level append-only grades
only "did the run notice the loophole", a one-bit trivia rung. K-rewrite is the same with a counter.
No empirical question here is worth a pre-test. [ARGUMENT, plus the step-4 [PROVEN] exploit]

## The result

- **Variant (iii) append-only / K-rewrite: KILL.** [PROVEN exploit + ARGUMENT] Behaviorally vacuous
  under the shadowing exploit; where it binds at all it taxes refactoring, which is not a skill axis
  of this world. Flips only if someone produces a cheap *behavioral* append-only checker, which is
  not currently known to exist.
- **Variants (i) early lock-in and (ii) checkpoint aggregation: UNDECIDED BY ARGUMENT, decided by
  the pre-test (step 6).** Both collapse arguments against them failed: one idealized strength
  (step 1), the other idealized computation (step 2). For bounded agents the session generates
  information, early locks bind, and mid-session states may separate skill more than finals do
  (step 3a). The standing threat is not collapse but noise: the 5-seed protocol re-grades a fixed
  session and never re-runs it, so session-level randomness stays un-averaged (step 5) and any
  added levels are suspect until shown skill-ordered. The pre-test measures exactly this on the
  recorded covtype and TEP runs for about 40 hosted throwaway gradings.
- **Flip conditions, both directions.** Toward KEEP: all three pre-test readouts pass (aggregate
  resolves a final-tie; early quality rank-correlates positively with final quality; natural
  commit-once incidence low); then escalate to a larger transcript set. Toward KILL: flat
  checkpoint scores across runs, or no added resolution, or added resolution with near-zero or
  negative early-vs-final correlation (manufactured luck). A KEEP for variant (ii) additionally
  requires solving the mid-session scorer problem (Open questions); without a defensible scorer it
  dies on validity even with a passing pre-test.

## Alternatives

- **Snapshots as an instrument, not a grader.** Whole-workdir snapshots over the session are a
  useful diagnostic regardless of the result (did a late edit regress a good earlier state; what do
  trajectories look like per dataset). No grading claim, no gaming surface, cheap to keep.
- **Test-time commit schemes.** The live survivors on the other side of the agent-time/test-time
  divide (label-budget active learning, instrument installation with an arrival-weighted metric,
  bounded TEP compounding; §22a/§22c) remain the primary commit-mode bets. This file's scheme
  grades the session while they grade the stream, so a KEEP here would be an addition, not a
  competitor.
- **Efficiency as a trainer objective.** If the underlying goal is rewarding fewer-steps-to-strength,
  the clean home is reward shaping over many independent sessions (where session noise averages
  out), which a reinforcement-learning trainer controls and a single-session task grade does not.
  Checkpoint grading inside one session is the noisy version of that objective.

## Open questions

- **The mid-session scorer problem.** A snapshot taken while a model is training is not runnable.
  Zero-scoring it penalizes real work; last-good-state scoring rewards writing early and stalling;
  skipping non-runnable marks biases toward runs that write early. Is there a scoring rule for
  non-runnable snapshots that is neither punitive nor gameable? If the pre-test passes, this is the
  blocking design question for variant (ii).
- **Replicate structure for session noise.** Rigorously separating skill-ordered trajectory spread
  from session luck needs multiple sessions per skill level, but all runs use one fixed model, so
  "skill level" has no independent handle. The pre-test's rank-correlation readout is a proxy, not
  a proof. A principled replicate design (same task, deliberately perturbed session conditions?) is
  an open methodological problem shared by any scheme that grades session dynamics.
- **Signal half-life.** The unbounded-agent ceiling (step 2) implies the checkpoint signal shrinks
  as agents get faster at the offline homework. If the pre-test passes today, how quickly does
  model improvement erode the band? A wasting-asset scheme may still be worth building, but that
  should be priced in.
