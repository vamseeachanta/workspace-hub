# 10 — Sensitivity

## Purpose

Quantify how results change when key input parameters vary. Sensitivity
analysis identifies which parameters most influence the outcome and reveals
whether the design is robust or dependent on a narrow input range.

## Schema Fields

```yaml
sensitivity:
  - parameter: string         # name of the parameter being varied
    range: string             # variation range (e.g., "1.0 to 6.0 mm")
    result: string            # outcome description (e.g., "Utilization 0.52–0.78, all pass")
```

> **Renderer Mapping Note:** The methodology recommends rich structures with
> `parameters[]` containing `symbol`, `baseline`, `sweep`, detailed `results`,
> a `tornado` chart object, and `conclusions`. The renderer uses a simple flat
> list where each entry is `{parameter, range, result}` — all strings. Encode
> sweep details and pass/fail outcomes into the `range` and `result` strings.
> Use section 14 (charts) for tornado chart visualization.

## Required Content

- At least the top 3 most uncertain or impactful parameters
- Range covering plausible variation (not arbitrary ±10%)
- Pass/fail status at extremes noted in `result`

## Quality Checklist

- [ ] Each entry has `parameter`, `range`, and `result` (all strings)
- [ ] Ranges are physically meaningful, not arbitrary percentages
- [ ] Parameters include those flagged high-impact in section 06
- [ ] Any parameter value that causes failure is explicitly noted in `result`
- [ ] Results state which parameters the design is most sensitive to

## Example Snippet

```yaml
sensitivity:
  - parameter: "Corrosion allowance"
    range: "1.0 to 6.0 mm"
    result: "Burst utilization 0.52–0.78, all pass. Design most sensitive to this parameter."
  - parameter: "Wall thickness tolerance"
    range: "0.5 to 1.5 mm"
    result: "Burst utilization 0.58–0.67, all pass."
  - parameter: "Design pressure"
    range: "300 to 400 barg"
    result: "Burst utilization 0.54–0.72, all pass. Fails at 480 barg."
```

## Common Mistakes

- Using nested `parameters[]` with `symbol`, `sweep`, `results` sub-objects
  (renderer expects flat `{parameter, range, result}` entries)
- Including `tornado` or `conclusions` objects (not consumed by renderer)
- Only sweeping ±10% without physical justification for the range
- Not sweeping the high-impact assumptions from section 06
- Missing the crossover point where the check changes from pass to fail
