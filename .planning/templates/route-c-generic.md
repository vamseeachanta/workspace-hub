<!-- Current workflow: create/update GitHub issue #NNN, copy this template into docs/plans/YYYY-MM-DD-issue-NNN-slug.md, post it for review with status:plan-review, and after user approval create .planning/plan-approved/NNN.md and add status:plan-approved. -->

---
wrk_id: WRK-NNN
title: "<short title>"
domain: generic
complexity: medium
created_at: YYYY-MM-DD
target_repos: []
standards: []
---

## Mission

One sentence: what this WRK delivers and why it matters.

## What

- Deliverable 1 (placeholder)
- Deliverable 2 (placeholder)
- Deliverable 3 (placeholder)

## Why

Business or technical rationale for this work (placeholder). Explain the need, the risk of not doing it,
and any dependencies that make now the right time.

## Acceptance Criteria

- [ ] AC-1: placeholder criterion
- [ ] AC-2: placeholder criterion
- [ ] AC-3: placeholder criterion
- [ ] AC-4: placeholder criterion

## Domain Checklist

- [ ] Regulatory/code compliance identified (list applicable standards)
- [ ] Test strategy defined (unit, integration, validation levels)
- [ ] Data sources / input files identified and accessible
- [ ] Edge cases and failure modes enumerated
- [ ] Reviewer sign-off approach defined

## Standards References

- Rules: `.claude/rules/` — coding-style, testing, git-workflow, legal-compliance, security, patterns
- Docs: `.claude/docs/` — orchestrator-pattern, design-patterns-examples, legal-scanning, pr-process
- Add domain-specific references here.

## Plan

Inline summary only if needed; the canonical issue plan lives at `docs/plans/YYYY-MM-DD-issue-NNN-slug.md`. After approval, add `.planning/plan-approved/NNN.md` and move the GitHub issue from `status:plan-review` to `status:plan-approved`.

> Stage 1: ...
> Stage 2: ...
> Stage 3: ...
