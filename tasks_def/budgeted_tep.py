"""Register the budgeted-tep task instance (importing this file registers it)."""
from pathlib import Path

from worlds.budgeted.world import BudgetedWorld
from tasks_def.configs import budgeted_tep as _cfg


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


BUDGETED_TEP = BudgetedWorld(
    name="budgeted-tep",
    config=_cfg.CONFIG,
    source_dir=_repo_root() / "tasks" / "budgeted-tep",
)
