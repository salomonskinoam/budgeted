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

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))   # repo root, so `sdk`/`tasks_def` import
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


# dataset -> world, npz, config module (for the view), task-id, primary eval-id.
# `world` routes the emitted record + table to worlds/<world>/readmes/ (multi-world: each world owns its
# own submission table + records; the SDK band_report is world-agnostic and takes the paths explicitly).
DATASETS = {
    "covtype":     dict(world="budgeted", npz="worlds/budgeted/data/covtype_anon.npz",  cfg="tasks_def.configs.budgeted_covtype",  eval="babd012a-4ae2-4349-99cb-a030db3f4491"),
    "tep":         dict(world="budgeted", npz="worlds/budgeted/data/tep_anon.npz",      cfg="tasks_def.configs.budgeted_tep",      eval="4d68f219-12f4-4f79-b61c-ee118052f610"),
    "unsw":        dict(world="budgeted", npz="worlds/budgeted/data/unsw_anon.npz",     cfg="tasks_def.configs.budgeted_unsw",     eval="27615e12-de7e-4b29-8ef7-900fe5870d0e"),
    "thyroid":     dict(world="budgeted", npz="worlds/budgeted/data/thyroid_anon.npz",  cfg="tasks_def.configs.budgeted_thyroid",  eval="6fcbf032-d5ef-4b13-9040-1fbc44a7a1ca"),
    "thyroid-dropTSH": dict(world="budgeted", npz="worlds/budgeted/data/thyroid_anon.npz", cfg="tasks_def.configs.budgeted_thyroid", eval="32c9a8ca-6045-4629-a27c-a01e13f656b7"),
    "hydraulic":   dict(world="budgeted", npz="worlds/budgeted/data/hydraulic_anon.npz", cfg="tasks_def.configs.budgeted_hydraulic", eval="f7318a3b-91ea-4456-a086-4d43bd449468"),
    "diabetes":    dict(world="budgeted", npz="worlds/budgeted/data/diabetes_anon.npz", cfg="tasks_def.configs.budgeted_diabetes", eval="9f3883e9-5b3a-4e42-94a7-f170450101dd"),
    "derma":       dict(world="budgeted", npz="worlds/budgeted/data/derma_anon.npz",    cfg="tasks_def.configs.budgeted_derma",    eval="0dd9f969-ebd5-44ef-b891-aeeccfcd6502"),
    "label-budget-covtype": dict(world="label_budget", npz="worlds/label_budget/data/covtype_anon.npz", cfg="tasks_def.configs.label_budget_covtype", eval="03bdb135-2c06-4dd3-bd13-b3c813daee88"),
    "label-budget-covtype-open": dict(world="label_budget", npz="worlds/label_budget/data/covtype_anon.npz", cfg="tasks_def.configs.label_budget_covtype_open", eval="303517c9-82fd-4641-84a2-cb4f88e41606"),
}


def _world_paths(world):
    """(records_dir, table_path) for a world, each world owning its own readmes/ (mirrors imputation)."""
    base = REPO / "worlds" / world / "readmes"
    return base / "tasks", base / "README_submission.md"

_T = "https://horizon.bespokelabs.ai/tasks/"
_E = "https://horizon.bespokelabs.ai/evaluations/"

