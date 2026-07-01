"""Mediated grading suite for the budgeted-acquisition world.

Run by grader.py (HorTask.grade) via `pytest verify.py --json-report` under the grader venv (root).
Unlike a static-prediction world, the grader DRIVES the student's Policy at grade time: it spawns
the policy runner as the `model` user (so student code cannot read /data_root), then per test row
runs the select/reveal/predict loop, ENFORCING the per-row budget and revealing only requested
feature values. Test features + labels stay grader-side; labels are never transmitted. Balanced
accuracy vs the hidden test labels -> BENCH_RESULT for the grader.
"""
from __future__ import annotations
import base64
import json
import os
import pwd
import subprocess
import threading
from pathlib import Path

import numpy as np
import pytest
from sklearn.metrics import balanced_accuracy_score, f1_score

from sdk.path_mappings import CONTAINER_ACTIVE_CONFIG, CONTAINER_DATA_ROOT, CONTAINER_DATA_AGENT
from sdk.hor_task import MODEL_VENV_PYTHON
from worlds.budgeted.paths import SOLUTION_SCRIPT, BENCH_RESULT, POLICY_RUNNER
from worlds.budgeted.objective import resolve

# Kill a hanging policy well under the platform's 600s grade cap, so one bad row can't burn the whole
# grade. On kill the runner's stdout hits EOF and the loop below scores the rest as wrong.
GRADE_WATCHDOG_S = 480.0

_CFG = json.loads(Path(CONTAINER_ACTIVE_CONFIG).read_text())
METRICS = _CFG["metrics"]
PRIMARY, GATES = resolve(_CFG["objective"], METRICS)
BEST_OBSERVED = _CFG["best_observed"]
SCORE_DIVISOR = float(_CFG["score_divisor"])
N_CLASSES = int(_CFG["n_classes"])
DATA_REL = _CFG["data_rel"]
ROOT_DIR = Path(CONTAINER_DATA_ROOT) / DATA_REL
AGENT_DIR = Path(CONTAINER_DATA_AGENT) / DATA_REL


def _demote_to_model():
    """preexec_fn: drop the spawned runner to the `model` user so it cannot read /data_root (700)."""
    pw = pwd.getpwnam("model")
    os.setgid(pw.pw_gid)
    os.setuid(pw.pw_uid)


def run_mediated() -> dict:
    """Drive the student's Policy over all test rows under budget; return metrics + predictions."""
    meta = json.loads((ROOT_DIR / "meta.json").read_text())
    B = float(meta["budget"]); costs = np.array(meta["costs"], float)
    Xte = np.load(ROOT_DIR / "test_features.npy"); yte = np.load(ROOT_DIR / "test_labels.npy")
    n = len(yte)

    proc = subprocess.Popen(
        [MODEL_VENV_PYTHON, str(POLICY_RUNNER), str(SOLUTION_SCRIPT), str(AGENT_DIR)],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1,
        preexec_fn=_demote_to_model,
    )
    # Watchdog: a policy that hangs (infinite loop in select_next/predict) would otherwise block recv()
    # forever and burn the platform grade cap. Killing the proc makes readline() return "" (EOF), which
    # the loop below treats as a dead runner and scores every remaining row as wrong.
    watchdog = threading.Timer(GRADE_WATCHDOG_S, proc.kill)
    watchdog.daemon = True
    watchdog.start()

    def send(m):
        proc.stdin.write(json.dumps(m) + "\n"); proc.stdin.flush()

    def recv():
        line = proc.stdout.readline()
        return None if line == "" else json.loads(line)   # "" = EOF, the runner died

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
    watchdog.cancel()

    # A broken/crashed policy leaves rows unpredicted; count them as wrong (default class 0) so a bad
    # solution scores low rather than erroring the grade. Budget is enforced above, never exceeded.
    preds[preds < 0] = 0
    assert max_over <= 1e-9, f"budget violated: max overspend {max_over}"
    # predictions_b64: the fixed-test predictions for this run, so per-run stats + the SDK's paired
    # rank_resolution / gap test can be recomputed hosted (the fusion world emits this the same way).
    preds_b64 = base64.b64encode(preds.astype(np.int32).tobytes()).decode()
    return {
        "balanced_accuracy": float(balanced_accuracy_score(yte, preds)),
        "macro_f1": float(f1_score(yte, preds, average="macro")),
        "predictions_b64": preds_b64,
    }


@pytest.fixture(scope="module")
def benchmarks() -> dict:
    student = run_mediated()
    preds_b64 = student.pop("predictions_b64")               # per-run predictions, kept out of metrics
    v = float(student[PRIMARY])
    score = v / BEST_OBSERVED / SCORE_DIVISOR
    result = {
        "primary": PRIMARY, "score": score,
        "reason": f"{METRICS[PRIMARY]['label']} = {v:.4f} (best_observed={BEST_OBSERVED})",
        "gates": {}, "gate_tolerance": _CFG["gate_tolerance"],
        "predictions_b64": preds_b64,
    }
    for m, val in student.items():
        result[f"student_{m}"] = val
    BENCH_RESULT.write_text(json.dumps(result))
    return {"student": student, "result": result}


def test_solution_present() -> None:
    assert SOLUTION_SCRIPT.exists(), f"no policy at {SOLUTION_SCRIPT}"


def test_policy_interface() -> None:
    """The deliverable is a valid module defining a Policy class with select_next + predict. Checked
    by AST (no import): the Policy imports student ML libs that live in model_venv, not this grader
    venv, so importing it here would spuriously fail. Its real behavior runs sandboxed in the fixture."""
    import ast
    tree = ast.parse(SOLUTION_SCRIPT.read_text())
    cls = next((n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Policy"), None)
    assert cls is not None, "solution.py must define a Policy class"
    methods = {n.name for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    for m in ("select_next", "predict"):
        assert m in methods, f"Policy must define {m}"


@pytest.mark.parametrize("metric", GATES or [None])
def test_gate_not_worsened(metric, benchmarks: dict) -> None:
    if metric is None:
        return


def test_record_benchmark(benchmarks: dict) -> None:
    score = benchmarks["result"]["score"]
    assert isinstance(score, float) and score >= 0.0
