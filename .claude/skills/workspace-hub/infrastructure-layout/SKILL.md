---
name: infrastructure-layout
version: "1.0.0"
category: workspace
description: "Canonical 5-domain layout for the infrastructure/ package in engineering Python repos (config, persistence, validation, utils, solvers). Apply when creating or auditing a repo's cross-cutting infrastructure layer."
invocation: /infrastructure-layout
applies-to: [claude, codex, gemini]
capabilities: []
requires: []
see_also: [repo-structure, file-taxonomy]
---

# Infrastructure Layout — Canonical Internal Package Structure

Use this skill when:
- **Creating** a new engineering Python repo that needs shared infrastructure
- **Auditing** an existing `infrastructure/` package for structural issues
- **Migrating** a monolithic or catch-all `infrastructure/` into domain-aligned modules
- **Reviewing** a PR that adds files to `infrastructure/`

## Quick Decision Tree — "Where does this file go?"

```
Is it shared across multiple domains in the same package?
│
├─ YES → Is it configuration loading / schema validation?
│        └─ YES → infrastructure/config/
│
├─ YES → Is it a database connection, cache, or audit trail?
│        └─ YES → infrastructure/persistence/
│
├─ YES → Is it a data validation pipeline or validator class?
│        └─ YES → infrastructure/validation/
│
├─ YES → Is it a numerical solver BASE CLASS or FRAMEWORK?
│        └─ YES → infrastructure/solvers/ (or base_solvers/)
│            Note: domain-specific implementations → domain package
│
├─ YES → Is it data I/O, ETL, visualization, or a utility function?
│        └─ YES → infrastructure/utils/
│
└─ NO  → It belongs in the DOMAIN package (structural/, subsea/, well/, etc.)

Is it a Flask/Dash app, blueprint, or web route?
└─ YES → src/<pkg>/web/   (NOT in infrastructure/)

Is it a test?
└─ YES → tests/infrastructure/<domain>/  (NOT in src/)
```

---

## What Is `infrastructure/`?

`infrastructure/` is the **cross-cutting layer** of an engineering Python package. It holds
concerns shared by all domains that are not domain-specific logic:

- Configuration loading and validation
- Database connections, caching, provenance tracking
- Input validation pipelines
- Shared utilities (data I/O, ETL, visualization helpers, math)
- Numerical solver framework (base classes, protocols, benchmarks)

**Not** in `infrastructure/`:
- Domain solvers (cathodic protection → `structural/`, VIV → `subsea/`)
- Web application blueprints and Flask routes (→ `web/`)
- Domain-specific plate buckling, well trajectory (→ `structural/`, `well/`)
- Per-domain data loaders (→ domain packages)

---

## Canonical 5-Domain Structure

```
src/<package>/infrastructure/
├── config/           ← all configuration loading and schema management
├── persistence/      ← databases, caches, provenance (formerly core/)
├── validation/       ← input validation pipelines and validators
├── utils/            ← shared utilities: data I/O, ETL, visualization, math
│   └── visualization/  ← matplotlib/plotly wrappers as a sub-package
└── solvers/ (or base_solvers/)  ← abstract solver framework, benchmarks, typed protocols
    ├── base.py           ← BaseSolver, ConfigurableSolver, AnalysisSolver
    ├── interfaces.py     ← SolverProtocol, typed protocol interfaces
    ├── structural/       ← FEM, buckling, stress elements
    ├── fatigue/          ← fatigue solvers (framework, not domain calcs)
    ├── viv/              ← VIV solver framework
    ├── marine/           ← marine solver framework
    ├── hydrodynamics/    ← hydrodynamic load calc framework
    ├── pipeline_solvers/ ← transformation / solver pipeline orchestration
    ├── well/             ← well geometry helpers
    └── benchmarks/       ← BenchmarkSuite, ReportGenerator
```

---

## Domain-by-Domain Rules

### `config/` — Configuration Management

**Contains:**
| File | Purpose |
|------|---------|
| `settings.py` | GlobalSettings (Pydantic BaseSettings + env-var support) |
| `registry.py` | ConfigRegistry, ConfigValidationError |
| `compat.py` | Backward-compat `load_config` shim |
| `framework.py` | ConfigLoader, SchemaValidator, ConfigManager |
| `models.py` | ConfigModel SQLAlchemy ORM base |
| `domains/` | YAML domain-config bundles (aqwa/, catenary/, orcaflex/, fatigue/, ...) |

**Rules:**
- `domains/` holds **data-only** YAML config bundles — no Python logic
- Use `pkgutil.get_data` or `importlib.resources` to load YAML; do NOT hardcode filesystem paths
- `base_configs/` is an alias for `config/` (legacy name) — shim only; canonical is `config/`

**Not here:** per-domain runtime config (→ `<domain>/config/`), pytest fixtures (→ `tests/fixtures/`)

