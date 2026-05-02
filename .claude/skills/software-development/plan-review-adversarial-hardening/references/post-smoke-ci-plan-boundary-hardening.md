# Archived Skill: `post-smoke-ci-plan-boundary-hardening`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/post-smoke-ci-plan-boundary-hardening`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/post-smoke-ci-plan-boundary-hardening`
Consolidation date: 2026-04-29

---

---
name: post-smoke-ci-plan-boundary-hardening
description: Harden a CI follow-up plan after an initial smoke/unblock issue lands. Use for post-smoke red workflows where later gates surface broad lint/type debt and the plan must stay bounded, evidence-backed, and review-honest.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Post-smoke CI plan boundary hardening

Use when:
- a previous issue already unblocked workflow startup/checkout/smoke
- the workflow is still red at later gates (lint, mypy, coverage, quality-gate)
- the next issue is a bounded CI-hardening tranche, not a repo-wide cleanup

## Goal
Draft a plan that removes the current first post-smoke blockers without pretending to solve all downstream CI debt.

## Required approach

1. Verify the live split from the validating CI run
- Inspect the exact run/job graph, not just issue comments.
- Record which OS/jobs fail at which step.
- Separate:
  - current first blocker(s)
  - later-stage blockers that will surface after those are removed

2. Reproduce locally enough to classify scope
- Run the exact or nearest local validator for the current failing gate(s).
- For typing gates, quantify breadth (example: "286 errors across 39 files") before promising fixes.
- If the failure surface is broad, do not draft a plan that quietly absorbs repo-wide debt.

3. Convert vague “make CI green” wording into an honest bounded tranche
If the issue body is broader than what the evidence supports, the plan must explicitly define:
- what gate is being fixed now
- what red state is allowed to remain
- what later-stage failures must be split or referenced

Do not use vague success phrases like:
- “meaningfully green”
- “advances past blockers”
without naming the exact next expected state.

4. Lock the workflow scope explicitly
For workflow edits, name the exact maintained target list.
Examples:
- exact flake8 path set
- exact mypy target files/modules
- exact dependency-install step(s) that change

Do not leave key questions open in the plan such as:
- “Should lint target X or Y?”
- “Should we install stubs or suppress?”
These must be resolved before plan-review if they affect correctness.

5. Create explicit follow-up issues for excluded surfaces
If you narrow CI scope away from broken but real files, create tracking issues immediately.
Typical excluded surfaces:
- auxiliary `.agent-os/` or tooling scripts
- duplicate non-package module copies
- broad repo-wide type debt already tracked elsewhere

In the plan, cite the concrete follow-up issue numbers, not placeholders or intentions.

6. Make TDD executable for workflow changes
For workflow-scope changes, add a real test artifact path.
Good pattern:
- create a workflow-scope regression test file under tests/
- parse/assert the exact workflow targets
- require a red phase before editing the workflow

Also ensure test commands match repo policy exactly:
- use `uv run` consistently if required by repo contract
- preserve `python -m pytest` / `--noconftest` conventions when the repo defines them

7. Keep review bookkeeping honest
If a review artifact is empty, timed out, or invalid:
- mark it INVALID explicitly
- do not fabricate or summarize findings that do not exist
- do not move to `status:plan-review` until enough valid review evidence exists per repo policy

## Planning checklist
- Exact validating run ID captured
- First blocker per OS/job captured
- Local breadth quantified for current failing gate
- Exact workflow target list defined
- Any exclusion has a follow-up issue number
- TDD workflow-test file path exists in Files to Change
- Static-analysis red phase is explicit, not implied
- Review summary matches actual artifacts on disk
- Success condition is bounded and falsifiable

## Common failure modes
- promising green CI while only fixing the first blocker
- narrowing lint/type scope without tracking excluded files
- using vague close criteria instead of explicit workflow states
- leaving critical implementation branches as “open questions”
- claiming review convergence when artifact files are empty

## Good outcome
A plan that says, in effect:
- “This tranche fixes lint scope X and mypy target Y”
- “These excluded surfaces are tracked in follow-up issues A/B”
- “Broad residual debt remains under issue C”
- “We will only move to plan-review after valid review artifacts support this exact bounded contract”
