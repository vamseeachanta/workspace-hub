# Terminal 5 — Docstring Uplift + Cron Automation (Claude/Hermes)

We are in /mnt/local-analysis/workspace-hub. Execute these 4 tasks in order.
Use `uv run` for all Python — never bare `python3` or `pip`.
Commit to `main` and push after each task. Do not branch.
Run `git pull origin main` before every push.
Do NOT ask the user any questions. Make reasonable decisions autonomously.

IMPORTANT: Do NOT write to any of the following paths — they are owned by other terminals:
- digitalmodel/src/digitalmodel/orcawave/, digitalmodel/tests/orcawave/, digitalmodel/src/digitalmodel/specs/ (Terminal 1)
- digitalmodel/tests/parametric_hull/, digitalmodel/tests/orcaflex/, digitalmodel/tests/hydrodynamics/ (Terminal 2)
- digitalmodel/tests/web/, digitalmodel/tests/field_development/, digitalmodel/tests/geotechnical/, digitalmodel/tests/nde/, digitalmodel/tests/reservoir/ (Terminal 3)
- digitalmodel/pyproject.toml (Terminal 3 owns dependency changes)
- scripts/document-intelligence/, data/document-index/, docs/document-intelligence/ (Terminal 4)
- digitalmodel/src/digitalmodel/reservoir/stratigraphic.py (Terminal 3 owns refactor)

Only write to:
- digitalmodel/src/digitalmodel/web/ (docstrings only — do NOT change logic)
- digitalmodel/src/digitalmodel/reservoir/ (docstrings only — NOT stratigraphic.py)
- digitalmodel/src/digitalmodel/infrastructure/ (docstrings only)
- digitalmodel/src/digitalmodel/marine_ops/ (docstrings only)
- digitalmodel/src/digitalmodel/solvers/ (docstrings only)
- digitalmodel/src/digitalmodel/hydrodynamics/ (docstrings only)
- digitalmodel/src/digitalmodel/specialized/ (docstrings only)
- digitalmodel/src/digitalmodel/signal_processing/ (docstrings only)
- config/cron/
- scripts/cron/

---

## TASK 1: Docstring Uplift Wave 2 (GH issue #1645)

### Context
- Packages needing docstrings: web, reservoir, infrastructure, marine_ops
- Target: add module-level docstrings and function/class docstrings to reach 55%+ coverage
- Do NOT change any logic, imports, or function signatures — docstrings ONLY

### Steps
1. For each package (web, reservoir, infrastructure, marine_ops):
   a. List all .py files in `digitalmodel/src/digitalmodel/<package>/`
   b. Read each file
   c. Add module-level docstring if missing
   d. Add function/class docstrings if missing (Google style)
   e. Verify no logic changes: `git diff --stat` should show only docstring additions
2. Commit after all 4 packages are done (one commit, many files)
3. Verify: `git diff HEAD~1 --stat` should show only the expected packages
4. Note: for reservoir/, do NOT touch stratigraphic.py (Terminal 3 is refactoring it)

### Docstring style (Google):
```python
"""One-line summary.

Longer description if needed.

Args:
    param1: Description.
    param2: Description.

Returns:
    Description of return value.

Raises:
    ValueError: When input is invalid.
"""
```

### Commit message
```
docs(packages): docstring uplift wave 2 — web, reservoir, infrastructure, marine_ops (#1645)
```

---

## TASK 2: Docstring Uplift Wave 3 (GH issue #1646)

### Context
- Packages needing docstrings: solvers, hydrodynamics, specialized, signal_processing
- Same rules as wave 2: docstrings ONLY, no logic changes

### Steps
1. For each package (solvers, hydrodynamics, specialized, signal_processing):
   a. List all .py files
   b. Read each file
   c. Add module/function/class docstrings (Google style)
   d. Verify no logic changes
2. Commit after all 4 packages

### Commit message
```
docs(packages): docstring uplift wave 3 — solvers, hydrodynamics, specialized, signal_processing (#1646)
```

---

## TASK 3: Automate Architecture Scanner as Cron Task (GH issue #1590)

### Context
- Architecture scanner exists at `scripts/analysis/` (built in prior batch)
- Module status matrix exists at `docs/architecture/`
- Need to schedule these to run periodically via cron
- Cron config source of truth: `config/scheduled-tasks.yaml` (check exact filename)

### Steps
1. Find the scheduled tasks config: search for `schedule-tasks.yaml` or `scheduled-tasks.yaml` in config/
2. Read it to understand the format
3. Find the architecture scanner script(s) in scripts/analysis/
4. Create wrapper: `scripts/cron/run-architecture-scan.sh`
   - Pulls latest from git
   - Runs architecture scanner
   - Commits results if changed
   - Pushes (with pull-before-push safety)
5. Add entry to scheduled tasks config (weekly, Sunday 2 AM)
6. Test the wrapper: run it manually and verify it works
7. Regenerate crontab if setup-cron.sh exists: read it first, run if safe

### Commit message
```
feat(cron): automate architecture scanner as weekly cron task (#1590)
```

---

## TASK 4: Schedule Staleness Scanner as Cron Task (GH issue #1625)

### Context
- Staleness scanner exists (built in prior batch) — find it in scripts/docs/ or scripts/analysis/
- Need to schedule it to run weekly and update the freshness dashboard

### Steps
1. Find the staleness scanner script
2. Create wrapper: `scripts/cron/run-staleness-scan.sh`
   - Pulls latest from git
   - Runs staleness scanner
   - Commits dashboard update if changed
   - Pushes (with pull-before-push safety)
3. Add entry to scheduled tasks config (weekly, Sunday 3 AM — offset from architecture scan)
4. Test the wrapper manually
5. Write: `docs/plans/cron-schedule-update-apr3.md` summarizing what was added

### Commit message
```
feat(cron): schedule staleness scanner as weekly cron task (#1625)
```

---

Post a brief progress comment on GH issues #1645, #1646, #1590, #1625 when each task completes.
