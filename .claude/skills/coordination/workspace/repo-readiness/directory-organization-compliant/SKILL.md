---
name: repo-readiness-directory-organization-compliant
description: "Sub-skill of repo-readiness: Directory Organization: \u2705 Compliant\
  \ (+4)."
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Directory Organization: ✅ Compliant (+4)

## Directory Organization: ✅ Compliant


```
repo/
├── src/              ✅ Present
│   └── modules/      ✅ Modular structure
├── tests/            ✅ Present
│   ├── unit/         ✅ Organized
│   └── integration/  ✅ Organized
├── docs/             ✅ Present
├── config/           ✅ Present
├── scripts/          ✅ Present
├── data/             ✅ Present
└── reports/          ✅ Present
```

## Module Architecture: ✅ Well-Organized


- **Modules Found**: 5
  - data_processor/
  - visualization/
  - analysis/
  - reporting/
  - utilities/

## Naming Conventions: ⚠️ Minor Issues


- ✅ Python files use snake_case
- ✅ Modules use lowercase
- ⚠️ 2 files need organization (see details)

## Test Coverage: ✅ Good


- Unit tests: 45 files
- Integration tests: 12 files
- Test coverage: 85% (target: 80%)
```

## 3. Mission & Objectives Extraction


**Sources:**
```
✓ .agent-os/product/mission.md
✓ .agent-os/product/tech-stack.md
✓ .agent-os/product/roadmap.md
✓ .agent-os/product/decisions.md
✓ README.md
✓ docs/OVERVIEW.md
```


*See sub-skills for full details.*
