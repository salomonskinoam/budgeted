# Building the world — running design doc (DISCARD AFTER BUILD)

> **⚠️ SUPERSEDED (do not follow §0–§7 below).** The PhysioNet/Shape-B plan in this doc was *executed
> and the dataset FAILED the anti-monoculture gate* (see §8, and `README_general_direction.md` §8
> Update 2). We have abandoned tabular/time-series data entirely. The **active direction is budgeted
> *perceptual* acquisition** — see `README_general_direction.md` §9–§14 (non-tabular directions, who
> the student is, the multi-step training recipe, and the task-generator multipliers). This doc's §1–§7
> are retained only as the record of the PhysioNet attempt; a fresh build plan will be written once the
> first perceptual primitive + dataset is chosen. §8 (the bake-off result) stays as the evidence log.

Working notes for standing up the **first** budgeted-feature-acquisition task. Scratch / living doc;
delete it once the world is built. Durable "why" lives in
[`README_general_direction.md`](README_general_direction.md) and
[`budgeted_acquisition_proposal.md`](budgeted_acquisition_proposal.md). SDK mechanics:
`../sdk/CREATING_A_WORLD.md`. Reference world to mirror: `multimodal_fusion` (`worlds/fusion/` +
`tasks_def/` + `tasks/<task>/`).

## 0. Decision
**First build = PhysioNet 2012 (ICU mortality), Shape B (sequential / temporal acquisition), FULL
granularity — no tabular collapse, no per-stay aggregation.**

Why (the two binding reasons):
- **Structural irreducibility / anti-monoculture.** A strictly-tabular task collapses to
  "flatten-and-tree" (GBTs) — a near-monoculture that also absorbs missingness for free, killing both
  prediction- and imputation-strategy diversity. The band would have nowhere to form. PhysioNet's
  irregular multivariate 48h trajectories resist flattening: the signal is in *what was measured,
  when, and how it trended*. (Direction doc §5, §7.)
- **The acquisition decision is genuinely temporal.** Buying = revealing a measurement over time
  under a running budget (`cost(f, t)`). "Given the cheap vitals trend so far, is it worth ordering
  the expensive lab now?" — that conditional, sequential decision is the real task.

This **rejects** the natively-tabular candidates (Diabetes-130, Thyroid) for the first build despite
their good falsifier scores — they fail the anti-monoculture test. Alternative irreducible candidate
if PhysioNet stalls: **C-MAPSS** (run-to-failure sensor sequences, regression).

Goal of THIS build: a machine to **observe a real score spread across open-ended student attempts.**
But first, a cheap offline gate (§1) that can kill the idea before we build the expensive trajectory
machinery.

## 1. Offline anti-monoculture pre-check — THE GATE (do this before anything else)
The honest tension: even in Shape B, a student may *choose* to flatten-and-tree (summarize bought
measurements into a row, run XGBoost). We can't forbid it. The task only works if **flatten-and-tree
leaves real score on the table** — i.e. some structure/timing-aware method can beat it. We verify
this **offline, before building trajectories or acquisition/grading mechanics.**

**The gate is UNBUDGETED — run on the full, native data.** The question is purely "does flatten-and-
tree get a free win on this data's structure?", which needs no budget. PhysioNet already ships heavy
irregular missingness (variables sampled at different times, many never measured), so the
masks-and-times signal the challenger exploits is exercised on raw data. A budget would only add an
arbitrary, not-yet-designed knob. Budgeted re-test is deferred to build time (§3), where
acquisition-induced missingness should only *widen* the gap — a confirmation, not a selector.

- **Hypothesis to reject:** "on the full native data, a tuned GBT on a flattened feature vector is
  unbeatable."
- **Pass condition:** a structure/timing-aware model beats a well-tuned GBT by a margin that survives
  seed / CV variation.

Procedure:
1. Target = in-hospital mortality; metric = AUPRC (and AUROC) given ~14% prevalence.
2. Use the **full native data** — no imposed budget, no extra dropping. The dataset's own irregular
   sampling *is* the partial-observation signal.
3. **Baseline A (the monoculture):** flatten to summaries + missingness indicators; tune
   XGBoost/LightGBM; let it handle NaN natively.
4. **Challenger B (structure-aware):** a model that consumes the irregular series with observation
   masks *and* times (GRU-D-style, or an explicit model of the measurement pattern) — not just values.
5. Fair compare: same splits, comparable tuning budget; repeat over seeds.

Decision:
- **B beats A by a clear margin** → modeling half has real diversity; trees aren't a free win →
  green-light the Shape B build.
- **B ≈ A or A ≥ B** → monoculture confirmed; switch dataset (C-MAPSS) — do **not** proceed to the
  trajectory build.

Scope: this tests the **prediction** half only — necessary, not sufficient. Acquisition-strategy
spread still needs students (§4). But it's cheap and kills bad ideas early.

- [ ] Pre-check run, result logged in §7.

