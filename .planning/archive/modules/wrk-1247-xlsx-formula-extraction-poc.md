# WRK-1247: POC — Deep XLSX Formula Extraction

## Context

The document intelligence pipeline extracts tables from XLSX files via `parsers/xlsx.py`,
but uses `data_only=True` (line 46) — only cell values, not formulas. This POC enhances
extraction to capture formulas, named ranges, and calculation chains from 10 selected
spreadsheets, proving the approach before scaling to 23K XLSX files.

## Key Insight: Excel Values = Test Data

Every Excel spreadsheet with formulas is simultaneously a specification, implementation
reference, AND test fixture. The cell values computed by Excel are the ground truth —
they become `pytest.approx()` assertions for the converted Python code. No separate
test data creation needed.

### Cache Quality Gate (from cross-review)

`data_only=True` returns the LAST CACHED value stored in XML. If a spreadsheet was
saved without recalculation (programmatic exports, LibreOffice, manual-calc mode),
ALL formula cells return `None`. This would silently produce vacuous tests.

**Mitigation — cache quality classification:**

Each formula cell is classified before test generation:
- `cached_ok`: has non-None cached value → emit `pytest.approx()` assertion
- `cached_missing`: cached value is None → log warning, do NOT emit assertion
- `cached_suspect`: value exists but file metadata suggests no recalculation → flag

**Threshold:** if >50% of formula cells are `cached_missing`, flag file as
`uncalculated` in yield report. Use `formulas` library as diagnostic fallback
to compute values (not as primary path — Excel cached values and library-evaluated
values answer different questions).

## Safety Boundaries

1. **VBA strings are untrusted data** — never passed to `exec`/`eval`/`compile`
2. **Python stubs are signature-only** with `raise NotImplementedError` — not auto-translated logic
3. **oletools VBA_Parser** wrapped in try/except for corrupted OLE streams
4. **All file paths from project sources** sanitized through legal deny-list before
   appearing in any committed artifact
5. **Source directory names** (`ace_project`, `dde_project`) are internal workspace
   mount paths, NOT client identifiers — but the selection script uses environment
   variables / config mapping, never hardcoded paths in committed code

## Skill Reference

Extraction patterns and library selection: `.claude/skills/data/office/xlsx-to-python/SKILL.md`

Libraries to use:
- **openpyxl**: dual-pass loading (values + formulas), named ranges
- **formulas** (v1.3.3): formula parsing, AST, dependency graph, evaluation for complex workbooks
- **networkx**: dependency graph topological sort
- **oletools**: VBA macro source code extraction from .xlsm files (VBA → Python stubs)

## Architecture Decision

**Create a separate `FormulaXlsxParser`** — do NOT modify the existing `XlsxParser`.

Rationale: the existing parser serves the data pipeline well (fast, read-only, values-only).
Formula extraction produces different output types and serves a different consumer
(dark-intelligence archive vs table CSV export). Isolating the parsers keeps both paths
clean. The `FormulaXlsxParser.can_handle()` accepts both `.xlsx` AND `.xlsm` extensions.

**Schema approach (from Codex review):** Extend `DocumentManifest` with an optional
`formula_payload: Optional[FormulaPayload]` field rather than creating a fully separate
`FormulaManifest` top-level type. This keeps formula data flowing through the existing
serialization pipeline while adding the formula layer.

**Two-pass strategy:**
- Pass 1: `data_only=True` → cell values (reuse existing XlsxParser)
- Pass 2: `data_only=False` → formula strings, named ranges, dependencies
- Merge by cell reference to get both values AND formulas

## Implementation Steps

### Phase 1: Foundation (TDD — Red/Green)

**Step 1: Write tests** → `scripts/data/doc_intelligence/tests/test_formula_xlsx_parser.py`

Tests create synthetic XLSX workbooks via `openpyxl.Workbook()` with known formulas:

