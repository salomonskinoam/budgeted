"""Per-task config for budgeted-tep: overrides the world defaults with this dataset's objective,
metric table, data layout, and hints. Merge order: world CONFIG < this < live kwargs."""

CONFIG: dict = {
    "objective": "balanced_accuracy",
    "metrics": {
        "balanced_accuracy": {"kind": "balanced_accuracy", "label": "balanced accuracy",
                              "lower_is_better": False},
    },
    "data_rel": "tep",
    "npz_name": "tep_anon.npz",
    "n_classes": 22,
    "hints": [
        "No single feature (or fixed set of features) is best for every case; which features are "
        "worth acquiring depends on what you have already observed.",
        "Train a predictor that works from any partial subset of features (e.g. random-mask the "
        "training rows) so predict() is robust however few features a case ends up with.",
        "select_next can be adaptive: use the values you have already observed to decide what to "
        "acquire next, and stop early when more features would not change the prediction.",
        "Cheaper features let you acquire more of them within the budget; weigh value against cost.",
    ],
}
