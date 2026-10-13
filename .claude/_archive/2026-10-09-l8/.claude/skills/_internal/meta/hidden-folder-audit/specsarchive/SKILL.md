---
name: hidden-folder-audit-specsarchive
description: 'Sub-skill of hidden-folder-audit: specs/archive/ (+1).'
version: 1.2.0
category: _internal
type: reference
scripts_exempt: true
---

# specs/archive/ (+1)

## specs/archive/


Standard location for completed specification plans.

```bash
# Archive completed plans (check YAML frontmatter for status: completed)
mkdir -p specs/archive
git mv specs/modules/<completed-plan>.md specs/archive/
```

## benchmarks/


Benchmark directories typically contain mixed content requiring separation.

| Subdirectory | Content | Action |
|--------------|---------|--------|
| `legacy_projects/` | Reference test data (*.dat, *.csv) | Move to `tests/fixtures/` |
| `reports/` | Timestamped HTML reports | Add to .gitignore |
| `results/` | Timestamped CSV/JSON | Add to .gitignore |
| Root `*.py` files | Benchmark scripts | Keep tracked |

```bash

*See sub-skills for full details.*
