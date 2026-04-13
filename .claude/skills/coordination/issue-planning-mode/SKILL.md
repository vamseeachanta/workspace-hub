---
name: issue-planning-mode
description: Mandatory planning workflow for ALL GitHub issues — plan, review, approve, then implement.
version: 3.1.0
author: Workspace Hub
category: coordination
tags: [planning, github, enforcement, workflow, onboarding]
related_skills:
  - engineering-issue-workflow
---

# Issue Planning Mode — Mandatory for ALL Issues

**ALL agents** (Claude, Codex, Gemini, Hermes) MUST follow this workflow for every GitHub issue.
Load this skill before drafting or executing any plan.

Full onboarding guide with step-by-step details: `docs/plans/README.md`

## Workflow Overview

```
Issue → Resource Intel → Draft Plan → Adversarial Review → Post to GH
  → Label status:plan-review → USER APPROVES → Label status:plan-approved
  → Implement (TDD) → Close
```

## Steps

### Step 1: Intake and Resource Intelligence

1. Read the full issue body — scope, acceptance criteria, references
2. Classify complexity: T1 (trivial), T2 (standard), T3 (complex)
3. Search existing code, standards, documents, and prior plans before writing

### Step 2: Draft Plan

Copy template and fill all sections:

```
docs/plans/_template-issue-plan.md  -->  docs/plans/YYYY-MM-DD-issue-NNN-slug.md
```

Required sections: Resource Intelligence Summary, Artifact Map, Deliverable, Pseudocode (T2/T3), Files to Change, TDD Test List, Acceptance Criteria, Risks.

Update the index table in `docs/plans/README.md` with a new row.

Execution discipline for delegated agents:
- If using Claude/Codex/Gemini in parallel worktrees, explicitly anchor the repo/worktree path in the prompt/context and verify the plan file was written in the intended checkout. Do not assume the child agent stayed in the requested worktree.
- After drafting, verify all expected artifacts exist where intended:
  - the plan file path
  - the `docs/plans/README.md` index row
  - no accidental extra rows/issues were inserted
- Keep status conservative as `draft` unless formal review artifacts actually exist under `scripts/review/results/`. GitHub comments alone are useful evidence, but they do not replace the repo’s review-artifact convention.

### Step 3: Adversarial Review

Route the plan to 2+ AI providers for review. Each gives: APPROVE | MINOR | MAJOR.
If any MAJOR: revise and re-review.

Post artifacts to `scripts/review/results/YYYY-MM-DD-plan-NNN-<agent>.md`.

### Step 4: Post and Label

1. Post the plan as a GitHub issue comment
2. Apply label: `gh issue edit NNN --add-label "status:plan-review"`
3. **STOP** — do NOT implement. Wait for user approval.

### Step 6: User Approval

The user (never the implementing agent) approves the plan:
- `gh issue edit NNN --remove-label "status:plan-review" --add-label "status:plan-approved"`
- Creates marker: `.planning/plan-approved/NNN.md`

### Step 5: User Approval

The **user** (not the implementing agent) approves:

```bash
gh issue edit NNN --remove-label "status:plan-review" --add-label "status:plan-approved"
mkdir -p .planning/plan-approved
echo "Approved by: <user>" > .planning/plan-approved/NNN.md
```

Self-approval by the implementing agent is blocked by the plan-approval gate.

### Status precedence and surfacing rules

- If a GitHub issue has multiple `status:*` labels, treat the **latest/most-advanced** state as authoritative. In practice: `status:plan-approved` outranks `status:plan-review`.
- When local plan indexes (for example `docs/plans/README.md`) disagree with newer approval markers or newer GitHub status labels, reconcile to the newer/more-advanced state before deciding whether user approval is still needed.
- Use `.planning/plan-approved/<issue>.md` as the canonical local proof that approval happened.
- Do **not** surface a plan to the user for approval until adversarial plan review is complete and the plan is actually approval-ready. Draft plans with pending/failed review should be revised first, then surfaced.

### Step 6: Implement (TDD)

Only after `status:plan-approved` label AND `.planning/plan-approved/NNN.md` marker exist:
1. Tests FIRST — write tests, confirm they fail
2. Implement minimum code to pass tests
3. Run full test suite — confirm no regressions
4. Self-review against approved plan

### Step 7: Close

- Commit with conventional message referencing the issue
- Push, post summary comment, close issue

## Batch / Overnight Sessions

- Draft plans and label `status:plan-review` — do NOT implement
- Only implement issues already labeled `status:plan-approved`

## Engineering-Critical Issues

Issues with `cat:engineering*` or `cat:data-pipeline` labels require the full
`engineering-issue-workflow` skill (adds cross-review after implementation).

## Enforcement

- **PreToolUse hook**: `.claude/hooks/plan-approval-gate.sh` blocks writes without approval marker
- **Pre-commit hook**: `scripts/enforcement/require-plan-approval.sh --strict` blocks commits without approval
- **Self-approval check**: gate verifies approval was not created in the same session

### Safe paths (no approval needed)

`.planning/`, `docs/plans/`, `docs/governance/`, `docs/reports/`, `docs/standards/`,
and the four top-level agent adapter markdown files

### Emergency bypass

```bash
SKIP_PLAN_APPROVAL_GATE=1  # for Claude Code hook
FORCE_PLAN_GATE=1 git commit  # for pre-commit hook
```

All bypasses are logged.

## References

- Full guide: `docs/plans/README.md`
- Template: `docs/plans/_template-issue-plan.md`
- Hard-stop policy: `docs/standards/HARD-STOP-POLICY.md`
- Engineering workflow: `.claude/skills/coordination/engineering-issue-workflow/SKILL.md`
