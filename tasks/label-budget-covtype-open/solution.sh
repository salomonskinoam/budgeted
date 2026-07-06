#!/usr/bin/env bash
# Oracle/baseline: write the reference label-budget Policy to the student deliverable path. No run: the
# grader's mediated loop drives the Policy at grade time. This is ladder rung (b), uniform-random
# acquisition + one gradient-boosting fit, the reference baseline AND the end-to-end protocol smoke test.
set -euo pipefail
mkdir -p /workdir/solution
cat > /workdir/solution/solution.py <<'PYEOF'
"""Baseline label-budget Policy: buy L uniform-random pool rows, fit one HistGradientBoosting, predict."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier


class Policy:
    def __init__(self, data_dir):
        d = Path(data_dir)
        meta = json.loads((d / "meta.json").read_text())
        self.Xtr = np.load(d / "train_features.npy")
        self.C = int(meta["n_classes"])
        self.order = np.random.default_rng(0).permutation(len(self.Xtr))
        self.model = None

    def select_queries(self, labeled, budget_left):
        if not labeled:                                     # round 1: buy L random rows in one batch
            return [int(i) for i in self.order[:budget_left]]
        if self.model is None:                              # budget spent: fit once on the full set, stop
            rows = np.fromiter(labeled.keys(), dtype=int)
            y = np.fromiter((labeled[int(r)] for r in rows), dtype=int)
            self.model = HistGradientBoostingClassifier(max_iter=200).fit(self.Xtr[rows], y)
        return []

    def predict(self, X_test):
        return self.model.predict(X_test)
PYEOF
echo "wrote /workdir/solution/solution.py"
