"""Recover each eval run's produced Policy from its transcript, replay it offline through the mediated
budget loop on the DEPLOYED test split, then run the SDK noise tools (rank_resolution / paired_gap).

Why offline replay works here (vs fusion's hosted probe): we hold worlds/budgeted/data/tep_anon.npz,
so the exact test split + costs + budget the grader used are reproducible locally. Each recovered
Policy runs in the bakeoff venv (xgboost/torch) as a subprocess, same select/reveal/predict protocol
as verify.run_mediated, budget enforced identically.

Usage:  scratch/bakeoff/.venv/bin/python scratch/analysis/recover_analyze.py <eval_id> <dataset> [runs]
Requires the `horizon` CLI (called by absolute path) for transcript fetch.
"""
from __future__ import annotations
import ast
import json
import os
import subprocess
import sys
import threading
from pathlib import Path

import numpy as np
from sklearn.metrics import balanced_accuracy_score

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from sdk.hor_utils.noise import rank_resolution, paired_gap_sigma, contiguous_label_blocks  # noqa: E402

DATA_DIR = ROOT / "worlds" / "budgeted" / "data"
RUNNER = ROOT / "scratch" / "world_derisk" / "policy_runner.py"
VENV = ROOT / "scratch" / "bakeoff" / ".venv" / "bin" / "python"
HORIZON = ROOT / "horizon_env" / "bin" / "horizon"
# Offline safety only (this is a dev tool, not the grader): mirror the platform's 600s grade cap so a
# pathological policy reproduces its hosted 0 instead of churning forever. We normally replay only the
# successful runs, so this rarely fires.
REPLAY_TIMEOUT_S = 600.0
BUDGET = None  # per-dataset per-row budget; set in main from the dataset's npz (== the task config budget)


def bacc(yt, yp):
    return balanced_accuracy_score(yt, yp)


def fetch_messages(eval_id: str, run: int) -> list:
    out = subprocess.run([str(HORIZON), "evaluations", "messages", eval_id, "--run", str(run), "--json"],
                         capture_output=True, text=True, timeout=300)
    return json.loads(out.stdout)


def reconstruct_files(msgs: list) -> dict:
    """Replay the str_replace_editor ops targeting solution.py, in sequence order, to its final text.

    The contract is single-file: the deliverable IS solution.py and the grader deletes everything else,
    so we reconstruct ONLY solution.py. A run whose policy imported helper modules simply fails to
    replay here, exactly as it now fails under the grader. Returns {"solution.py": text} or {}."""
    text = None
    for m in sorted(msgs, key=lambda x: x["sequence_number"]):
        c = m.get("content")
        if not isinstance(c, str) or "str_replace_editor" not in c:
            continue
        idx = c.find("{")
        if idx < 0:
            continue
        try:
            call = ast.literal_eval(c[idx:])
        except Exception:
            continue
        if not (isinstance(call, dict) and str(call.get("path", "")).endswith("/workdir/solution/solution.py")):
            continue
        cmd = call.get("command")
        if cmd == "create":
            text = call.get("file_text", "")
        elif cmd == "str_replace" and text is not None:
            text = text.replace(call["old_str"], call["new_str"], 1)
        elif cmd == "insert" and text is not None:
            lines = text.splitlines(keepends=True)
            at = int(call.get("insert_line", len(lines)))
            lines.insert(at, call.get("new_str", "") + "\n")
            text = "".join(lines)
    return {"solution.py": text} if text is not None else {}


def materialize_agent_dir(work: Path, z) -> Path:
    """Write the /data_agent view the runner + Policy read: train/val arrays + meta (costs, budget)."""
    agent = work / "data_agent"
    agent.mkdir(parents=True, exist_ok=True)
    for s in ("train", "val"):
        np.save(agent / f"{s}_features.npy", z[f"{s}_features"].astype(np.float32))
        np.save(agent / f"{s}_labels.npy", z[f"{s}_labels"].astype(np.int64))
    meta = {
        "n_features": int(z["train_features"].shape[1]),
        "n_classes": int(len(np.unique(z["train_labels"]))),
        "budget": BUDGET,
        "costs": z["costs"].astype(float).tolist(),
        "feature_ids": list(range(int(z["train_features"].shape[1]))),
    }
    (agent / "meta.json").write_text(json.dumps(meta))
    return agent


def run_policy(run_dir: Path, agent_dir: Path, Xte, costs) -> np.ndarray:
    """Drive one Policy through the mediated loop; return its test predictions (same enforcement as verify).
    run_dir holds solution.py plus any helper modules; cwd + PYTHONPATH = run_dir so sibling imports work."""
    n = len(Xte)
    sol_path = run_dir / "solution.py"
    env = {**os.environ, "PYTHONPATH": str(run_dir)}
    proc = subprocess.Popen([str(VENV), str(RUNNER), str(sol_path), str(agent_dir)],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1,
                            cwd=str(run_dir), env=env)
    watchdog = threading.Timer(REPLAY_TIMEOUT_S, proc.kill)
    watchdog.daemon = True
    watchdog.start()

    def send(m):
        proc.stdin.write(json.dumps(m) + "\n"); proc.stdin.flush()

    def recv():
        line = proc.stdout.readline()
        return None if line == "" else json.loads(line)

    preds = np.full(n, -1)
    for i in range(n):
        send({"cmd": "row", "budget": BUDGET})
        spent = 0.0; bought = set()
        while True:
            m = recv()
            if m is None:
                break
            if m["act"] == "buy":
                j = int(m["fid"])
                if j in bought or spent + costs[j] > BUDGET + 1e-9:
                    send({"val": None})
                else:
                    bought.add(j); spent += costs[j]
                    send({"val": float(Xte[i, j])})
            elif m["act"] == "predict":
                preds[i] = int(m["label"]); break
        if preds[i] < 0:
            break
    try:
        send({"cmd": "end"})
    except BrokenPipeError:
        pass
    proc.stdin.close(); proc.wait(); watchdog.cancel()
    preds[preds < 0] = 0
    return preds


