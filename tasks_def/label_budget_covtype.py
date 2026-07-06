"""Register the label-budget-covtype task instance (importing this file registers it)."""
from pathlib import Path

from worlds.label_budget.world import LabelBudgetWorld
from tasks_def.configs import label_budget_covtype as _cfg


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


LABEL_BUDGET_COVTYPE = LabelBudgetWorld(
    name="label-budget-covtype",
    config=_cfg.CONFIG,
    source_dir=_repo_root() / "tasks" / "label-budget-covtype",
)
