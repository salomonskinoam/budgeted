"""Build-time data prep: vendor the committed anonymized-TEP npz to /data_root.

Runs once in the Dockerfile via `python -m worlds.budgeted.setup_data` (model_venv, has numpy).
Loads worlds/budgeted/data/<npz_name> (pure np.load, no download, no pickle) and writes EVERY split
(train/val/test) with LABELS + meta.json to /data_root/<data_rel> (grader-only, 700). The prehook
later projects only train/val into /data_agent; test stays grader-side. Fails the build on any error.
"""
from __future__ import annotations
import json
import sys
import traceback
from pathlib import Path
import numpy as np

from sdk.path_mappings import CONTAINER_DATA_ROOT
from sdk.hor_logger import log
from worlds.budgeted.active import active_config
from worlds.budgeted.data_view import DataView

_CFG = active_config()
DATA_REL = _CFG.data_rel
NPZ = Path(__file__).resolve().parent / "data" / _CFG.npz_name
ROOT_DIR = Path(CONTAINER_DATA_ROOT) / DATA_REL
SPLITS = ("train", "val", "test")


def main() -> None:
    z = np.load(NPZ)
    ROOT_DIR.mkdir(parents=True, exist_ok=True)
    # The DataView applies the config-driven transform (drop features / re-cost) HOSTED here, so the
    # /data_root view (grader truth) reflects config, no local rebuild. Empty spec = identity.
    view = DataView(_CFG)
    splits = {s: (z[f"{s}_features"], z[f"{s}_labels"]) for s in SPLITS}
    splits, costs = view.apply(splits, z["costs"])
    for s in SPLITS:
        X, y = splits[s]
        np.save(ROOT_DIR / f"{s}_features.npy", X.astype(np.float32))
        np.save(ROOT_DIR / f"{s}_labels.npy", y.astype(np.int64))
    costs = costs.astype(np.float32)
    n_features = int(splits["train"][0].shape[1])
    # Budget is config-controlled (tasks_def/configs): the config value is the difficulty knob and
    # overrides whatever was baked into the npz; fall back to the npz only if the config omits it.
    cfg_budget = getattr(_CFG, "budget", None)
    budget = float(cfg_budget if cfg_budget is not None else z["budget"])
    meta = {
        "n_features": n_features,
        "n_classes": int(_CFG.n_classes),
        "budget": budget,
        "costs": costs.tolist(),
        "feature_ids": list(range(n_features)),
        "n_train": int(len(splits["train"][1])),
        "n_val": int(len(splits["val"][1])),
        "n_test": int(len(splits["test"][1])),
    }
    (ROOT_DIR / "meta.json").write_text(json.dumps(meta, indent=2))
    log("setup_data", f"vendored {DATA_REL} to /data_root ({view.summary()}): n_train={meta['n_train']} "
                      f"n_test={meta['n_test']} n_feat={meta['n_features']} budget={meta['budget']}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log("setup_data", f"FAILED: {e}\n{traceback.format_exc()}")
        sys.exit(1)
