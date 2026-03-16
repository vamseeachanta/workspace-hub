---
name: xlsx-to-python-recommended-stack
description: 'Sub-skill of xlsx-to-python: Recommended Stack (+2).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Recommended Stack (+2)

## Recommended Stack


| Library | Purpose | Install | Status |
|---------|---------|---------|--------|
| **openpyxl** | Cell values + formula strings + named ranges | `uv add openpyxl` | Active, stable |
| **formulas** | Formula parsing, AST, dependency graph, evaluation | `uv add formulas` | Active (v1.3.3) |
| **networkx** | Dependency graph analysis (topological sort) | `uv add networkx` | Active, stable |
| **oletools** | VBA macro source code extraction from .xlsm/.xls | `uv add oletools` | Active, stable |


## Alternative Libraries (evaluated, not primary)


| Library | What It Does | Why Not Primary | When to Use |
|---------|-------------|-----------------|-------------|
| **pycel** | Compiles Excel to executable Python + graph viz | Broader scope than needed; heavier dependency | When you need full workbook simulation |
| **xlcalculator** | Converts Excel formulas to Python + evaluates | Inactive (no releases in 12+ months); modernized koala2 | Reference for formula-to-Python translation patterns |
| **graphedexcel** | Cell dependency graph visualization (networkx + matplotlib) | Viz-only; no formula parsing | Quick visual audit of spreadsheet complexity |
| **excel-dependency-graph** | Directed graph of formula dependencies | Lightweight but limited features | Simple dependency mapping without evaluation |
| **formula-dependency-excel** | Cell dependency extraction | Minimal; proof-of-concept level | Quick prototyping |


## Key Insight from `formulas` Library


The `formulas` library can compile an entire Excel workbook into a Python
`DispatchPipe` — a callable function with defined inputs and outputs. This is
the most mature approach for complex workbooks:

```python
import formulas

# Load and compile the workbook
xl_model = formulas.ExcelModel().loads("calculation.xlsx").finish()

# Get the dependency-ordered calculation dispatcher
solution = xl_model.calculate()

# Access any cell's computed value
value = solution.get("'Sheet1'!B10")

# Compile a reusable function with fixed I/O
func = xl_model.compile(
    inputs=["'Inputs'!B2:B10"],
    outputs=["'Results'!C5:C8"]
)
result = func({"'Inputs'!B2:B10": input_array})
```

**When to use `formulas` vs raw openpyxl:**

| Scenario | Use |
|----------|-----|
| Simple formulas (arithmetic, basic functions) | openpyxl + custom parser |
| Complex formulas (VLOOKUP, INDEX/MATCH, nested IF) | `formulas` library |
| Need dependency graph visualization | `formulas` + `plot` extra, or graphedexcel |
| Need to evaluate formulas without Excel | `formulas` or pycel |
| Need only formula strings + cell refs | openpyxl alone |
