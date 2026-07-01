"""World config for the budgeted-acquisition world: the shared, dataset-agnostic base layer.

Only what every task shares: the deliverable interface (the student ships a Policy in solution.py)
and the scoring normalizers. Dataset-specific keys (data_rel, npz_name, n_classes, objective,
metrics, hints) live in tasks_def/configs/<task>.py; the SDK merges world < task < live kwargs.
Pure data, no imports. See ../../sdk/DESIGN.md.
"""

CONFIG: dict = {
    "script_rel": "solution/solution.py",   # the student's deliverable (a Policy class); grader drives it
    "best_observed": 1.0,                    # score normalizer: score = metric / best_observed / score_divisor
    "score_divisor": 1.0,
    "gate_tolerance": 0.0,                   # no gate metrics in v1
    "debug": False,                          # MUST be False in production
}
