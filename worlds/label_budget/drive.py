"""Grade-time drive loop for the label-budget world: rounds of label reveal under a shared pool, then
one batched test prediction.

SEPARATE from world.py because it pulls numpy + the sklearn-backed harness, which must load ONLY under
the grader venv (verify_suite imports this at grade time). world.py stays light so the orchestration
Python that imports tasks_def needs no ML deps. See readmes/commit_schemes/03_train_label_budget.md.
"""
from __future__ import annotations
import base64
import json
import os
from pathlib import Path

import numpy as np

from sdk.path_mappings import CONTAINER_DATA_ROOT, CONTAINER_DATA_AGENT, CONTAINER_WORKDIR
from sdk.mediated.harness import enforce_single_file, spawn_runner, finalize


def run_mediated(world) -> dict:
    """Drive one active-learning session (rounds of label reveal under the shared budget L), then one
    batched test prediction; return metrics."""
    data_rel = world.config.data_rel
    root_dir = Path(CONTAINER_DATA_ROOT) / data_rel
    agent_dir = Path(CONTAINER_DATA_AGENT) / data_rel

    enforce_single_file()
    meta = json.loads((root_dir / "meta.json").read_text())
    L = int(meta["label_budget"]); n_train = int(meta["n_train"])
    ytr = np.load(root_dir / "train_labels.npy")
    Xte = np.load(root_dir / "test_features.npy"); yte = np.load(root_dir / "test_labels.npy")
    n_test = len(yte)

    proc, send, recv = spawn_runner(agent_dir)
    owned: dict = {}; state = {"pool_left": L, "dead": False}

    def do_round(budget_left) -> str:
        """One select round: prompt the policy, reveal min(new-requested, pool_left) labels. Returns
        'stop' / 'dead' / 'query'. The pool is grader-side, so the budget can never be exceeded."""
        send({"cmd": "select", "budget_left": int(budget_left)})
        m = recv()
        if m is None:
            state["dead"] = True; return "dead"
        if m.get("act") == "stop":
            return "stop"
        rows = m.get("rows", [])                                  # act == "query"
        new = [int(r) for r in rows if int(r) not in owned and 0 <= int(r) < n_train]
        take = new[:state["pool_left"]]                          # reveal min(requested_new, pool_left)
        reveal = {r: int(ytr[r]) for r in take}
        owned.update(reveal); state["pool_left"] -= len(take)
        send({"labels": {str(r): int(v) for r, v in reveal.items()},
              "budget_left": int(state["pool_left"])})
        return "query"

    try:
        while state["pool_left"] > 0 and not state["dead"]:
            before = state["pool_left"]
            r = do_round(state["pool_left"])
            if r in ("stop", "dead"):
                break
            if state["pool_left"] == before:                     # queried but bought nothing new -> done
                break
        if not state["dead"]:                                    # one final refit-and-stop pass at budget 0
            do_round(0)
    except (BrokenPipeError, ValueError, KeyError):
        state["dead"] = True

    # Batched predict: hand the held-out test FEATURES over a model-readable file (labels stay
    # grader-side). A broken/silent policy leaves the default class-0 predictions and scores low.
    preds = np.zeros(n_test, dtype=np.int32)
    if not state["dead"]:
        try:
            tmp = Path(CONTAINER_WORKDIR) / "tmp" / "test_features.npy"
            np.save(tmp, Xte.astype(np.float32)); os.chmod(tmp, 0o644)
            send({"cmd": "predict", "test_path": str(tmp)})
            m = recv()
            if m is not None and m.get("act") == "predict":
                got = np.frombuffer(base64.b64decode(m["labels_b64"]), dtype=np.int32)
                if len(got) == n_test:
                    preds = got.copy()
        except (BrokenPipeError, ValueError, KeyError):
            pass
    try:
        send({"cmd": "end"})
    except BrokenPipeError:
        pass
    proc.stdin.close(); proc.wait()
    return finalize(preds, yte)
