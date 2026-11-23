# Terminal 4 — Test Infrastructure + Docstring Uplift
# Provider: Gemini (analysis, doc generation, audit)
# Issues: #1647, #1665, #1645
# Est. Time: 2-3 hours

We are in /mnt/local-analysis/workspace-hub. This is a Python monorepo with
`digitalmodel/` as a nested git repo (separate .git). All commits for
digitalmodel code MUST be made from inside `digitalmodel/`.

Use `uv run` for all Python — never bare `python3` or `pip`.
Do NOT ask the user any questions. Work autonomously.
Do NOT branch — commit to `main` and push after each task.
Run `git pull origin main --rebase` before every push (stash if needed).

IMPORTANT: Do NOT write to any of these paths (owned by other terminals):
- digitalmodel/src/digitalmodel/cathodic_protection/ (Terminal 1)
- digitalmodel/tests/cathodic_protection/ (Terminal 1)
- digitalmodel/src/digitalmodel/ansys/ (Terminal 2)
- digitalmodel/tests/ansys/ (Terminal 2)
- digitalmodel/src/digitalmodel/fatigue/ (Terminal 3)
- digitalmodel/tests/fatigue/ (Terminal 3)
- digitalmodel/src/digitalmodel/solvers/ (Terminal 5)
- scripts/solver/ (Terminal 5)
- scripts/cron/ (Terminal 5)

Only write to:
- digitalmodel/pyproject.toml (dependency additions only — TASK 1)
- digitalmodel/src/digitalmodel/web/ (docstrings only — TASK 3)
- digitalmodel/src/digitalmodel/reservoir/ (docstrings only — TASK 3)
- digitalmodel/src/digitalmodel/infrastructure/ (docstrings only — TASK 3)
- digitalmodel/src/digitalmodel/marine_ops/ (docstrings only — TASK 3)
- docs/dashboards/ (TASK 2 reports)

---

## TASK 1: Fix Broken Test Dependencies (#1647)
GH Issue: #1647

The test health dashboard revealed 149 pytest collection errors. Most are caused by
missing optional dependencies: pint, plotly, deepdiff, factory-boy, loguru.

### Steps:
1. Check current state: `cd digitalmodel && uv run pytest --co -q 2>&1 | grep "ERROR" | head -30`
2. Look at pyproject.toml for current dev dependencies:
   `cat digitalmodel/pyproject.toml | grep -A 50 '\[project.optional-dependencies\]'`
3. Add missing test deps to pyproject.toml under `[project.optional-dependencies]` test group:
   - pint
   - plotly
   - deepdiff
   - factory-boy
   - loguru
   Check which are actually imported: `cd digitalmodel && grep -r "import pint\|import plotly\|import deepdiff\|import factory\|import loguru" src/ tests/ | head -30`
4. Install: `cd digitalmodel && uv sync --extra test` (or however deps are structured)
5. Re-run collection: `cd digitalmodel && uv run pytest --co -q 2>&1 | grep "ERROR" | wc -l`
6. Report how many errors remain

Commit message: `fix(deps): add missing test dependencies — pint, plotly, deepdiff, factory-boy (#1647)`
Commit from inside `digitalmodel/` directory.

---

## TASK 2: Triage 149 Pytest Collection Errors (#1665)
GH Issue: #1665

After fixing deps in Task 1, triage the remaining errors.

### Steps:
1. Run: `cd digitalmodel && uv run pytest --co -q 2>&1 | grep "ERROR" > /tmp/remaining_errors.txt`
2. Categorize errors:
   - Missing pip dependencies (list which ones)
   - Broken imports (circular deps, stale references — list files)
   - Missing test fixtures/data (list files)
   - Other (syntax errors, etc.)
3. Write triage report: `docs/dashboards/test-error-triage-2026-04-02.md`
   - Summary table: category | count | example | fix needed
   - Top 5 worst packages by error count
   - Recommended fix order
4. Fix any easy wins (simple import fixes, missing __init__.py, etc.)
5. Re-run to get updated count
6. Comment on #1665 with results

Commit message: `docs(dashboards): test error triage report — categorized 149 collection errors (#1665)`
Commit from workspace-hub root for the report, from digitalmodel/ for any source fixes.

---

## TASK 3: Docstring Uplift Wave 2 (#1645)
GH Issue: #1645 — web, reservoir, infrastructure, marine_ops packages

### Rules:
- ONLY add/improve docstrings — do NOT change any logic or function signatures
- Use Google-style docstrings (Args, Returns, Raises, Examples)
- Every public function and class needs a docstring

### Steps:
1. For each package (web, reservoir, infrastructure, marine_ops):
   a. List all .py files: `ls digitalmodel/src/digitalmodel/<pkg>/*.py`
   b. Check which functions lack docstrings: `cd digitalmodel && uv run python -c "import ast; ..."`
   c. Add/improve Google-style docstrings to all public functions and classes
   d. Verify no tests break: `cd digitalmodel && uv run pytest tests/<pkg>/ -v --tb=short 2>&1 | tail -10`
2. Start with web/ (69 files, 0 tests — docstrings are the main quality gate)
3. Then reservoir/ (be careful: do NOT modify stratigraphic.py logic)
4. Then infrastructure/
5. Then marine_ops/

Commit message per package:
- `docs(web): Google-style docstring uplift — all public APIs (#1645)`
- `docs(reservoir): Google-style docstring uplift — all public APIs (#1645)`
- `docs(infrastructure): Google-style docstring uplift — all public APIs (#1645)`
- `docs(marine_ops): Google-style docstring uplift — all public APIs (#1645)`

Each commit from inside `digitalmodel/` directory.

---

After all tasks, post progress comments:
```
gh issue comment 1647 --repo vamseeachanta/workspace-hub --body "Terminal 4 overnight: fixed missing test deps. Added pint, plotly, deepdiff, factory-boy, loguru to dev deps. Collection errors reduced from 149 to N."

gh issue comment 1665 --repo vamseeachanta/workspace-hub --body "Terminal 4 overnight: triage complete. See docs/dashboards/test-error-triage-2026-04-02.md for full categorization. N errors by missing deps, N by broken imports, N by missing fixtures."

gh issue comment 1645 --repo vamseeachanta/workspace-hub --body "Terminal 4 overnight: docstring wave 2 complete for web, reservoir, infrastructure, marine_ops packages."
```
