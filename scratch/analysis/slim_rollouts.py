"""Slim every pulled rollout in .rollouts/ down to just the fields the band analysis reads, dropping
the multi-MB agent transcript. Keeps the durable record (score, submitted code, per-row predictions)
that readmes/tasks/<task>.md files point to, in the exact nested shape band_resolution.py::_decode_runs
parses. Idempotent: re-running on already-slim files is a no-op. Run: python scratch/analysis/slim_rollouts.py
"""
from __future__ import annotations
import glob
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _loads(x):
    if isinstance(x, str):
        try:
            return json.loads(x)
        except json.JSONDecodeError:
            return {}          # a plain-text feedback (failed run) has no parseable fields
    return x


def main() -> None:
    kept_fields = ("score", "submission", "predictions_b64")
    files = sorted(glob.glob(str(REPO / ".rollouts" / "**" / "*.json"), recursive=True))
    before = sum(Path(f).stat().st_size for f in files)
    for f in files:
        d = json.load(open(f))
        gr = _loads(d.get("grade_result")) or {}
        meta = _loads(gr.get("metadata")) if isinstance(gr, dict) else {}
        fb = _loads(meta.get("feedback")) if isinstance(meta, dict) else {}
        slim_fb = {k: fb[k] for k in kept_fields if isinstance(fb, dict) and k in fb}
        slim = {
            "evaluation_id": d.get("evaluation_id"),
            "run_number": d.get("run_number"),
            "score": d.get("score"),
            "grade_result": {"metadata": {"feedback": slim_fb}},
        }
        json.dump(slim, open(f, "w"))
    after = sum(Path(f).stat().st_size for f in files)
    print(f"slimmed {len(files)} rollouts: {before/1e6:.1f} MB -> {after/1e6:.2f} MB")


if __name__ == "__main__":
    main()
