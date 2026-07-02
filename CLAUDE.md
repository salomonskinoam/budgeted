# Claude working notes — budgeted

Design bible: `readmes/README_general_direction.md` (what makes a band, the falsifiers, the
acquisition-spread gate, why we landed on the mediated-grader task). Read it before touching the world.

## Scores: spread, and above all LEVELS
**We do NOT care about the mean. The product is the BAND.** Two metrics, reported together:
- **spread** = max − min across runs (report min/max/std/spread/mean, but never conclude from mean/std).
- **LEVELS = the number of statistically-distinguishable score tiers** (SDK `rank_resolution` `n_levels`
  in `sdk/hor_utils/noise.py`). **This is the most important metric.** A wide spread with only 1–2
  levels is a weak task; many resolvable levels is the goal. Always report `n_levels` next to spread.

A tight cluster is a bad task even at a high mean. A single high outlier above a packed score is good; a
single low outlier is not as good. Levels are capped by the **rarest class** (resolution): if the test
set can only resolve ~2 tiers, no lever creates more, widen the data before chasing more levels.

## Writing style

- Never use the em-dash ("—"). Use a comma, period, or parentheses instead. Also no "--" to replace it.
- Keep drafts short. Fewer words than you think you need.
- OMIT the "co authored by claude" from git commits.
- No inline imports. All imports go at the top of the file, always.

## Oracle

- **Never promote a solution to the oracle (`solution.sh`) without explicit user approval.** Present
  the candidate + its score and ask first.
- Oracles are NOT IMPORTANT until the final testing phase on taiga. the best observed until then should just be 1.0 even if we have offline "oracles" for testing. these are fake and do NOT reflect what the actual oracle is.

## Grader timeout

**The platform's time cap is the ONLY timeout. Never impose a shorter grader-side watchdog, and
never reduce a timeout below the platform's.** The cap is the sysadmin's to own and to raise (one day they will);
our code must not undercut it. A hanging policy is killed by that cap and doesn't score, and we deal with it.

## Compute: gate every local run through the user (unapproved heavy runs crashed the machine twice)

This is a weak personal laptop. Local runs are **ALLOWED, but any non-trivial one MUST be explicitly
approved by the user BEFORE running it.** Never launch one unprompted; describe what it is, why local,
and wait for the go. No "this one looks light" self-judgment, if it does real work, ask first.

**Requires prior user approval** — only genuinely HEAVY computation (default these to HOSTED unless the
user OKs local):
- model training, budget sweeps, policy replay, `recover_analyze.py`, XGBoost, torch
- **building or loading any dataset / npz** — including a "quick" `pd.read_csv` / `np.load` /
  `train_test_split` on real data. `make_data_*.py` for a big dataset defaults to hosted.
- fanning out compute-heavy local subagents (N parallel jobs = N× the load)

