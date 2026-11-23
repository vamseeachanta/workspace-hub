---
name: discipline-refactor-standard-folders-module-structure
description: "Sub-skill of discipline-refactor: Standard Folders \u2192 Module Structure\
  \ (+1)."
version: 2.0.0
category: _internal
type: reference
scripts_exempt: true
---

# Standard Folders → Module Structure (+1)

## Standard Folders → Module Structure


| Folder | Module Pattern | Example |
|--------|----------------|---------|
| `src/<pkg>/` | `src/<pkg>/modules/<discipline>/` | `src/myapp/modules/data/` |
| `tests/` | `tests/modules/<discipline>/` | `tests/modules/data/` |
| `docs/` | `docs/modules/<discipline>/` | `docs/modules/data/` |
| `specs/` | `specs/modules/<discipline>/` | `specs/modules/data/` |
| `data/` | `data/modules/<discipline>/` | `data/modules/ingestion/` |
| `logs/` | `logs/modules/<discipline>/` | `logs/modules/api/` |
| `.claude/skills/` | `.claude/skills/<discipline>/` | `.claude/skills/data/` |


## Exceptions (Keep Flat)


| Folder | Reason |
|--------|--------|
| `specs/templates/` | Shared templates |
| `docs/assets/` | Shared images/files |
| `.claude/state/` | Runtime state |
| `scripts/` | Build/deploy scripts |
| `config/` | Configuration files |

---