| # | Test | Verifies |
|---|------|----------|
| 1 | `test_can_handle_xlsx` | Extension check |
| 2 | `test_parse_simple_formula` | `=A1+B1` → CellFormula with refs `["A1","B1"]` |
| 3 | `test_parse_named_ranges` | Defined name → NamedRange extraction |
| 4 | `test_identify_input_cells` | Literal-value cells referenced by formulas |
| 5 | `test_identify_output_cells` | Formula cells not referenced by others |
| 6 | `test_calculation_chain_order` | Topological sort correctness |
| 7 | `test_cross_sheet_references` | `Sheet1!A1` parsed correctly |
| 8 | `test_empty_workbook` | No crash, empty manifest |
| 9 | `test_formula_reference_parsing` | Regex handles `$A$1`, ranges, cross-sheet |
| 10 | `test_cache_quality_gate_all_ok` | All formula cells have cached values → all `cached_ok` |
| 11 | `test_cache_quality_gate_missing` | Workbook with no cached values → all `cached_missing`, warning |
| 12 | `test_only_cached_ok_cells_emit_assertions` | Test gen skips `cached_missing` cells |
| 13 | `test_extract_vba_macros` | oletools extracts VBA Function/Sub from .xlsm |
| 14 | `test_vba_function_to_python_stub` | VBA Function signature → Python def stub (raises NotImplementedError) |
| 15 | `test_formula_to_archive_yaml` | FormulaPayload → dark-intelligence YAML |
| 16 | `test_formula_to_calc_report` | Chains → calc-report YAML schema |
| 17 | `test_archive_yaml_schema_valid` | All required fields present |

Tests use committed fixture workbooks (handcrafted XML) for cached-value scenarios
and synthetic `openpyxl.Workbook()` for formula parsing / dependency extraction.

**Step 2: Create schema extensions** → modify `schema.py` (+~60 lines)

```python
@dataclass
class CellFormula:
    cell_ref: str            # "B5"
    sheet: str
    formula: str             # "=A5*C3+D2"
    cached_value: Any        # computed value from data-pass (may be None)
    cache_status: str        # "cached_ok" | "cached_missing" | "cached_suspect"
    references: List[str]    # ["A5", "C3", "D2"]

@dataclass
class NamedRange:
    name: str                # "pile_diameter"
    cell_ref: str            # "'Inputs'!$B$3"
    scope: Optional[str]     # sheet name or None (workbook-scoped)

@dataclass
class VbaModule:
    filename: str            # "Module1.bas"
    code: str                # full VBA source text (untrusted — never eval)
    block_type: str          # "function" | "subroutine" | "module"
    signatures: List[str]    # ["Function CalcStress(P, D, t) As Double"]

@dataclass
class FormulaPayload:
    """Optional formula-layer extension for DocumentManifest."""
    formulas: List[CellFormula]
    named_ranges: List[NamedRange]
    input_cells: List[CellFormula]
    output_cells: List[CellFormula]
    calculation_chain: List[str]
    vba_modules: List[VbaModule]     # empty for .xlsx
    cache_quality: dict              # {"total": N, "ok": N, "missing": N, "suspect": N}
```

Added as `DocumentManifest.formula_payload: Optional[FormulaPayload] = None`.

**Step 3: Create formula reference parser** → `formula_reference_parser.py` (~80 lines)

Regex-based extraction of cell references from Excel formula strings:
- Simple: `A1`, `Z99`, `AA100`
- Absolute: `$A$1`, `A$1`, `$A1`
- Ranges: `A1:B10`
- Cross-sheet: `Sheet1!A1`, `'Sheet Name'!A1`
- Functions: extract refs from `SUM(A1:A10)`, `IF(A1>0,B1,C1)` args

**Step 4: Create chain builder** → `formula_chain_builder.py` (~60 lines)

- Build DAG from formula references
- Topological sort → calculation_chain
- Classify input cells (no formula, referenced by formulas) and output cells (formula, not referenced)

**Step 5: Create VBA extractor** → `vba_extractor.py` (~60 lines)

Uses `oletools.olevba.VBA_Parser` to:
- Detect if file is macro-enabled (.xlsm)
- Extract VBA Function/Sub source code as clear text
- Classify blocks (function, subroutine, module)
- Parse VBA function signatures → Python def stubs
- Cross-reference cell formulas that call VBA UDFs (e.g. `=CalcStress(B2,B3)`)

