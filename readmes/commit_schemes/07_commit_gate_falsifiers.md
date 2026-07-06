# 07 The commit gate: the pre-build falsifier battery

## The question

Before real student evaluations (expensive, user-gated) are spent on a commit-mode scheme, which
cheap tests rule the scheme out, in what order should they run, and what does surviving all of them
license? This is the commit-scheme analogue of the acquisition-spread gate (direction doc section
16), which correctly predicted student banding and packing before a single student ran, rebuilt
under two corrections. First, the band is the spread across REAL rollouts of VARYING strength
(folder README), so the primary evidence is a probe LADDER, several policies spanning naive to
sophisticated, not one simple-versus-rich pair. Second, agents are COMPUTATIONALLY BOUNDED and
computation generates information (file 00), so every kill in the battery must respect both the
insight axis and the compute axis: a measured tie kills, a paper claim that something "could have
been computed" does not.

## Background (terms defined)

- **Commit-mode scheme**, a task where the policy interacts with STATE that is not easily
  changeable: a commitment whose take-back is allowed but neither cheap nor easy (folder README,
  direction doc section 22). The commit may sit at test time (the online policy commits as it sees
  the stream) or at agent time (state that constrains test time).
- **Peek data**, the train and validation split, features and labels, fully available at agent time.
  It seeds a smart decider. The only permitted ignorance is of the gradually revealed test stream
  (which cases arrive, in what order). Hard constraint from the task owner (folder README).
- **Agent time (the session)**, the period the student works before shipping its artifact.
  **Grade time**, when the grader runs and drives the shipped policy; grade-time compute is bounded
  only by the platform's time cap.
- **The test stream**, the ordered sequence of test cases the grader reveals one at a time. The
  scheme reruns the shipped policy under **5 fixed stream seeds**; the score is the mean over the 5.
- **The band (the product)**, the dispersion of scores across real student rollouts of varying
  strength at a fixed budget. Measured, never computed (direction doc section 4).
- **Bounded agent** (file 00), an agent whose decision quality at any moment is a function of the
  compute it has ALREADY SPENT, not only of the data available to it. Session computation generates
  information (experiment results on peek, debugged code, late insights), so "could have computed X"
  does not mean "would have computed X by then." Consequence (file 00, the two-axis rule): a
  dominance or precomputability argument is a legitimate kill only when the dominant move is EASY to
  discover AND FAST to compute; naming an offline-computable optimum alone locates the ceiling and
  says nothing about the band below it.
- **Front-loading** (file 00, direction doc section 22b), the principle that grade-time compute is
  time-fungible: the platform cap is a total, it does not care WHEN compute is spent, so any
  grade-time improvement that needs only compute is dominated by doing the work in `__init__` before
  the first commit. The exemption is resources revealed by the stream itself (which rows arrived,
  purchased labels): by construction those arrive only mid-stream, so no amount of front-loaded
  compute substitutes for them.
- **Probe policy**, a hand-written throwaway `Policy` (the same `select_next` / `predict` contract
  the student ships, direction doc section 20) run through the REAL grader to stand in for a rung a
  real agent might land on.
- **Probe ladder**, an ordered set of 4 to 6 probe policies of increasing sophistication for the
  scheme under test, chosen to mirror rungs that weak, middling, and strong agents would plausibly
  occupy.
- **Level**, one statistically distinguishable score tier across runs (the SDK `rank_resolution`
  `n_levels` statistic in `sdk/hor_utils/noise.py`). The most important metric (CLAUDE.md). A wide
  spread with only 1 to 2 levels is a weak task.
- **Resolution**, the number of levels the test set supports at all: achievable score range divided
  by the grading noise floor. Capped by the RAREST class, not total rows, because balanced accuracy
  averages per-class recalls and a k-instance class has recall standard error about the square root
  of p(1 minus p) over k (direction doc section 18).
