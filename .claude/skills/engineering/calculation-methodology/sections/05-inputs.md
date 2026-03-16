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
    value: number             # parameter value
    unit: string              # unit of measurement
    source: string            # optional — where the value comes from
    notes: string             # optional — clarifications or validation notes
```

> **Renderer Mapping Note:** The methodology recommends `category` (geometry,
> load, environment, operational) and structured `validation` objects
> (min, max, note). The renderer does not consume these fields — they will be
> silently dropped. Use `notes` to capture validation range information,
> e.g., `"Typical range: 100–1500 mm"`.

## Required Content

- Every parameter used in the calculation must appear here
- Each parameter must have a source (document, measurement, or assumption ref)
- Units must be stated explicitly (no unitless numbers without explanation)

## Quality Checklist

- [ ] No parameter appears in section 08 that is not listed here
- [ ] Units are consistent with the calculation system (SI preferred)
- [ ] Sources are traceable documents, not "engineering judgment"
- [ ] Validation range information captured in `notes` or `source`
- [ ] Every entry has `name`, `symbol`, `value`, and `unit`

## Example Snippet

```yaml
inputs:
  - name: "Outer diameter"
    symbol: "D_o"
    value: 323.9
    unit: "mm"
    source: "Line pipe data sheet DS-PL-001 Rev B"
    notes: "Typical subsea pipeline OD range: 100–1500 mm"

  - name: "Nominal wall thickness"
    symbol: "t_nom"
    value: 20.6
    unit: "mm"
    source: "Line pipe data sheet DS-PL-001 Rev B"

  - name: "Design pressure"
    symbol: "p_d"
    value: 345
    unit: "barg"
    source: "Process design basis DB-PR-001 Rev A, Table 3.2"
```

## Common Mistakes

- Parameter used in the calculation but not listed in inputs
- Source given as "assumed" without pointing to the assumption in section 06
- Value stated without unit — especially angles (degrees vs radians)
- Including `category` or `validation` fields (not consumed by renderer)
- Mixing unit systems mid-table (some inputs in imperial, others in SI)
