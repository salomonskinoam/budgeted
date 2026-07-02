"""One-off: build the committed anonymized-Hydraulic npz (pump fault, 3-class).
Mirrors make_data.py (TEP). Loader + cost tiers reuse scratch/bakeoff/acq_gate_hydraulic.py.

Gate buys a whole SENSOR (its 5 stats) for one cost. The budgeted world buys PER FEATURE,
so each sensor's 5 stat-features get cost = sensor_cost/5 (cheap 1/5=0.2, expensive 3/5=0.6);
a full sensor then costs exactly 1 or 3, matching the gate.

Run once; commits worlds/budgeted/data/hydraulic_anon.npz.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
from sklearn.model_selection import train_test_split

SEED = 0
BUDGET = 3
TARGET = "pump"
HERE = Path(__file__).resolve().parent
D = HERE.parents[1] / "scratch" / "bakeoff" / "data" / "hydraulic"

CHEAP = ["TS1", "TS2", "TS3", "TS4", "VS1", "CE", "CP", "SE"]
EXP = ["PS1", "PS2", "PS3", "PS4", "PS5", "PS6", "EPS1", "FS1", "FS2"]
SENS = CHEAP + EXP


def summ(name):
    a = np.loadtxt(D / f"{name}.txt")
    return np.stack([a.mean(1), a.std(1), a.min(1), a.max(1), a[:, -1]], 1)  # (2205,5)


# X: (2205, 85), 17 sensors x 5 stats
X = np.concatenate([summ(s) for s in SENS], 1).astype(np.float32)

# per-feature cost: each sensor's 5 features get sensor_cost/5
sensor_cost = np.array([1.0 if s in CHEAP else 3.0 for s in SENS])
orig_cost = np.repeat(sensor_cost / 5.0, 5)  # (85,), aligns with block layout of X

# labels: pump -> 3 classes
prof = np.loadtxt(D / "profile.txt")
col = {"cooler": 0, "valve": 1, "pump": 2, "accum": 3}
_, y = np.unique(prof[:, col[TARGET]], return_inverse=True)
ncls = len(np.unique(y))

# anonymize
rng = np.random.default_rng(SEED)
col_perm = rng.permutation(85)
X = X[:, col_perm]
costs = orig_cost[col_perm]
y = rng.permutation(ncls)[y]

# stratified split 0.55 / 0.225 / 0.225
Xtr, Xtmp, ytr, ytmp = train_test_split(X, y, train_size=0.55, stratify=y, random_state=SEED)
Xva, Xte, yva, yte = train_test_split(Xtmp, ytmp, train_size=0.5, stratify=ytmp, random_state=SEED)

np.savez_compressed(
    HERE / "data" / "hydraulic_anon.npz",
    train_features=Xtr, train_labels=ytr.astype(np.int64),
    val_features=Xva, val_labels=yva.astype(np.int64),
    test_features=Xte, test_labels=yte.astype(np.int64),
    costs=costs.astype(np.float32), budget=np.float32(BUDGET))

uc, cnt = np.unique(np.round(costs, 3), return_counts=True)
rare = np.bincount(yte, minlength=ncls)
rare = rare[rare > 0].min()
print(f"wrote hydraulic_anon.npz: n_train={len(ytr)} n_val={len(yva)} n_test={len(yte)}")
print(f"n_features={X.shape[1]} n_classes={ncls} budget={BUDGET}")
print("cost values + counts:", dict(zip(uc.tolist(), cnt.tolist())))
print(f"rarest test-class count={rare}  test dist={np.bincount(yte, minlength=ncls).tolist()}")
