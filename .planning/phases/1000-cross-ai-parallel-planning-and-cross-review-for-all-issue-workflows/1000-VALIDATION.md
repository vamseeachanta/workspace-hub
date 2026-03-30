---
phase: 1000
slug: cross-ai-parallel-planning-and-cross-review-for-all-issue-workflows
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-29
---

# Phase 1000 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | bash + bats-core (shell script testing) |
| **Config file** | none — Wave 0 installs bats if missing |
| **Quick run command** | `bash scripts/development/ai-plan/cross-plan.sh --dry-run` |
| **Full suite command** | `bats tests/ai-review/*.bats` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `bash scripts/development/ai-plan/cross-plan.sh --dry-run`
- **After every plan wave:** Run `bats tests/ai-review/*.bats`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| TBD | 01 | 1 | cross-plan dispatch | integration | `bash cross-plan.sh --dry-run` | ❌ W0 | ⬜ pending |
| TBD | 02 | 1 | parallel review | integration | `bash cross-review-loop.sh --parallel --dry-run` | ❌ W0 | ⬜ pending |
| TBD | 03 | 2 | delegation templates | unit | `grep phase_0_plan agent-delegation-templates.md` | ✅ | ⬜ pending |
| TBD | 04 | 2 | GSD skill integration | integration | `grep cross_plan plan-phase.md` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/ai-review/cross-plan.bats` — test stubs for cross-plan dispatch
- [ ] `tests/ai-review/parallel-review.bats` — test stubs for parallel review
- [ ] bats-core installed (or skip if not available, fall back to bash assertions)

*If none: "Existing infrastructure covers all phase requirements."*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| All 3 CLIs produce valid plans | cross-plan output | Requires live API calls | Run `cross-plan.sh` with real phase, verify 3 plan files created |
| Plan merge produces coherent result | synthesis quality | Subjective quality check | Read merged PLAN.md, verify no contradictions |
| Parallel review completes without rate limits | parallel dispatch | Requires live API calls | Run `cross-review-loop.sh --parallel` on real commit |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
