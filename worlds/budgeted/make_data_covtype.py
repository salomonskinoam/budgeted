"""One-off: build the anonymized Forest CoverType npz (the big dermatology-analog: real, 7-class,
populous, heterogeneous feature relevance). Light prep only (fetch + split + save; NO training).
Cost tiers mirror derma's clinical-vs-histopath split: cheap context vs expensive survey features.
Elevation (the dominant single predictor) is placed in the EXPENSIVE tier so it is not a free lunch,
preserving the per-case acquisition tension. Run once; commits worlds/budgeted/data/covtype_anon.npz.
"""
from __future__ import annotations
import gzip
import io
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

SEED = 0
BUDGET = 6
SUBSAMPLE = 250_000  # keep the npz lean while leaving the rarest class populous (~270 in the test split)
HERE = Path(__file__).resolve().parent
UCI_URL = "https://archive.ics.uci.edu/static/public/31/covertype.zip"
CACHE = HERE / "data" / ".covtype.data.gz"

# Light prep: pull the 11 MB UCI zip (sklearn's fetch_covtype mirror 403s), extract covtype.data.gz,
# parse the 55-col CSV (54 features + target 1..7). No training.
if not CACHE.exists():
    raw = urllib.request.urlopen(UCI_URL, timeout=120).read()
    gz = zipfile.ZipFile(io.BytesIO(raw)).read("covtype.data.gz")
    CACHE.write_bytes(gz)
df = pd.read_csv(gzip.open(CACHE, "rb"), header=None).values
X = df[:, :54].astype(np.float32); y = (df[:, 54].astype(np.int64) - 1)   # 1..7 -> 0..6
n_features = X.shape[1]                                                    # 54

# Cost tiers. Columns (fetch_covtype order): 0=Elevation, 1..9 other cartographic, 10..13 Wilderness,
# 14..53 Soil_Type. Cheap(1) = cols 1..13 (context you get free from a DEM/GIS). Expensive(3) =
# Elevation (col 0, the dominant predictor) + the 40 soil-survey indicators (cols 14..53).
orig_cost = np.ones(n_features, float)
orig_cost[0] = 3.0
orig_cost[14:54] = 3.0

# Subsample stratified to keep it light + populous.
if len(y) > SUBSAMPLE:
    X, _, y, _ = train_test_split(X, y, train_size=SUBSAMPLE, stratify=y, random_state=SEED)

rng = np.random.default_rng(SEED)
col_perm = rng.permutation(n_features)
X = X[:, col_perm]; costs = orig_cost[col_perm]
y = rng.permutation(7)[y]

Xtr, Xtmp, ytr, ytmp = train_test_split(X, y, train_size=0.55, stratify=y, random_state=SEED)
Xva, Xte, yva, yte = train_test_split(Xtmp, ytmp, train_size=0.5, stratify=ytmp, random_state=SEED)
np.savez_compressed(HERE / "data" / "covtype_anon.npz",
    train_features=Xtr, train_labels=ytr.astype(np.int64),
    val_features=Xva, val_labels=yva.astype(np.int64),
    test_features=Xte, test_labels=yte.astype(np.int64),
    costs=costs.astype(np.float32), budget=np.float32(BUDGET))
print(f"wrote covtype_anon.npz: train={len(ytr)} val={len(yva)} test={len(yte)} "
      f"feat={n_features} classes=7 budget={BUDGET} cheap={int((costs==1).sum())} exp={int((costs==3).sum())} "
      f"rarest_test={int(np.bincount(yte).min())}")
