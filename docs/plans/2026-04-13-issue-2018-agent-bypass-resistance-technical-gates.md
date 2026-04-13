# Plan for #2018: agent bypass resistance -- enforce workflow with technical gates, not text instructions

> **Status:** adversarial-reviewed
> **Complexity:** T3
> **Date:** 2026-04-13
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2018
> **Review artifacts:** scripts/review/results/2026-04-13-plan-2018-subagent.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `.claude/hooks/plan-approval-gate.sh` — runtime PreToolUse enforcement surface for implementation writes.
- Found: `scripts/enforcement/require-plan-approval.sh` — pre-commit gate for plan approval before commits.
- Found: `scripts/enforcement/require-review-on-push.sh` and related governance docs/tests — existing review gate infrastructure already enforces parts of the desired workflow.
- Found: `tests/work-queue/test_session_governor.py` contains extensive tests for the plan-approval gate and strict review gate behavior.
- Found: `docs/governance/TRUST-ARCHITECTURE.md` explicitly defines Category B plan-gate requirements and approval marker semantics.
- Found: `scripts/enforcement/upgrade-enforcement.sh` references issues `#1876` and `#2017`, showing the repo already has an enforcement-upgrade path and adjacent workflow-hardening work.
- Gap: there is no canonical local plan in `docs/plans/` for #2018 even though the issue is strategically important and tied to multiple enforcement surfaces.

### Standards
N/A — harness / workflow enforcement / governance task

### Documents consulted
- GitHub issue #2018 — mission statement and acceptance criteria for bypass resistance.
- `docs/governance/TRUST-ARCHITECTURE.md` — canonical approval/governance contract.
- `docs/standards/HARD-STOP-POLICY.md` — hard-gate policy context.
- `tests/work-queue/test_session_governor.py` — existing gate test surface.
- `scripts/enforcement/require-plan-approval.sh` — commit gate.
- `.claude/hooks/plan-approval-gate.sh` — runtime write gate.
- `scripts/enforcement/upgrade-enforcement.sh` — enforcement promotion path.

### Gaps identified
- No canonical local plan artifact exists for #2018.
- Need a parent plan that distinguishes what already exists from what still must be hardened.
- Need to avoid duplicating sibling issues while still defining the integrated bypass-resistance target state.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-13-issue-2018-agent-bypass-resistance-technical-gates.md` |
| Runtime plan gate | `.claude/hooks/plan-approval-gate.sh` |
| Commit gate | `scripts/enforcement/require-plan-approval.sh` |
| Push/review gate | `scripts/enforcement/require-review-on-push.sh` |
| Governance tests | `tests/work-queue/test_session_governor.py` |
| Trust contract | `docs/governance/TRUST-ARCHITECTURE.md` |
| Planning index update | `docs/plans/README.md` |

---

## Deliverable

A parent enforcement plan for #2018 that defines the integrated bypass-resistance target state across runtime hooks, commit/push gates, compliance measurement, and rollback/escalation surfaces while cleanly separating already-landed infrastructure from remaining gaps.

---

## Pseudocode

```text
inventory current workflow-enforcement surfaces already implemented
map each issue #2018 acceptance criterion to existing hook/script/test coverage
identify remaining enforcement gaps:
    runtime bypasses still possible
    commit/push gaps still possible
    compliance measurement / alerting gaps
    rollback/escalation gaps
split remaining work into bounded implementation slices
define a parent completion metric that measures whole-system bypass resistance
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/plans/2026-04-13-issue-2018-agent-bypass-resistance-technical-gates.md` | canonical parent plan |
| Update (if needed) | `docs/governance/TRUST-ARCHITECTURE.md` | align target-state language |
| Update | `docs/plans/README.md` | add plan row |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_parent_plan_maps_existing_gates | plan accounts for already-implemented hook/commit/push gates | plan + referenced files | explicit mapping |
| test_parent_plan_identifies_remaining_gaps | plan distinguishes landed enforcement from missing work | plan content | concrete gap list |
| test_parent_plan_splits_work_into_bounded_slices | parent issue does not remain monolithic | plan content | bounded child workstreams |
| test_parent_plan_defines_system_level_success_metric | plan defines measurable bypass-resistance outcome | plan content | explicit target metrics |

---

## Acceptance Criteria

- [ ] Canonical local plan exists for #2018.
- [ ] Plan maps existing enforcement infrastructure to the issue’s acceptance criteria.
- [ ] Plan identifies the remaining gaps that still allow bypass.
- [ ] Plan defines bounded implementation slices instead of one monolithic enforcement blob.
- [ ] Plan defines measurable system-level success criteria.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Subagent review | MINOR | Parent-integrator role is sound; rollback scope and issue-tree mapping should be tightened during implementation |

**Overall result:** MINOR (approval-ready)

Revisions made based on review:
- none required for approval readiness; findings are implementation-time refinements rather than blockers

---

## Risks and Open Questions

- **Risk:** issue #2018 may overlap heavily with other enforcement issues; the plan must act as a parent integrator, not a duplicate implementation ticket.
- **Open:** should rollback remain a hard requirement in this issue, or be explicitly split into a downstream child issue if current infra lacks safe automatic rollback semantics?

---

## Complexity: T3

**T3** — parent enforcement architecture/roadmap issue spanning multiple hooks, scripts, metrics, and governance surfaces.
