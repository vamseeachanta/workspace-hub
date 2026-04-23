---
name: bounded-post-smoke-ci-hardening-plan
description: Plan post-smoke CI hardening as a bounded blocker-removal tranche instead of overpromising full green. Includes issue-body alignment, follow-up split rules, honest review bookkeeping, and reliable local validation commands.
version: 1.0.0
author: Hermes Agent
---

# Bounded Post-Smoke CI Hardening Plan

Use when a repo has already cleared the initial smoke/unblock milestone, but CI is still red on later gates (lint, type check, coverage, quality gate).

## When to use
- A prior issue already unblocked checkout / install / smoke
- The next issue is about "post-smoke hardening"
- Full repo-wide green is not realistic in one bounded tranche
- Adversarial review is likely to reject vague "make CI green" language

## Core rule
Do not promise full CI green unless the evidence supports it.
Plan the next issue as:
1. remove the current first blocker(s)
2. expose the next real failure surface
3. track broader debt explicitly in follow-up issues

## Required planning steps

### 1. Verify the first blocker by OS/job
Use the live CI run and record exactly where each lane stops.
Example split:
- linux/macos stop first at flake8
- windows stops first at mypy
- quality gate is red only because upstream jobs are red

This creates the correct bounded tranche.

### 2. Align the GitHub issue body to the bounded tranche
If the existing issue body still sounds like "restore workflow to green", edit it before pushing the plan to review.
Make the issue explicitly say:
- this tranche removes the current first post-smoke blockers
- this tranche is expected to expose the next failure surface
- broad repo-wide lint/type/coverage debt is not silently absorbed here

If the issue body and plan disagree, adversarial review will keep returning MAJOR.

### 3. Split broad debt into explicit follow-ups
Before claiming excluded surfaces are safe to omit, create or link follow-up issues.
Typical examples:
- broad repo-wide mypy debt
- auxiliary `.agent-os/` or `scripts/` Python files excluded from package lint
- duplicate non-package helper copies outside the maintained surface

Embed live issue evidence for those follow-ups in the plan, not just prose references.

### 4. Prefer deterministic workflow inspection over brittle pytest tests for YAML structure
Do not create pytest files just to parse workflow YAML unless the repo explicitly wants that.
Instead, use deterministic inspection commands in the TDD/acceptance contract.
Example pattern:
- verify both flake8 commands now target the intended paths
- verify smoke step still appears before lint/mypy
- verify smoke command remains single-line / shell-neutral

This is usually less brittle than workflow-specific pytest tests.

### 5. Make local validation truly isolated
If the repo injects global pytest addopts (coverage gates, junit, etc.), local TDD commands can fail for unrelated reasons.
Use:
- `uv run python -m pytest ... --noconftest -o addopts=`
for isolated red/green checks.

If local mypy needs extra stubs only for the targeted verification, use:
- `uv run --with types-PyYAML mypy ...`
or the equivalent needed package.

Do not claim a local validation path is reproducible unless the local command includes the same extra dependency assumptions the plan relies on.

### 6. Be honest about review artifacts
Empty review files are invalid artifacts, not completed reviews.
In the plan summary:
- name valid provider artifacts accurately
- mark empty artifacts as invalid
- do not invent findings for empty files
- do not move to `status:plan-review` until the review gate you claim is actually satisfied

## Recommended acceptance shape
A good bounded post-smoke CI plan should require:
- issue body aligned to bounded scope
- exact first-blocker removal target(s)
- exact workflow edits named
- exact local validation commands
- explicit recording of the next exposed failure surface after the blocker-removal tranche
- explicit linkage to follow-up issues for excluded broad debt

## Reusable command patterns

### Isolated pytest
`cd <repo> && uv run python -m pytest <path> --noconftest -o addopts= -q`

### Local targeted mypy with ad hoc stub dependency
`cd <repo> && uv run --with types-PyYAML mypy <file1> <file2> --ignore-missing-imports`

### Deterministic workflow inspection
Use a short `uv run python - <<'PY' ... PY` or equivalent assertion block to check:
- exact lint target paths
- smoke-before-lint ordering
- shell-neutral smoke command shape

## Red flags caught in review
If you see any of these, rewrite before plan-review:
- issue body says "green the workflow" but plan only removes first blockers
- plan excludes surfaces without linked follow-up issues
- local pytest commands still inherit repo-wide coverage gates
- review summary cites findings from empty artifact files
- acceptance criteria only say "advance past blockers" without requiring capture of the next failure surface
