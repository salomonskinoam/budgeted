# Budgeted feature acquisition world, proposal

A world of tasks where the student builds a policy that, under a cost budget, decides which
features to buy per instance and then predicts, meant to run later in a production setting with the
same constraints.

This is a directional doc, the why and the constraints, to bootstrap a new world repo. Specific
datasets, exact metrics, and final wording are decided later, inside the world.

## Why this world
Choosing which costly features to buy under a budget has several genuinely different strategy
families and no single winner; the best approach depends on the cost layout, the budget, and the
data's structure, so scores spread. Real skill (a planner that beats a simple greedy buyer) exists
only when the data has CONDITIONAL structure: a cheap feature that gates which expensive one is
worth buying, or interactions a one-step-ahead greedy buyer cannot see. If a greedy buyer is
near-optimal, the band collapses, so engineering tasks where that conditional structure is present
(on real data) is the core design problem.

## The prompt (parameterized)
> You are given a dataset {{dataset}} and i need you to create {{artifact}} that optimized
> {{objective, metric}}, but there is a catch: features are not free. Acquiring feature f costs
> {{cost(f)/unknown cost/cost(f, t)}}, and you have a budget of {{total budget/per sample/per X}}.
> This {{artifact}} will later run in a production environment that adheres to these same
> constraints. It should be able to decide which features to buy (within budget), then predict
> {{target}} in order to optimize{{metric}} there. A validation slice is provided so you can score
> yourself and iterate. {{Notice that the ordering is arbitrary}}.
> Deliverable: {{artifact}}

What gets parameterized: the base dataset, the cost model (known per-feature cost, unknown cost, or
time-dependent cost(f, t)), the budget model (total, per-sample, per-X), the target/metric, and the
mode (agent-time vs deferred/grader-time).

## The task must be instrumental
Graded on the prediction quality achieved under the budget. A task must FAIL with a bad acquisition
policy and SUCCEED with a good one. A solution that does not beat a naive buyer (random /
cheapest-first) at the same budget scores zero.

## Data
REAL data only, never synthetic. The cost structure (per-feature costs + budget) is engineered on
top of real data. The conditional/gating structure that makes planning beat greedy must come from
real feature dependencies plus the cost design; choosing real domains where this is native (for
example medical panels, sensor cascades) is part of the build. Which datasets: chosen later, inside
the world.

## Modes and the graded artifact
Default is agent-time; a deferred / grader-time mode is added later; the graded artifact is the same
across modes so the switch is seamless.

## The band is the goal
The main design work is shaping the cost structure (and choosing data) so strong and weak policies
land at clearly different scores. If a simple greedy buyer is near-optimal the band collapses; the
build must make the buying decisions genuinely conditional so planning skill separates. Measure the
spread first.

## Reward hacking
The grader hard-enforces the budget (no buying everything); guard leakage / forbidden-dir reads;
avoid degenerate instances (one near-perfect feature, or budget >> need) by designing costs so the
budget binds.

## Constraints
CPU-only for now.

## Building it
Build this as an SDK world (a `worlds/<world>/` subclass plus task instances). See
`CREATING_A_WORLD.md` in the SDK.
