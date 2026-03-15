---
name: calculation-methodology
description: >
  Guides the creation of engineering calculation documents through a 6-phase
  workflow covering problem definition, input gathering, method selection,
  computation, validation, and reporting. Produces structured YAML calculation
  files that the calculation-report skill renders to HTML/PDF.
version: 1.0.0
updated: 2026-03-15
category: engineering
triggers:
  - engineering calculation
  - design calculation
  - calculation note
  - calc methodology
  - structural calculation
  - pipeline calculation
  - fatigue calculation
  - code check
  - design verification
related_skills:
  - engineering/calculation-report
  - engineering/standards
  - engineering/units
capabilities:
  - structured_calculation_authoring
  - code_compliance_checking
  - sensitivity_analysis_guidance
  - verification_workflow
  - calculation_quality_assurance
---

# Calculation Methodology

> Structured workflow for engineering calculation documents. Covers phases 1-5
> (authoring); phase 6 hands off to `calculation-report` for rendering.

## 6-Phase Workflow

| Phase | Name              | Gate                                         | Output                        |
|-------|-------------------|----------------------------------------------|-------------------------------|
| 1     | Problem Definition | Scope, objective, and limitations stated      | Sections 01-02 populated      |
| 2     | Input Gathering    | All inputs sourced, units verified            | Sections 03-06 populated      |
| 3     | Method Selection   | Standard identified, applicability confirmed  | Section 07 populated          |
| 4     | Computation        | Step-by-step calc with clause refs            | Sections 08-09 populated      |
| 5     | Validation         | Independent check or benchmark completed      | Sections 10-13 populated      |
| 6     | Reporting          | Trigger `calculation-report` skill            | Sections 14-16, final output  |

## Section Reference Table

Each section has a dedicated reference file in `sections/` with purpose, schema
fields, required content, quality checklist, example snippet, and common mistakes.

| #  | Section          | Reference File        | Phase | Required |
|----|------------------|-----------------------|-------|----------|
| 01 | Metadata         | `01-metadata.md`      | 1     | Yes      |
| 02 | Scope            | `02-scope.md`         | 1     | Yes      |
| 03 | Design Basis     | `03-design-basis.md`  | 2     | Yes      |
| 04 | Materials        | `04-materials.md`     | 2     | Conditional |
| 05 | Inputs           | `05-inputs.md`        | 2     | Yes      |
| 06 | Assumptions      | `06-assumptions.md`   | 2     | Yes      |
| 07 | Methodology      | `07-methodology.md`   | 3     | Yes      |
| 08 | Calculations     | `08-calculations.md`  | 4     | Yes      |
| 09 | Outputs          | `09-outputs.md`       | 4     | Yes      |
| 10 | Sensitivity      | `10-sensitivity.md`   | 5     | Recommended |
| 11 | Validation       | `11-validation.md`    | 5     | Yes      |
| 12 | Verification     | `12-verification.md`  | 5     | Yes      |
| 13 | Conclusions      | `13-conclusions.md`   | 5     | Yes      |
| 14 | Charts           | `14-charts.md`        | 6     | Recommended |
| 15 | Data Tables      | `15-data-tables.md`   | 6     | Recommended |
| 16 | References       | `16-references.md`    | 6     | Yes      |

## Phase-to-Section Mapping

### Phase 1 — Problem Definition
Populate sections 01 (Metadata) and 02 (Scope). Establish document control,
define the calculation objective, and bound the scope with explicit inclusions,
exclusions, and validity ranges. No computation occurs in this phase.

### Phase 2 — Input Gathering
Populate sections 03 (Design Basis), 04 (Materials), 05 (Inputs), and
06 (Assumptions). Every input must have a traceable source. Material properties
must reference certificates or code tables. Assumptions must state whether they
are conservative or best-estimate and justify why.

### Phase 3 — Method Selection
Populate section 07 (Methodology). Select the governing standard and edition.
Confirm applicability to the problem geometry, load regime, and material.
Present equations in symbolic form before substituting numeric values.

### Phase 4 — Computation
Populate sections 08 (Calculations) and 09 (Outputs). Execute the method
step-by-step with clause references at each step. Record intermediate results
with units. Summarize results with pass/fail status and utilization ratios.

### Phase 5 — Validation
Populate sections 10 (Sensitivity), 11 (Validation), 12 (Verification), and
13 (Conclusions). Perform sensitivity sweeps on key parameters. Validate
against benchmarks or alternative methods. Record independent check details.
State the adequacy conclusion with governing check identification.

### Phase 6 — Reporting
Populate sections 14 (Charts), 15 (Data Tables), and 16 (References).
Finalize visualizations and citation list. Then trigger the `calculation-report`
skill to render the structured YAML into HTML/PDF output.

**Handoff to calculation-report:**
```
# After all sections are populated:
# 1. Validate YAML structure against schema
# 2. Invoke calculation-report skill with the calc YAML path
# 3. Review rendered output for formatting issues
```

## Quality Checklist — Commonly Missed Items

These items are the most frequent causes of calculation rejection in
engineering review, drawn from EFCOG, DNV, Structures Centre, and Caltrans
guidance:

### Problem Definition (Phase 1)
- [ ] Calculation objective states what is being proved, not just what is computed
- [ ] Exclusions are explicit — reviewers should not guess what is out of scope
- [ ] Validity range specifies temperature, pressure, and geometry limits

### Input Gathering (Phase 2)
- [ ] Every input has a source reference (not just a value)
- [ ] Units are consistent throughout — no mid-calculation unit changes
- [ ] Material partial safety factors match the code edition cited
- [ ] Assumptions are numbered and each has a justification sentence

### Method Selection (Phase 3)
- [ ] Standard edition year is stated (not just the standard number)
- [ ] Applicability limits of the method are checked against actual parameters
- [ ] Equations appear in symbolic form before numeric substitution

### Computation (Phase 4)
- [ ] Each calculation step cites the specific clause or equation number
- [ ] Intermediate results are shown (not just final answers)
- [ ] Hand-check or order-of-magnitude sanity check is present

### Validation (Phase 5)
- [ ] At least one independent validation method is used
- [ ] Sensitivity analysis covers the top 3 most uncertain parameters
- [ ] Verification record includes checker name and date
- [ ] Conclusion explicitly states which check governs the design

### Reporting (Phase 6)
- [ ] All referenced standards appear in the reference list with edition
- [ ] Charts have axis labels, units, and titles
- [ ] Data tables state units in column headers, not in cell values

## Usage

```
# Typical invocation pattern:
# 1. Agent loads this skill when a calculation task is identified
# 2. Work through phases 1-5, populating section YAML
# 3. At phase 6, hand off to calculation-report for rendering
#
# For section-specific guidance, read the relevant file:
#   .claude/skills/engineering/calculation-methodology/sections/01-metadata.md
```

## Research Sources

This skill synthesizes calculation documentation best practices from:
- EFCOG (Energy Facility Contractors Group) — calculation note guidance
- DNV (Det Norske Veritas) — recommended practices for documentation
- Structures Centre — structural calculation note templates
- Eng-Tips — practitioner discussions on calculation quality
- Caltrans — bridge design calculation documentation standards