---

### `persistence/` — Database, Cache, Provenance

**Contains:**
| File | Purpose |
|------|---------|
| `database_manager.py` | DatabaseManager (MSSQL/PG/MongoDB/Access connection pools) |
| `database_legacy.py` | Legacy DB wrapper (backward compat) |
| `sqlite.py` | SQLite local cache |
| `cache.py` | TTL/LRU in-process result cache |
| `provenance.py` | ProvenanceTracker (input hash + audit trail) |

**Rules:**
- Formerly named `core/` — keep a `core/__init__.py` shim if migrating
- No domain-specific query logic here — this is connection/pool management only
- SQLite is for local caching of intermediate results, not primary storage

---

### `validation/` — Input Validation Pipelines

**Contains:**
| File | Purpose |
|------|---------|
| `pipeline.py` | ValidationPipeline, BaseValidator, domain validators, ValidationCache, HTML report |
| `data_validator.py` | DataValidator (primary public API) |
| `template_validator.py` | Template schema validation |

**Rules:**
- `DataValidator` is the public surface — callers use `from infrastructure.validation import DataValidator`
- `validators/` is a deprecated alias — if it exists, it must be a DeprecationWarning shim only
- Domain validators (RangeValidator, MatrixValidator, etc.) may live here — they are generic, not domain-specific

---

### `utils/` — Shared Utilities

**Contains:**
| File | Purpose |
|------|---------|
| `data.py` | ReadData, SaveData, AttributeDict, Transform, DateTimeUtility |
| `ETL_components.py` | Excel-to-YAML ETL pipeline |
| `excel_utilities.py` | Spreadsheet read/write helpers |
| `ymlInput.py` | YAML input utilities |
| `time_series_components.py` | Time-series I/O and processing |
| `path_utils.py` | Filesystem path utilities |
| `parallel_processing.py` | Multiprocessing helpers |
| `update_deep.py` | Deep-merge for nested dicts |
| `basic_statistics.py` | Descriptive statistics |
| `standards_lookup.py` | Standards document discovery |
| `engineering_units.py` | Re-export bridge to `assetutilities.units` |
| `MaterialProperties.py` | Material property tables |
| `application_configuration.py` | Application-level config bootstrap |
| `database.py` | Legacy Database class |
| `send_email.py` | SMTP email dispatch |
| `visualization/` | Matplotlib/Plotly wrappers (sub-package) |
| `visualization/visualizations.py` | Matplotlib wrappers |
| `visualization/visualizations_interactive.py` | Interactive Plotly wrappers |
| `visualization/plotDefault.py` | Default plot styles |

**Rules:**
- `common/` is a deprecated alias for `utils/` — shim only; canonical is `utils/`
- `visualization/` is always a sub-package (not inline) so import paths are consistent
- Dead code (`visualization_unused.py` pattern) — delete, do not migrate

---

### `solvers/` (or `base_solvers/`) — Solver Framework

**Contains:**
| Path | Purpose |
|------|---------|
| `base.py` | BaseSolver, ConfigurableSolver, AnalysisSolver, SolverStatus |
| `interfaces.py` | SolverProtocol, ConfigurableSolverProtocol, typed protocols |
| `structural/` | Beam elements, elastic buckling, von Mises, matrix ops, FEA helpers |
| `fatigue/` | Fatigue solver framework (not domain calcs — those go in domain packages) |
| `viv/` | VIV analysis components, Shear7 model |
| `marine/` | Pipe properties, riser stack-up, ship design framework |
| `hydrodynamics/` | DNV RP H103 load calcs, cathodic protection calcs |
| `pipeline_solvers/` | Math solvers (polynomial, FFT, interpolation), transformation pipeline |
| `well/` | Well trajectory geometry (wellpath3D) |
| `config/` | Per-solver configuration schema |
| `benchmarks/` | BenchmarkSuite, ConfigurationBenchmarks, ReportGenerator |

**Rules:**
- Abstract base classes only — no domain-specific implementations (those belong in domain packages)
- `base_solvers/` is an acceptable name if the repo uses it consistently; do NOT rename mid-project
- Stub sub-packages (only `__init__.py`) are acceptable as reserved namespaces for future solvers

---

## What Does NOT Belong in `infrastructure/`

| Item | Correct location |
|------|-----------------|
| Flask/Dash apps, blueprints, routes | `src/<pkg>/web/` |
| Plate capacity / buckling domain solver | `src/<pkg>/structural/plate_capacity/` |
| Reservoir analysis scripts | `src/<pkg>/reservoir/` |
| Domain-specific cathodic protection analysis | `src/<pkg>/structural/cp/` or `src/<pkg>/subsea/cp/` |
| Per-domain data loaders (BSEE, EIA, SODIR) | `src/<pkg>/<domain>/` |
| Unit tests | `tests/infrastructure/` |
| Runtime config for a specific domain | `config/<domain>/` at repo root |
| Generated HTML reports | `reports/` (gitignored) |

