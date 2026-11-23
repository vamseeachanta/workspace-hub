---
name: repo-structure-never-tests-inside-src
description: 'Sub-skill of repo-structure: NEVER: tests/ inside src/ (+7).'
version: 1.4.0
category: workspace
type: reference
scripts_exempt: true
---

# NEVER: tests/ inside src/ (+7)

## NEVER: tests/ inside src/


```
src/digitalmodel/asset_integrity/tests/   ← WRONG
tests/asset_integrity/                    ← CORRECT
```

Tests must never live inside the package tree. They belong in `tests/<domain>/`.


## NEVER: Generated/output files in tests/


```
tests/output/                 ← WRONG (committed artifacts)
tests/outputs/                ← WRONG (committed artifacts)
```

Add to `.gitignore`. These dirs hold generated test artifacts, not test code.


## NEVER: tests/unit/ wrapper (flat domain layout only)


```
tests/unit/well/              ← WRONG (unit/ is a redundant wrapper)
tests/unit/metocean/          ← WRONG
tests/well/                   ← CORRECT
tests/metocean/               ← CORRECT
```

The test root mirrors `src/<pkg>/` directly. No intermediate `unit/` or `modules/` wrapper.


## NEVER: Catch-all dirs in tests/ or src/


```
tests/phase2/                 ← WRONG (unnamed, no meaning)
tests/phase3/                 ← WRONG
src/worldenergydata/modules/  ← WRONG (catch-all at package level)
```

Every directory must map to a specific domain. Phased catch-all dirs must be migrated to
domain-aligned paths before merging.


## NEVER: kebab-case dirs in src/ Python tree


```
src/digitalmodel/visualization/orcaflex-dashboard/   ← WRONG (cannot be a Python package)
src/digitalmodel/visualization/orcaflex_dashboard/   ← CORRECT
```

All directories under `src/<package>/` must be snake_case — Python cannot import kebab dirs.


## NEVER: WRK deliverable reports in docs/


```
worldenergydata/docs/wrk-083-export-validation-report.md   ← WRONG
workspace-hub/.claude/work-queue/done/WRK-083.md           ← CORRECT
```

WRK deliverables live only in `workspace-hub/.claude/work-queue/`. Submodule `docs/` is for
reference documentation, not session work products.


## NEVER: Three or more parallel archive dirs


```
tests/_archived/          ← consolidate
tests/_archived_tests/    ← consolidate
tests/legacy_tests/       ← consolidate
tests/_archive/           ← CORRECT (single archive dir)
```


## NEVER: Non-Python files loose in src/ package tree


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
