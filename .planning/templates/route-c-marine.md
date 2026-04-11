<!-- Current workflow: create/update GitHub issue #NNN, copy this marine template into docs/plans/YYYY-MM-DD-issue-NNN-slug.md, post it for review with status:plan-review, and after user approval create .planning/plan-approved/NNN.md and add status:plan-approved. -->
<!-- Extends route-c-generic.md with Naval Architecture / Offshore Marine domain sections -->

---
wrk_id: WRK-NNN
title: "<short title>"
domain: marine
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

## Marine / Offshore Checklist

- [ ] Vessel/structure type defined (FPSO, jacket, semi-sub, monopile, riser, mooring)
- [ ] Environmental conditions specified (Hs, Tp, wind speed, current — operating and 100-yr return)
- [ ] RAO (Response Amplitude Operator) requirements: DOFs to capture, wave frequencies, heading
- [ ] Fatigue approach selected: S-N curve source, DFF (fatigue design factor), SCF methodology
- [ ] Hydrodynamic assumptions: Morison equation vs diffraction panel; drag/inertia coefficients (Cd, Cm)
- [ ] Mooring/riser system: line types, pre-tension, max offset criteria
- [ ] Classification society code: DNV-RP-C205, DNV-RP-C203, DNV-RP-F204, ABS MODU Rules
- [ ] Vortex-induced vibration (VIV) check required? (riser/conductor screening criteria)
- [ ] Marine growth / corrosion allowance accounted for
- [ ] Intact and damage stability criteria (if applicable)
- [ ] Output: RAO tables, fatigue life summary, tension/offset envelopes

## Standards References

- Rules: `.claude/rules/` — coding-style, testing, git-workflow, legal-compliance, security, patterns
- Docs: `.claude/docs/` — orchestrator-pattern, design-patterns-examples, legal-scanning, pr-process

## Standards References (Marine)

- **DNV-RP-C205** — Environmental conditions and environmental loads
- **DNV-RP-C203 / DNV-RP-0005** — Fatigue design of offshore steel structures (S-N curves)
- **DNV-RP-F204** — Riser fatigue
- **DNVGL-OS-E301** — Position mooring
- **ABS MODU Rules** — Mobile offshore drilling units
- **ABS Rules for Building and Classing FPSOs**
- **API RP 2SK** — Design and analysis of stationkeeping systems for floating structures
- **API RP 2T** — Planning, designing, and constructing tension leg platforms

## Plan

Inline summary only if needed; the canonical issue plan lives at `docs/plans/YYYY-MM-DD-issue-NNN-slug.md`. After approval, add `.planning/plan-approved/NNN.md` and move the GitHub issue from `status:plan-review` to `status:plan-approved`.

> Stage 1: ...
> Stage 2: ...
> Stage 3: ...
