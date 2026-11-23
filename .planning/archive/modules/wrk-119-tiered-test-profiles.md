---
title: "Test Suite Optimization — Tiered Test Profiles"
description: "Design and implement tiered test profiles (commit, task, session) across workspace-hub, worldenergydata, and digitalmodel"
version: "1.0"
module: "workspace-hub/testing"

session:
  id: "20260212"
  agent: "claude-opus-4-6"

review:
  required_iterations: 3
  current_iteration: 0
  status: "pending"
  reviewers:
    openai_codex:
      status: "pending"
      iteration: 0
      feedback: ""
    google_gemini:
      status: "pending"
      iteration: 0
      feedback: ""
    legal_sanity:
      status: "pending"
      iteration: 0
      violations: 0
  ready_for_next_step: false

status: "implementing"
progress: 80

created: "2026-02-12"
updated: "2026-02-12"
target_completion: "2026-02-15"

priority: "high"
tags: [testing, infrastructure, cross-repo]

links:
  spec: "specs/modules/wrk-119-tiered-test-profiles.md"
  branch: ""
---

# Test Suite Optimization — Tiered Test Profiles

> **Module**: workspace-hub/testing | **Status**: draft | **Created**: 2026-02-12

## Summary

Speed up test execution across workspace-hub, worldenergydata, and digitalmodel by implementing three tiered test profiles matched to workflow context: pre-commit (fast), per-task (module-scoped), and per-session (full regression). Also standardize the inconsistent test invocation infrastructure.

---

## Current State (Exploration Findings)

### worldenergydata
- **384 test files** across 8+ module directories
- **Broken venv**: `.venv` symlinks point to missing miniconda3 — must use system `python3` (3.12.3)
- **`--noconftest` workaround**: Root conftest.py has `py.path.local` deprecation issue in pytest 9.0.2
- **Markers defined**: 18 (unit, integration, slow, benchmark, performance, etc.) — but only 296 files use `@pytest.mark.unit`
- **Config**: pytest.ini has `--cov-fail-under=80`, 300s timeout, `addopts` includes coverage + strict markers
- **CI**: Uses `uv run pytest` but uv is not installed locally
- **PYTHONPATH**: Manual `src:../assetutilities/src` required
- **Parallelization**: Makefile has `-n auto --dist loadscope` but not used in practice locally

### digitalmodel
- **346 test files** across 31 conftest.py files (2,676 lines of fixtures)
- **Healthy venv**: `.venv` managed by uv 0.10.0, Python 3.11.14
- **Markers defined**: 27 (unit, integration, slow, benchmark, performance, security, property, chaos_test, etc.)
- **Config**: pytest.ini has `--cov-fail-under=85`, 300s timeout, 50 maxfail
- **CI**: 13 GitHub workflows, module-specific test workflows
- **PYTHONPATH**: Root conftest.py adds `src/`, `../assetutilities/src/`, `../aceengineercode/`
- **Parallelization**: Makefile has `-n auto --dist loadscope`, pytest-xdist installed

### workspace-hub
- **5 Python test files** + JS test files (legacy baseline system)
- **No root pytest.ini or pyproject.toml** for Python
- **CI disabled**: Workflows assume Node.js, need rewrite
- **Mixed stack**: Jest/Playwright/Stryker (JS) + pytest (Python)
- **Pre-commit**: Only commitizen for commit messages

### Key Pain Points
1. **Inconsistent invocation**: Each repo has different PYTHONPATH, conftest, and venv requirements
2. **No fast feedback loop**: Full suite (700+ tests) runs even for single-file changes
3. **Broken venv in worldenergydata**: Forces `--noconftest` workaround, losing fixtures
4. **No test-file mapping**: No way to auto-discover which tests cover a changed source file
5. **Marker underuse**: 18+ markers defined but majority of tests lack markers entirely

---

## Architecture

### Tiered Test Runner (3 scripts at workspace-hub level)

