# Handoffs index

Continuation briefs for the `budgeted` world, one concern per file. Start here, then open the one you
need.

**Bibles (durable reference, up in `readmes/`):**
- Design bible: [`../../README_general_direction.md`](../../README_general_direction.md)
- World architecture: [`../../world_architecture.md`](../../world_architecture.md) (the shared `sdk/mediated` framework, how to add a task, conventions)
- Band method: [`../../band_method.md`](../../band_method.md) (#band_supports, `band_resolution.py`, the submission set + verdict rule)

**One-line state.** Submission set decided on #band_supports: **budgeted-covtype (8.06), budgeted-tep
(9.14), and label-budget-covtype-open (7.82) SHIP**; five datasets buried; the current program is
**commit-mode tasks** (`../../commit_schemes/`, on branch `roadmap/commit-schemes`). The first commit
scheme, **label-budget (item 2), was built,** its hint-on version eliminated on strategy, and its OPEN
salvage now ships as a real skill gradient. Plain global budget is DEAD (§22, it collapses).

| handoff | read when |
|---|---|
| [`commit_scheme_roadmap.md`](commit_scheme_roadmap.md) | deciding WHAT to work on (why plain global budget died, the commit-mode program, roadmap 08, first picks + per-scheme status) |
| [`scheme_1_transcript_replay.md`](scheme_1_transcript_replay.md) | item 1 (grade the session, not just the artifact); orthogonal to budget mode |
| [`scheme_2_label_budget.md`](scheme_2_label_budget.md) | item 2 (active learning; BUILT, ships as skill-gradient salvage) |
| [`scheme_3_small_chunk.md`](scheme_3_small_chunk.md) | item 3 (noisy incremental reads) **DROPPED 2026-07-07**, see file for why |
| [`global_budget_next.md`](global_budget_next.md) | HISTORICAL only, the §21 global-budget idea before §22 refuted it |

**Where the program stands:** item 2 SHIPS; item 3 DROPPED. Live direction is a **new world** for
concept-drift online active learning (§23 in the design bible), composing scheme 7 (streaming
delayed-label learning) with scheme 6 (paid revision). Items 4 (instrument) and 5 (TEP compounding)
remain later. See `commit_scheme_roadmap.md`.
