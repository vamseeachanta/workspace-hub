---
name: xlsx-to-python-step-6-calculation-block-detection
description: "Sub-skill of xlsx-to-python: Step 6 \u2014 Calculation Block Detection."
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Step 6 — Calculation Block Detection

## Step 6 — Calculation Block Detection


Heuristic to separate calculation regions from data/lookup tables:

```python
def detect_calculation_blocks(ws_formulas, min_formula_ratio=0.3):
    """Identify contiguous regions dominated by formulas."""
    blocks = []
    current_block = []
    for row in ws_formulas.iter_rows():
        formula_count = sum(
            1 for c in row
            if isinstance(c.value, str) and c.value.startswith("=")
        )
        total = sum(1 for c in row if c.value is not None)
        if total > 0 and formula_count / total >= min_formula_ratio:
            current_block.append(row[0].row)
        else:
            if len(current_block) >= 2:
                blocks.append((current_block[0], current_block[-1]))
            current_block = []
    if len(current_block) >= 2:
        blocks.append((current_block[0], current_block[-1]))
    return blocks
```
