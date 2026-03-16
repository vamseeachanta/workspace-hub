---
name: dark-intelligence-workflow
description: 'Extract calculation methodology from legacy Excel/files into clean,
  client-free dark intelligence archive — the canonical path for porting legacy calculations
  to public repos while avoiding legal/IP issues.

  '
version: 1.0.0
category: data
related_skills:
- research-literature
- calculation-report
- legal-sanity-scan
triggers:
- dark intelligence
- extract from excel
- port legacy calculation
- archive calculation
- extract methodology
---

# Dark Intelligence Workflow Skill

## Overview

Use this skill when porting engineering calculations from legacy Excel spreadsheets
(or other legacy formats) into clean, client-free implementations in the 4 public
repos. The workflow extracts only generic methodology — equations, input/output
schemas, worked examples — and strips all client/project identifiers before archival.

## Inputs

- **source_file**: path to the Excel/legacy file containing calculations
- **category**: engineering discipline (e.g. `structural`, `geotechnical`, `subsea`)
- **subcategory**: specific topic (e.g. `fatigue`, `pile_capacity`, `wall_thickness`)
- **target_repo**: destination repo (`digitalmodel`, `assetutilities`, `worldenergydata`, `assethold`)

## 7-Step Workflow

### Step 1 — Identify

Locate the Excel/file containing engineering calculations.

**What to look for:**
- Formulas (cell formulas, array formulas)
- Named ranges (often contain key parameters)
- VBA macros (may contain iterative solvers or logic)
- Validation/check sheets (comparison against known answers)
- Input sheets with units and descriptions
- README or documentation tabs

**Check doc index for the file:**

```bash
uv run --no-project python -c "
import json
matches = []
with open('data/document-index/index.jsonl') as f:
    for line in f:
        rec = json.loads(line)
        path_lower = rec.get('path', '').lower()
        if '<filename>' in path_lower or '<category>' in path_lower:
            matches.append(rec)
print(f'Found {len(matches)} matching documents')
for m in matches[:20]:
    print(f\"  {m.get('source', '?'):15s} {m.get('path', '')[:80]}\")
"
```

**Output:** file path, description of what the spreadsheet calculates, list of tabs/sheets.

### Step 2 — Extract

Pull out generic methodology from the file. Extract each of these:

| Item | What to capture |
|------|----------------|
| **Equations** | Convert Excel formulas to LaTeX notation |
| **Input ranges** | Parameter names, symbols, units, typical value ranges |
| **Output ranges** | Result names, symbols, units, expected values for test cases |
| **Standard references** | Any codes/standards cited (API, DNV, ISO, ASME, etc.) |
| **Methodology notes** | Documentation within the file, assumptions, limitations |
| **Unit systems** | SI, Imperial, or mixed — note conversions used |
| **Worked examples** | Complete input-output pairs with known-correct answers |

**Tips for Excel formula extraction:**
- `=` formulas: translate operators directly to math notation
- Named ranges: map to variable names in the archive
- `IF/AND/OR`: translate to conditional logic descriptions
- `VLOOKUP/INDEX/MATCH`: identify the lookup table data
- Array formulas (`Ctrl+Shift+Enter`): note array dimensions
- VBA `Function`: extract algorithm as pseudocode

### Step 3 — Sanitize (HARD GATE)

**This step is non-negotiable. Extraction cannot proceed without passing.**

Run the legal sanity scan on all extracted content:

```bash
bash scripts/legal/legal-sanity-scan.sh
```

**Check for and remove:**
- Client names, project names, project numbers
- Proprietary labels and internal codenames
- Client infrastructure identifiers (field names, platform names)
- Client-specific file paths or network locations
- Employee names (other than yourself for academic work)

**If ANY block-severity violations are found: STOP.**
Remediate all violations before proceeding to Step 4.

Replace all client-specific references with generic equivalents:
- Project names -> generic descriptive names (e.g. "example_platform")
- Field names -> "field_A", "field_B" or generic descriptions
- Client tool names -> generic equivalents

