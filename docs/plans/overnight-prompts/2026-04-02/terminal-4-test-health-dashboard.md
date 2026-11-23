# Terminal 4 — Test Health Dashboard + Reservoir Refactor + Cron Scheduling

Provider: **Gemini** (analysis, doc generation, audit reports)
Issues: #1573, #1633, #1590, #1625

---

We are in /mnt/local-analysis/workspace-hub. Execute these 3 tasks in order.
Use `uv run` for all Python — never bare python3. Commit to main and push after each task.
Do not branch. TDD: write tests before implementation.
Do NOT ask the user any questions. Run `git pull origin main` before every push.

IMPORTANT: Do NOT write to scripts/solver/, scripts/analysis/, scripts/docs/,
scripts/document-intelligence/, docs/architecture/, docs/roadmaps/,
digitalmodel/src/digitalmodel/structural/, digitalmodel/src/digitalmodel/subsea/,
digitalmodel/src/digitalmodel/asset_integrity/, digitalmodel/tests/orcaflex/,
digitalmodel/tests/solver/, digitalmodel/tests/web/ — those are owned by other terminals.
Only write to: scripts/quality/, tests/quality/, docs/dashboards/,
digitalmodel/src/digitalmodel/reservoir/stratigraphic.py,
digitalmodel/tests/reservoir/, config/cron/.

---

## TASK 1: Cross-Repo Test Health Dashboard (GH issue #1573)

**Context**: We have 30+ packages with varying test coverage. No unified dashboard exists
to show pass/fail status and coverage trends. The module status matrix covers maturity
but not test execution results.

**Acceptance criteria**:
1. Write tests first: `tests/quality/test_test_health_dashboard.py`
   - Test test runner output parsing
   - Test markdown report generation
   - Test pass/fail counting logic
   - Test package-level aggregation
   - At least 8 test functions
2. Create `scripts/quality/test-health-dashboard.py`:
   - Run `uv run pytest digitalmodel/tests/ --tb=no -q` and parse results
   - Per-package: total tests, passed, failed, skipped, errors
   - Overall: total pass rate, packages with failures, coverage gaps
   - Generate `docs/dashboards/test-health-dashboard.md` with:
     - Summary table (package | tests | pass | fail | skip | rate)
     - Red/green status badges (emoji-based)
     - Timestamp of last run
     - List of packages with 0 tests (gap list)
3. Tests pass: `uv run pytest tests/quality/ -v`

**Commit message**: `feat(quality): cross-repo test health dashboard with per-package metrics (#1573)`

---

## TASK 2: Refactor reservoir/stratigraphic.py (GH issue #1633)

**Context**: `digitalmodel/src/digitalmodel/reservoir/stratigraphic.py` is a raw plotting
script with undefined globals (WELL1, WELL2, df_logs, statdata). Importing it raises
NameError. This blocks reservoir package maturity.

**Acceptance criteria**:
1. Write tests first: `digitalmodel/tests/reservoir/test_stratigraphic.py`
   - Test with mock DataFrames (no real well data needed)
   - Test function signatures and return types
   - Test error handling for bad inputs
   - At least 6 test functions
   - Mock matplotlib: `@pytest.fixture(autouse=True) def mock_plt(monkeypatch): ...`
2. Refactor `stratigraphic.py`:
   - Wrap plotting logic in functions with proper signatures:
     - `create_cross_section(wells_list, df_logs, statdata, ...)` — main entry
     - `plot_gr_track(ax, df, ...)` — gamma ray log track
     - `plot_rt_track(ax, df, ...)` — resistivity track
     - `plot_rhob_nphi_track(ax, df, ...)` — density-neutron overlay
     - `plot_facies_track(ax, df, ...)` — facies classification track
   - Add type hints and docstrings
   - Add `if __name__ == '__main__':` guard for CLI use
   - Remove bare global references
3. Verify import works: `uv run python -c "from digitalmodel.reservoir.stratigraphic import create_cross_section; print('OK')"`
4. Tests pass: `uv run pytest digitalmodel/tests/reservoir/test_stratigraphic.py -v`

**Commit message**: `refactor(reservoir): stratigraphic.py — raw script to importable module (#1633)`

---

## TASK 3: Schedule Architecture Scanner + Staleness Scanner as Cron Tasks (GH issues #1590, #1625)

**Context**: The architecture scanner (`scripts/analysis/architecture-scanner.py`) and
staleness scanner (`scripts/docs/staleness-scanner.py`) should run periodically.
The repo uses `config/cron/schedule-tasks.yaml` as the cron source of truth.

**Acceptance criteria**:
1. Read existing `config/cron/schedule-tasks.yaml` to understand the format
2. Add two new cron entries:
   - Architecture scanner: weekly (Sunday 2am) — runs scanner, commits updated reports
   - Staleness scanner: weekly (Sunday 3am) — runs scanner, commits freshness dashboard
3. Create wrapper scripts if needed:
   - `scripts/analysis/cron-architecture-scan.sh` — pulls, runs scanner, commits, pushes
   - `scripts/docs/cron-staleness-scan.sh` — pulls, runs scanner, commits, pushes
4. Verify YAML is valid: `uv run python -c "import yaml; yaml.safe_load(open('config/cron/schedule-tasks.yaml'))"`
5. Do NOT modify setup-cron.sh — only add entries to the YAML

**Commit message**: `feat(cron): schedule architecture + staleness scanners as weekly tasks (#1590, #1625)`

---

Post a brief progress comment on GH issues #1573, #1633, #1590, #1625 when complete.
