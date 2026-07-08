"""Task-keyed band manifest: the single source of truth for which evals belong to each task, and the
world-authored presentation (budget label, task id, verdict line, submit flag, narrative). Keyed by the
bare task name. Replaces the old eval-hash `DATASETS` + `REPORT_META` split in band_resolution.py.

Each entry:
  world        - which world owns the task (routes analysis/readmes to worlds/<world>/...)
  cfg          - config module for DataView (y_true reconstruction). Shared by all of a task's evals.
  npz          - committed data file (relative to repo root). Shared by all of a task's evals.
  budget_label - col-1 "(...)" difficulty lever ("6", "L=2000", ...)
  task_id      - Horizon task id (for the task_url link)
  submit       - exact submit-column text ("**YES**", "NO (strategy)", ...)
  verdict_line - the world-authored one-liner (record header + table col 6)
  narrative    - optional {title -> markdown} extra record sections (empty for simple rows)
  evals        - the LIST: [{eval_id, label}]. evals[0] is the PRIMARY (headlines the table row).
                 A multi-eval task (thyroid) lists all its evals here; the SDK renders one block each.
"""
from __future__ import annotations

MANIFEST = {
    "budgeted-covtype": dict(
        world="budgeted", cfg="tasks_def.configs.budgeted_covtype",
        npz="worlds/budgeted/data/covtype_anon.npz",
        budget_label="6", task_id="4de1e511-7738-4889-bed3-a0a532b051e5", submit="**YES**",
        verdict_line="WIDE band, endpoints ~7 LSD apart; the test resolves it despite the rarest class holding 266 rows",
        narrative={},
        evals=[dict(eval_id="babd012a-4ae2-4349-99cb-a030db3f4491", label="")],
    ),
    "budgeted-tep": dict(
        world="budgeted", cfg="tasks_def.configs.budgeted_tep",
        npz="worlds/budgeted/data/tep_anon.npz",
        budget_label="15", task_id="36abdac8-4edd-4304-a48c-53933cd34f62", submit="**YES**",
        verdict_line="WIDE band, endpoints ~8 LSD apart (synthetic + anonymized Tennessee Eastman Process, 22 faults; accepted for tasks)",
        narrative={},
        evals=[dict(eval_id="4d68f219-12f4-4f79-b61c-ee118052f610", label="")],
    ),
    "budgeted-unsw": dict(
        world="budgeted", cfg="tasks_def.configs.budgeted_unsw",
        npz="worlds/budgeted/data/unsw_anon.npz",
        budget_label="2", task_id="f8cc010b-53f1-4745-9481-146ff721bb50", submit="NO",
        verdict_line="NARROW band, endpoints < 1 LSD apart (inside noise)",
        narrative={},
        evals=[dict(eval_id="27615e12-de7e-4b29-8ef7-900fe5870d0e", label="")],
    ),
    "budgeted-thyroid": dict(
        world="budgeted", cfg="tasks_def.configs.budgeted_thyroid",
        npz="worlds/budgeted/data/thyroid_anon.npz",
        budget_label="3", task_id="c69cfa04-5416-486c-b25a-0b345eea4d98", submit="NO",
        verdict_line="below the 3-tier bar (73-row rarest class inflates sigma); drop-TSH salvage TIGHTER, it failed",
        narrative={"Why the drop-TSH salvage failed": (
            "The drop-TSH salvage TIGHTENED the band (0.098 -> 0.020 width, #band_supports 2.57 -> 1.48), "
            "it did not widen it. Removing TSH removed the one discriminative axis, collapsing the "
            "endpoints. Confirms the design bible: no cost/feature knob manufactures the heterogeneity "
            "this data lacks (both variants REJECT)."
        )},
        evals=[dict(eval_id="6fcbf032-d5ef-4b13-9040-1fbc44a7a1ca", label="orig"),
               dict(eval_id="32c9a8ca-6045-4629-a27c-a01e13f656b7", label="drop-TSH")],
    ),
    "budgeted-hydraulic": dict(
        world="budgeted", cfg="tasks_def.configs.budgeted_hydraulic",
        npz="worlds/budgeted/data/hydraulic_anon.npz",
        budget_label="3", task_id="2935f9b4-ea7f-4127-8b73-b91a7d4d6f24", submit="NO",
        verdict_line="CEILING: gap test says endpoints indistinct; one cheap sensor solves it so the budget never binds",
        narrative={},
        evals=[dict(eval_id="f7318a3b-91ea-4456-a086-4d43bd449468", label="")],
    ),
    "budgeted-diabetes": dict(
        world="budgeted", cfg="tasks_def.configs.budgeted_diabetes",
        npz="worlds/budgeted/data/diabetes_anon.npz",
        budget_label="3", task_id="bb7097fc-2984-4b74-8088-e200de4373f3", submit="NO",
        verdict_line="NARROW band; readmission learnable from the cheap groups, expensive labs inert, converge ~0.62",
        narrative={},
        evals=[dict(eval_id="9f3883e9-5b3a-4e42-94a7-f170450101dd", label="")],
    ),
    "budgeted-derma": dict(
        world="budgeted", cfg="tasks_def.configs.budgeted_derma",
        npz="worlds/budgeted/data/derma_anon.npz",
        budget_label="6", task_id="1a019b65-bfed-4779-8e00-e3982d3c7a51", submit="NO",
        verdict_line="real spread, but the rarest test class = 4 rows buries it; unresolvable at any run count",
        narrative={},
        evals=[dict(eval_id="0dd9f969-ebd5-44ef-b891-aeeccfcd6502", label="")],
    ),
    "label-budget-covtype": dict(
        world="label_budget", cfg="tasks_def.configs.label_budget_covtype",
        npz="worlds/label_budget/data/covtype_anon.npz",
        budget_label="L=2000", task_id="33da8224-530b-4641-a61a-7f1a1655b823", submit="NO (strategy)",
        verdict_line="band VIABLE (wide, endpoints ~6 LSD apart), but ELIMINATED on strategy homogeneity (all 5 students wrote one recipe), not on the band",
        narrative={},
        evals=[dict(eval_id="03bdb135-2c06-4dd3-bd13-b3c813daee88", label="")],
    ),
    "label-budget-covtype-open": dict(
        world="label_budget", cfg="tasks_def.configs.label_budget_covtype_open",
        npz="worlds/label_budget/data/covtype_anon.npz",
        budget_label="L=1500", task_id="e9ee3601-21ce-4162-b868-ab424d7932cd", submit="**YES** (skill gradient)",
        verdict_line="the open-ended (no-hints) + rare-class-starved salvage of label-budget-covtype: a WIDE band AND a real, code-legible skill gradient (rare-class recall c1/c6, p_le0=0)",
        narrative={},
        evals=[dict(eval_id="303517c9-82fd-4641-84a2-cb4f88e41606", label="")],
    ),
}
