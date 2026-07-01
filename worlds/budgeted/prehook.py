"""Pre-agent setup. Runs as root via setup.sh (`python -m worlds.budgeted.prehook`, model_venv) before
the agent starts.

setup_data vendored the full dataset to /data_root (700). This hook asserts that, then projects the
STUDENT VIEW into /data_agent (755): train+val features+labels + the student meta.json (n_features,
n_classes, budget, costs). Test features and ALL labels stay grader-side in /data_root. A leak guard
fails the build if any test file lands in /data_agent. Sets final permissions + the student's writeable
solution dir. Logs via the SDK logger.
"""
from __future__ import annotations
import json
import shutil
import subprocess
import sys
from pathlib import Path

from sdk.path_mappings import CONTAINER_DATA_AGENT, CONTAINER_DATA_ROOT, CONTAINER_WORKDIR
from sdk.hor_logger import log
from worlds.budgeted.active import active_config

_CFG = active_config()
DATA_REL = _CFG.data_rel
DATA_AGENT = Path(CONTAINER_DATA_AGENT)
DATA_ROOT = Path(CONTAINER_DATA_ROOT)
AGENT_DIR = DATA_AGENT / DATA_REL
ROOT_DIR = DATA_ROOT / DATA_REL
SOLUTION = Path(CONTAINER_WORKDIR) / "solution"

STUDENT_FILES = ["train_features.npy", "train_labels.npy", "val_features.npy", "val_labels.npy"]


def assert_world_state() -> None:
    for s in ("train", "val", "test"):
        assert (ROOT_DIR / f"{s}_features.npy").exists(), f"missing {s}_features"
        assert (ROOT_DIR / f"{s}_labels.npy").exists(), f"missing {s}_labels"
    meta = json.loads((ROOT_DIR / "meta.json").read_text())
    assert meta["n_test"] > 0, f"n_test not positive: {meta}"
    log("prehook", f"world-state OK (full vendor in /data_root, n_test={meta['n_test']})")


def project_student_view() -> None:
    AGENT_DIR.mkdir(parents=True, exist_ok=True)
    for f in STUDENT_FILES:
        shutil.copy(ROOT_DIR / f, AGENT_DIR / f)
    # student meta: everything the student needs, nothing about the test split beyond its existence
    meta = json.loads((ROOT_DIR / "meta.json").read_text())
    student_meta = {k: meta[k] for k in ("n_features", "n_classes", "budget", "costs", "feature_ids")}
    (AGENT_DIR / "meta.json").write_text(json.dumps(student_meta, indent=2))
    log("prehook", f"projected student view: {STUDENT_FILES} + meta (budget={meta['budget']})")


def leak_guard() -> None:
    forbidden = {"test_features.npy", "test_labels.npy"}
    leaked = sorted(forbidden & {p.name for p in AGENT_DIR.iterdir()})
    assert not leaked, f"prehook leaked test data into /data_agent: {leaked}"


def set_permissions() -> None:
    subprocess.run(["chmod", "-R", "700", str(DATA_ROOT)], check=True)
    subprocess.run(["chmod", "-R", "755", str(DATA_AGENT)], check=True)
    SOLUTION.mkdir(parents=True, exist_ok=True)
    subprocess.run(["chown", "-R", "model:model", str(SOLUTION)], check=True)
    subprocess.run(["chmod", "-R", "755", str(SOLUTION)], check=True)
    log("prehook", "permissions set")


def main() -> None:
    assert_world_state()
    project_student_view()
    leak_guard()
    set_permissions()
    log("prehook", "all checks passed")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log("prehook", f"FAILED: {e}")
        sys.exit(1)
