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
from sdk.mediated import config_world
from sdk.hor_utils.noise import (
    contiguous_label_blocks, block_bootstrap_sigma, rank_resolution, paired_gap_sigma,
)
from sdk.hor_utils.resolution import resolution
from sdk.hor_utils.band_report import EvalStats, TaskBandReport, write as write_band_report, validate
from tasks_def.band_manifest import MANIFEST

REPO = Path(__file__).resolve().parents[2]
Z = 2.0
CEILING = 0.97          # best score above this -> Method B invalid, use the gap test
FLOOR = 0.15            # scores at/below this are degenerate (no working policy) -> excluded from the band


def bacc(yt, yp):
    return balanced_accuracy_score(yt, yp)


_T = "https://horizon.bespokelabs.ai/tasks/"
_E = "https://horizon.bespokelabs.ai/evaluations/"

STRATEGY_STUB = ("# {task}: strategy analysis\n\n**[PENDING]** the 5-run solution comparison (skill "
                 "gradient vs strategy diversity, the label-budget lesson) has not been written yet. "
                 "This file is HUMAN-owned and updated INDEPENDENTLY of the generated table/record "
                 "(the analysis seam, sdk/methodology/noise_floor.md). Editing it never re-touches the "
                 "SDK-owned record or master table.\n")


def _world_paths(world):
    """(records_dir, table_path) for a world, each world owning its own readmes/ (mirrors imputation)."""
    base = REPO / "worlds" / world / "readmes"
    return base / "tasks", base / "README_submission.md"


def _analysis_dir(world, task):
    """worlds/<world>/analysis/<task>/ — the task-keyed source-of-truth dir (band_supports.json + STRATEGY.md)."""
    return REPO / "worlds" / world / "analysis" / task


def _best_observed(cfg_mod):
    """Per-task best_observed sourced from the config, falling back to the SDK mediated world default."""
    cfg = importlib.import_module(cfg_mod).CONFIG
    return float(cfg.get("best_observed", config_world.CONFIG["best_observed"]))


def _task_links(task, spec):
    """Link block for a task. analysis/source_json are relative to the world's README_submission.md
    (the table), per the analysis seam; record is relative to the same; eval urls from the manifest."""
    return dict(
        task_url=(_T + spec["task_id"]) if spec.get("task_id") else "",
        evals=[{"label": ev.get("label", ""), "url": _E + ev["eval_id"]} for ev in spec["evals"]],
        record=f"tasks/{task}.md",
        analysis=f"../analysis/{task}/STRATEGY.md",
        source_json=f"../analysis/{task}/band_supports.json",
    )


def _task_report(task, spec, evals):
    """Assemble the task-keyed TaskBandReport from its EvalStats list + manifest metadata."""
    return TaskBandReport(
        task=task, world=spec["world"], metric="balanced-acc", budget_label=spec.get("budget_label", ""),
        best_observed=_best_observed(spec["cfg"]), verdict_line=spec.get("verdict_line", ""),
        submit=spec.get("submit", ""), primary_eval=spec["evals"][0]["eval_id"], evals=evals,
        links=_task_links(task, spec), narrative=spec.get("narrative", {}),
    )


def _mk_eval(d, ev):
    """Build an EvalStats from a per-eval stats dict `d` (analyze result OR a stored json), stamping the
    manifest's eval_id/label and deriving the band-note from the failed-run count."""
    es = EvalStats.from_dict(d)
    es.eval_id, es.label = ev["eval_id"], ev.get("label", "")
    if es.n_failed and not es.band_note:
        es.band_note = f"(+{es.n_failed} fail)"
    return es


def assemble_task(task, spec):
    """Analyze each of the task's evals, wrap each as EvalStats, assemble the TaskBandReport. Returns
    (TaskBandReport | None, per-eval result dicts); report is None if any eval errored."""
    results = [analyze_eval(spec["cfg"], spec["npz"], ev["eval_id"], ev.get("label", "")) for ev in spec["evals"]]
    if any("error" in r for r in results):
        return None, results
    evals = [_mk_eval(r, ev) for ev, r in zip(spec["evals"], results)]
    return _task_report(task, spec, evals), results


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


