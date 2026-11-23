---
phase: 5
slug: nightly-research-automation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-29
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | bash + cron verification |
| **Config file** | config/scheduled-tasks/schedule-tasks.yaml |
| **Quick run command** | `bash scripts/cron/gsd-researcher-nightly.sh --dry-run` |
| **Full suite command** | `bash scripts/cron/gsd-researcher-nightly.sh --dry-run && bash scripts/cron/staleness-check.sh --dry-run` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `bash scripts/cron/gsd-researcher-nightly.sh --dry-run`
- **After every plan wave:** Run full suite command
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| *Populated during planning* | | | | | | | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Verify existing `scripts/cron/gsd-researcher-nightly.sh` runs without errors
- [ ] Verify `scripts/notify.sh` notification dispatch works
- [ ] Verify `claude` CLI is in PATH and authenticated

*Existing infrastructure covers most phase requirements.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Nightly cron fires on schedule | UAT | Requires real-time wait | Check cron log next morning |
| Research insights are actionable | UAT | Subjective quality | Review Friday synthesis report |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
