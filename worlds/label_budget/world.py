"""LabelBudgetWorld: active-learning-as-a-task, as a thin MediatedWorld.

The student gets the training FEATURES unlabeled plus a total label budget L. At grade time the grader
drives one active-learning session: round by round the policy names pool rows to have labeled, the
grader reveals those labels charging the shared pool, the policy trains on what it bought, then predicts
the whole (held-out) test set in ONE batched call. Train labels and all test data stay grader-side.

All the generic plumbing lives in sdk/mediated/; the grade-time drive loop is in drive.py (kept apart
so this file needs no ML deps, the orchestration Python imports it). This file supplies the declarative
surface: the Policy interface (select_queries + predict), the features-only projection (every label is
grader-side), the `label_budget` scalar, and the production prompt.
See sdk/mediated/world_base.py and readmes/commit_schemes/03_train_label_budget.md.
"""
from __future__ import annotations
from typing import Any, Dict

from sdk.mediated.world_base import MediatedWorld

_PROMPT = """\
You are building a classifier for a production setting where labels are expensive. You are given a large
POOL of training examples with their FEATURES but NOT their labels, plus a fixed budget of
{label_budget} labels you may purchase in total. Working in rounds, your policy names which pool rows to
have labeled next; each label you get is spent from the shared budget. You train on the labels you buy,
then classify a batch of new cases. The score is balanced accuracy across the {n_classes} classes (each
class weighted equally, so rare classes matter as much as common ones). Spending the label budget well
is the whole problem: which examples are most worth labeling depends on what you have already learned.

## Data
The unlabeled training pool lives under {data_dir}/ as NumPy .npy arrays:
- train_features.npy (n_pool x n_features)   # the pool; labels are NOT provided, you purchase them
{data_dir}/meta.json gives n_features, n_classes, n_train (the pool size; valid pool row ids are
0..n_train-1), and label_budget (the total labels you may purchase).

## Deliverable
Write a Python file to {script_path} defining a `Policy` class with this interface:

    class Policy:
        def __init__(self, data_dir):
            # data_dir is {data_dir}. Load train_features.npy + meta here (no labels are on disk).
        def select_queries(self, labeled: dict, budget_left: int) -> list[int]:
            # labeled maps pool_row_id -> its revealed class id, for EVERY row you have bought so far.
            # budget_left is how many labels you may still purchase. Return a list of NEW pool row ids
            # to have labeled this round (up to budget_left of them are honored), or [] to stop buying.
            # You are called repeatedly; (re)train your model here whenever you like. When budget_left
            # reaches 0 you are called once more so you can train on the full purchased set, then [].
        def predict(self, X_test) -> list[int]:
            # X_test is an (n_cases x n_features) array of new cases; return one class id per row.

The system loads **only this one file**: `{script_path}` must be entirely self-contained. Put the whole
policy (any helpers, any trained model) inside it, do not split it across modules or write other files
the policy imports at runtime, only `{script_path}` is deployed and anything else is discarded. The
system constructs `Policy(data_dir)` once, calls `select_queries` round by round (revealing the labels
you purchase, never exceeding the budget), and finally calls `predict` on a batch of held-out cases. Do
not read anything outside {data_dir}/.

## Environment
{environment_info}
{hints}"""


class LabelBudgetWorld(MediatedWorld):
    def world_slug(self) -> str:
        return "label_budget"

    def policy_methods(self) -> tuple:
        return ("select_queries", "predict")

    def projection_spec(self) -> Dict[str, Any]:
        # Features-only pool. EVERY label (train + val + test) and the test features stay grader-side.
        return {
            "student_files": ["train_features.npy"],
            "student_meta_keys": ["n_features", "n_classes", "n_train", "label_budget", "feature_ids"],
            "forbidden": {"train_labels.npy", "val_features.npy", "val_labels.npy",
                          "test_features.npy", "test_labels.npy"},
        }

    def meta_extras(self, z) -> Dict[str, Any]:
        return {"label_budget": int(self.config.label_budget)}

    def prompt_template(self) -> str:
        return _PROMPT

    def prompt_vars(self) -> Dict[str, Any]:
        return {"label_budget": int(self.config.label_budget)}
