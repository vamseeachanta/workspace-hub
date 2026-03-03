# Python Runtime Rules

> **Hard rule**: Always use `uv run` for all Python execution in workspace-hub repos.
> Never invoke bare `python3`, `pip install`, or `.venv/bin/python` directly.

## Why

`uv` reuses a cached virtual environment. Bare `python3` and `pip install` either use the
wrong Python, pollute the system environment, or silently reinstall packages on every run.

## Command Patterns

### workspace-hub hub scripts (no pyproject.toml in scope)
```bash
uv run --no-project python <script.py>
uv run --no-project python -c "import json; ..."
```

### Tier-1 Python repos (have pyproject.toml + uv.lock)
Run from the repo root — `uv run` auto-activates the project venv:

| Repo | pytest command |
|------|---------------|
| assetutilities | `uv run python -m pytest tests/ --noconftest` |
| digitalmodel | `PYTHONPATH=src uv run python -m pytest` |
| worldenergydata | `PYTHONPATH="src:../assetutilities/src" uv run python -m pytest --noconftest` |
| assethold | `uv run python -m pytest tests/ --noconftest --tb=short -q` |
| ogmanufacturing | `uv run python -m pytest tests/` |

### One-off scripts in hub context
```bash
# Generate index, reports, etc.
uv run --no-project python scripts/data/document-index/phase-e2-remap.py
uv run --no-project python .claude/work-queue/scripts/generate-index.py
```

### Installing / running tools
```bash
uv tool run <tool>          # ephemeral tool run (e.g. uv tool run black)
uv tool install <tool>      # permanent tool install to ~/.local/bin
uv add <package>            # add dep to current project (NOT pip install)
```

## Anti-Patterns (Never Do)

| Anti-pattern | Why banned | Use instead |
|-------------|-----------|-------------|
| `python3 script.py` | May use wrong Python; no venv | `uv run --no-project python script.py` |
| `pip install <pkg>` | Pollutes system/env; not reproducible | `uv add <pkg>` in the repo |
| `.venv/bin/python -m pytest` | Manual venv activation; fragile on path changes | `uv run python -m pytest` |
| `python -m venv .venv && pip install -r ...` | Creates disposable env from scratch every time | Let uv manage the venv |
| `source .venv/bin/activate` (in scripts) | Shell-state dependency; breaks subshells | `uv run` handles activation per command |

## Exception: acma-ansys05 (Windows)

On acma-ansys05, use `uv` via Git Bash. If `uv` is not in PATH:
```bash
# Locate uv
$USERPROFILE/.local/bin/uv run python -m pytest
# Or add to Git Bash PATH in .bashrc
export PATH="$HOME/.local/bin:$PATH"
```

## Verification

Check uv is available before running:
```bash
uv --version                          # should be ≥ 0.5.0
uv run --no-project python --version  # should match repo's .python-version
```

## uv Not Available

If `uv` is genuinely not installed on a machine:
1. Install via: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Do NOT fall back to bare `python3` without noting the fallback in the WRK evidence
3. Flag the machine in `workstations/SKILL.md` under install gaps

---

## Session Learnings

> This section is updated by comprehensive-learning Phase 1 when new per-repo patterns
> are confirmed across multiple sessions. Do not edit manually — edit the table above.

| Date | Repo | Learning | Source |
|------|------|---------|--------|
| 2026-03-03 | workspace-hub | Hub scripts need `--no-project` flag (no pyproject.toml at hub root) | WRK-689 |
| 2026-03-03 | digitalmodel | `PYTHONPATH=src` required even with uv; pytest.ini does not set it | MEMORY.md |
| 2026-03-03 | worldenergydata | `PYTHONPATH="src:../assetutilities/src"` needed; `--noconftest` required | MEMORY.md |
