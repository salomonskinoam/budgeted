"""Register the budgeted-derma task instance (importing this file registers it)."""
from pathlib import Path

from worlds.budgeted.world import BudgetedWorld
from tasks_def.configs import budgeted_derma as _cfg


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


BUDGETED_DERMA = BudgetedWorld(
    name="budgeted-derma",
    config=_cfg.CONFIG,
    source_dir=_repo_root() / "tasks" / "budgeted-derma",
)
