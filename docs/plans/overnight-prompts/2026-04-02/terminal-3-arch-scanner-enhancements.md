# Terminal 3 — Architecture Scanner Enhancements + Maturity Tracker Updates

Provider: **Codex seat 2** (bounded TDD implementation)
Issues: #1626, #1627, #1629, #1634

---

We are in /mnt/local-analysis/workspace-hub. Execute these 4 tasks in order.
Use `uv run` for all Python — never bare python3. Commit to main and push after each task.
Do not branch. TDD: write tests before implementation.
Do NOT ask the user any questions. Run `git pull origin main` before every push.

IMPORTANT: Do NOT write to scripts/solver/, digitalmodel/tests/orcaflex/,
digitalmodel/tests/solver/, scripts/docs/, scripts/document-intelligence/,
docs/roadmaps/, docs/dashboards/, docs/document-intelligence/,
digitalmodel/src/digitalmodel/structural/, digitalmodel/src/digitalmodel/subsea/,
digitalmodel/src/digitalmodel/asset_integrity/ — those are owned by other terminals.
Only write to: scripts/analysis/, tests/analysis/, docs/architecture/,
digitalmodel/src/digitalmodel/data_models/__init__.py,
digitalmodel/src/digitalmodel/reservoir/stratigraphic.py,
digitalmodel/tests/reservoir/.

---

## TASK 1: Fix data_models missing __init__.py (GH issue #1626)

**Context**: `digitalmodel/src/digitalmodel/data_models/` lacks an `__init__.py`,
making it invisible to the architecture scanner (reports 30 packages instead of 31).

**Acceptance criteria**:
1. Create `digitalmodel/src/digitalmodel/data_models/__init__.py` with appropriate
   module docstring and public API exports
2. Inspect existing .py files in data_models/ to determine what should be exported
3. Re-run architecture scanner: `uv run python scripts/analysis/architecture-scanner.py`
4. Verify data_models appears in output — should now report 31 packages
5. Update `docs/architecture/api-surface-map.md` and `docs/architecture/api-surface-map.yaml`

**Commit message**: `fix(data_models): add __init__.py — visible to architecture scanner (#1626)`

---

## TASK 2: Architecture Scanner — Cross-Package API Name Collision Detection (GH issue #1627)

**Context**: `scripts/analysis/architecture-scanner.py` reports 3,271 public symbols across
30+ packages. We need collision detection.

**Acceptance criteria**:
1. Write tests first: `tests/analysis/test_collision_detection.py`
   - Test collision detection with mock package data
   - Test deduplication logic
   - Test report formatting
   - At least 8 test functions
2. Add `--detect-collisions` flag to `scripts/analysis/architecture-scanner.py`
3. Build reverse index: symbol_name → list of packages exporting it
4. Flag any symbol exported by 2+ packages
5. Append collision report section to `docs/architecture/api-surface-map.md`
6. Output top-20 most common colliding symbol names
7. Tests pass: `uv run pytest tests/analysis/test_collision_detection.py -v`

**Commit message**: `feat(arch): API name collision detection across packages (#1627)`

---

## TASK 3: Module Status Matrix — LOC-Weighted Scoring (GH issue #1629)

**Context**: `scripts/analysis/module_status_matrix.py` classifies packages by simple
thresholds. We need a richer scoring model.

**Acceptance criteria**:
1. Write tests first: `tests/analysis/test_weighted_scoring.py`
   - Test LOC-weighted score calculation
   - Test test-to-source ratio metric
   - Test trend comparison (current vs previous JSON snapshot)
   - At least 6 test functions
2. Add to module_status_matrix.py:
   - LOC-weighted quality score (tests * files / total_loc * 100)
   - Test-to-source ratio column
   - Trend column (↑ ↓ → compared to previous run if JSON exists)
3. Re-run: `uv run python scripts/analysis/module_status_matrix.py`
4. Update `docs/architecture/module-status-matrix.md` with new columns
5. Update `docs/architecture/module-status-matrix.json` for future trend tracking
6. Tests pass: `uv run pytest tests/analysis/test_weighted_scoring.py -v`

**Commit message**: `feat(arch): LOC-weighted scoring + trend tracking for module status matrix (#1629)`

---

## TASK 4: Update Maturity Tracker — 5 Packages SKELETON → DEVELOPMENT (GH issue #1634)

**Context**: Overnight run on 2026-04-01 added tests to field_development, geotechnical,
nde, reservoir packages (plus web got some). The maturity tracker needs updating.

**Acceptance criteria**:
1. Re-run the module status matrix: `uv run python scripts/analysis/module_status_matrix.py`
2. Verify field_development, geotechnical, nde, reservoir show as DEVELOPMENT (not SKELETON)
3. Check if web now has tests (it got 5 test files in the previous run)
4. Regenerate `docs/architecture/module-status-matrix.md`
5. Regenerate `docs/architecture/module-status-matrix.json`
6. Post comment on #1634 with before/after counts

**Commit message**: `docs(arch): update maturity tracker — 5 packages SKELETON → DEVELOPMENT (#1634)`

---

Post a brief progress comment on GH issues #1626, #1627, #1629, #1634 when complete.
