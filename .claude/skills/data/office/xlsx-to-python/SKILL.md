---
name: xlsx-to-python
description: "Convert Excel calculation spreadsheets to Python code \u2014 extract\
  \ formulas, build dependency graphs, generate pytest tests using cell values as\
  \ assertions, and produce dark-intelligence archive YAMLs.\n"
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

# Xlsx To Python

## When to Use

- Porting engineering calculations from Excel to Python
- Extracting calculation methodology from legacy spreadsheets
- Building dark-intelligence archives from XLSX files
- Any time a spreadsheet contains formulas that should become code

## Pre-Conversion Assembly: Multi-Source Workbook Transfer

Before converting, you need all target workbooks collected into a single git repo (typically `client_projects`) that can be transferred to the Windows machine running Claude Desktop.

### Step 0: Inventory and Rank

1. Scan all sources for `.xlsx`, `.xls`, `.xlsm` files (case-insensitive, exclude `~$*` temp files):
   ```bash
   find /mnt/ace/ -type f \( -iname '*.xlsx' -o -iname '*.xls' -o -iname '*.xlsm' \) ! -name '~$*' 2>/dev/null
   find workspace-hub/ -type f \( -iname '*.xlsx' -o -iname '*.xls' -o -iname '*.xlsm' \) ! -name '~$*' ! -path '*/node_modules/*' ! -path '*/.git/*' 2>/dev/null
   ```
2. Read sheets/formulas of each candidate to estimate complexity (use `openpyxl` to list sheet names, count formulas, detect cross-sheet refs)
3. Rank by: GTM value, reusability across projects, complexity (Low/Med/High sheets), and estimated token cost (Low ~500K, Med ~1.5M, High ~3-5M tokens)
4. Create a tracking document with: `INVENTORY -> ANALYZED -> CONVERTED -> VERIFIED` status per workbook

### Step 1: Copy into `client_projects` Repo

The `client_projects` repo is the transfer vehicle to Windows. Workbooks are scattered across `/mnt/ace/` (raw workspace) and workspace-hub sub-repos. Use `rsync` to copy only Excel files while preserving directory structure:

```bash
# Use rsync -- preserve directory tree, copy ONLY xlsx/xls/xlsm
rsync -av --include='*/' --include='*.xlsx' --include='*.xls' --include='*.xlsm' --exclude='*' \
  /mnt/ace/rock-oil-field/s7/ballymore/ client_projects/engineering_workbooks/ballymore/
```

