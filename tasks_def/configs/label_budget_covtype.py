"""Per-task config for label-budget-covtype: active-learning-as-a-task on anonymized Forest CoverType.
Overrides the mediated-world defaults with this dataset's objective, metric, data layout, and the total
label budget L. Merge order: world CONFIG < this < live kwargs.

FROZEN REFERENCE. This is the exact config the 5-run band (eval 03bdb135, ~2 occupied levels) was
measured on: L=2000, natural pool, the how-to hints present. Do NOT edit it to run experiments; branch
a new task (see label_budget_covtype_open.py). See memory experiments-are-new-tasks.
"""

CONFIG: dict = {
    "objective": "balanced_accuracy",
    "metrics": {
        "balanced_accuracy": {"kind": "balanced_accuracy", "label": "balanced accuracy",
                              "lower_is_better": False},
    },
    "data_rel": "covtype",
    "npz_name": "covtype_anon.npz",
    "n_classes": 7,
    "label_budget": 2000,
    "view": {},
    "hints": [
        "Labeling the examples the current model is least sure about (uncertainty sampling) often beats labeling at random, but early on, before the model is any good, its uncertainty is noise, so a few well-spread labels first can help.",
        "Cover the feature space: picking pool rows far from what you have already labeled (a diversity / coreset strategy) avoids spending the budget on near-duplicates.",
        "Buy in a few rounds and retrain between them, so later picks use what earlier labels taught the model; buying everything at once cannot adapt.",
        "Rare classes drive the balanced-accuracy score, so make sure the budget reaches them rather than piling onto the common classes.",
        "Spend the budget deliberately: sparse early, denser once the model can judge its own uncertainty, and stop if extra labels stop helping.",
    ],
}
