---
id: GOT-004
type: gotcha
title: "Legacy OrcFxAPI script count inflated by .venv"
category: orcaflex
tags: [orcaflex, inventory, scan, venv, legacy]
repos: [digitalmodel]
confidence: 0.9
created: "2026-02-24"
last_validated: "2026-02-24"
source_type: session
related: []
status: active
access_count: 0
---

# Legacy Script Count Inflated by .venv

## Problem

A `grep -r "import OrcFxAPI" --include="*.py"` scan of `digitalmodel/` returned
194 hits, which became the basis for WRK-316. The actual count of hand-written
domain scripts is far lower.

## Root Cause

The scan included `.venv/` — virtualenv copies of OrcFxAPI stubs/wrappers — which
inflated the count by ~160 files.

## Solution

Always exclude `.venv` and `__pycache__` from inventory scans:

```bash
grep -r "import OrcFxAPI" --include="*.py" --exclude-dir=.venv docs/
```

Or in Python:

```python
py_files = [
    f for f in SCAN_ROOT.rglob("*.py")
    if ".venv" not in f.parts and "__pycache__" not in f.parts
]
```

## Actual Counts (WRK-316, 2026-02-24)

- `docs/domains/orcaflex/`: **42** Python files total, **32** importing OrcFxAPI
- The 194 count was workspace-wide including `.venv`
