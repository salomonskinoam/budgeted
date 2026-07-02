# Budgeted-acquisition tasks: submission set

One row per built task, with its student score **band** (the spread is the product, not the mean, see
`../CLAUDE.md`), a verdict, and task / run / analysis links. The full per-task writeup is one file under
[`readmes/tasks/`](tasks/), reached from each row's `analysis` link.

## Master table

`band` = worst→best non-errored run (raw metric). `spread` = band width. `levels` = distinguishable
tiers (SDK `rank_resolution` idea; see note). `submit`: **YES** valid skill-separating task, **NO**
rejected (band is noise), **PENDING** no rigorous verdict yet.

Per-row acquisition **budget** in parentheses (the difficulty lever, derived per dataset from an
offline budget sweep). Partial rows show scores graded so far (N/5). `submit`: **YES** skill-separating,
**NO** rejected (packed / unresolvable), **PENDING** still running or no rigorous verdict.

| task (budget) | metric | band (so far) | spread | levels | verdict / why | submit | links |
|---|---|---|---|---|---|---|---|
| budgeted-tep (15) | balanced-acc | 0.672–0.851 | 0.179 | ≥3 (top two 11.4σ apart) | scaffold: rigorous paired-gap 0.094 at 11.4σ (not noise) → graded tiers over a 2/5 floor. Single-file baseline re-run in flight | PENDING | [task](https://horizon.bespokelabs.ai/tasks/36abdac8-4edd-4304-a48c-53933cd34f62) · [run](https://horizon.bespokelabs.ai/evaluations/4d68f219-12f4-4f79-b61c-ee118052f610) · [analysis](tasks/budgeted-tep.md) |
| budgeted-covtype (6) | balanced-acc | running (0/5) | — | — | **the derma-analog**: real heterogeneous structure + resolved (Forest CoverType, 7 classes, rarest test 266, Elevation forced expensive). The one candidate that can both band and be measured | PENDING | [task](https://horizon.bespokelabs.ai/tasks/4de1e511-7738-4889-bed3-a0a532b051e5) · [run](https://horizon.bespokelabs.ai/evaluations/4d58d081-af97-4f4e-a3af-72ede82a5cdf) |
| budgeted-unsw (2) | balanced-acc | running (0/5) | — | — | razor-thin lever: adaptive beats fixed only at B=2 (one feature); dead by B≥4. Testing if students spread at all | PENDING | [task](https://horizon.bespokelabs.ai/tasks/f8cc010b-53f1-4745-9481-146ff721bb50) · [run](https://horizon.bespokelabs.ai/evaluations/27615e12-de7e-4b29-8ef7-900fe5870d0e) |
| budgeted-thyroid (3) | balanced-acc | 0.747–0.803 (4/5) | 0.056 | ~1 (packed) | **BURY**: acquisition is a step function, one decisive lab at cost 3, so students converge to ~0.80; spread ≈ 1 SE (rarest class 73). No graded ladder | NO* | [task](https://horizon.bespokelabs.ai/tasks/c69cfa04-5416-486c-b25a-0b345eea4d98) · [run](https://horizon.bespokelabs.ai/evaluations/6fcbf032-d5ef-4b13-9040-1fbc44a7a1ca) |
| budgeted-hydraulic (3) | balanced-acc | 0.991–0.994 (4/5) | 0.003 | 1 | **BURY**: one cheap sensor already solves the pump fault (~0.99 = full), budget never binds, students packed at the ceiling | NO* | [task](https://horizon.bespokelabs.ai/tasks/2935f9b4-ea7f-4127-8b73-b91a7d4d6f24) · [run](https://horizon.bespokelabs.ai/evaluations/f7318a3b-91ea-4456-a086-4d43bd449468) |
| budgeted-diabetes (3) | balanced-acc | 0.614–0.620 (3/5) | 0.006 | 1 | **BURY**: 30-day-readmission is learnable only from the cheap feature groups; the expensive labs are inert, so everyone converges to the ~0.62 ceiling (no failures, no spread) | NO* | [task](https://horizon.bespokelabs.ai/tasks/bb7097fc-2984-4b74-8088-e200de4373f3) · [run](https://horizon.bespokelabs.ai/evaluations/9f3883e9-5b3a-4e42-94a7-f170450101dd) |
| budgeted-derma (6) | balanced-acc | 0.931–0.946 (4/5) | 0.015 | 1 (unresolvable) | **BURY (resolution)**: real heterogeneous structure, but the test set is tiny (rarest class 4, SE ≈ 0.18); scores are packed within noise and cannot resolve a band at any run count. This is why covtype exists | NO* | [task](https://horizon.bespokelabs.ai/tasks/1a019b65-bfed-4779-8e00-e3982d3c7a51) · [run](https://horizon.bespokelabs.ai/evaluations/0dd9f969-ebd5-44ef-b891-aeeccfcd6502) |

`NO*` = bury verdict from partial data (4/5 or 3/5 graded); the graded runs are already packed far
inside the noise floor, so a 5th run cannot open a band (at most it adds a single low-outlier floor,
which is not a graded ladder).

**Rigorous verdict (paired resampling, not score-only).** The grader emits per-run `predictions_b64`
and offline replay (`scratch/analysis/recover_analyze.py`) reconstructs each run's policy and re-scores
it on the fixed test split. Replayed successes match hosted near-exactly (run 2: 0.8528 vs 0.8507; run
3: 0.7583 vs 0.7584), so the replay is faithful. `paired_gap_sigma` on those two = **gap 0.094, 11.4σ,
P(gap≤0)=0**: they are genuinely distinct tiers, not test noise. (run 4, hosted 0.672, used a
multi-file solution, which the single-file contract now forbids; it is excluded here, and its score
counts only under the old grader that allowed helper modules.)

Latest eval `fe32868b` (5 runs): **fail · fail · 0.672 · 0.758 · 0.851** (2 runs produced no working
policy, scored 0; no infra errors). Supersedes the first eval `2eb7b2e7` (7 runs: error · 0.717 ·
0.730 · 0.769 · 0.782 · 0.806), which was tighter (spread 0.089, ~2 tiers).

## Salvage sweep — real students on the offline-eliminated datasets
The offline acquisition-spread gate (`README_general_direction.md` §16–§19) rejected 5 datasets, but
that gate only tested *acquisition* spread (adaptive vs fixed with a shared predictor); it never
measured whether real LLM students spread (modeling/execution differences can band even a gate-FAIL).
So we built each as a task and ran 5 real student evals to **bury or salvage empirically** — "run it
and see" rather than trust the gate.

Per dataset the **budget** (the difficulty lever) was derived from a budget sweep as the tightest value
where acquisition could still matter (below the cheapest fixed panel that already wins): UNSW 2,
Hydraulic 3, Thyroid 3, Diabetes 3, Derma 6, CoverType 6. The sweeps showed only UNSW (razor-thin) and
Derma (real but tiny) even *could* band; Hydraulic/Thyroid/Diabetes have no working lever (one decisive
cheap feature / wrong target).

**Result so far confirms the gate:** the four dead-lever datasets return **packed** student scores
(spread far inside the per-class noise floor) → buried. The reason each buries is dataset-specific but
the same shape: no per-case decision the student can get right or wrong, so everyone converges. The
open question is now just **covtype** (the real, resolvable derma-analog) and **unsw**, both running.

## Notes
- Reference: oracle (masking-XGBoost + greedy eddi) validates at balanced accuracy **0.741**; noop ~0.045.
- **budgeted-tep is a SCAFFOLD** (synthetic + anonymized TEP). It proves the mediated-acquisition
  pipeline; the durable target is a real, big, many-class differential dataset
  (`README_general_direction.md` §17 / §19 / §20).
- Batch: `0067d7a3-4134-40d9-a4eb-c29faeeb24fe`.

## Methodology (how a band is judged)
Viability is the SDK's **gap test + rank_resolution** (`../sdk/methodology/noise_floor.md`;
`../sdk/hor_utils/noise.py` — `paired_gap_sigma`, `rank_resolution`): resample the fixed test blocks,
recompute each run's score, and report whether the top→bottom ordering (gap) and the middle tiers
(`n_levels`) survive test-set noise. Both require **per-run predictions**, not just scores.

### Rigorous verdict: hosted probe (no local compute)
The mediated grader emits `predictions_b64` per run (`verify.py` + `world.grade`). The rigorous
`rank_resolution` / `paired_gap_sigma` needs each run's policy replayed on the fixed test set — that
replay is XGBoost-heavy and **must run hosted**, never on the laptop (per `../CLAUDE.md`). So Phase 6 is
a **throwaway hosted task per dataset** whose oracle re-runs the recorded policies and returns
predictions (fusion's `recover_via_probe` pattern), not the local `recover_analyze.py`. The score-only
bands above are enough to bury the packed datasets; the hosted probe is reserved for the ones that
show a real spread (covtype / unsw / tep).
