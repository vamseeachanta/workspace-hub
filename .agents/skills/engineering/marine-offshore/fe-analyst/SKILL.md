---
name: fe-analyst
version: 1.0.0
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

## Sub-Skills

- [1. FEA Fundamentals for Slender Structures](1-fea-fundamentals-for-slender-structures/SKILL.md)
- [What to Document (+2)](what-to-document/SKILL.md)
- [What to Document (+1)](what-to-document/SKILL.md)
- [BC Types in OrcaFlex (+2)](bc-types-in-orcaflex/SKILL.md)
- [OrcaFlex Discretization (+3)](orcaflex-discretization/SKILL.md)
- [What to Document](what-to-document/SKILL.md)
- [Environmental Load Summary (+1)](environmental-load-summary/SKILL.md)
- [Static Analysis (+3)](static-analysis/SKILL.md)
- [Key Results to Extract and Plot (+1)](key-results-to-extract-and-plot/SKILL.md)
- [DNV-OS-F101 Pipeline Code Checks (+2)](dnv-os-f101-pipeline-code-checks/SKILL.md)
- [Plot Types Per Section](plot-types-per-section/SKILL.md)
- [12. Standards Reference](12-standards-reference/SKILL.md)
- [13. Common FEA Mistakes and Remedies](13-common-fea-mistakes-and-remedies/SKILL.md)
