---
name: infrastructure-layout-config-configuration-management
description: "Sub-skill of infrastructure-layout: `config/` \u2014 Configuration Management\
  \ (+4)."
version: 1.0.0
category: workspace
type: reference
scripts_exempt: true
---

# `config/` — Configuration Management (+4)

## `config/` — Configuration Management


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


## `persistence/` — Database, Cache, Provenance


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


## `validation/` — Input Validation Pipelines


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


## `utils/` — Shared Utilities


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


## `solvers/` (or `base_solvers/`) — Solver Framework


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