## 2. Data prep plan (full granularity — NO aggregation)
Source: PhysioNet Challenge 2012 v1.0.0 — set A (4,000 labeled) + sets B/C (~4,000 each) held out.
~14% in-hospital mortality.

Steps:
1. Download sets A/B/C (open license).
2. Parse each record's **irregular time-series**: keep every (variable, time, value) triple for the
   ~37 variables over 48h, plus the 5 admission descriptors. Represent as values + observation
   **masks** + **timestamps** (the mask/time channels are first-class signal).
3. Label: in-hospital mortality (binary).
4. Splits: train / validation (student-visible) / held-out test (grader); stratify on label.

Acquirable unit = **a measurement** (a variable at a time/window). Buying reveals that value; the
budget caps total acquisitions per stay. This is the `cost(f, t)` shape.

## 3. Cost + budget model — OWNER: user (TBD), starting proposal only
- **Cost tiers:** continuously-monitored vitals (HR, Temp, RR, NIBP) cheap; ordered labs (lactate,
  creatinine, troponins, blood gases, albumin) expensive. Real + plausible (Realism High).
- **Time dependence:** `cost(f, t)` — buying a measurement at time t; optionally cost varies with
  time/urgency. Per-stay budget.
- Set the budget on the **rising part of the score-vs-budget curve** (run the binding probe), below
  "buy everything," and where no single cheap vital already tops the score.

## 4. Pre-student falsifier checks (on prepared data, before student rollouts)
- [ ] **Anti-monoculture** — the §1 offline gate (the big one).
- [ ] **Degeneracy** — `score(best affordable single measurement) / score(full)` well below 1.
- [ ] **Binding** — score-vs-budget still rising at the chosen budget; `cost(all)/budget >> 1`.
- [ ] **Leakage** — no buyable measurement trivially encodes mortality; budget enforcement
      un-bypassable; forbidden-dir reads blocked.

## 5. The spread experiment (the deliverable)
- Build the task, **run open-ended students** (do NOT hand them strategies).
- Collect the **score distribution across runs** (mirror `multimodal_fusion/analysis/run*_<score>`).
- Fan-out = a task; pile-up at one value (high or low) = no discrimination → redesign. This is
  "measure the spread first."

## 6. World scaffolding (mirror `worlds/fusion/`, per CREATING_A_WORLD.md)
- [ ] `worlds/budgeted/` — `world.py` (`HorTask`), `config_world.py`, `paths.py`, `objective.py`,
      `verify.py` (writes `{primary, score, reason}`), `prompt_builder.py`, `prehook.py`,
      `setup_data.py`, `Dockerfile`, `data/physionet2012.npz`.
- [ ] `tasks_def/configs/physionet2012.py` + `tasks_def/physionet2012.py` + register in
      `tasks_def/__init__.py`.
- [ ] `tasks/physionet2012-budgeted/` apex shims; no per-task Dockerfile.
- [ ] **Sequential acquisition + grading mechanics** — the new design surface vs a static panel: the
      artifact reveals measurements step-by-step under a running budget, then predicts; verify must
      enforce the budget over time. (Design this once §1 passes.)
- [ ] Encapsulation under 700 dirs (reward-hacking); `hor.py validate -a oracle` passes / `-a noop` 0.
- Modes: agent-time first; deferred/grader-time (`train_at_grade`) later, same graded artifact.

## 7. Open questions / decisions for the user
1. **Cost + budget model** (§3) — needed for the *build*, NOT for the §1 gate (which is unbudgeted).
   Proposal is vitals-cheap / labs-expensive, per-stay `cost(f, t)` budget on the rising part of the
   binding curve.
2. **Metric** — AUPRC vs AUROC vs cost-sensitive, given ~14% prevalence. (Used in the §1 gate too.)
3. **Acquisition granularity in time** — per individual measurement, or per time-window block?
4. **Challenger model for the §1 gate** — CONFIRMED: GRU-D-style structure-aware baseline.

## 8. Status log
- **§1 anti-monoculture gate — PhysioNet 2012 set-a (mortality), fast 5-fold pass: FAIL.**
  Flatten-and-tree (XGBoost, 330 engineered summary features incl. slope/first/last/count/time) vs
  GRU-D (hourly value/mask/δ). Result: GBT AUPRC 0.511±0.046 / AUROC 0.855±0.023 **beats** GRU-D
  AUPRC 0.462±0.044 / AUROC 0.816±0.025; paired ΔAP −0.049, 95% CI [−0.081, −0.017], GRU-D won
  **0/5** folds. Leakage-sensitivity clean (drop `total_obs`: 0.511→0.494). Sanity gate passed
  (overfit-tiny AP 1.000, decay params active), so not a broken-challenger false FAIL. Decisive (not
  borderline) → escalation unwarranted. **Conclusion: PhysioNet mortality is a tabular monoculture;
  the tree gets the free win. Discard PhysioNet for this world; fall back to C-MAPSS (RUL regression,
  run-to-failure sequences) and re-run the same gate there.**
  Scratch experiment: `scratch/bakeoff/` (CPU torch venv).
