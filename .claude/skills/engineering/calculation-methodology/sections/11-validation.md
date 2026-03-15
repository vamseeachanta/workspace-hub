# 11 — Validation

## Purpose

Confirm the calculation results using an independent method: benchmarks,
alternative analytical methods, published test data, or comparison with
previous projects. Validation checks that the right answer was obtained,
not just that the method was followed correctly.

## Schema Fields

```yaml
validation:
  methods:
    - type: enum               # benchmark | alternative_method | test_data | project_comparison
      description: string
      source: string           # reference for the validation data
      comparison:
        this_calculation: number
        validation_value: number
        unit: string
        difference_pct: number
        acceptable_tolerance: number
        status: enum           # acceptable | unacceptable
  software_validation:
    tool: string               # software name if used
    version: string
    model_description: string
    verification_case: string  # reference to a verified benchmark
  conclusion: string           # overall validation assessment
```

## Required Content

- At least one independent validation method
- Quantitative comparison with tolerance and pass/fail
- Source reference for validation data
- Conclusion stating whether the calculation is validated

## Quality Checklist

- [ ] Validation method is truly independent (not the same formula re-applied)
- [ ] Acceptance tolerance is stated and justified (not arbitrary)
- [ ] Differences are explained if outside tolerance but still acceptable
- [ ] Software validation references a verified benchmark case
- [ ] Published test data or worked examples are preferred over ad-hoc checks

## Example Snippet

```yaml
validation:
  methods:
    - type: alternative_method
      description: "ASME B31.8 Barlow formula for burst pressure"
      source: "ASME B31.8-2022, Eq. 841.1.1"
      comparison:
        this_calculation: 55.8
        validation_value: 57.2
        unit: "MPa"
        difference_pct: 2.5
        acceptable_tolerance: 10.0
        status: acceptable
    - type: benchmark
      description: "DNV-ST-F101 worked example in Appendix E"
      source: "DNV-ST-F101 (2021) Appendix E, Example E-1"
      comparison:
        this_calculation: 55.8
        validation_value: 55.6
        unit: "MPa"
        difference_pct: 0.4
        acceptable_tolerance: 1.0
        status: acceptable
  conclusion: >
    Results are within 2.5% of the ASME alternative method and within 0.4%
    of the DNV worked example. Calculation is validated.
```

## Common Mistakes

- Using the same formula as validation (that is verification, not validation)
- No tolerance stated — reviewer cannot judge if a 5% difference is acceptable
- Software results presented without benchmarking the software itself
- Validation skipped because "the method is well-established"
- Test data comparison without stating test conditions and applicability
