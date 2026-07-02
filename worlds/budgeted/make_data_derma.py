"""One-off: build the committed anonymized UCI Dermatology (6-class) npz.
Run once; commits worlds/budgeted/data/derma_anon.npz. setup_data.py loads it at build time.

Loader + cost logic mirror scratch/bakeoff/acq_gate_derma.py: 34 features, y = last col (1..6 -> 0..5),
12 FREE features (clinical idx 0-10 + age idx 33) cost 0.0, 22 HISTOPATHOLOGY features (idx 11-32) cost 1.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
from sklearn.model_selection import train_test_split

SEED = 0
BUDGET = 6
N_CLASSES = 6
N_FEATURES = 34
HERE = Path(__file__).resolve().parent
DERMA = HERE.parents[1] / "scratch" / "bakeoff" / "data" / "derma" / "dermatology.data"

# --- load via the gate loader ---
rows = [ln.strip().split(",") for ln in open(DERMA) if ln.strip()]
A = np.array([[np.nan if v == "?" else float(v) for v in r] for r in rows], np.float32)
X = A[:, :N_FEATURES].astype(np.float32)                 # nan allowed (missing age)
y = (A[:, N_FEATURES].astype(int) - 1).astype(np.int64)  # 1..6 -> 0..5

# --- per-feature cost vector (free = clinical 0-10 + age 33; histo 11-32 = cost 1) ---
free_idx = set(range(0, 11)) | {33}
histo_idx = set(range(11, 33))
costs = np.array([1.0 if j in histo_idx else 0.0 for j in range(N_FEATURES)], np.float32)

# --- anonymize: shuffle columns (costs travel), relabel classes ---
rng = np.random.default_rng(SEED)
col_perm = rng.permutation(N_FEATURES)
X = X[:, col_perm]
costs = costs[col_perm]
y = rng.permutation(N_CLASSES)[y]

# --- stratified split 0.55 / 0.225 / 0.225 ---
Xtr, Xtmp, ytr, ytmp = train_test_split(X, y, train_size=0.55, stratify=y, random_state=SEED)
Xva, Xte, yva, yte = train_test_split(Xtmp, ytmp, train_size=0.5, stratify=ytmp, random_state=SEED)

np.savez_compressed(HERE / "data" / "derma_anon.npz",
    train_features=Xtr, train_labels=ytr.astype(np.int64),
    val_features=Xva, val_labels=yva.astype(np.int64),
    test_features=Xte, test_labels=yte.astype(np.int64),
    costs=costs.astype(np.float32), budget=np.float32(BUDGET))

rarest_test = int(np.bincount(yte, minlength=N_CLASSES).min())
print(f"wrote derma_anon.npz: train={len(ytr)} val={len(yva)} test={len(yte)} "
      f"feat={N_FEATURES} classes={N_CLASSES} budget={BUDGET} "
      f"cost0={int((costs==0.0).sum())} cost1={int((costs==1.0).sum())} "
      f"rarest_test_class={rarest_test}")
