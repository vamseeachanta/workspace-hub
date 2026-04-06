---
name: excel-workbook-to-python-cowork
description: Convert engineering Excel workbooks to Python code using Claude Desktop cowork on Windows. Reads workbook with openpyxl, extracts all formulas and calculation logic, produces Python module + pytest suite + README in the same folder.
trigger: User asks to convert an Excel workbook to Python code, or references issue #1934/#1935 batches
effort: medium
model: any
---

# Excel Workbook to Python — Cowork on Windows

## Context

Proven workflow from Ballymore jumper benchmark (#1935): Windows cowork produces
higher quality code than Linux headless extraction (18 vs 7 functions, 81 vs 53 tests,
full OrcaFlex section breakdown, COG calculations).

## Prerequisites

- Windows machine (ws014 / licensed-win-2) with Claude Desktop cowork mode
- `pip install openpyxl pytest` in the Python environment
- client_projects repo cloned: `git clone https://github.com/vamseeachanta/client_projects`
- Workbook in `engineering_workbooks/` directory (or provide path)

## Workflow

### Step 1: Open workbook in Excel + cowork

Open the workbook in Excel on Windows. Launch Claude Desktop cowork session.
Paste this prompt (replace `{WORKBOOK_PATH}` and `{MODULE_NAME}`):

```
Convert this workbook to Python:
Workbook: {WORKBOOK_PATH}
Module name: {MODULE_NAME}

RULES:
1. Read with openpyxl. For EVERY sheet: extract all cell values, formulas,
   cross-sheet references, constants, and named ranges.
2. Map the dependency graph: which sheets feed into which.
3. Create {MODULE_NAME}.py in the SAME FOLDER as the workbook:
   - Python 3.11+ with dataclasses, typing, math (no external deps)
   - Use __post_init__ for derived fields that auto-compute from inputs
   - Separate dataclass per logical input group (pipe, buoyancy, rigging, etc.)
   - One function per calculation step — at least one per sheet
   - Dedicated function for OrcaFlex section breakdown if workbook has line-type definitions
   - Dedicated functions for COG calculations if present
   - Dedicated functions for uninsulated AND insulated weight variants if both exist
   - Every unit conversion is a named constant (INCH_TO_M = 0.0254, LB_TO_KG = 0.453592, etc.)
   - Every derived value has a cell reference comment: # Source: Sheet!Cell -- description
   - run_all() pipeline function that returns dict of all results
   - if __name__ == "__main__" block that prints summary
4. Create test_{MODULE_NAME}.py in the SAME FOLDER:
   - Use pytest (not unittest)
   - One test class per sheet
   - Test every intermediate and final value against spreadsheet formulas
   - Expected values traced to cell references in docstrings
   - Test cross-sheet data flow (e.g. bend_radius from Bare pipe → GA)
   - test_all_sheets_pipeline end-to-end test
   - Use pytest.approx() with rel=1e-6 or abs as appropriate
5. Create README.md in the SAME FOLDER:
   - Engineering purpose
   - Architecture data flow diagram (ASCII)
   - Table: Sheet → Function → Dataclass mapping
   - Key formulas with cell references
   - Quick start: how to run module and tests
6. Run pytest and fix ALL failures before finishing
7. Return props/results from every function (don't forget return statements)
```

### Step 2: Verify output

After cowork finishes, verify:
1. Module file exists next to workbook: `{MODULE_NAME}.py`
2. Test file exists: `test_{MODULE_NAME}.py`
3. README exists: `README.md`
4. Tests pass: `python -m pytest test_{MODULE_NAME}.py -v`

### Step 3: Commit and push

```bash
cd client_projects
git add engineering_workbooks/path/to/{MODULE_NAME}.py
git add engineering_workbooks/path/to/test_{MODULE_NAME}.py
git add engineering_workbooks/path/to/README.md
git commit -m "feat(#1935): {workbook_name} — cowork conversion, N tests passing"
git push
```

### Step 4: Cross-review on Linux

Pull on ace-linux-1 and verify:
```bash
cd /mnt/local-analysis/workspace-hub/client_projects && git pull
uv run python -m pytest engineering_workbooks/path/to/test_{MODULE_NAME}.py -v -o addopts=
```

## Quality Checklist

- [ ] Every sheet has at least one dedicated function
- [ ] OrcaFlex line-type section breakdown included (if workbook has it)
- [ ] COG (center of gravity) calculations included (if workbook has them)
- [ ] Both insulated and uninsulated weight variants (if both exist)
- [ ] Connector and clamp properties as separate dataclasses
- [ ] Pipe weight estimation per KIT (if present)
- [ ] All tests pass on both Windows and Linux
- [ ] run_all() returns all sections in a dict
- [ ] README has data flow diagram

## Pitfalls

1. **Missing return statements**: Claude sometimes forgets `return props` in
   functions that use `__post_init__`. Always verify every function returns.
2. **sys.path hardcoded to /tmp**: The test file may have `sys.path.insert(0, "/tmp")`.
   Change to `sys.path.insert(0, os.path.dirname(__file__))`.
3. **unittest vs pytest**: Prompt explicitly says pytest. If unittest appears, ask to convert.
4. **Code in Excel cells**: If the code ends up as Excel sheet content (column A text),
   extract to .py files using openpyxl on Linux:
   ```python
   import openpyxl
   wb = openpyxl.load_workbook("workbook.xlsx")
   for sheet_name in ["module.py", "test_module.py", "README.md"]:
       ws = wb[sheet_name]
       lines = [str(row[0].value) if row[0].value else "" for row in ws.iter_rows(max_col=1)]
       open(sheet_name, "w").write("\n".join(lines) + "\n")
   ```
5. **pyproject.toml conflicts**: Run tests with `-o addopts=` to override repo pytest config.

## Batch Processing

For the 100 workbook pipeline (#1934), process in ranked order:
- Priority list: `docs/document-intelligence/EXCEL-CONVERSION-PRIORITY.md`
- Registry: `docs/document-intelligence/EXCEL-CONVERSION-REGISTRY.md`
- Batch issues: #1935 through #1940

Work one batch folder at a time. Each folder in `engineering_workbooks/` maps to a batch.

## Recommendation for Remaining 99 Workbooks

**Use Windows cowork for all conversions.** It produces:
- More granular function decomposition (18+ vs 7)
- Full OrcaFlex section breakdowns when present
- COG calculations for each KIT
- Uninsulated + insulated weight variants
- Better README documentation with architecture diagrams
- 50%+ more test coverage

**Linux role**: Cross-review only. Pull, run tests, verify, commit docs.