**Step 6: Create FormulaXlsxParser** → `parsers/formula_xlsx.py` (~150 lines)

```python
class FormulaXlsxParser:
    def parse(self, filepath: str, domain: str) -> FormulaManifest:
        # Pass 1: data_only=True → cell values
        # Pass 2: data_only=False → formula strings
        # Merge, build chain, classify inputs/outputs
```

### Phase 2: Integration

**Step 7: Create formula-to-archive converter** → `formula_to_archive.py` (~120 lines)

Maps FormulaManifest → dark-intelligence archive YAML:
- `input_cells` → `inputs:` (name from named range or column header)
- `formulas` → `equations:` (Excel formula → LaTeX for simple ops)
- `output_cells` → `outputs:`
- `named_ranges` → symbol mapping for LaTeX

**Step 8: Modify deep_extract.py** (+~20 lines)

Add formula extraction path: if XLSX/XLSM file detected, run FormulaXlsxParser alongside
existing extraction, produce archive YAML. For .xlsm, also run VBA extraction.

**Step 9: Register parser** → modify `parsers/__init__.py` (1 line)

### Phase 3: POC Execution

**Step 10: Create file selection script** → `select_poc_xlsx.py` (~50 lines)

Query `data/document-index/index.jsonl` for 10 XLSX/XLSM files:
- Filename contains: `calc`, `design`, `analysis`, `check`, `sizing`, `capacity`
- Diverse domains (≥3 disciplines)
- File size > 10KB
- Include at least 2 `.xlsm` files (macro-enabled) if available
- Output: `knowledge/dark-intelligence/xlsx-poc/poc-file-list.yaml`

**Step 11: Run extraction on 10 files**

Per file: FormulaXlsxParser → legal scan → archive YAML → calc-report YAML → pytest tests

Output structure:
```
knowledge/dark-intelligence/xlsx-poc/
  poc-file-list.yaml
  <file-stem>/
    archive.yaml       # dark-intelligence YAML
    calc-report.yaml   # calculation report
    formulas.yaml      # raw FormulaManifest
    tests/test_<stem>.py
```

**Step 12: Write yield report + gap analysis**

## Files Summary

| File | Action | Lines |
|------|--------|-------|
| `tests/test_formula_xlsx_parser.py` | CREATE | ~300 |
| `schema.py` | MODIFY | +70 |
| `formula_reference_parser.py` | CREATE | ~80 |
| `formula_chain_builder.py` | CREATE | ~60 |
| `vba_extractor.py` | CREATE | ~60 |
| `parsers/formula_xlsx.py` | CREATE | ~150 |
| `formula_to_archive.py` | CREATE | ~120 |
| `deep_extract.py` | MODIFY | +25 |
| `parsers/__init__.py` | MODIFY | +1 |
| `select_poc_xlsx.py` | CREATE | ~50 |

All under `scripts/data/doc_intelligence/`.

## Risks

| Risk | Mitigation |
|------|-----------|
| Some XLSX have no formulas (data exports) | Quick-scan during selection; swap out zero-formula files |
| Cached values missing (no recalculation) | Cache quality gate: classify cells, skip `cached_missing` from test gen |
| `data_only=False` slower + more memory | POC is 10 files; add size guard for production |
| Formula regex misses edge cases | Log unparsed refs as warnings; iterate on regex |
| Cross-sheet refs create complex DAGs | POC: per-sheet chains; cross-sheet logged but not unified |
| Legal scan flags content | Run early; have replacement patterns ready |
| VBA from untrusted files | VBA strings are data only — never eval/exec; stubs raise NotImplementedError |
| Corrupted OLE streams in .xlsm | oletools VBA_Parser wrapped in try/except |

## Verification

1. `uv run --no-project python -m pytest scripts/data/doc_intelligence/tests/test_formula_xlsx_parser.py -v` — all 17 tests green
2. Legal scan on all 10 archive YAMLs: `scripts/legal/legal-sanity-scan.sh`
3. Each of 10 files produces: archive.yaml + calc-report.yaml + test file
4. Yield report documents: formulas found, chains mapped, tests generated per file
5. Gap analysis identifies what extractor cannot handle
