# Handoff: elevate the budgeted mediator into a generic SDK primitive

**For a NEW chat.** This chat built + validated the mediated trust model for ONE world (`budgeted-tep`)
and is staying scoped to it. The next step, generalizing the mediator into an SDK-controlled primitive
that many worlds reuse, is yours to drive. This doc is the brief.

## What exists today (the reference implementation, budgeted world)

A grade-time **pipe-mediated, privilege-separated subprocess**. The grader holds the secrets (test
features + labels) and doles out feature values to the student's code under a budget it enforces.

- `worlds/budgeted/verify.py::run_mediated` (the trusted parent): runs as root in the grader venv,
  holds `test_features` + `test_labels`, spawns the student policy as a child and drops it to the
  unprivileged `model` user (`preexec_fn=_demote_to_model`, setgid+setuid). Line-JSON over
  stdin/stdout: `{"cmd":"row","budget":B}` -> child `{"act":"buy","fid":j}` -> parent reveals
  `{"val":x}` or refuses `{"val":null}` -> child `{"act":"predict","label":k}`. **Budget is enforced
  in the parent** (refuses any buy over budget / duplicate); labels never enter the child.
- `worlds/budgeted/policy_runner.py` (the child): imports the student `Policy`, sees only
  `/data_agent` (train/val + meta) and the per-buy values the parent reveals. Baked to
  `/opt/budgeted/policy_runner.py` (root-owned 755) so the student can run but not tamper with it.
- Security rests on: `/data_root` 700 root (test + labels unreadable by `model`), runner+grader
  root-owned, budget enforced parent-side. See `Dockerfile` perms (lines ~46, 50-55, 66) and the
  reward-hack table in git history / this chat.
- `world.py::grade` rides per-run `predictions_b64` into feedback so per-run predictions are
  recoverable hosted (for `rank_resolution`).

## What the user wants generalized (verbatim intent)

1. **More worlds need this trust model**, so it should be an **SDK-controlled primitive**, not bespoke
   per-world code copied around.
2. **Subprocess vs HTTP server is OPEN.** "I am not sure if we always want a subprocess or an http
   server." The primitive should probably abstract the transport, not hard-pick one.
3. **Speed matters.** Pick transports/serialization that keep per-interaction latency low (the
   budgeted grader does one round-trip per feature per row; a slow transport blows up grade time).
4. **Agent-time access, not just grade-time.** "In some cases we will want the student to have access
   to the 'server' at agent time." The mediator must be able to serve the student DURING the rollout,
   not only during grading.
5. **Therefore it should generally run during the PREHOOK.** A prehook-launched mediator/server the
   student can hit at agent time (and that grading can also drive), rather than a process spawned only
   inside `verify.py`.

## Design questions to resolve in the new chat

- **Transport abstraction:** one interface, pluggable backends (pipe subprocess for grade-time-only;
  local HTTP/UDS socket for agent-time). What's the minimal protocol (open-session / query / spend /
  close) that both budget-acquisition and future worlds share?
- **Prehook-launched lifecycle:** how does a prehook start a long-lived mediator, expose an endpoint to
  the agent (UDS path? localhost port?), keep secrets (labels, budget ledger) on the trusted side, and
  hand the SAME mediator to the grader at grade time? How is it torn down?
- **Preserve the invariants** (non-negotiable): labels/test data never in the student's address space
  or on a student-readable path; the budget/cost ledger enforced by the trusted side; the mediator
  binary/script tamper-proof (root-owned); the student demoted (`model` user) with no path to
  `/data_root`.
- **Agent-time trust is harder than grade-time.** At grade time the student's code is a child we
  control; at agent time the AGENT drives and may probe the endpoint adversarially. Rate/budget
  accounting, session identity, and "no oracle leakage through the endpoint" need explicit thought.
- **Speed:** UDS vs TCP vs pipe; JSON vs msgpack; batching multiple buys per round-trip.
- **Config surface:** budget + per-feature costs are already config-driven for budgeted
  (`tasks_def/configs/budgeted_tep.py` `budget`, npz `costs`). The SDK primitive should take these as
  generic ledger parameters.

## Boundaries

- Keep `budgeted-tep` working as the reference; the generalization should be able to re-express it with
  no behavior change (same band). Do NOT regress this task.
- Reference files: `worlds/budgeted/{verify.py,policy_runner.py,world.py,Dockerfile}`,
  `sdk/path_mappings.py`, `sdk/hor_task.py`.
