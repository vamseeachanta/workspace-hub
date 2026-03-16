---
name: xlsx-to-python
description: 'Convert Excel calculation spreadsheets to Python code — extract formulas,
  build dependency graphs, generate pytest tests using cell values as assertions,
  and produce dark-intelligence archive YAMLs.

  '
version: 1.0.0
category: data
type: skill
trigger: manual
auto_execute: false
capabilities:
- formula_extraction
- vba_macro_extraction
- dependency_graph_building
- named_range_mapping
- calculation_chain_analysis
- test_generation_from_cell_values
- dark_intelligence_archive
- calc_report_generation
tools:
- Read
- Write
- Edit
- Bash
- Grep
- Glob
related_skills:
- openpyxl
- dark-intelligence-workflow
- calculation-report
- doc-intelligence-promotion
triggers:
- xlsx to python
- excel to python
- extract formulas from excel
- convert spreadsheet to code
- xlsx formula extraction
tags:
- excel
- xlsx
- formulas
- python
- tdd
- dark-intelligence
scripts_exempt: true
---

# XLSX-to-Python Conversion Skill

> Convert Excel calculation spreadsheets into Python functions + pytest tests.
> The spreadsheet's own computed values are the ground truth for test assertions.

## Core Principle: Excel Values = Test Data

When an Excel spreadsheet contains a calculation with input values and computed
results, **those cell values are the test cases**. The two-pass extraction strategy:

- **Pass 1** (`data_only=True`): read computed cell values — these become `pytest.approx()` assertions
- **Pass 2** (`data_only=False`): read formula strings — these become Python function implementations

This means every spreadsheet with formulas is simultaneously a specification,
an implementation reference, AND a test fixture.

## When to Use

- Porting engineering calculations from Excel to Python
- Extracting calculation methodology from legacy spreadsheets
- Building dark-intelligence archives from XLSX files
- Any time a spreadsheet contains formulas that should become code

## Python Libraries — Landscape & Selection

### Recommended Stack

| Library | Purpose | Install | Status |
|---------|---------|---------|--------|
| **openpyxl** | Cell values + formula strings + named ranges | `uv add openpyxl` | Active, stable |
| **formulas** | Formula parsing, AST, dependency graph, evaluation | `uv add formulas` | Active (v1.3.3) |
| **networkx** | Dependency graph analysis (topological sort) | `uv add networkx` | Active, stable |
| **oletools** | VBA macro source code extraction from .xlsm/.xls | `uv add oletools` | Active, stable |

### Alternative Libraries (evaluated, not primary)

| Library | What It Does | Why Not Primary | When to Use |
|---------|-------------|-----------------|-------------|
| **pycel** | Compiles Excel to executable Python + graph viz | Broader scope than needed; heavier dependency | When you need full workbook simulation |
| **xlcalculator** | Converts Excel formulas to Python + evaluates | Inactive (no releases in 12+ months); modernized koala2 | Reference for formula-to-Python translation patterns |
| **graphedexcel** | Cell dependency graph visualization (networkx + matplotlib) | Viz-only; no formula parsing | Quick visual audit of spreadsheet complexity |
| **excel-dependency-graph** | Directed graph of formula dependencies | Lightweight but limited features | Simple dependency mapping without evaluation |
| **formula-dependency-excel** | Cell dependency extraction | Minimal; proof-of-concept level | Quick prototyping |

### Key Insight from `formulas` Library

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

## VBA Macro Extraction (XLSM Files)

When an Excel file is macro-enabled (`.xlsm`), it contains VBA source code that often
implements iterative solvers, custom functions, input validation, or multi-step
calculation orchestration. This VBA code maps almost directly to Python functions,
making macro-enabled files the highest-value extraction targets.

### openpyxl Limitation

openpyxl can *preserve* VBA with `keep_vba=True` but treats `vbaProject.bin` as an
opaque binary blob — it cannot read the VBA source code.

### oletools/olevba — VBA Source Extraction

