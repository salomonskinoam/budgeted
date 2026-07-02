"""Per-task config for budgeted-derma: overrides the world defaults with this dataset's objective,
metric table, data layout, budget, and hints. Merge order: world CONFIG < this < live kwargs."""

CONFIG: dict = {
    "objective": "balanced_accuracy",
    "metrics": {
        "balanced_accuracy": {"kind": "balanced_accuracy", "label": "balanced accuracy",
                              "lower_is_better": False},
    },
    "data_rel": "derma",
    "npz_name": "derma_anon.npz",
    "n_classes": 6,
    # Per-case acquisition budget (cost units), derived from the offline budget sweep as the
    # constraining value for this dataset. Config-controlled; overrides the npz scalar.
    "budget": 6,
    "hints": [
        "No single feature (or fixed set of features) is best for every case; which features are worth acquiring depends on what you have already observed.",
        "Train a predictor that works from any partial subset of features (e.g. random-mask the training rows) so predict() is robust however few features a case ends up with.",
        "select_next can be adaptive: use the values you have already observed to decide what to acquire next, and stop early when more features would not change the prediction.",
        "Cheaper features let you acquire more of them within the budget; weigh value against cost.",
        "Some features have zero acquisition cost; acquiring those never spends budget, so a good policy takes them whenever they help."
    ],
}
