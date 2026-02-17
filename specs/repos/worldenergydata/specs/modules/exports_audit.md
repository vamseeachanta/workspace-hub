# Module Exports Audit Report

**Version:** 1.0.0
**Date:** 2026-01-24
**Purpose:** Comprehensive audit of `__all__` declarations in `src/worldenergydata/modules/`

## Executive Summary

This audit documents the current public API surface across all modules in the worldenergydata package. The analysis covers:
- Current `__all__` exports per module
- Import patterns used (lazy imports, direct re-exports, submodule strings)
- Missing `__all__` declarations that should be added

---

## Module Inventory

| Module | Has `__init__.py` | Has `__all__` | Pattern Type |
|--------|-------------------|---------------|--------------|
| `bsee/` | No (uses bsee.py) | N/A | Router class |
| `fdas/` | Yes | Yes | Direct re-exports |
| `marine_safety/` | Yes | Yes | Submodule strings |
| `hse/` | Yes (empty) | No | Missing |
| `vessel_hull_models/` | Yes | Yes | Submodule strings |
| `well_production_dashboard/` | Yes | Yes | Direct re-exports |
| `reporting/` | Yes | Yes | Submodule strings |

---

## Detailed Module Analysis

### 1. BSEE Module (Bureau of Safety and Environmental Enforcement)

**Location:** `src/worldenergydata/modules/bsee/`

**Root `__init__.py`:** MISSING - Uses `bsee.py` as entry point

**Pattern:** Router class pattern with nested submodules

#### Submodule Exports

| Submodule | `__all__` | Pattern | Exports |
|-----------|-----------|---------|---------|
| `data/cache/` | Yes | Direct re-exports | `ChunkManager`, `ChunkMetadata` |
| `data/config/` | Yes | Direct re-exports | `ConfigRouter` |
| `data/enhanced/` | Yes | Direct re-exports | `DataRefreshChunked` |
| `data/processors/` | Yes | Direct re-exports | `MemoryProcessor`, `OptimizedProcessor` |
| `data/scrapers/` | Yes | Direct re-exports | `BSEEWebScraper` |
| `analysis/financial/` | Yes | Lazy imports + functions | `SMEAnalyzer`, `SMEDataLoader`, `LeaseGrouper`, `DrillingCompletion`, `CashFlowCalculator`, `FinancialParameters`, `DevelopmentType`, `ReportGenerator`, `SMEFinancialCLI`, `SMEConfigLoader`, `load_sme_config`, `run_sme_analysis`, `__version__` |
| `analysis/well_data_verification/` | Yes | Direct re-exports | `VerificationResult`, `VerificationWorkflow`, `VerificationError`, `VerificationConfig`, `BSEEDataAdapter` |
| `analysis/well_data_verification/audit/` | Yes | Direct re-exports | `AuditDatabase`, `AuditEvent`, `UserActivity`, `VerificationStatus`, `DataLineage`, `AuditLogger`, `ActivityTracker`, `VerificationStatusManager`, `DataLineageTracker`, `ComplianceReport`, `ComplianceReportGenerator` |
| `analysis/well_data_verification/engine/` | Yes | Direct re-exports | `WorkflowEngine`, `WorkflowState`, `WorkflowStep`, `WorkflowSession`, `WorkflowCheckpoint`, `StepValidator`, `WorkflowValidator`, `ProgressTracker`, `StepStatus` |
| `paleowells/` | Yes | Direct re-exports | `PaleowellsDataProcessor`, `PaleowellsVisualizer` |
| `reports/comprehensive/` | Yes | Direct re-exports | `ReportController`, `ReportConfiguration`, `ReportParameters`, `ReportType`, `OrganizationalUnit`, `Well`, `Lease`, `Field`, `Block`, `WellSummary`, `ProductionMetrics`, `EconomicMetrics`, `HierarchyLevel`, `ProductionPeriod`, `HierarchicalDataLoader`, `DataAggregator`, `BlockAggregator`, `FieldAggregator`, `LeaseAggregator` |
| `reports/comprehensive/aggregators/` | Yes | Direct re-exports | `DataAggregator`, `BlockAggregator`, `FieldAggregator`, `LeaseAggregator` |
| `reports/comprehensive/exporters/` | Yes | Direct re-exports | `ReportExporter`, `ExportFormat`, `ExportConfig`, `ExportResult` |
| `reports/comprehensive/performance/` | Yes | Direct re-exports | `MetricsCache`, `CacheEntry`, `CachedAggregator`, `CacheManager`, `cache_manager`, `ParallelProcessor`, `ProcessingResult`, `BatchProcessor` |
| `reports/comprehensive/templates/` | Yes | Direct re-exports | `BaseReportTemplate`, `TemplateType`, `TemplateContext`, `TemplateLoader`, `TemplateConfig` |
| `reports/comprehensive/visualizations/` | Yes | Direct re-exports | `ProductionChart`, `WellPerformanceChart`, `EconomicChart`, `GeographicChart`, `DashboardBuilder`, `ChartConfig`, `PerformanceMetrics`, `EconomicMetrics`, `WellLocation`, `FieldBoundary`, `DashboardConfig`, `DashboardChartConfig` |