---

## Canonical `__init__.py` Exports

Each domain package should re-export its primary public API from `__init__.py`
so callers use short imports (`from pkg.infrastructure.config import GlobalSettings`).

```python
# infrastructure/config/__init__.py
from .settings import GlobalSettings
from .registry import ConfigRegistry, ConfigValidationError
from .framework import ConfigLoader, SchemaValidator, ConfigManager
from .models import ConfigModel

__all__ = [
    "GlobalSettings", "ConfigRegistry", "ConfigValidationError",
    "ConfigLoader", "SchemaValidator", "ConfigManager", "ConfigModel",
]
```

```python
# infrastructure/persistence/__init__.py
from .database_manager import DatabaseManager
from .cache import TTLCache
from .provenance import ProvenanceTracker

__all__ = ["DatabaseManager", "TTLCache", "ProvenanceTracker"]
```

```python
# infrastructure/validation/__init__.py
from .data_validator import DataValidator
from .pipeline import ValidationPipeline, BaseValidator, ValidationCache

__all__ = ["DataValidator", "ValidationPipeline", "BaseValidator", "ValidationCache"]
```

```python
# infrastructure/solvers/__init__.py  (or base_solvers/)
from .base import BaseSolver, ConfigurableSolver, AnalysisSolver, SolverStatus
from .interfaces import SolverProtocol

__all__ = ["BaseSolver", "ConfigurableSolver", "AnalysisSolver", "SolverStatus", "SolverProtocol"]
```

```python
# infrastructure/utils/__init__.py
from .data import ReadData, SaveData, AttributeDict
from .update_deep import update_deep_dictionary
from .path_utils import resolve_path
from .engineering_units import convert_units

__all__ = ["ReadData", "SaveData", "AttributeDict", "update_deep_dictionary", "resolve_path", "convert_units"]
```

```python
# infrastructure/__init__.py  — top-level; expose domains, not symbols
"""Cross-cutting infrastructure: config, persistence, validation, utils, solvers."""
from . import config, persistence, validation, utils
try:
    from . import solvers
except ImportError:
    from . import base_solvers as solvers  # support both naming conventions
```

---

## Naming: `solvers/` vs `base_solvers/`

Both names are acceptable. Prefer `solvers/` for new repos. Use `base_solvers/` only
if the repo already has it and renaming would break callers.

| Repo | Canonical name | Notes |
|------|---------------|-------|
| digitalmodel (existing) | `base_solvers/` | Historical; do not rename mid-project |
| new repos | `solvers/` | Preferred |

Never use both simultaneously in the same repo.

---

## New Repo Bootstrap

When creating a new engineering Python repo with an `infrastructure/` layer:

```bash
# 1. Scaffold the 5 canonical packages
pkg=your_package_name
base=src/$pkg/infrastructure

for d in config persistence validation utils utils/visualization solvers; do
  mkdir -p $base/$d
  cat > $base/$d/__init__.py <<EOF
"""$d layer — see infrastructure-layout skill for canonical contents."""
EOF
done

# 2. Create top-level __init__.py
cat > $base/__init__.py <<EOF
"""Cross-cutting infrastructure: config, persistence, validation, utils, solvers."""
from . import config, persistence, validation, utils, solvers
EOF

# 3. Add pyproject.toml entry (src layout)
# [tool.setuptools.packages.find]
# where = ["src"]

# 4. Verify
python3 -c "import $pkg.infrastructure; print('OK')"
```

### Minimal `config/` for a new repo

```python
# src/<pkg>/infrastructure/config/settings.py
from pydantic_settings import BaseSettings

class GlobalSettings(BaseSettings):
    debug: bool = False
    log_level: str = "INFO"
    database_url: str = ""

    class Config:
        env_prefix = "APP_"
        env_file = ".env"
```

### Minimal `persistence/` for a new repo

```python
# src/<pkg>/infrastructure/persistence/cache.py
import time
from typing import Any, Dict, Optional, Tuple

class TTLCache:
    """Simple TTL cache for in-process result reuse."""
    def __init__(self, ttl_seconds: int = 300):
        self._store: Dict[str, Tuple[Any, float]] = {}
        self._ttl = ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        if key in self._store:
            value, ts = self._store[key]
            if time.time() - ts < self._ttl:
                return value
            del self._store[key]
        return None

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (value, time.time())
```

---

## Migration Guide (Existing Monolithic `infrastructure/`)

When `infrastructure/` has grown into a catch-all with 40+ mixed files:

### Step 1 — Audit and classify

