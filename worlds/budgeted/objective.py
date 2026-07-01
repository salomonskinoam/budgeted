"""Resolve the objective into the primary metric and the guarded (gate) metrics.
One place, so the grade-time verify suite and the push-time prompt builder never disagree."""
from __future__ import annotations
from typing import Iterable, List, Tuple


def resolve(objective: str, metrics: Iterable[str]) -> Tuple[str, List[str]]:
    primary = objective
    gates = [m for m in metrics if m != primary]
    return primary, gates
