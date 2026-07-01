"""BudgetedWorld: the budgeted-acquisition world's HorTask subclass.

The student ships a Policy class (solution.py); the grader DRIVES it at grade time (verify.py runs
the mediated select/reveal/predict loop under budget). So there is no separate produced artifact and
no grade-time "produce" run of the deliverable: the deliverable IS the artifact, and the real work
happens in verify. The grade orchestration (gate -> benchmark -> score) lives in HorTask.
"""
from __future__ import annotations
import ast
import json
from pathlib import Path
from typing import Any, Dict, Optional

from sdk.hor_grading_result import GradingResult
from sdk.hor_task import HorTask

from worlds.budgeted import config_world
from worlds.budgeted.paths import (
    SOLUTION_SCRIPT, VERIFY_FILE, BENCH_RESULT, PYTEST_REPORT, TASK_LOG,
)
from worlds.budgeted.prompt_builder import PromptBuilder


class BudgetedWorld(HorTask):
    WORLD_CONFIG = config_world.CONFIG
    INJECTED_PACKAGES = ("worlds", "tasks_def")

    def build_prompt(self) -> str:
        return PromptBuilder(self.config, self.source_dir).build()

    def grade(self, transcript: str = "") -> GradingResult:
        """Ride the per-run test predictions into the feedback string (world-side; SDK stays generic).

        A hosted VALIDATION surfaces only GradingResult.feedback (it drops `details`/subscores), but the
        paired rank_resolution / gap test needs each run's per-row predictions. verify.py wrote
        `predictions_b64` into the benchmark result (-> result.details on the scored path); copy it into
        the feedback JSON so a hosted run returns it, to be read back during recovery. A run that
        produced no predictions (failed / no policy -> no details) is returned unchanged."""
        result = super().grade(transcript)
        if result.details and "predictions_b64" in result.details:
            feedback = json.loads(result.feedback)
            feedback["predictions_b64"] = result.details["predictions_b64"]
            result.feedback = json.dumps(feedback)
        return result

    def dockerfile_template(self) -> Path:
        return Path(__file__).resolve().parent / "Dockerfile"

    def _produce(self) -> dict:
        """No grade-time run of the deliverable: the student's Policy is not a runnable script, it is
        driven by verify.py. If solution.py is present, pass produce as a no-op; verify does the work.
        Absent solution.py -> the artifact check downstream fails the run (the noop case, scored 0)."""
        return {"returncode": 0, "timed_out": False, "duration_s": 0.0,
                "stdout": "policy present; graded by the mediated loop in verify", "stderr": ""}

    def artifact_gates(self, build: Dict[str, Any]) -> Optional[str]:
        """Pre-benchmark gate: the deliverable is a syntactically valid module defining a Policy class
        with select_next + predict. Checked by AST (no import): the Policy imports student ML libs
        (xgboost/torch) that live in model_venv, not the grader venv, so we must NOT import it here.
        Its real behavior is exercised by the sandboxed mediated run in verify."""
        if not SOLUTION_SCRIPT.exists():
            return f"no policy at {SOLUTION_SCRIPT}"
        try:
            tree = ast.parse(SOLUTION_SCRIPT.read_text())
        except SyntaxError as e:
            return f"solution.py has a syntax error: {e}"
        cls = next((n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Policy"), None)
        if cls is None:
            return "solution.py does not define a Policy class"
        methods = {n.name for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        for m in ("select_next", "predict"):
            if m not in methods:
                return f"Policy missing method {m}"
        return None

    def deliverable_path(self) -> Path:
        return SOLUTION_SCRIPT

    def produced_artifact_path(self) -> Path:
        return SOLUTION_SCRIPT

    def verify_file(self) -> Path:
        return VERIFY_FILE

    def bench_result_path(self) -> Path:
        return BENCH_RESULT

    def pytest_report_path(self) -> Path:
        return PYTEST_REPORT

    def task_log_path(self) -> Path:
        return TASK_LOG

    def upload_probe_file(self) -> Optional[Path]:
        return None
