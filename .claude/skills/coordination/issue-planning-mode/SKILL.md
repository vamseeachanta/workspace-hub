---
name: issue-planning-mode
description: Enforce the strict issue planning workflow before implementation begins.
version: 3.0.0
author: Claude Code
category: coordination
tags: [planning, github, enforcement, workflow]
---

# Issue Planning Mode

Load this skill before drafting or executing any plan for a GitHub issue.

## Workflow Steps

### Step 1: Create plan file

Copy the template and fill it in:

```
docs/plans/_template-issue-plan.md  -->  docs/plans/YYYY-MM-DD-issue-NNN-slug.md
```

Required sections: Resource Intelligence, Artifact Map, Deliverable, Pseudocode, Files to Change, TDD Test List, Acceptance Criteria.

### Step 2: Apply `status:plan-review` label

```bash
gh issue edit NNN --add-label "status:plan-review"
```

This signals the plan is ready for adversarial review. Do NOT proceed to implementation.

### Step 3: Get adversarial review

Run cross-review via at least one external AI agent (Codex, Gemini, or Hermes):

```bash
/gsd:review --phase N --codex
```

Post review artifacts to `scripts/review/results/YYYY-MM-DD-plan-NNN-<agent>.md`.

### Step 4: Get user approval

The **user** (not the implementing agent) must approve the plan:

```bash
gh issue edit NNN --add-label "status:plan-approved"
```

A human operator then creates the approval marker:

```bash
mkdir -p .planning/plan-approved
echo "Approved by: <user>" > .planning/plan-approved/NNN.md
```

Self-approval by the implementing agent is blocked by the plan-approval gate.

### Step 5: Implement

Only after `status:plan-approved` label exists AND `.planning/plan-approved/NNN.md` marker exists may implementation begin. The `plan-approval-gate.sh` hook enforces this.

## Enforcement

- **PreToolUse hook**: `.claude/hooks/plan-approval-gate.sh` blocks writes to implementation paths without an approval marker
- **Pre-commit hook**: `scripts/enforcement/require-plan-approval.sh --strict` blocks commits of implementation files without plan approval evidence
- **Self-approval check**: The gate verifies the approval marker was not created in the same session as the implementation work

## Safe paths (no approval needed)

These paths can always be written without an approval marker:
- `.planning/` (plan creation)
- `docs/plans/` (plan files)
- `docs/governance/` and `docs/reports/` (governance artifacts)
- `docs/standards/` (standards)
- Top-level harness adapter files (the 4 agent markdown configs)

## Emergency bypass

```bash
SKIP_PLAN_APPROVAL_GATE=1  # for Claude Code hook
FORCE_PLAN_GATE=1 git commit  # for pre-commit hook
```

All bypasses are logged.
