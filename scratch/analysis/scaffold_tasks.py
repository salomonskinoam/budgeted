"""Generate budgeted-<ds> task scaffolds (config + registration + task dir) for the salvage datasets.
Mirrors tasks/budgeted-tep + tasks_def/{budgeted_tep,configs/budgeted_tep}. Run once from repo root."""
from __future__ import annotations
import shutil
from pathlib import Path

import numpy as np

ROOT = Path("/home/noam/src/budgeted")
TEP_TASK = ROOT / "tasks" / "budgeted-tep"

# ds -> (n_classes, budget)
DATASETS = {
    "unsw": (6, 2),
    "thyroid": (3, 3),
    "derma": (6, 6),
    "hydraulic": (3, 3),
    "diabetes": (2, 3),
    "covtype": (7, 6),
}

GENERIC_HINTS = [
    "No single feature (or fixed set of features) is best for every case; which features are "
    "worth acquiring depends on what you have already observed.",
    "Train a predictor that works from any partial subset of features (e.g. random-mask the "
    "training rows) so predict() is robust however few features a case ends up with.",
    "select_next can be adaptive: use the values you have already observed to decide what to "
    "acquire next, and stop early when more features would not change the prediction.",
    "Cheaper features let you acquire more of them within the budget; weigh value against cost.",
]
ZERO_COST_HINT = ("Some features have zero acquisition cost; acquiring those never spends budget, so "
                  "a good policy takes them whenever they help.")

CONFIG_TMPL = '''"""Per-task config for budgeted-{ds}: overrides the world defaults with this dataset's objective,
metric table, data layout, budget, and hints. Merge order: world CONFIG < this < live kwargs."""

CONFIG: dict = {{
    "objective": "balanced_accuracy",
    "metrics": {{
        "balanced_accuracy": {{"kind": "balanced_accuracy", "label": "balanced accuracy",
                              "lower_is_better": False}},
    }},
    "data_rel": "{ds}",
    "npz_name": "{ds}_anon.npz",
    "n_classes": {nc},
    # Per-case acquisition budget (cost units), derived from the offline budget sweep as the
    # constraining value for this dataset. Config-controlled; overrides the npz scalar.
    "budget": {budget},
    "hints": [
{hints}
    ],
}}
'''

REG_TMPL = '''"""Register the budgeted-{ds} task instance (importing this file registers it)."""
from pathlib import Path

from worlds.budgeted.world import BudgetedWorld
from tasks_def.configs import budgeted_{ds} as _cfg


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


BUDGETED_{DS} = BudgetedWorld(
    name="budgeted-{ds}",
    config=_cfg.CONFIG,
    source_dir=_repo_root() / "tasks" / "budgeted-{ds}",
)
'''

GRADER_TMPL = '''from tasks_def.budgeted_{ds} import BUDGETED_{DS}


def grade(transcript: str = "") -> object:
    return BUDGETED_{DS}.grade(transcript)
'''

TASKYAML_TMPL = '''prompt: |
  <PLACEHOLDER>

metadata:
  difficulty: "hard"
  category: "budgeted-acquisition"
  tags:
    - budgeted-acquisition
    - active-feature-acquisition
    - anonymized-{ds}
'''

IGNORE = shutil.ignore_patterns("__pycache__", ".validation", ".rollouts", ".rollouts-full", "*.pyc")


def main():
    init_lines = ["from tasks_def import budgeted_tep  # noqa: F401  importing registers the instance"]
    for ds, (nc, budget) in DATASETS.items():
        DS = ds.upper()
        has_free = float(np.load(ROOT / "worlds" / "budgeted" / "data" / f"{ds}_anon.npz")["costs"].min()) == 0.0
        hints = GENERIC_HINTS + ([ZERO_COST_HINT] if has_free else [])
        hints_str = ",\n".join('        "' + h + '"' for h in hints)

        (ROOT / "tasks_def" / "configs" / f"budgeted_{ds}.py").write_text(
            CONFIG_TMPL.format(ds=ds, nc=nc, budget=budget, hints=hints_str))
        (ROOT / "tasks_def" / f"budgeted_{ds}.py").write_text(REG_TMPL.format(ds=ds, DS=DS))

        task_dir = ROOT / "tasks" / f"budgeted-{ds}"
        if task_dir.exists():
            shutil.rmtree(task_dir)
        shutil.copytree(TEP_TASK, task_dir, ignore=IGNORE)
        (task_dir / "grader.py").write_text(GRADER_TMPL.format(ds=ds, DS=DS))
        (task_dir / "task.yaml").write_text(TASKYAML_TMPL.format(ds=ds))

        init_lines.append(f"from tasks_def import budgeted_{ds}  # noqa: F401  importing registers the instance")
        print(f"scaffolded budgeted-{ds}: n_classes={nc} budget={budget} free_features={has_free}")

    (ROOT / "tasks_def" / "__init__.py").write_text("\n".join(init_lines) + "\n")
    print("updated tasks_def/__init__.py with", len(init_lines), "task imports")


if __name__ == "__main__":
    main()
