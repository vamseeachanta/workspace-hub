# 05 — Inputs

## Purpose

Tabulate all input parameters with symbol, value, unit, source, and validation
range. This section is the single source of truth for every number used in
the calculation. Reviewers check inputs first — errors here propagate everywhere.

## Schema Fields

```yaml
inputs:
  - name: string              # descriptive parameter name
    symbol: string            # mathematical symbol (e.g., "D_o")
    value: number
    unit: string
    source: string            # where the value comes from
    category: enum            # geometry | load | environment | operational
    validation:
      min: number             # physically reasonable minimum
      max: number             # physically reasonable maximum
      note: string            # optional explanation of range
```

## Required Content

- Every parameter used in the calculation must appear here
- Each parameter must have a source (document, measurement, or assumption ref)
- Units must be stated explicitly (no unitless numbers without explanation)
- Validation ranges for key parameters

## Quality Checklist

- [ ] No parameter appears in section 08 that is not listed here
- [ ] Units are consistent with the calculation system (SI preferred)
- [ ] Sources are traceable documents, not "engineering judgment"
- [ ] Validation ranges catch data entry errors (e.g., OD in mm not m)
- [ ] Categorization helps reviewers locate parameters by type

## Example Snippet

```yaml
inputs:
  - name: "Outer diameter"
    symbol: "D_o"
    value: 323.9
    unit: "mm"
    source: "Line pipe data sheet DS-PL-001 Rev B"
    category: geometry
    validation:
      min: 100
      max: 1500
      note: "Typical subsea pipeline OD range"

  - name: "Nominal wall thickness"
    symbol: "t_nom"
    value: 20.6
    unit: "mm"
    source: "Line pipe data sheet DS-PL-001 Rev B"
    category: geometry
    validation:
      min: 5
      max: 50

  - name: "Design pressure"
    symbol: "p_d"
    value: 345
    unit: "barg"
    source: "Process design basis DB-PR-001 Rev A, Table 3.2"
    category: operational
    validation:
      min: 0
      max: 600
```

## Common Mistakes

- Parameter used in the calculation but not listed in inputs
- Source given as "assumed" without pointing to the assumption in section 06
- Value stated without unit — especially angles (degrees vs radians)
- Validation range missing — a reviewer cannot tell if 323.9 mm is reasonable
  without knowing the expected OD range
- Mixing unit systems mid-table (some inputs in imperial, others in SI)
