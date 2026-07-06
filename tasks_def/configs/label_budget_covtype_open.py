"""Per-task config for label-budget-covtype-OPEN: a band-widening VARIANT of label-budget-covtype.
Same world (LabelBudgetWorld) and dataset, three parameters changed to try to spread student skill:

  - hints = []            : open-ended, the prompt states the goal + interface but names NO strategy
                            (the reference telegraphed uncertainty/diversity/rare-class/spend-curve and
                            every student wrote that same recipe -> converged). Discovery is now a skill.
  - pool_per_class        : sharpen rare-class starvation (dominant anon classes 2,3 stay huge, the
                            other five capped to 1000), so naive labeling starves the rare classes a
                            rare-class hunter can still buy -> acquisition skill separates.
  - label_budget = 1500   : slightly lower so each pick counts more.

This is a NEW task; the frozen reference (label_budget_covtype.py) is untouched.
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
    "label_budget": 1500,
    "view": {"pool_per_class": {0: 1000, 1: 1000, 2: 100000, 3: 100000, 4: 1000, 5: 1000, 6: 1000}},
    "hints": [],
}