def analyze_eval(cfg_mod, npz, eval_id, label=""):
    """Per-eval band stats from the stored predictions of one eval (no policy replay). Returns a dict of
    EvalStats-compatible keys (+ `_submissions`/`op`/`verdict` diagnostics the SDK schema drops)."""
    cfg = _cfg(cfg_mod)
    yvars = _y_true_variants(npz, cfg)
    raw = _decode_runs(eval_id)
    if not raw:
        return {"eval_id": eval_id, "label": label, "error": "no rollouts on disk (pull first)"}

    # align each run to the matching y_true length; keep runs with predictions
    y_true = None
    preds, scores, metas, failed = [], [], [], 0
    for rn, p, sc, sub in raw:
        if p is None:
            failed += 1
            continue
        if len(p) not in yvars:
            return {"eval_id": eval_id, "label": label, "error": f"run {rn} preds len {len(p)} matches no y_true {list(yvars)}"}
        yt = yvars[len(p)]
        y_true = yt if y_true is None else y_true
        assert len(p) == len(y_true), f"mixed test sizes within eval {eval_id}"
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
        "_submissions": submissions,   # popped + dumped to solutions/ by callers; not in EvalStats
        "op": float(bb["op"]), "verdict": verdict,     # console diagnostics; dropped by EvalStats.from_dict
        "eval_id": eval_id, "label": label,
        "per_class_recall": per_class_recall, "recall_delta": recall_delta,
        "n_runs": len(preds), "n_failed": failed, "n_nondegenerate": len(nd_scores),
        "band": [lo, hi], "spread": width, "mid": mid,
        "scores_sorted": [round(s, 4) for s in nd_scores],
        "n_test": int(len(y_true)), "n_classes": int(len(classes)),
        "rarest_class": int(classes[rarest_i]), "rarest_count": int(counts[rarest_i]),
        "per_class_counts": {int(c): int(n) for c, n in zip(classes, counts)},
        "sigma_abs": sigma_abs, "lsd": lsd, "band_supports": band_supports, "observed": n_observed,
        "ceiling": bool(ceiling), "sigma_source": "stratified block-bootstrap on the median run",
        "gap": {k: (round(v, 4) if isinstance(v, float) else v)
                for k, v in gap.items() if k in ("gap", "sigma_gap", "ratio", "p_le0")},
    }


def _dump_solutions(adir, eval_id, subs, multi):
    """Dump each run's verbatim solution.py for the CODE half of the analysis. Multi-eval tasks nest
    per-eval under solutions/<eval8>/ so evals don't clobber each other."""
    soldir = (adir / "solutions" / eval_id[:8]) if multi else (adir / "solutions")
    soldir.mkdir(parents=True, exist_ok=True)
    for rn, code in subs.items():
        if code:
            (soldir / f"run{rn}.py").write_text(code)


def _write_task(tbr, spec, emit, records_override=None, table_override=None):
    """Write the task-keyed truth (band_supports.json) + a STRATEGY.md stub (never overwritten), and,
    on emit, render the record + upsert the world's master-table row via the SDK."""
    adir = _analysis_dir(spec["world"], tbr.task)
    adir.mkdir(parents=True, exist_ok=True)
    (adir / "band_supports.json").write_text(json.dumps(tbr.to_dict(), indent=2))
    strat = adir / "STRATEGY.md"
    if not strat.exists():
        strat.write_text(STRATEGY_STUB.format(task=tbr.task))
    if emit:
        records_dir = Path(records_override) if records_override else _world_paths(spec["world"])[0]
        table_path = Path(table_override) if table_override else _world_paths(spec["world"])[1]
        records_dir.mkdir(parents=True, exist_ok=True)
        write_band_report(tbr, records_dir, table_path)