- **Seed-blocked analysis of variance**, the procedure that turns the 5-seed scores of a set of
  probes into levels. Lay the scores in a two-way table: one ROW per probe, one COLUMN per stream
  seed. Seed is a BLOCKING factor, a nuisance dimension removed rather than studied, because a given
  seed shifts every probe's score together (a lucky stream helps them all) and only differences
  BETWEEN probes matter. The analysis of variance splits the table's total spread into three parts:
  between-probes (the signal), between-seeds (the block, subtracted out), and the RESIDUAL (what
  remains, within-cell noise plus probe-by-seed interaction). Its output is the **pooled residual
  standard deviation**, the single noise estimate the battery uses.
- **Resolution gap, written Delta\***, the smallest difference between two probes' seed-averaged
  scores that counts as real rather than noise:

      Delta* = t_threshold  x  (pooled residual standard deviation)  x  sqrt(2 / S)

  where S is the number of seeds (5), `sqrt(2/S)` is the standard-error factor for a DIFFERENCE of
  two means each averaged over S seeds, and `t_threshold` is Student's t critical value at the
  residual degrees of freedom for the chosen confidence. Two probes whose mean scores differ by more
  than Delta\* are two levels; closer than Delta\* they are one. (In the SDK the same idea is
  realized by resampling in `rank_resolution`; Delta\* is its closed-form seed-space equivalent for
  a handful of probes over 5 seeds.)
- **Reachability of a rung** (file 00), its cost to a bounded agent, on TWO axes:
  **discoverability** (the insight axis: is the move a named textbook recipe, one obvious code
  pattern, or several compounding insights?) and **compute cost** (the time axis: how long the move
  takes to build and train once found, against the session and the grade cap). A rung must be judged
  on both; either axis alone misprices it.

## The process

The battery has five tests, presented in RUN ORDER, cheapest killer first; stop at the first kill,
since later tests cost grader runs an already-killed scheme does not deserve. Each test states its
procedure, probes, statistic, and kill threshold. Reasoning claims carry the folder's evidence tags.

How every probe runs (infrastructure, common to tests 2 through 4): probes are throwaway solutions
pushed through hosted VALIDATION runs against the real grader, never student evaluation runs and
never local heavy compute (CLAUDE.md). Ladder probes are near-identical policies differing in
`select_next`; push them together against the dedicated batch so the 5-seed scores come back as one
set for the seed-blocked table. Read scores and probe crashes from the full validation output files
(`tasks/<task>/.validation/<build_id>/output.txt`), never from the lossy one-line terminal summary.

### Test 1. Resolution floor (free arithmetic, no grader)

**What it rules out.** A dataset or config whose test split hosts too few levels for any scheme.

**Procedure.** Take the intended test split. For the scored metric (balanced accuracy unless the
scheme changes it), find the rarest class, count k. Its per-class recall standard error is about
`sqrt(p(1-p)/k)`, worst near `0.5/sqrt(k)`; the balanced-accuracy noise floor is roughly twice that
(a two-standard-error band). Estimate the achievable score RANGE over any plausible configuration:
the trivial constant or free-features-only policy for the bottom, the offline oracle or full panel
for the top. Levels available equal range divided by the floor.

**Statistic.** `range / noise_floor` (the arithmetic estimate of range over Delta\*).

**Kill threshold.** Below about **4**, KILL the dataset or config. [PROVEN] The cap is arithmetic
and no lever rescues it: Dermatology had rarest class 7, balanced-accuracy standard error about
0.035, range about 0.124, roughly 2 levels, and pooling all 366 rows by cross-validation still left
the rarest class near 20, about 3 levels at best (direction doc section 18). Widen the data instead
of chasing levers.

### Test 2. Vacuity / stream-information test (two probes, one paired gap)

**What it rules out.** A scheme whose commit structure is decorative: front-loaded compute over peek
already achieves everything that reading the stream achieves, so the stream prefix is not
load-bearing (direction doc section 22b, the information boundary).

