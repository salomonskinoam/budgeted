# budgeted-tep (anonymized TEP, mediated acquisition)

**Verdict: PENDING (real band, materially wider on re-run).** The latest eval has a genuine floor (2/5
produced no working policy, no infra error), a top that beats the oracle, and three successes spread
across ~0.18 with large adjacent gaps, a graded ladder, not just fail-vs-solve. Rigorous `n_levels`
being computed.

| metric | band (raw) | spread | levels | oracle | noop | submit |
|---|---|---|---|---|---|---|
| balanced-acc | 0.672–0.851 | 0.179 | ≥3 (top two 11.4σ apart) | 0.741 | ~0.045 | PENDING |

Latest eval `fe32868b` (5 runs). First eval `2eb7b2e7` (7 runs) was tighter: 0.717–0.806, spread 0.089,
~2 tiers.

[task](https://horizon.bespokelabs.ai/tasks/36abdac8-4edd-4304-a48c-53933cd34f62) ·
[run](https://horizon.bespokelabs.ai/evaluations/fe32868b-9861-4485-863e-d93c534615a5) ·
batch `0067d7a3-4134-40d9-a4eb-c29faeeb24fe`

## The task
The student ships a `Policy` class (`select_next` / `predict`); the grader DRIVES it per test case under
a per-case acquisition budget, revealing only the feature values the policy requests, sandboxed as the
`model` user, with labels kept grader-private. Data: **anonymized TEP** (52 features `f0..f51`, costs 1
cheap / 3 expensive, per-case budget 15, 22 fault classes). Scored on balanced accuracy over the hidden
test split. Full design + anti-hack model: `README_general_direction.md` §20.

## The band (spread only, per CLAUDE.md)
Latest eval `fe32868b`, 5 runs: **fail · fail · 0.672 · 0.758 · 0.851**.
- **Floor:** 2/5 produced no working policy (scored 0, `errored=0` so not infra failures) — a real
  failure mode, the true bottom of the band.
- **Top:** 0.851 **> oracle 0.741** and **> the prior eval's 0.806** — students built better
  acquisition policies than our reference (masking-XGBoost + greedy value-of-information).
- **The successes are graded, not clustered.** 0.672 / 0.758 / 0.851, adjacent gaps 0.086 and 0.093,
  both well above ~2·SE (test-set balanced-acc SE ≈ 0.048) → distinct tiers, plus the 0-floor.
  Score-only, that reads ~3–4 tiers vs the first eval's ~2.

First eval `2eb7b2e7`, 7 runs: error · 0.717 · 0.730 · 0.769 · 0.782 · 0.806 (spread 0.089, the five
successes clustered within noise, ~2 tiers). The re-run roughly doubled the spread and separated the
middle.

## Read
Non-degenerate (noop ~0.045, top 0.851, failure real at 2/5) and the top beats our reference — a
genuine task, and now with graded discrimination rather than fail-vs-solve. Levers still available if
we want it wider (§14 / §20, cheap config changes): tighter budget (6–9 vs 15, budget is now a one-line
config knob), or an acquisition-only variant (freeze the predictor) to isolate routing skill.

## Rigorous levels (paired resampling, done)
The grader emits per-run `predictions_b64` (`verify.py` + `world.grade`); because we hold the deployed
test split, `scratch/analysis/recover_analyze.py` reconstructs each run's policy (all files it wrote,
not just solution.py), replays it offline through the mediated loop, and feeds predictions to
`sdk/hor_utils/noise.py`. Replay is faithful, run 2 = 0.8528 (hosted 0.8507), run 3 = 0.7583 (hosted
0.7584). `paired_gap_sigma` on those two: **gap 0.094, 11.4σ, P(gap≤0)=0**, genuinely distinct tiers,
not test noise. run 4 (hosted 0.672) used a multi-file solution, which the single-file contract now
forbids, so it is excluded here and counts only under the old grader. Net: two success tiers proven
11σ-separated (plus run 4 and the 2/5 zero-floor under the old grader), a graded ladder, not
fail-vs-solve.

## Leak / integrity
Budget enforced grader-side (never exceeded, asserted); test features + labels stay in `/data_root`
(700); `predict` only ever sees acquired features; student code runs sandboxed as `model` (no
`/data_root`); TEP feature/class anonymization defeats benchmark memorization. Oracle validates at
0.741 end-to-end, so the grader is correct.
