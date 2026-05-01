# Archived Skill: `bounded-post-smoke-ci-hardening-plan`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/bounded-post-smoke-ci-hardening-plan`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/bounded-post-smoke-ci-hardening-plan`
Consolidation date: 2026-04-29

---

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

### 4. Prefer deterministic workflow verification over brittle pytest tests for YAML structure
Do not create pytest files just to parse workflow YAML unless the repo explicitly wants that.

Default pattern:
- start with deterministic inspection commands while drafting the plan
- if adversarial review keeps flagging ad hoc inspection as too weak, promote the contract to a persisted verifier script such as `scripts/ci/verify_<workflow>.py`

The persisted verifier should check only the bounded workflow contract, for example:
- both flake8 commands target the intended paths
- smoke step still appears before lint/mypy
- smoke command remains single-line / shell-neutral
- the exact targeted mypy tranche is still present

If you choose the persisted-script route, make the plan explicit about:
- what current-main red state the verifier would catch
- whether the script is only a local verification artifact or also wired into CI/pre-commit later
- why that enforcement level is sufficient for the bounded tranche

This is usually less brittle than workflow-specific pytest tests and stronger than one-off inline inspection snippets.

### 5. Make local validation truly isolated
If the repo injects global pytest addopts (coverage gates, junit, etc.), local TDD commands can fail for unrelated reasons.
Use:
- `uv run python -m pytest ... --noconftest -o addopts=`
for isolated red/green checks.

If the workflow runs only unit-marked tests, make the plan require the affected tests to carry the correct marker, e.g.:
- `pytestmark = pytest.mark.unit`
Otherwise the local red/green test can pass while the workflow silently skips it.

If local mypy needs extra stubs only for the targeted verification, use:
- `uv run --with types-PyYAML mypy ... --follow-imports=silent`
or the equivalent needed package/flags actually proven locally.

If flake8 is not directly spawnable under `uv run flake8 ...`, prefer the reproducible form:
- `uv run --with flake8 python -m flake8 ...`
Record the exact command that reproduced the blocker and the exact command expected to go green.

Do not claim a local validation path is reproducible unless the local command includes the same extra dependency assumptions and flags the plan relies on.

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
- explicit statement of any temporary gate narrowing tradeoff (for example, targeted mypy files instead of broad `src/`) and where re-expansion debt is tracked
- explicit note on likely next blocker after the current tranche (for example coverage thresholds) so "not fully green yet" is disclosed up front
- an explicit CI-parity note distinguishing isolated local red/green commands from the real workflow invocation
- at least one attested real-workflow command/result for the likely next blocker, not just a hypothetical warning

### CI-parity hardening rule
If you use isolated local pytest commands such as `--noconftest -o addopts=` for TDD, the plan must also say what real workflow command will still run in CI and what divergence remains. Do not let review readers infer equivalence when there is none.

Required pattern:
1. keep isolated local commands for bounded red/green work
2. separately capture the real workflow command shape (markers, conftest/addopts, coverage thresholds)
3. state explicitly that local green does not imply CI green when the workflow still enforces broader coverage or different discovery behavior

Example of useful attested next-blocker evidence:
- `pytest tests/unit/ --cov=src --cov=. --cov-report=term-missing --cov-fail-under=80 --verbose -m unit`
- result: fails on coverage threshold even after the current lint/type tranche

This evidence should be folded into the plan so the success contract reads as:
- remove the current first blocker(s)
- expose/record the next real blocker
- do not imply end-to-end green if the real workflow still predictably fails at coverage

### Persisted verifier enforcement rule
If adversarial review rejects ad hoc YAML inspection and pushes you toward a persisted verifier script (for example `scripts/ci/verify_<workflow>.py`), the plan must specify the verifier's enforcement level.

Do not stop at "we will add a verifier script." Also say one of:
- local-only verification artifact for this tranche, with rationale
- wired into CI in the same issue
- wired into pre-commit in the same issue
- deferred enforcement, with an explicit follow-up issue

Also define the verifier's concrete red state on current main. Example assertions:
- wrong flake8 target scope
- smoke step ordered after lint/mypy
- shell-specific multiline smoke command reintroduced
- mypy target widened/narrowed away from the approved tranche

Without this, review will correctly treat the verifier as under-specified.

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
