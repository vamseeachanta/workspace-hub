> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-16
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_local_venv_pytest_import_hang.md

---
name: Local venv pytest import hang
description: Pytest module import can hang indefinitely at digitalmodel/.venv even when Python itself runs fine — `import pytest` alone times out at 30s. CI is the verification fallback.
type: feedback
originSessionId: 942f20e5-0933-4d14-9c8a-0fa2f91d5be7
---
`uv run pytest --version` and even `.venv/bin/python -c "import pytest"` hang past 30 s on digitalmodel's local venv (verified 2026-05-11 during #515 follow-up PR #600 prep), but Python itself runs (`python -c "print('hi')"` works instantly).

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
