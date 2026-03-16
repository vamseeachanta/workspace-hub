---
name: clean-code-dead-code-identification-and-removal
description: 'Sub-skill of clean-code: Dead Code Identification and Removal.'
version: 2.1.0
category: workspace
type: reference
scripts_exempt: true
---

# Dead Code Identification and Removal

## Dead Code Identification and Removal


Dead code is any code that is never called, imported, or referenced.

```bash
# Find files that nothing imports (potential dead modules)
# Run from repo root:
python3 -c "
import ast, os, sys
from pathlib import Path

src = Path('src')
all_files = list(src.rglob('*.py'))
imported = set()

for f in all_files:
    try:
        tree = ast.parse(f.read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if hasattr(node, 'module') and node.module:
                    imported.add(node.module.split('.')[-1])
    except:
        pass

for f in all_files:
    stem = f.stem
    if stem not in imported and stem != '__init__':
        print(f)
"
```

Common dead code patterns to delete:
- `*_unused.py` — explicitly named dead code
- `*_old.py`, `*_bak.py`, `*.py.bak` — backup files (use git, not backup files)
- Files with only `pass` in every function
- Commented-out code blocks >5 lines (use git history instead)
- `__all__ = []` with no exports (likely orphaned)

---
