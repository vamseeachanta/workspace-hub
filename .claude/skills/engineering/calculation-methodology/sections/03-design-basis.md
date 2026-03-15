# 03 — Design Basis

## Purpose

Establish the normative framework: which codes and standards govern the
calculation, design life, safety class, and load combinations. This section
anchors every subsequent calculation step to a specific code clause.

## Schema Fields

```yaml
design_basis:
  codes:
    - standard: string       # e.g., "DNV-ST-F101"
      edition: string        # e.g., "2021-08"
      title: string          # full title of the standard
      role: enum             # primary | supplementary | informative
  design_life:
    value: number
    unit: string             # years
  safety_class:
    class: string            # e.g., "medium", "high"
    justification: string
  location_class:
    class: string
    justification: string
  load_combinations:
    - id: string             # e.g., "LC-01"
      description: string
      loads:
        - type: string
          value: number
          unit: string
          factor: number     # load factor / partial safety factor
      reference: string      # code clause
```

## Required Content

- At least one primary code with edition year
- Design life with unit
- Safety class with justification
- At least one load combination with partial factors

## Quality Checklist

- [ ] Code edition includes the year or date (not just the standard number)
- [ ] Primary vs supplementary roles are distinguished
- [ ] Safety class justification references consequence of failure
- [ ] Load combination factors match the cited code edition
- [ ] Load combinations cover all relevant limit states (ULS, SLS, ALS/FLS)

## Example Snippet

```yaml
design_basis:
  codes:
    - standard: "DNV-ST-F101"
      edition: "2021-08"
      title: "Submarine Pipeline Systems"
      role: primary
    - standard: "DNV-RP-F105"
      edition: "2017-06"
      title: "Free Spanning Pipelines"
      role: supplementary
  design_life:
    value: 25
    unit: "years"
  safety_class:
    class: "medium"
    justification: "Hydrocarbon pipeline in non-populated area"
  load_combinations:
    - id: "LC-01"
      description: "System test — mill pressure test"
      loads:
        - type: "internal_pressure"
          value: 517
          unit: "barg"
          factor: 1.0
      reference: "DNV-ST-F101 Sec.5 Table 5-7"
```

## Common Mistakes

- Standard cited without edition year — different editions have different factors
- Safety class stated without justification for why that class was selected
- Load factors taken from a different edition than the one cited
- Missing limit states — e.g., fatigue limit state omitted for cyclic loading
- Informative references treated as normative requirements
