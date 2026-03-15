# 09 — Outputs

## Purpose

Summarize calculation results with pass/fail status, utilization ratios, and
identification of governing cases. This section gives the reviewer a quick
assessment without reading every calculation step.

## Schema Fields

```yaml
outputs:
  summary:
    - check: string            # name of the design check
      reference: string        # code clause
      capacity: number
      demand: number
      unit: string
      utilization: number      # demand / capacity (0.0 to 1.0+)
      limit: number            # maximum allowable utilization
      status: enum             # pass | fail
      governing: boolean       # is this the governing check?
  governing_case:
    check: string
    utilization: number
    margin: string             # remaining margin description
  overall_status: enum         # adequate | inadequate | marginal
```

## Required Content

- Summary table with all checks, their utilization ratios, and pass/fail
- Identification of the governing (highest utilization) case
- Overall adequacy status
- Units on both capacity and demand values

## Quality Checklist

- [ ] Every check from section 08 appears in the output summary
- [ ] Utilization = demand / capacity (not inverted)
- [ ] Governing case is explicitly identified
- [ ] Marginal results (utilization > 0.85) are flagged for attention
- [ ] Overall status is a clear adequacy statement

## Example Snippet

```yaml
outputs:
  summary:
    - check: "Pressure containment (burst)"
      reference: "DNV-ST-F101 Eq. 5.8"
      capacity: 55.8
      demand: 34.5
      unit: "MPa"
      utilization: 0.618
      limit: 1.0
      status: pass
      governing: true
    - check: "External pressure (collapse)"
      reference: "DNV-ST-F101 Eq. 5.11"
      capacity: 42.3
      demand: 12.1
      unit: "MPa"
      utilization: 0.286
      limit: 1.0
      status: pass
      governing: false
  governing_case:
    check: "Pressure containment (burst)"
    utilization: 0.618
    margin: "38.2% remaining capacity"
  overall_status: adequate
```

## Common Mistakes

- Utilization ratio inverted (capacity / demand instead of demand / capacity)
- Governing case not identified — reviewer has to scan all rows
- Missing checks — a limit state computed in section 08 is omitted from summary
- No overall status — the calculation ends without a clear adequacy statement
- Units omitted from capacity/demand columns
