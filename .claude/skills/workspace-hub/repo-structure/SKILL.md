---
name: repo-structure
version: "1.1.0"
category: workspace
description: "Canonical source layout, test mirroring, root cleanliness, and gitignore rules for all workspace-hub tier-1 repos. Consult before creating directories or files in any submodule."
invocation: /repo-structure
applies-to: [claude, codex, gemini]
capabilities: []
requires: []
see_also: [file-taxonomy]
---

# Repo Structure — Canonical Source Layout

Consult before creating any directory or moving source files. For output file placement
(reports, results, data) see `/file-taxonomy`.

## Tier Classification (Determines Which Rules Apply)

| Tier | Repos | Rules |
|------|-------|-------|
| **Python package** | assetutilities, digitalmodel, worldenergydata, assethold, pdf-large-reader | Full src/ layout — ALL rules below apply |
| **Admin/tooling** | aceengineer-admin, aceengineer-website, pyproject-starter | src/ layout applies to Python; website = content/ not src/ |
| **Client/portfolio** | frontierdeepwater, doris, saipem, acma-projects | EXEMPT — follow client conventions; indexing not API surface |

Client/portfolio repos must NOT be refactored to the Python layout. Do not open WRK items
for structural changes in those repos.

---

## Source Layout (Python Package Repos)

### Canonical Structure

```
repo/
  src/
    <package_name>/        ← installed package root (snake_case)
      __init__.py          ← required at every level
      common/              ← cross-cutting utilities
      modules/             ← domain feature modules
        <domain>/
          __init__.py
          core.py          ← main logic
          utils.py         ← helpers
      cli/                 ← command-line entrypoints (if any)
  tests/
    <domain>/              ← mirrors src/<package>/<domain>/
      unit/
      integration/
      fixtures/
  docs/
  config/
  scripts/
  data/
  reports/                 ← gitignored (generated)
  pyproject.toml           ← required at repo root
  pytest.ini               ← required; must include pythonpath = src
```

### Rules

1. **One package per `src/`** — `src/` contains exactly `src/<package_name>/`. No other
   Python packages at `src/other_package/` level.
2. **`__init__.py` required** at every directory that is a Python package.
3. **`pythonpath = src`** in `pytest.ini` — never rely on PYTHONPATH env variable for CI.
4. **Tests mirror src** — `tests/<domain>/` maps to `src/<package>/<domain>/`.
   Do NOT use `tests/modules/<domain>/` wrapper — the `modules/` level is redundant.
5. **No loose scripts at root** — ad-hoc `.py` files at repo root belong in `scripts/`
   or `src/<package>/cli/` or `src/<package>/tools/`.

---

## Root Directory Rules

### Allowed at Repo Root

```
src/             tests/           docs/            config/
scripts/         data/            specs/           reports/
pyproject.toml   pytest.ini       README.md        CHANGELOG.md
CLAUDE.md        AGENTS.md        Makefile         LICENSE
.gitignore       .claude/         .codex/          .gemini/
.github/         .pre-commit-config.yaml
```

### NOT Allowed at Repo Root

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

### Root-Level `src/` Must Contain Only the Package

```
src/              ← OK
  package_name/   ← OK (the installed package)
  modules/        ← WRONG — orphaned, not installed
  validators/     ← WRONG — orphaned, not installed
  other_stuff/    ← WRONG
```

---

## Gitignore Compliance

These must be in `.gitignore` for every Python package repo:

```
# Build artifacts — NEVER commit
dist/
build/
*.egg-info/
__pycache__/
*.pyc

# Virtual environments
.venv/
venv/

# Coverage artifacts
htmlcov/
.coverage
coverage.json
coverage.xml
.coverage_report.json

# Runtime artifacts
logs/
cache/
results/
reports/

# Legacy framework dirs (delete if present, gitignore as safety net)
.agent-os/
.hive-mind/
.swarm/
.claude-flow/
```

---

## Agent Infrastructure Rules

Only ONE location for agent configuration per repo:

```
.claude/
  agents/       ← agent YAML definitions
  commands/     ← slash commands
  skills/       ← repo-local skills (if any)
  hooks/
  docs/
  settings.json
```

**Never create** `agents/` at repo root. **Never create** `.agent-os/`. These are
superseded patterns.

---

## Compliance Quick-Check

Run against any repo before and after structural changes:

```bash
# 1. No orphaned dirs at src/ root (non-package dirs)
ls src/ | grep -v "^$(basename $(pwd | sed 's/-/_/g'))$"

# 2. Every package dir has __init__.py
find src/ -type d | while read d; do
  [ -f "$d/__init__.py" ] || echo "MISSING __init__.py: $d"
done

# 3. No loose .py at repo root
ls *.py 2>/dev/null && echo "WARNING: loose .py files at root"

# 4. pytest.ini has pythonpath
grep -q "pythonpath" pytest.ini && echo "OK" || echo "MISSING pythonpath in pytest.ini"

# 5. Windows path artifacts (backslash dirs)
ls | grep '\\' && echo "WARNING: Windows-path directory artifacts found"

# 6. agent-os still present
[ -d ".agent-os" ] && echo "WARNING: .agent-os/ vestigial — delete"
```

---

---

## Enforcement Rules (Zero-Tolerance)

These patterns are prohibited and must be corrected immediately when found. They recur across
the digitalmodel and worldenergydata repos and cause test discovery failures, import errors,
and inconsistent tooling.

### NEVER: tests/ inside src/

```
src/digitalmodel/asset_integrity/tests/   ← WRONG
tests/asset_integrity/                    ← CORRECT
```

Tests must never live inside the package tree. They belong in `tests/<domain>/`.

### NEVER: Generated/output files in tests/

```
tests/output/                 ← WRONG (committed artifacts)
tests/outputs/                ← WRONG (committed artifacts)
```

Add to `.gitignore`. These dirs hold generated test artifacts, not test code.

### NEVER: tests/unit/ wrapper (flat domain layout only)

```
tests/unit/well/              ← WRONG (unit/ is a redundant wrapper)
tests/unit/metocean/          ← WRONG
tests/well/                   ← CORRECT
tests/metocean/               ← CORRECT
```

The test root mirrors `src/<pkg>/` directly. No intermediate `unit/` or `modules/` wrapper.

### NEVER: Catch-all dirs in tests/ or src/

```
tests/phase2/                 ← WRONG (unnamed, no meaning)
tests/phase3/                 ← WRONG
src/worldenergydata/modules/  ← WRONG (catch-all at package level)
```

Every directory must map to a specific domain. Phased catch-all dirs must be migrated to
domain-aligned paths before merging.

### NEVER: kebab-case dirs in src/ Python tree

```
src/digitalmodel/visualization/orcaflex-dashboard/   ← WRONG (cannot be a Python package)
src/digitalmodel/visualization/orcaflex_dashboard/   ← CORRECT
```

All directories under `src/<package>/` must be snake_case — Python cannot import kebab dirs.

### NEVER: WRK deliverable reports in docs/

```
worldenergydata/docs/wrk-083-export-validation-report.md   ← WRONG
workspace-hub/.claude/work-queue/done/WRK-083.md           ← CORRECT
```

WRK deliverables live only in `workspace-hub/.claude/work-queue/`. Submodule `docs/` is for
reference documentation, not session work products.

### NEVER: Three or more parallel archive dirs

```
tests/_archived/          ← consolidate
tests/_archived_tests/    ← consolidate
tests/legacy_tests/       ← consolidate
tests/_archive/           ← CORRECT (single archive dir)
```

---

## See Also

- `/file-taxonomy` — where to place reports, results, data, and cache files
- `scripts/operations/validate-file-placement.sh` — automated enforcement checks
- `.claude/docs/workspace-structure.md` — full ecosystem canonical layout
- `.claude/rules/coding-style.md` — naming conventions (snake_case, kebab-case)
