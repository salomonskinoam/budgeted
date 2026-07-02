"""Register the budgeted-covtype task instance (importing this file registers it)."""
from pathlib import Path

from worlds.budgeted.world import BudgetedWorld
from tasks_def.configs import budgeted_covtype as _cfg


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


BUDGETED_COVTYPE = BudgetedWorld(
    name="budgeted-covtype",
    config=_cfg.CONFIG,
    source_dir=_repo_root() / "tasks" / "budgeted-covtype",
)