```python
from oletools.olevba import VBA_Parser

def extract_vba_code(filepath: str) -> list[dict]:
    """Extract VBA macro source code from .xlsm/.xls files."""
    macros = []
    try:
        vba_parser = VBA_Parser(filepath)
        if vba_parser.detect_vba_macros():
            for filename, stream_path, vba_filename, vba_code in vba_parser.extract_macros():
                macros.append({
                    "filename": vba_filename,
                    "stream_path": stream_path,
                    "code": vba_code,
                    "type": _classify_vba(vba_code),
                })
        vba_parser.close()
    except Exception as exc:
        macros.append({"error": str(exc)})
    return macros

def _classify_vba(code: str) -> str:
    """Classify VBA code block type."""
    code_lower = code.lower()
    if "function " in code_lower:
        return "function"       # Custom functions called from cell formulas
    elif "sub " in code_lower:
        return "subroutine"     # Macros / event handlers
    elif "type " in code_lower:
        return "type_definition" # User-defined types
    return "module"             # Module-level code
```

### VBA → Python Translation Patterns

| VBA Pattern | Python Equivalent |
|-------------|------------------|
| `Function CalcStress(P, D, t) As Double` | `def calc_stress(p: float, d: float, t: float) -> float:` |
| `Dim x As Double` | `x: float` (type annotation) |
| `If ... Then ... ElseIf ... End If` | `if ... elif ... else:` |
| `For i = 1 To N ... Next i` | `for i in range(1, n + 1):` |
| `Do While ... Loop` | `while ...:` |
| `Application.WorksheetFunction.VLookup(...)` | `np.interp(...)` or dict lookup |
| `GoTo ErrorHandler` | `try/except` |
| `ReDim arr(1 To N)` | `arr = [0.0] * n` |
| `Cells(row, col).Value` | Function parameter or return value |

### When VBA Exists — Enhanced Extraction Flow

```
1. Detect .xlsm → extract VBA via oletools
2. Parse VBA Function/Sub signatures → Python function stubs
3. Extract formulas via openpyxl dual-pass (values + formulas)
4. Cross-reference: cell formulas that call VBA functions
5. VBA function body → Python implementation
6. Cell values → pytest assertions (same as non-macro path)
```

VBA functions are often called from cell formulas as UDFs (User Defined Functions).
When a formula like `=CalcStress(B2, B3, B4)` is found, the VBA `Function CalcStress`
provides the implementation and the cell value provides the test assertion.

## Extraction Pipeline

### Step 1 — Dual-Pass Loading

```python
from openpyxl import load_workbook

def load_xlsx_dual_pass(filepath: str):
    """Load workbook twice: values + formulas."""
    # Pass 1: computed values (for test assertions)
    wb_values = load_workbook(filepath, data_only=True)

    # Pass 2: formula strings (for implementation)
    wb_formulas = load_workbook(filepath, data_only=False)

    return wb_values, wb_formulas
```

**Critical note:** `data_only=True` reads cached values from the last Excel save.
If the file was saved without recalculation (programmatic exports, LibreOffice,
manual-calc mode), ALL formula cells return `None`. This would silently produce
vacuous tests (`assert result == None`).

### Cache Quality Gate (MANDATORY)

Every formula cell must be classified before test generation:

```python
def classify_cache_quality(formula_cells: list[dict]) -> dict:
    """Classify cache quality for each formula cell."""
    stats = {"total": 0, "ok": 0, "missing": 0, "suspect": 0}
    for cell in formula_cells:
        stats["total"] += 1
        if cell["value"] is None:
            cell["cache_status"] = "cached_missing"
            stats["missing"] += 1
        else:
            cell["cache_status"] = "cached_ok"
            stats["ok"] += 1

    # File-level threshold: >50% missing = uncalculated file
    if stats["total"] > 0 and stats["missing"] / stats["total"] > 0.5:
        return {**stats, "file_status": "uncalculated",
                "action": "skip test generation; use formulas lib as diagnostic fallback"}
    return {**stats, "file_status": "ok", "action": "proceed with test generation"}
```

