"""BudgetedWorld: the feature-acquisition world as a thin MediatedWorld.

All the generic plumbing (sandbox, JSON transport, scoring, data vendoring, prehook projection, prompt
scaffolding, HorTask grade orchestration) lives in sdk/mediated/; the grade-time drive loop is in
drive.py (kept apart so this file needs no ML deps, the orchestration Python imports it). This file
supplies the declarative surface: the Policy interface (select_next + predict), which files the student
sees (train+val features AND labels), the per-case `budget` scalar, and the production prompt.
See sdk/mediated/world_base.py.
"""
from __future__ import annotations
from typing import Any, Dict

from sdk.mediated.world_base import MediatedWorld

_PROMPT = """\
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

The system loads **only this one file**: `{script_path}` must be entirely self-contained. Put the whole
policy (any helpers, any trained weights loaded at construction) inside it, do not split it across
modules or write other files the policy imports at runtime, only `{script_path}` is deployed and
anything else is discarded. The system constructs `Policy(data_dir)` once, then for each case calls
`select_next` repeatedly (revealing each acquired feature's value, charging its cost, never letting you
exceed the budget) and finally `predict`. Do not read anything outside {data_dir}/.

## Environment
{environment_info}
{hints}"""


class BudgetedWorld(MediatedWorld):
    def world_slug(self) -> str:
        return "budgeted"

    def policy_methods(self) -> tuple:
        return ("select_next", "predict")

    def projection_spec(self) -> Dict[str, Any]:
        return {
            "student_files": ["train_features.npy", "train_labels.npy",
                              "val_features.npy", "val_labels.npy"],
            "student_meta_keys": ["n_features", "n_classes", "budget", "costs", "feature_ids"],
            "forbidden": {"test_features.npy", "test_labels.npy"},
        }

    def meta_extras(self, z) -> Dict[str, Any]:
        # Budget is config-controlled (the difficulty knob) and overrides the npz scalar; fall back to
        # the npz only if the config omits it.
        cfg_budget = self.config.budget if "budget" in self.config else None
        return {"budget": float(cfg_budget if cfg_budget is not None else z["budget"])}

    def prompt_template(self) -> str:
        return _PROMPT