**BSEE Issues:**
1. No root `__init__.py` - module structure relies on direct file imports
2. Inconsistent - some submodules use lazy imports, most use direct
3. Many analysis submodules (`bsee_analysis.py`, `well_api12.py`, etc.) lack `__init__.py` packaging

---

### 2. FDAS Module (Field Development Analysis System)

**Location:** `src/worldenergydata/modules/fdas/`

**Root `__init__.py`:** Present with comprehensive `__all__`

**Pattern:** Direct re-exports from submodules

```python
__all__ = [
    # Core financial
    'excel_like_mirr',
    'calculate_npv',
    'calculate_irr',
    'calculate_all_metrics',
    'FinancialCalculationError',
    # Configuration
    'AssumptionsManager',
    'PriceDeckManager',
    'classify_dev_system_by_depth',
    'ConfigurationError',
    # Adapters
    'BseeAdapter',
    'LeaseMapping',
    'AdapterError',
    # Metadata
    '__version__',
]
```

#### Submodule Exports

| Submodule | `__all__` | Exports |
|-----------|-----------|---------|
| `core/` | Yes | `excel_like_mirr`, `calculate_npv`, `calculate_trimmed_npv`, `calculate_irr`, `calculate_payback_period`, `validate_cashflow_stream`, `calculate_all_metrics`, `FinancialCalculationError`, `normalize_dev_system`, `classify_dev_system_by_depth`, `AssumptionsManager`, `PriceDeckManager`, `ConfigurationError`, `load_configuration`, `DEFAULT_ASSUMPTIONS` |
| `adapters/` | Yes | `BseeAdapter`, `LeaseMapping`, `WellDataAdapter`, `ProductionAdapter`, `AdapterError` |
| `data/` | Yes | `ProductionProcessor`, `aggregate_monthly_production`, `identify_first_oil_date`, `ProductionProcessingError`, `DrillingTimelineExtractor`, `CompletionActivityClassifier`, `calculate_drilling_days`, `DrillingDataError` |
| `analysis/` | Yes | `CashflowEngine`, `MonthlyCashflowModel`, `generate_monthly_cashflow`, `CashflowError` |
| `reports/` | Yes | `ExcelReportGenerator`, `FDASReportBuilder`, `format_financial_summary`, `create_project_summary_sheet`, `ReportGenerationError` |

**FDAS Issues:**
1. Root `__all__` is incomplete - missing `calculate_trimmed_npv`, `calculate_payback_period`, `validate_cashflow_stream` from core
2. Missing `WellDataAdapter`, `ProductionAdapter` from adapters in root exports
3. Missing entire `data/` submodule exports from root
4. Missing entire `analysis/` submodule exports from root
5. Missing entire `reports/` submodule exports from root

---

### 3. Marine Safety Module

**Location:** `src/worldenergydata/modules/marine_safety/`

**Root `__init__.py`:** Present with submodule string exports

**Pattern:** Submodule strings with module-level imports

```python
__all__: List[str] = [
    "config",
    "constants",
    "exceptions",
    "database",
    "scrapers",
    "utils",
]
```

#### Submodule Exports