def parse_runs(arg: str) -> list:
    return [int(x) for x in arg.split(",")] if "," in arg else list(range(1, int(arg) + 1))


def main():
    global BUDGET
    eval_id = sys.argv[1]
    dataset = sys.argv[2] if len(sys.argv) > 2 else "tep"
    runs = parse_runs(sys.argv[3]) if len(sys.argv) > 3 else list(range(1, 8))
    work = ROOT / "scratch" / "analysis" / eval_id[:8]
    work.mkdir(parents=True, exist_ok=True)
    z = np.load(DATA_DIR / f"{dataset}_anon.npz")
    BUDGET = float(z["budget"])
    print(f"dataset={dataset}  per-row budget={BUDGET}")
    Xte = z["test_features"].astype(np.float32); yte = z["test_labels"].astype(np.int64)
    costs = z["costs"].astype(float)
    agent = materialize_agent_dir(work, z)

    recovered = []
    for run in runs:
        try:
            msgs = fetch_messages(eval_id, run)
        except Exception as e:
            print(f"run {run}: fetch failed ({e})"); continue
        files = reconstruct_files(msgs)
        if "solution.py" not in files or "class Policy" not in files["solution.py"]:
            print(f"run {run}: no Policy recovered (errored/no deliverable) -> excluded from band")
            continue
        run_dir = work / f"run{run}"
        run_dir.mkdir(exist_ok=True)
        for name, text in files.items():
            (run_dir / name).parent.mkdir(parents=True, exist_ok=True)
            (run_dir / name).write_text(text)
        extra = [n for n in files if n != "solution.py"]
        try:
            preds = run_policy(run_dir, agent, Xte, costs)
            score = bacc(yte, preds)
        except Exception as e:
            print(f"run {run}: replay failed ({e})"); continue
        np.save(work / f"run{run}_pred.npy", preds)
        recovered.append((run, score, preds))
        print(f"run {run}: balanced_acc = {score:.4f}  (files: solution.py{'+' + ','.join(extra) if extra else ''})")

    # Split off the failure floor (timed-out / crashed policies land near the noop ~0.045 level); the
    # rigorous middle-tier resolution is measured over the SUCCESSFUL policies only.
    FLOOR = 0.15
    recovered.sort(key=lambda r: r[1])
    failures = [r for r in recovered if r[1] < FLOOR]
    successes = [r for r in recovered if r[1] >= FLOOR]
    print("\n==== BAND (recovered, offline replay) ====")
    print("all runs (low->high):", ", ".join(f"{r}:{s:.4f}" for r, s, _ in recovered))
    print(f"failures (<{FLOOR}, the floor):", [r for r, _, _ in failures] or "none")
    if len(successes) < 2:
        print("\n<2 successful runs; cannot compute rank_resolution."); return
    scores = np.array([r[1] for r in successes])
    preds_list = [r[2] for r in successes]
    block_ids = contiguous_label_blocks(yte)
    rr = rank_resolution(yte, preds_list, block_ids, bacc, block_strata=yte, B=1000, seed=0)
    gp = paired_gap_sigma(yte, preds_list[-1], preds_list[0], block_ids, bacc, B=1000, seed=0, block_strata=yte)

    print(f"\nsuccesses (low->high): " + ", ".join(f"{r}:{s:.4f}" for r, s, _ in successes))
    print(f"n_success={len(successes)}  min={scores.min():.4f}  max={scores.max():.4f}  "
          f"spread={scores.max()-scores.min():.4f}  std={scores.std():.4f}  mean={scores.mean():.4f}")
    print(f"\nrank_resolution: n_levels={rr['n_levels']}  mean_tau={rr['mean_tau']:.3f}  "
          f"std_tau={rr['std_tau']:.3f}  n_solutions={rr['n_solutions']}")
    print("  pair_flip (adjacent, low->high):", np.round(rr["pair_flip"], 3).tolist())
    print(f"\npaired_gap (best vs worst): gap={gp['gap']:.4f}  sigma={gp['sigma_gap']:.4f}  "
          f"ratio={gp['ratio']:.2f}  p_le0={gp['p_le0']:.4f}  n_blocks={gp['n_blocks']}")
    json.dump({"success_scores": scores.tolist(), "success_runs": [r for r, _, _ in successes],
               "n_failures": len(failures), "failure_runs": [r for r, _, _ in failures],
               "n_levels": rr["n_levels"], "mean_tau": rr["mean_tau"],
               "pair_flip": rr["pair_flip"].tolist(),
               "gap": gp["gap"], "sigma_gap": gp["sigma_gap"], "ratio": gp["ratio"], "p_le0": gp["p_le0"]},
              open(work / "verdict.json", "w"), indent=1)
    print(f"\nsaved -> {work}/verdict.json")


if __name__ == "__main__":
    main()
