# Commit-scheme analyses

One file per design question about commit-mode tasks (state the policy interacts with that is hard
to change, take-backs allowed but costly). Each file is self-contained and may seed its own work
chain. The task owner reads each file independently.

## Why this folder exists

Plain global budget collapses (see `../README_general_direction.md` §22). Commit-mode schemes are
the candidate replacements. A first analysis round was rejected for two failures: verdicts were
asserted without visible reasoning, and collapse arguments assumed every agent is strong. These
files are the redo.

## The correction every file obeys

The band (the product) is the spread across REAL student rollouts of VARYING strength. Nobody says
all agents are strong. "The optimal play is computable from peek data" is therefore never, by
itself, a kill: covtype banded (0.675 to 0.848, about 3 levels) even though a near-optimal per-row
policy was computable offline. What this world's history supports: when probe policies of different
sophistication separate by more than noise, real students band (§16, §19); when one dominant move
is easy for most agents to find, scores pack. Every reasoning step is tagged [PROVEN] (mathematical
reduction or working exploit), [ARGUMENT] (heuristic backed by this world's evidence), or
[CONJECTURE] (needs a pre-test). The operative question for every scheme: how many graded rungs
does its skill ladder have between naive and optimal, and do real agents of varying strength land
on distinguishable rungs.

## Hard constraints (task owner)

- Peek data (train and validation, features and labels) is always fully available at agent time;
  it seeds a smart decider. The only permitted ignorance is of the gradually revealed test stream
  (which cases arrive, in what order). Lucky blind first commitments = dead scheme.
- Evaluation reruns the shipped policy under 5 fixed stream seeds; score = mean over seeds; levels
  are counted by a seed-blocked analysis of variance. Skill gaps must survive that averaging.
- Production framing to the student, never grading language.
- No unexplained abbreviations in these files. No em-dash character anywhere in them.

## File conventions

Sections, in order: The question / Background (every term defined) / Reasoning (numbered steps,
each tagged [PROVEN] / [ARGUMENT] / [CONJECTURE]) / Verdict (and what evidence would flip it) /
Alternatives (when data or the metric is the pitfall) / Open questions (worth a dedicated chat).

## Index

- `00_band_theory_what_collapse_arguments_prove.md` (the reference frame the others use)
- `01_agent_time_commits.md`
- `02_small_chunk_information_release.md`
- `03_train_label_budget.md`
- `04_instrument_installation.md`
- `05_compounding_state.md`
- `06_paid_revision.md`
- `07_commit_gate_falsifiers.md`
- `08_ordering_and_roadmap.md` (the suggested ordering of the surviving work items, with reasoning)
