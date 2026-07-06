"""Sandboxed policy runner for the LABEL-BUDGET world: the subprocess end of the mediated protocol.

Baked into the image at /opt/mediated/policy_runner.py (root-owned 755). sdk/mediated/harness.py spawns
THIS under model_venv, dropped to the `model` user, so neither this harness nor the imported student
Policy can read /data_root (700). It sees only /data_agent (the unlabeled pool + meta) and the labels
the grader reveals as they are purchased. Standalone by necessity: /root/src is locked 700 at grade
time, so the runner cannot import the shared SDK, it speaks the protocol itself.

Because the policy TRAINS mid-session (it refits between rounds), stdout is redirected to stderr for the
WHOLE session so training noise never corrupts the JSON channel; the protocol writes to the saved real
stdout. Line-JSON with the grader:
  grader -> runner: {"cmd":"select","budget_left":k} | {"cmd":"predict","test_path":p} | {"cmd":"end"}
  runner -> grader: {"act":"query","rows":[...]} (then reads {"labels":{id:cls,...}}) | {"act":"stop"}
                  | {"act":"predict","labels_b64":<int32 preds>}
"""
from __future__ import annotations
import base64
import contextlib
import importlib.util
import json
import sys

import numpy as np


def load_policy(policy_path, data_dir):
    spec = importlib.util.spec_from_file_location("student_policy", policy_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.Policy(data_dir)


def main() -> None:
    policy_path, data_dir = sys.argv[1], sys.argv[2]
    out = sys.stdout                                    # the protocol channel; saved before redirect

    def send(m):
        out.write(json.dumps(m) + "\n"); out.flush()

    with contextlib.redirect_stdout(sys.stderr):        # keep all policy/training noise off the channel
        policy = load_policy(policy_path, data_dir)
        labeled: dict[int, int] = {}
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            cmd = json.loads(line)
            c = cmd["cmd"]
            if c == "end":
                break
            if c == "select":
                rows = policy.select_queries(dict(labeled), int(cmd["budget_left"]))
                if not rows:
                    send({"act": "stop"})
                else:
                    send({"act": "query", "rows": [int(r) for r in rows]})
                    resp = json.loads(sys.stdin.readline())          # {"labels": {id: cls, ...}, ...}
                    for k, v in resp.get("labels", {}).items():
                        labeled[int(k)] = int(v)
            elif c == "predict":
                X = np.load(cmd["test_path"])
                preds = np.asarray(policy.predict(X), dtype=np.int32)
                send({"act": "predict", "labels_b64": base64.b64encode(preds.tobytes()).decode()})


if __name__ == "__main__":
    main()
