---
name: artifact-verification
description: Orchestrator checklist to verify worker outputs against the approved plan before accepting artifacts. Phase 2 of orchestrator/worker context enforcement (#2020).
version: 1.0.0
category: coordination
tags: [orchestrator, worker, verification, governance, artifacts]
related_skills:
  - cross-review-policy
  - issue-planning-mode
  - engineering-issue-workflow
issue_ref: "#2020"
---

# Artifact Verification — Orchestrator Checklist

When a worker (subagent, Codex, Gemini, or parallel terminal) returns results,
the orchestrator MUST verify those results against the approved plan before
accepting them. This skill provides the verification protocol.

## Why This Exists

Workers optimize for task completion, not plan adherence. Without verification:
- Workers skip optional deliverables that the plan required
- Workers modify files outside their assigned scope (contention risk)
- Workers produce code that passes tests but drifts from the spec
- Orchestrators rubber-stamp results because the output "looks right"

## When to Use

- After any worker/subagent returns results
- After overnight batch runs (morning review)
- Before merging worker-produced branches
- Before closing a GitHub issue completed by a worker

## Verification Checklist

For each worker output, the orchestrator checks:

### 1. Scope Alignment

- [ ] Files changed match the plan's "Files to Change" list
- [ ] No files outside the worker's assigned scope were modified
- [ ] No files from other workers' negative write boundaries were touched

### 2. Acceptance Criteria

- [ ] Each acceptance criterion from the approved plan is satisfied
- [ ] Evidence exists for each criterion (test output, file content, command result)
- [ ] No acceptance criteria were silently dropped

### 3. Test Coverage

- [ ] Tests were written/updated as specified in the plan
- [ ] Tests pass (verify via `uv run pytest` or equivalent)
- [ ] Test names and coverage match the plan's TDD test list

### 4. Artifact Completeness

- [ ] All deliverables listed in the plan are present
- [ ] Documentation updates (if required by plan) are included
- [ ] Commit messages follow conventional format and reference the issue

### 5. No Unplanned Side Effects

- [ ] No unrelated files were modified (check `git diff --stat`)
- [ ] No new dependencies added that weren't in the plan
- [ ] No configuration changes outside plan scope

## Verification Markers

After verification passes, the orchestrator creates a marker:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
ISSUE=NNN
mkdir -p "$REPO_ROOT/.planning/verified"
cat > "$REPO_ROOT/.planning/verified/$ISSUE.md" << 'MARKER'
# Verification: Issue #NNN

- verified_by: <orchestrator agent or user>
- verified_at: <timestamp>
- worker: <worker agent identity>
- plan: docs/plans/YYYY-MM-DD-issue-NNN-slug.md
- verdict: PASS | PARTIAL | FAIL

## Checklist Results
- [x] Scope alignment
- [x] Acceptance criteria
- [x] Test coverage
- [x] Artifact completeness
- [x] No unplanned side effects

## Notes
<any deviations, partial passes, or follow-up items>
MARKER
```

### Verification Verdicts

| Verdict | Meaning | Action |
|---------|---------|--------|
| **PASS** | All checklist items satisfied | Accept artifacts, proceed to merge/close |
| **PARTIAL** | Most items pass, minor gaps identified | Accept with noted follow-ups |
| **FAIL** | Critical items missing or wrong | Reject, provide specific feedback to worker |

### On FAIL: Feedback Protocol

When verification fails, the orchestrator provides specific feedback:

1. List each failed checklist item with the expected vs actual result
2. Reference the exact plan section that was not met
3. Do NOT give generic rejection ("this doesn't meet the spec")
4. Re-dispatch the worker with the feedback and the relevant plan section

## Integration with Existing Workflow

This skill fits between the implementation step and the close step of
`issue-planning-mode`:

```
Plan Approved --> Worker Implements --> ARTIFACT VERIFICATION --> Cross-Review --> Close
```

The verification step is distinct from cross-review:
- **Verification**: Did the worker build what the plan specified? (scope check)
- **Cross-review**: Is what was built correct and well-engineered? (quality check)

## Overnight Batch Integration

For overnight batch runs with multiple terminals:

1. Each terminal produces its output
2. Morning review runs this checklist for each terminal's output
3. Verification markers are created for each terminal
4. Only verified outputs proceed to cross-review and merge

## References

- Orchestrator-worker methodology: `docs/methodology/orchestrator-worker.md`
- Plan approval gate: `.claude/hooks/plan-approval-gate.sh`
- Cross-review policy: `.claude/skills/coordination/cross-review-policy/SKILL.md`
- Session governance: `docs/governance/SESSION-GOVERNANCE.md`
