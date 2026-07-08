# Drift world, concept brief

**Status: NOT BUILT. This file is the brief for a dedicated build chat.** It captures the design
settled in the 2026-07-07 discussion. Full rationale: design bible `readmes/README_general_direction.md`
§23. Band judging: `readmes/band_method.md`. Build on the shared `sdk/mediated` framework (like
`worlds/label_budget` and the sibling `imputation` world), not the old `worlds/budgeted` shape.

## What the world is

Online active learning under REAL concept drift. Still the "budgeted" family (a commit is a kind of
budget), but different enough in mechanics to be its own world. The student ships a `Policy` whose skill
is adapting a model to a distribution that shifts during the graded stream, then optionally paying to
fix predictions it already committed. It composes two roadmap schemes:
- **Scheme 7 (streaming delayed-label learning):** the signal source.
- **Scheme 6 (paid revision):** the mechanism to act on that signal retroactively.

## Mechanic

- **Peek (agent time):** early batches of a real drift dataset, full features AND labels. The only
  permitted ignorance is the test stream (hard constraint, §12/§22). The student may build any
  adaptation machinery here (drift detector, online learner) in `__init__`.
- **Test stream (grade time):** later, DRIFTED batches, revealed one row at a time. The frozen
  peek-trained model is genuinely stale on them (that is the headroom).
- **Delayed labels (prequential):** after the policy predicts row t, the true label of an earlier row
  (delay k) is streamed back. This is the stream-revealed resource that resists front-loading: you
  cannot precompute an adaptation to a drift you have not seen. The delay makes label-echo impossible.
- **Paid revision (optional, scheme 6):** a shared-pool budget to overwrite a past committed prediction
  once the adapted model disagrees with the stale one. Load-bearing ONLY because 7 supplies a real
  reason the model improved.

## Why it should band

- Real headroom: frozen model decays under drift.
- Stream-revealed signal: delayed labels can't be front-loaded.
- A skill ladder with middle rungs: ship-frozen < detect-and-retrain < windowed / forgetting
  adaptation < adapt-and-revise.
- Strategy stays legible: the student ships the code that trains and updates the model, and that code
  IS the strategy (the weights are just its output), so the 5-solution code comparison still works.

## The make-or-break (run this pre-test BEFORE building the world)

Does an ALIVE REGIME exist on the real data? The drift must be PARTIALLY STRUCTURED: preparable from
peek (you can build a detector / online learner up front) but with a realization only knowable from
stream feedback.
- Fully peek-predictable drift front-loads (inert): a smart agent precomputes the adapted model.
- Fully random drift is unpreparable (no skill): nobody can beat the baseline.

Cheap hosted (gated) check on the candidate dataset: train on early batches, measure the frozen model's
decay across later batches, then measure recovery with online updates fed delayed labels. Also check the
rarest test class count per batch (band levels are capped by the rarest class). Kill if decay is
negligible (no headroom) or if recovery is trivial/impossible (no alive regime).

## Data (REAL only, no synthetic; synthetic drift makes low-quality tasks)

Ranked for this world (needs multi-class resolution + tabular features + genuine drift):
- **Gas Sensor Array Drift (UCI), lead.** ~13.9k samples, 128 features, 6 gas classes, 10 batches over
  36 months; drift is REAL sensor aging/poisoning. Peek = early batches, test = later batches.
- **INSECTS (Souza et al., USP).** Real insect-sensor data, temperature-driven drift, ships in
  abrupt / gradual / incremental / recurring variants, ~6 classes.
- **Rialto (10 classes).** Real building timelapse, lighting/weather drift over 20 days.
- Weaker (binary caps band levels): Electricity/Elec2, NOAA Weather.
- NOT covtype: its streaming "drift" is spatial row ordering (p(x) shifts, p(y|x) stable), not real
  concept drift.

## Build notes

- New world under `worlds/drift/` on `sdk/mediated` (config_world / active / objective / paths /
  prehook / prompt_builder / setup_data / world / verify / Dockerfile).
- This world's submission table + task records + `analysis/<task>/STRATEGY.md` live under
  `worlds/drift/readmes/` and `worlds/drift/analysis/` once tasks exist; wire the per-world band_report
  driver rather than hand-writing them.
- Judge every result with #band_supports AND a strategy-diversity check (the label-budget lesson: a
  resolvable band can still be one converged recipe).
- Gate every student eval and any heavy local compute through the user (CLAUDE.md).
