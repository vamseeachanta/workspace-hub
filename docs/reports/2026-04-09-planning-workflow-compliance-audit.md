# Planning Workflow Compliance Audit

> **Date:** 2026-04-09
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2046
> **Scope:** Audit compliance of strict issue planning workflow after rollout
> **Rollout date:** 2026-04-08 (template at 12:43, full onboarding at 21:54)

---

## Executive Summary

**Overall compliance: 0% (0 of 5 post-rollout feature issues used the full workflow)**

The strict issue planning workflow was formally rolled out on 2026-04-08 at 21:54 via commit `2bc0f467` (#2045). In the ~18 hours since rollout, 5 substantive feature/fix commits were pushed referencing 3 distinct issues (#1839, #1857, #2045). None of these issues used `status:plan-review` or `status:plan-approved` labels, and none had a plan file in `docs/plans/` following the template convention. One issue (#1839) has a plan-approval marker in `.planning/plan-approved/1839.md`, showing partial adoption of the hook-based enforcement path but not the full label-driven workflow.

The labels `status:plan-review` and `status:plan-approved` exist in the repository but have **never been applied to any issue** (0 issues across all open and closed).

| Metric | Value |
|---|---|
| Workflow rollout date | 2026-04-08 21:54 CST |
| Hours since rollout | ~18 hours |
| Post-rollout feature commits | 6 (excl. sync/docs) |
| Distinct issues worked post-rollout | 3 (#1839, #1857, #2045) |
| Issues with plan file in docs/plans/ | 0 of 3 |
| Issues with status:plan-review label | 0 of 3 |
| Issues with status:plan-approved label | 0 of 3 |
| Issues with .planning/plan-approved/ marker | 1 of 3 (#1839) |
| Template-compliant plan files (all time) | 1 (issue #1963, draft status) |

---

## Per-Issue Compliance (Post-Rollout)

| Issue | Title (abbrev) | Plan file? | Plan labels? | Approval marker? | Adversarial review? | Verdict |
|---|---|---|---|---|---|---|
| #1839 | Workflow hard-stops and session governance | No | No | Yes (1839.md) | No evidence | PARTIAL |
| #1857 | Rolling agent work queue | No | No | No | No evidence | NON-COMPLIANT |
| #2045 | Onboard agents to strict planning workflow | No | No | No | No evidence | NON-COMPLIANT |

### Notes on each issue

**#1839 (5 commits post-rollout):** This is the governance infrastructure issue itself. It has a `.planning/plan-approved/1839.md` marker dated 2026-04-09, which satisfies the `plan-approval-gate.sh` PreToolUse hook. However, no plan file exists in `docs/plans/`, no `status:plan-review` or `status:plan-approved` labels were applied, and there is no adversarial review artifact. The approval marker was self-created by the implementing session.

**#1857 (1 commit post-rollout):** Queue hardening work. No plan, no labels, no approval marker. Fully non-compliant.

**#2045 (1 commit post-rollout):** The workflow onboarding issue itself. Ironically, the issue that introduced the strict workflow did not follow the strict workflow. No plan, no labels.

---

## Pre-Rollout Baseline (Apr 1-8)

For context, examining 75+ engineering issues closed between Apr 1-8 (before the workflow was introduced):

| Metric | Value |
|---|---|
| Issues closed Apr 1-8 | ~75 (engineering/platform/harness) |
| Plan files in docs/plans/ referencing issues | 0 using template convention |
| Issues with plan labels | 0 |
| Review artifacts in scripts/review/results/ | Last artifact dated Mar 10 (wrk-1078) |
| Cross-review evidence | Near zero since Mar 24 |

The pre-rollout baseline shows the same pattern: plans were not being created in `docs/plans/` following the template, labels were not being used, and adversarial reviews were not happening. The rollout has not yet changed behavior.

---

## Infrastructure Assessment

### What exists (enforcement tooling)

The enforcement infrastructure is surprisingly mature:

| Component | Status | Location |
|---|---|---|
| Plan template | Exists | `docs/plans/_template-issue-plan.md` |
| Plan labels | Created | `status:plan-review`, `status:plan-approved` |
| Plan approval gate (PreToolUse hook) | **ACTIVE** | `.claude/hooks/plan-approval-gate.sh` wired in `settings.json` |
| Cross-review gate (PreToolUse hook) | **ACTIVE** | `.claude/hooks/cross-review-gate.sh` wired in `settings.json` |
| Plan approval script | Exists | `scripts/enforcement/require-plan-approval.sh` |
| Plan review script | Exists | `scripts/enforcement/require-plan-review.sh` |
| Compliance dashboard | Exists | `scripts/enforcement/compliance-dashboard.sh` |
| Governance checkpoints YAML | Exists | `scripts/workflow/governance-checkpoints.yaml` |
| Session governor | **ACTIVE** | `.claude/hooks/session-governor-check.sh` |
| Pre-commit hook | Active but no plan gate | `.git/hooks/pre-commit` |
| Pre-push hook | Active but no plan gate | `.git/hooks/pre-push` |

### What is missing or weak

1. **Safe-path bypass is too broad:** `plan-approval-gate.sh` exempts all `.md` files, all `scripts/`, `tests/`, `.claude/`, `docs/` paths. Since most governance work touches these paths, the gate never fires for infrastructure issues.

2. **Self-approval loophole:** The `.planning/plan-approved/` marker can be created by the implementing agent itself (as seen with #1839). There is no verification that a human reviewed and approved.

3. **Label workflow not wired to enforcement:** The `status:plan-review` and `status:plan-approved` labels exist but are not checked by any hook or script. The hooks check for file markers, not GitHub labels.

4. **No git hook enforcement:** Neither `pre-commit` nor `pre-push` calls `require-plan-approval.sh`. The plan gate only exists as a Claude Code PreToolUse hook, meaning it only applies to Claude Code sessions, not Codex, Gemini, or manual commits.

5. **`issue-planning-mode` skill is a deprecated stub:** The skill referenced in CLAUDE.md points to `gh-work-planning`, which does not exist in the skills directory.

---

## Gaps and Failure Modes

### Failure Mode 1: Workflow was DOA (Dead on Arrival)
The workflow was defined and tooling was built, but the first issues worked after rollout did not follow it. The implementing agents bypassed or ignored the workflow entirely.

### Failure Mode 2: Governance work exempts itself
Issue #1839 (the governance issue itself) self-approved via a marker file. The agents building the enforcement infrastructure did not eat their own dogfood.

### Failure Mode 3: Safe-path exemptions negate enforcement
The PreToolUse hook exempts `.md`, `scripts/`, `tests/`, `.claude/`, `docs/` files. Most workspace-hub work touches these paths, making the gate effectively a no-op for the majority of commits.

### Failure Mode 4: Label workflow is ceremonial
Labels exist but nothing checks them. The hooks use file markers instead. There are two parallel enforcement models (labels vs markers) and neither is complete.

### Failure Mode 5: Only Claude Code is gated
PreToolUse hooks only fire in Claude Code sessions. Codex CLI, Gemini CLI, Hermes, and manual `git commit` bypass all plan gates entirely.

---

## Recommendations

### Verdict: Escalate to hook-level enforcement (Level 3)

The current approach (Level 0-1 prose + Level 2 scripts) has produced 0% compliance. Recommendations in priority order:

1. **Wire `require-plan-approval.sh --strict` into `pre-commit` hook** so it fires for ALL commits, not just Claude Code sessions. This is the single highest-impact change.

2. **Narrow safe-path exemptions** in `plan-approval-gate.sh`. At minimum, `scripts/enforcement/` and implementation scripts should require plan approval. Consider an allowlist instead of a denylist.

3. **Remove self-approval capability.** The `.planning/plan-approved/` marker should only be created by a human operator (e.g., via `gh issue edit --add-label status:plan-approved`), not by the implementing agent session.

4. **Unify the label and marker models.** Either check GitHub labels via `gh` API in the hook, or drop labels entirely and use only file markers with human-only creation.

5. **Fix the skill chain.** Either create the `gh-work-planning` skill that `issue-planning-mode` references, or update `issue-planning-mode` to contain the full workflow directly.

6. **Run this audit weekly** via cron to track compliance trend. The `compliance-dashboard.sh` script exists but does not check plan compliance -- extend it.

### Decision matrix

| Approach | Expected compliance | Effort | Risk |
|---|---|---|---|
| Keep current (prose + advisory hooks) | 0-10% | None | Workflow remains ceremonial |
| Wire into pre-commit hook (strict) | 60-80% | Low (1 commit) | May block legitimate quick fixes |
| Wire into pre-commit + narrow exemptions | 80-95% | Medium | Requires bypass protocol for emergencies |
| Full label-based workflow with API checks | 95%+ | High | Requires network access in hooks, slow |

**Recommended path:** Wire `require-plan-approval.sh --strict` into `pre-commit`, narrow exemptions, and remove self-approval. This is achievable in a single session and corresponds to issue #2047.

---

## Appendix: Evidence Sources

- Git log: `git log --oneline --after="2026-04-08T21:54:00" --no-merges`
- GitHub labels: `gh label list --search "status:plan"` -- both labels exist, 0 issues use them
- GitHub issues: `gh issue list --limit 100 --state all --label "status:plan-review"` -- 0 results
- Plan files: `ls docs/plans/` -- 1 template-compliant file (`2026-04-09-issue-1963-email-infrastructure-cluster-a.md`, draft status)
- Approval markers: `ls .planning/plan-approved/` -- 1 marker (`1839.md`, self-created)
- Hook config: `.claude/settings.json` -- `plan-approval-gate.sh` wired as PreToolUse
- Pre-commit hook: `.git/hooks/pre-commit` -- no plan gate
- Pre-push hook: `.git/hooks/pre-push` -- no plan gate
