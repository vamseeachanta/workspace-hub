---
name: xlsx-to-python-step-1-dual-pass-loading
description: "Sub-skill of xlsx-to-python: Step 1 \u2014 Dual-Pass Loading (+5)."
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Step 1 — Dual-Pass Loading (+5)

## Step 1 — Dual-Pass Loading


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


## Cache Quality Gate (MANDATORY)


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


## Step 2 — Formula Cell Identification


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


## Step 3 — Named Range Extraction


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


## Step 4 — Formula Reference Parsing


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


## Step 5 — Dependency Graph & Chain Building


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
