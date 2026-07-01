"""Sandboxed policy runner: the subprocess end of the mediated grading protocol.

Baked into the image at /opt/budgeted/policy_runner.py (root-owned, 755 = readable/executable by
all, writeable by root only, so the student cannot tamper with it). verify.py spawns THIS under
model_venv, dropped to the `model` user, so neither this harness nor the imported student Policy can
read /data_root (700). It sees only /data_agent (train/val + meta) and the per-buy feature VALUES the
grader reveals. Speaks line-JSON with the grader over stdin/stdout:
  grader -> runner: {"cmd":"row","budget":B} | {"cmd":"end"}
  runner -> grader: {"act":"buy","fid":j} (then reads {"val":x|null}) | {"act":"predict","label":k}
"""
from __future__ import annotations
import contextlib
import importlib.util
import json
import sys
from pathlib import Path


def load_policy(policy_path, data_dir):
    spec = importlib.util.spec_from_file_location("student_policy", policy_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.Policy(data_dir)


def main() -> None:
    policy_path, data_dir = sys.argv[1], sys.argv[2]
    costs = json.loads((Path(data_dir) / "meta.json").read_text())["costs"]
    with contextlib.redirect_stdout(sys.stderr):        # keep training noise off the protocol channel
        policy = load_policy(policy_path, data_dir)

    out = sys.stdout

    def send(m):
        out.write(json.dumps(m) + "\n"); out.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        cmd = json.loads(line)
        if cmd["cmd"] == "end":
            break
        budget_left = float(cmd["budget"]); observed = {}
        while True:
            fid = policy.select_next(dict(observed), budget_left)
            if fid is None or fid in observed or costs[fid] > budget_left + 1e-9:
                break
            send({"act": "buy", "fid": int(fid)})
            resp = json.loads(sys.stdin.readline())
            if resp.get("val") is None:                 # grader refused (budget) -> stop buying
                break
            observed[fid] = float(resp["val"]); budget_left -= costs[fid]
        send({"act": "predict", "label": int(policy.predict(dict(observed)))})


if __name__ == "__main__":
    main()
