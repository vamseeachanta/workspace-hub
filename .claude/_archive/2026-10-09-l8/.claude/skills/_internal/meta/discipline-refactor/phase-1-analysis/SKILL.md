---
name: discipline-refactor-phase-1-analysis
description: 'Sub-skill of discipline-refactor: Phase 1: Analysis.'
version: 2.0.0
category: _internal
type: reference
scripts_exempt: true
---

# Phase 1: Analysis

## Phase 1: Analysis


**Spawn**: `Task` with `subagent_type=Explore`

**Prompt**:
```
Analyze the repository for discipline-based, module-based refactoring:

1. Identify package name:
   - Check pyproject.toml [project.name] or [tool.poetry.name]
   - Check package.json name
   - Check existing src/<name>/ structure
   - Derive from repo name if not found

2. Scan ALL top-level directories:
   - src/ - code structure
   - tests/ - test organization
   - docs/ - documentation structure
   - specs/ - specifications
   - data/ - data files
   - logs/ - log files
   - .claude/skills/ - skill organization

3. Identify disciplines from existing code:
   - What domain modules exist?
   - What functional areas are present?
   - Map existing directories to discipline names

4. Check for existing modules/ patterns:
   - Already have src/<pkg>/modules/?
   - Already have tests/modules/?
   - What's the current organization level?

5. Output discipline mapping:
   - Suggested disciplines (use consistent names)
   - Current path → new module path for each folder
   - Package name to use

Report in structured format for Phase 2.
```

---
