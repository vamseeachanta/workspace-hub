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
  limitations: string        # optional — known constraints (scalar string)
  validity_range: string     # optional — applicable parameter range (scalar string)
```

> **Renderer Mapping Note:** The methodology recommends structured validity
> ranges (temperature, pressure, geometry with min/max/unit). The renderer
> treats both `limitations` and `validity_range` as scalar strings. Encode
> structured range details as a descriptive string, e.g.,
> `"Temperature: -10 to 80 degC; Pressure: 0 to 345 barg"`.

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
  limitations: >
    Analysis assumes uniform wall thickness — mill tolerance applied as
    reduction. Dynamic effects from slugging not considered.
  validity_range: "Temperature: -10 to 80 degC; Pressure: 0 to 345 barg"
```

## Common Mistakes

- Objective states "calculate wall thickness" instead of "demonstrate adequacy"
- No exclusions listed — reviewer assumes everything is covered and finds gaps
- Validity range omitted, making it unclear if the calculation applies at
  extreme operating conditions
- Using `limitations` as a list instead of a scalar string
- Scope does not reference which standards govern the checks