# WORLD-OWNED presentation + human judgment per dataset (the SDK only formats these; it never
# synthesizes a verdict line or a submit flag). task = bare record/row key; narrative = extra ## sections
# the analyst writes (empty for simple rows). This is the seam's world half; the SDK band_report renders it.
REPORT_META = {
    "covtype": dict(task="budgeted-covtype", budget="6", metric="balanced-acc", task_url=_T+"4de1e511-7738-4889-bed3-a0a532b051e5",
        submit="**YES**", verdict_line="WIDE band, endpoints ~7 LSD apart; the test resolves it despite the rarest class holding 266 rows",
        evals=[("eval", _E+"babd012a-4ae2-4349-99cb-a030db3f4491")]),
    "tep": dict(task="budgeted-tep", budget="15", metric="balanced-acc", task_url=_T+"36abdac8-4edd-4304-a48c-53933cd34f62",
        submit="**YES**", verdict_line="WIDE band, endpoints ~8 LSD apart (synthetic + anonymized Tennessee Eastman Process; accepted for tasks)",
        evals=[("eval", _E+"4d68f219-12f4-4f79-b61c-ee118052f610")]),
    "unsw": dict(task="budgeted-unsw", budget="2", metric="balanced-acc", task_url=_T+"f8cc010b-53f1-4745-9481-146ff721bb50",
        submit="NO", verdict_line="NARROW band, endpoints < 1 LSD apart (inside noise)",
        evals=[("eval", _E+"27615e12-de7e-4b29-8ef7-900fe5870d0e")]),
    "thyroid": dict(task="budgeted-thyroid", budget="3", metric="balanced-acc", task_url=_T+"c69cfa04-5416-486c-b25a-0b345eea4d98",
        submit="NO", verdict_line="below the 3-tier bar (73-row rarest class inflates sigma); drop-TSH salvage tighter, it failed",
        evals=[("orig", _E+"6fcbf032-d5ef-4b13-9040-1fbc44a7a1ca"), ("drop-TSH", _E+"32c9a8ca-6045-4629-a27c-a01e13f656b7")]),
    "hydraulic": dict(task="budgeted-hydraulic", budget="3", metric="balanced-acc", task_url=_T+"2935f9b4-ea7f-4127-8b73-b91a7d4d6f24",
        submit="NO", verdict_line="CEILING: gap test says endpoints indistinct; one cheap sensor solves it so the budget never binds",
        evals=[("eval", _E+"f7318a3b-91ea-4456-a086-4d43bd449468")]),
    "diabetes": dict(task="budgeted-diabetes", budget="3", metric="balanced-acc", task_url=_T+"bb7097fc-2984-4b74-8088-e200de4373f3",
        submit="NO", verdict_line="NARROW band; readmission learnable from the cheap groups, expensive labs inert, converge ~0.62",
        evals=[("eval", _E+"9f3883e9-5b3a-4e42-94a7-f170450101dd")]),
    "derma": dict(task="budgeted-derma", budget="6", metric="balanced-acc", task_url=_T+"1a019b65-bfed-4779-8e00-e3982d3c7a51",
        submit="NO", verdict_line="real spread, but the rarest test class = 4 rows buries it; unresolvable at any run count",
        evals=[("eval", _E+"0dd9f969-ebd5-44ef-b891-aeeccfcd6502")]),
    "label-budget-covtype": dict(task="label-budget-covtype", budget="L=2000", metric="balanced-acc", task_url=_T+"33da8224-530b-4641-a61a-7f1a1655b823",
        submit="NO (strategy)", verdict_line="band VIABLE (wide), but ELIMINATED on strategy homogeneity (all 5 students wrote one recipe), not on the band",
        evals=[("eval", _E+"03bdb135-2c06-4dd3-bd13-b3c813daee88")]),
    "label-budget-covtype-open": dict(task="label-budget-covtype-open", budget="L=1500", metric="balanced-acc", task_url=_T+"e9ee3601-21ce-4162-b868-ab424d7932cd",
        submit="**YES** (skill gradient)", verdict_line="the open-ended + rare-class-starved salvage of label-budget-covtype: a WIDE band AND a real, code-legible skill gradient (rare-class recall c1/c6, p_le0=0)",
        evals=[("eval", _E+"303517c9-82fd-4641-84a2-cb4f88e41606")]),
}


