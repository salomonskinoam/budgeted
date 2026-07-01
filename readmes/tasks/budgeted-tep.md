# budgeted-tep (anonymized TEP, mediated acquisition)

**Verdict: PENDING (real but top-clustered).** The band has a genuine floor (one run errored) and a top
run that beats the oracle, but the successful runs cluster (0.72–0.81) within test-set noise, so it
currently resolves ~2 tiers (fail vs solve), not a graded ladder. Real, non-degenerate, not yet a
confidently wide band.

| metric | band (raw) | spread | levels | oracle | noop | submit |
|---|---|---|---|---|---|---|
| balanced-acc | 0.717–0.806 | 0.089 | ~2* | 0.741 | ~0.045 | PENDING |

[task](https://horizon.bespokelabs.ai/tasks/36abdac8-4edd-4304-a48c-53933cd34f62) ·
[run](https://horizon.bespokelabs.ai/evaluations/2eb7b2e7-c573-40dc-b134-35776173f74d) ·
batch `0067d7a3-4134-40d9-a4eb-c29faeeb24fe`

## The task
The student ships a `Policy` class (`select_next` / `predict`); the grader DRIVES it per test case under
a per-case acquisition budget, revealing only the feature values the policy requests, sandboxed as the
`model` user, with labels kept grader-private. Data: **anonymized TEP** (52 features `f0..f51`, costs 1
cheap / 3 expensive, per-case budget 15, 22 fault classes). Scored on balanced accuracy over the hidden
test split. Full design + anti-hack model: `README_general_direction.md` §20.

## The band (spread only, per CLAUDE.md)
7 runs: **errored · 0.717 · 0.730 · 0.769 · 0.782 · 0.806** (run 4 was still finishing at write time).
- **Floor:** 1/7 errored (produced no working policy) — a real failure mode, the true bottom of the band.
- **Top:** 0.806 **> oracle 0.741** — students built better acquisition policies than our reference
  (masking-XGBoost + greedy value-of-information). Healthy: the task rewards skill above the floor.
- **The 5 successful cluster.** Adjacent gaps are 0.013 / 0.039 / 0.013 / 0.024, all below ~2·SE
  (test-set balanced-acc SE ≈ 0.048), so they sit within test noise of each other → ~1 tier among the
  successful, ~2 with the error included.

## Read
Non-degenerate (noop ~0.045, top 0.806, failure possible) and the top beats our reference — a genuine
task. But the discrimination today is **fail-vs-solve**, not fine-grained: good agents converge to
~0.8. To widen the band (levers, §14 / §20, all cheap config changes):
- **Tighter budget** (6–9 vs 15) — the offline acquisition-spread gate showed the *largest*
  adaptive-vs-fixed gaps at tight budgets, so weak policies should fall further.
- **Acquisition-only variant** (freeze the predictor) — isolates routing skill, removing the
  "who trained a better XGBoost" confound that lets everyone cluster high.

## `*levels` caveat + rigorous next step
The ~2 levels is a **score-only, unpaired approximation** (adjacent gaps vs an absolute per-run SE),
which over-states noise; the SDK's paired `rank_resolution` may resolve more. To get the real
`gap / sigma / P(gap<=0) / n_levels`, the grader must emit per-run `predictions_b64` (as the fusion
world does) so predictions can be recovered hosted and fed to `sdk/hor_utils/noise.py`.

## Leak / integrity
Budget enforced grader-side (never exceeded, asserted); test features + labels stay in `/data_root`
(700); `predict` only ever sees acquired features; student code runs sandboxed as `model` (no
`/data_root`); TEP feature/class anonymization defeats benchmark memorization. Oracle validates at
0.741 end-to-end, so the grader is correct.
