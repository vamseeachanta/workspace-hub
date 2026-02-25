# Plan: Engineering Calculation Translation (Spanish to English)

**Date:** 2026-01-19
**Status:** Implemented
**Author:** Gemini

## Objective
Translate a set of engineering calculation Excel files located in `62092_sesa/data/calculations` from Spanish to English to facilitate international collaboration and review.

## Scope
- **Source Directory:** `/mnt/github/workspace-hub/doris/62092_sesa/data/calculations`
- **Target Files:** All `.xlsx` files in the source directory.
- **Output:** New files with `_en.xlsx` suffix (non-destructive).

## Methodology

### 1. Analysis
- Inspect source files to identify content structure (sheet names, headers, data cells).
- Identify key technical vocabulary requiring translation.
- Determine necessary libraries (`openpyxl` for read/write, `pandas` for inspection).

### 2. Tool Development
- Develop a Python script `scripts/python/translate_excel.py`.
- Implement a dictionary-based translation mechanism.
- **Refinement:** Use Regex for short words (e.g., "DE", "LA") to avoid partial matches in other words, ensuring safer translation.
- **Sheet Names:** Handle Excel constraints (31 character limit for sheet names).

### 3. Translation Dictionary
Key terms identified and mapped:
- **General:** "MEMORIA DE CÁLCULO" -> "CALCULATION REPORT", "INDICE" -> "TABLE OF CONTENTS"
- **Technical:** "FLOTADORES" -> "BUOYANCY MODULES", "LASTRE" -> "COATING", "TENSIONADOR" -> "TENSIONER"
- **Units/Dimensions:** "Espesor" -> "Thickness", "Diametro" -> "Diameter"

### 4. Execution
- Run script to generate translated copies.
- Verify file creation.

### 5. Verification
- Inspect generated files using `pandas`.
- Check for "CALCULATION" vs "CALCUTHETION" errors (fixed by regex boundary checks).
- Confirm sheet names are translated and valid.

## Deliverables
1. **Script:** `scripts/python/translate_excel.py`
2. **Skill Documentation:** `.claude/skills/data-engineering/excel-translation/SKILL.md`
3. **Translated Files:**
    - `GSM-AO-M-MCA-10020-0000-A_en.xlsx`
    - `GSM-AO-T-MCA-10001-0000-A_en.xlsx`

## Future Improvements
- Externalize dictionary to a JSON/YAML file.
- Add CLI arguments for input/output directories.
- Add fuzzy matching for near-miss typos in source files.
