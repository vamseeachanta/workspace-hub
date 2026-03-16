---
name: xlsx-to-python-research-finding-no-existing-library-does-this
description: 'Sub-skill of xlsx-to-python: Research Finding: No Existing Library Does
  This (+5).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Research Finding: No Existing Library Does This (+5)

## Research Finding: No Existing Library Does This


Evaluated 2026-03-16. No library — `formulas`, `pycel`, `xlcalculator`, `koala2`,
`graphedexcel`, or the AI-powered `Pyoneer` — detects repeated row patterns and
collapses them into loops. They all operate cell-by-cell.

The building block exists in **openpyxl**: `openpyxl.formula.translate.Translator`
can normalize a formula from any row back to a canonical "row 1" form. If two cells
produce the same normalized formula, they share a pattern.


## Pattern Detection: openpyxl Translator


```python
from openpyxl.formula.translate import Translator

def normalize_formula(formula: str, cell_ref: str, origin_row: int = 1) -> str:
    """Translate formula back to row-1 to create a canonical form."""
    col = ''.join(c for c in cell_ref if c.isalpha())
    origin = f"{col}{origin_row}"
    try:
        return Translator(formula, cell_ref).translate_formula(origin)
    except Exception:
        return formula  # absolute refs won't translate

def detect_row_patterns(formulas: list[dict]) -> dict:
    """Group formulas by normalized pattern.

    Returns: {normalized_formula: [{"row": N, "cell_ref": "X", ...}, ...]}
    Each group with len > 1 is a loop candidate.
    """
    from collections import defaultdict
    patterns = defaultdict(list)
    for f in formulas:
        norm = normalize_formula(f["formula"], f["cell_ref"])
        patterns[norm].append(f)
    return dict(patterns)
```


## Code Generation: Pattern → Python


For each pattern group, emit one of:

| Group Size | Python Output |
|-----------|--------------|
| 1 cell | Single expression: `result = a1**2 + b1` |
| 2-5 cells | List comprehension or explicit assignments |
| 6+ cells | `for` loop over row range, or numpy vectorized op |

```python
def pattern_to_python(pattern_key: str, cells: list[dict], var_map: dict) -> str:
    """Generate Python code from a formula pattern group."""
    expr = formula_to_python(f"={pattern_key}", var_map)
    if expr is None:
        return f"# MANUAL: {pattern_key} ({len(cells)} cells)"

    if len(cells) == 1:
        return f"result = {expr}"

    # Detect row range
    rows = sorted(int(c["cell_ref"].lstrip("ABCDEFGHIJKLMNOPQRSTUVWXYZ")) for c in cells)
    start, end = rows[0], rows[-1]

    # Identify column variables used in the formula
    return (
        f"# Pattern: {pattern_key} ({len(cells)} rows)\n"
        f"for i in range({start}, {end + 1}):\n"
        f"    result[i] = {expr}  # row-indexed"
    )
```


## Compression Statistics (POC Evidence)


From WRK-1247 conductor length assessment (2,699 formulas):

| Metric | Excel | Python |
|--------|-------|--------|
| Total formula instances | 2,699 | — |
| Unique patterns | 132 | ~132 functions |
| Loop-able (≥3 repetitions) | 64 patterns (2,629 cells) | 64 `for` loops |
| One-off formulas | 70 | 70 expressions |
| **Compression ratio** | — | **20x** |

97% of formulas are loop candidates.


## Translation Yield by Complexity (POC Evidence)


| Formula Type | Auto-translatable | Example |
|-------------|-------------------|---------|
| Simple arithmetic | Yes (68%) | `=E42*25.4/1000` → `e42*25.4/1000` |
| Trig / math functions | Yes | `=PI()/4*D^2` → `math.pi/4*d**2` |
| String concatenation | No | `=A1&" text"` |
| VLOOKUP/INDEX/MATCH | No — use `formulas` lib | `=VLOOKUP(A1,B:C,2)` |
| IF/IFS | No — use `formulas` lib | `=IF(A1>0,B1,C1)` |

For untranslatable formulas, use the `formulas` library to compile the workbook
into a callable `DispatchPipe`, then call it with varied inputs.


## Pipeline: Extract → Detect Patterns → Generate Python


```
1. Dual-pass load (openpyxl)           → formula strings + cached values
2. Normalize formulas (Translator)     → canonical row-1 forms
3. Group by pattern                    → {pattern: [rows]}
4. For each pattern:
   a. Translate formula → Python expr  → formula_to_python()
   b. Determine loop/single/vectorize  → based on group size
   c. Generate function + test         → with Excel values as assertions
5. Assemble module                     → one .py file per sheet
```
