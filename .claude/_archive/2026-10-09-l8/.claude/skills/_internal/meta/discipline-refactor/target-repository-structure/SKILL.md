---
name: discipline-refactor-target-repository-structure
description: 'Sub-skill of discipline-refactor: Target Repository Structure.'
version: 2.0.0
category: _internal
type: reference
scripts_exempt: true
---

# Target Repository Structure

## Target Repository Structure


```
<repo>/
├── src/<package_name>/
│   └── modules/
│       ├── _core/              # Shared utilities
│       ├── <discipline-1>/     # Domain module
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── services.py
│       │   └── utils.py
│       └── <discipline-2>/
│
├── tests/
│   └── modules/
│       ├── _core/
│       ├── <discipline-1>/
│       └── <discipline-2>/
│
├── docs/
│   └── modules/
│       ├── _core/
│       ├── <discipline-1>/
│       └── <discipline-2>/
│
├── specs/
│   └── modules/
│       ├── _core/
│       ├── <discipline-1>/
│       └── <discipline-2>/
│
├── data/
│   └── modules/
│       ├── <discipline-1>/
│       └── <discipline-2>/
│
├── logs/
│   └── modules/
│       ├── <discipline-1>/
│       └── <discipline-2>/
│
├── .claude/
│   ├── skills/
│   │   ├── _core/
│   │   ├── <discipline-1>/
│   │   └── <discipline-2>/
│   └── CLAUDE.md
│
└── pyproject.toml / package.json
```

---
