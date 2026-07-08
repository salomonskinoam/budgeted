# Worklog (newest on top)

- Task-keyed, SDK-dictated band source of truth. Was: eval-hash-keyed flat jsons under `scratch/analysis/`
  + metadata split across `DATASETS`/`REPORT_META` in the driver (disagreeing on multi-eval thyroid) +
  `best_observed` implicit in the SDK default. Now: SDK owns `TaskBandReport` + `EvalStats` (one task ->
  a LIST of evals, each with its own stats; legacy `BandReport` auto-lifts and renders byte-identically,
  so imputation is untouched, verified). Truth lives at `worlds/<world>/analysis/<task>/band_supports.json`
  (task-keyed, committed); metadata + which-evals-per-task in `tasks_def/band_manifest.py`; `best_observed`
  sourced from the task config. Thyroid is now ONE task with 2 evals (orig + drop-TSH), machine-rendered
  (was hand-written); its salvage insight preserved as a manifest `narrative`. `--migrate` did the free
  regroup (no re-analysis); the stale eval-hashed scratch jsons were removed. SDK bumped d208041. Full
  per-eval recall backfills on the next (approval-gated) `--emit`. `--validate` green across both worlds.

- Readme reorg (option A, multi-world) + multi-world band-report generator. Bibles (durable reference)
  live at repo-top `readmes/` (`README_general_direction`, `band_method`, `world_architecture`); session
  handoffs at `readmes/ai/handoffs/`; each world now OWNS its submission table + task records under
  `worlds/<world>/readmes/` (budgeted + label_budget split out of the old combined repo-top doc; records
  git-moved, not regenerated). `band_resolution.py` gained a per-dataset `world` field and routes
  emit/records/table per world (`_world_paths`); `--validate` now checks EVERY world (passes). Mirrors
  `../imputation`'s self-contained-world layout. All cross-links fixed. Scheme 3 (small-chunk) DROPPED.
  New `worlds/drift/readmes/README_concept.md` scaffolds (brief only, not built) the next direction: a
  concept-drift online-active-learning world (design-bible §23) composing scheme 7 (streaming
  delayed-label learning) + scheme 6 (paid revision). SDK submodule bumped f8cb6b4 -> eb21fca (band_report
  analysis seam).

- Submission table re-decided on #band_supports (the RESOLUTION CAPACITY), not observed levels. The
  old `levels` column reported `rank_resolution.n_levels` (where runs LANDED) and used it as if it were
  capacity, wrong metric. #band_supports = `resolution` tiers = 1 + spread/LSD = tiers the band can hold
  between its endpoints; decision rule >=3 viable, <=2 reject, ceiling -> gap test. New reproducible
  source of truth `scratch/analysis/band_resolution.py` decodes each run's stored predictions_b64
  (no policy replay), reconstructs graded test labels via DataView, and computes sigma (stratified
  bootstrap) / #band_supports / #observed / gap test -> `scratch/analysis/<eval8>/band_supports.json`.
  One durable record per row under `readmes/tasks/<task>.md`. Results: covtype 8.06 YES, tep 9.14 SCAFFOLD,
  unsw 1.49 / thyroid 2.57 / diabetes 1.32 / derma 1.21 / hydraulic ceiling(p_le0 0.39) all REJECT.
  label-budget-covtype #band_supports 6.82 (band VIABLE, wide, top-heavy occupancy) but ELIMINATED on
  strategy homogeneity (all 5 students wrote one recipe), not on band. covtype band 0.675-0.848
  reproduced exactly from predictions_b64 (method faithful).

