---
name: repo-structure
version: "1.4.0"
category: workspace
description: "Canonical source layout, test mirroring, root cleanliness, gitignore, docs classification, and committed artifact rules for all workspace-hub tier-1 repos. Consult before creating directories or files in any submodule."
invocation: /repo-structure
applies-to: [claude, codex, gemini]
capabilities: []
requires: []
see_also: [file-taxonomy, infrastructure-layout, clean-code]
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
| `setup.py` (when pyproject.toml exists) | DELETE — pyproject.toml supersedes it |
| `archive/`, `backups/` | `_archive/` (single, underscore-prefixed) |
| `*.xlsx`, `*.csv` output files | `results/<domain>/` and gitignored |
| `test_export*.json` | `tests/<domain>/fixtures/` or gitignored |
| `COVERAGE_ANALYSIS.txt` | gitignored (session artifact) |
| `verdict.txt`, `test_output_ss` | gitignored (session artifacts) |
| `coverage.wrk*.xml` | gitignored (session artifacts) |
| Windows path dirs (`D:\...`) | DELETE — filesystem artifact, never track |

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

These must be in `.gitignore` for every Python package repo. Copy this block as a starting point — every repo MUST have all sections.

```gitignore
# ── Build artifacts — NEVER commit ──────────────────────────────────────────
dist/
build/
*.egg-info/
__pycache__/
*.pyc
*.pyo
*.pyd
setup.py.bak

# ── Virtual environments ─────────────────────────────────────────────────────
.venv/
venv/
.env

# ── Coverage artifacts ───────────────────────────────────────────────────────
htmlcov/
.coverage
coverage.json
coverage.xml
coverage*.xml
.coverage_report.json

# ── Runtime output — NEVER commit ───────────────────────────────────────────
logs/
cache/
results/
reports/
output/
outputs/
benchmark_output/

# ── Test artifacts ────────────────────────────────────────────────────────────
tests/output/
tests/outputs/
test_output/
test_output_ss

# ── Session artifacts — NEVER commit ─────────────────────────────────────────
verdict.txt
coverage.wrk*.xml
COVERAGE_ANALYSIS.txt
memory/

# ── Generated output files at root — NEVER commit ────────────────────────────
report_*.xlsx
report_*.csv
test_export*.json
analyze_coverage.py   # move to scripts/analysis/ if needed

# ── Legacy framework dirs (delete if present, gitignore as safety net) ───────
.agent-os/
.hive-mind/
.swarm/
.claude-flow/

# ── IDE / OS ─────────────────────────────────────────────────────────────────
.DS_Store
Thumbs.db
*.swp
```

### Gitignore Enforcement: Root-Level Output Artifacts

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

## docs/ Content Classification

`docs/` is for **user-facing reference documentation only**. It is NOT an agent configuration directory.

### Allowed in docs/

| Content Type | Location |
|-------------|----------|
| Reference docs — explains how a module works | `docs/modules/<domain>/` or `docs/domains/<domain>/` |
| How-to guides for humans | `docs/guides/` |
| API documentation | `docs/api/` |
| Data source descriptions | `docs/data-sources/` |
| Migration guides | `docs/guides/migration-*.md` |
| Domain-specific references | `docs/<domain>/` (e.g., `docs/hse/`, `docs/petrophysics/`) |

### NOT Allowed in docs/

| Misplaced File | Correct Location |
|----------------|-----------------|
| `AGENT_OS_COMMANDS.md` | DELETE (agent_os is archived) |
| `MANDATORY_SLASH_COMMAND_ECOSYSTEM.md` | `.claude/docs/` or DELETE |
| `AI_AGENT_ORCHESTRATION.md` | `.claude/docs/ai-orchestration.md` |
| `AI_USAGE_GUIDELINES.md` | `.claude/docs/` if agent-facing, else `docs/guides/` |
| `sub_ai/` directory | `.claude/docs/` |
| `raw_data/` | `data/<domain>/` |
| `prompt-review/` | `.claude/docs/` or delete |
| WRK deliverable reports | `workspace-hub/.claude/work-queue/done/` |
| Session notes | `.claude/docs/` or delete |

**Rule**: If a file in `docs/` contains slash commands, agent protocols, or provider instructions, it belongs in `.claude/docs/`, not `docs/`.

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

Run against any repo before and after structural changes. For automated enforcement, use `scripts/operations/validate-file-placement.sh`.

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

# 7. Tests inside src/ (FAIL)
find src/ -name "test_*.py" -o -name "*_test.py" | grep -v __pycache__

# 8. Committed output artifacts at root (FAIL)
git ls-files | grep -E '^(report_.*\.(xlsx|csv)|test_export.*\.json|COVERAGE_ANALYSIS\.txt|verdict\.txt)$'

# 9. Agent harness files in docs/ (WARN)
ls docs/ | grep -iE '^(AGENT_OS|MANDATORY_SLASH|AI_AGENT_ORCHESTRATION)' 2>/dev/null

# 10. Legacy setup.py alongside pyproject.toml (WARN)
[ -f setup.py ] && [ -f pyproject.toml ] && echo "WARNING: setup.py is superseded by pyproject.toml — remove it"
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

### NEVER: Non-Python files loose in src/ package tree

Non-Python files in `src/` create invisible coupling between package code and static assets.
They cannot be tested as Python modules and confuse linters and type-checkers.

| File type | Wrong location | Correct location |
|-----------|---------------|-----------------|
| `.md` documentation | `src/<pkg>/bsee/docs/` | `docs/domains/bsee/` |
| `.ipynb` notebooks | `src/<pkg>/specialized/gis/` | `notebooks/gis/` |
| `.yml` config | `src/<pkg>/specialized/gis/arcgis.yml` | `config/gis/arcgis.yml` |
| Empty `__init__.py`-only dirs | anywhere in src/ | DELETE |

**Exception — package resources**: `.sql` query files and `.html` Jinja templates that are
loaded at runtime via `importlib.resources` MAY remain inside `src/<pkg>/<domain>/sql/` or
`src/<pkg>/<domain>/templates/`. **Required**: they MUST be declared in `pyproject.toml`:

```toml
[tool.setuptools.package-data]
"worldenergydata.bsee" = ["sql/*.sql", "templates/*.html"]
```

Without this declaration, pip install will silently omit them.

**Quick scan for violations:**
```bash
# Non-Python files in src/
find src/ -not -name "*.py" -not -name "*.pyc" -not -path "*/__pycache__/*" \
  -not -path "*/.git/*" -not -name "__init__.py" | grep -v ".egg-info"
```

---

## See Also

- `/file-taxonomy` — where to place reports, results, data, and cache files
- `/infrastructure-layout` — canonical 5-domain layout for the infrastructure/ package (config, persistence, validation, utils, solvers)
- `scripts/operations/validate-file-placement.sh` — automated enforcement checks
- `.claude/docs/workspace-structure.md` — full ecosystem canonical layout
- `.claude/rules/coding-style.md` — naming conventions (snake_case, kebab-case)
