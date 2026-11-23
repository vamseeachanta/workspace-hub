<!-- Current workflow: create/update GitHub issue #NNN, copy this structural template into docs/plans/YYYY-MM-DD-issue-NNN-slug.md, post it for review with status:plan-review, and after user approval create .planning/plan-approved/NNN.md and add status:plan-approved. -->
<!-- Extends route-c-generic.md with Structural / FEA domain sections -->

---
wrk_id: WRK-NNN
title: "<short title>"
domain: structural
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

## Structural / FEA Checklist

- [ ] Load cases defined (operating, survival, accidental, fatigue, seismic if applicable)
- [ ] Element types selected and justified (beam, shell, solid; mesh density rationale)
- [ ] Material properties specified (E, ν, ρ, yield/UTS, fatigue S-N curve source)
- [ ] Boundary conditions documented (fixed, pinned, symmetry, contact)
- [ ] Analysis type selected (linear static, nonlinear, modal, buckling, transient)
- [ ] Verification standard identified: ISO 19902 / DNV-OS-C101 / API RP 2A-WSD / API 579 / ABS Rules
- [ ] Unity check / utilisation ratio criteria defined (e.g. UC ≤ 0.8 for primary members)
- [ ] Code safety factors noted (load factor, resistance factor, consequence class)
- [ ] Model validation approach: hand calc for key members, benchmark against known solution
- [ ] Result outputs defined: stress maps, deformation, RF summary table, buckling mode shapes

## Standards References

- Rules: `.claude/rules/` — coding-style, testing, git-workflow, legal-compliance, security, patterns
- Docs: `.claude/docs/` — orchestrator-pattern, design-patterns-examples, legal-scanning, pr-process

## Standards References (Structural)

- **ISO 19902** — Fixed steel offshore structures (primary reference for offshore structural)
- **DNV-OS-C101** — Design of offshore steel structures (general)
- **DNV-OS-C201** — Structural design of offshore units (WSD method)
- **API RP 2A-WSD / LRFD** — Fixed offshore platforms (WSD and LRFD editions)
- **API 579-1 / ASME FFS-1** — Fitness for service
- **ABS Rules for Offshore Structures** — Mobile drilling units and fixed platforms
- **AISC 360** — Specification for structural steel buildings (when not offshore-specific)

## Plan

Inline summary only if needed; the canonical issue plan lives at `docs/plans/YYYY-MM-DD-issue-NNN-slug.md`. After approval, add `.planning/plan-approved/NNN.md` and move the GitHub issue from `status:plan-review` to `status:plan-approved`.

> Stage 1: ...
> Stage 2: ...
> Stage 3: ...
