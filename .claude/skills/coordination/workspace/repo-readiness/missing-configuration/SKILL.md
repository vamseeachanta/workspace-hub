---
name: repo-readiness-missing-configuration
description: 'Sub-skill of repo-readiness: Missing Configuration (+4).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Missing Configuration (+4)

## Missing Configuration


**Error:** CLAUDE.md not found
```
❌ Critical: No CLAUDE.md found in repository root

Action Required:
1. Create CLAUDE.md with repository configuration
2. Use template from workspace-hub/templates/CLAUDE.md
3. Re-run readiness check

Quick Fix:
cp ~/workspace-hub/templates/CLAUDE.md ./CLAUDE.md
```

## Incomplete Structure


**Error:** Required directories missing
```
⚠️ Warning: Required directories missing
   Missing: tests/, docs/

Action Required:
1. Create missing directories
2. Follow FILE_ORGANIZATION_STANDARDS.md
3. Re-run readiness check

Quick Fix:
mkdir -p tests/{unit,integration} docs config scripts
```

## Unclear Mission


**Error:** No mission.md found
```
⚠️ Warning: Project mission not defined
   Missing: .agent-os/product/mission.md

Action Required:
1. Create .agent-os/product/mission.md
2. Define project purpose and objectives
3. Document technical decisions

Quick Fix:
mkdir -p .agent-os/product
cp ~/workspace-hub/templates/mission.md .agent-os/product/
```

## Dirty Git State


**Error:** Uncommitted changes present
```
⚠️ Warning: Repository has uncommitted changes
   Files modified: 5

Action Required:
1. Review uncommitted changes: git status
2. Commit changes: git add . && git commit -m "message"
3. Or stash: git stash
4. Re-run readiness check
```

## Environment Issues


**Error:** Virtual environment not found
```
⚠️ Warning: No virtual environment detected

Action Required:
1. Create UV environment: uv venv
2. Install dependencies: uv pip install -r requirements.txt
3. Activate environment: source .venv/bin/activate
4. Re-run readiness check
```