### Step 4 — Archive

Save extracted methodology as structured YAML.

**Location:** `knowledge/dark-intelligence/<category>/<subcategory>/`

**Filename:** `dark-intelligence-<descriptive-name>.yaml`

**Schema:**

```yaml
# dark-intelligence-<name>.yaml
source_type: "excel|python|matlab|fortran"
source_description: "Generic description of what this calculates (no client refs)"
extracted_date: "YYYY-MM-DD"
legal_scan_passed: true
category: "<engineering category>"
subcategory: "<specific topic>"

equations:
  - name: "<equation name>"
    latex: "<LaTeX formula>"
    excel_formula: "<original Excel formula, sanitized>"
    standard: "<standard reference if any>"
    description: "<what it computes>"

inputs:
  - name: "<input name>"
    symbol: "<LaTeX symbol>"
    unit: "<unit>"
    typical_range: [min, max]
    test_value: <value for TDD>

outputs:
  - name: "<output name>"
    symbol: "<LaTeX symbol>"
    unit: "<unit>"
    test_expected: <expected value for TDD>
    tolerance: <acceptable error>

worked_examples:
  - description: "<example problem statement>"
    inputs: {key: value}
    outputs: {key: value}
    use_as_test: true

assumptions:
  - "<assumption 1>"
  - "<assumption 2>"

references:
  - "<standard or textbook reference>"

notes: "<any methodology notes, limitations, applicability>"
```

**Validation:** ensure `legal_scan_passed: true` is present and all fields
use generic descriptions free of client identifiers.

### Step 5 — Generate TDD Test Data

Convert each worked example from the archive into a pytest test function.

**Template:**

```python
def test_<calc_name>_from_dark_intelligence():
    """Extracted from legacy calculation — verified against original output."""
    # Arrange — inputs from archive
    <input_name> = <test_value>

    # Act — call the implementation
    result = <function>(<inputs>)

    # Assert — expected output from archive
    assert abs(result - <expected>) < <tolerance>, (
        f"Expected {<expected>}, got {result}"
    )
```

**Rules:**
- One test per worked example where `use_as_test: true`
- Use `tolerance` from the archive for floating-point comparisons
- Include the source description in the docstring
- Tests MUST fail initially (Red phase of TDD)

### Step 6 — Implement

Build the clean implementation using extracted methodology and test data.

**Process:**
1. Choose target repo based on category (see repo-map.yaml)
2. Write failing tests first (from Step 5 output)
3. Implement equations from the archive YAML
4. Run tests until green
5. Refactor while keeping tests green

**Target repo selection:**

| Category | Primary repo |
|----------|-------------|
| Structural, geotechnical, subsea, pipeline | digitalmodel |
| Shared utilities, unit conversion, common calcs | assetutilities |
| Energy market, drilling, production data | worldenergydata |
| Financial analysis, portfolio | assethold |

### Step 7 — Produce Calc Report

Generate a calculation-report YAML from the extracted data.

1. Use the `data/calculation-report` skill for the report template
2. Populate with equations, inputs, outputs from the archive YAML
3. Include worked examples as verification cases
4. Validate the YAML against the calc-report schema
5. Generate HTML report for review

## Integration Points

| Skill | Relationship |
|-------|-------------|
| `data/research-literature` | Step 5 of research-literature (university resources) feeds into this workflow |
| `data/calculation-report` | Step 7 output follows the calc-report schema |
| `coordination/workspace/legal-sanity-scan` | Step 3 hard gate uses the legal scan |

## AC Checklist

- [ ] Source file identified and documented (Step 1)
- [ ] All equations, inputs, outputs extracted (Step 2)
- [ ] Legal sanity scan passed with zero block violations (Step 3)
- [ ] Archive YAML saved to `knowledge/dark-intelligence/` (Step 4)
- [ ] TDD test functions generated from worked examples (Step 5)
- [ ] Clean implementation passes all tests (Step 6)
- [ ] Calculation report YAML generated and validated (Step 7)
