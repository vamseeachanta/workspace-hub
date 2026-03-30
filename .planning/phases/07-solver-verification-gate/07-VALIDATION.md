---
phase: 7
slug: solver-verification-gate
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-30
---

# Phase 7 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest tests/ -x -q --ignore=tests/solver` |
| **Full suite command** | `uv run pytest tests/ -v --ignore=tests/solver` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/ -x -q --ignore=tests/solver`
- **After every plan wave:** Run `uv run pytest tests/ -v --ignore=tests/solver`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 07-01-01 | 01 | 1 | D-14 | integration | `uv sync --check` on licensed-win-1 | ❌ W0 | ⬜ pending |
| 07-01-02 | 01 | 1 | D-06/D-08 | integration | `ssh licensed-win-1 "claude -p ..."` | ❌ W0 | ⬜ pending |
| 07-02-01 | 02 | 1 | D-09/D-10 | integration | `python -c "import OrcFxAPI; ..."` on licensed-win-1 | ❌ W0 | ⬜ pending |
| 07-02-02 | 02 | 1 | D-05/D-11 | artifact | `test -f tests/fixtures/*.owr` | ❌ W0 | ⬜ pending |
| 07-03-01 | 03 | 2 | D-12/D-13 | unit | `uv run pytest tests/test_module_separation.py` | ❌ W0 | ⬜ pending |
| 07-03-02 | 03 | 2 | D-16/D-17 | unit | `uv run pytest -m "not solver" -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_module_separation.py` — stubs for D-12/D-13 license boundary verification
- [ ] `tests/conftest.py` — `@pytest.mark.solver` marker registration, reference fixture paths
- [ ] SSH connectivity script — verify dev-primary → licensed-win-1 SSH path

*If none: "Existing infrastructure covers all phase requirements."*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| OrcFxAPI imports on licensed-win-1 | D-08 gate 1 | Requires Windows machine with license | SSH into licensed-win-1, run `python -c "import OrcFxAPI; print(OrcFxAPI.__version__)"` |
| Remote CC trigger from dev-primary | D-07/D-08 gate 2 | Cross-machine SSH + Claude Code | From dev-primary: `ssh licensed-win-1 "claude -p 'echo hello'"` |
| L00/L01 solver execution | D-09/D-10 | Requires OrcaFlex license | Run smoke test script on licensed-win-1, verify .owr output |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
