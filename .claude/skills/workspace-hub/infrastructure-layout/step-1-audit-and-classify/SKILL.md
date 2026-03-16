---
name: infrastructure-layout-step-1-audit-and-classify
description: "Sub-skill of infrastructure-layout: Step 1 \u2014 Audit and classify\
  \ (+3)."
version: 1.0.0
category: workspace
type: reference
scripts_exempt: true
---

# Step 1 — Audit and classify (+3)

## Step 1 — Audit and classify


```bash
# Count files per subdir
find src/<pkg>/infrastructure -maxdepth 2 -name "*.py" | \
  awk -F/ '{print $(NF-1)}' | sort | uniq -c | sort -rn

# Find external callers per module
grep -r "infrastructure\." src/ tests/ --include="*.py" | \
  grep -v "infrastructure/infrastructure" | \
  awk -F: '{print $1}' | sort | uniq
```

Classify every subdir into one of: `config | persistence | validation | utils | solvers | DOMAIN (move out)`


## Step 2 — Execute in safe phases (zero-risk first)


| Phase | Action | Risk |
|-------|--------|------|
| 2A | Merge config dirs; rename persistence; move template validator | Zero — add shims |
| 2B | Remove deprecated shim dirs with 0 callers | Zero |
| 2C | Extract web layer → `src/<pkg>/web/` | Low — no Python callers |
| 2D | Move engineering solvers from common/ → solvers/ | Medium — update callers |
| 2E | Move misplaced domain logic out of infrastructure/ | Low if 0 callers |
| 2F | Move residual utils/IO files → utils/; shim common/ | Medium — update callers |


## Step 3 — Backward-compat shim pattern


For every file moved, leave a shim at the old path:

```python
# infrastructure/common/data.py  ← shim after moving to utils/
"""Backward-compat shim. Use infrastructure.utils.data instead."""
import warnings
warnings.warn(
    "infrastructure.common.data is deprecated. "
    "Use infrastructure.utils.data instead.",
    DeprecationWarning,
    stacklevel=2,
)
from infrastructure.utils.data import *  # noqa: F401,F403
```

Keep shims until all callers are updated. Then delete shim dirs in a separate cleanup PR.


## Step 4 — Update callers


```bash
# Find all callers of a moved module
grep -r "from.*infrastructure\.common\." src/ tests/ --include="*.py"
grep -r "infrastructure\.common\." src/ tests/ --include="*.py"

# After updating callers, verify zero remaining old-path imports
grep -r "infrastructure\.common\b" src/ --include="*.py" | \
  grep -v "__init__.py\|DeprecationWarning"
```

---
