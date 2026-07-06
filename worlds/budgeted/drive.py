"""Grade-time drive loop for the feature-acquisition world: the per-row select/reveal/predict protocol.

SEPARATE from world.py because it pulls numpy + the sklearn-backed harness, which must load ONLY under
the grader venv (verify_suite imports this at grade time). world.py stays light so the orchestration
Python that imports tasks_def (for build_prompt / grade orchestration) needs no ML deps. Was the
run_mediated half of the old worlds/budgeted/verify.py.
"""
from __future__ import annotations
import json
from pathlib import Path

import numpy as np

from sdk.path_mappings import CONTAINER_DATA_ROOT, CONTAINER_DATA_AGENT
from sdk.mediated.harness import enforce_single_file, spawn_runner, finalize


def run_mediated(world) -> dict:
    """Drive the student's Policy over all test rows under the per-case budget; return metrics."""
    data_rel = world.config.data_rel
    root_dir = Path(CONTAINER_DATA_ROOT) / data_rel
    agent_dir = Path(CONTAINER_DATA_AGENT) / data_rel

    enforce_single_file()
    meta = json.loads((root_dir / "meta.json").read_text())
    B = float(meta["budget"]); costs = np.array(meta["costs"], float)
    Xte = np.load(root_dir / "test_features.npy"); yte = np.load(root_dir / "test_labels.npy")
    n = len(yte)

    proc, send, recv = spawn_runner(agent_dir)
    preds = np.full(n, -1); max_over = 0.0; dead = False
    for i in range(n):
        if dead:
            break
        try:
            send({"cmd": "row", "budget": B})
            spent = 0.0; bought = set()
            while True:
                m = recv()
                if m is None:                                       # runner crashed -> stop
                    dead = True; break
                if m["act"] == "buy":
                    j = int(m["fid"])
                    if j in bought or spent + costs[j] > B + 1e-9:  # ENFORCE budget / no dup
                        send({"val": None})
                    else:
                        bought.add(j); spent += costs[j]
                        send({"val": float(Xte[i, j])})             # reveal ONLY the requested value
                elif m["act"] == "predict":
                    preds[i] = int(m["label"]); max_over = max(max_over, spent - B); break
        except (BrokenPipeError, ValueError, KeyError):             # broken student policy
            dead = True
    try:
        send({"cmd": "end"})
    except BrokenPipeError:
        pass
    proc.stdin.close(); proc.wait()

    # A broken/crashed policy leaves rows unpredicted; count them as wrong (default class 0) so a bad
    # solution scores low rather than erroring the grade. Budget is enforced above, never exceeded.
    preds[preds < 0] = 0
    assert max_over <= 1e-9, f"budget violated: max overspend {max_over}"
    return finalize(preds, yte)
