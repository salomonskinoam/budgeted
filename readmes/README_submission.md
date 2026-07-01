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
| budgeted-tep | balanced-acc | 0.717–0.806 | 0.089 | ~2* (fail vs solve) | 1/7 | real floor (error) + top beats the 0.741 oracle, but the successful runs top-cluster within test noise | PENDING | [task](https://horizon.bespokelabs.ai/tasks/36abdac8-4edd-4304-a48c-53933cd34f62) · [run](https://horizon.bespokelabs.ai/evaluations/2eb7b2e7-c573-40dc-b134-35776173f74d) · [analysis](tasks/budgeted-tep.md) |

`*levels` is a **score-only approximation** (adjacent-score gaps vs the test-set balanced-acc SE
≈0.048). The rigorous SDK `rank_resolution` needs **per-run predictions** on the fixed test set, which
the mediated grader does not yet emit; the paired test may resolve more tiers. See TODO below.

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

### TODO for a rigorous verdict
The mediated grader must emit `predictions_b64` per run (as the fusion world does), so we can recover
predictions hosted and run `paired_gap_sigma` + `rank_resolution` for `gap / sigma / P(gap<=0) /
n_levels`. Until then every verdict here is a **score-only approximation**.
