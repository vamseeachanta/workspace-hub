---
name: clean-code-hard-limits-zero-tolerance
description: 'Sub-skill of clean-code: Hard Limits (Zero-Tolerance).'
version: 2.1.0
category: workspace
type: reference
scripts_exempt: true
---

# Hard Limits (Zero-Tolerance)

## Hard Limits (Zero-Tolerance)


| Metric | Hard Limit | Target | Action When Exceeded |
|--------|-----------|--------|----------------------|
| File length | **400 lines** | 200 lines | Split by responsibility |
| Function length | **50 lines** | 20–30 lines | Extract helpers |
| Class public methods | **10 methods** | 5–7 methods | Extract sub-classes or use composition |
| Nesting depth | **4 levels** | 2 levels | Extract guard clauses or sub-functions |
| Import count per file | **20 imports** | 10–12 imports | Sign of a God Object — split the file |

**Exception 1 — Legacy solver**: Low-churn files with full test coverage may remain until a
dedicated refactor WRK is approved. Document with `# noqa: clean-code` at the top of the file.

**Exception 2 — Pure declarative data**: Files whose content is ≥95% frozen dataclass/dict
literals with zero logic (no conditionals, no I/O, no imports from sibling modules) are exempt
from the 400L limit. The logic module that consumes them must still be ≤400L.
Example: `activity_definitions.py` (1,419L) — 14 `return Activity(...)` builder functions.
Test: if every function body is a single `return SomeDataclass(...)`, it is a data file, not a
God Object.

---