def to_band_report(ds, r):
    """Map an analyze() result dict `r` + the world's REPORT_META into the SDK BandReport schema. Pure
    mapping, no math. verdict_line / submit / narrative are world-authored (REPORT_META); the SDK only
    formats the numbers `r` already computed."""
    from sdk.hor_utils.band_report import BandReport
    m = REPORT_META.get(ds, {"task": ds, "budget": "", "metric": "balanced-acc",
                             "submit": "SUBMIT" if r.get("verdict") == "SUBMIT" else "REJECT",
                             "verdict_line": str(r.get("verdict", "")), "evals": [("eval", _E + r["eval"])],
                             "task_url": ""})
    d = dict(r)
    d.update(dict(
        task=m["task"], budget_label=m.get("budget", ""), metric=m.get("metric", "balanced-acc"),
        band_supports=None if r.get("ceiling") else r.get("band_supports"),
        n_runs=r.get("n_runs_with_preds", 0), n_nondegenerate=r.get("n_nondegenerate", 0),
        sigma_source="stratified block-bootstrap on the median run",
        verdict_line=m["verdict_line"], submit=m["submit"], narrative=m.get("narrative", {}),
        links=dict(task_url=m.get("task_url", ""),
                   evals=[{"label": lbl, "url": url} for lbl, url in m.get("evals", [])],
                   record=f"tasks/{m['task']}.md",
                   source_json=f"scratch/analysis/{r['eval'][:8]}/band_supports.json"),
    ))
    return BandReport.from_dict(d)


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
        sub = fb.get("submission") if isinstance(fb, dict) else None   # the verbatim solution.py
        if not isinstance(fb, dict) or "predictions_b64" not in fb:
            runs.append((rn, None, float(d.get("score") or 0.0), sub))  # failed / no policy
            continue
        p = np.frombuffer(base64.b64decode(fb["predictions_b64"]), dtype=np.int32)
        runs.append((rn, p, float(fb.get("score", np.nan)), sub))
    return sorted(runs, key=lambda r: (r[0] is None, r[0]))


def _recall_by_class(y_true, yp, classes):
    """Per-class recall (fraction of each true class predicted correctly) for one run."""
    return {int(c): round(float((yp[y_true == c] == c).mean()), 3) if (y_true == c).any() else 0.0
            for c in classes}


