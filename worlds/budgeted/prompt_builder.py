"""Builds the student-facing task prompt from a task's merged config.

Framed as a PRODUCTION task: a classifier that runs under a per-case feature-acquisition budget.
The prompt describes the deployment contract (a Policy the system calls per case, acquiring features
on request under a budget) and the deliverable interface. It never mentions grading, evaluation, a
test set, or a scoring harness: the student is asked to build the best policy for the stated
production setting, nothing more. One template serves every dataset; values come from the merged
config (world < task). See ../../sdk/DESIGN.md.
"""
from __future__ import annotations
import tomllib
from pathlib import Path

from sdk.hor_config import HorConfig
from sdk.path_mappings import CONTAINER_DATA_AGENT, CONTAINER_WORKDIR

_TEMPLATE = """\
You are building a classifier for a production system where acquiring each input feature has a cost,
and every case must be handled under a fixed acquisition budget. For each case the system starts
with nothing observed and repeatedly asks your policy which feature to acquire next; acquiring a
feature reveals its value and spends its cost. Once your policy stops (or the budget is exhausted),
it predicts the class from the features it chose to acquire. Build the policy that classifies as
accurately as possible under the budget (measured as balanced accuracy across cases, so every one of
the {n_classes} classes matters equally). Spending the budget well is the whole problem: features
differ in cost, and which ones are worth acquiring depends on the case.

## Data
Training data lives under {data_dir}/ as NumPy .npy arrays, fully observed (no budget at training
time, the budget only applies in production per the loop above):
- train_features.npy (n_cases x n_features), train_labels.npy (integer class ids 0..{n_classes_m1})
- val_features.npy, val_labels.npy (same layout) for your own model selection
{data_dir}/meta.json gives the exact n_features, n_classes, the per-feature acquisition cost vector
`costs` (feature id -> cost), and the per-case `budget`.

## Deliverable
Write a Python file to {script_path} defining a `Policy` class with this interface:

    class Policy:
        def __init__(self, data_dir):
            # data_dir is {data_dir}. Train here on train/val (fully observed).
        def select_next(self, observed: dict, budget_left: float) -> int | None:
            # observed maps already-acquired feature-id -> its value. Return the next feature id to
            # acquire (its cost must be <= budget_left), or None to stop acquiring for this case.
        def predict(self, observed: dict) -> int:
            # return the predicted class id given the features acquired for this case.

The system constructs `Policy(data_dir)` once, then for each case calls `select_next` repeatedly
(revealing each acquired feature's value, charging its cost, never letting you exceed the budget)
and finally `predict`. Do not read anything outside {data_dir}/. Only /workdir is writeable.

## Environment
{environment_info}
{hints}"""


class PromptBuilder:
    def __init__(self, cfg: HorConfig, source_dir: Path) -> None:
        self.cfg = cfg
        self.source_dir = Path(source_dir)

    @property
    def data_dir(self) -> str:
        return str(CONTAINER_DATA_AGENT / self.cfg.data_rel)

    @property
    def script_path(self) -> str:
        return str(CONTAINER_WORKDIR / self.cfg.script_rel)

    @property
    def environment_info(self) -> str:
        py = tomllib.loads((self.source_dir / "src" / "venvs" / "pyproject.toml").read_text())
        model = py["dependency-groups"]["model"]
        pkgs = ", ".join(sorted(d.split(">=")[0].split("==")[0] for d in model if "torch" not in d.lower())
                         + ["torch (cpu)"])
        return (f"- Python: /venvs/model_venv/bin/python\n"
                f"          Packages: {pkgs}\n"
                f"          Internet is blocked; pip installs will fail. Write intermediates to /workdir.")

    @property
    def hints(self) -> str:
        hints = list(self.cfg.hints) if "hints" in self.cfg else []
        if not hints:
            return ""
        return "\n## Hints\n\nYou might try any, none, or several of these:\n" + \
               "\n".join(f"- {h}" for h in hints)

    def build(self) -> str:
        n = int(self.cfg.n_classes)
        return _TEMPLATE.format(
            n_classes=n, n_classes_m1=n - 1,
            data_dir=self.data_dir, script_path=self.script_path,
            environment_info=self.environment_info, hints=self.hints,
        )
