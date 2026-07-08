# Handoff: scheme 1, transcript-replay pre-test (first pick)

**Roadmap 08 item 1. Status: NOT RUN.** The cheapest first pick, no new world mechanic. Design:
`../../commit_schemes/01_agent_time_commits.md` (step 6 has the full procedure).

## The idea

Grade the student's WORKING SESSION, not just its final artifact. Does grading the climb (fixing state
early, or snapshotting the deliverable at wall-clock marks and aggregating) resolve skill-ordered levels
that final-only grading ties? Undecided by argument (both collapse arguments failed); a pre-test decides.

## What to build (no new mechanic, reuses the existing graders)

1. A transcript parser + edit-replayer that reconstructs the FULL workdir (not just `solution.py`, per the
   laundering result) at 25 / 50 / 75 / 100 percent of each run's session length.
2. Source transcripts: the covtype eval `babd012a-4ae2-4349-99cb-a030db3f4491` (5 runs, `budgeted-covtype`)
   and the TEP scaffold eval (5 runs, `budgeted-tep`).
3. Score each runnable snapshot through the EXISTING mediated grader as a throwaway HOSTED validation
   (~40 gradings = 5 runs x 4 marks x 2 datasets). Record non-runnable snapshots (mid-edit) as data.
4. Read out: final-tie resolution, early-vs-final rank correlation, commit-once incidence.

## Kill / keep

Killed if checkpoint scores are near-identical across runs at every mark, or the aggregate adds no
resolution over the finals, or the early-vs-final correlation is near zero (added levels are un-averaged
session luck). Even a KEEP has a low actionability ceiling (it is an ADDITION to a stream-facing scheme,
not a competitor) and needs a defensible mid-session scorer.

## Open item before building

Confirm the TEP eval id (roadmap 08 open question 6): the covtype transcripts are pinned to `babd012a`,
but the TEP scaffold eval id is ambiguous across the docs. Run `horizon evaluations list` on task
`36abdac8-4edd-4304-a48c-53933cd34f62` first. Judge results with `band_method.md`.
