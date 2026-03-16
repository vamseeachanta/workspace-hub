---
name: infrastructure-layout-acceptance-criteria-post-migration-gate
description: 'Sub-skill of infrastructure-layout: Acceptance Criteria (Post-Migration
  Gate).'
version: 1.0.0
category: workspace
type: reference
scripts_exempt: true
---

# Acceptance Criteria (Post-Migration Gate)

## Acceptance Criteria (Post-Migration Gate)


A fully compliant `infrastructure/` meets ALL of the following:

- [ ] Contains exactly `config/`, `persistence/`, `validation/`, `utils/`, `solvers/` (or `base_solvers/`) as canonical dirs
- [ ] `grep -r "infrastructure\.common\b" src/` returns zero non-shim results
- [ ] `grep -r "infrastructure\.core\b" src/` returns zero non-shim results
- [ ] `grep -r "infrastructure\.validators\b" src/` returns zero non-shim results
- [ ] No Flask/web app code inside `infrastructure/`
- [ ] No domain-specific solvers or data loaders inside `infrastructure/`
- [ ] All 5 canonical packages importable: `python3 -c "import pkg.infrastructure.<domain>"`
- [ ] All existing tests pass with no new failures

---