def migrate():
    """FREE regroup: build the task-keyed truth from the EXISTING per-eval scratch jsons (no re-analysis),
    then render records + upsert rows. `per_class_recall` survives only where the source json carried it
    (it backfills on the next --emit, which recomputes)."""
    for task, spec in MANIFEST.items():
        evals = [_mk_eval(json.load(open(REPO / "scratch" / "analysis" / ev["eval_id"][:8] / "band_supports.json")), ev)
                 for ev in spec["evals"]]
        tbr = _task_report(task, spec, evals)
        _write_task(tbr, spec, emit=True)
        print(f"migrated {task:28s} ({len(evals)} eval{'s' if len(evals) != 1 else ''}) "
              f"-> worlds/{spec['world']}/analysis/{task}/")
    print("done; run --validate")


def _print_eval(tag, es, verdict):
    bs = "ceiling" if es.ceiling else f"{es.band_supports:.2f}"
    print(f"{tag:26s} band {es.band[0]:.3f}-{es.band[1]:.3f} w={es.spread:.3f} "
          f"sig={es.sigma_abs:.4f} LSD={es.lsd:.4f} rare={es.rarest_count:>5d} "
          f"#obs={es.observed} #supports={bs:>7s}  {verdict}")
    cls = sorted(next(iter(es.per_class_recall), {}).get("recall", {}))
    if cls:
        print("   recall/class weak->strong  (" + " ".join(f"c{c}" for c in cls) + ")")
        for pr in es.per_class_recall:
            print(f"     run{pr['run']} {pr['score']:.3f} | " + " ".join(f"{pr['recall'][c]:.2f}" for c in cls))
        print("   delta(hi-lo)/class: " + " ".join(f"c{c}:{es.recall_delta.get(c, 0):+.2f}" for c in cls))


def main(argv):
    args = argv[1:]

    def _g(flag):
        return args[args.index(flag) + 1] if flag in args else None

    # World enforcement entry: validate EVERY world's row<->record invariant via the SDK (one command).
    if "--validate" in args:
        worlds = sorted({spec["world"] for spec in MANIFEST.values()})
        probs = []
        for world in worlds:
            rdir, tpath = _world_paths(world)
            wp = validate(tpath, rdir)
            for pr in wp:
                print(f"[{world}] [{pr.kind}] {pr.task}: {pr.detail}")
            probs.extend(wp)
        print(f"{len(probs)} problem(s)." if probs else "invariant OK across all worlds (row <-> record bijection holds).")
        return 1 if any(pr.kind != "polarity_advisory" for pr in probs) else 0

    # FREE migration: regroup existing per-eval scratch jsons into the task-keyed truth (no re-analysis).
    if "--migrate" in args:
        migrate()
        return 0

    emit = "--emit" in args   # opt-in: after computing, render the record + upsert the world's table row
    records_override = _g("--records-dir")     # override the per-world default (adhoc/testing only)
    table_override = _g("--table")

    manifest = dict(MANIFEST)
    if "--eval" in args:      # adhoc ANY-eval: --eval <id> --cfg <mod> --npz <path> [--name X] [--world W]
        name = _g("--name") or "adhoc"
        manifest[name] = dict(world=_g("--world") or "budgeted", cfg=_g("--cfg"), npz=_g("--npz"),
                              budget_label="", task_id="", submit="", verdict_line="", narrative={},
                              evals=[dict(eval_id=_g("--eval"), label="")])
        keys = [name]
    else:
        keys = [a for a in args if not a.startswith("--")] or list(manifest)

    reports = []
    for task in keys:
        spec = manifest[task]
        tbr, results = assemble_task(task, spec)
        if tbr is None:
            print(f"{task:26s} ERROR: {next(r for r in results if 'error' in r)['error']}")
            continue
        adir = _analysis_dir(spec["world"], task)
        adir.mkdir(parents=True, exist_ok=True)
        multi = len(spec["evals"]) > 1
        for r in results:
            _dump_solutions(adir, r["eval_id"], r.pop("_submissions", {}), multi)
        _write_task(tbr, spec, emit, records_override, table_override)
        reports.append(tbr)
        for r, es in zip(results, tbr.evals):
            _print_eval(f"{task}/{r['label']}" if multi else task, es, r["verdict"])
        if emit:
            print(f"   EMITTED -> worlds/{spec['world']}/analysis/{task}/ + {spec['world']} readmes")
    return reports


if __name__ == "__main__":
    main(sys.argv)
