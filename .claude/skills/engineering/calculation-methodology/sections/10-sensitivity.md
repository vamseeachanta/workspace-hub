# 10 — Sensitivity

## Purpose

Quantify how results change when key input parameters vary. Sensitivity
analysis identifies which parameters most influence the outcome and reveals
whether the design is robust or dependent on a narrow input range.

## Schema Fields

```yaml
sensitivity:
  parameters:
    - name: string             # parameter being varied
      symbol: string
      baseline: number
      unit: string
      sweep:
        min: number
        max: number
        step: number
      results:
        - input_value: number
          output_name: string
          output_value: number
          utilization: number
          status: enum         # pass | fail
  tornado:
    output_metric: string      # which output is shown on tornado chart
    ranked_parameters:
      - parameter: string
        low_value: number
        high_value: number
        output_at_low: number
        output_at_high: number
        delta: number          # absolute change in output
  conclusions:
    - string                   # key findings from the sensitivity study
```

## Required Content

- At least the top 3 most uncertain or impactful parameters swept
- Sweep range covering plausible variation (not arbitrary +/- 10%)
- Pass/fail status at each sweep point
- Ranking of parameter influence (tornado chart data)

## Quality Checklist

- [ ] Sweep ranges are physically meaningful, not arbitrary percentages
- [ ] Parameters swept include those flagged high-impact in section 06
- [ ] Tornado chart data ranks parameters by influence on the governing check
- [ ] Any sweep point that causes a failure is explicitly highlighted
- [ ] Conclusions state which parameters the design is most sensitive to

## Example Snippet

```yaml
sensitivity:
  parameters:
    - name: "Corrosion allowance"
      symbol: "t_corr"
      baseline: 3.0
      unit: "mm"
      sweep:
        min: 1.0
        max: 6.0
        step: 1.0
      results:
        - input_value: 1.0
          output_name: "Burst utilization"
          output_value: 0.52
          utilization: 0.52
          status: pass
        - input_value: 6.0
          output_name: "Burst utilization"
          output_value: 0.78
          utilization: 0.78
          status: pass
  tornado:
    output_metric: "Burst utilization"
    ranked_parameters:
      - parameter: "Corrosion allowance"
        low_value: 1.0
        high_value: 6.0
        output_at_low: 0.52
        output_at_high: 0.78
        delta: 0.26
  conclusions:
    - "Design is most sensitive to corrosion allowance — 6 mm CA still passes"
    - "Wall thickness tolerance has second-largest effect"
```

## Common Mistakes

- Only sweeping +/- 10% without physical justification for the range
- Not sweeping the high-impact assumptions from section 06
- Sensitivity results not linked back to the governing check
- Missing the crossover point where the check changes from pass to fail
- No conclusions drawn — data presented without interpretation