**Default (no approval needed): hosted.** A throwaway hosted task whose oracle/**validation** run does
the computation and returns the result (e.g. `predictions_b64`), like fusion's `recover_via_probe`.
`push` / `validate` / `evaluations submit` run on Horizon and are safe. Heavy compute we offload goes
via a throwaway task's VALIDATION run, never by spending evaluation runs.

**No approval needed (always allowed):** listeners / pollers / monitors (network-only status polling of
hosted evals — never heavy), tiny/instant work, file edits, config, git, network calls to hosted APIs.

## Jargon

- **the student** — the agent attempting to solve a task (learning via RL).
- **runs** — evaluations: agent rollouts against a task. "do 8 runs" = run 8 evals.
- **grader == judge**
- **world** — the Docker environment a task lives in.
- **produce** — running the student's solution to generate the graded artifact. NEVER call this
  "build". "Build" is reserved for Docker images only. The grader runs the student script to
  *produce* the artifact, then grades it.

## Model / agent-type defaults

- Default model: **`biggie-max-polara`** unless told otherwise.
- On **Teapot** (`--teapot`): **`nighthawk`**.
- Agent-type: always **`meteor`** (pass `--agent-type meteor` explicitly).
- Machine-type (hosted eval VM, 16 vCPU / 32 GB): **`e2-custom-16-32768`**.
- Submit: `horizon evaluations submit <task_id> --runs N --model biggie-max-polara --agent-type meteor --machine-type e2-custom-16-32768 --json`
- **Runs are EXPENSIVE. Gate EVERY evaluation run through the user, never launch one unprompted.** Default `--runs 5` unless the user says otherwise.

## Commands — always complete, never placeholder

**Never give a command with `<placeholders>` or partial data.** Always fill in real values from context (task name, task ID, eval ID, batch ID, etc.). If a value is genuinely unknown, surface it explicitly: "I don't know the eval ID — run `horizon evaluations list` to find it" — then stop and wait. A command the user must complete before running is not a command.

## CLI

- Always `source horizon_env/bin/activate` from the repo root first.
- ALWAYS name the task — `.` does not work with `-m local`.
- mini_batch_id: `0067d7a3-4134-40d9-a4eb-c29faeeb24fe` (dedicated batch; the first push of a new task asks for it).

### Always surface the run link

Whenever an evaluation is submitted/running, give the user the **direct link** to it, no exceptions:
`https://horizon.bespokelabs.ai/evaluations/<eval-id>`. One link per eval-id, surfaced as soon as the
eval-id is known and again when results land. Alongside it, surface the **task link**:
`https://horizon.bespokelabs.ai/tasks/<task-id>`. Show both together whenever you show the run link.

### Hosted vs local

**Always use hosted (`-m hosted`).** "Hosted" = Cloud Batch on Horizon's infrastructure.
"Local" = Docker on your machine — never use this.

### Build/validation logs are TRUNCATED in the terminal

The hosted validate prints a lossy one-line `Feedback:`. The **full** Docker build log +
traceback is saved to `tasks/<task>/.validation/<build_id>/output.txt` by `validate-logs`.
**Never trust the terminal summary for debugging** — read `output.txt`.

## Paths

- Tasks are self-contained: all paths live in the task's `src/paths.py`. Never hardcode a path anywhere — always import from there.
- Container-path constants live in `sdk.path_mappings`. Use ONLY these locations inside containers — never invent arbitrary paths:

| Constant | Container path | Permissions | Purpose |
|---|---|---|---|
| `CONTAINER_SRC` | `/root/src` | root-only | Task source (setup_data.py, prehook.py, verify.py) |
| `CONTAINER_TESTS` | `/tests` | 700 (locked) | Grader entry point + hidden checks |
| `CONTAINER_DATA_AGENT` | `/data_agent` | 755 | Agent-readable data (student-visible inputs) |
| `CONTAINER_DATA_ROOT` | `/data_root` | 700 (locked) | Grader-only data (reference + test split + ALL labels) |
| `CONTAINER_WORKDIR` | `/workdir` | agent r/w | Student's scratch space |
| `CONTAINER_MODEL_VENV` | `/venvs/model_venv` | 755 (read/exec only) | Student Python env (torch, model libs) |
| `CONTAINER_GRADER_VENV` | `/venvs/grader_venv` | 700 (locked) | Grader subprocess env; invisible to student |

- All path values are `pathlib.Path` (or `PurePosixPath` for container paths), never strings.
- In Dockerfiles: `COPY ./tests/foo /root/src/foo` — do not invent other destinations.
- `setup.sh` always delegates to a Python prehook — no logic in the shell file.
- Data lives at `/data_agent/` and `/data_root/` — never under `/workdir/`.

## Fail-fast, zero-fallback principle

**One linear code path. No fallbacks. No stubs. No conditional degradation.**

Every artifact that a stage produces (file, list, count) must always be produced, even if it is empty.
The next stage reads it unconditionally. An empty artifact is a valid successful state.

Rules:
- **Producers always write their output**, even when empty (empty file, empty list, 0 count).
- **Consumers always read unconditionally**. Never guard a read with an existence check. Missing artifact = crash = surfaced immediately.
- **Zero is not an error.** Handle it the same as non-zero. Never branch on emptiness.
- **No `if X.exists()`**, no `if len(X) > 0`, no `or default_value`. If it should exist, it does.
- **No placeholder scores or stub returns.** If grader data is missing, raise, do not `return score=1.0`.
- **Only business logic creates `if` statements.** Technicalities (file exists? list empty? stage ran?) must never branch; they are guaranteed by the pipeline or it crashes.

## Dockerfile rules

- **Keep Dockerfiles lean**: only `COPY`, `RUN pip install -r requirements.txt` (or `uv sync`), and `RUN python3 <script>`. No inline package lists, no logic.
- **Delegate pip deps to the venv pyproject / requirements.** One install line, not a multi-line package list.
- **Delegate all complex steps to Python scripts** (data prep in `setup_data.py`, etc.).

## Worklog

`readmes/WORKLOG.md` is the running log of what was done and why. Maintain it: after any
substantive change (new pattern, fix, decision, gotcha resolved), add an entry on TOP. No
timestamps. Say what was done and why, not how. Keep entries short.

____

When the user wants you to do something "for each X", a subagent should be assigned "each X".
