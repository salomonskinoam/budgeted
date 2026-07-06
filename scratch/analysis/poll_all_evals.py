"""Poll the 6 salvage evals; print one band line per eval as it reaches a terminal state, then exit.
Network-only (status API), no local compute. Stdout is the Monitor event stream."""
import json
import subprocess
import time

HORIZON = "/home/noam/src/budgeted/horizon_env/bin/horizon"
EVALS = {
    "tep": "4d68f219-12f4-4f79-b61c-ee118052f610",
    "unsw": "27615e12-de7e-4b29-8ef7-900fe5870d0e",
    "thyroid-droptsh": "32c9a8ca-6045-4629-a27c-a01e13f656b7",
    "derma": "0dd9f969-ebd5-44ef-b891-aeeccfcd6502",
    "hydraulic": "f7318a3b-91ea-4456-a086-4d43bd449468",
    "diabetes": "9f3883e9-5b3a-4e42-94a7-f170450101dd",
    "covtype": "4d58d081-af97-4f4e-a3af-72ede82a5cdf",
}
TERMINAL = {"completed", "failed", "cancelled"}
done = set()

while len(done) < len(EVALS):
    for ds, eid in EVALS.items():
        if ds in done:
            continue
        try:
            out = subprocess.run([HORIZON, "evaluations", "status", eid, "--json"],
                                 capture_output=True, text=True, timeout=120)
            d = json.loads(out.stdout)
        except Exception:
            continue
        if d.get("status", "") in TERMINAL:
            done.add(ds)
            raw = [r.get("extracted_score") for r in d.get("rollout_statuses", [])]
            scores = sorted(x for x in raw if x is not None)
            n_none = sum(x is None for x in raw)
            ro = d.get("rollouts", {})
            print(f"budgeted-{ds} {d['status']}: scores={scores} failed_runs={n_none} "
                  f"avg={ro.get('avg_score')} errored={ro.get('errored')} "
                  f"({len(done)}/{len(EVALS)} evals done)", flush=True)
    if len(done) < len(EVALS):
        time.sleep(120)
print("ALL 6 SALVAGE EVALS DONE", flush=True)
