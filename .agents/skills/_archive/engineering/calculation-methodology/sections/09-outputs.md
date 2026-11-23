# 09 — Outputs

## Purpose

Summarize calculation results with pass/fail status, utilization ratios, and
identification of governing cases. This section gives the reviewer a quick
assessment without reading every calculation step.

## Schema Fields

```yaml
outputs:
  - name: string              # result description
    symbol: string            # mathematical symbol
    value: number             # computed value
    unit: string              # unit of measurement
    pass_fail: string         # optional — "pass" or "fail"
    limit: number             # optional — allowable limit (rendered as "≤ limit")
    notes: string             # optional — computation trace or clarification
```

> **Renderer Mapping Note:** The methodology recommends a nested structure
> with `summary[]` containing `check`, `reference`, `capacity`, `demand`,
> `utilization`, `limit`, `status`, `governing` fields, plus a
> `governing_case` object and `overall_status`. The renderer uses a flat
> list where each entry is `{name, symbol, value, unit}` with optional
> `pass_fail`, `limit`, and `notes`. Encode utilization and governing
> information in `notes`, and use section 13 (conclusions) for the overall
> adequacy statement and governing check identification.

## Required Content

- All key results from the calculation
- Pass/fail status for design checks
- Units on all values
- Limit values for checks that have acceptance criteria

## Quality Checklist

- [ ] Every check from section 08 appears as an output entry
- [ ] `pass_fail` uses lowercase `"pass"` or `"fail"` (not `"PASS"`)
- [ ] `limit` is a number (the renderer prepends "≤")
- [ ] Governing case is identifiable from the utilization values
- [ ] Each entry has `name`, `symbol`, `value`, and `unit`

## Example Snippet

```yaml
outputs:
  - name: "Initial current demand"
    symbol: "I_ci"
    value: 15.0
    unit: "A"
    notes: "I_ci = 5000 × 0.150 × 0.02 = 15.0 A"
  - name: "Factored Damage"
    symbol: "D_{factored}"
    value: 0.45
    unit: "-"
    pass_fail: "pass"
    limit: 1.0
    notes: "D * DFF = 0.15 * 3.0"
  - name: "Burst Utilization"
    symbol: "U_{burst}"
    value: 0.618
    unit: "-"
    pass_fail: "pass"
    limit: 1.0
    notes: "Demand/Capacity = 34.5/55.8 — governing check"
```

## Common Mistakes

- Using nested `summary[]` with `check/capacity/demand/utilization` structure
  (renderer expects flat `{name, symbol, value, unit}` entries)
- Including `governing_case` or `overall_status` objects (use section 13 instead)
- Using uppercase `"PASS"` instead of lowercase `"pass"`
- Units omitted from output values
- Missing `symbol` field (required by renderer)
