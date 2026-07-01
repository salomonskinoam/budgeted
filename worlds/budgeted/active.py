"""Resolve the ACTIVE task's merged config at build/prehook time (no grade-time side-channel yet).

setup_data and prehook run as `python -m worlds.budgeted.{setup_data,prehook}` before the grader
writes /root/active_config.json, so they read the task name from BUDGETED_TASK (baked per image) and
look the merged config up in the registry. The `import tasks_def` is deferred to avoid an import cycle.
"""
from __future__ import annotations
import functools
import os


@functools.lru_cache(maxsize=None)
def active_config():
    name = os.environ["BUDGETED_TASK"]
    import tasks_def  # noqa: F401  deferred: importing registers every task instance
    from sdk.hor_task_registry import HorTaskRegistry
    return HorTaskRegistry.get(name).config
