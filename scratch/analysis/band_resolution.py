"""Band RESOLUTION per task (Method B) — the single source of truth for #band_supports.

For each recorded eval this computes, from the stored per-run `predictions_b64` (NO policy replay):
  - band        = [min,max] balanced accuracy over non-degenerate runs (failed/0-score excluded)
  - sigma_abs   = test-set resampling std of balanced accuracy, STRATIFIED by class (block_bootstrap_sigma
                  on the median-scoring run) — the noise floor, capped by the rarest test class
  - LSD         = z*sqrt(2)*sigma_abs   (z=2)
  - band_supports = 1 + width/LSD  (resolution(); how many tiers the band CAN hold)  <-- the decision metric
  - n_observed  = rank_resolution n_levels (how many tiers the runs LANDED in; contrast only)
  - gap p_le0   = paired_gap_sigma(best,worst) reversal rate (ceiling-safe cross-check / fallback)

y_true is reconstructed EXACTLY as the grader vended it: DataView(cfg).apply on the committed npz,
test split in saved order (only covtype's test_per_class subsamples). Each run asserts
len(preds)==len(y_true); if an eval predates the test-balance fix its preds match the raw test split,
handled by picking whichever y_true length matches.

Decision rule: band_supports >= 3 -> SUBMIT-viable; <= 2 -> reject. Ceiling bands (best ~1.0) invalidate
Method B -> use the gap test (p_le0) instead.

Run:  python scratch/analysis/band_resolution.py [dataset ...]   (default: all)
Writes scratch/analysis/<eval8>/band_supports.json and prints a summary table.
"""
from __future__ import annotations
import base64
import glob
import importlib
import json
import sys
import types
from pathlib import Path

import numpy as np
from sklearn.metrics import balanced_accuracy_score

from sdk.mediated.data_view import DataView
from sdk.hor_utils.noise import (
    contiguous_label_blocks, block_bootstrap_sigma, rank_resolution, paired_gap_sigma,
)
from sdk.hor_utils.resolution import resolution

REPO = Path(__file__).resolve().parents[2]
Z = 2.0
CEILING = 0.97          # best score above this -> Method B invalid, use the gap test
FLOOR = 0.15            # scores at/below this are degenerate (no working policy) -> excluded from the band


def bacc(yt, yp):
    return balanced_accuracy_score(yt, yp)


# dataset -> npz, config module (for the view), task-id, primary eval-id
DATASETS = {
    "covtype":     dict(npz="worlds/budgeted/data/covtype_anon.npz",  cfg="tasks_def.configs.budgeted_covtype",  eval="babd012a-4ae2-4349-99cb-a030db3f4491"),
    "tep":         dict(npz="worlds/budgeted/data/tep_anon.npz",      cfg="tasks_def.configs.budgeted_tep",      eval="4d68f219-12f4-4f79-b61c-ee118052f610"),
    "unsw":        dict(npz="worlds/budgeted/data/unsw_anon.npz",     cfg="tasks_def.configs.budgeted_unsw",     eval="27615e12-de7e-4b29-8ef7-900fe5870d0e"),
    "thyroid":     dict(npz="worlds/budgeted/data/thyroid_anon.npz",  cfg="tasks_def.configs.budgeted_thyroid",  eval="6fcbf032-d5ef-4b13-9040-1fbc44a7a1ca"),
    "thyroid-dropTSH": dict(npz="worlds/budgeted/data/thyroid_anon.npz", cfg="tasks_def.configs.budgeted_thyroid", eval="32c9a8ca-6045-4629-a27c-a01e13f656b7"),
    "hydraulic":   dict(npz="worlds/budgeted/data/hydraulic_anon.npz", cfg="tasks_def.configs.budgeted_hydraulic", eval="f7318a3b-91ea-4456-a086-4d43bd449468"),
    "diabetes":    dict(npz="worlds/budgeted/data/diabetes_anon.npz", cfg="tasks_def.configs.budgeted_diabetes", eval="9f3883e9-5b3a-4e42-94a7-f170450101dd"),
    "derma":       dict(npz="worlds/budgeted/data/derma_anon.npz",    cfg="tasks_def.configs.budgeted_derma",    eval="0dd9f969-ebd5-44ef-b891-aeeccfcd6502"),
    "label-budget-covtype": dict(npz="worlds/label_budget/data/covtype_anon.npz", cfg="tasks_def.configs.label_budget_covtype", eval="03bdb135-2c06-4dd3-bd13-b3c813daee88"),
}


