> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-22
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_local_venv_pytest_import_hang.md

---
name: Local venv pytest import hang
description: uv-run local verification (pytest AND linters black/isort) can hang indefinitely on repo venvs (digitalmodel, worldenergydata) even when Python runs fine. Fallbacks — CI, or version-pin-matched STANDALONE tools.
type: feedback
originSessionId: 942f20e5-0933-4d14-9c8a-0fa2f91d5be7
---
`uv run pytest --version` and even `.venv/bin/python -c "import pytest"` hang past 30 s on digitalmodel's local venv (verified 2026-05-11 during #515 follow-up PR #600 prep), but Python itself runs (`python -c "print('hi')"` works instantly).

**Generalizes beyond pytest — `uv run <linter>` also hangs.** On worldenergydata (verified 2026-05-25, PR #433), `uv run black/isort` (and pytest) hang at EXIT 124 the same way. This is the same hang the prior session hit that left worldenergydata's reconciled merge unpushed (it could never reach the linters, so a Black + an isort failure stayed hidden until a real CI run surfaced them serially — 3× ~14-min CI cycles wasted before checking locally).

**Standalone-tool bypass (the fast path — do this BEFORE pushing for CI):** run the linters from version-pin-matched standalone installs instead of `uv run`. They read the repo's `pyproject.toml` config from cwd, so output is byte-identical to CI *if the version matches the lockfile pin*:
- `~/.local/bin/black <file>` — was 25.9.0, matched `uv.lock` black pin exactly
- `~/.local/bin/isort <file>` — uv-tool-installed 8.0.1, matched pin (`profile=black` from pyproject)
- `uvx flake8 src/ --max-line-length=100 --extend-ignore=E203,W503 ...` — isolated env, sidesteps the project's uv-build hang entirely
Always `grep 'name = "<tool>"' -A2 uv.lock` to confirm the local version matches the pin before trusting local results. Replicate the WHOLE lint job locally (black + isort + flake8 over all of src/ tests/) in one pass to catch every offender — the CI lint step runs `bash -e` and dies at the FIRST failing sub-step, so serial CI pushes only reveal one violation at a time. See also [[feedback_uv_run_isolation]].

**Why:** Unknown — `import _pytest` alone hangs, so it's a pytest-internal import chain issue, not pyproject or plugin config. Possibly stale `__pycache__`, dependency drift in `.venv`, or an indexing call that hangs on something.

**How to apply:**

- Don't block on local pytest verification when the import itself hangs. Move to CI.
- Run `python -c "import py_compile; py_compile.compile('<test_file>', doraise=True)"` to confirm syntax — fast, no pytest dependency.
- Push the branch; rely on CI's pytest install (which is fresh from `uv sync` on a clean Python).
- If you really need local execution, try:
  1. `rm -rf .venv && uv sync` (rebuild venv)
  2. `rm -rf .pytest_cache __pycache__` (clear caches)
  3. `uv run --refresh pytest --version` (force re-install)

**Don't:** Spend > 5 minutes diagnosing local pytest hangs. The PR will tell you if there's a real test problem within minutes via CI.

**Side effects to watch for:**
- Hung pytest processes (PIDs accumulating with no progress)
- Background bash tasks that wait on pytest completion will pile up
- Cleanup with `pkill -9 -f pytest` is safe (your own processes)
