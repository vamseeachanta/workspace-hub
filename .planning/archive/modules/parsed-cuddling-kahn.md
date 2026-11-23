# WRK-1269: POC v2 — Pattern-aware XLSX-to-Python

## Context

WRK-1247 extracted formulas from 10 XLSX files and produced 187K test stubs (one per cell).
This WRK produces **compact Python code** — the conductor workbook's 2,699 formulas become
~132 functions with 64 loops. Output should look like engineer-written Python, not a cell dump.

**Key insight**: Engineering spreadsheets repeat the same formula across rows (one per depth,
time step, load case). `openpyxl.formula.translate.Translator` normalizes formulas to row-1
canonical form. Identical normalized formulas share a pattern → collapse to a `for` loop.

## Pipeline

```
formulas.yaml (v1) → detect patterns → loop collapse → assemble .py module
                                                      → generate tests
                                                      → generate calc-report YAML → HTML
```

Reuses v1 extraction outputs — no need to re-parse XLSX files.

## Files to Create

All in `scripts/data/doc_intelligence/`:

| # | File | Purpose | ~Lines |
|---|------|---------|--------|
| 1 | `pattern_detector.py` | Normalize formulas via Translator, group by pattern, compression stats | 120 |
| 2 | `loop_collapse_generator.py` | Pattern group → Python code (single/explicit/loop) | 200 |
| 3 | `module_assembler.py` | Assemble one .py file per workbook (<500 lines) | 180 |
| 4 | `test_generator_v2.py` | Baseline + 10 parametric variations per function | 160 |
| 5 | `calc_report_from_patterns.py` | Calc-report YAML from patterns (not per-cell) | 150 |
| 6 | `run_poc_v2.py` | Orchestrate pipeline across 6 processable files | 200 |

Each gets a test file in `tests/`.

## Existing Code Reused

| File | Function Used |
|------|--------------|
| `formula_to_python.py` | `formula_to_python()`, `can_translate()` — translate pattern → Python expr |
| `formula_reference_parser.py` | `parse_formula_references()` — build var_map |
| `formula_chain_builder.py` | `build_dependency_graph()`, `classify_cells()` — input/output classification |
| `run_poc_extraction.py` | Structural pattern for runner |

## Build Order (TDD — tests first each phase)

### Phase 1: `pattern_detector.py`
- `normalize_formula(formula, cell_ref)` → canonical row-1 form via Translator
- `detect_row_patterns(formulas)` → `{canonical: [cells]}`
- `compute_compression_stats(patterns)` → total/unique/ratio
- Tests: hand-crafted formulas, absolute refs, mixed refs, 10K synthetic perf test

### Phase 2: `loop_collapse_generator.py` (depends on Phase 1)
- `pattern_to_python_code(pattern, cells, var_map)` → dispatches by group size:
  - 1 cell → single expression
  - 2-5 cells → explicit assignments
  - 6+ cells → `for` loop
- `generate_function_from_pattern(name, pattern, cells, var_map, inputs)` → `def` function
- Tests: each size bucket, untranslatable → `# MANUAL:` stub, `ast.parse()` validity

### Phase 3: `module_assembler.py` (depends on Phase 2)
- `assemble_module(stem, patterns, classification, named_ranges, domain)` → complete .py
- Groups functions by sheet, adds imports, docstring, main()
- Constraint: <500 lines per module
- Tests: synthetic workbook → valid Python, line count, function count

### Phase 4: `test_generator_v2.py` (depends on Phase 1, parallel with 3)
- `generate_test_module(stem, patterns, classification, formulas)` → test file
- Baseline: `pytest.approx(cached_value)` per output
- Parametric: 10 variations (nominal, all-min, all-max, one-at-a-time, stress, near-zero, large, random)
- Tests: known cached values, exactly 10 variations, `ast.parse()`

### Phase 5: `calc_report_from_patterns.py` (depends on Phase 1, parallel with 3-4)
- `generate_calc_report_yaml(stem, patterns, classification, formulas, domain, stats)` → dict
- Lists unique patterns as equations (not all cells)
- Conforms to `config/reporting/calculation-report-schema.yaml`
- Tests: required sections present, equation count = unique patterns

### Phase 6: `run_poc_v2.py` (depends on all above)
- Reads `poc-file-list.yaml` + v1 `formulas.yaml` per stem
- Runs full pipeline per file → writes to `xlsx-poc-v2/<stem>/`
- Generates HTML via `scripts/reporting/generate-calc-report.py`
- Writes `compression-report.yaml` across all files
- Tests: synthetic data end-to-end, output file existence

### Phase 7: Integration validation
- Run on all 6 files
- Spot-check conductor workbook: ~132 functions, ~64 loops
- `ast.parse()` all generated .py files
- Run generated tests
- Verify compression report

## Output per workbook

```
knowledge/dark-intelligence/xlsx-poc-v2/<stem>/
  patterns.yaml         # detected patterns + compression stats
  calculations.py       # Python module with functions + loops
  test_calculations.py  # baseline + parametric tests
  calc-report.yaml      # structured calc-report
  report.html           # rendered HTML
```

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| 647K formulas in flowback calculator | Process per-sheet, not per-workbook |
| Translator fails on array/structured refs | try/except → raw formula as singleton pattern |
| Translation rate <60% on some files | Untranslatable → `# MANUAL:` stubs, track rate per file |
| Module >500 lines | Line-count check, merge small helpers into dict-calculator |

## Verification

```bash
# Run all tests
uv run --no-project --with openpyxl --with pytest --with networkx --with PyYAML \
  python -m pytest scripts/data/doc_intelligence/tests/test_pattern_detector.py \
  scripts/data/doc_intelligence/tests/test_loop_collapse_generator.py \
  scripts/data/doc_intelligence/tests/test_module_assembler.py \
  scripts/data/doc_intelligence/tests/test_test_generator_v2.py \
  scripts/data/doc_intelligence/tests/test_calc_report_from_patterns.py \
  scripts/data/doc_intelligence/tests/test_run_poc_v2.py -v

# Full POC run
uv run --no-project --with openpyxl --with networkx --with PyYAML \
  python scripts/data/doc_intelligence/run_poc_v2.py

# Validate generated Python
uv run --no-project python -c "
import ast, glob
for f in glob.glob('knowledge/dark-intelligence/xlsx-poc-v2/*/calculations.py'):
    ast.parse(open(f).read()); print(f'OK: {f}')
"
```
