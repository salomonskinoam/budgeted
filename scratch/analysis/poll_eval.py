"""Poll a hosted eval and print one line per run as it reaches a terminal state, then a final line.
Stdout is the Monitor event stream. Usage: python poll_eval.py <eval_id>"""
import json
import subprocess
import sys
import time

EID = sys.argv[1]
HORIZON = "/home/noam/src/budgeted/horizon_env/bin/horizon"
TERMINAL_RUN = {"completed", "succeeded", "failed", "errored", "cancelled"}
TERMINAL_EVAL = {"completed", "failed", "cancelled"}
seen = {}

while True:
    try:
        out = subprocess.run([HORIZON, "evaluations", "status", EID, "--json"],
                             capture_output=True, text=True, timeout=120)
        d = json.loads(out.stdout)
    except Exception:
        time.sleep(120)
        continue
    for r in d.get("rollout_statuses", []):
        rn = r.get("runNumber"); st = r.get("status"); sc = r.get("extracted_score")
        if st in TERMINAL_RUN and seen.get(rn) != st:
            seen[rn] = st
            print(f"run {rn}: {st}  score={sc}", flush=True)
    status = d.get("status", "")
    if status in TERMINAL_EVAL:
        ro = d.get("rollouts", {})
        print(f"EVAL {status}: {ro.get('successful')}/{ro.get('total')} ok  errored={ro.get('errored')}  "
              f"avg={ro.get('avg_score')}", flush=True)
        break
    time.sleep(120)