**Procedure.** Build TWO versions of one middling probe, sharing the same predictor: one that
CONDITIONS its commits on the revealed stream prefix, and one whose commit schedule is FIXED from
peek, computed in `__init__` before the first commit. The twins must be COMPUTE-MATCHED: the
precomputed twin front-loads at least as much total compute as the stream-aware twin will spend, and
neither twin does mid-stream work the other lacks the budget for. This matters because grade-time
compute is time-fungible (front-loading, Background): twins that differ merely in WHEN they compute
would measure timing, and timing is an artifact any agent erases by moving the work into `__init__`.
Compute-matched, the measured gap isolates the one thing that resists front-loading: information the
stream itself reveals. Run both through the real grader across the 5 seeds.

**Probes.** The stream-aware probe versus its compute-matched, precomputed-schedule twin. Same
predictor, same total compute; the only difference is whether commits read the stream.

**Statistic.** `gap = score(stream-aware) - score(precomputed)`, against Delta\*.

**Kill threshold.** `gap <= Delta*`, KILL. [ARGUMENT] Note what kind of kill this is under the
corrected frame: not a paper precomputability claim ("the schedule is a pure function of peek"),
which file 00 shows proves only a ceiling, but a MEASURED tie through the real grader, the
legitimate form of a dominance kill (the simple, front-loadable twin ties the stream-aware one). The
worked contrast is the paid-revision analysis (direction doc section 22a): revision triggered by
compute alone is dominated by front-loading, but paired with a label budget the stream-aware policy
honestly beats every precomputed schedule, because purchased labels arrive only mid-stream.

### Test 3. Luck test (skill-identical replicates)

**What it rules out.** A scheme that manufactures score differences from luck rather than skill,
violating the owner's constraint that lucky blind first commitments must not move the score (folder
README).

**Procedure.** Write K skill-identical probe replicates (K about 4 to 6): the same strategy,
differing ONLY in arbitrary tie-breaks or which case they happen to commit on first. Run all K
through the real grader across the 5 seeds and lay them into the seed-blocked table.

**Probes.** K replicates of one strategy, seeded differently in tie-breaking or first pick, nothing
else.

**Statistic.** `n_levels` across the K replicates.

**Kill threshold.** More than **1** level, KILL. [ARGUMENT] If replicates of one skill separate, the
levels are minted from luck and the 5-seed mean is failing to average it out; a band built on that
is not a skill band and the owner rejects it (direction doc section 22). Small-chunk information
release is the standard mitigation when a scheme trips this: making each pick non-pivotal drains
first-pick luck (direction doc section 22a).

### Test 4. Ladder separation (the PRIMARY test)

**What it rules out.** A scheme whose skill ladder has too few rungs the test can resolve, so real
rollouts of varying strength would land on one or two scores. This replaces the old single
simple-versus-rich pair: a band is a spread across many strengths, so the evidence must be a ladder,
not one gap.

**Procedure.** Hand-write **4 to 6 probe policies** spanning naive to sophisticated for the scheme
under test. Span BOTH reachability axes across the rungs, not just one: some rungs should differ by
INSIGHT (a smarter rule at the same compute) and at least one pair by COMPUTE (the same rule given a
larger front-loaded training budget within the grade cap), so the ladder samples where bounded
agents actually differ (file 00). Run each probe through the real grader, hosted, across the 5
seeds. Build the seed-blocked two-way table, compute the pooled residual standard deviation and
Delta\*, order the probes by mean score, and count how many ADJACENT ladder steps separate by more
than Delta\*.

**Probes.** A representative ladder for a stream-facing commit scheme: (a) a constant or
free-features-only policy (floor); (b) a fixed offline-computed schedule (the test 2 twin can be
reused); (c) a textbook greedy rule reacting to the stream; (d) the same rule with a substantially
larger front-loaded training budget; (e) a richer adaptive rule that plans over the remaining
stream; (f) an optimistic near-oracle upper rung using realized values but never the label. Tailor
the middle rungs to the scheme; the point is a gradient of sophistication on both axes, not these
exact six.

**Statistic.** The count of adjacent-step separations exceeding Delta\* (equivalently the
`n_levels` the ladder resolves). This count IS the closing resolution check under real commit
dynamics; the old battery's separate "resolution range under the scheme" gate is folded in here.