def analyze(ds):
    spec = DATASETS[ds]
    cfg = _cfg(spec["cfg"])
    yvars = _y_true_variants(spec["npz"], cfg)
    raw = _decode_runs(spec["eval"])
    if not raw:
        return {"dataset": ds, "eval": spec["eval"], "error": "no rollouts on disk (pull first)"}

    # align each run to the matching y_true length; keep runs with predictions
    y_true = None
    preds, scores, metas, failed = [], [], [], 0
    for rn, p, sc, sub in raw:
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
        metas.append((rn, sub))

    # non-degenerate band (drop collapsed/floor runs; they are a bonus floor, not the operating floor)
    keep = [i for i, s in enumerate(scores) if s > FLOOR]
    nd_scores = [scores[i] for i in keep]
    nd_preds = [preds[i] for i in keep]
    nd_meta = [metas[i] for i in keep]
    order = np.argsort(nd_scores)
    nd_scores = [nd_scores[i] for i in order]
    nd_preds = [nd_preds[i] for i in order]
    nd_meta = [nd_meta[i] for i in order]

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

    # DRIVER: per-class recall for every non-degenerate run (sorted weak->strong), plus the
    # best-minus-worst delta per class. This localizes WHICH classes carry the band, the skill axis
    # the code comparison then has to explain. Submissions are dumped by main() for that comparison.
    per_class_recall = [
        {"run": nd_meta[i][0], "score": round(nd_scores[i], 4),
         "recall": _recall_by_class(y_true, nd_preds[i], classes)}
        for i in range(len(nd_preds))
    ]
    recall_delta = ({int(c): round(per_class_recall[-1]["recall"][int(c)]
                                   - per_class_recall[0]["recall"][int(c)], 3) for c in classes}
                    if len(nd_preds) > 1 else {})
    submissions = {nd_meta[i][0]: nd_meta[i][1] for i in range(len(nd_meta))}

    return {
        "_submissions": submissions,   # popped + dumped to solutions/ by main(); not persisted in json
        "per_class_recall": per_class_recall,
        "recall_delta_hi_minus_lo": recall_delta,
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
    args = argv[1:]

    def _g(flag):
        return args[args.index(flag) + 1] if flag in args else None

    # World enforcement entry: validate EVERY world's row<->record invariant via the SDK (one command).
    if "--validate" in args:
        from sdk.hor_utils.band_report import validate
        worlds = sorted({spec["world"] for spec in DATASETS.values()})
        probs = []
        for world in worlds:
            rdir, tpath = _world_paths(world)
            wp = validate(tpath, rdir)
            for pr in wp:
                print(f"[{world}] [{pr.kind}] {pr.task}: {pr.detail}")
            probs.extend(wp)
        print(f"{len(probs)} problem(s)." if probs else "invariant OK across all worlds (row <-> record bijection holds).")
        return 1 if any(pr.kind != "polarity_advisory" for pr in probs) else 0

    emit = "--emit" in args   # opt-in: after computing, render the record + upsert the world's table row
    # Explicit --records-dir/--table override the per-world default (used by adhoc/testing only).
    records_override = _g("--records-dir")
    table_override = _g("--table")

    # Generic ANY-eval mode (a row not in DATASETS): --eval <id> --cfg <module> --npz <path> [--name X] [--world W].
    if "--eval" in args:
        name = _g("--name") or "adhoc"
        DATASETS[name] = dict(world=_g("--world") or "budgeted", npz=_g("--npz"), cfg=_g("--cfg"), eval=_g("--eval"))
        keys = [name]
    else:
        keys = [a for a in args if not a.startswith("--")] or list(DATASETS)
    rows = []
    for ds in keys:
        r = analyze(ds)
        rows.append(r)
        if "error" in r:
            print(f"{ds:22s} ERROR: {r['error']}")
            continue
        out = REPO / "scratch" / "analysis" / r["eval"][:8]
        out.mkdir(parents=True, exist_ok=True)
        # dump the verbatim solutions (the CODE half of the analysis) for side-by-side reading
        subs = r.pop("_submissions", {})
        soldir = out / "solutions"; soldir.mkdir(exist_ok=True)
        for rn, code in subs.items():
            if code:
                (soldir / f"run{rn}.py").write_text(code)
        (out / "band_supports.json").write_text(json.dumps(r, indent=2))
        if emit:
            from sdk.hor_utils.band_report import write as write_band_report
            w_records, w_table = _world_paths(DATASETS[ds]["world"])
            records_dir = Path(records_override) if records_override else w_records
            table_path = Path(table_override) if table_override else w_table
            records_dir.mkdir(parents=True, exist_ok=True)
            report = to_band_report(ds, r)
            write_band_report(report, records_dir, table_path)
            print(f"   EMITTED record + upserted row -> {records_dir}/{report.task}.md")
        bs = "ceiling" if r["ceiling"] else f"{r['band_supports']:.2f}"
        print(f"{ds:22s} band {r['band'][0]:.3f}-{r['band'][1]:.3f} w={r['width']:.3f} "
              f"sig={r['sigma_abs']:.4f} LSD={r['lsd']:.4f} rare={r['rarest_count']:>5d} "
              f"#obs={r['n_observed']} #supports={bs:>7s}  {r['verdict']}")
        # DRIVER table: per-class recall weak->strong + the hi-minus-lo delta (which classes carry the band)
        cls = sorted(next(iter(r["per_class_recall"]), {}).get("recall", {}))
        if cls:
            print("   recall/class weak->strong  (" + " ".join(f"c{c}" for c in cls) + ")")
            for pr in r["per_class_recall"]:
                print(f"     run{pr['run']} {pr['score']:.3f} | " + " ".join(f"{pr['recall'][c]:.2f}" for c in cls))
            print("   delta(hi-lo)/class: " + " ".join(f"c{c}:{r['recall_delta_hi_minus_lo'].get(c,0):+.2f}" for c in cls))
            print(f"   solutions dumped -> {soldir}")
    return rows


if __name__ == "__main__":
    main(sys.argv)
