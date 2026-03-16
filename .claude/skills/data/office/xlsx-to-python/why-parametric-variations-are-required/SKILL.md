---
name: xlsx-to-python-why-parametric-variations-are-required
description: 'Sub-skill of xlsx-to-python: Why Parametric Variations Are Required
  (+4).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Why Parametric Variations Are Required (+4)

## Why Parametric Variations Are Required


A single test point (the original Excel values) proves the implementation matches
at one configuration. Engineering calculations must be valid across their input
range. Parametric variations catch:
- Off-by-one errors in unit conversions
- Boundary condition failures (zero, negative, extreme values)
- Formula implementation bugs that happen to pass at one point
- Missing edge case handling


## The 10-Variation Rule


For every extracted calculation, generate **10 parametric test cases** that vary
inputs within reasonable engineering limits. The variations should cover:

1. **Original values** (baseline — from Excel cached values)
2. **All-minimum** inputs at lower typical range
3. **All-maximum** inputs at upper typical range
4. **One-at-a-time low** — each input at its minimum while others stay nominal
5. **One-at-a-time high** — each input at its maximum while others stay nominal
6. **Mid-range** — all inputs at 50% of range
7. **Stress combination** — inputs at toughest combination (e.g., max load + min strength)
8. **Near-zero** — inputs near zero where division-by-zero or sign issues appear
9. **Large values** — inputs at 10x typical to catch overflow/precision issues
10. **Random within range** — random valid combination for regression testing


## Implementation Pattern


```python
import pytest

# Input ranges from extraction (typical_range from dark-intelligence archive)
INPUT_RANGES = {
    "diameter": {"min": 0.1, "max": 5.0, "nominal": 1.0, "unit": "m"},
    "wall_thickness": {"min": 0.005, "max": 0.1, "nominal": 0.025, "unit": "m"},
    "pressure": {"min": 0.0, "max": 50.0, "nominal": 10.0, "unit": "MPa"},
}

def make_variation(overrides: dict) -> dict:
    """Create a test case from nominal values with overrides."""
    case = {k: v["nominal"] for k, v in INPUT_RANGES.items()}
    case.update(overrides)
    return case

# Parametric test cases
VARIATIONS = [
    pytest.param(make_variation({}), id="nominal"),
    pytest.param(make_variation({k: v["min"] for k, v in INPUT_RANGES.items()}), id="all-min"),
    pytest.param(make_variation({k: v["max"] for k, v in INPUT_RANGES.items()}), id="all-max"),
    # One-at-a-time variations for each input...
]

@pytest.mark.parametrize("inputs", VARIATIONS)
def test_calculation_parametric(inputs):
    """Parametric variation — verify calculation across input range."""
    result = calculate(**inputs)
    # At minimum: check result is finite and within physical bounds
    assert result is not None
    assert not (isinstance(result, float) and (result != result))  # NaN check
    # Tighter assertions added once reference values are computed
```


## How to Get Reference Values for Variations


Since the Excel file only contains ONE set of values, reference values for
parameter variations come from:

1. **`formulas` library** — compile the workbook and evaluate at new inputs
2. **Manual calculation** — for simple formulas, compute expected values by hand
3. **Cross-validation** — if the same calculation exists in digitalmodel/assetutilities,
   run both and compare
4. **Physical bounds only** — when exact reference is unavailable, assert output
   is within physically meaningful bounds (e.g., stress > 0, efficiency 0-1)

```python
# Using formulas library for parametric reference values
import formulas

xl_model = formulas.ExcelModel().loads("calculation.xlsx").finish()

for variation in VARIATIONS:
    # Set input cells to variation values
    inputs = {"'Inputs'!B2": variation["diameter"], ...}
    solution = xl_model.calculate(inputs=inputs)
    expected = solution["'Results'!C5"]
    # Use as reference value in parametric test
```


## Generating Variations from Archive YAML


The dark-intelligence archive's `inputs[].typical_range` field provides the
min/max for each parameter. Use this to auto-generate variations:

```python
def generate_variations(archive: dict, n: int = 10) -> list[dict]:
    """Generate n parametric variations from archive input ranges."""
    inputs = archive.get("inputs", [])
    nominal = {inp["name"]: inp["test_value"] for inp in inputs}
    ranges = {
        inp["name"]: inp.get("typical_range", [inp["test_value"] * 0.5, inp["test_value"] * 2.0])
        for inp in inputs
        if inp.get("test_value") is not None
    }

    variations = [nominal]  # Case 0: original values

    # All-min, all-max
    variations.append({k: r[0] for k, r in ranges.items()})
    variations.append({k: r[1] for k, r in ranges.items()})

    # One-at-a-time for each input
    for key in ranges:
        low = {**nominal, key: ranges[key][0]}
        high = {**nominal, key: ranges[key][1]}
        variations.append(low)
        variations.append(high)

    # Trim or pad to n
    import random
    while len(variations) < n:
        rand_case = {k: random.uniform(r[0], r[1]) for k, r in ranges.items()}
        variations.append(rand_case)

    return variations[:n]
```
