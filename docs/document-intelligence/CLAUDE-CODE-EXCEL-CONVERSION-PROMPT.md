# CLAUDE CODE PROMPT FOR WS014
# Save this file and paste into Claude Code on Windows
# Or just use CLAUDE.md in the client_projects repo root

---

PROMPT START =================================================

You are an engineering software developer converting Excel workbooks to Python code.

## Task

Read the Excel workbook at: `{WORKBOOK_PATH}`

Extract ALL calculation logic, formulas, constants, unit conversions, and dependencies from every sheet. Produce a complete Python implementation with tests.

## Analysis Phase

1. Open the workbook with openpyxl: `pip install openpyxl` (or use existing install)
2. For each sheet, identify:
   - Input values (hardcoded numbers)
   - Formula cells (starting with =)
   - Cross-sheet references (SheetName!Cell)
   - Constants (PI conversions, unit factors like 0.0254, 0.453592, 9.81)
   - Named ranges or headers that define structure
3. Map the dependency graph: which cells depend on which other cells
4. Identify the engineering domain and calculation methodology

## Code Generation Phase

Create these files in the same directory as the workbook:

### 1. `{workbook_name}.py` - Main calculation module
- Use Python 3.11+ with dataclasses, typing, and pathlib
- Define dataclasses for all input parameter groups (pipe props, buoyancy, rigging, etc.)
- One function per calculation step (matching each logical section/sheet)
- Hardcoded defaults match the spreadsheet's input values exactly
- Every unit conversion is explicit with a constant factor (INCH_TO_M = 0.0254, LB_TO_KG = 0.453592, etc.)
- Cross-sheet references become function calls or parameter passing
- Add docstrings with engineering context: what calculation, units in/out, formula source
- Add cell references as comments: `# Source: Sheet:GA, Cell:D18 -- straight pipe length in meters`
- Use `math.pi`, `math.sqrt`, `math.cos`, `math.radians` -- no external math libs
- Return typed results (dataclass or dict with descriptive keys)

### 2. `test_{workbook_name}.py` - Test suite
- Use pytest
- One test per sheet or calculation section
- Test inputs taken from the spreadsheet's hardcoded input values
- Test expected outputs computed from the spreadsheet's formulas
- Test both intermediate values AND final results
- For cross-sheet tests, verify the full pipeline produces matching results
- Include a test called `test_all_sheets_pipeline` that runs end-to-end
- Expected values must match the spreadsheet to at least 6 decimal places

### 3. `README.md` - Documentation
- Engineering purpose: what does this workbook calculate
- List all sheets and what each does
- Key formulas/physics used
- How to run tests: `pytest test_{workbook_name}.py -v`
- How to use the module programmatically with example code
- Notes on any assumptions or simplifications
- Link to original workbook filename

## Verification

After creating all files:
1. Run: `python -m pytest test_{workbook_name}.py -v`
2. If any tests fail, debug and fix until ALL pass
3. Double-check that hardcoded inputs in both the module and tests match the spreadsheet exactly

## Style Guidelines

- NO magic numbers -- every constant has a named variable with a comment
- Type hints on all function signatures and dataclass fields
- Follow PEP 8 naming conventions
- Keep functions focused: one calculation step per function
- Use descriptive variable names matching spreadsheet labels (e.g., `bend_radius_inch`, `pipe_od_meter`)

---

PROMPT END =================================================


## HOW TO USE ON WS014

1. Open Claude Code in the client_projects repo directory
2. Run for each workbook:

   Claude Code, convert this workbook to Python:
   
   Workbook: engineering_workbooks/ballymore/jumper_manifold_to_plet/Jumper_Input_Ballymore_Manifold-PLET V2.xlsx
   Module name: jumper_lift
   
   {Paste the analysis + code rules from above}

3. Or save the prompt above as CLAUDE.md in the repo root so it auto-applies

## BATCH MODE (convert entire folder)

If you want to convert ALL workbooks in a folder at once:

   Claude Code, convert ALL Excel workbooks in this folder to Python:
   
   Directory: engineering_workbooks/ballymore/
   
   For EACH .xlsx/.xls/.xlsm file:
   - Create a Python module extracting all calculation logic
   - Create pytest test suite
   - Create README documentation
   - Run tests and fix any failures
   
   {Paste the analysis + code rules from above}