**Rules:**
- Only `cached_ok` cells emit `pytest.approx()` assertions
- `cached_missing` cells are logged in yield report but produce NO assertions
- If >50% missing, flag file as `uncalculated` — exclude from test generation
- Use `formulas` library as diagnostic fallback only (Excel cached values and
  library-evaluated values answer different questions)

### Step 2 — Formula Cell Identification

```python
def extract_formula_cells(wb_formulas, wb_values):
    """Extract all formula cells with both formula text and computed value."""
    cells = []
    for sheet_name in wb_formulas.sheetnames:
        ws_f = wb_formulas[sheet_name]
        ws_v = wb_values[sheet_name]
        for row in ws_f.iter_rows():
            for cell in row:
                if cell.data_type == 'f' or (
                    isinstance(cell.value, str) and cell.value.startswith('=')
                ):
                    value_cell = ws_v[cell.coordinate]
                    cells.append({
                        "sheet": sheet_name,
                        "ref": cell.coordinate,
                        "formula": cell.value,
                        "value": value_cell.value,
                        "row": cell.row,
                        "col": cell.column,
                    })
    return cells
```

### Step 3 — Named Range Extraction

```python
def extract_named_ranges(wb):
    """Extract all defined names as variable definitions."""
    named_ranges = []
    for defn in wb.defined_names.definedName:
        destinations = list(defn.destinations)
        for sheet_title, cell_ref in destinations:
            named_ranges.append({
                "name": defn.name,
                "sheet": sheet_title,
                "cell_ref": cell_ref,
                "scope": "workbook" if defn.localSheetId is None else sheet_title,
            })
    return named_ranges
```

### Step 4 — Formula Reference Parsing

Parse cell references from Excel formula strings:

```python
import re

# Matches: A1, $A$1, A$1, $A1, Sheet1!A1, 'Sheet Name'!A1
CELL_REF_RE = re.compile(
    r"(?:'([^']+)'!|([A-Za-z_]\w*)!)?"  # optional sheet prefix
    r"(\$?[A-Z]{1,3}\$?\d+)"             # cell reference
    r"(?::(\$?[A-Z]{1,3}\$?\d+))?"       # optional range end
)

def parse_formula_references(formula: str) -> list[str]:
    """Extract cell references from an Excel formula string."""
    refs = []
    for match in CELL_REF_RE.finditer(formula):
        sheet = match.group(1) or match.group(2) or ""
        start_ref = match.group(3).replace("$", "")
        end_ref = match.group(4)
        prefix = f"{sheet}!" if sheet else ""
        refs.append(f"{prefix}{start_ref}")
        if end_ref:
            refs.append(f"{prefix}{end_ref.replace('$', '')}")
    return refs
```

### Step 5 — Dependency Graph & Chain Building

```python
import networkx as nx

def build_dependency_graph(formula_cells: list[dict]) -> nx.DiGraph:
    """Build directed graph: edges point from dependency → dependent."""
    G = nx.DiGraph()
    for cell in formula_cells:
        cell_id = f"{cell['sheet']}!{cell['ref']}"
        G.add_node(cell_id, **cell)
        for ref in parse_formula_references(cell["formula"]):
            # Normalize: add sheet prefix if missing
            if "!" not in ref:
                ref = f"{cell['sheet']}!{ref}"
            G.add_edge(ref, cell_id)
    return G

def classify_cells(G: nx.DiGraph) -> dict:
    """Classify cells into inputs, intermediates, outputs."""
    inputs = [n for n in G.nodes() if G.in_degree(n) == 0]
    outputs = [n for n in G.nodes() if G.out_degree(n) == 0
               and G.in_degree(n) > 0]  # must have a formula
    chain = list(nx.topological_sort(G))
    return {"inputs": inputs, "outputs": outputs, "chain": chain}
```

### Step 6 — Calculation Block Detection

Heuristic to separate calculation regions from data/lookup tables:

