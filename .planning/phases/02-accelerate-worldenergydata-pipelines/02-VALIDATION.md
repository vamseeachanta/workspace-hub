---
phase: 2
slug: accelerate-worldenergydata-pipelines
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-25
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | `worldenergydata/pyproject.toml` |
| **Quick run command** | `cd worldenergydata && uv run pytest tests/ -x -q --tb=short` |
| **Full suite command** | `cd worldenergydata && uv run pytest tests/ -v` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd worldenergydata && uv run pytest tests/ -x -q --tb=short`
- **After every plan wave:** Run `cd worldenergydata && uv run pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | D-17 | unit | `uv run pytest tests/test_adapter_pattern.py -v` | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 1 | D-18 | integration | `uv run pytest tests/test_eia_adapter.py -v` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02 | 1 | D-10 | integration | `uv run pytest tests/test_bsee_adapter.py -v` | ❌ W0 | ⬜ pending |
| 02-03-01 | 03 | 2 | D-13,D-14 | unit | `uv run pytest tests/test_staleness.py -v` | ❌ W0 | ⬜ pending |
| 02-04-01 | 04 | 2 | D-15,D-16 | unit | `uv run pytest tests/test_alerting.py -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_adapter_pattern.py` — stubs for adapter base pattern validation
- [ ] `tests/test_eia_adapter.py` — stubs for EIA adapter integration
- [ ] `tests/test_bsee_adapter.py` — stubs for BSEE adapter integration
- [ ] `tests/test_staleness.py` — stubs for staleness monitoring
- [ ] `tests/test_alerting.py` — stubs for email alerting
- [ ] `tests/conftest.py` — shared fixtures (mock scheduler, temp data dirs)

*Existing infrastructure covers pytest basics; Wave 0 adds phase-specific test files.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Email alert delivery | D-15 | Requires SMTP server | Configure test SMTP, trigger failure, verify email received |
| systemd scheduler daemon | D-17 | Requires systemd host | Deploy service, check `systemctl status`, verify job runs |
| SODIR API availability | D-03 | External API dependency | Run SODIR adapter against live endpoint, verify data returned |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
