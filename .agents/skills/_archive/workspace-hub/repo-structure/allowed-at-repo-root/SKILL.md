---
name: repo-structure-allowed-at-repo-root
description: 'Sub-skill of repo-structure: Allowed at Repo Root (+2).'
version: 1.4.0
category: workspace
type: reference
scripts_exempt: true
---

# Allowed at Repo Root (+2)

## Allowed at Repo Root


```
src/             tests/           docs/            config/
scripts/         data/            specs/           reports/
pyproject.toml   pytest.ini       README.md        CHANGELOG.md
CLAUDE.md        AGENTS.md        Makefile         LICENSE
.gitignore       .claude/         .codex/          .gemini/
.github/         .pre-commit-config.yaml
```


## NOT Allowed at Repo Root


| Item | Correct Location |
|------|-----------------|
| Loose `.py` scripts | `scripts/` or `src/<pkg>/tools/` |
| `agents/` directory | `.claude/agents/` only |
| `.agent-os/` | DELETE — superseded by `.claude/skills/` |
| `.hive-mind/`, `.swarm/` | DELETE — gitignored |
| `business/` docs | `docs/business/` |
| `modules/` | Move into `src/<package>/modules/` |
| `bin/` (empty) | DELETE |
| `_coding_agents/` | DELETE |
| `examples/` | `docs/examples/` or leave at root only if README documents it |
| `setup.py` (when pyproject.toml exists) | DELETE — pyproject.toml supersedes it |
| `archive/`, `backups/` | `_archive/` (single, underscore-prefixed) |
| `*.xlsx`, `*.csv` output files | `results/<domain>/` and gitignored |
| `test_export*.json` | `tests/<domain>/fixtures/` or gitignored |
| `COVERAGE_ANALYSIS.txt` | gitignored (session artifact) |
| `verdict.txt`, `test_output_ss` | gitignored (session artifacts) |
| `coverage.wrk*.xml` | gitignored (session artifacts) |
| Windows path dirs (`D:\...`) | DELETE — filesystem artifact, never track |


## Root-Level `src/` Must Contain Only the Package


```
src/              ← OK
  package_name/   ← OK (the installed package)
  modules/        ← WRONG — orphaned, not installed
  validators/     ← WRONG — orphaned, not installed
  other_stuff/    ← WRONG
```

---