```python
def detect_calculation_blocks(ws_formulas, min_formula_ratio=0.3):
    """Identify contiguous regions dominated by formulas."""
    blocks = []
    current_block = []
    for row in ws_formulas.iter_rows():
        formula_count = sum(
            1 for c in row
            if isinstance(c.value, str) and c.value.startswith("=")
        )
        total = sum(1 for c in row if c.value is not None)
        if total > 0 and formula_count / total >= min_formula_ratio:
            current_block.append(row[0].row)
        else:
            if len(current_block) >= 2:
                blocks.append((current_block[0], current_block[-1]))
            current_block = []
    if len(current_block) >= 2:
        blocks.append((current_block[0], current_block[-1]))
    return blocks
```

## Test Generation: Excel Values as Assertions

This is the core value proposition. Every formula cell with a cached value
produces a test assertion:

```python
def generate_tests_from_xlsx(
    formula_cells: list[dict],
    named_ranges: list[dict],
    classification: dict,
    module_name: str,
) -> str:
    """Generate pytest file using Excel cell values as ground truth."""
    # Build name lookup: cell_ref → named_range_name
    name_map = {
        f"{nr['sheet']}!{nr['cell_ref']}": nr["name"]
        for nr in named_ranges
    }

    lines = [
        '"""Auto-generated from XLSX extraction — cell values are test assertions."""',
        "import pytest",
        f"# from {module_name} import <function>  # TODO: wire implementation",
        "",
    ]

    # Group outputs by sheet for test organization
    for output_ref in classification["outputs"]:
        cell = next(
            (c for c in formula_cells
             if f"{c['sheet']}!{c['ref']}" == output_ref),
            None,
        )
        if cell is None or cell["value"] is None:
            continue

        func_name = name_map.get(output_ref, cell["ref"]).lower()
        func_name = re.sub(r"[^a-z0-9_]", "_", func_name)

        # Collect inputs for this output by tracing the dependency graph
        lines.append(f"def test_{func_name}_from_xlsx():")
        lines.append(f'    """Extracted: {cell["sheet"]}!{cell["ref"]} = {cell["formula"]}"""')
        lines.append(f"    # Expected value from Excel (ground truth)")

        if isinstance(cell["value"], (int, float)):
            lines.append(f"    expected = {cell['value']}")
            lines.append(f"    # result = <function>(<inputs>)  # TODO")
            lines.append(f"    # assert result == pytest.approx(expected, rel=1e-6)")
        else:
            lines.append(f"    expected = {cell['value']!r}")
            lines.append(f"    # result = <function>(<inputs>)  # TODO")
            lines.append(f"    # assert result == expected")
        lines.append("")

    return "\n".join(lines)
```

### Test Assertion Patterns by Data Type