```
workspace-hub/scripts/test/
├── test-commit.sh      # Tier 1: Pre-commit (~5-10s)
├── test-task.sh        # Tier 2: Per-task (~30-60s)
├── test-session.sh     # Tier 3: Full regression
├── lib/
│   ├── detect-repo.sh      # Detect which repo a file belongs to
│   ├── map-tests.sh        # Map source files → test files
│   ├── invoke-pytest.sh    # Standardized pytest invocation per repo
│   └── report.sh           # Unified result reporting
└── config/
    ├── worldenergydata.conf  # Repo-specific pytest flags, PYTHONPATH
    ├── digitalmodel.conf     # Repo-specific pytest flags, PYTHONPATH
    └── workspace-hub.conf    # Repo-specific pytest flags
```

### Test File Mapping Convention

Source-to-test mapping follows these rules (checked in order):
1. `src/<pkg>/<module>/foo.py` → `tests/<module>/test_foo.py`
2. `src/<pkg>/<module>/foo.py` → `tests/unit/test_foo.py`
3. `src/<pkg>/<module>/sub/foo.py` → `tests/<module>/sub/test_foo.py`
4. Fallback: run all tests in the module's test directory

### Standardized Invocation (per-repo config)

Each `.conf` file defines:
```bash
REPO_ROOT="/mnt/local-analysis/workspace-hub/<repo>"
PYTHONPATH="src:../assetutilities/src"
PYTEST_BIN="python3 -m pytest"   # or ".venv/bin/pytest" if venv healthy
CONFTEST_FLAG=""                  # or "--noconftest" if conftest broken
BASE_ARGS="-v --tb=short"
MARKER_EXCLUDE="-m 'not slow and not benchmark and not performance'"
```

---

## Phases

### Phase 1: Infrastructure & Standardization (Foundation)

**Goal**: Fix the broken pieces and create the shared library.

- [ ] **1.1** Create `scripts/test/` directory structure at workspace-hub level
- [ ] **1.2** Create `lib/invoke-pytest.sh` — standardized pytest invocation per repo
  - Detects venv health (check `.venv/bin/python` symlink target exists)
  - Falls back to system `python3` with correct PYTHONPATH
  - Handles `--noconftest` decision based on conftest health check
  - Passes repo-specific config (coverage thresholds, timeouts, markers)
