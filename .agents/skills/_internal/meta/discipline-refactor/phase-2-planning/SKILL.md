---
name: discipline-refactor-phase-2-planning
description: 'Sub-skill of discipline-refactor: Phase 2: Planning.'
version: 2.0.0
category: _internal
type: reference
scripts_exempt: true
---

# Phase 2: Planning

## Phase 2: Planning


**Spawn**: `Task` with `subagent_type=Plan`

**Call**: `@skill-creator` for new discipline skills

**Prompt**:
```
Create module-based migration plan based on Phase 1 analysis.

Context: {analysis_results}

Create plan for ALL directories:

1. Package identification:
   - Confirm package name: <package_name>
   - Confirm disciplines: [_core, discipline-1, discipline-2, ...]

2. Code structure (src/):
   BEFORE: src/<package>/feature1/, src/<package>/feature2/
   AFTER:  src/<package>/modules/_core/, src/<package>/modules/<discipline>/

3. Test structure:
   BEFORE: tests/test_feature1.py, tests/integration/
   AFTER:  tests/modules/_core/, tests/modules/<discipline>/

4. Documentation structure:
   BEFORE: docs/api/, docs/guides/
   AFTER:  docs/modules/_core/, docs/modules/<discipline>/

5. Specs structure:
   BEFORE: specs/feature-spec.md, specs/plan.md
   AFTER:  specs/modules/<discipline>/, specs/templates/

6. Data structure (if exists):
   BEFORE: data/raw/, data/processed/
   AFTER:  data/modules/<discipline>/

7. Skills structure:
   BEFORE: .claude/skills/category/
   AFTER:  .claude/skills/<discipline>/

8. Import updates:
   - from <package>.feature → from <package>.modules.<discipline>
   - Update __init__.py files
   - Update relative imports

9. Create README.md for each module with:
   - Module purpose
   - Key files
   - Dependencies on other modules

Output executable task list for Phase 3.
```

---
