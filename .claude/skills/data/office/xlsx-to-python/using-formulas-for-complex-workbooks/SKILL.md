---
name: xlsx-to-python-using-formulas-for-complex-workbooks
description: 'Sub-skill of xlsx-to-python: Using `formulas` for Complex Workbooks.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Using `formulas` for Complex Workbooks

## Using `formulas` for Complex Workbooks


For spreadsheets with VLOOKUP, INDEX/MATCH, nested IF, or cross-sheet chains,
use the `formulas` library instead of manual parsing:

```python
import formulas

def compile_xlsx_to_function(filepath: str, input_range: str, output_range: str):
    """Compile an Excel workbook into a callable Python function."""
    xl_model = formulas.ExcelModel().loads(filepath).finish()

    # Get full dependency graph
    solution = xl_model.calculate()

    # Compile reusable function
    func = xl_model.compile(
        inputs=[input_range],
        outputs=[output_range],
    )
    return func, solution

# Usage:
func, solution = compile_xlsx_to_function(
    "pile_capacity.xlsx",
    "'Inputs'!B2:B15",
    "'Results'!C5:C10",
)

# The solution dict contains all computed values — use as test assertions
expected = solution["'Results'!C5"]
```

**Dependency graph visualization:**

```python
# Requires: uv add formulas[plot]
xl_model = formulas.ExcelModel().loads("calculation.xlsx").finish()
xl_model.calculate()
# Access the internal dispatcher for graph analysis
dsp = xl_model.dsp
dsp.plot()  # matplotlib visualization
```
