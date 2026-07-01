FROM apex_arena:base
WORKDIR /workdir

# SINGLE shared Dockerfile for every budgeted task. materialize() renders it (baking {{TASK_NAME}})
# when a task ships no Dockerfile of its own. COPY-FROM paths are ./tests/<pkg> because materialize
# injects the code packages under tests/ (the apex/Teapot strict allowlist).

# /tmp is root-only (not student-writeable); the student writes intermediates to /workdir.
RUN chmod 1755 /tmp

ENV PIP_NO_COLOR=1 \
    TQDM_DISABLE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/root/src \
    UV_HTTP_TIMEOUT=180 \
    UV_CONCURRENT_DOWNLOADS=4

# Which task this image is; active_config() reads it at build/prehook/grade time.
ENV BUDGETED_TASK={{TASK_NAME}}

# ── Pre-flight checks ─────────────────────────────────────────────────────────
RUN mkdir -p /root/src
COPY ./task.yaml                    /root/src/task.yaml
COPY ./src/pre_build/check_build.py /root/src/check_build.py
RUN python3 /root/src/check_build.py

# ── Heavy 1: venvs (model + grader) ───────────────────────────────────────────
RUN --mount=type=bind,source=./src/venvs,target=/tmp/venvs \
    UV_PROJECT_ENVIRONMENT=/venvs/model_venv uv sync \
        --project /tmp/venvs --only-group model --frozen \
    && UV_PROJECT_ENVIRONMENT=/venvs/grader_venv uv sync \
        --project /tmp/venvs --only-group grader --frozen --compile-bytecode \
    && chmod 755 /venvs \
    && chown -R model:model /venvs/model_venv \
    && chmod -R 755 /venvs/model_venv \
    && chmod -R 700 /venvs/grader_venv \
    && rm -rf /root/.cache/uv

# ── Heavy 2: inject code packages + lay out data ──────────────────────────────
RUN mkdir -p /root/src /data_agent /data_root
COPY ./tests/sdk       /root/src/sdk
COPY ./tests/worlds    /root/src/worlds
COPY ./tests/tasks_def /root/src/tasks_def
RUN /venvs/model_venv/bin/python -m worlds.budgeted.setup_data
RUN chmod -R 700 /data_root & chmod -R 755 /data_agent & wait

# ── Policy runner: baked to a root-owned 755 path so the sandboxed model user can run it but the
#    student cannot tamper with it. verify.py spawns it under model_venv, dropped to model. ──
RUN mkdir -p /opt/budgeted \
    && cp /root/src/worlds/budgeted/policy_runner.py /opt/budgeted/policy_runner.py \
    && chown -R root:root /opt/budgeted && chmod 755 /opt/budgeted && chmod 755 /opt/budgeted/policy_runner.py

# Lock down all source under /root/src (student-invisible).
RUN chmod -R 700 /root/src

RUN mkdir -p /workdir/solution && chown -R model:model /workdir/solution && chmod -R 755 /workdir/solution
RUN mkdir -p /workdir/tmp && chown model:model /workdir/tmp && chmod 755 /workdir/tmp
ENV TMPDIR=/workdir/tmp TMP=/workdir/tmp TEMP=/workdir/tmp

COPY ./setup.sh /mcp_server/tasks/{{TASK_NAME}}/setup.sh
RUN chmod +x /mcp_server/tasks/{{TASK_NAME}}/setup.sh

COPY ./tests/    /tests/
COPY ./grader.py /tests/
RUN chown -R root:root /tests && chmod -R 700 /tests