Key findings:
- **client_projects `.gitattributes`** marks `*.xlsx`, `*.xls`, `*.xlsm` as `binary` (not LFS). Large repos will grow proportionally to total file size.
- **/mnt/ace/** is the raw workspace where files are physically present — workspace-hub sub-repos may have sparse overlays where xlsx files are on-disk but not git-tracked.
- **Already-in-repo workbooks**: Check `git ls-files '*.xlsx' '*.xls' '*.xlsm'` to avoid duplicating what's already tracked.
- **Organize under `engineering_workbooks/`** in the repo to avoid path collisions with existing data directories.

### Step 2: Legal Scan

Run legal compliance before committing:
```bash
bash scripts/legal/legal-sanity-scan.sh  # from workspace-hub root
```

### Step 3: Commit and Push

```bash
cd client_projects
git add engineering_workbooks/
git commit -m "feat(doc-intelligence): add #N engineering workbooks for Excel-to-code conversion"
git push
```

### Step 3b: Quality Validation After Conversion

After each batch is converted on Windows (ws014), validate before accepting:

1. **Pull the converted code** from `client_projects` repo back to Linux
2. **Run the full test suite** — all tests must pass (zero failures)
3. **Fix bugs before accepting** — Claude-in-Excel often produces code with:
   - Missing `return` statements in factory functions (common pattern: `if props is None: props = ClassName()` without `return props`)
   - Wrong `sys.path` entries in test files
   - Import paths that assume Windows directory structure
4. **Compare capabilities vs workbook** — ensure every sheet's calculations are covered

### Step 4: Track Progress

Maintain two docs in `docs/document-intelligence/`:
- `EXCEL-CONVERSION-PRIORITY.md` — ranked list with budget estimates per workbook
- `EXCEL-CONVERSION-REGISTRY.md` — detailed sheet-level analysis, cross-sheet references, target Python modules

### Step 5: Transfer to Windows Machine

The **execution machine is ws014** (Windows). Transfer via:
```bash
git clone git@github.com:vamseeachanta/client_projects.git  # on ws014
```

**The conversion prompt runs in Claude Code on ws014** — NOT the Copilot in Excel add-in and NOT Cowork. Copilot in Excel can only read cell values and explain formulas; it cannot write Python files, create tests, or organize code into repos. Claude Code has full filesystem access and can use openpyxl to read Excel files, extract formula logic, write Python modules, and create PRs.

### Step 5b: Large File Bypass (if needed)

If git hooks block files > 5MB:
```bash
git commit --no-verify  # bypasses size check hooks in client_projects
```
This is safe for intentional Excel workbook staging in `engineering_workbooks/`.

### Step 6: Round-Trip — Code Back to Repos

Once workbooks are converted to Python:
- **Target repos**: `digitalmodel/` (engineering algorithms), `assetutilities/` (production/utilities)
- **Traceability**: Name Python modules after the source workbook, include link to workbook in docstring
- **Tests**: Assert outputs match original spreadsheet cell values
- **Commit**: From within the target repo directory (per workspace-hub convention)
- **Update registry**: Mark workbook as `CONVERTED` and `VERIFIED` with link to PR

## Conversion Quality Requirements

Established quality bar from first conversion (Ballymore Jumper, 7 sheets, 2.3MB):

### Minimum Bar (must achieve per workbook)

- **Tests**: All must pass with zero failures. Claude-in-Excel commonly produces buggy code that needs fixing.
- **Common bugs to check**:
  - Missing `return props` in factory functions (the pattern `if props is None: props = ClassName()` without returning is the most common bug)
  - Wrong `sys.path` in test files (pointing to `/tmp` or hardcoded Windows paths)
  - Functions that create default instances but don't use them
- **Coverage scope**: Every sheet must have at least one test class covering its calculations
- **Formula fidelity**: Each test assertion must include cell reference comment (e.g., `# Bare pipe!H4 = PI()*(E4²-E5²)/4*7850`)
- **Type hints**: All function signatures must have types
- **Constants**: Every magic number must be a named constant with comment

### Claude-in-Excel vs Native CLI Comparison

| Aspect | Windows Claude Code | Linux openpyxl |
|--------|-------------------|----------------|
| Completeness | Typically more thorough (24 functions vs 7 for Ballymore) | Adequate but may miss edge cases |
| Test coverage | Higher test count (81 vs 53 for Ballymore) | Solid but less comprehensive |
| Documentation | Includes architecture diagrams, data flow graphs | Basic README |
| OrcaFlex output | Produces full line-type section breakdown | May skip |
| COG calculations | Both insulated + uninsulated variants | Often skipped |
| Code quality | More bugs (5-16 of 81 tests fail before fixes) | Cleaner on first run |
| Usability | Code may be trapped in Excel cells, needs extraction | Immediately runnable .py files |

**Recommendation**: Run conversion on ws014 (Windows) using Claude Desktop cowork.
The quality advantage (24 vs 7 functions, 81 vs 53 tests, COG, full OrcaFlex breakdown)
outweighs the 10-20% failure rate which is fixable with the known bug list below.
Linux gives clean but less complete code.

### Known Bugs in Windows Cowork Output (fix before accepting)

Buggy pattern #1 — most common (16/81 failures in Ballymore):
```python
def compute_buoyancy(props=None):
    if props is None:
        props = BuoyancyModuleProperties()
    # MISSING: return props  <-- BUG
```
Fix: Ensure EVERY `compute_*` function returns its result.

Buggy pattern #2:
```python
sys.path.insert(0, "/tmp")  # Wrong path
```
Fix: `sys.path.insert(0, os.path.dirname(__file__))`

Buggy pattern #3:
```python
import unittest  # Prompt says pytest
```
Fix: Convert to pytest. Use this conversion guide:
- `self.assertAlmostEqual(a, b, places=N)` -> `assert a == pytest.approx(b, abs=1e-N)`
- `self.assertEqual(a, b)` -> `assert a == b`
- `self.assertTrue(x)` -> `assert x`
- `self.assertGreater(a, b)` -> `assert a > b`
- `self.assertLess(a, b)` -> `assert a < b`
- `self.assertIn(a, b)` -> `assert a in b`
- `class TestX(unittest.TestCase):` -> `class TestX:`
- `def setUp(self):` -> `def setup_method(self):`

Buggy pattern #4:
- Code output as Excel cell text (column A of new sheet) instead of .py file
- Extract with: open workbook, read cell values from that sheet column A, write to .py file

### Preferred Architecture Pattern

For each workbook, produce:

```python
# Dataclasses with separate input/property/result separation
@dataclass
class BarePipeInputs:
    od_in: float = 10.75
    wt_in: float = 1.79
    bend_radius_in: float = 50.0
    insul_od_in: float = 16.75
    insul_density_lb_ft3: float = 61.1

@dataclass
class PipeProperties:
    # All computed properties, populated by calculate_* functions
    od_m: float = 0.0
    # ...
```

This pattern avoids the `__post_init__` trap where derived fields auto-compute but tests can't verify intermediate steps. Keep functions separate from data.

## Integration with digitalmodel

After conversion, integrate into the digitalmodel repo:
1. Copy module → `src/digitalmodel/marine_ops/installation/{module}.py`
2. Copy tests → `tests/marine_ops/installation/test_{module}.py`
3. Create spec.yml → `docs/domains/orcaflex/subsea/{domain}/installation/{project}/spec.yml`
4. Update `__init__.py` to export new functions
5. Use `JumperConfig` pattern for parametric multi-model support:
```python
@dataclass
class JumperConfig:
    name: str = "default"
    seg_a_inch: float = 336.0  # segment lengths
    # ... all configurable params

KNOWN_CONFIGS = {
    "model_a": JumperConfig(name="model_a", seg_a_inch=336.0, ...),
    "model_b": JumperConfig(name="model_b", seg_a_inch=400.0, ...),
}
```
6. Create `generate_orcaflex_line_sections_yaml()` function for model pipeline

## Round-Trip Validation Checklist

For each converted workbook:
1. [ ] Module runs without errors: `python {module}.py`
2. [ ] All tests pass: `python -m pytest test_{module}.py -v`
3. [ ] Key values match spreadsheet to 6 decimal places
4. [ ] Cross-sheet references work correctly (e.g. bend radius flowing from Bare pipe to GA)
5. [ ] Weight tally grand total matches spreadsheet
6. [ ] README documents engineering purpose, sheet coverage, usage examples
7. [ ] No missing return statements in compute_* functions (check ALL of them)
8. [ ] No hardcoded sys.path in tests

## Batch Tracking with GitHub Issues

For multi-workbook conversion campaigns, create a parent feature issue + child issues per batch:

```bash
# Parent feature: overall scope, budget, checklist
gh issue create --title "FEATURE: Excel-to-Code Conversion Pipeline — N workbooks via ws014" \
  --label "cat:engineering" --label "cat:data-pipeline"

# Child issues: one per domain (e.g. Ballymore, FDAS, Talos Venice)
gh issue create --title "Batch 1: Ballymore Jumper — 10 workbooks" \
  --add-label "cat:engineering,cat:data-pipeline,domain:document-intelligence"
```

Each child issue lists every workbook with: source path, domain, sheet count, expected target Python module, and checklist items for converted deliverables.

Budget model: Low ~500K-1M tokens (1-3 sheets, simple math), Med ~1M-2M tokens (2-7 sheets, cross-refs), High ~2M-5M tokens (7+ sheets, macros, iteration, complex engineering).

## Sub-Skills

- [Core Principle: Excel Values = Test Data](core-principle-excel-values-test-data/SKILL.md)
- [Recommended Stack (+2)](recommended-stack/SKILL.md)
- [openpyxl Limitation (+3)](openpyxl-limitation/SKILL.md)
- [Step 1 — Dual-Pass Loading (+5)](step-1-dual-pass-loading/SKILL.md)
- [Step 6 — Calculation Block Detection](step-6-calculation-block-detection/SKILL.md)
- [Test Assertion Patterns by Data Type (+1)](test-assertion-patterns-by-data-type/SKILL.md)
- [Dark Intelligence Archive Generation](dark-intelligence-archive-generation/SKILL.md)
- [Using `formulas` for Complex Workbooks](using-formulas-for-complex-workbooks/SKILL.md)
- [Why Parametric Variations Are Required (+4)](why-parametric-variations-are-required/SKILL.md)
- [Research Finding: No Existing Library Does This (+5)](research-finding-no-existing-library-does-this/SKILL.md)
- [Integration with Existing Pipeline](integration-with-existing-pipeline/SKILL.md)
- [Checklist](checklist/SKILL.md)
