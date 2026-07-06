# 08 Ordering and roadmap: which commit-scheme pre-test to run, in what order, and why

## The question

Six live work items survive the commit-scheme analyses (`01_agent_time_commits.md` through
`06_paid_revision.md`, one deep-dive per scheme, all siblings in this folder), and one falsifier
battery (`07_commit_gate_falsifiers.md`, the pre-build gate every item runs through) applies to all
of them. Real student evaluation runs are expensive and user-gated,
so the work is a sequence of cheap hosted PRE-TESTS that rule schemes out before any student runs.
In what order should these six items run, and why? The answer has to be auditable (each ordering
choice derived from stated criteria, not asserted) and it has to be self-contained enough that an
agent with no other context can pick up any single item and know what it is, what it costs, what
kills it, and what a pass buys.

## Background (the bootstrap section, every term defined)

An agent reading only this section should be able to start any of the six items. Read the cited
sibling file (same folder) for the full reasoning behind each. Two out-of-folder sources recur:
"the direction doc" means `../README_general_direction.md` (the design bible; cited by section
number, sections 15 to 22 carry the history used here), and the operating constraints come from
`../../CLAUDE.md` (restated in the Operating rules subsection below so this file stands alone).

### The world

- **The task.** A student (a large language model coding agent) is handed a classification problem
  with a per-case acquisition budget. It ships a Python `Policy` class: `__init__(data_dir)` trains
  on fully visible training and validation data, `select_next(observed, budget_left)` chooses which
  feature to buy next, and `predict(observed)` returns a class. The student never predicts by hand;
  its code trains a model and the model predicts. See `../README_general_direction.md` section 20
  (what was built and why).
- **The mediated grader.** At grade time a grader process DRIVES the shipped policy row by row over
  a hidden test stream: for each row it runs select, reveal, predict, enforcing the budget itself
  and revealing only the feature values the policy paid for. Labels stay grader-only and are never
  transmitted. Because the grader owns the loop, it can also meter other resources (labels,
  installs) or advance a simulated world between cases. In code: `worlds/budgeted/verify.py` is the
  grader entry point that spawns and drives the policy; `worlds/budgeted/policy_runner.py` is the
  sandboxed subprocess harness the policy runs inside (dropped to an unprivileged user, no access to
  grader-only data); `worlds/budgeted/prompt_builder.py` builds the student-facing prompt
  (production framing, never grading language); `worlds/budgeted/data_view.py` applies config-driven
  hosted data transforms at setup time (drop features, cost overrides, per-class test balancing), so
  a data reshape is a config change plus a re-push, never a local rebuild. The built world runs on
  the anonymized Tennessee Eastman Process scaffold (task `budgeted-tep`) and on Forest CoverType
  (covtype, task `budgeted-covtype`); their identifiers are under Reference identifiers below.
- **Peek data (hard owner constraint).** The train and validation split, features AND labels, is
  fully visible to the student the whole session. It seeds a smart decider. The only permitted
  ignorance is of the test stream: which cases arrive, in what order. A scheme that forces decisions
  from withheld knowledge (blind first picks) is rejected, because there score differences are
  first-pick luck, not skill. See the direction doc section 22 (where this constraint is set).
- **Balanced accuracy.** The world's score metric: the mean of per-class recall (fraction correct
  within each true class), so every class counts equally regardless of how often it appears. It is
  invariant to the class ARRIVAL mix (changing how many of each class arrive does not change it),
  but NOT invariant to WITHIN-class composition (which rows of a class arrive). This coupling
  property decides several schemes (the direction doc section 22b; worked micro-example in
  `04_instrument_installation.md`, steps S6 to S8).

### The product and the metric

- **The band (the product).** The dispersion of scores across REAL student rollouts of VARYING
  strength at a fixed budget. It is measured across real runs, never computed from a portfolio of
  strategies we imagine. A task where every competent student lands on one score is worthless
  however high that score is.
- **Levels.** The number of statistically distinguishable score tiers across runs, the `n_levels`
  statistic of `rank_resolution` in `sdk/hor_utils/noise.py` (the code that counts levels lives
  there). This is the single most important metric (`../../CLAUDE.md`). A wide spread with only 1
  to 2 levels is a weak task; many resolvable levels is the goal.
- **The 5-seed protocol.** Evaluation reruns the shipped policy under 5 fixed stream seeds; the
  score is the mean over seeds; levels are counted by a seed-blocked analysis of variance (the seed
  is treated as a paired blocking factor, so the same seed's stream luck cancels when two policies
  are compared). A skill gap has to survive that averaging.
- **Delta-star.** The resolution gap: the seed-blocked analysis-of-variance threshold below which
  two scores count as one level. Roughly, a t critical value times the pooled residual standard
  deviation times the square root of (2 divided by the number of seeds). Two policies whose mean
  scores differ by more than Delta-star are two levels; closer than that, one. Levels are
  approximately the achievable score range divided by Delta-star, so there are two ways to add
  levels: widen true score gaps (add strategy rungs) or shrink Delta-star (reduce seed noise).
- **Resolution.** How many levels the test set supports at all, capped by the RAREST class (a
  k-instance class has recall standard error about the square root of p times (1 minus p) over k),
  not by total rows. Dermatology proved a real skill structure can bury on a rarest class of 7
  instances (the direction doc section 18, where resolution was made a pre-check).

### The corrected reasoning frame (the two owner corrections every file obeys)

The full derivation of this frame is `00_band_theory_what_collapse_arguments_prove.md` (the
reference file every other analysis cites); the corrections are restated here in full so this file
stands alone.

- **Skill ladder.** The ordered set of distinct-scoring RUNGS between the naive move and the
  optimum, each rung carrying a DISCOVERABILITY (how hard it is to think of) and a COMPUTE COST (how
  long it takes to build and train once thought of). A tall ladder with reachable middle rungs
  spreads agents of varying strength; a one-rung ladder stacks them.
