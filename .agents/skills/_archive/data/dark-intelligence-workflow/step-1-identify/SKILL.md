---
name: dark-intelligence-workflow-step-1-identify
description: "Sub-skill of dark-intelligence-workflow: Step 1 \u2014 Identify (+4)."
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Step 1 — Identify (+4)

## Step 1 — Identify


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


## Step 2 — Extract


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


## Step 3 — Sanitize (HARD GATE)


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


## Step 4 — Archive


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


## Step 5 — Generate TDD Test Data


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