def _cfg(mod_name):
    return types.SimpleNamespace(**importlib.import_module(mod_name).CONFIG)


def _y_true_variants(npz_path, cfg):
    """Both the DataView-transformed test labels and the raw test labels, keyed by length, so a run's
    preds can be aligned to whichever view was live at grade time."""
    z = np.load(REPO / npz_path)
    splits = {s: (z[f"{s}_features"], z[f"{s}_labels"]) for s in ("train", "val", "test")}
    tf, _ = DataView(cfg).apply(splits, z["costs"])
    y_dv = tf["test"][1].astype(np.int64)
    y_raw = z["test_labels"].astype(np.int64)
    return {len(y_dv): y_dv, len(y_raw): y_raw}


def _decode_runs(eval_id):
    """(run_number, preds int32, score) for every rollout of this eval that carries predictions."""
    runs = []
    for f in sorted(glob.glob(str(REPO / ".rollouts" / "**" / "*.json"), recursive=True)):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if d.get("evaluation_id") != eval_id:
            continue
        rn = d.get("run_number")

        def _loads(x):
            if isinstance(x, str):
                try:
                    return json.loads(x)
                except json.JSONDecodeError:
                    return None
            return x

        gr = _loads(d.get("grade_result"))
        meta = gr.get("metadata") or {} if isinstance(gr, dict) else {}
        fb = _loads(meta.get("feedback"))
        if not isinstance(fb, dict) or "predictions_b64" not in fb:
            runs.append((rn, None, float(d.get("score") or 0.0)))     # failed / no policy
            continue
        p = np.frombuffer(base64.b64decode(fb["predictions_b64"]), dtype=np.int32)
        runs.append((rn, p, float(fb.get("score", np.nan))))
    return sorted(runs, key=lambda r: (r[0] is None, r[0]))