- **Correction one, strength.** Nobody claims all agents are strong. A dominance argument ("one move
  is best, everyone converges to it") names the fixed point STRONG agents reach; it says nothing
  about where weaker agents land unless it ALSO shows the move is easy to discover. So "the optimal
  play is computable offline from peek data" is by itself only a CEILING statement. The working
  counterexample: on covtype a near-optimal per-row policy was computable offline, yet real students
  banded from balanced accuracy 0.675 to 0.848, about 3 levels (eval
  `babd012a-4ae2-4349-99cb-a030db3f4491`, 5 runs).
- **Correction two, bounded computation.** Agents are computationally bounded; computation during a
  session GENERATES information (experiment results on peek data, debugged code, late insights). So
  "could have computed X earlier" does not mean "would have." A precomputability claim kills only if
  the computation is also FAST (finishable by weak agents before the scheme samples their climb).
  The pairing of these two: a dominance or precomputability argument is a legitimate kill only when
  the dominant move is EASY to discover AND FAST to compute; otherwise it locates the ceiling and is
  silent about the band below.
- **Front-loading.** The grade-time cap (currently 600 seconds) is a total and does not care WHEN
  compute is spent, so any grade-time improvement needing only compute plus already-visible data is
  dominated by doing the work in `__init__` before the first commit. The one thing front-loading
  does not reach is a resource REVEALED mid-stream (a purchased label, an arrived row). This is the
  test that separates schemes with real temporal structure from decorative ones.
- **Probe ladder.** A hand-written set of throwaway `Policy` objects of increasing sophistication,
  run through the REAL grader via hosted validation (never student evaluation runs, never local
  heavy compute), to stand in for the rungs real agents would occupy. This world's record is
  one-directional: where probe policies of differing sophistication separated by more than noise,
  real students banded; where probes did not separate, students packed (the direction doc sections
  16 and 19, the acquisition-spread gate record). Probe separation is therefore the best
  pre-student predictor available, though it prices
  rung SEPARATION, not rung REACHABILITY, which stays partly a judgment call.

### The history this roadmap is trying to beat

- **Per-row budget is memoryless (the direction doc section 21).** The built world gives every case a
  fresh budget, so acquisition is adaptive within a row but memoryless across rows: the optimization
  is identical on every case, one best per-row policy exists, and competent agents converge to it.
  The strategy space is dominated; scores pack.
- **Plain global budget collapses (the direction doc section 22; `05_compounding_state.md` step P2
  spells out both halves).** Sharing one pool
  across an independent, identically distributed stream self-averages: the pool is a single scalar
  that concentrates around a smooth expected trajectory, and the counter-play is a per-row rule with
  one peek-calibrated price on cost. That counter-play is a textbook recipe, fits one code pattern,
  and is fast (one calibration sweep). Both axes of the two-axis rule line up, so this collapse is a
  legitimate kill, not a mere ceiling statement. Every surviving scheme has to break at least one of
  the two collapse ingredients: the self-averaging scalar state, or the easy-and-fast counter-play.

### One-paragraph state of each scheme (with file pointer)

- **Agent-time commits (`01_agent_time_commits.md`).** Grade the student's own working session, not just its final
  artifact: fix state early (early lock-in), or snapshot the deliverable at wall-clock marks and
  aggregate (checkpoint grading), or restrict rewrites (append-only). The append-only variant is
  KILLED by proven exploits (Python shadowing makes text-level append-only behaviorally vacuous;
  scratch-space laundering defeats file-level snapshots). Early lock-in and checkpoint grading are
  UNDECIDED BY ARGUMENT (both collapse arguments failed, one idealizing strength, one idealizing
  computation) and are settled by the transcript-replay pre-test (this roadmap's item 1). The
  standing threat is that the 5 seeds re-grade a fixed session and never re-run it, so session noise
  stays un-averaged.
- **Small-chunk information release (`02_small_chunk_information_release.md`).** A purchase returns a NOISY reading of a feature
  value; buying again refines it by averaging. A first-round KILL was OVERTURNED to a pre-test: the
  averaging attack bounds only the ceiling, the scheme CONTAINS the discrete world that banded,
  acting on partial posteriors adds middle rungs the discrete world has no room for, and its
  luck-smoothing shrinks Delta-star, which by itself raises measurable levels. This roadmap's item 3.
- **Train-label budget (`03_train_label_budget.md`).** Ship the training features visible but hide the training labels;
  the student BUYS labels one row (or batch) at a time from one shared budget, through the mediated
  reveal loop retargeted from feature reveal to label reveal. This is active learning turned into
  the task. KEEP, the strongest survivor: strong on infrastructure and on non-dominance (active
  learning is a field defined by the absence of a dominant acquisition rule), with resolvable rungs
  below the random baseline (broken loop, cold-start uncertainty), at it (random), and above it
  (coreset, hybrid, budget scheduling, semi-supervised). Purchased labels are the one resource
  front-loading does not reach. Gated on the acquisition-strategy ladder pre-test. This roadmap's
  item 2.
- **Instrument installation (`04_instrument_installation.md`).** Installing an instrument (a feature group) costs a large
  one-time amount from a shared pool; once installed, reading its features on any later row is free
  or cheap. FIX-FIRST: as specified (free reads, balanced accuracy, class mixtures) it is PROVEN to
  collapse to fixed-panel selection, and balanced accuracy is invariant to the class arrival mix, so
  the install decision is not stream-dependent. Two repairs are live, one surer (switch to an
  arrival-weighted metric, so the optimal panel provably flips with the class mix) and one
  metric-preserving but conjectural (drive seed variation with within-class DIFFICULTY mixtures,
  betting covtype's soil structure makes the best panel rotate rather than merely escalate). The
  regret-matrix pre-test decides. This roadmap's item 4.
- **Compounding state (`05_compounding_state.md`).** The policy's own early actions change the later environment. The
  live variant is consequence dynamics: a case handled wrongly comes back later, harder and worth
  more. SURVIVES fix-first but honest ONLY on the Tennessee Eastman Process (TEP), whose simulator
  supplies real propagation physics (on a static dataset like covtype the dynamic would be
  fabricated). Conditional on a compounding gain g strictly below 1 (a severity cap plus
  force-resolution after k returns), which simultaneously bounds luck and keeps the seed-blocked
  noise model valid. Congestion pricing and scalar backlog KILL (concentrating scalar state plus an
  easy-and-fast counter-play). TEP is a simulation and hence a scaffold, not the shippable product.
  This roadmap's item 5.
- **Paid revision (`06_paid_revision.md`).** During the stream the policy commits a prediction per row and may pay
  to revise a past one. KILL as a standalone scheme (the stream's only novel external signal is its
  class mixture and balanced accuracy neutralizes it; the compute channel is dominated by
  front-loading; revision value is a vanishing boundary effect; the two optima are easy single
  moves). SURVIVES only PAIRED with the label budget: one pool funds both buying labels and revising
  past predictions, so the late model is honestly better than the early one (it was trained on
  labels bought after the early rows committed), revision cashes a non-vanishing learning-curve
  integral, and a genuine labels-versus-revision rationing tradeoff with no dominant rule appears.
  Contingent on item 2 passing. This roadmap's item 6.
- **The commit gate (`07_commit_gate_falsifiers.md`).** The pre-build falsifier battery every item runs through: test 1
  resolution floor (free arithmetic), test 2 vacuity (a stream-aware probe versus its
  compute-matched precomputed twin), test 3 luck (skill-identical replicates must resolve to one
  level), test 4 ladder separation (the primary test, 4 to 6 probes, count adjacent separated
  steps), test 5 discoverability audit (judgment on discovery, wall-clock on compute). Run cheapest
  killer first, stop at the first kill.

### Operating rules (non-negotiable, from `../../CLAUDE.md` and this folder's `README.md`)

A new agent picking up any item must obey all of these; they are restated here so no other file is
needed to work safely.

- **Heavy compute is NEVER run locally.** The owner's machine is a weak laptop; unapproved heavy
  local runs have crashed it twice. Heavy means model training, budget sweeps, policy replay, and
  even LOADING or building a dataset (a "quick" comma-separated-values read or a train/test split
  on real data counts). The default home for all of it is HOSTED: a throwaway task whose VALIDATION
  run performs the computation and returns the result. Any non-trivial local run requires explicit
  owner approval BEFORE it starts. Always allowed without approval: pollers and monitors of hosted
  jobs, tiny instant work, file edits, configuration, git, network calls to the hosted services.
- **Every student evaluation run is user-gated.** Never launch one unprompted. Defaults when the
  owner approves: 5 runs, model `biggie-max-polara`, agent-type `meteor`, machine-type
  `e2-custom-16-32768`. Whenever an evaluation is submitted or running, surface the direct run link
  `https://horizon.bespokelabs.ai/evaluations/<eval-id>` together with the task link
  `https://horizon.bespokelabs.ai/tasks/<task-id>`, as soon as the identifiers are known and again
  when results land.
- **The platform's 600 second grade cap is the ONLY timeout.** Never impose a shorter grader-side
  watchdog and never reduce a timeout below the platform's. A hanging policy is killed by the cap
  and scores low; that is correct behavior, not a bug to guard against.
- **Read validation logs from the file, never the terminal.** The hosted validate prints a lossy
  one-line summary; the full Docker build log and traceback are saved to
  `tasks/<task>/.validation/<build_id>/output.txt`. Never debug from the terminal summary.
- **Deliverable contracts.** The student ships a SINGLE Python file (`solution.py`) whose class the
  grader drives; nothing else the student writes is graded. Each analysis file in this folder is
  likewise a single self-contained document the owner reads independently.
- **Writing rules for these files.** Never use the em-dash character, and never substitute a double
  hyphen for one; use a comma, period, or parentheses. No unexplained abbreviations: spell out
  active learning, Tennessee Eastman Process, analysis of variance, and so on at first use.
  Reasoning steps carry the [PROVEN] / [ARGUMENT] / [CONJECTURE] tags, and no verdict is stated
  before the reasoning that produces it. To the student, always production framing, never grading
  language.

### Reference identifiers (what a new agent needs to touch the existing artifacts)

- **budgeted-covtype**: task `4de1e511-7738-4889-bed3-a0a532b051e5`; its banded 5-run student eval
  is `babd012a-4ae2-4349-99cb-a030db3f4491` (balanced accuracy 0.675 to 0.848, about 3 levels).
- **budgeted-tep**: task `36abdac8-4edd-4304-a48c-53933cd34f62` (the Tennessee Eastman Process
  scaffold; its recorded student outcomes were fail, fail, 0.65, 0.80, 0.82).
- **mini_batch_id** for the FIRST push of any new throwaway task:
  `0067d7a3-4134-40d9-a4eb-c29faeeb24fe`.
- Command-line prerequisites: `source horizon_env/bin/activate` from the repo root first, and
  always name the task explicitly in push and validate commands.

### The six items, named

1. **Transcript-replay pre-test** (`01_agent_time_commits.md`, step 6 gives the full procedure):
   parse the recorded transcripts of the covtype eval (`babd012a-4ae2-4349-99cb-a030db3f4491`,
   5 runs) and the budgeted-tep scaffold eval, reconstruct workdir snapshots at 25, 50, 75, and 100
   percent marks, score about 40 snapshots via hosted throwaway validation, read out final-tie
   resolution, early-versus-final rank correlation, and commit-once incidence.
2. **Label-budget pre-test** (`03_train_label_budget.md`, the strongest survivor; step P17 gives
   the gates): build the metered label-reveal probe harness (retarget of the mediated drive loop in
   `worlds/budgeted/verify.py`), run the acquisition-strategy ladder (random, uncertainty, margin,
   coreset, hybrid, budget-scheduler) at a budget swept to bind, on covtype (optionally reshaped
   with a pool-imbalance transform in `worlds/budgeted/data_view.py`), 5 seeds, hosted; includes
   the adaptive-versus-precomputed-schedule vacuity gate.
3. **Small-chunk pre-test** (`02_small_chunk_information_release.md`, step 7 gives the probes):
   build a noisy-mediator probe harness (a sample returns value plus Gaussian noise, repeated buys
   refine), run the five-probe ladder at matched budgets plus the decisive seed-variance comparison
   against the discrete world plus the averaging-attack degeneracy probe.
4. **Instrument-installation portfolio-regret pre-test** (`04_instrument_installation.md`, Part G
   gives the construction): train one masking predictor from peek hosted, compute the
   portfolio-by-mixture regret matrix in BOTH repair variants (arrival-weighted metric;
   within-class difficulty mixtures), kill if one affordable portfolio is uniformly near-optimal.
5. **TEP consequence-dynamics build plus probes** (`05_compounding_state.md`, steps P5 to P11):
   the heaviest item, the grader advances simulator state, g strictly below 1 tuning, probe ladder
   plus amplification probe; honest only on the Tennessee Eastman Process, which is scaffold-only.
6. **Paid-revision pairing** (`06_paid_revision.md`, steps R9 to R14): contingent extension of
   item 2 (one pool funds labels AND revisions); only meaningful after item 2 passes its gate.

## The process

Five ordering criteria are used, and where they conflict the winning one is named. The criteria:
cost to first result (build effort plus hosted runs), probability the pre-test passes (from each
file's argument strength), value of information (how much an early result redirects later work),
dependency structure (what must precede what, and what components are shared), and product value (a
deployable real-data task beats a scaffold demo). Each step below reads forward and is tagged
[PROVEN] (a reduction or a structural fact from the files), [ARGUMENT] (a judgment backed by the
files' evidence), or [CONJECTURE] (a claim that a run would settle).

**O1 [PROVEN], the one hard precedence.** `06_paid_revision.md` defines item 6 (the paid-revision
pairing) as an extension of item 2's (the label-budget scheme, `03_train_label_budget.md`) shared
pool, and step R9 there establishes that revision does something plain per-row play does not ONLY
when the late model is honestly better than the early one, which happens only when labels are bought
mid-stream (R3, R3b, R3c ruled out every other source). So item 6 has no measurable content until
item 2's label-reveal harness exists AND item 2 has passed its dominance gate (if the label half
does not band, R12 and open question 1 of file 06 say revision has nothing to cash and the pairing
dies with it). Item 6 after item 2 is not a preference; it is structural. No other hard precedence
exists among the six.

**O2 [ARGUMENT], cost to first result, ranked.** Item 1 (the transcript-replay pre-test,
`01_agent_time_commits.md`) is the cheapest by a wide margin: it needs NO new world mechanic. It
parses transcripts that already exist, replays file edits locally to reconstruct workdir snapshots
(tiny text work, no data loading, no approval-gated compute, per `01_agent_time_commits.md` step
6.1), and scores about 40 snapshots through the EXISTING covtype and TEP graders as throwaway
hosted validations. Items 2, 3, and 4 are moderate: item 2 retargets the mediated reveal loop in
`worlds/budgeted/verify.py` from feature values to labels and adds a pool-imbalance transform to
`worlds/budgeted/data_view.py`; item 3 (the small-chunk pre-test,
`02_small_chunk_information_release.md`) adds a Gaussian-noise mechanic to the reveal loop; item 4
(the instrument-installation pre-test, `04_instrument_installation.md`) trains one masking
predictor and assembles a mostly offline regret matrix. Item 6 is cheap to build GIVEN item 2 (it extends that harness with a
revision ledger and anti-batch forcing) but is zero until item 2 exists and passes. Item 5 (the
Tennessee Eastman Process consequence-dynamics build, `05_compounding_state.md`) is the
heaviest: it puts consequence dynamics inside the grader (state advanced between cases,
re-perturbation of returning cases, g tuning, force-resolve and corner pricing) and needs the most
probe runs. Cost-to-first-result order, cheapest first: 1, then {2, 3, 4} close together, then 6
(conditional), then 5.

**O3 [ARGUMENT], probability of an actionable pass, from each file's verdict.** Item 2 is the
strongest: file 03's verdict is KEEP, it is strong on infrastructure and on non-dominance, and its
one real empirical risk (random sampling is a strong baseline on large redundant tabular pools) has
a named mitigation (the pool-imbalance transform) before the dataset is abandoned. Item 3 is
promote-to-pre-test with a floor argument (it contains covtype, which banded) and a make-or-break
unknown (does an "alive regime" exist where fully recovering a value costs more than the budget, so
partial-posterior play is forced). Item 4 is fix-first: as specified it is PROVEN inert under the
standard metric, so a pass requires a repair to land, either a metric change (surer but deviates
from the world's standard metric) or a conjecture about covtype's soil structure rotating the best
panel; its band-certainty is the weakest of the real-data three. Item 5 survives fix-first but only
on a scaffold, and its pass is conditional on g tuning AND the probe ladder separating AND the
amplification probe staying sub-noise. Item 1 is genuinely undecided by argument and has a LOW
actionability ceiling even on a pass: a KEEP only escalates checkpoint grading to a larger
transcript set (5 runs is a smell test, too few for the levels statistic) and still needs the
mid-session scorer problem solved, and the recorded runs had no checkpoint rule so they under-test
early lock-in. Item 6 has a strong FORM (its rationing tradeoff is exactly the non-dominated space
direction doc section 21 chased) but is fully contingent on item 2.

**O4 [ARGUMENT], value of information, ranked.** Item 3 carries the highest cross-cutting value: its
seed-variance measurement (run one probe at 5 seeds under both the noisy and the discrete scheme,
compare the analysis-of-variance residual) measures Delta-star, the DENOMINATOR of the levels
statistic, and small-chunking is also the standard luck mitigation the whole battery leans on
(`07_commit_gate_falsifiers.md` test 3, the skill-identical-replicates luck test). A number there
informs every other scheme's resolution accounting. Item 4's masking
predictor is reusable: a masking-robust predictor (train on random feature subsets so inference
accepts any partial observation) is the standard first engineering step every real-data item here
needs, so building it once for the earliest build de-risks the rest. Item 1's value is a cheap,
whole-branch verdict (does grading the session, not just the artifact, add skill-ordered resolvable
levels) bought for about 40 gradings and no build. Item 2's value includes gating item 6 entirely.
Item 5's value is narrow (it validates one scaffold-only mechanic) and item 6's value is realized
only after item 2.

**O5 [ARGUMENT], product value, ranked.** Items 2, 3, and 4 run on covtype, a real, large,
many-class dataset, so a pass points at a deployable task. Item 2 is highest: file 03 step P4 notes
its test pass is a single batched prediction rather than a per-row drive, so the test split can be
large again and the grading is both cheaper and higher-resolution than the world already built.
Item 5 runs on the Tennessee Eastman Process, which direction doc section 19 keeps as a SCAFFOLD
(it is a simulation, and a public benchmark), so even a clean pass validates the pipeline rather
than shipping the durable product. Item 1 is a grading-MODE question orthogonal to which dataset
ships; file 01 is explicit that a KEEP there is an ADDITION to a stream-facing scheme, not a
competitor to it. So on product value the real-data builds beat the scaffold, and item 2 leads.

**O6 [ARGUMENT], parallelism, honestly.** The machine rule is hosted-only and student evaluation
runs are user-gated, but probe validations are cheap throwaway pushes, though still real pushes, so
they are batched rather than fired one at a time. Item 1 shares NO components with any build (it runs
on the existing graders), so it runs concurrently with the first build and returns its result first.
Items 2, 3, and 4 share a masking-robust or shared predictor, so that predictor is built once and
reused rather than three times. Item 5 shares only the drive-loop skeleton and the TEP data. Item 6
shares item 2's entire harness. So the only genuine concurrency worth exploiting is item 1 alongside
item 2; the rest of the builds contend for the same reveal-loop code and the same shared predictor
and are better run in sequence so each reuses the last one's components.

**O7 [ARGUMENT], resolving the criteria into an order.** The first contested adjacency is 1 versus 2
at the front. Cost-to-first-result and value-per-cost favor item 1 (no build, banks a branch
verdict); probability-of-actionable-pass and product-value favor item 2 (the main line). O6
dissolves the conflict rather than picking a loser: the two share nothing, so both go first, item 1
returning first because it is cheapest and item 2 proceeding as the lead build. After that pair, item
3 is placed ahead of the remaining builds because its cross-cutting value of information wins (O4):
its Delta-star measurement de-risks the levels accounting for every scheme, and it reuses item 2's
reveal-loop retarget pattern and shared predictor. Item 6 comes next because the hard precedence (O1)
lets it start the moment item 2 passes, its FORM is the strongest of the remaining items (O3), and it
is cheap given item 2 (O2); it is placed after item 3 because it is contingent on item 2's result
while item 3 is not, and because item 3's metric measurement informs item 6 too. Item 4 follows: it
is real data (beating item 5 on product value, O5) but its band-certainty is the weakest of the
real-data set (O3, proven inert without a repair). Item 5 is last on the clearest margin: heaviest to
build (O2), scaffold-only product (O5), and narrowest value of information (O4); it is run only if
the real-data survivors disappoint, or on a separate pipeline-validation track that never displaces
them.

**O8 [ARGUMENT], why each survivor makes a MORE CERTAIN band than the history.** Tie each to the two
collapse ingredients of the history (a self-averaging scalar state, and an easy-and-fast
counter-play, stated in the Background history subsection). The label budget (item 2) replaces the scalar self-averaging pool with
an ENDOGENOUS, path-dependent state (the labeled set plus the remaining pool, chosen by the student),
so the self-averaging step has nothing to average, and purchased labels are the one resource
front-loading does not reach, so the session keeps genuine temporal structure (file 03 P7, P19).
Small-chunk (item 3) attacks the metric's denominator directly: its luck-smoothing shrinks
Delta-star, which raises measurable levels even before any new strategy rung, and it contains a world
that already banded (file 02 steps 2, 5). Paid-revision-paired (item 6) opens a labels-versus-revision
rationing tradeoff with no dominant rule, the exact non-dominated space section 21 named (file 06
R11). Instrument installation (item 4), once repaired, makes the install decision genuinely
stream-dependent so the counter-play is no longer a peek-calibrated constant (file 04 S12). TEP
consequence dynamics (item 5) makes state high-dimensional and action-coupled, so two policies
diverge under their own choices and no scalar shadow price has a foothold, with g strictly below 1
holding luck bounded (file 05 P3, P7). Item 1 does not add a scheme; it tests whether grading the
climb itself (which bounded agents traverse at different speeds) resolves skill-ordered levels the
final artifact ties.

**O9 [CONJECTURE], the ordering is a priority list, not a strict serialization.** The steps above
rank the items by expected payoff per unit cost, but hosted throwaway validations are cheap enough
that a fast pre-test can overtake a slow build. The intended reading: item 1 and item 2 start
together, item 3 follows the moment item 2's reveal harness and shared predictor exist, item 6 fires
when item 2 passes its dominance gate, item 4 runs whenever the shared predictor is free, and item 5
is held to last. A single early kill or an early large seed-variance number could reorder the tail;
the "What evidence would reorder this" subsection of The result lists the specific evidence.

## The result

### Status tracking

Every per-item block below carries a **Status.** line, and that line
is the single source of truth for where the item stands. (Open questions track separately: each is
OPEN until a chat resolves it, then prefix it RESOLVED with the deciding fact.) The ordering list right below is a
priority ranking, not a status board, do not duplicate status into it. Set each **Status.** to
exactly one of:

- **NOT STARTED** — no build, no hosted run yet.
- **BLOCKED (on X)** — cannot begin until X resolves; always name X.
- **IN PROGRESS** — build or hosted pre-test underway; note what has run.
- **PASSED** — its gate cleared; record the deciding eval id.
- **KILLED** — a falsifier fired; record which falsifier and the eval id.

Update the line the moment an item's state changes, and put the deciding eval id or falsifier in
parentheses so the history is auditable from this file alone. As of this writing all six are
NOT STARTED (correct any that are already underway).

### The ordering

1. **Transcript-replay pre-test (item 1, `01_agent_time_commits.md`)**, run immediately,
   concurrent with item 2. Cheapest, no new mechanism, first result, independent, banks a
   whole-branch verdict on agent-time grading.
2. **Label-budget pre-test (item 2, `03_train_label_budget.md`)**, the lead build and main line.
   Highest pass probability and product value, builds the reusable label-reveal harness and shared
   predictor, and gates item 6.
3. **Small-chunk pre-test (item 3, `02_small_chunk_information_release.md`)**, highest
   cross-cutting value of information (measures Delta-star, the levels denominator), reuses item
   2's reveal-loop pattern.
4. **Paid-revision pairing (item 6, `06_paid_revision.md`)**, contingent on item 2 passing;
   strongest FORM among the remaining items, cheap as an extension of item 2's harness.
5. **Instrument-installation portfolio-regret pre-test (item 4, `04_instrument_installation.md`)**,
   real data, but weakest band-certainty (proven inert without a repair), reuses the shared masking
   predictor.
6. **TEP consequence-dynamics build plus probes (item 5, `05_compounding_state.md`)**, heaviest
   build, scaffold-only product, narrowest value of information; last, or on a separate
   pipeline-validation track.

### Per-item blocks

Each block: what to build or parse, rough cost, the risk (with the file's probability-flavored
tag), the reward (including reusable components), and why the scheme makes a more certain band than
the per-row and global-budget history.

**1. Transcript-replay pre-test (`01_agent_time_commits.md`).**
- **Status.** NOT STARTED. Its TEP half is BLOCKED on open question 6 (confirm the TEP eval id via
  `horizon evaluations list`) before the parser is built; the covtype half
  (`babd012a-4ae2-4349-99cb-a030db3f4491`) is unblocked.
- **Requires.** A transcript parser plus edit-replayer that reconstructs the full workdir (not just
  `solution.py`, per the laundering result) at 25, 50, 75, and 100 percent of each run's session
  length, for the covtype eval `babd012a-4ae2-4349-99cb-a030db3f4491` (5 runs, task
  `budgeted-covtype`, `4de1e511-7738-4889-bed3-a0a532b051e5`) and the Tennessee Eastman Process
  scaffold eval (5 runs, task `budgeted-tep`, `36abdac8-4edd-4304-a48c-53933cd34f62`; its eval id
  is flagged in Open questions). Score each runnable snapshot through the EXISTING mediated grader
  (`worlds/budgeted/verify.py`) as a throwaway hosted validation. Record non-runnable snapshots (mid-edit, model still training) as data, not
  errors.
- **Costs.** Local text work for the parser and replayer (no data loading, no approval-gated
  compute). About 40 hosted throwaway gradings (5 runs times 4 marks times 2 datasets). No new world
  mechanic, no student runs. The cheapest item.
- **Risk / kill.** UNDECIDED BY ARGUMENT [ARGUMENT]. Killed if checkpoint scores are near-identical
  across runs at every mark (no mid-session spread to grade), or the aggregate adds no resolution
  over the finals, or it adds resolution but the early-versus-final rank correlation is near zero or
  negative (the added levels are un-averaged session luck; the 5 stream seeds re-grade a fixed
  session and never re-run it, so session noise is not averaged, `01_agent_time_commits.md` step 5
  [PROVEN]). Even a
  KEEP has a low actionability ceiling: it only escalates to a larger transcript set and still needs
  a defensible mid-session scorer (open question in file 01), and the recorded runs under-test early
  lock-in because they had no checkpoint rule.
- **Reward.** A cheap, clean verdict on an entire branch (grade the session, not just the artifact).
  A KILL drops the branch for about 40 gradings. A KEEP is an ADDITION to a stream-facing scheme,
  not a competitor. The reconstructed snapshots are a reusable diagnostic (trajectory shapes per
  dataset) regardless of the verdict.
- **Band certainty versus history.** It does not add a scheme; it tests whether the temporal climb
  bounded agents traverse (`00_band_theory_what_collapse_arguments_prove.md` steps R3 and R6) is
  itself a skill-ordered, resolvable axis that final-only
  grading ties. If the early-versus-final correlation is clearly positive, mid-session state is
  skill-ordered and grades a rung the final artifact hides.

**2. Label-budget pre-test (`03_train_label_budget.md`).**
- **Status.** NOT STARTED.
- **Requires.** Retarget the mediated reveal loop (`worlds/budgeted/verify.py`, with the sandboxed
  subprocess harness `worlds/budgeted/policy_runner.py`) from revealing feature VALUES at test
  time to revealing LABELS at training time: `/data_agent` exposes the full feature matrices
  unlabeled plus the budget L, `/data_root` holds the labels and test split, the policy's grade-time
  session is a round-based `select_queries` loop the grader drives, ending in one batched test
  prediction per seed. A shared ordinary predictor across all probes. A six-rung acquisition ladder
  (random, least-confident uncertainty, margin or entropy with calibration, k-center coreset,
  BADGE-style hybrid, budget scheduler; BADGE is Batch Active learning by Diverse Gradient
  Embeddings, defined in `03_train_label_budget.md`). A pool-imbalance transform (`pool_per_class`
  in `worlds/budgeted/data_view.py`) as the reshape lever. Per-seed test-split resampling as the primary seed axis (so every probe has
  honest within-run variance).
- **Costs.** Moderate build (new reveal semantics, but reuses the drive loop, the sandbox isolation,
  and the `data_view.py` pattern). Hosted runs: the five gates of `03_train_label_budget.md` step
  P17, chiefly gate 2 (six probes
  times 5 seeds) and gate 4 (an L-sweep per rung), plus the cheap gates 0, 1, 3. No student runs.
- **Risk / kill.** KEEP, gated [ARGUMENT / CONJECTURE on magnitudes]. Killed if gate 1 fails (no
  label-adaptive rule beats the best precomputed label-free schedule by more than Delta-star, so the
  reveal loop is decoration), or gate 2 fails (at every L where the classes are learnable the best
  rung ties random within Delta-star; the real empirical risk, since random is strong on large
  redundant tabular pools), or gate 0 fails (range over Delta-star below about 4 even with the
  enlarged batched-predict test set). All three are cheap hosted checks.
- **Reward.** The strongest survivor graduates toward student runs. Reusable components: the
  label-reveal harness and the shared predictor are exactly what item 6 extends, and the shared
  predictor plus the reshape pattern carry to items 3 and 4. Per file 03 step P4 the grading is
  cheaper and higher-resolution than the current world.
- **Band certainty versus history.** Active learning is a field defined by the ABSENCE of a dominant
  acquisition rule (file 03 P11), so the upper rungs do not collapse onto one move. The state (the
  labeled set plus remaining pool) is endogenous and path-dependent, so the self-averaging that
  killed the global pool has nothing to average (P19), and purchased labels are the one resource
  front-loading does not reach (P7), so the session keeps genuine temporal structure. There are
  resolvable rungs BELOW the baseline (broken loop, cold-start uncertainty), which widens the ladder
  on the low side the way covtype's engineering rungs did.

**3. Small-chunk pre-test (`02_small_chunk_information_release.md`).**
- **Status.** NOT STARTED.
- **Requires.** A noisy-mediator probe harness: a purchase of feature j returns the true value plus
  a fresh Gaussian draw of known standard deviation; buying again gives an independent draw;
  averaging refines. One shared masking-robust predictor across probes. A five-probe ladder at
  matched total budget (random allocator, fixed per-row sample count, greedy expected-information-gain,
  a sequential-testing stopping rule, an offline Monte-Carlo-planned allocation). The decisive
  seed-variance comparison (one probe at 5 seeds under both the noisy scheme and the discrete
  scheme, compare the analysis-of-variance residual). The averaging-attack degeneracy probe (compute
  the break-even number of reads, buy exactly that many, play the discrete world).
- **Costs.** Moderate build (a noise mechanic in the reveal loop plus a running posterior in the
  probes). Hosted runs: five ladder probes plus the two-scheme seed-variance run plus the degeneracy
  probe, 5 seeds each. No student runs.
- **Risk / kill.** PROMOTE TO PRE-TEST [ARGUMENT with a make-or-break CONJECTURE]. Killed if the
  noisy mechanic COMPRESSES the spread below the discrete world's (all of: the greedy, sequential,
  and planned probes packing within Delta-star of the fixed and random probes, AND the measured seed
  variance failing to fall below the discrete world's, AND no price-and-noise regime avoiding the
  three degenerate corners). Equally fatal: the "alive regime" not existing on real data (the
  break-even number of reads is always either trivially cheap or unaffordable, with no middle), which
  the degeneracy probe is the cheapest test of.
- **Reward.** A pass adds an uncertainty-management ladder the discrete world has no room for, and,
  crucially, a measured value for how much luck-smoothing shrinks Delta-star. Reusable: the
  Delta-star measurement recalibrates the levels accounting for EVERY other scheme, and the noise
  mechanic is the general first-pick-luck mitigation the whole battery relies on
  (`07_commit_gate_falsifiers.md` test 3, the luck test).
- **Band certainty versus history.** Two mechanisms point the same way. It shrinks the DENOMINATOR of
  the levels statistic (file 02 step 5): with smaller seed noise, smaller true gaps become resolvable,
  so measured levels rise even with no new rung. And it CONTAINS the discrete world that already
  banded at about 3 levels (step 2), so absent a positive compression argument its levels are at
  least covtype's.

**4. Paid-revision pairing (`06_paid_revision.md`).**
- **Status.** NOT STARTED, BLOCKED on item 2 passing its dominance gate (hard precedence O1).
- **Requires.** Built ON TOP of item 2's label-reveal harness: one shared pool funds both buying
  labels and revising past committed predictions. A revision ledger and price `c_rev`. Anti-batch
  forcing so it does not collapse to offline batch active learning: mandatory per-row commit at
  arrival plus a revision window (or a rising revision price). Refunds excluded (a revealed value
  cannot be un-seen, PROVEN-dead, file 06 R1).
- **Costs.** Low GIVEN item 2 (extends that harness), zero until item 2 exists and passes its
  dominance gate. Hosted runs: the pairing's own probe ladder plus commit-gates 1, 2, 3 of file 07.
  No student runs.
- **Risk / kill.** Contingent SURVIVOR [ARGUMENT / CONJECTURE]. It inherits item 2's active-learning
  falsifier (if random ties canonical acquisition on covtype, the label half does not band and
  revision has nothing to cash, file 06 open question 1), needs the anti-batch forcing to hold
  (else the dominant move is buy-all-labels-then-predict-once, R12), and carries a seed-by-strategy
  luck residual (which labels a seed's early stream lets you buy, R13) that has to resolve to one
  level under commit-gate 3.
- **Reward.** The strongest FORM of a rationing scheme: one pool, two competing uses (more labels
  versus cashing the current better model onto past rows) with no dominant split. Reuses item 2's
  entire harness and inherits item 3's Delta-star measurement.
- **Band certainty versus history.** The late model is honestly better than the early one because it
  was trained on labels bought AFTER the early rows committed, so revision cashes a non-vanishing
  learning-curve integral rather than a shrinking boundary tail (file 06 R10), and the
  labels-versus-revision tradeoff is exactly the non-dominated space direction doc section 21 chased
  and the plain global pool collapsed out of (R11).

**5. Instrument-installation portfolio-regret pre-test (`04_instrument_installation.md`).**
- **Status.** NOT STARTED.
- **Requires.** Train ONE masking-robust predictor from peek (hosted). Enumerate the affordable
  install portfolios (a few dozen of the 128 subsets of about 7 instruments). Compute the
  portfolio-by-mixture regret matrix in BOTH repair variants: variant D (arrival-weighted metric,
  columns are class mixtures) and variant C (balanced accuracy kept, columns are within-class
  DIFFICULTY mixtures, plus the check that the free wilderness signal predicts difficulty). Each
  cell simulates the deployment (sample a stream under the mixture, run the free-signal-driven
  install-then-predict loop with the shared predictor, score).
- **Costs.** Moderate, and largely OFFLINE: it is a simulation over a matrix using one predictor,
  plus hosted throwaway validations for the probe forms. Wall-clock the winning strategy's build to
  confirm it is not minutes of obvious code. No student runs.
- **Risk / kill.** FIX-FIRST [PROVEN collapse as specified; CONJECTURE on the repair]. As specified
  (free reads, balanced accuracy, class mixtures) it is PROVEN inert: free reads reduce it to
  fixed-panel selection, and the balanced-accuracy-optimal panel is invariant to the class arrival
  mix (worked example, file 04 S6 to S8). Killed OUTRIGHT if a single affordable portfolio sits
  within Delta-star of the column-best in EVERY column of BOTH repair variants (no rotation, covtype
  has no heterogeneity the mechanic can convert). Flipped to build only if the best portfolio rotates
  across columns by more than Delta-star, with a fat affordable mixture-independent core keeping
  first-pick luck small.
- **Reward.** The masking predictor is reusable across the real-data items. A pass gives a
  deployable install-economics task on real data; but its band-certainty is the weakest of the
  real-data three because it needs a repair (a metric change, or a conjecture about covtype's soil
  structure) to have any live rung at all.
- **Band certainty versus history.** Only the REPAIRED scheme beats the history: repair D makes the
  optimal panel provably flip with the class mixture (file 04 S7), so the install decision is
  genuinely stream-dependent and the easy-and-fast peek-calibrated counter-play (the second collapse
  ingredient) no longer exists; the install-timing tradeoff (early risks reading the mixture wrong,
  late wastes degraded rows) turns on, which is the one non-dominated tradeoff the mechanic offers.

**6. TEP consequence-dynamics build plus probes (`05_compounding_state.md`).**
- **Status.** NOT STARTED, held to last (or a separate pipeline-validation track).
- **Requires.** The heaviest build: the grader advances a simulated plant state between cases (a
  mishandled fault propagates and the sensors drift, honest physics from the Tennessee Eastman
  Process simulator), returning cases re-perturbed with fresh noise so past purchases do not launder
  forward. A compounding gain g strictly below 1 via a severity cap plus force-resolution after k
  returns, with force-resolution penalized at least as much as handling the case properly. Corner
  pricing (defer-everything, engage-blindly, and predict-a-constant must all lose). A five-rung
  probe ladder (ignore the dynamic, defer-nothing greedy, severity thresholds, lookahead planning,
  reserve management near stream end), an amplification probe (flip one early action, measure the
  final-score change), and a wall-clock of the lookahead rung.
- **Costs.** Highest of the six: dynamics in the grader, re-perturbation, g and k tuning, corner
  pricing, plus the most probe runs (ladder times 5 seeds, amplification over several early actions
  and seeds). No student runs, but the most hosted validation and the most build.
- **Risk / kill.** SURVIVES fix-first, scaffold-only [ARGUMENT / CONJECTURE]. Killed if the probe
  ladder collapses to 1 or 2 levels, or the amplification probe fails at every g that still leaves
  the dynamic non-trivial (g at or above 1 makes one early error snowball and decide the winner by
  seed luck, PROVEN, file 05 P5, P7), or the wall-clock plus a probe shows the lookahead rung is both
  textbook-easy and fast while the lower rungs also fail to separate.
- **Reward.** Even a clean pass validates the PIPELINE on the scaffold, not a shippable product (TEP
  is a simulation and a public benchmark, direction doc section 19). Narrow reusable value.
- **Band certainty versus history.** The state (the set of unresolved cases) is high-dimensional and
  action-coupled, so two policies diverge onto trajectories that do not reconverge and there is no
  scalar summary for a shadow price to calibrate against (file 05 P3), breaking the first collapse
  ingredient; the offline-optimal plan is several insights deep and heavy to build, so it is a high
  rung rather than an easy-and-fast counter-play, breaking the second; g strictly below 1 keeps luck
  bounded and the seed-blocked noise model valid (P7).

### What evidence would reorder this

- **Item 1 returns a clean KEEP with high early-versus-final correlation.** [ARGUMENT] Then
  agent-time checkpoint grading becomes a live ADD-ON to whichever stream scheme ships, and its
  larger-transcript escalation and mid-session-scorer work move up, though still as an addition, not
  ahead of the lead build.
- **Item 2 fails gate 2 (random ties canonical acquisition on covtype even after the pool-imbalance
  reshape).** [ARGUMENT] Then item 6 dies with it (O1), item 2's screen moves to a bigger many-class
  dataset (file 03 Alternatives), and item 3 becomes the lead real-data build.
- **Item 3's seed-variance number is large (Delta-star shrinks substantially under small-chunk).**
  [CONJECTURE] Then item 3 rises toward the top on its own merits (it raises measurable levels for
  every scheme, and it is the direct rescue of the global-pool motivation), and small-chunking is
  applied as a modifier to items 2 and 6.
- **Item 4's regret matrix shows genuine rotation beyond Delta-star.** [CONJECTURE] Then item 4
  moves ahead of item 6 among the real-data builds, since it would no longer need item 2 to precede
  it and its band-certainty would stop being the weakest.
- **The real-data survivors (2, 3, 4) all disappoint.** [ARGUMENT] Then item 5 stops being last: the
  scaffold-only consequence-dynamics build becomes the primary remaining bet, accepting its lower
  product value because a scaffold band beats no band.

## Alternatives (orderings rejected, and why)

- **Item 5 (TEP consequence dynamics, `05_compounding_state.md`) first, because path dependence is
  the deepest mechanism.**
  Rejected. It is the heaviest build (O2), scaffold-only (O5), and narrowest in value of information
  (O4). Leading with it spends the most effort for a product that direction doc section 19 will not
  ship, before the cheap real-data pre-tests have said whether a deployable scheme exists. The depth
  of the mechanism does not outweigh three criteria pointing the other way.
- **Item 6 (paid-revision pairing, `06_paid_revision.md`) before item 2 (the label-budget pre-test,
  `03_train_label_budget.md`), because the rationing tradeoff is the whole point of the direction
  doc section 21.** Rejected on a PROVEN precedence (O1): item 6 has no measurable content until item
  2's harness exists and item 2 has passed its dominance gate. Building revision machinery first
  would be building on a foundation that might not band.
- **Item 4 (instrument installation, `04_instrument_installation.md`) ahead of items 2 and 3 (the
  small-chunk pre-test, `02_small_chunk_information_release.md`), because its masking predictor is
  reusable.** Rejected. The predictor is reusable no matter which real-data item builds it first
  (O4), so build it inside the higher-value item 2. Item 4's own band-certainty is the weakest of
  the real-data three (proven inert without a repair, O3), so leading with it front-loads the least
  certain payoff.
- **Item 1 (transcript replay, `01_agent_time_commits.md`) demoted to last because its
  actionability ceiling is low.** Rejected.
  Low actionability is a reason not to over-invest in it, not a reason to delay it: it costs almost
  nothing, shares nothing with the builds, and returns first (O2, O6). Delaying a free independent
  decider banks its branch verdict later for no saving.
- **A strict one-at-a-time serialization (finish each item before starting the next).** Rejected.
  Hosted throwaway validations are cheap enough that item 1 runs concurrently with item 2 and item 3
  starts as soon as item 2's shared components exist (O6, O9). Strict serialization would idle the
  concurrency the hosted-only rule actually permits (it forbids heavy LOCAL runs, not concurrent
  hosted pushes), while still batching pushes sensibly.

## Open questions (each worth a dedicated chat)

Each is OPEN until resolved; when a chat settles one, prefix it RESOLVED with the deciding fact.


1. **Is the shared predictor genuinely reusable across items 2, 3, and 4 as one artifact?** Item 2
   (`03_train_label_budget.md`) wants an ordinary predictor shared across acquisition probes, item
   3 (`02_small_chunk_information_release.md`) wants a masking-robust one, item 4
   (`04_instrument_installation.md`) wants a masking-robust one. Confirm one masking-robust predictor serves all three (a
   masking-robust model is a strict generalization of an ordinary one), so the O4 reuse claim holds
   in code, not just in principle.
2. **Does item 3's Delta-star measurement transfer across schemes, or is it scheme-specific?** The
   seed-variance shrink is measured on the small-chunk feature-reveal loop; whether the same shrink
   applies to the label-reveal loop (item 2) or the install loop (item 4) is a separate empirical
   question. If it does not transfer, item 3's cross-cutting value of information (a load-bearing
   reason it sits at position 3) is narrower than O4 assumes.
3. **How many hosted throwaway pushes is "batch sensibly" in practice?** The ordering assumes probe
   validations are cheap enough to run several schemes' pre-tests in an overlapping window, but the
   dedicated batch (the `mini_batch_id` under Reference identifiers) has finite throughput and each
   push is real. A rough per-item push count (gate 2
   alone is six probes times 5 seeds) would let the concurrency in O6 and O9 be scheduled against
   actual capacity rather than assumed free.
4. **Does a KEEP on item 1 compose with the stream-facing survivors, or conflict?**
   `01_agent_time_commits.md` calls a KEEP an addition, but checkpoint grading samples the session
   while the survivors grade the stream;
   whether a single task can grade both without the session-noise contamination of file 01 step 5
   leaking into the stream score is unresolved, and it decides whether item 1's payoff is additive or
   merely diagnostic.
5. **What reorders faster, a kill or a large positive measurement?** The reorder rules above treat
   kills (drop the branch) and large positive numbers (promote the scheme) symmetrically, but a kill
   frees capacity immediately while a promotion only redirects it. Whether the tail of the ordering
   should react more to one than the other is a scheduling judgment the first two results will inform.
6. **Which eval id holds the recorded Tennessee Eastman Process transcripts item 1 needs?** A
   standalone-audit gap, flagged rather than silently filled: the covtype transcripts are pinned to
   eval `babd012a-4ae2-4349-99cb-a030db3f4491`, but no file in this folder records the TEP scaffold
   eval's id. `../README_general_direction.md` section 20 names eval
   `2eb7b2e7-c573-40dc-b134-35776173f74d` as the launched budgeted-tep student eval (7 runs
   submitted), while `01_agent_time_commits.md` and `05_compounding_state.md` describe a 5-run TEP
   record (fail, fail, 0.65, 0.80, 0.82). One more partial pointer exists:
   `../handoffs/global_budget_next.md` records the latest scaffold-baseline TEP eval as
   `4d68f219-...` (truncated there; the 5-run record above is most likely this one). Confirm the
   full id on task `36abdac8-4edd-4304-a48c-53933cd34f62` by running `horizon evaluations list`
   (after `source horizon_env/bin/activate` from the repo root) before building the transcript
   parser.
