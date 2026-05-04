---
name: clean-code-file-size-decision-tree
description: 'Sub-skill of clean-code: File Size Decision Tree.'
version: 2.1.0
category: workspace
type: reference
scripts_exempt: true
---

# File Size Decision Tree

## File Size Decision Tree


When a file exceeds 400 lines:

```
Is it a God Object (does many unrelated things)?
  YES → Split by responsibility (see Decomposition Patterns below)
  NO  → Is it a report generator / long output formatter?
         YES → Extract: data-gathering logic → separate module
                        formatting/rendering → reporter.py / formatter.py
         NO  → Is it a data model / schema file?
                YES → Acceptable if types are coherent; add __all__
                NO  → Is it a legacy solver (low churn, full tests)?
                       YES → Add # noqa: clean-code; open WRK for future split
                       NO  → Split now
```

---