- [ ] **1.3** Create repo config files (`config/*.conf`) for worldenergydata, digitalmodel, workspace-hub
- [ ] **1.4** Create `lib/detect-repo.sh` — given a file path, identify which repo it belongs to
- [ ] **1.5** Create `lib/map-tests.sh` — given source files, find corresponding test files
  - Convention-based: `src/pkg/module/foo.py` → `tests/module/test_foo.py`
  - Fallback: entire module test directory
  - Returns empty if no tests found (skip, don't fail)
- [ ] **1.6** Fix worldenergydata conftest.py `py.path.local` deprecation
  - Replace `py.path.local` usage with `pathlib.Path` equivalents
  - Remove need for `--noconftest` workaround
- [ ] **1.7** Write tests for the test infrastructure itself (meta-tests)
  - Test `map-tests.sh` with known source→test pairs
  - Test `detect-repo.sh` with paths from each repo
  - Test `invoke-pytest.sh` with dry-run mode

**Files created/modified:**
- `scripts/test/lib/invoke-pytest.sh` (new, ~80 lines)
- `scripts/test/lib/detect-repo.sh` (new, ~30 lines)
- `scripts/test/lib/map-tests.sh` (new, ~60 lines)
- `scripts/test/config/worldenergydata.conf` (new, ~15 lines)
- `scripts/test/config/digitalmodel.conf` (new, ~15 lines)
- `scripts/test/config/workspace-hub.conf` (new, ~15 lines)
- `worldenergydata/tests/conftest.py` (edit — fix py.path.local)
- `scripts/test/tests/test_map_tests.sh` (new, ~40 lines)

### Phase 2: Tier 1 — Pre-Commit Profile (~5-10s)

**Goal**: Fast feedback on changed files only. Safe to run on every commit.

- [ ] **2.1** Create `scripts/test/test-commit.sh`
  - Detect changed files via `git diff --cached --name-only --diff-filter=ACM`
  - Filter to `.py` files only
  - Group by repo using `detect-repo.sh`
  - Map to test files using `map-tests.sh`
  - Invoke pytest per-repo using `invoke-pytest.sh` with:
    - Only mapped test files (no full discovery)
    - `-x` (fail fast)
    - `--no-header` (minimal output)
    - `-m 'not slow and not benchmark and not integration'` (unit tests only)
    - No coverage (speed)
    - 30s timeout per test
  - Exit 0 if no test files found (don't block commit for untested files)
  - Report: pass/fail count per repo, total time
- [ ] **2.2** Add optional pre-commit hook integration
  - Add to `.pre-commit-config.yaml` as local hook (disabled by default)
  - Instructions to enable: `pre-commit install`
- [ ] **2.3** Test with representative scenarios
  - Change 1 file in worldenergydata → only matching tests run
  - Change 1 file in digitalmodel → only matching tests run
  - Change file with no tests → graceful skip
  - Change files in 2 repos → both repos tested

**Files created/modified:**
- `scripts/test/test-commit.sh` (new, ~100 lines)
- `.pre-commit-config.yaml` (edit — add local hook, disabled)

### Phase 3: Tier 2 — Per-Task Profile (~30-60s)

**Goal**: Run all tests for the module being worked on. Used during active development.

- [ ] **3.1** Create `scripts/test/test-task.sh`
  - Accept module name as argument: `test-task.sh bsee` or `test-task.sh dynacard`
  - Auto-detect from WRK item: `test-task.sh --wrk WRK-119` reads `target_repos` from frontmatter
  - Auto-detect from git changes: `test-task.sh --auto` groups changed files by module
  - Find all tests in the module directory
  - Invoke pytest per-repo with:
    - All tests in module directory
    - `-m 'not slow and not benchmark'` (skip only very slow tests)
    - Coverage for the module only (`--cov=src/<pkg>/<module>`)
    - 60s timeout per test
  - Report: pass/fail, coverage %, time per module
- [ ] **3.2** Add module-to-test-directory mapping config
  - `config/module-map.yml` — maps module names to test directories per repo
  - Example: `bsee: { repo: worldenergydata, src: src/worldenergydata/bsee, tests: tests/modules/bsee }`
- [ ] **3.3** Test with representative modules
  - `test-task.sh bsee` → runs ~50 BSEE tests
  - `test-task.sh dynacard` → runs dynacard visualization tests
  - `test-task.sh --auto` with mixed changes

**Files created/modified:**
- `scripts/test/test-task.sh` (new, ~120 lines)
- `scripts/test/config/module-map.yml` (new, ~60 lines)

### Phase 4: Tier 3 — Per-Session Profile (Full Regression)

**Goal**: Comprehensive test run before pushing or ending a session.

- [ ] **4.1** Create `scripts/test/test-session.sh`
  - Accept repo filter: `test-session.sh` (all) or `test-session.sh worldenergydata`
  - Run full test suite per repo using `invoke-pytest.sh` with:
    - All tests (no marker filtering)
    - Full coverage reporting
    - HTML + terminal coverage output
    - JUnit XML output for CI compatibility
    - 300s timeout per test
    - `-n auto` parallel execution where supported
  - Aggregate results across repos
  - Report: summary table (repo | tests | pass | fail | skip | coverage% | time)
- [ ] **4.2** Add coverage reporting aggregation
  - Merge coverage from multiple repos into workspace-level summary
  - Output to `reports/test-session-<date>.md`
- [ ] **4.3** Test full session run
  - Verify all 3 repos execute
  - Verify coverage reports generate correctly

**Files created/modified:**
- `scripts/test/test-session.sh` (new, ~100 lines)
- `scripts/test/lib/report.sh` (new, ~50 lines)

### Phase 5: Documentation & Integration

**Goal**: Make the tiered system discoverable and integrated into workflows.

- [ ] **5.1** Create `docs/testing/README.md` — test infrastructure guide
  - Overview of 3 tiers with usage examples
  - Repo-specific notes (venv state, PYTHONPATH, markers)
  - Troubleshooting common issues
  - How to add new test mappings
- [ ] **5.2** Update CLAUDE.md testing section to reference tiered scripts
- [ ] **5.3** Add test tier hints to work queue skill
  - When `/work run` processes an item, suggest the appropriate test tier

**Files created/modified:**
- `docs/testing/README.md` (new, ~150 lines)
- `CLAUDE.md` (edit — add testing section reference)
- `.claude/skills/coordination/workspace/work-queue/SKILL.md` (minor edit)

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| conftest.py fix breaks existing tests | Medium | High | Run full suite before and after fix; keep `--noconftest` as fallback flag |
| Source→test mapping misses some tests | Medium | Low | Fallback to module-level test directory; log unmapped files |
| Parallel execution causes flaky tests | Low | Medium | Tier 1/2 run sequentially; only Tier 3 uses `-n auto` |
| Different Python versions across repos | Low | Low | Config files specify per-repo Python binary |

## Estimated Effort

| Phase | Lines of Code | Effort |
|-------|--------------|--------|
| Phase 1: Infrastructure | ~260 lines (bash + config) + conftest fix | Moderate |
| Phase 2: Tier 1 (commit) | ~120 lines (bash) | Light |
| Phase 3: Tier 2 (task) | ~180 lines (bash + YAML) | Light |
| Phase 4: Tier 3 (session) | ~150 lines (bash) | Light |
| Phase 5: Documentation | ~200 lines (markdown) | Light |
| **Total** | **~910 lines** | **Moderate** |

---

## Cross-Review Process (MANDATORY)

> **REQUIREMENT**: Minimum **3 review iterations** with OpenAI Codex and Google Gemini before implementation.

### Review Status

| Gate | Status |
|------|--------|
| Legal Sanity | Pending |
| Iterations (>= 3) | 0/3 |
| OpenAI Codex | Pending |
| Google Gemini | Pending |
| **Ready** | Pending |

### Review Log

| Iter | Date | Reviewer | Verdict | Findings | Fixed |
|------|------|----------|---------|----------|-------|
| 1 | 2026-02-12 | Claude | MINOR | 4: PYTHONPATH accumulation, cd side-effect, --wrk arg parsing, report state reset | 4/4 |
| 1 | 2026-02-12 | Codex | MAJOR | 6: `local` outside function, test file skipping, path traversal, sed parsing, bash portability (accepted), hardcoded repos (accepted) | 4/6 |
| 1 | 2026-02-12 | Gemini | MAJOR | 9: unused config vars, missing set -euo, ALL_REPOS incomplete, unquoted expansion, fragile YAML parsing (accepted), module extraction (accepted), TestPerformanceTracker (pre-existing), workspace-hub handling (accepted), inconsistent repo lists (accepted) | 4/9 |

**Accepted findings** (not fixed — by design or out of scope):
- Bash 4+ dependency: Linux-only workspace, bash 5.x guaranteed
- Hardcoded repo lists: Intentionally minimal, extend via config
- Fragile YAML parsing: Controlled format in module-map.yml, adequate for use case
- TestPerformanceTracker: Pre-existing worldenergydata issue, not introduced by WRK-119
- Module extraction edge cases: Handles all current module layouts; revisit if new patterns emerge

### Approval Checklist

- [x] Plan reviewed by user
- [x] **APPROVED**: Ready for implementation

---

## Progress

| Phase | Status | Notes |
|-------|--------|-------|
| Exploration | Done | 3 repos audited |
| Plan Draft | Done | This document |
| Plan Approved | Done | User approved |
| Phase 1: Infrastructure | Done | lib/, config/, conftest fix. Cross-reviewed: 3 agents, 19 total findings, 12 fixed |
| Phase 2: Tier 1 (commit) | Done | test-commit.sh — staged/unstaged/all modes, submodule support |
| Phase 3: Tier 2 (task) | Done | test-task.sh — module name, --auto, --wrk modes, module-map.yml |
| Phase 4: Tier 3 (session) | Done | test-session.sh — full regression, markdown report generation |
| Phase 5: Documentation | Done | docs/testing/README.md |

---

## Session Log

| Date | Session ID | Agent | Notes |
|------|------------|-------|-------|
| 2026-02-12 | 20260212 | claude-opus-4-6 | Plan created after exploring all 3 repos |
| 2026-02-12 | 20260212 | claude-opus-4-6 | All 5 phases implemented, cross-reviewed by Claude+Codex+Gemini, fixes applied |