| Excel Cell Type | Python Test Pattern |
|----------------|-------------------|
| Number (float) | `assert result == pytest.approx(expected, rel=1e-6)` |
| Integer | `assert result == expected` |
| Boolean | `assert result is True/False` |
| String | `assert result == "expected_string"` |
| Date | `assert result == datetime(YYYY, M, D)` |
| Error (#REF!, #N/A) | Skip — log as extraction gap |

### Tolerance Selection

| Domain | Typical Tolerance | Rationale |
|--------|------------------|-----------|
| Structural (stress, force) | `rel=1e-4` | 4 sig figs standard in engineering |
| Geotechnical (soil params) | `rel=1e-3` | Higher uncertainty in soil data |
| Financial (currency) | `abs=0.01` | Cent-level precision |
| General engineering | `rel=1e-6` | Default — tighten if needed |

## Dark Intelligence Archive Generation

Convert extraction results to the canonical archive YAML:

```python
def formula_manifest_to_archive(
    formula_cells: list[dict],
    named_ranges: list[dict],
    classification: dict,
    category: str,
    subcategory: str,
) -> dict:
    """Convert XLSX extraction to dark-intelligence archive YAML."""
    name_map = {
        f"{nr['sheet']}!{nr['cell_ref']}": nr["name"]
        for nr in named_ranges
    }

    archive = {
        "source_type": "excel",
        "source_description": f"{category}/{subcategory} calculation",
        "extracted_date": datetime.now().strftime("%Y-%m-%d"),
        "legal_scan_passed": False,  # Must be set after legal scan
        "category": category,
        "subcategory": subcategory,
        "equations": [],
        "inputs": [],
        "outputs": [],
        "worked_examples": [],
        "assumptions": [],
        "references": [],
    }

    # Map input cells
    for input_ref in classification["inputs"]:
        cell = next(
            (c for c in formula_cells
             if f"{c['sheet']}!{c['ref']}" == input_ref),
            None,
        )
        name = name_map.get(input_ref, input_ref)
        archive["inputs"].append({
            "name": name,
            "symbol": name,
            "unit": "",  # Must be filled manually or from column headers
            "test_value": cell["value"] if cell else None,
        })

    # Map formula cells as equations
    for cell in formula_cells:
        cell_id = f"{cell['sheet']}!{cell['ref']}"
        if cell_id in classification["inputs"]:
            continue
        archive["equations"].append({
            "name": name_map.get(cell_id, cell["ref"]),
            "excel_formula": cell["formula"],
            "latex": "",  # TODO: formula-to-LaTeX translation
            "description": f"Cell {cell['ref']} in {cell['sheet']}",
        })

    # Map output cells
    for output_ref in classification["outputs"]:
        cell = next(
            (c for c in formula_cells
             if f"{c['sheet']}!{c['ref']}" == output_ref),
            None,
        )
        if cell and cell["value"] is not None:
            name = name_map.get(output_ref, output_ref)
            archive["outputs"].append({
                "name": name,
                "symbol": name,
                "unit": "",
                "test_expected": cell["value"],
                "tolerance": 1e-6,
            })

    return archive
```

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

## Parametric Test Variations (MANDATORY)

> **Standard practice for every XLSX-to-Python conversion.**
> The original Excel values are the baseline. Generate 10 additional parameter
> variations to stress-test the implementation across the input range.

### Why Parametric Variations Are Required

A single test point (the original Excel values) proves the implementation matches
at one configuration. Engineering calculations must be valid across their input
range. Parametric variations catch:
- Off-by-one errors in unit conversions
- Boundary condition failures (zero, negative, extreme values)
- Formula implementation bugs that happen to pass at one point
- Missing edge case handling

### The 10-Variation Rule

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

### Implementation Pattern

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

### How to Get Reference Values for Variations

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

### Generating Variations from Archive YAML

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

## Integration with Existing Pipeline

| Component | How This Skill Integrates |
|-----------|--------------------------|
| `parsers/xlsx.py` | Existing parser handles values; this skill adds formula layer |
| `parsers/formula_xlsx.py` | New parser created by WRK-1247 using patterns from this skill |
| `deep_extract.py` | Extended with formula extraction path for XLSX files |
| `dark-intelligence-workflow` | Step 2 (Extract) uses this skill's extraction pipeline |
| `calculation-report` | Step 7 output follows calc-report YAML schema |
| `legal-sanity-scan` | HARD GATE: must pass before archival |

## Checklist

- [ ] Dual-pass load (values + formulas) — verify cached values exist
- [ ] All formula cells extracted with both formula text and computed value
- [ ] Named ranges mapped to variable names
- [ ] Dependency graph built and classified (inputs/intermediates/outputs)
- [ ] Calculation blocks identified (vs data/lookup tables)
- [ ] Baseline tests generated using Excel cell values as `pytest.approx()` assertions
- [ ] 10 parametric variations generated per calculation (all-min, all-max, one-at-a-time, stress combo, near-zero, large, random)
- [ ] Parametric tests verify at minimum: result is finite, within physical bounds
- [ ] Dark-intelligence archive YAML produced with `legal_scan_passed: false`
- [ ] Legal scan passed — set `legal_scan_passed: true`
- [ ] Calc-report YAML generated from archive