```bash
# Count files per subdir
find src/<pkg>/infrastructure -maxdepth 2 -name "*.py" | \
  awk -F/ '{print $(NF-1)}' | sort | uniq -c | sort -rn

# Find external callers per module
grep -r "infrastructure\." src/ tests/ --include="*.py" | \
  grep -v "infrastructure/infrastructure" | \
  awk -F: '{print $1}' | sort | uniq
```

Classify every subdir into one of: `config | persistence | validation | utils | solvers | DOMAIN (move out)`

### Step 2 — Execute in safe phases (zero-risk first)

| Phase | Action | Risk |
|-------|--------|------|
| 2A | Merge config dirs; rename persistence; move template validator | Zero — add shims |
| 2B | Remove deprecated shim dirs with 0 callers | Zero |
| 2C | Extract web layer → `src/<pkg>/web/` | Low — no Python callers |
| 2D | Move engineering solvers from common/ → solvers/ | Medium — update callers |
| 2E | Move misplaced domain logic out of infrastructure/ | Low if 0 callers |
| 2F | Move residual utils/IO files → utils/; shim common/ | Medium — update callers |

### Step 3 — Backward-compat shim pattern

For every file moved, leave a shim at the old path:

```python
# infrastructure/common/data.py  ← shim after moving to utils/
"""Backward-compat shim. Use infrastructure.utils.data instead."""
import warnings
warnings.warn(
    "infrastructure.common.data is deprecated. "
    "Use infrastructure.utils.data instead.",
    DeprecationWarning,
    stacklevel=2,
)
from infrastructure.utils.data import *  # noqa: F401,F403
```

Keep shims until all callers are updated. Then delete shim dirs in a separate cleanup PR.

### Step 4 — Update callers

```bash
# Find all callers of a moved module
grep -r "from.*infrastructure\.common\." src/ tests/ --include="*.py"
grep -r "infrastructure\.common\." src/ tests/ --include="*.py"

# After updating callers, verify zero remaining old-path imports
grep -r "infrastructure\.common\b" src/ --include="*.py" | \
  grep -v "__init__.py\|DeprecationWarning"
```

---

## Compliance Checks

Run after any structural change to `infrastructure/`:

```bash
pkg=your_package_name
infra=src/$pkg/infrastructure

# 1. Canonical dirs present
for d in config persistence validation utils solvers; do
  [ -d "$infra/$d" ] && echo "OK: $d" || echo "MISSING: $d"
done

# 2. No stale catch-all dirs (common/, core/, validators/ should be shims only)
for legacy in common core validators base_configs; do
  if [ -d "$infra/$legacy" ]; then
    real=$(find "$infra/$legacy" -name "*.py" | xargs grep -L "DeprecationWarning" 2>/dev/null | grep -v __init__ | wc -l)
    [ "$real" -gt 0 ] && echo "WARN: $legacy/ has $real non-shim files — migrate to canonical path"
  fi
done

# 3. Web layer not in infrastructure/
[ -d "$infra/services" ] && \
  find "$infra/services" -name "*.py" | xargs grep -L "DeprecationWarning" 2>/dev/null | \
  grep -v __init__ | grep -q . && \
  echo "WARN: real Flask/web code still in infrastructure/services/ — move to web/"

# 4. No domain logic embedded in infrastructure/domains/
[ -d "$infra/domains" ] && \
  find "$infra/domains" -name "*.py" | xargs grep -L "DeprecationWarning" 2>/dev/null | \
  grep -q . && echo "WARN: infrastructure/domains/ has non-shim files — move to domain packages"

# 5. External callers still using deprecated paths
for legacy_path in "infrastructure\.common\b" "infrastructure\.core\b" "infrastructure\.validators\b" "infrastructure\.base_configs\b"; do
  count=$(grep -r "$legacy_path" src/ --include="*.py" | grep -v "DeprecationWarning\|# " | wc -l)
  [ "$count" -gt 0 ] && echo "WARN: $count callers still using $legacy_path"
done

# 6. Run import smoke test
python3 -c "import $pkg.infrastructure.config; import $pkg.infrastructure.persistence; import $pkg.infrastructure.validation; import $pkg.infrastructure.utils; import $pkg.infrastructure.solvers; print('All 5 domains import OK')"
```

---

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

## Real-World Reference

This skill was developed during WRK-415 (2026-02-24) on the `digitalmodel` repo, which had
218 Python files across 12 mixed subdirs. The migration was executed in 6 phases (2A–2F)
and produced the structure above. Spec at `digitalmodel/specs/modules/infrastructure-refactor.md`.

---

## See Also

- `/repo-structure` — top-level repo layout (src/, tests/, docs/, config/)
- `/file-taxonomy` — where to place reports, data, and generated files
- `scripts/operations/validate-file-placement.sh` — automated repo-wide placement checks
- `digitalmodel/specs/modules/infrastructure-refactor.md` — detailed migration audit (reference)
