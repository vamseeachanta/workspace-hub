---
name: discipline-refactor-phase-4-validation
description: 'Sub-skill of discipline-refactor: Phase 4: Validation.'
version: 2.0.0
category: _internal
type: reference
scripts_exempt: true
---

# Phase 4: Validation

## Phase 4: Validation


**Spawn**: `Task` with `subagent_type=Bash`

**Prompt**:
```
Validate module-based refactoring:

1. Structure validation:
   - [ ] src/<package>/modules/ exists with disciplines
   - [ ] tests/modules/ mirrors src structure
   - [ ] docs/modules/ exists
   - [ ] specs/modules/ exists
   - [ ] Each module has __init__.py (Python) or index (JS)
   - [ ] Each module has README.md

2. Import validation:
   - [ ] No old import paths remain
   - [ ] All imports resolve
   - [ ] Circular imports checked

3. Test validation:
   - [ ] pytest / npm test passes
   - [ ] Coverage maintained

4. Documentation validation:
   - [ ] Internal links work
   - [ ] Module READMEs complete

Generate report. On failure, suggest:
git checkout pre-module-refactor-{date}
```

---
