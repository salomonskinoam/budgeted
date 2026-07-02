# Budgeted-acquisition tasks: submission set

One row per built task, with its student score **band** (the spread is the product, not the mean, see
`../CLAUDE.md`), a verdict, and task / run / analysis links. The full per-task writeup is one file under
[`readmes/tasks/`](tasks/), reached from each row's `analysis` link.

## Master table

`band` = worst→best non-errored run (raw metric). `spread` = band width. `levels` = distinguishable
tiers (SDK `rank_resolution` idea; see note). `submit`: **YES** valid skill-separating task, **NO**
rejected (band is noise), **PENDING** no rigorous verdict yet.

| task | metric | band | spread | levels | errored | verdict | submit | links |
|---|---|---|---|---|---|---|---|---|
| budgeted-tep | balanced-acc | 0.672–0.851 | 0.179 | ≥3 (top two 11.4σ apart, P≤0=0) | 2/5 | real floor (2 no-policy failures, no infra error) + top 0.851 beats the 0.741 oracle and prior 0.806; rigorous paired-gap on the two reproducible successes = 0.094 at 11.4σ (not noise) → genuinely graded tiers, plus a third success (0.672) and the floor | PENDING | [task](https://horizon.bespokelabs.ai/tasks/36abdac8-4edd-4304-a48c-53933cd34f62) · [run](https://horizon.bespokelabs.ai/evaluations/fe32868b-9861-4485-863e-d93c534615a5) · [analysis](tasks/budgeted-tep.md) |

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

### Rigorous verdict: machinery now in place
The mediated grader now emits `predictions_b64` per run (`verify.py` + `world.grade`, as the fusion
world does). Because we hold the deployed test split (`tep_anon.npz`), recovery does not even need
fusion's hosted probe: `scratch/analysis/recover_analyze.py` reconstructs each run's `Policy` from its
transcript, replays it offline through the identical mediated/budget loop, and feeds the predictions to
`paired_gap_sigma` + `rank_resolution` for `gap / sigma / P(gap<=0) / n_levels`. Running now on
`fe32868b`; results will replace the score-only `*` estimate above.
