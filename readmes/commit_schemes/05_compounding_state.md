# 05. Compounding state

## The question

Can we build a version of the budgeted world where the policy's **own early actions change the
later environment**, so that a choice made on an early case has real, physical consequences for the
cases that come after? And if we can, does that produce a **band**: a spread of scores across
student attempts of varying strength, resolvable into several distinct levels?

"Compounding state" is the name for that property. In a plain task each case is independent: what
you do on case 3 has no effect on case 40. In a compounding-state task the two are linked, the
environment carries a memory of what the policy did, and that memory bends what the policy meets
later. This is *true path dependence*: the sequence of your own actions, not just luck, decides
what world you end up in.

## Background (terms defined)

- **The policy / the student.** The thing being graded is a piece of code an agent writes. It is a
  small program that, case by case, decides what to do (which measurements to buy, what to predict,
  whether to defer). "The student" is the agent that wrote it; "the policy" is the running program.
  Different students write policies of different quality, and the whole point of the task is that
  those quality differences should show up as different scores.

- **Case / stream.** The policy is run over a sequence of cases (rows), one after another, called
  the **stream**. In our world a case is one situation to classify (for example, one snapshot of a
  machine's sensors, where the label is which fault, if any, is present).

- **Buying features under a budget.** For each case the policy may **buy** measurements (features).
  Each feature has a cost. There is a budget limiting how much it can buy per case (or, in richer
  variants, across the whole stream). After buying what it can afford, the policy predicts the
  label. This is the "budgeted acquisition" world: you cannot see everything, you must choose what
  to pay for, then commit to an answer.

- **Peek data.** At the time the student writes its policy it has the **full training and validation
  data, features and labels, completely visible**. It can study the data, fit models, and precompute
  anything. This is a hard rule of this world: the only thing the policy does not know in advance is
  the **test stream**, which specific cases arrive and in what order. There are no blind guesses
  from withheld knowledge; every good decision is, in principle, informable from peek data.

- **Bounded agent.** An agent whose decision quality at any moment depends on the compute it has
  **already spent**, not only on the data available to it. Computation generates information:
  experiment results on peek data, debugged code, insights that arrive late in the session. "All
  peek data is visible from minute zero" therefore does not mean "all conclusions from peek data
  are held from minute zero." This is the frame of file `00_band_theory` and it governs everything
  in this file.

- **The both-axes rule (file 00's operative criterion).** "The optimal play is computable offline
  from peek data" kills a scheme's band **only** when that computable play is also **easy to
  discover** (no nontrivial chain of insights) and **fast to compute** (finishable well within the
  session even by weak agents). If either axis is hard, the same statement only locates the
  **ceiling**, the top rung of the ladder, and says nothing about how agents distribute below it.
  Covtype is the working counterexample: a near-optimal per-row policy was offline-computable there,
  yet real students banded 0.675 to 0.848, about 3 levels.

- **Skill ladder / rung.** The ordered set of distinct-scoring strategies between the naive move and
  the optimum, each rung carrying a **discoverability** (how hard it is to think of) and a
  **compute cost** (how long it takes to build once thought of). A tall ladder with reachable
  middle rungs spreads agents of varying strength; a one-rung ladder stacks them.

- **Seed.** The test stream is generated from a random **seed** (a number that fixes all the
  randomness). Evaluation reruns the same shipped policy under **5 fixed seeds** and averages the
  score. Two different policies run under the same seed see the same arriving cases in the same
  order (in a plain task; step P7 handles what happens when dynamics are added).

- **Spread and the band.** The **spread** is the gap between the best and worst student scores. The
  **band** is that spread being real and wide. It is the product of this whole effort. A task where
  every competent student lands on the same score is worthless, however high that score is.

- **Levels and Delta\*.** **Levels** is the number of score tiers that are *statistically
  distinguishable* given the grading noise, counted by a **seed-blocked analysis of variance** (it
  compares policies while holding the seed fixed, so differences caused by which stream a seed drew
  are separated from differences caused by policy skill). **Delta\*** is the resolution gap of that
  analysis: two scores closer than Delta\* count as one level. Many resolvable levels is the goal.

- **The global-budget collapse.** The immediately prior idea was a **global budget**: one shared
  pool of money spent across the whole stream, instead of a fresh budget per case. It failed, and
  step P2 below spells out both halves of why: the pool's trajectory is predictable, *and* the
  counter-play to a predictable pool is easy and fast. Compounding state is the attempt to introduce
  a state that resists at least one of those two halves.

- **balanced accuracy.** The score metric. For a many-class problem it is the average of the
  per-class recall (fraction correct within each true class), so every class counts equally
  regardless of how often it appears. Written out in full so there is no ambiguity: it is not
  overall accuracy; a rare class weighs as much as a common one.

- **The Tennessee Eastman Process (TEP).** A widely used **simulated chemical plant** benchmark for
  fault diagnosis. Concretely: it is a *computer simulation* of an industrial chemical reactor with
  many sensors, in which more than twenty distinct **fault types** can be injected (a valve sticks,
  a feed composition drifts, a cooling loop degrades, and so on). Each fault shows up as a different
  pattern across the sensors, and telling them apart is the classification task. In this repository
  TEP is the scaffold task **budgeted-tep**, with its features anonymized (shuffled and renamed
  `f0..f51`) and its classes relabeled to defeat memorization of the public benchmark. Because TEP is a
  *simulation* and not real-world collected data, the repo treats it as a **pipeline-validation
  scaffold** (something to prove the machinery works on) rather than as the final shippable product;
  the durable target remains a real, large, many-class dataset.

- **covtype.** A real, static, tabular dataset (forest cover-type classification) used here as a
  stand-in for "an ordinary snapshot dataset with no time axis." "Static snapshot" means every row
  was recorded once and sits frozen; there is no notion of a case *evolving* or *coming back*. It
  banded modestly in earlier work (roughly 0.675 to 0.848, about 3 levels).

- **The mediated grader.** The grader does not just read a file of predictions. It **drives** the
  policy: for each case it runs the policy's decide-then-reveal-then-predict loop itself, enforcing
  the budget and revealing only the feature values the policy paid for. This is what lets us add
  dynamics: the grader owns the loop, so it can also advance a simulated world between cases and feed
  the consequences back in.

## The process

**Tags.** `[PROVEN]` = a mathematical reduction or a working exploit. `[ARGUMENT]` = a heuristic
backed by this world's own evidence. `[CONJECTURE]` = a claim that still needs a pre-test before we
trust it.

**P1 [ARGUMENT]. The two questions every variant must answer.** Under the both-axes rule, each
candidate mechanism gets examined on two separate fronts. Front one: does its state escape the
averaging that made the global budget predictable? If the state is predictable, a counter-play can
be planned in advance from peek data. Front two: where such a plan exists, is finding and finishing
it **easy and fast**, or is it expensive and several insights deep? Only "predictable state AND
easy-fast counter-play" flattens the ladder; "predictable state, hard counter-play" leaves the
counter-play as a high rung that separates agents. Keeping these two fronts apart is the correction
this rewrite exists to apply: the first draft treated front one alone as decisive, which silently
assumed every agent is strong and computation is free.

**P2. The averaging argument, in plain words, and why the global budget fell to it.**
`[PROVEN]` (the mathematics of front one). Imagine a casino. On any single night the take is noisy:
a few big winners, a few big losers. But over a month the nightly take is extremely predictable,
because it is the sum of a huge number of small, roughly independent bets, and sums of many small
independent things concentrate tightly around their average. The global budget is exactly this
casino: its state is a single number, the money pool, changed by many small spends over a long
stream, so the pool's remaining-balance curve concentrates around a smooth expected trajectory.
`[ARGUMENT]` (front two, which the first draft skipped). A predictable pool admits a known
counter-play: a per-row rule with one tuning knob, a price on cost, calibrated from peek data. That
counter-play is a **textbook recipe** (shadow pricing is standard), fits **one obvious code pattern**
(calibrate one number on peek, then run the existing per-row buyer), and is **fast** (one
calibration sweep, minutes). It clears both axes, easy and fast, which is what makes the
global-budget collapse a legitimate kill even under the corrected frame, and not merely a ceiling
statement. The lesson for this file: a variant dies only when *both* halves line up like that.

**P3 [ARGUMENT]. What kind of state escapes the averaging.** The pool's vulnerability was being one
additively-evolving number. Consider instead a **high-dimensional, action-coupled** state: a whole
collection of things whose contents depend on which actions the policy took. Two policies that make
different early choices push such a state onto genuinely different trajectories that do not
reconverge, because each policy's later situation is a consequence of its own earlier actions rather
than of a shared, smooth aggregate. There is no single summary number to calibrate a knob against,
so the shadow-price pattern has no obvious foothold. And note what front two adds even here: with
peek-learnable dynamics an optimal plan against the rich state always exists in principle, but
*computing* it is a different matter from the pool case; planning against a rich evolving state is
heavy, which by the both-axes rule pushes that plan up the ladder instead of collapsing it. The
danger, examined in P5 and P7: a rich state that diverges under skill can also diverge under luck,
and that has to be controlled.

**P4. Variant (i): congestion pricing.** *Mechanism.* A feature's **price goes up the more the
policy uses it**, like a toll road that charges more when busy. Early heavy use of feature X makes X
expensive for all later cases, so early choices shape later costs.

`[PROVEN]` (front one). The price of X at any moment is a deterministic function of its cumulative
usage, and cumulative usage is a sum of many small increments (one per case that bought X). The
casino again: over a long stream, usage climbs a smooth, predictable curve, so the entire **price
path is predictable in advance** from peek data. The state, though nominally one number per feature,
is additively evolving and concentrates just like the pool.

`[ARGUMENT]` (front two, the part that must be argued concretely rather than asserted). Is the
counter-play against a known price path easy AND fast? The natural optimal pattern is
**water-filling**: keep buying a feature while its marginal value still exceeds its current price;
as the price climbs past the value, stop and move the spending to the next-best feature, so that
every unit of budget ends up buying roughly the same marginal value. The case that this is easy:
(a) water-filling against a known price schedule is a **textbook allocation recipe**; (b) it fits
**one code pattern**, precompute the price curves from projected usage, then run a greedy
value-per-current-cost loop, which is a small edit to the per-row buyer every student already
writes; (c) it is **fast**, a single pass over the projected stream, seconds. One honest wrinkle:
the usage that drives the price is the policy's *own* usage, so curve and plan must be solved
together (plan implies usage, usage implies prices, prices imply plan). But iterating that loop a
few times converges quickly (prices rise with usage, demand falls as prices rise), and the loop is
still one small piece of code. So both axes plausibly collapse here. `[CONJECTURE]` (the residual).
"Easy to discover" is, per file 00, only ever proxied (textbook-recipe and one-pattern are proxies,
not measurements), so the flat-ladder reading should be confirmed by the standard dominance probe (a
water-filling probe versus a strictly richer planner, through the real grader) before it is treated
as final. The forward conclusion of this step: front one holds provably, front two holds on strong
proxies, so the ladder here looks short.

**P5. Variant (ii): consequence dynamics.** *Mechanism.* A case handled **wrongly comes back later,
harder and worth more**. Think of an untreated patient who returns sicker, or a machine fault left
undiagnosed that worsens and spreads. The state is the **set of still-unresolved cases**, which
cases the policy got wrong and how bad they have become.

`[ARGUMENT]` (front one). That set is high-dimensional (a whole collection, not one number) and it
genuinely diverges between policies: a skilled policy leaves a smaller, less-festering backlog than
a clumsy one, and the difference feeds forward. This is exactly the P3 shape, no scalar summary, no
shadow-price foothold.

`[ARGUMENT]` (front two, retagged from the first draft). Is the optimal counter-play computable
offline? In principle yes, because the dynamics are fully peek-learnable (P9). But look at what the
computation *is*: build a forward model of how cases worsen and return, then solve a finite-horizon
sequential decision problem against that model (simulate futures, plan purchases to minimize total
downstream cost, handle the end of the stream). That sits behind **several composed insights**
(first notice the dynamic matters at all, then model it, then realize planning beats simple
thresholds, then get the horizon right) and costs **real session compute** (forward simulation and
lookahead are expensive to build and to run). By the both-axes rule this is not a collapse
ingredient; it is a **high rung**. The first draft's framing, that offline computability of the plan
threatens this variant, was an unbounded-computation error.

`[CONJECTURE]` (the two-sided knob). The same divergence that carries skill can carry luck, and one
knob controls both: the **compounding gain g**, defined concretely as the multiplier on a case's
score weight (and difficulty) each time it returns relative to its previous appearance.

`[PROVEN]` (what g does). Suppose a returned case is **capped in severity** (it can only get so bad)
and **force-resolved after a fixed number of returns** (after k comebacks it is settled no matter
what). Then one early mistake contributes a burst now, g times that burst on the next return,
g-squared after that, a geometric series. If **g < 1** the series is finite and small (it sums to
burst divided by (1 minus g)): the total downstream footprint of any single early error is bounded,
which simultaneously bounds luck (an unlucky early hard case cannot swing the final score by more
than that bounded sum) and keeps within-run perturbations small (which P7 needs). If **g > 1** the
series diverges: one early error grows without bound and comes to dominate the score, so which
policy wins is decided by who happened to dodge the case that snowballed, a property of the seed,
not of skill. g is the master dial, and the build constraint is g strictly below 1.

`[ARGUMENT]` (the honesty caveat). On a **static snapshot dataset like covtype**, any "return worse"
dynamic is **invented by us**: covtype rows do not come back, so we would have to fabricate a rule
for how a mishandled case worsens (multiply some feature by something, bump a difficulty score).
Fabricated physics is arbitrary, hard to justify, and invites reverse engineering. On the
**Tennessee Eastman Process** the *simulator itself supplies honest physics*: an undiagnosed fault
genuinely propagates through the simulated plant, the sensors genuinely drift further, according to
the plant model and not a rule we made up. TEP is therefore the natural home for this variant, with
the standing caveat that TEP is a simulation and hence a scaffold.

**P6. Variant (iii): queue and backlog.** *Mechanism.* The policy may **defer** a case to later at a
cost (postpone deciding it). Deferred cases pile up and must all be cleared before the stream ends,
so early deferral shapes the later workload.

`[PROVEN]` (front one). A single **backlog count** grows and shrinks by small increments over a long
stream, so it concentrates around a smooth curve, the casino once more.

`[ARGUMENT]` (front two). The counter-play against a predictable backlog curve is a **fixed deferral
threshold with one knob** calibrated on peek, the same recipe family as the shadow price in P2:
textbook, one code pattern, minutes to compute. Both axes line up the same way they did for the
global budget, so the plain single-count queue points to a short ladder for the same paired reasons,
not on predictability alone.

`[CONJECTURE]` (the richer version). Per-class backlogs with **different clearing costs** change the
state from a scalar to a vector whose *composition* depends on which classes the policy chose to
defer, a skill-laden diverging choice with no single-knob summary. That might recover rungs, but it
is strictly more speculative than variant (ii) and would need its own probe ladder.

**P7. The noise-model question.** Our levels statistic compares different policies **on the same
seeds**: hold the stream fixed, and a score difference between two policies is attributed to skill.
With action-coupled dynamics, two policies steer the world into different states, so after a few
cases they are no longer facing the same situations even under the same seed, and the premise "same
seed, same test" appears to break.

`[PROVEN]` (why it survives, under one stated condition). It holds provided the seed fixes
everything **exogenous**, meaning everything that comes from outside the policy: which base cases
arrive, in what order, plus the fixed rules of the dynamics (how a returned case worsens, by how
much, capped where). If the seed nails all of that down, then any *within-seed* divergence between
two policies is a **deterministic consequence of their own choices**. That is precisely the thing
being measured: signal, not noise. Two policies ending in different states under the same seed is
the task working, the better policy having earned a cleaner world. The only noise left is **across
seeds** (a different seed draws a different base stream), which is exactly the axis the 5-seed
average and the seed-blocked analysis of variance already handle. The condition to enforce in the
build: dynamics rules are seed-fixed, never re-randomized per policy.

`[PROVEN]` (the g connection). Within one run and one seed, how much do a policy's own early wobbles
perturb its own later state? That perturbation obeys the P5 geometric series. With g < 1 an early
wobble decays, the within-run residual stays small, and levels stay countable. With g > 1 it blows
up, the residual swamps the between-policy signal, and levels stop being countable. So g < 1 does
double duty: it bounds luck (P5) and it keeps the noise model valid (this step). One knob, two
guarantees.

**P8. The skill ladder for variant (ii), rung by rung, both axes per rung.** The scheme lives or
dies on whether several rungs sit between naive and optimal *and* real agents of varying strength
land on different ones. `[ARGUMENT]` for the rung ordering; the separations are `[CONJECTURE]`
until probed. Beneath all of these sit the engineering rungs file 00 documents on every hard task
(get a working driven policy at all, get a competent predictor trained); the TEP scaffold's own
spread included outright failures, so we do not assume every agent even reaches rung 1 cleanly.

1. **Ignore the dynamic.** Treat every row independently, as if nothing ever comes back.
   *Discoverability:* the default, this is where an agent lands by not engaging. *Compute:* none
   beyond the base task. Leaves the worst backlog.
2. **Defer-nothing greedy.** Handle each case as well as possible right now, never postpone, no
   forward thinking about returns. *Discoverability:* easy, the obvious "try hard on each case"
   move. *Compute:* cheap. Better than rung 1 because cases get resolved promptly.
3. **Threshold rules on predicted severity.** Spend more budget on cases the model flags as costly
   if they return worse, less on easy ones. The first rung that uses the dynamics.
   *Discoverability:* one insight (model the return cost), natural for a mid-strength agent that
   reads the dynamics data. *Compute:* light, one auxiliary severity model plus a threshold.
4. **Lookahead planning against the peek-learned dynamics.** Build a forward model of returns and
   plan purchases to minimize total downstream cost, not just this-case cost. *Discoverability:*
   several composed insights (P5, front two). *Compute:* heavy, simulation plus planning code that
   takes real session time to build and debug. This is the high rung the both-axes rule protects:
   computable in principle, neither easy nor fast in practice.
5. **Reserve management near stream end.** Near the end there is no "later" for a comeback to hurt
   you in, so the optimal spend profile shifts (stop paying to prevent returns that will never
   arrive). *Discoverability:* subtle, a horizon insight on top of rung 4. *Compute:* modest once
   rung 4 exists.

`[CONJECTURE]` (the load-bearing question). Do the middle rungs separate by more than Delta\*, and
are they reachable by *middling* agents? The design intent is that rung 3 is one natural insight
away for a mid-strength agent and beats rungs 1 and 2 by a real margin, because preventing expensive
comebacks is worth real score. Whether that margin clears the noise floor is exactly what the P11
probe ladder must measure before anything is built.

**P9. Luck under constraint (a).** `[PROVEN]` (what the constraint guarantees). Constraint (a): the
dynamics must be **fully learnable from peek**. We ship the simulator itself, or a large body of
historical trajectories, so a student can learn exactly how a case worsens on return, with what
probability, capped where. Nothing about the dynamics is a blind guess, which keeps the scheme
inside the world's hard rule: no skill differences manufactured from withheld knowledge. The only
unknown at agent time is which cases the test seed draws and in what order.

`[ARGUMENT]` (what luck remains). Only **which hard cases happen to arrive early** in a given seed.
An early cluster of intrinsically hard cases gives that seed a rougher ride. This residual is
bounded by g < 1 (an early hard case's downstream footprint is a finite geometric sum, P5) and
averaged over the 5 seeds (a bad early draw in one seed is washed by the others). Luck is present
but controlled on two fronts, and the seed-blocked statistic separates exactly this across-seed
component from the within-seed skill signal (P7).

**P10. Gaming.** `[ARGUMENT]` Concrete exploits and the pricing that closes them:

- **Recognize-and-reuse.** If a returning case arrives with the *same* feature values it had before,
  a policy could recognize it and reuse the features it already paid for, getting later information
  free. Fix: **replayed cases must be re-perturbed with fresh noise** so a returning case is not
  byte-identical to its earlier self and past purchases do not launder forward. (On TEP this is
  honest: a fault that has propagated genuinely presents different sensor values, so re-perturbation
  is physics, not obfuscation.)
- **Corner strategies.** Three degenerate policies must be priced to lose: (a) **defer everything**
  (never decide, dump it all to the end) must score worse than engaging, via deferral cost plus the
  end-of-stream clear-everything requirement; (b) **defer nothing, engage blindly** must lose to
  severity-aware spending; (c) **buy nothing, predict a constant** must lose badly under balanced
  accuracy. If any corner ties the smart play, the ladder has no floor.
- **Force-resolve abuse.** Because a case is force-resolved after k returns, a policy could
  deliberately let cheap cases ride to force-resolution to save budget. Fix: force-resolution
  carries a **penalty at least as large as** the cost of handling the case properly, so dumping to
  force-resolve never pays.
- **Metric coupling check.** Compounding changes which cases, and how many, get scored; verify the
  metric is not silently invariant to that. Balanced accuracy weights classes equally regardless of
  arrival counts; confirm returned and worsened cases enter the score with the intended extra weight
  and are not averaged away by the per-class balancing. A metric that neutralizes the compounding
  neutralizes the scheme, the way balanced accuracy neutralized instrument-installation mixtures
  elsewhere in this world.

**P11. The pre-test.** `[CONJECTURE]` (thresholds are proposals until run). All probes are throwaway
policies run through the **real grader via hosted validation**, no student evaluation runs spent,
replayed across the 5 seeds. Three probe suites:

- **Probe ladder.** Hand-write the five rungs from P8 as fixed probe policies and run them across
  the 5 seeds. Read the seed-blocked resolution: how many rungs land on distinguishable levels?
  **Keep** if at least about 3 rungs separate (ladder range over Delta\* at least about 4, matching
  the resolution-floor requirement used elsewhere in this world). **Kill** if the ladder collapses
  to 1 or 2 levels: if hand-written rungs do not separate, real students will not either.
- **Amplification probe (the g check).** Take one probe, **flip a single early action**, rerun the
  same seed, and measure the change in final score. Repeat over several early actions and seeds.
  **Keep** if a single early flip moves the final score by **less than one seed's worth of noise**
  (g < 1 confirmed, early perturbations decay, luck bounded). **Retune** if one flip moves the score
  by more than a seed's worth of noise (g too high): tighten the severity cap, shorten k, re-probe.
  **Kill** if no tuning keeps the flip sub-noise while the dynamic still moves the probe ladder.
- **Wall-clock the rung-4 probe** (file 00's measurable half of reachability). Time the build and
  run of the lookahead probe on the task machine. If it turns out trivially fast to build from a
  textbook pattern, the "neither easy nor fast" defense of the top rung weakens and the dominance
  question reopens; if it costs real hours, the high-rung reading stands.

Passing never promises a band; failing the ladder or the g check guarantees there is none.

## The result

- **(i) Congestion pricing: KILL, pending one cheap confirmation.** Front one is proven (the price
  path is a deterministic function of concentrating cumulative usage, hence predictable). Front two
  is argued concretely: the counter-play is water-filling against a known price curve, a textbook
  recipe in one code pattern, seconds to compute, with the plan-price fixed point closable by a
  short cheap iteration. Both axes line up, which under the corrected frame is what a legitimate
  kill requires. Because "easy to discover" rests on proxies, the kill is confirmed by the standard
  dominance probe (water-filling versus a strictly richer planner) before being final. *What would
  flip it:* that probe showing the richer planner beating water-filling by more than Delta\*, which
  would mean the fixed-point plan is less obvious than the proxies suggest and rungs exist.

- **(ii) Consequence dynamics: SURVIVES, fix-first, scaffold-only.** The state (the set of
  unresolved cases) is high-dimensional and diverges under skill, so front one fails to bite; and
  the offline-computable optimum fails front two (several insights deep, heavy to build), so it is a
  high rung, not a collapse. The survival is conditional on **g < 1** (severity cap plus
  force-resolve after k returns), which simultaneously bounds luck and keeps the seed-blocked noise
  model valid, and on the dynamics being fully peek-learnable. It is **honest only on TEP** (real
  propagation physics; on covtype any dynamic is invented), and TEP is a scaffold, so this variant
  validates the pipeline rather than shipping as the final product. *What would flip it to KILL:*
  the probe ladder collapsing to 1 or 2 levels; or the amplification probe failing at every g that
  still leaves the dynamic non-trivial; or the wall-clock check plus a probe showing rung 4 is both
  textbook-easy and fast, flattening the top while rungs 1 to 3 also fail to separate.

- **(iii) Queue and backlog: THIN, not worth building before (ii) settles.** The single-count
  version fails for the same paired reasons as congestion pricing: a concentrating scalar state plus
  a one-knob textbook threshold counter-play, easy and fast. *What would flip it:* the per-class
  backlogs-with-distinct-clearing-costs variant passing its own probe ladder, showing backlog
  *composition* creates separated rungs. Strictly more speculative than (ii).

## Alternatives

- **The data pitfall (honest physics).** The only honest source of return-worse physics in hand is
  TEP, a simulation and hence a scaffold. On real static data the dynamic would be invented, exactly
  the arbitrariness the world's real-data rule exists to avoid. Real datasets with **native
  sequential consequence structure** are the way off the scaffold:
  - **Equipment monitoring with real degradation trajectories.** Machines measured repeatedly as
    they wear out (run-to-failure logs). A component left unaddressed genuinely degrades further in
    the *recorded* data, so "handled wrong, returns worse" is real, not fabricated. Acquisition
    cost: moderate; such corpora exist but need cleaning and many are small or single-machine.
  - **Clinical episodes with real revisits.** Longitudinal patient records where an undertreated
    condition leads to a real, recorded, sicker readmission. Honest physics (real biology).
    Acquisition cost: high, credentialed, heavy to clean; and the earlier target lesson applies, the
    target must be a **diagnosis the acquirable tests actually diagnose**, not a noisy downstream
    outcome.
  Both carry real acquisition cost; that is the honest tradeoff against TEP being free but simulated.
- **The metric pitfall.** If balanced accuracy averages the compounding away (P10, last bullet), the
  fix is an **arrival-weighted metric** (overall accuracy, or an explicit extra weight on returned
  and worsened cases) so a mishandled-then-returned case actually costs more in the score, matching
  the physical harm. A richer scheme is not the fix for a decoupled metric.

## Open questions

1. **Exact g and k on TEP.** What severity cap and force-resolve horizon keep g comfortably below 1
   while leaving the dynamic strong enough to separate the probe ladder? An empirical tuning problem
   on the simulator, gated by the amplification probe.
2. **Does the middle of the ladder separate?** Rungs 3 and 4 are load-bearing; whether real middling
   students land on distinct levels there, above the noise floor, is the single most important
   unknown, and only the probe ladder plus eventual student runs answer it.
3. **How fast is rung 4 really?** The high-rung defense of lookahead planning rests on it being
   expensive and several insights deep. A time-boxed probe (the same probe-building process cut off
   at different compute budgets, scored through the real grader) would measure how much of the rung
   is compute conversion versus insight, per file 00's temporal-climb question.
4. **Metric weight for returns.** How much extra should a returned case weigh so the compounding
   shows in the score without letting one seed's unlucky early cluster dominate? Couples to g; needs
   its own small sweep.
5. **Real-recurrence data feasibility.** Is there a run-to-failure or clinical-revisit dataset large
   enough (populous classes, enough resolvable levels) to carry this variant off the TEP scaffold
   onto real data? The durable-target question; deserves a dedicated survey.
