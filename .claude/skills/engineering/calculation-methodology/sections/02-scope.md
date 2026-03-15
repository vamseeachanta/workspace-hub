# 02 — Scope

## Purpose

Define the calculation objective, what is included and excluded, and the
validity range of the results. A well-defined scope prevents scope creep
during computation and tells reviewers exactly what is being demonstrated.

## Schema Fields

```yaml
scope:
  objective: string          # what the calculation proves or determines
  inclusions:
    - string                 # items explicitly covered
  exclusions:
    - string                 # items explicitly not covered
  limitations:
    - string                 # known constraints on the analysis
  validity_range:
    temperature:
      min: number
      max: number
      unit: string
    pressure:
      min: number
      max: number
      unit: string
    geometry:
      description: string   # applicable geometry range
```

## Required Content

- Objective statement phrased as what is being proved (not just computed)
- At least one inclusion and one exclusion
- Validity range for the primary operating parameters

## Quality Checklist

- [ ] Objective says "demonstrate adequacy of..." not "calculate the..."
- [ ] Exclusions prevent reviewer questions about missing checks
- [ ] Limitations acknowledge simplifications or boundary effects
- [ ] Validity range is quantitative, not vague ("high temperature")
- [ ] Scope aligns with the design basis codes cited in section 03

## Example Snippet

```yaml
scope:
  objective: >
    Demonstrate that the 12-inch export pipeline wall thickness is adequate
    for internal pressure, external pressure, and combined loading per
    DNV-ST-F101 (2021).
  inclusions:
    - "Internal pressure containment (burst)"
    - "External pressure collapse"
    - "Combined loading — pressure and bending"
  exclusions:
    - "On-bottom stability (covered in PRJ-CALC-003)"
    - "Free span fatigue (covered in PRJ-CALC-004)"
  limitations:
    - "Analysis assumes uniform wall thickness — mill tolerance applied as reduction"
    - "Dynamic effects from slugging not considered"
  validity_range:
    temperature:
      min: -10
      max: 80
      unit: "degC"
    pressure:
      min: 0
      max: 345
      unit: "barg"
```

## Common Mistakes

- Objective states "calculate wall thickness" instead of "demonstrate adequacy"
- No exclusions listed — reviewer assumes everything is covered and finds gaps
- Validity range omitted, making it unclear if the calculation applies at
  extreme operating conditions
- Scope does not reference which standards govern the checks
