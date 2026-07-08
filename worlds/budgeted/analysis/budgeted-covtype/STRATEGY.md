# budgeted-covtype: strategy analysis

HUMAN-owned. Updated independently of the generated record/table (the analysis seam,
sdk/methodology/noise_floor.md §15b). The machine-owned band numbers live in `band_supports.json`.

## The five solutions, held together

Scores are balanced accuracy on the fixed 2066-row test set (300/class, rarest class 0 = 266).
Ordered worst to best.

| run | score | acquisition | predictor | what separates it |
|---|---|---|---|---|
| run3 | 0.675 | **adaptive** EDDI: per-candidate VoI by imputation sampling, entropy-gain / cost, early stop | one NaN-masking XGB (random-mask augmentation) | general mask-tolerant model; adaptive routing spends compute but does not out-pick a fixed panel |
| run4 | 0.686 | **adaptive**: acquire elevation (f29) first, then 3 cheap features chosen by observed elevation bin | one NaN-masking XGB | same general predictor; per-case routing off the cheap gate still lands at the bottom |
| run1 | 0.739 | fixed panel [29,19,37,47] (greedy forward-search) | mean-impute + mask-vector XGB | worse panel (picked f19) and a weaker imputation predictor |
| run2 | 0.836 | fixed panel [29,47,37,15] | **dedicated 4-feature XGB** + shorter-prefix fallbacks | trains a model on exactly the acquired subset |
| run5 | 0.848 | fixed panel [29,47,37,16] | **dedicated 4-feature XGB** | same recipe as run2; marginal panel/hyperparam edge |

## Mechanism check (noise_floor.md §11: identifiable technique, not artifact)

**The band is real skill.** Endpoints 0.675 -> 0.848, gap ratio 15.6, P(gap<=0) = 0
(`band_supports.json`). The win is an identifiable technique, not a reproducible fluke: the top runs
**train a predictor on exactly the feature subset they acquire** (a dedicated model per panel), while
the bottom runs use **one general mask-tolerant model** that must serve every possible subset. The
edge is concentrated in the harder forest classes: run5 - run3 per-class recall delta is +0.30 on
class 3, +0.26 on class 5, +0.24 on class 2, +0.23 on class 4, while the populous classes 0/1 barely
move (-0.01 / +0.08). Same panel, better modeling of the ambiguous classes.

**All five are good failures, none dumb.** Every solution is a competent, trained policy. None
crashed, misread the `Policy` interface, exceeded budget, or reward-hacked. The low runs lose because
their predictor is genuinely weaker on the hard classes, which is exactly the skill the task is meant
to grade.

## The load-bearing finding: covtype bands on MODELING, not acquisition

The two genuinely adaptive policies (run3 EDDI VoI, run4 elevation-bin routing) are the **two lowest**
scores. The two highest are **fixed panels**. So at budget 6, per-case acquisition routing does not
beat a well-chosen fixed panel here; the spread comes entirely from the **prediction half**
(dedicated-subset model + panel selection), not the acquisition half. This is design-bible §2 in the
data ("skill = whatever scores higher; a fixed panel can be the skilled play") and it is consistent
with §16-17: covtype's feature relevance is not heterogeneous enough for adaptive-beats-fixed to be
the winning axis. The task is a valid band, but it validates the world's **grader / modeling** spread,
not the acquisition-routing thesis that TEP's 22 classes were brought in to carry.

## Note on anonymization

The top solutions correctly identify f29 as elevation (cost 3, high cardinality, dominant single
predictor) and reason about elevation bins. This is **not** benchmark memorization (no public covtype
leaderboard is being recalled); it is re-deriving a feature's role from the shipped training data,
which is the task. Anonymization still blocks the actual hack (memorizing published results); it does
not, and need not, hide feature semantics that are visible in the data.