| Submodule | `__all__` | Pattern | Exports |
|-----------|-----------|---------|---------|
| `database/` | Yes | Submodule strings | `models`, `db_manager` |
| `scrapers/` | Yes | Submodule strings | `base_scraper` |
| `utils/` | Yes | Submodule strings | `logger`, `validators` |
| `processors/` | Yes | Direct re-exports | `BaseProcessor`, `DataCleaner`, `DataNormalizer` |
| `importers/` | Yes | Direct re-exports | `BaseImporter`, `MISLEImporter` |
| `analysis/` | Yes | Direct re-exports | `CauseStatistics`, `FrequencyDistribution`, `TemporalTrend`, `CrossTabulation`, `StatisticalSummary`, `HatchMaloperationAnalyzer` |
| `analysis/incidents/` | Yes | Direct re-exports | `HatchMaloperationAnalyzer` |

**Marine Safety Issues:**
1. Root `__all__` uses submodule strings but doesn't export `processors`, `importers`, or `analysis`
2. `cli.py` exists but not in `__all__`
3. Inconsistent pattern - some submodules use strings, others use direct re-exports

---

### 4. HSE Module (Health, Safety, Environment)

**Location:** `src/worldenergydata/modules/hse/`

**Root `__init__.py`:** Empty (only contains newline)

**Pattern:** MISSING

```python
# Current content is empty
```

#### Submodule Exports

| Submodule | `__all__` | Exports |
|-----------|-----------|---------|
| `database/` | Yes | `Base`, `HSEIncident`, `InjuryIncident`, `SpillIncident`, `ViolationIncident`, `EquipmentFailure` |

**HSE Issues:**
1. **CRITICAL:** Root `__init__.py` has no `__all__` declaration
2. `database/` submodule is not exposed at root level
3. Module is essentially inaccessible from package root

---

### 5. Vessel Hull Models Module

**Location:** `src/worldenergydata/modules/vessel_hull_models/`

**Root `__init__.py`:** Present with submodule string exports

**Pattern:** Submodule strings without actual imports (incomplete)

```python
__all__: List[str] = [
    "config",
    "constants",
    "exceptions",
    "data",
    "geometry",
    "visualization",
]
```

#### Submodule Exports

| Submodule | `__all__` | Exports |
|-----------|-----------|---------|
| `data/` | Yes | `VesselHullModel`, `VesselHullModelCreate`, `VesselHullModelUpdate` |
| `data/cache/` | Empty | None |
| `geometry/` | Yes | `OBJParser`, `OBJMesh`, `parse_obj_file`, `validate_obj_file`, `GDFHeader`, `parse_gdf_header`, `parse_gdf_file`, `convert_gdf_to_obj`, `validate_gdf_file`, `export_to_msh`, `convert_obj_to_msh`, `convert_gdf_to_msh`, `validate_msh_file` |
| `visualization/` | Yes | `render_vessel_hull`, `create_hull_figure`, `export_hull_html`, `export_hull_png`, `render_obj_to_png`, `generate_preview_gallery`, `create_comparison_grid` |
| `visualization/templates/` | Empty | None |
| `acquisition/` | Yes (empty) | None |
| `acquisition/repository_clients/` | Empty | None |
| `reports/` | Yes (empty) | None |

**Vessel Hull Models Issues:**
1. Root `__all__` references submodule strings but doesn't import them
2. `acquisition/` declared as empty `__all__ = []` - no public API
3. `reports/` declared as empty `__all__ = []` - no public API
4. `cli.py` exists but not in `__all__`
5. Several nested `__init__.py` files are empty placeholders

---

### 6. Well Production Dashboard Module

**Location:** `src/worldenergydata/modules/well_production_dashboard/`

**Root `__init__.py`:** Present with direct re-exports

**Pattern:** Direct re-exports

```python
__all__ = [
    'WellProductionDashboard',
    'WellDashboardConfig',
    'WellMetrics',
    'FieldAggregator',
    'DashboardAPI',
    'DashboardCLI'
]
```

**Well Production Dashboard Issues:**
1. Many module files not in `__all__`:
   - `api_enhanced.py`
   - `cache_config.py`
   - `export_manager.py`
   - `field_aggregation.py` (has `FieldAggregator` but may have more)
   - `interactive_components.py`
   - `monitoring.py`
   - `query_optimizer.py`
   - `well_detail_views.py`
