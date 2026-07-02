"""DataView: the single class that owns the transform from the committed npz to the /data_root view.

Applied HOSTED at setup_data time (in-container, model_venv), so re-costing features or dropping them
is a **config change + re-push**, never a local npz rebuild. Every dataset goes through it, an empty
spec is the identity transform. The config key `view` (in tasks_def/configs/<task>.py) drives it:

    "view": {
        "drop_features": [i, ...],        # feature indices to remove entirely (not acquirable)
        "cost_overrides": {i: cost, ...}, # set specific feature costs (e.g. make one expensive)
        "test_per_class": N,              # balance/cap the TEST split to N rows per class (see below)
    }

Feature indices are into the committed (anonymized) order; drops are applied after cost overrides and
re-index contiguously. `test_per_class` subsamples the TEST split to a class-balanced N-per-class set,
this keeps the mediated grade under the platform cap for big datasets (the grader drives every test row
one-at-a-time) AND improves resolution (every class gets N examples). meta.json reflects the transform.
"""
from __future__ import annotations

import numpy as np


class DataView:
    def __init__(self, cfg) -> None:
        view = dict(getattr(cfg, "view", None) or {})
        self.drop = sorted({int(i) for i in view.get("drop_features", [])})
        self.cost_overrides = {int(k): float(v) for k, v in dict(view.get("cost_overrides", {})).items()}
        self.test_per_class = int(view["test_per_class"]) if view.get("test_per_class") else None

    def is_identity(self) -> bool:
        return not self.drop and not self.cost_overrides and self.test_per_class is None

    def apply(self, splits: dict, costs) -> tuple[dict, np.ndarray]:
        """splits: {split_name: (X, y)}; costs: per-feature vector. Returns (transformed splits, costs)."""
        costs = np.array(costs, dtype=float)
        for i, c in self.cost_overrides.items():
            costs[i] = c
        keep = np.array([j for j in range(len(costs)) if j not in set(self.drop)], dtype=int)
        out = {name: (X[:, keep], y) for name, (X, y) in splits.items()}
        if self.test_per_class is not None and "test" in out:
            Xte, yte = out["test"]
            rng = np.random.default_rng(0)
            idx = []
            for c in np.unique(yte):
                ci = np.where(yte == c)[0]
                idx.extend(rng.choice(ci, size=min(self.test_per_class, len(ci)), replace=False))
            idx = np.array(sorted(int(i) for i in idx))
            out["test"] = (Xte[idx], yte[idx])
        return out, costs[keep]

    def summary(self) -> str:
        if self.is_identity():
            return "identity"
        return f"drop={self.drop} cost_overrides={self.cost_overrides} test_per_class={self.test_per_class}"
