# Archived Skill: `mixed-ops-vs-repo-fix-plan-boundary`

Original path: `/home/vamsee/.hermes/skills/workspace-hub/mixed-ops-vs-repo-fix-plan-boundary`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub/mixed-ops-vs-repo-fix-plan-boundary`
Consolidation date: 2026-04-29

---

---
name: mixed-ops-vs-repo-fix-plan-boundary
description: Plan mixed operational-vs-repo remediation issues by proving live-state classification first, then only proposing code changes for confirmed repo-owned failure paths.
version: 1.0.0
category: workspace-hub
tags: [planning, operations, cron, diagnosis, github-issues, review]
---

# Mixed Ops vs Repo Fix Plan Boundary

Use when an issue blends two possibilities:
1. an operational/live-environment problem
2. a repo-owned code/config defect

Examples:
- cron job missing evidence logs
- scheduled task may be not installed vs installed-but-failing
- wrapper script may fail only under real shell/cron conditions

## Core rule

Do not write a plan that assumes a code fix before proving whether the live problem is actually repo-owned.

The plan must first classify the live state, then branch:
- diagnosis-only / operator-guidance outcome
- repo-code remediation outcome

## Required planning pattern

### 1. Capture a reviewable live-state artifact

Create a durable artifact under `docs/reports/` showing the real live state.
Examples:
- installed crontab probe
- current task status from live logs
- host-specific environment evidence

This artifact should eliminate at least one branch of ambiguity.

### 2. Narrow the failure branches explicitly

Write the remaining branches in the plan, for example:
- not installed
- installed but not firing
- installed and failing after launch

If one branch is already eliminated by evidence, say so explicitly.

### 3. Add an explicit stop condition

The plan must say:
- If hermetic reproduction does NOT show a repo-owned defect, stop at diagnosis + operator guidance.
- Do NOT pretend a repo patch solved the host problem.

### 4. Separate operator evidence from product behavior

Do not turn live host inspection into a fake unit test.
Instead:
- treat live probes as reviewable artifacts / operator evidence
- keep repo tests focused on reproducible repo-owned behavior

### 5. Pick one owner for evidence/logging

When the issue involves multiple possible evidence sources, explicitly choose one source of truth.
Example:
- wrapper-owned logging is canonical
- outer cron redirection removed to avoid double-write ambiguity

Avoid plans that leave logging ownership ambiguous.

### 6. Use hermetic shell reproduction for cron-like failures

If shell-ordering or cron environment is suspected:
- reproduce under `/bin/sh`, not just bash
- stub downstream dependencies
- test the exact generated command shape, not only fragments

### 7. Make acceptance criteria branch-aware

Acceptance criteria should distinguish:
- repo-owned failure reproduced and fixed
- operational-only classification recorded with no repo code changes

## Good wording pattern

"If hermetic reproduction shows no repo-owned defect, this issue ends as diagnosis-only with operator guidance and no repo code changes. If hermetic reproduction confirms a repo-owned failure path, then the bounded fix is implemented."

## Pitfalls

- Spending many iterations tightening a plan that still mixes diagnosis and remediation
- Treating operational probes as if they were stable CI tests
- Leaving two logging/evidence owners in place
- Claiming success after a repo patch when the live issue was really host drift
- Failing to capture the live-state artifact in a durable repo path

## When to stop iterating

If repeated adversarial review still says the diagnosis-vs-remediation boundary is unclear after multiple tightening passes, stop forcing that issue forward.
Switch to a different issue and return later with better evidence or a narrower scope.