- Shared mediated-grading framework extracted to `sdk/mediated/` (data_view, objective, active,
  config_world, paths, setup_data, prehook, prompt_builder, harness, verify_suite, world_base,
  Dockerfile). Both worlds import it; nothing world-to-world is shared, no duplicated logic. Each
  world keeps only its scheme surface: a light `world.py` (declarative: policy_methods,
  projection_spec, meta_extras, prompt_template) + a grade-time `drive.py` (numpy/sklearn drive loop,
  imported only by verify_suite under grader venv, so the light orchestration Python that loads
  tasks_def needs no ML deps) + a standalone `policy_runner.py` (sandbox can't import /root/src).
  `materialize` gained a generic `dockerfile_substitutions()` hook ({{WORLD_SLUG}}); one shared
  Dockerfile, env unified to HOR_ACTIVE_TASK, runner baked to /opt/mediated. budgeted-covtype
  regression: 4/4 tests, balanced accuracy 0.5848 (drive loop moved verbatim, behavior preserved).
- New world `worlds/label_budget/` (active-learning-as-a-task, commit-scheme item 2): student gets
  the train FEATURES unlabeled + a label budget L; grader drives rounds of label reveal under a shared
  pool, then one batched held-out test predict. Features-only projection (every label grader-side);
  test features handed over at predict via a model-readable file. Task `label-budget-covtype`
  (33da8224-...), covtype pool 137500 / test 56250, L=2000. Baseline (random acq + HGB) validates at
  balanced accuracy 0.518 (mid-ladder, headroom to the full-label ceiling). Protocol proven by a local
  runner-subprocess simulation before hosting.
- All 8 task venv tomls unified: model + grader groups both carry the full set (numpy, scikit-learn,
  xgboost, torch CPU, pytest, pytest-json-report); uv.lock regenerated (torch 2.5.1+cpu) and
  propagated. No import ever fails on a missing package whichever venv runs the code.

- Roadmap file added: commit_schemes/08_ordering_and_roadmap.md orders the six surviving work
  items (transcript replay first and concurrent; label budget the lead build; small-chunk third
  for its Delta* measurement; revision pairing after the label budget passes; instruments fifth;
  TEP compounding last, scaffold-only). Its Background section doubles as the bootstrap brief for
  new agents. Indexed in the folder README; §22a points to it.
- Second owner correction applied across ALL commit_schemes files: agents are computationally
  BOUNDED ("could have committed the same state later" does not mean "would have"; computation
  generates information; a precomputability claim kills only if the move is easy AND fast). Plus
  the front-loading principle: grade-time compute is time-fungible, only stream-revealed resources
  (e.g. purchased labels) resist front-loading. All 8 files restructured to the owner's format
  (The question / Background / The process / The result / Alternatives / Open questions, no
  verdict-first writing). Verdict movements: agent-time lock-in and checkpoint variants now
  UNDECIDED BY ARGUMENT (transcript-replay pre-test decides); instrument install's install-at-row-0
  collapse SURVIVES the correction (its dominant move is also fast and obvious); label budget
  strengthened (labels are the non-front-loadable resource); paid-revision standalone kill
  re-derived via front-loading. §22a/22b updated to match.
- Commit gate (file 07) rebuilt under the bounded-agent correction and the owner's section format.
  Probe LADDER separation is the primary test (4-6 probes, count adjacent steps beyond Delta*);
  the discoverability audit now covers BOTH reachability axes (discovery judgment + wall-clocked
  compute vs session and grade cap); vacuity twins are compute-matched so the gap isolates
  stream-revealed information, not front-loadable timing. Run order: floor, vacuity, luck, ladder,
  audit; graduation still user-gated.
- First commit-scheme verdict round REJECTED (verdicts without reasoning; all-agents-strong
  fallacy). Redone as 8 self-contained reasoning files in readmes/commit_schemes/ (band theory,
  agent-time commits, small-chunk, label budget, instruments, compounding, revision, falsifier
  gate), every step tagged PROVEN/ARGUMENT/CONJECTURE. Verdict changes: small-chunk KILL overturned
  (promote to pre-test); paid revision survives paired with the label budget; agent-time commits
  still killed but on the information-boundary argument, which does not assume agent strength.
  §22a-22b rewritten to point at the folder. Survivors: label budget (+revision pairing),
  instruments via metric escape, TEP compounding. Nothing built.
- Established in discussion (recorded in §22): plain global budget collapses via the shadow-price
  argument; the design constraint is a smart decider seeded by full peek, ignorant only of the
  gradually revealed test stream.
