---
name: excel-workbook-to-python-cowork
description: Convert engineering Excel workbooks to Python code using Claude Desktop cowork on Windows. Benchmarked superior output with 24 vs 7 functions and 81 vs 53 tests for Ballymore jumper.
trigger: User asks to convert an Excel workbook to Python code, or references workbook conversion tasks
effort: medium
---

# Excel Workbook to Python - Claude Cowork on Windows

## Why Windows Cowork Outperforms Linux Headless

From Ballymore jumper benchmark (#471) comparing both approaches on same workbook:

- Windows - 24 functions, 81 passing tests, 27-section OrcaFlex breakdown
- Linux - 7 functions, 53 passing tests, basic section counts only

Windows also produced: COG calculations (both insulated and uninsulated variants), pipe weight estimates, comprehensive architecture diagrams with ASCII data flow visualization.

## Execution Machine

- ws014 (licensed-win-2) with Claude Desktop cowork mode and MCP
- Excel and openpyxl installed, pytest for testing
- client_projects repo cloned

## Prompt Template for Cowork

Paste this prompt into Claude Desktop cowork after opening workbook:

```
Convert this workbook to Python code:
Workbook path: {full_path_to.xlsx}
Module name: {module_name}

RULES:
1. Read EVERY sheet with openpyxl - extract all cell values, formulas,
   cross-sheet references, constants, and named ranges. Map full dependency graph.

2. Create {module_name}.py in SAME FOLDER as workbook:
   - Python 3.11+ with dataclasses, typing, and math only
   - Use __post_init__ for derived fields that auto-compute from inputs
   - Separate dataclass per logical input group (pipe props, rigging, etc.)
   - One function per calculation sheet minimum, more if sheet has distinct sections
   - OrcaFlex section breakdown function if workbook has line-type definitions
   - COG functions for both insulated and uninsulated variants if present
   - Named constants for every unit conversion like INCH_TO_M=0.0254
   - Cell reference comment on every derived value like # Source: Sheet!Cell - description
   - run_all() pipeline function returning dict of all results
   - generate_yaml() for OrcaFlex line section generation
   - if __name__ block with summary print
   - CRITICAL: every function must return its result, no exceptions

3. Create test_{module_name}.py in SAME FOLDER:
   - Use pytest framework (NOT unittest)
   - One test class per sheet with setup_method
   - Test every intermediate and final computed value
   - Test cross-sheet data flow between dependent calculations
   - Target 80+ tests per workbook
   - Use pytest.approx with appropriate abs or rel tolerance

4. Create README.md with ASCII architecture diagram showing data flow

5. Run pytest and fix ALL failures before considering complete
```

## Integration Pattern for digitalmodel

After cowork produces code:

1. Verify all tests pass on ws014 with pytest
2. Commit to client_projects repo under engineering_workbooks
3. Copy module to digitalmodel src digitalmodel marine ops installation
4. Copy tests to digitalmodel tests marine ops installation
5. Update module imports to use digitalmodel package path
6. Update init.py exports
7. Create or update spec.yml for the jumper config
8. Commit and push digitalmodel

## Pitfalls Learned

1. Missing return statements - Claude frequently forgets to return results. Always verify every function has a return statement.
2. unittest vs pytest confusion - Claude may generate unittest despite explicit pytest instruction. Convert class methods and assertions if needed.
3. sys.path hardcoded - Test files may have sys.path insert zero slash tmp which breaks imports. Fix to use os.path.dirname of file.
4. Code trapped in Excel cells - If Claude puts code as Excel cell text in column A, extract with openpyxl on Linux by reading all cells in sheet and writing to py file.
5. Multiple jumper variants - Parameterize with JumperConfig dataclass and KNOWN_CONFIGS dict to support multiple jumper models with same pipe but different segment lengths.

## Test Standard

Convert and verify on Linux using workspace-hub virtual environment pytest. All tests must pass before committing. Target 90 percent or higher pass rate on first run. Fix failures iteratively before final commit.

## Pipeline Stages

The full pipeline flows from spec yaml through JumperConfig to run jumper analysis then Go No-Go evaluation then OrcaFlex YAML generation then output file writing. Each stage is independently testable.

## References

- Ballymore MF-PLET converter achieved 1007 lines with 24 functions and 81 tests plus 27 OrcaFlex sections
- Go No-Go logic implements 12 DNV-compliant criteria with 21 tests producing MARGINAL decision
- Pipeline supports both MF-PLET and PLET-PLEM jumper configurations from single code path