**Kill threshold.** Fewer than **2** separated adjacent steps, KILL. **3 or more**, strong signal.
Exactly **2**, borderline: hold the verdict until test 5 reads the ladder's reachability.

**Why ladder separation predicts real-student banding.** [ARGUMENT] This world's record is
one-directional and consistent (direction doc sections 16 and 19; file 00): where probe policies of
differing sophistication separated by more than noise, real students banded, on covtype (students
spread 0.675 to 0.848, about 3 levels, with probe separation preceding it) and on the Tennessee
Eastman Process scaffold (probes climbing from fixed-best 0.79 to adaptive 0.81 to 0.84, the
optimistic probe 0.15 above fixed-best at budget 6, far beyond twice the noise; students then landed
fail, fail, 0.65, 0.80, 0.82). Where probes did NOT separate, students packed: the buried five
(PhysioNet, Diabetes-130, thyroid, UNSW-NB15, hydraulic), where a fixed panel tied the adaptive one
within noise and everything buried at 1 to 2 levels.

**Known limitations, both stated honestly.** [CONJECTURE] Our probes are our imagination; students
explore beyond it (direction doc section 4), so the ladder can under-count rungs (a strategy we did
not write) or over-count (a rung we can code but the graded agents do not find). And the probe
measures rung SEPARATION, not rung REACHABILITY: it prices neither the insight cost nor the
session-compute cost of building each rung (file 00). Test 5 covers reachability; neither test
replaces running students.

### Test 5. Discoverability audit, on both reachability axes (judgment plus wall-clock)

**What it rules out.** A ladder that separates for probes but flattens in practice because its rungs
are mispriced for the bounded agents we grade. Two failure shapes: a top rung cheap on BOTH axes, so
rollouts of every strength converge there and scores pack high; and middle rungs expensive on either
axis while floor and top are reachable, so the ladder collapses to bimodal (a floor cluster, a
ceiling cluster, no middle).

**Procedure.** Audit each rung of the surviving test 4 ladder on both axes.

The DISCOVERY axis is judgment, not measurement (file 00); do it honestly with three proxies:
- **Named recipe?** Does the strategy have a standard name and library support (forward selection,
  greedy value-of-information, Hyperband, random sampling as an active-learning baseline)? A named,
  library-backed move is highly discoverable.
- **One code pattern, or several compounding insights?** A move that is one obvious loop is far more
  discoverable than one needing several composed, non-obvious insights.
- **Seen in the record?** Search the recorded transcripts of past evals for the strategy. Whether any
  real rollout actually found it is the only direct evidence, the strongest proxy, though sparse and
  specific to agents already run.

The COMPUTE axis has a real number (file 00): WALL-CLOCK the rung's build-and-train on the task
machine and compare it to the session length, to the platform's grade-time cap, and to any commit
point the scheme places inside them. A rung that finishes in minutes is fast, flattened for
everyone; a rung whose build consumes a large fraction of the session separates agents by how early
they start it and how little they waste, even when its recipe is named. One more check on this axis:
a rung whose advantage is only that it computes LATER than another is no rung at all, since
grade-time compute is front-loadable (Background); discard it from the ladder before reading shape.

**Statistic.** None; a judgment call on the discovery axis, a measured wall-clock on the compute
axis. Report per-rung ratings (discovery high/medium/low, compute time versus session and cap) and
the resulting ladder shape.

**Kill / flag thresholds.** If the TOP rung is cheap on BOTH axes (named recipe, one pattern, fast),
FLAG collapse-high: agents of every strength likely reach it and pack, even though probes separated.
If the MIDDLE rungs are expensive on either axis while floor and top are cheap, FLAG bimodal.
[CONJECTURE] Neither flag is an automatic kill the way tests 1 to 4 are, because the discovery
proxies are weak; but a flagged scheme must not graduate on ladder separation alone. It needs the
strongest available proxy (the rung actually appearing in recorded transcripts, or a time-boxed
probe showing the compute axis genuinely spreads the climb) before student runs are spent.