2. Need to verify if additional public classes/functions exist in excluded files

---

### 7. Reporting Module

**Location:** `src/worldenergydata/modules/reporting/`

**Root `__init__.py`:** Present with submodule string exports

**Pattern:** Submodule strings

```python
__all__ = ["templates", "utils"]
```

#### Submodule Exports

| Submodule | `__all__` | Exports |
|-----------|-----------|---------|
| `templates/` | Missing | None (empty `__init__.py`) |
| `utils/` | Missing | None (empty `__init__.py`) |

**Reporting Issues:**
1. Both referenced submodules have empty `__init__.py` files
2. Module is essentially a placeholder with no actual exports
3. Should either be populated or removed

---

## Import Pattern Analysis

### Pattern Types Found

1. **Direct Re-exports (Recommended)**
   ```python
   from .submodule import Class, function
   __all__ = ['Class', 'function']
   ```
   Used by: FDAS, Well Production Dashboard, most BSEE submodules

2. **Submodule String Exports**
   ```python
   __all__ = ["submodule1", "submodule2"]
   from package import submodule1, submodule2
   ```
   Used by: Marine Safety, Vessel Hull Models, Reporting

3. **Lazy Imports with Try/Except**
   ```python
   def _lazy_import():
       global Class
       try:
           from .file import Class
       except ImportError:
           Class = None
   ```
   Used by: BSEE `analysis/financial/`

4. **Empty Declarations**
   ```python
   __all__ = []
   ```
   Used by: Vessel Hull Models `acquisition/`, `reports/`

5. **Missing Declarations**
   Used by: HSE root, Reporting submodules, various BSEE files

---

## Recommendations

### 1. Standardize on Direct Re-exports Pattern

**Rationale:** Provides explicit, IDE-friendly exports with clear public API surface.

**Template:**
```python
"""
Module docstring.
"""

from .submodule import (
    PublicClass,
    public_function,
    PublicException,
)

__version__ = "1.0.0"

__all__ = [
    "PublicClass",
    "public_function",
    "PublicException",
    "__version__",
]
```

### 2. Priority Fixes

| Priority | Module | Action |
|----------|--------|--------|
| Critical | `bsee/` | Create root `__init__.py` with proper exports |
| Critical | `hse/` | Add `__all__` with database exports |
| High | `fdas/` | Complete root `__all__` with all submodule exports |
| High | `marine_safety/` | Add missing submodules (`processors`, `importers`, `analysis`) |
| Medium | `vessel_hull_models/` | Implement proper imports for declared submodules |
| Medium | `reporting/` | Either implement submodules or remove placeholder |
| Low | `well_production_dashboard/` | Audit additional files for public exports |

### 3. Consistency Guidelines

1. **Always use `__all__`** - Even for internal-only modules, declare empty `__all__ = []`
2. **Type annotate `__all__`** - Use `__all__: List[str] = [...]` for clarity
3. **Group exports** - Use comments to categorize (Classes, Functions, Exceptions, Constants)
4. **Include version** - Add `__version__` to all module-level `__all__`
5. **Avoid lazy imports** - Unless circular dependency issues require it

### 4. Migration Path

1. Create `src/worldenergydata/modules/__init__.py` with lazy module discovery
2. Add root `__init__.py` to BSEE module
3. Populate HSE root exports
4. Audit each module for internal-only vs public API designation
5. Generate API documentation from `__all__` declarations

---

## Appendix: Export Count Summary

| Module | Root Exports | Submodule Exports | Total Unique |
|--------|--------------|-------------------|--------------|
| BSEE | 0 (missing) | ~75+ | ~75+ |
| FDAS | 13 | 31 | 44 |
| Marine Safety | 6 | 17 | 23 |
| HSE | 0 (missing) | 6 | 6 |
| Vessel Hull Models | 6 | 19 | 25 |
| Well Production Dashboard | 6 | 0 | 6 |
| Reporting | 2 | 0 | 2 |

**Total Documented Exports:** ~181 (estimated, pending BSEE root creation)
