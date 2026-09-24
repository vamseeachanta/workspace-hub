---
name: discipline-refactor-phase-3-execution
description: 'Sub-skill of discipline-refactor: Phase 3: Execution.'
version: 2.0.0
category: _internal
type: reference
scripts_exempt: true
---

# Phase 3: Execution

## Phase 3: Execution


**Spawn**: `Task` with `subagent_type=general-purpose`

**Call**: `@git-sync-manager`, `@parallel-batch-executor`

**Prompt**:
```
Execute module-based refactoring:

Migration Plan: {migration_plan}
Package Name: {package_name}
Disciplines: {disciplines}

Execute in order:

1. BACKUP:
   git tag pre-module-refactor-$(date +%Y%m%d)

2. CREATE MODULE STRUCTURE:
   # For each discipline in [_core, discipline-1, ...]:
   mkdir -p src/<package>/modules/<discipline>
   mkdir -p tests/modules/<discipline>
   mkdir -p docs/modules/<discipline>
   mkdir -p specs/modules/<discipline>
   mkdir -p data/modules/<discipline>  # if data/ exists
   mkdir -p .claude/skills/<discipline>

3. MOVE CODE:
   # Move source files to appropriate modules
   # Update __init__.py in each module
   # Preserve git history with git mv

4. MOVE TESTS:
   # Move test files to mirror source structure
   # Update test imports

5. MOVE DOCS:
   # Move documentation to module folders
   # Update internal links

6. MOVE SPECS:
   # Move specifications to module folders
   # Keep templates/ at top level

7. UPDATE IMPORTS:
   # Search and replace import paths
   # from <pkg>.old_path → from <pkg>.modules.<discipline>
   # Update conftest.py
   # Update pyproject.toml entry points

8. UPDATE CONFIGS:
   # pyproject.toml: packages, entry points
   # Update CI/CD paths
   # Update Makefile/scripts

9. CREATE MODULE README:
   # Add README.md to each module explaining purpose

Report progress. Stop on failure.
```

---
