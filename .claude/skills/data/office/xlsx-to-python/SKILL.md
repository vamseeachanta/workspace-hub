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
