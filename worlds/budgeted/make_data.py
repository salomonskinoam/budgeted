"""One-off: build the committed anonymized-TEP npz from the raw TEP fault files.
Run once; commits worlds/budgeted/data/tep_anon.npz. setup_data.py loads it at build time.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from sklearn.model_selection import train_test_split

SEED = 0; BUDGET = 15
HERE = Path(__file__).resolve().parent
TEP = HERE.parents[1] / "scratch" / "bakeoff" / "data" / "tep"
Xs, ys = [], []
for i in range(22):
    a = np.loadtxt(TEP / f"d{i:02d}.dat")
    if a.shape[0] == 52: a = a.T
    Xs.append(a.astype(np.float32)); ys.append(np.full(len(a), i))
X = np.concatenate(Xs); y = np.concatenate(ys)
rng = np.random.default_rng(SEED)
col_perm = rng.permutation(52)
orig_cost = np.array([3 if 22 <= j < 41 else 1 for j in range(52)], float)
X = X[:, col_perm]; costs = orig_cost[col_perm]
y = rng.permutation(22)[y]
Xtr, Xtmp, ytr, ytmp = train_test_split(X, y, train_size=0.55, stratify=y, random_state=SEED)
Xva, Xte, yva, yte = train_test_split(Xtmp, ytmp, train_size=0.5, stratify=ytmp, random_state=SEED)
np.savez_compressed(HERE / "data" / "tep_anon.npz",
    train_features=Xtr, train_labels=ytr.astype(np.int64),
    val_features=Xva, val_labels=yva.astype(np.int64),
    test_features=Xte, test_labels=yte.astype(np.int64),
    costs=costs.astype(np.float32), budget=np.float32(BUDGET))
print(f"wrote tep_anon.npz: train={len(ytr)} val={len(yva)} test={len(yte)} "
      f"feat=52 classes=22 budget={BUDGET} cheap={int((costs==1).sum())} exp={int((costs==3).sum())}")
