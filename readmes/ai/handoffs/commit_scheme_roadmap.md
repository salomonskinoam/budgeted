# Handoff: the commit-scheme program (what we do now)

This is the "what to work on and why" hub. The current work is **commit-mode tasks**, do not build plain
global budget.

## Why we are here (the global-budget dead end)

- **§21** proposed a global/incremental feature budget (ration a shared pool across cases) to escape the
  per-row memoryless dominance.
- **§22 REFUTED it**: a plain shared pool over an iid stream self-averages into a per-row shadow-price rule
  calibratable from peek data, so it COLLAPSES (all competent agents converge again). Plain global budget
  is not a new scheme. **Do not build it.**
- The pivot (§22): **commit-mode tasks**, STATE the policy interacts with whose take-backs are costly.
  "Global budget" only survives WRAPPED in a commit mechanism (a global LABEL budget = the label-budget
  scheme; a shared pool funding paid revision).

The full per-scheme analyses live in **`../../commit_schemes/`** (files 00-07, self-contained, tagged
[PROVEN]/[ARGUMENT]/[CONJECTURE]); **`../../commit_schemes/08_ordering_and_roadmap.md`** orders them and is the
authoritative roadmap (its Background section is a standalone bootstrap brief). Read 08 before starting any
scheme; do not re-derive the ordering.

## The ordering (roadmap 08) and status

**First picks:** items 1, 2, 3 go first (1 and 2 concurrent, 3 next); item 6 is contingent on 2.

| # (08) | scheme | design file | status |
|---|---|---|---|
| 1 | Transcript-replay pre-test (grade the session, not just the artifact) | `commit_schemes/01_agent_time_commits.md` | first pick, **not run** -> [`scheme_1_transcript_replay.md`](scheme_1_transcript_replay.md) |
| 2 | Label budget (active learning; buy training labels) | `commit_schemes/03_train_label_budget.md` | first pick, **BUILT; hint-on version eliminated on strategy; OPEN salvage SHIPS (7.82, skill gradient)** -> [`scheme_2_label_budget.md`](scheme_2_label_budget.md) |
| 3 | Small-chunk information release (noisy incremental reads) | `commit_schemes/02_small_chunk_information_release.md` | **DROPPED (2026-07-07)**: strong (luck-smoothing) argument is global-pool-only, marginal over covtype, brutal multi-dim tuning with possibly-empty window -> [`scheme_3_small_chunk.md`](scheme_3_small_chunk.md) |
| 6 | Paid revision (revise a past commit from the pool) | `commit_schemes/06_paid_revision.md` | contingent on item 2 passing its dominance gate |
| 4 | Instrument installation (one-time unlock a feature group) | `commit_schemes/04_instrument_installation.md` | fix-first (proven inert as specified; needs a repair) |
| 5 | Compounding state on TEP (actions change the later environment) | `commit_schemes/05_compounding_state.md` | heaviest, scaffold-only, last |

The falsifier battery every scheme runs through pre-build: `commit_schemes/07_commit_gate_falsifiers.md`.

## What to do next

- **Label budget (item 2) is DONE for this pass:** `label-budget-covtype-open` SHIPS as a real skill
  gradient (7.82). The only open extension is true strategy DIVERSITY (vs the current skill gradient),
  which needs the deferred label-cost second axis, optional. See `scheme_2_label_budget.md`.
- ~~Start small-chunk (item 3)~~ **DROPPED 2026-07-07** (see `scheme_3_small_chunk.md`): its one strong
  argument (luck-smoothing) is global-pool-only, upside over covtype is marginal, tuning is brutal.
- **Transcript-replay (item 1)** (`scheme_1_transcript_replay.md`), the cheap independent pre-test,
  still not run, next candidate.

Judge every result with `band_method.md` (#band_supports), and pair it with a strategy-diversity check,
the label-budget lesson: a resolvable band can still be one converged recipe.
