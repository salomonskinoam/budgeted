"""Concrete grade-time paths for the budgeted world (world-generic; no dataset dependency).

The deliverable is the student's Policy script; there is no separate produced .npy artifact (the
grader drives the Policy at grade time). Grader-only world files live next to this module under
/root/src (700). Grading always runs containerized, so bases are literal container paths.
"""
from pathlib import Path
from sdk.path_mappings import CONTAINER_WORKDIR, CONTAINER_ROOT, CONTAINER_TASK_LOG
from worlds.budgeted.config_world import CONFIG

WORKDIR_PATH: Path = Path(CONTAINER_WORKDIR)
ROOT_PATH: Path = Path(CONTAINER_ROOT)

SOLUTION_SCRIPT: Path = WORKDIR_PATH / CONFIG["script_rel"]   # the student's Policy; also the artifact

_WORLD_DIR = Path(__file__).resolve().parent
VERIFY_FILE: Path = _WORLD_DIR / "verify.py"
POLICY_RUNNER: Path = Path("/opt/budgeted/policy_runner.py")  # root-owned 755; runs sandboxed as model user
PYTEST_REPORT: Path = ROOT_PATH / "pytest_report.json"
BENCH_RESULT: Path = ROOT_PATH / "benchmark_result.json"
TASK_LOG: Path = Path(CONTAINER_TASK_LOG)
