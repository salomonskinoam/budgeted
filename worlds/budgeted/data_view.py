"""DataView: the single class that owns the transform from the committed npz to the /data_root view.

Applied HOSTED at setup_data time (in-container, model_venv), so re-costing features or dropping them
is a **config change + re-push**, never a local npz rebuild. Every dataset goes through it, an empty
spec is the identity transform. The config key `view` (in tasks_def/configs/<task>.py) drives it:

    "view": {
        "drop_features": [i, ...],        # feature indices to remove entirely (not acquirable)
        "cost_overrides": {i: cost, ...}, # set specific feature costs (e.g. make one expensive)
    }

Indices are into the committed (anonymized) feature order. Drops are applied after cost overrides and
re-index the remaining features contiguously; meta.json's n_features/costs reflect the transformed view.
"""
from __future__ import annotations

import numpy as np


class DataView:
    def __init__(self, cfg) -> None:
        view = dict(getattr(cfg, "view", None) or {})
        self.drop = sorted({int(i) for i in view.get("drop_features", [])})
        self.cost_overrides = {int(k): float(v) for k, v in dict(view.get("cost_overrides", {})).items()}

    def is_identity(self) -> bool:
        return not self.drop and not self.cost_overrides

    def apply(self, splits: dict, costs) -> tuple[dict, np.ndarray]:
        """splits: {split_name: (X, y)}; costs: per-feature vector. Returns (transformed splits, costs)."""
        costs = np.array(costs, dtype=float)
        for i, c in self.cost_overrides.items():
            costs[i] = c
        keep = np.array([j for j in range(len(costs)) if j not in set(self.drop)], dtype=int)
        out = {name: (X[:, keep], y) for name, (X, y) in splits.items()}
        return out, costs[keep]

    def summary(self) -> str:
        return f"drop={self.drop} cost_overrides={self.cost_overrides}" if not self.is_identity() else "identity"
