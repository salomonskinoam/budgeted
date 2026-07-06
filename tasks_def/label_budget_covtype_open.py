"""Register the label-budget-covtype-open task instance (importing this file registers it).
A band-widening variant of label-budget-covtype; same world, its own config (see configs/)."""
from pathlib import Path

from worlds.label_budget.world import LabelBudgetWorld
from tasks_def.configs import label_budget_covtype_open as _cfg


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


LABEL_BUDGET_COVTYPE_OPEN = LabelBudgetWorld(
    name="label-budget-covtype-open",
    config=_cfg.CONFIG,
    source_dir=_repo_root() / "tasks" / "label-budget-covtype-open",
)