def analyze(ds):
    spec = DATASETS[ds]
    cfg = _cfg(spec["cfg"])
    yvars = _y_true_variants(spec["npz"], cfg)
    raw = _decode_runs(spec["eval"])
    if not raw:
        return {"dataset": ds, "eval": spec["eval"], "error": "no rollouts on disk (pull first)"}

    # align each run to the matching y_true length; keep runs with predictions
    y_true = None
    preds, scores, failed = [], [], 0
    for rn, p, sc in raw:
        if p is None:
            failed += 1
            continue
        if len(p) not in yvars:
            return {"dataset": ds, "error": f"run {rn} preds len {len(p)} matches no y_true {list(yvars)}"}
        yt = yvars[len(p)]
        y_true = yt if y_true is None else y_true
        assert len(p) == len(y_true), f"mixed test sizes within eval {spec['eval']}"
        preds.append(p.astype(np.int64))
        scores.append(bacc(y_true, p))

    # non-degenerate band (drop collapsed/floor runs; they are a bonus floor, not the operating floor)
    keep = [i for i, s in enumerate(scores) if s > FLOOR]
    nd_scores = [scores[i] for i in keep]
    nd_preds = [preds[i] for i in keep]
    order = np.argsort(nd_scores)
    nd_scores = [nd_scores[i] for i in order]
    nd_preds = [nd_preds[i] for i in order]

    lo, hi = float(min(nd_scores)), float(max(nd_scores))
    width, mid = hi - lo, (hi + lo) / 2.0

    block_ids = contiguous_label_blocks(y_true)
    strata = y_true

    # sigma ruler: the MEDIAN-scoring non-degenerate run (a representative operating point)
    ref = nd_preds[len(nd_preds) // 2]
    bb = block_bootstrap_sigma(y_true, ref, block_ids, bacc, B=1000, seed=0, block_strata=strata)
    sigma_abs = float(bb["sigma"])

    # per-class test resolution cap
    classes, counts = np.unique(y_true, return_counts=True)
    rarest_i = int(np.argmin(counts))

    ceiling = hi >= CEILING or sigma_abs == 0.0 or len(set(nd_scores)) < 2

    # Method B (band_supports) — valid away from the ceiling
    if not ceiling:
        res = resolution(nd_scores, sigma_rel=sigma_abs / mid, z=Z)
        band_supports = float(res["tiers"])
        lsd = float(res["lsd"])
    else:
        band_supports, lsd = None, (Z * (2 ** 0.5) * sigma_abs)

    # #observed (contrast) — needs >=2 runs
    n_observed = int(rank_resolution(y_true, nd_preds, block_ids, bacc,
                                     block_strata=strata, B=1000, seed=0)["n_levels"]) if len(nd_preds) > 1 else 1

    # gap test (ceiling-safe cross-check / the fallback verdict for ceiling bands)
    gap = paired_gap_sigma(y_true, nd_preds[-1], nd_preds[0], block_ids, bacc,
                           B=1000, seed=0, block_strata=strata) if len(nd_preds) > 1 else {}

    if ceiling:
        verdict = "CEILING (Method B invalid) -> gap test: " + (
            "SUBMIT" if gap.get("p_le0", 1.0) < 0.05 and width > 3 * (Z * (2**0.5) * sigma_abs) else "REJECT")
    else:
        verdict = "SUBMIT" if band_supports >= 3.0 else "REJECT"

    return {
        "dataset": ds, "eval": spec["eval"],
        "n_runs_with_preds": len(preds), "n_failed": failed, "n_nondegenerate": len(nd_scores),
        "band": [lo, hi], "width": width, "mid": mid,
        "scores_sorted": [round(s, 4) for s in nd_scores],
        "n_test": int(len(y_true)), "n_classes": int(len(classes)),
        "rarest_class": int(classes[rarest_i]), "rarest_count": int(counts[rarest_i]),
        "per_class_counts": {int(c): int(n) for c, n in zip(classes, counts)},
        "sigma_abs": sigma_abs, "op": float(bb["op"]), "lsd": lsd,
        "band_supports": band_supports, "n_observed": n_observed,
        "ceiling": bool(ceiling),
        "gap": {k: (round(v, 4) if isinstance(v, float) else v)
                for k, v in gap.items() if k in ("gap", "sigma_gap", "ratio", "p_le0")},
        "verdict": verdict,
    }


def main(argv):
    keys = argv[1:] or list(DATASETS)
    rows = []
    for ds in keys:
        r = analyze(ds)
        rows.append(r)
        if "error" in r:
            print(f"{ds:22s} ERROR: {r['error']}")
            continue
        out = REPO / "scratch" / "analysis" / r["eval"][:8]
        out.mkdir(parents=True, exist_ok=True)
        (out / "band_supports.json").write_text(json.dumps(r, indent=2))
        bs = "ceiling" if r["ceiling"] else f"{r['band_supports']:.2f}"
        print(f"{ds:22s} band {r['band'][0]:.3f}-{r['band'][1]:.3f} w={r['width']:.3f} "
              f"sig={r['sigma_abs']:.4f} LSD={r['lsd']:.4f} rare={r['rarest_count']:>5d} "
              f"#obs={r['n_observed']} #supports={bs:>7s}  {r['verdict']}")
    return rows


if __name__ == "__main__":
    main(sys.argv)
