---
name: repo-structure-gitignore-enforcement-root-level-output-artifacts
description: 'Sub-skill of repo-structure: Gitignore Enforcement: Root-Level Output
  Artifacts.'
version: 1.4.0
category: workspace
type: reference
scripts_exempt: true
---

# Gitignore Enforcement: Root-Level Output Artifacts

## Gitignore Enforcement: Root-Level Output Artifacts


**NEVER commit output files to repo root.** These patterns must be gitignored, not tracked:

| Pattern | Wrong location | Correct location |
|---------|---------------|-----------------|
| `report_*.xlsx` | repo root | `results/<domain>/` (and gitignored) |
| `test_export*.json` | repo root | `tests/<domain>/fixtures/` or gitignored |
| `COVERAGE_ANALYSIS.txt` | repo root | `reports/coverage/` (gitignored) |
| `analyze_coverage.py` | repo root | `scripts/analysis/analyze_coverage.py` |
| `*.wrk*.xml` | repo root | gitignored (session artifacts) |
| `verdict.txt` | repo root | gitignored (session artifact) |

If a file of this type is already committed: `git rm --cached <file>` then add to `.gitignore`.

---
