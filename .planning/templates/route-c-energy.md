<!-- Copy this template with: scripts/work-queue/new-spec.sh WRK-NNN energy -->
<!-- Extends route-c-generic.md with Oil & Gas / Energy domain sections -->

---
wrk_id: WRK-NNN
title: "<short title>"
domain: energy
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

## Energy / O&G Checklist

- [ ] Field/reservoir type: conventional, unconventional (shale, tight), deepwater, shelf
- [ ] Reservoir parameters: porosity, permeability, fluid PVT, drive mechanism
- [ ] Production profile basis: decline curve (Arps), material balance, reservoir simulation
- [ ] Economic assumptions: capex, opex, royalty rate, fiscal regime, discount rate
- [ ] BSEE / regulatory hooks: OCS permit type, Well Control Rule compliance, SEMS requirements
- [ ] Fluid flow correlations selected: single-phase (Colebrook-White/Moody), multiphase (Beggs-Brill, Hagedorn-Brown)
- [ ] Wellbore design: casing program, tubing sizing, artificial lift type (if applicable)
- [ ] Surface facilities: separator train, gas lift, water injection, export specification
- [ ] HSE / H2S handling: sour service, NACE MR0175 material requirements
- [ ] Data sources: DrillingInfo / Enverus, BSEE Well Activity, EIA, state agency APIs
- [ ] Output: P10/P50/P90 production forecast, NPV/IRR table, risk register

## Standards References

- Rules: `.claude/rules/` — coding-style, testing, git-workflow, legal-compliance, security, patterns
- Docs: `.claude/docs/` — orchestrator-pattern, design-patterns-examples, legal-scanning, pr-process

## Standards References (Energy)

- **BSEE: 30 CFR Part 250** — OCS oil and gas operations
- **BSEE Well Control Rule** — Blowout preventer and well control requirements
- **API RP 14E** — Design and installation of offshore production platform piping systems
- **API RP 505** — Recommended practices for classification of locations for electrical installations
  at petroleum facilities
- **NACE MR0175 / ISO 15156** — Petroleum and natural gas industries — materials for use in H2S
  environments (sour service)
- **SPE-PRMS** — Petroleum Resources Management System (reserves classification)
- **EIA API endpoints** — See `.claude/docs/` for data-access patterns

## Plan

Inline Route A plan, or reference to `specs/wrk/WRK-NNN/plan.md` for Route C.

> Stage 1: ...
> Stage 2: ...
> Stage 3: ...
