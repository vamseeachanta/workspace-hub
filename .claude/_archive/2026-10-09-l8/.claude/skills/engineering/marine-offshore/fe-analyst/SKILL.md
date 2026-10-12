---
name: fe-analyst
version: 1.1.0
category: engineering
description: "Finite Element Analysis Analyst \u2014 slender structure FEA for marine\
  \ and offshore systems"
tags:
- fea
- orcaflex
- pipeline
- riser
- mooring
- jumper
- installation
- boundary-conditions
- mesh
- design-checks
- html-report
- dnv
- api
created: 2026-02-17
author: Claude
type: skill
trigger: manual
auto_execute: false
tools:
- Read
- Write
- Edit
- Bash
- Grep
- Glob
- Task
related_skills:
- structural-analysis
- mooring-analysis
- hydrodynamic-analysis
capabilities: []
requires: []
scripts_exempt: true
---

# Fe Analyst

## When to Use This Skill

- Setting up or reviewing OrcaFlex FE models for pipelines, risers, jumpers, moorings, or installation analyses
- Designing the HTML report layout for an analysis type
- Assessing mesh quality and discretization adequacy
- Applying boundary conditions correctly for a structural scenario
- Performing code checks (DNV, API, ISO) on results
- Generating standardized analysis reports with Plotly interactive plots

---

## Method references

These archived methods preserve the existing analysis sequence. Check applicability against the owning project's current qualified inputs, standards and accepted workflow; archive content is not current approval or readiness evidence. For the complete task-to-report route, use `.claude/skills/workspace-hub/agent-teams/orchestrator-routing/references/engineering-context.md`.

- 1. FEA Fundamentals for Slender Structures
- What to Document
- BC Types in OrcaFlex
- OrcaFlex Discretization
- Environmental Load Summary
- Static Analysis
- Key Results to Extract and Plot
- DNV-OS-F101 Pipeline Code Checks
- Plot Types Per Section
- 12. Standards Reference
- 13. Common FEA Mistakes and Remedies