## The result

**Graduation criterion.** A scheme graduates to real student evaluations only if it:
1. clears the resolution floor (test 1, range over Delta\* at least about 4);
2. is non-vacuous (test 2, the stream-aware twin beats its compute-matched precomputed twin by more
   than Delta\*);
3. is luck-free (test 3, skill-identical replicates resolve to one level);
4. separates on the ladder (test 4, at least 3 separated adjacent steps, or exactly 2 with a clean
   test 5 read);
5. carries no un-mitigated collapse-high or bimodal flag from the two-axis audit (test 5).

Student evaluations remain expensive and user-gated (CLAUDE.md): default 5 runs, hosted, every run's
link surfaced.

**What the battery can promise.** Only exclusion. Failing any test guarantees there is no band, for
the test's stated reason (direction doc section 5: falsifiers, not predictions). Each kill is either
arithmetic (test 1) or a MEASURED result through the real grader (tests 2 to 4), which keeps every
kill legitimate under the bounded-agent correction: no test in the battery concludes from "the
optimum is computable" or from "this could have been computed earlier," and no test assumes the
graded population is uniformly strong.

**What it does not promise.** [CONJECTURE] Passing never promises a band. The probe-to-student link
is an empirical record, one-directional so far (separation preceded banding, non-separation preceded
packing, direction doc sections 16 and 19); a scheme whose ladder separates and whose audit is clean
can still pack if real agents find a move our probes and proxies missed, and a single clean instance
of either direction breaking revises the battery (file 00 lists both flip conditions). Reachability
in particular is proxied, never measured: the discovery axis is judgment, and even the wall-clocked
compute axis prices our implementation of a rung, not every implementation an agent might write.

## Alternatives (when the pitfall is the data or the metric, not the scheme)

- **The data is the pitfall (resolution).** When test 1 kills, or test 4 finds real structure that
  stays inside Delta\*, the fix is bigger data with populous classes (direction doc section 18), not
  a richer scheme. Dermatology is the worked case: real routing structure, buried by a rarest class
  of 7.
- **The metric is the pitfall (coupling).** Balanced accuracy is invariant to the class arrival mix,
  so a scheme whose test-time uncertainty is "which classes arrive" scores identically across the
  axis it means to grade; it is NOT invariant to within-class composition (direction doc section
  22b). A vacuity or ladder failure on such a scheme may be the metric decoupling the skilled axis,
  not a missing ladder. Check metric coupling BEFORE running the battery on any composition-based
  scheme; the fix there is an arrival-weighted metric, and the battery is then rerun under it.

## Open questions (each worth a dedicated chat)

1. **How many probes make an honest ladder?** Four to six is asserted, not derived. Too few and a
   middle collapse hides (bimodal reads as separated); too many and we price our own imagination as
   if it were the student space. Calibrate against a scheme whose student band is already known
   (covtype).
2. **Can reachability be probed instead of judged?** The discovery axis wants a cheap "weak-agent"
   probe tier (a deliberately under-resourced policy locating the low rungs); the compute axis wants
   time-boxed probe tiers (the same probe-building process cut off at increasing compute budgets,
   scored through the real grader) to show whether commit points sit inside the rising part of the
   climb (file 00, open question 4). Either would turn the one-directional record into a two-sided
   calibration.
3. **Can a ladder's rungs invert against agent strength?** Skill is defined only by score (direction
   doc section 2), which admits a scheme where an over-engineered attempt lands below a crude one.
   If such an inversion exists, "richer beats simpler" mis-orders the ladder and the separated-step
   count overstates the band. Worth a targeted probe on any scheme with a plausible
   over-engineering trap.
4. **Compute-matching the vacuity twins when stream resources feed training.** In a label-budget
   scheme the stream-aware twin retrains on purchased labels; its precomputed twin can hold a fixed
   purchase schedule but must somehow spend matching compute without the adaptive information. A
   worked construction for "same compute, less stream information" in that setting is needed before
   test 2 is trustworthy there, precisely the scheme family where the vacuity test matters most.
