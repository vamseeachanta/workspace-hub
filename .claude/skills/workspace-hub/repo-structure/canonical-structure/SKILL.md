---
name: repo-structure-canonical-structure
description: 'Sub-skill of repo-structure: Canonical Structure (+1).'
version: 1.4.0
category: workspace
type: reference
scripts_exempt: true
---

# Canonical Structure (+1)

## Canonical Structure


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


## Rules


1. **One package per `src/`** — `src/` contains exactly `src/<package_name>/`. No other
   Python packages at `src/other_package/` level.
2. **`__init__.py` required** at every directory that is a Python package.
3. **`pythonpath = src`** in `pytest.ini` — never rely on PYTHONPATH env variable for CI.
4. **Tests mirror src** — `tests/<domain>/` maps to `src/<package>/<domain>/`.
   Do NOT use `tests/modules/<domain>/` wrapper — the `modules/` level is redundant.
5. **No loose scripts at root** — ad-hoc `.py` files at repo root belong in `scripts/`
   or `src/<package>/cli/` or `src/<package>/tools/`.

---
