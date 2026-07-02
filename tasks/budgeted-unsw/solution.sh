#!/usr/bin/env bash
# Oracle: write the reference Policy to the student deliverable path. No run: the grader's mediated
# loop drives the Policy at grade time. (Approval-gated oracle; a competent masking-predictor +
# greedy value-of-information acquisition.)
set -euo pipefail
mkdir -p /workdir/solution
cat > /workdir/solution/solution.py <<'PYEOF'
"""Reference budgeted-acquisition Policy: masking-robust XGBoost + eddi-style adaptive acquisition."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import xgboost as xgb

K = 2  # imputation samples per candidate for value-of-information


class Policy:
    def __init__(self, data_dir):
        d = Path(data_dir)
        meta = json.loads((d / "meta.json").read_text())
        self.D = int(meta["n_features"]); self.C = int(meta["n_classes"])
        self.costs = np.array(meta["costs"], float)
        Xtr = np.load(d / "train_features.npy"); ytr = np.load(d / "train_labels.npy").astype(int)
        rng = np.random.default_rng(0)
        Xaug, yaug = [], []
        for pk in (1.0, 0.5, 0.2, 0.0):
            M = Xtr.copy(); M[rng.random(M.shape) > pk] = np.nan
            Xaug.append(M); yaug.append(ytr)
        Xaug = np.vstack(Xaug); yaug = np.concatenate(yaug)
        cw = len(ytr) / (self.C * np.bincount(ytr, minlength=self.C).clip(1))
        self.clf = xgb.XGBClassifier(objective="multi:softprob", num_class=self.C, n_estimators=200,
                                     max_depth=6, learning_rate=0.15, subsample=0.8,
                                     tree_method="hist", n_jobs=4, verbosity=0)
        self.clf.fit(Xaug, yaug, sample_weight=cw[yaug])
        self.pool = Xtr

    def _vec(self, observed):
        v = np.full(self.D, np.nan, np.float32)
        for k, val in observed.items():
            v[int(k)] = val
        return v

    def select_next(self, observed, budget_left):
        cand = [j for j in range(self.D) if j not in observed and self.costs[j] <= budget_left + 1e-9]
        if not cand:
            return None
        base = self._vec(observed); rng = np.random.default_rng(len(observed))
        rows, idx = [], []
        for j in cand:
            for _ in range(K):
                r = base.copy(); r[j] = self.pool[rng.integers(len(self.pool)), j]
                rows.append(r); idx.append(j)
        P = self.clf.predict_proba(np.array(rows))
        val = {c: P[[t for t, jj in enumerate(idx) if jj == c]].std(0).mean() / self.costs[c] for c in cand}
        best = max(cand, key=lambda c: val[c])
        return best if val[best] > 1e-6 else None

    def predict(self, observed):
        return int(self.clf.predict_proba(self._vec(observed).reshape(1, -1))[0].argmax())
PYEOF
echo "wrote /workdir/solution/solution.py"
