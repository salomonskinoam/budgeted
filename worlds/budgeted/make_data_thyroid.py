"""One-off: build the committed anonymized-Thyroid (3-class) npz from the raw ann-thyroid files.
Run once; commits worlds/budgeted/data/thyroid_anon.npz. setup_data.py loads it at build time.

Loader + cost tiers mirror scratch/bakeoff/acq_gate_thyroid.py:
  X = first 21 cols, y = last col (class 1..3 -> 0..2).
  16 FREE clinical/history features (cols 0..15) -> cost 0.0
  5 LAB features (TSH,T3,TT4,T4U,FTI = cols 16..20) -> cost 3.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
from sklearn.model_selection import train_test_split

SEED = 0
BUDGET = 3
LAB_COST = 3
HERE = Path(__file__).resolve().parent
THY = HERE.parents[1] / "scratch" / "bakeoff" / "data" / "thyroid"


def load(path):
    rows = [list(map(float, ln.split())) for ln in open(path) if ln.strip()]
    a = np.array(rows, np.float32)
    return a[:, :21], (a[:, 21].astype(np.int64) - 1)   # X(21), y in {0,1,2}


# mirror the gate: separate files. ann-test.data IS the test split (~[73,177,3178]);
# ann-train.data splits into train / val. Keeps the imbalanced test distribution.
X_train_full, y_train_full = load(THY / "ann-train.data")
X_test, y_test = load(THY / "ann-test.data")

# per-feature cost vector: labs (cols 16..20) = 3, free (cols 0..15) = 0
orig_cost = np.array([LAB_COST if 16 <= j < 21 else 0.0 for j in range(21)], float)

# anonymize (rng(0); col_perm shuffle costs travel; relabel classes)
rng = np.random.default_rng(SEED)
col_perm = rng.permutation(21)
relabel = rng.permutation(3)
X_train_full = X_train_full[:, col_perm]
X_test = X_test[:, col_perm]
costs = orig_cost[col_perm]
y_train_full = relabel[y_train_full]
y_test = relabel[y_test]

# stratified split of the train file: train 0.55 / val 0.225 of the pooled scale.
# 0.55 / (0.55 + 0.225) = 0.7097 of the train file -> train; rest -> val.
train_frac = 0.55 / (0.55 + 0.225)
Xtr, Xva, ytr, yva = train_test_split(
    X_train_full, y_train_full, train_size=train_frac, stratify=y_train_full, random_state=SEED)
Xte, yte = X_test, y_test

np.savez_compressed(HERE / "data" / "thyroid_anon.npz",
    train_features=Xtr.astype(np.float32), train_labels=ytr.astype(np.int64),
    val_features=Xva.astype(np.float32), val_labels=yva.astype(np.int64),
    test_features=Xte.astype(np.float32), test_labels=yte.astype(np.int64),
    costs=costs.astype(np.float32), budget=np.float32(BUDGET))

print(f"wrote thyroid_anon.npz")
print(f"  n_train={len(ytr)} n_val={len(yva)} n_test={len(yte)}")
print(f"  n_features={Xtr.shape[1]} n_classes={len(np.unique(np.concatenate([ytr, yva, yte])))}")
print(f"  cost0={int((costs == 0).sum())} cost3={int((costs == 3).sum())}")
print(f"  test class counts={np.bincount(yte)} rarest_test={int(np.bincount(yte).min())}")
