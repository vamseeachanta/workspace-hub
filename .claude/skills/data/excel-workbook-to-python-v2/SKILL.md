---
name: excel-workbook-to-python-v2
description: Convert engineering Excel workbooks to Python code using Claude Desktop cowork on Windows. Proven superior quality vs Linux openpyxl extraction (24 vs 7 functions, 81 vs 53 tests). Validated on Ballymore jumper installation analysis.
trigger: User asks to convert an Excel workbook to Python code, or references workbook conversion (#1934, #471)
effort: medium
model: any
context: 7/12/10
---

# Excel Workbook to Python — Claude Cowork on Windows (v2)

## Benchmark Results

| Metric | Windows Cowork | Linux openpyxl |
|--------|---------------|----------------|
| Functions | 24 | 7 |
| Tests passing | 81 | 53 |
| OrcaFlex breakdown | 27-section | Basic counts |
| COG calcs | Insulated + uninsulated | Not implemented |
| Architecture docs | ASCII diagram, formula table | Basic README |
| Code quality | `__post_init__`, typed | Good but fewer features |

## Execution Machine

- **ws014** (licensed-win-2): Claude Desktop with cowork mode + MCP
- Excel installed, openpyxl and pytest available in Python environment
- `client_projects` repo cloned to ws014

## Step-by-Step Workflow

### Step 1: Open Excel workbook on Windows

Open the workbook in Excel. Launch Claude Desktop cowork session.

### Step 2: Copy workbook path

Locate workbook path in `client_projects/engineering_workbooks/`.
Copy full Windows path (e.g., `C:\path\to\client_projects\engineering_workbooks\ballymore\...`).

### Step 3: Prompt in Claude Desktop cowork

```
Convert this workbook to Python:
Workbook: {full Windows path to .xlsx/.xlsm}
Module name: {snake_case_module_name}

RULES:
1. Read EVERY sheet with openpyxl — extract all cell values, formulas,
   cross-sheet refs, constants, and named ranges. Map dependency graph.

2. Create {module_name}.py in the SAME FOLDER as the workbook:
   - Python 3.11+ with dataclasses, typing, math (no external deps)
   - Use __post_init__ for derived fields that auto-compute from inputs
   - Separate dataclass per logical input group (pipe, buoyancy, rigging, etc.)
   - One function per calculation step — at least one per sheet
   - Dedicated function for OrcaFlex section breakdown if workbook has it
   - Dedicated functions for COG (insulated + uninsulated)
   - Dedicated functions for pipe weight estimation
   - Dedicated connector/clamp dataclasses as separate entities
   - Every unit conversion is a named constant (INCH_TO_M = 0.0254, etc.)
   - Every derived value has a cell reference comment: # Source: Sheet!Cell -- description
   - CRITICAL: Every function must return its result (no missing returns!)
   - run_all() pipeline function that returns dict of all results
   - generate_orcaflex_line_sections_yaml() for 27-section line-type breakdown
   - if __name__ == "__main__" block that prints summary

3. Create test_{module_name}.py in the same folder:
   - Use pytest (NOT unittest)
   - One test class per sheet
   - Test every intermediate and final value against spreadsheet formulas
   - Expected values traced to cell references in docstrings
   - Test cross-sheet data flow (e.g. bend_radius from Bare pipe → GA)
   - test_all_sheets_pipeline end-to-end test
   - Target 80+ tests per workbook

4. Create README.md in the same folder:
   - Engineering purpose
   - Architecture data flow diagram (ASCII)
   - Table: Sheet → Function → Dataclass mapping
   - Key formulas with cell references
   - Quick start: how to run module and tests

5. Run: pytest test_{module_name}.py -v — fix ALL failures before finishing

6. CRITICAL PITFALLS — avoid these:
   - ALWAYS return props/results from functions that create them
   - Use os.path.dirname(__file__) for sys.path, NOT hardcoded /tmp
   - Never use unittest — only pytest
   - Handle both dict and dataclass result types
```

### Step 4: Verify on Windows

```bash
python -m pytest test_{module_name}.py -v
```

### Step 5: Save workbook to client_projects repo

```bash
cd client_projects
git add engineering_workbooks/path/to/{module_name}.py
git add engineering_workbooks/path/to/test_{module_name}.py
git commit -m "feat: {workbook_name} — cowork conversion, N tests passing"
git push
```

### Step 6: Copy to digitalmodel repo

```bash
# On ace-linux-1
cd /mnt/local-analysis/workspace-hub/digitalmodel
# Copy module
cp path/to/{module_name}.py src/digitalmodel/marine_ops/installation/
# Copy tests
cp path/to/test_{module_name}.py tests/marine_ops/installation/
# Convert imports: from {module_name} import → from digitalmodel.marine_ops.installation.{module_name} import
# Update __init__.py exports
git commit -m
git push
```

### Step 7: Create spec.yml

Create `docs/domains/orcaflex/subsea/{domain}/spec.yml` following the pattern
from existing `docs/domains/orcaflex/pipeline/installation/` specs.

## Critical Pitfalls

### 1. Missing return statements
Claude sometimes omits `return` in functions that use `__post_init__`:
```python
def compute_buoyancy(props=None):
    if props is None:
        props = BuoyancyModuleProperties()
    return props  # <--- EASY TO MISS
```
**Fix**: Verify EVERY function returns its result. Check the test file for
AttributeError like `'NoneType' object has no attribute` — this means a return was missed.

### 2. sys.path hardcoded to /tmp
Test file may have: `sys.path.insert(0, "/tmp")`
**Fix**: Change to `sys.path.insert(0, os.path.dirname(__file__))`

### 3. unittest vs pytest
Prompt explicitly says pytest. If unittest appears, convert:
- `unittest.TestCase` → plain class
- `setUp(self)` → `self.setup_method()`
- `self.assertAlmostEqual(a, b, places=N)` → `assert a == pytest.approx(b, abs=1e-N)`
- `self.assertEqual(a, b)` → `assert a == b`
- `self.assertTrue(x)` → `assert x`

### 4. Code in Excel cells
If code ends up as Excel column A text (one line per cell), extract with openpyxl:
```python
import openpyxl
wb = openpyxl.load_workbook("workbook.xlsx")
for sheet_name in ["module.py", "test_module.py", "README.md"]:
    ws = wb[sheet_name]
    lines = [str(row[0].value) if row[0].value else "" for row in ws.iter_rows(max_col=1)]
    open(sheet_name, "w").write("\n".join(lines) + "\n")
```

### 5. pyproject.toml conflicts
Run tests with `-o addopts=` to override repo pytest config that adds coverage.

## Conversion Checklist

For each workbook:
- [ ] All sheets have at least one function
- [ ] OrcaFlex line-type section breakdown (if workbook has it)
- [ ] COG calculations (insulated + uninsulated variants)
- [ ] Both insulated and uninsulated weight variants
- [ ] Connector and clamp properties as separate dataclasses
- [ ] Pipe weight estimation per KIT
- [ ] All tests pass on both Windows and Linux
- [ ] run_all() returns all sections in a dict
- [ ] README has data flow diagram with ASCII art
- [ ] spec.yml created for digitalmodel integration

## Integration Pattern

After conversion:
1. Commit to client_projects repo
2. Copy to digitalmodel (update imports)
3. Create/update digitalmodel `__init__.py` exports
4. Create spec.yml in `docs/domains/orcaflex/subsea/`
5. Create GitHub issue for tracking

## Registry Reference

- **Priority list**: `docs/document-intelligence/EXCEL-CONVERSION-PRIORITY.md`
- **Workbook registry**: `docs/document-intelligence/EXCEL-CONVERSION-REGISTRY.md`
- **Workspace-hub issues**: vamseeachanta/workspace-hub#1933-1940
- **Digitalmodel issues**: vamseeachanta/digitalmodel#471-477
