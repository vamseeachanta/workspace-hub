# 11 — Validation

## Purpose

Confirm the calculation results using an independent method: benchmarks,
alternative analytical methods, published test data, or comparison with
previous projects. Validation checks that the right answer was obtained,
not just that the method was followed correctly.

## Schema Fields

```yaml
validation:
  method: string              # optional — validation method description
  test_file: string           # optional — path to test file
  test_count: integer         # optional — number of test cases
  test_categories:            # optional — list of test category names
    - string
  benchmark_source: string    # optional — reference for benchmark data
```

> **Renderer Mapping Note:** The methodology recommends a `methods[]` array
> with structured comparison objects (`this_calculation`, `validation_value`,
> `difference_pct`, `acceptable_tolerance`, `status`) plus
> `software_validation` and `conclusion`. The renderer uses a flat dict with
> all fields optional. Encode detailed comparison results in `method`, and
> reference benchmark sources in `benchmark_source`.

## Required Content

- At least one validation approach described in `method`
- Source reference for validation data in `benchmark_source`
- Test file path if automated tests exist

## Quality Checklist

- [ ] All fields are scalars or simple lists (no nested comparison objects)
- [ ] Validation method is truly independent (not the same formula re-applied)
- [ ] Benchmark source is a traceable reference
- [ ] Test categories help reviewers understand coverage scope
- [ ] Software validation references a verified benchmark case

## Example Snippet

```yaml
validation:
  method: >
    Independent check using ASME B31.8 Barlow formula. Result: 57.2 MPa
    vs this calculation 55.8 MPa (2.5% difference, within 10% tolerance).
    Also compared to DNV-ST-F101 Appendix E worked example: 55.6 MPa
    (0.4% difference).
  test_file: "tests/test_wall_thickness_burst.py"
  test_count: 12
  test_categories:
    - "Burst pressure — seawater"
    - "Burst pressure — air"
    - "Collapse pressure"
  benchmark_source: "DNV-ST-F101 (2021) Appendix E, Example E-1"
```

## Common Mistakes

- Using nested `methods[]` with structured `comparison` objects
  (renderer expects flat scalar fields)
- Including `software_validation` or `conclusion` sub-objects
- Using the same formula as validation (that is verification, not validation)
- Validation skipped because "the method is well-established"
- Test data comparison without stating test conditions and applicability
