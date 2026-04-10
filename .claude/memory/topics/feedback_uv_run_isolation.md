> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-10
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_uv_run_isolation.md

---
name: feedback_uv_run_isolation
description: "uv run --no-project creates isolated env without .venv packages — use fallback imports or avoid optional deps"
type: feedback
---

`uv run --no-project python script.py` creates an ephemeral virtual environment that does NOT include packages installed in `.venv/` via `uv pip install`. This means optional dependencies like `networkx` that are installed in `.venv` won't be available when scripts run via `uv run --no-project`.

**Why:** Discovered in WRK-1247 — networkx was installed in `.venv` but the batch runner script couldn't import it. Interactive `-c` mode worked because it uses the current `.venv`, but script-file mode with `--no-project` isolates.

**How to apply:**
- For hub scripts with optional deps: always provide a fallback path (e.g., `_get_output_cells()` that works without networkx)
- Never rely on `uv pip install` making packages available to `--no-project` scripts
- If a dep is truly required: either use inline script deps (`# /// script` + `# dependencies = [...]`) WITHOUT local imports, OR don't use `--no-project`
- The `.venv` is only guaranteed accessible via `uv run python` (without `--no-project`) when a `pyproject.toml` exists in scope
