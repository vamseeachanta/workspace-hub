# Adversarial Re-Review Request: Issue #2018

You are an independent adversarial reviewer. This plan was revised after prior MAJOR findings. Evaluate the revised plan on its current text only. Find any remaining gaps, risks, missing edge cases, unclear scope boundaries, or workflow/governance violations. Do NOT rubber-stamp.

Return verdict as one of: APPROVE, MINOR, MAJOR.

Required output format:
1. Verdict
2. Ready for user approval: Yes/No
3. Retrieval adequacy: adequate/insufficient
4. Top blockers (numbered)
5. Critical findings
6. High findings
7. Medium findings
8. Low findings
9. Required revisions before user approval

Context:
- Repository: workspace-hub
- Review type: plan-stage adversarial re-review
- Focus on whether the revised plan is now actually approval-ready.

GitHub issue metadata:
- Issue: #2018
- Title: feat: agent bypass resistance -- enforce workflow with technical gates, not text instructions
- URL: https://github.com/vamseeachanta/workspace-hub/issues/2018
- Labels: priority:high, cat:engineering, cat:harness, domain:workflow, status:plan-review

GitHub issue body:
## Mission: Agents must follow the workflow without exceptions

### Current State
- Review compliance at 4% (#2012)
- Text-based instructions in CLAUDE.md and AGENTS.md get bypassed over time
- Agents (all of them) act like humans who want to get shit done and skip the hard parts
- Plan gate and commit gate testing in progress (#1876)

### Core Insight
> "Even hermes is not confident LLM text will make it adhere to it -- overtime agents just bypass"

The problem is fundamental: LLMs optimize for task completion, not process adherence. Telling an agent to follow rules is like telling a developer to write tests -- it happens sometimes, not always.

### Required: Infrastructure Enforcement

Text instructions MUST be backed by technical enforcement:

1. **Pre-commit hook** -- blocks commits without plan approval marker
2. **CI gate** -- rejects PRs without cross-review evidence
3. **Agent prefill** -- injects workflow constraints into session context
4. **Compliance dashboard** -- tracks and alerts on violations
5. **Auto-rollback** -- reverts commits that bypass gates

### Why This Matters
Without enforcement mode, every single artifact produced is potentially lower quality. The 3-agent review system only works if agents actually use it.

### Acceptance Criteria
- [ ] Pre-commit hook blocks 100% of non-compliant commits
- [ ] CI pipeline rejects PRs without review sign-off
- [ ] Compliance rate > 80% (from current 4%)
- [ ] Zero engineering commits without plan review for 30+ days
- [ ] All agents tested: Hermes, Claude Code, Codex, Gemini

### Notes
- #1876 covers the implementation details
- #2012 tracks the compliance audit backlog
- This is the PRIORITY for any serious engineering work

### Related
- #1876 (Enforce engineering workflow via Hermes prefill + Claude Code hooks)
- #2012 (Review backlog audit - 4% compliance)
- docs/standards/HARD-STOP-POLICY.md
- docs/standards/AI_REVIEW_ROUTING_POLICY.md

Plan under review (docs/plans/2026-04-13-issue-2018-agent-bypass-resistance-technical-gates.md):
# Plan for #2018: agent bypass resistance -- enforce workflow with technical gates, not text instructions

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-04-13
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2018
> **Review artifacts:** scripts/review/results/2026-04-14-plan-2018-codex.md | scripts/review/results/2026-04-14-plan-2018-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `.claude/hooks/plan-approval-gate.sh` is the runtime write gate and currently permits several bypass-sensitive environment variables and broad safe-path exemptions.
- Found: `scripts/enforcement/require-plan-approval.sh` is the pre-commit gate and currently excludes multiple control-plane paths from implementation detection.
- Found: `scripts/enforcement/require-review-on-push.sh` is the push/review gate and must remain in the effective fail-fast chain.
- Found: `.claude/hooks/cross-review-gate.sh` is a separate review-enforcement surface that this parent plan must account for instead of treating review as push-only.
- Found: `.github/workflows/enforcement-gate.yml` is the CI/PR enforcement surface and is required retrieval for any claim of end-to-end bypass resistance.
- Found: `scripts/enforcement/compliance-dashboard.sh` already exists as an advisory compliance surface; this plan must explicitly decide whether dashboarding remains advisory or becomes a stronger control signal.
- Found: `tests/work-queue/test_session_governor.py` already covers parts of runtime and review-gate behavior but does not, by itself, prove full bypass resistance.
- Found: issue comments and related governance issues show the repo already has landed enforcement slices, but the parent issue still lacks a clean bypass matrix and closure criteria.

### Standards
- `docs/standards/HARD-STOP-POLICY.md` — hard-stop sequencing and no-implementation-before-approval policy.
- `docs/standards/AI_REVIEW_ROUTING_POLICY.md` — default three-agent adversarial review expectations.
- `docs/plans/README.md` — planning workflow contract and required review/approval ordering.
- `AGENTS.md` — repo hard-gate order and TDD-first expectation.

### Documents consulted
- GitHub issue #2018 — required control set, acceptance criteria, and governance intent.
- GitHub issue #1839 — umbrella governance/enforcement context this issue must preserve.
- `.claude/hooks/plan-approval-gate.sh`
- `scripts/enforcement/require-plan-approval.sh`
- `scripts/enforcement/require-review-on-push.sh`
- `.claude/hooks/cross-review-gate.sh`
- `.github/workflows/enforcement-gate.yml`
- `scripts/enforcement/compliance-dashboard.sh`
- `docs/governance/TRUST-ARCHITECTURE.md`
- `docs/standards/HARD-STOP-POLICY.md`
- `docs/standards/AI_REVIEW_ROUTING_POLICY.md`
- `tests/work-queue/test_session_governor.py`

### Gaps identified
- No single plan artifact currently maps each live enforcement surface to known bypasses, desired end state, owner issue, and required tests.
- Current plan review evidence shows unresolved scope around rollback and agent bootstrap/prefill validation.
- Existing tests are not yet a true bypass-resistance suite across runtime hook, commit, push, CI, and agent surfaces.
- Sibling issue boundaries are not yet explicit enough to prevent #2018 from being closed by documentation alone.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-13-issue-2018-agent-bypass-resistance-technical-gates.md` |
| Runtime plan gate | `.claude/hooks/plan-approval-gate.sh` |
| Commit gate | `scripts/enforcement/require-plan-approval.sh` |
| Push/review gate | `scripts/enforcement/require-review-on-push.sh` |
| Cross-review hook | `.claude/hooks/cross-review-gate.sh` |
| CI gate | `.github/workflows/enforcement-gate.yml` |
| Compliance dashboard | `scripts/enforcement/compliance-dashboard.sh` |
| Existing governance tests | `tests/work-queue/test_session_governor.py` |
| Planned new/expanded tests | `tests/enforcement/` or `tests/work-queue/` |
| Trust contract | `docs/governance/TRUST-ARCHITECTURE.md` |
| Planning index update | `docs/plans/README.md` |

---

## Deliverable

A parent enforcement plan for #2018 that enumerates all material bypass paths across runtime hooks, commit/push gates, CI, approval-state signaling, and agent bootstrap surfaces; assigns each path to a concrete closure or delegated child issue; and defines the functional tests required before the repo can claim meaningful bypass resistance.

---

## Pseudocode

```text
retrieve all live enforcement surfaces and current issue comments
build bypass matrix with rows for:
    runtime hook
    pre-commit
    pre-push
    cross-review hook
    CI / PR gate
    approval-marker / label-state spoofing
    env-var bypasses
    safe-path abuse
    manual git/manual shell path
    agent bootstrap / prefill for Hermes, Claude, Codex, Gemini
for each row:
    record current control
    record known bypass / weakness
    define desired target state
    define owning issue or child issue
    define falsifiable test / evidence required
resolve whether rollback is implemented here or explicitly delegated to a mandatory child issue
define sibling-boundary table against #1839 and adjacent enforcement issues
define parent completion criteria based on closed bypass paths and passing tests, not document existence
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Rewrite | `docs/plans/2026-04-13-issue-2018-agent-bypass-resistance-technical-gates.md` | make the parent plan evidence-backed and bypass-oriented |
| Update | `docs/plans/README.md` | keep plan status/index aligned |
| Update (if needed) | `docs/governance/TRUST-ARCHITECTURE.md` | align wording only if runtime semantics change |
| Planned implementation surface | `.claude/hooks/plan-approval-gate.sh` | runtime hook hardening |
| Planned implementation surface | `scripts/enforcement/require-plan-approval.sh` | pre-commit hardening |
| Planned implementation surface | `scripts/enforcement/require-review-on-push.sh` | push/review hardening |
| Planned implementation surface | `.claude/hooks/cross-review-gate.sh` | review-enforcement alignment |
| Planned implementation surface | `.github/workflows/enforcement-gate.yml` | CI gate alignment |
| Planned implementation surface | `scripts/enforcement/compliance-dashboard.sh` | compliance measurement role clarified |
| Planned test surface | `tests/work-queue/test_session_governor.py` or `tests/enforcement/` | functional bypass-resistance tests |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_runtime_write_blocked_without_marker` | runtime write gate blocks non-safe implementation writes without approval | write attempt fixture | blocked |
| `test_control_plane_safe_path_cannot_mask_bypass` | control-plane path exemptions cannot be abused to bypass enforcement intent | path fixture touching exempt/control-plane paths | explicit allowed/blocked result |
| `test_precommit_blocks_unapproved_implementation_change` | strict pre-commit gate blocks qualifying changes without approval evidence | staged change fixture | commit blocked |
| `test_prepush_blocks_missing_review_evidence` | push gate blocks missing review evidence | push fixture | push blocked |
| `test_ci_gate_rejects_missing_plan_or_review` | PR/CI gate enforces same invariants as local gates | CI fixture | CI failure |
| `test_env_var_bypass_behavior_is_explicit` | env-var bypasses are either rejected or explicitly scoped/logged | env-var matrix | deterministic behavior |
| `test_self_approved_marker_spoofing_rejected` | stale/self-approved marker spoofing does not satisfy gate | spoofed marker fixture | rejected |
| `test_agent_bootstrap_surfaces_receive_constraints` | Hermes/Claude/Codex/Gemini bootstrap surfaces carry workflow constraints | provider-specific config/prompt fixtures | explicit references present |
| `test_rollback_behavior_or_delegation_is_explicit` | rollback is either implemented/testable or formally delegated to a mandatory child issue | rollback decision fixture | explicit pass/fail outcome |

---

## Acceptance Criteria

- [ ] Bypass matrix exists and covers runtime hook, pre-commit, pre-push, cross-review hook, CI, approval marker/label drift, env-var bypasses, safe-path abuse, manual git path, and agent bootstrap surfaces.
- [ ] Each bypass row has a current control, known weakness, desired target state, owner issue, and required test/evidence.
- [ ] Rollback is no longer an open question: it is either concretely designed here or explicitly delegated to a mandatory child issue before approval.
- [ ] Parent/sibling issue boundary table exists and makes clear what #2018 still owns after related enforcement issues.
- [ ] Functional enforcement tests are defined for runtime, git, CI, env-var, spoofing, and provider bootstrap behavior.
- [ ] Plan review state is fully reconciled with review artifacts and GitHub labels before implementation begins.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Codex | MAJOR | Plan is too inventory/document centric; missing bypass matrix, missing live retrieval from CI/review/dashboard surfaces, rollback unresolved |
| Gemini | MAJOR | Plan acts like meta-plan instead of implementation-grade enforcement plan; missing agent-prefill, CI, rollback, and functional TDD |

**Overall result:** MAJOR — not approval-ready

Revisions required before approval:
- replace inventory framing with bypass-closure framing
- add missing live enforcement retrieval
- replace document-only TDD with functional enforcement tests
- resolve rollback and sibling-boundary ownership

---

## Risks and Open Questions

- **Risk:** CI/local parity can drift even if local hooks look strict; CI must be part of the planned control set.
- **Risk:** broad safe-path or env-var exceptions can leave nominally “strict” enforcement advisory in practice.
- **Open:** none for approval readiness; rollback and ownership must be resolved before this plan returns to review.

---

## Complexity: T3

**T3** — cross-surface enforcement/governance plan spanning runtime hooks, git gates, CI, compliance measurement, and multi-agent bootstrap behavior.


Review questions — address ALL:
1. Did the revision resolve the prior MAJOR blockers in a concrete way?
2. Is retrieval now adequate for the issue class?
3. Are files-to-change, TDD, acceptance criteria, and risks concrete and falsifiable?
4. Are there still unresolved scope/governance/status inconsistencies that should block approval?
5. Should this revised plan now be approved, revised again, or split?
