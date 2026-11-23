---
phase: 1
slug: accelerate-digitalmodel-development
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-25
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (already in pyproject.toml) |
| **Config file** | `digitalmodel/pyproject.toml` (`[tool.pytest.ini_options]`) |
| **Quick run command** | `cd digitalmodel && python -m pytest tests/{module}/ -x -q` |
| **Full suite command** | `cd digitalmodel && python -m pytest tests/cathodic_protection/ tests/{new_modules}/ -q` |
| **Estimated runtime** | ~15 seconds (new module tests only; excludes broken legacy suite) |

---

## Sampling Rate

- **After every task commit:** Run `cd digitalmodel && python -m pytest tests/{module}/ -x -q`
- **After every plan wave:** Run full suite for all new + CP modules
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | D-05/D-06 | unit | `pytest tests/test_manifest_schema.py` | ❌ W0 | ⬜ pending |
| 01-02-01 | 02 | 1 | D-07 | unit | `pytest tests/on_bottom_stability/` | ❌ W0 | ⬜ pending |
| 01-03-01 | 03 | 2 | D-07 | unit | `pytest tests/spectral_fatigue/` | ❌ W0 | ⬜ pending |
| 01-04-01 | 04 | 2 | D-07 | unit | `pytest tests/{module3}/` | ❌ W0 | ⬜ pending |
| 01-05-01 | 05 | 3 | D-03 | integration | `pytest tests/ --ignore=tests/structural/analysis/` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_manifest_schema.py` — validates YAML manifest against Pydantic schema
- [ ] `tests/on_bottom_stability/conftest.py` — fixtures for DNV-RP-F109 test data
- [ ] `tests/on_bottom_stability/test_dnv_rp_f109.py` — stubs for stability calculations
- [ ] Test directories for each new module with `__init__.py` and `conftest.py`

*Self-contained suites per D-03 — no dependency on legacy test infrastructure.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Standards traceability in docstrings | D-05 | Semantic content check | Inspect docstrings for "Standard Section, Eq N" format |
| Market signal validation of module selection | D-01 | Business judgment | Review module choices against competitor capabilities |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
