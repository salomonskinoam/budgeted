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

_CFG = active_config()
DATA_REL = _CFG.data_rel
NPZ = Path(__file__).resolve().parent / "data" / _CFG.npz_name
ROOT_DIR = Path(CONTAINER_DATA_ROOT) / DATA_REL
SPLITS = ("train", "val", "test")


def main() -> None:
    z = np.load(NPZ)
    ROOT_DIR.mkdir(parents=True, exist_ok=True)
    for s in SPLITS:
        np.save(ROOT_DIR / f"{s}_features.npy", z[f"{s}_features"].astype(np.float32))
        np.save(ROOT_DIR / f"{s}_labels.npy", z[f"{s}_labels"].astype(np.int64))
    costs = z["costs"].astype(np.float32)
    # Budget is config-controlled (tasks_def/configs): the config value is the difficulty knob and
    # overrides whatever was baked into the npz; fall back to the npz only if the config omits it.
    cfg_budget = getattr(_CFG, "budget", None)
    budget = float(cfg_budget if cfg_budget is not None else z["budget"])
    meta = {
        "n_features": int(z["train_features"].shape[1]),
        "n_classes": int(_CFG.n_classes),
        "budget": budget,
        "costs": costs.tolist(),
        "feature_ids": list(range(int(z["train_features"].shape[1]))),
        "n_train": int(len(z["train_labels"])),
        "n_val": int(len(z["val_labels"])),
        "n_test": int(len(z["test_labels"])),
    }
    (ROOT_DIR / "meta.json").write_text(json.dumps(meta, indent=2))
    log("setup_data", f"vendored {DATA_REL} to /data_root: n_train={meta['n_train']} "
                      f"n_test={meta['n_test']} n_feat={meta['n_features']} budget={meta['budget']}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log("setup_data", f"FAILED: {e}\n{traceback.format_exc()}")
        sys.exit(1)
