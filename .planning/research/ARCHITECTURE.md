# Architecture Research: OrcaWave Automation Features

**Domain:** Hydrodynamic diffraction analysis automation (OrcaWave/OrcaFlex integration)
**Researched:** 2026-03-29
**Confidence:** HIGH (based on direct codebase inspection of existing components)

## Existing Architecture Inventory

Before defining new components, here is what exists and where it lives. Every new feature must slot into this structure or explicitly extend it.

### Layer Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                       CLI / Entry Points                            │
│  Click CLI (diffraction/cli.py)  |  Orchestrator (solvers/         │
│  OrcaWave MCP server             |  orcawave/orchestrator.py)      │
├─────────────────────────────────────────────────────────────────────┤
│                    Batch / Workflow Orchestration                    │
│  orcawave_batch_runner.py        |  batch_processor.py             │
│  benchmark_runner.py             |  (NEW: sensitivity_runner)      │
├─────────────────────────────────────────────────────────────────────┤
│                    Input Schema / Spec Layer                        │
│  input_schemas.py (DiffractionSpec, Pydantic v2)                   │
│  spec_converter.py -> orcawave_backend.py (spec -> .yml)           │
│                     -> aqwa_backend.py                              │
├─────────────────────────────────────────────────────────────────────┤
│                    Solver Execution Layer                            │
│  orcawave_runner.py (RunConfig, RunResult, RunStatus)              │
│  (requires licensed-win-1 for actual execution)                    │
├─────────────────────────────────────────────────���───────────────────┤
│                    Result Extraction & Validation                    │
│  result_extractor.py  |  orcawave_data_extraction.py               │
│  output_validator.py  |  output_schemas.py (DiffractionResults)    │
│  orcawave_converter.py (OrcFxAPI -> unified schema)                │
├───────────────────────────��──────────────────────────���──────────────┤
│                    Comparison & Analysis                             │
│  comparison_framework.py (ComparisonReport, DeviationStatistics)   │
│  multi_solver_comparator.py  |  benchmark_correlation.py           │
│  (NEW: sensitivity_analyzer)                                       │
├─────────────────────────��───────────────────────────────────────────┤
│                    Report Generation                                │
│  report_generator.py (shim -> sub-modules)                         │
│  report_data_models.py  |  report_computations.py                  │
│  report_extractors.py   |  report_builders*.py (4 files)           │
│  orcawave/reporting/ (builder.py, config.py, 7 section modules)   │
│  orcaflex/reporting/ (builder.py, config.py, 7 section modules)   │
│  (NEW: unified_report_builder, report_templates/)                  │
├──────────────────────────────────────────��──────────────────────────┤
│                    Export Layer                                      │
│  orcaflex_exporter.py  |  polars_exporter.py                       │
│  rao_plotter.py        |  benchmark_plotter.py (259 Plotly plots)  │
├─────────────────────────────────────────────────────────────────────┤
│                    Data / Config Layer                               │
│  docs/domains/orcawave/ (L00-L04 benchmarks, hull_forms, examples) │
│  YAML spec files (spec.yml per benchmark)                          │
│  docs/domains/orcawave/examples/report_config_template.yml         │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities (Existing)

| Component | Location | Responsibility |
|-----------|----------|----------------|
| `DiffractionSpec` | `diffraction/input_schemas.py` | Canonical solver-agnostic YAML schema (Pydantic v2) |
| `OrcaWaveBackend` | `diffraction/orcawave_backend.py` | Converts DiffractionSpec to OrcaWave .yml input |
| `SpecConverter` | `diffraction/spec_converter.py` | Facade: spec.yml -> solver-specific inputs |
| `OrcaWaveRunner` | `diffraction/orcawave_runner.py` | Bridges spec -> file generation -> solver execution |
| `OrcaWaveBatchRunner` | `diffraction/orcawave_batch_runner.py` | Multi-job orchestration with parallel execution |
| `BatchProcessor` | `diffraction/batch_processor.py` | Multi-vessel batch conversion (AQWA/OrcaWave -> unified) |
| `ResultExtractor` | `diffraction/result_extractor.py` | Raw solver output -> DiffractionResults |
| `OutputValidator` | `diffraction/output_validator.py` | Physics-based validation checks on results |
| `DiffractionResults` | `diffraction/output_schemas.py` | Unified output dataclass (RAOs, added mass, damping) |
| `ComparisonReport` | `diffraction/comparison_framework.py` | N-way solver deviation statistics |
| `BenchmarkRunner` | `diffraction/benchmark_runner.py` | End-to-end benchmark orchestration with plots |
| `DiffractionReportData` | `diffraction/report_data_models.py` | Pydantic model for report rendering |
| `generate_diffraction_report` | `diffraction/report_generator.py` | Physics-causal-chain HTML report from DiffractionReportData |
| `OrcaWaveReportBuilder` | `orcawave/reporting/builder.py` | Section-based HTML from .owr via OrcFxAPI.Diffraction |
| `OrcaFlexReportBuilder` | `orcaflex/reporting/builder.py` | Section-based HTML from .sim via OrcFxAPI.Model |
| `ReportConfig` (orcawave) | `orcawave/reporting/config.py` | Pydantic config: per-section enable/disable |
| `OrcaFlexExporter` | `diffraction/orcaflex_exporter.py` | DiffractionResults -> OrcaFlex vessel type YAML/CSV/Excel |
| `OrcaWaveOrchestrator` | `solvers/orcawave/diffraction/orchestrator.py` | Legacy 5-phase Windows workflow (setup/execute/process/QA/package) |
| `SensitivityAnalysisService` | `visualization/orcaflex_dashboard/backend/` | OrcaFlex-specific sensitivity (OAT, Sobol, Monte Carlo) |

### Existing Patterns Worth Preserving

1. **Pydantic v2 schemas as contracts**: `DiffractionSpec` and `ReportConfig` establish the pattern. New features must use Pydantic v2 models for all configuration.
2. **Section-based report builders**: Both `orcawave/reporting/builder.py` and `orcaflex/reporting/builder.py` use the same pattern: config toggles sections, each section is a separate module with a `build_*()` function.
3. **Dry-run mode**: `OrcaWaveRunner` and `OrcaWaveOrchestrator` both support dry-run. All new orchestration must preserve this for CI.
4. **Backend pattern**: `orcawave_backend.py` and `aqwa_backend.py` behind `SpecConverter` facade. New spec generation follows this.
5. **Split sub-modules**: `report_generator.py` was decomposed (WRK-591) into `report_data_models`, `report_computations`, `report_extractors`, `report_builders*`. New report code should follow the same split.

## New Architecture: Integration of Automation Features

### System Overview with New Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CLI / Entry Points                                │
│  dm diffraction run-analysis   (existing)                          │
│  dm diffraction sensitivity    (NEW)                               │
│  dm diffraction batch-report   (NEW)                               │
│  dm diffraction generate-spec  (NEW — deterministic YAML from UI)  │
├─────────────────────────────────────────────────────────────────────┤
│                    Orchestration Layer                               │
│                                                                     │
│  ┌──────────────┐  ┌─────────────────┐  ┌───────────────────┐      │
│  │ OrcaWave     │  │ Sensitivity     │  │ BatchReport       │      │
│  │ BatchRunner  │  │ Runner          │  │ Orchestrator      │      │
│  │ (MODIFY)     │  │ (NEW)           │  │ (NEW)             │      │
│  └──────┬───────┘  └───────┬─────────┘  └────────┬──────────┘      │
│         │                  │                      │                 │
├─────────┴──────────────────┴──────────────────────┴─────────────────┤
│                    Spec Generation Layer                             │
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────────────┐                 │
│  │ SpecConverter     │  │ SensitivitySpecFactory   │                │
│  │ (existing)        │  │ (NEW — creates variant   │                │
│  │                   │  │  DiffractionSpecs from   │                │
│  │                   │  │  base + parameter sweep) │                │
│  └──────────────────┘  └──────────────────────────┘                 │
│                                                                     │
│  ┌──────────────────────────────────────────────┐                   │
│  │ SpecBuilder (NEW — programmatic spec         │                   │
│  │ construction from analysis type + hull       │                   │
│  │ library + environment, replacing manual YAML │                   │
│  │ authoring for standard analysis types)       │                   │
│  └──────────────────────────────────────────────┘                   │
├──���───────────────────────────────��──────────────────────────────────┤
│                    Solver Execution (no changes)                     │
│  OrcaWaveRunner  |  RunConfig  |  (licensed-win-1 required)        │
├───────────────────────────────���─────────────────────────────────────┤
│                    Result Extraction (no changes)                    │
│  ResultExtractor  |  OutputValidator  |  DiffractionResults        │
├���────────────────────────────────────────────────────────────────────┤
│                    Analysis Layer                                    │
│                                                                     │
│  ┌─────────────────────┐  ┌──────────────────────────────┐         │
│  │ ComparisonFramework  │  │ DiffractionSensitivity       │        │
│  │ (existing)           │  │ Analyzer (NEW — operates on  │        │
│  │                      │  │ DiffractionResults[], ranks  │        │
│  │                      │  │ parameter influence on RAOs) │        │
│  └─────────────────────┘  └──────────────────────────────┘         │
├────────��────────────────────────────────────────────────────────────┤
│                    Report Generation Layer                           │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │ CalcReportBuilder (MODIFY — enhanced template system)     │      │
│  │  - ReportTemplate enum (DIFFRACTION, SENSITIVITY, BATCH)  │      │
│  │  - section registry (extends existing section modules)     │      │
│  │  - client branding / metadata injection                    │      │
│  │  - operates on DiffractionReportData (existing)            │      │
│  │  - new: SensitivityReportData, BatchReportData            │      │
│  └───────────────────────────────────────────────────────────┘      │
│                                                                     │
│  ┌────────────────────────┐  ┌─────────────────────────┐           │
│  │ Sensitivity Sections   │  │ Batch Summary Sections  │           │
│  │ (NEW section modules)  │  │ (NEW section modules)   │           │
│  │  - tornado_chart.py    │  │  - cross_vessel_table.py│           │
│  │  - parameter_matrix.py │  │  - fleet_summary.py     │           │
│  │  - response_surface.py │  │  - comparison_matrix.py │           │
│  └────────────────────────┘  └���────────────────────────┘           │
├────��────────────────────────────────────────────────────────���───────┤
│                    Export Layer (extend, not replace)                │
│  OrcaFlexExporter (existing) | PolarsExporter (existing)           │
│  BatchExporter (NEW — consolidated multi-vessel package)           │
└��─────────────────────────────────���─────────────────────────────��────┘
```

### New Components Required

| Component | Location | Responsibility | Depends On |
|-----------|----------|----------------|------------|
| `SpecBuilder` | `diffraction/spec_builder.py` | Deterministic DiffractionSpec construction from analysis-type + hull-library + environment parameters. Eliminates manual YAML authoring for standard analyses. | `input_schemas.DiffractionSpec`, `hull_library/` |
| `SensitivitySpecFactory` | `diffraction/sensitivity_spec_factory.py` | Given a base DiffractionSpec and parameter ranges, produces a list of variant specs for sweep execution. | `input_schemas.DiffractionSpec` |
| `SensitivityRunner` | `diffraction/sensitivity_runner.py` | Orchestrates sweep: factory -> batch run -> collect results -> analyze. | `SensitivitySpecFactory`, `OrcaWaveBatchRunner`, `DiffractionSensitivityAnalyzer` |
| `DiffractionSensitivityAnalyzer` | `diffraction/sensitivity_analyzer.py` | Statistical analysis of parameter influence on RAOs/coefficients across multiple DiffractionResults. Adapts patterns from `SensitivityAnalysisService`. | `output_schemas.DiffractionResults`, `comparison_framework` |
| `SensitivityReportData` | `diffraction/report_data_models.py` (extend) | Pydantic model for sensitivity report rendering. | `DiffractionSensitivityAnalyzer` output |
| `BatchReportOrchestrator` | `diffraction/batch_report_orchestrator.py` | Orchestrates multi-vessel report generation: runs batch -> generates per-vessel reports + fleet summary. | `OrcaWaveBatchRunner`, `CalcReportBuilder` |
| `BatchReportData` | `diffraction/report_data_models.py` (extend) | Pydantic model for fleet/batch summary rendering. | Per-vessel `DiffractionReportData` |
| Sensitivity section modules | `orcawave/reporting/sections/sensitivity_*.py` | HTML section builders for tornado charts, parameter matrices, response surfaces. | `SensitivityReportData` |
| Batch section modules | `orcawave/reporting/sections/batch_*.py` | HTML section builders for cross-vessel comparison tables and fleet summaries. | `BatchReportData` |
| `BatchExporter` | `diffraction/batch_exporter.py` | Packages multi-vessel results into a single deliverable (ZIP with per-vessel dirs + fleet summary). | `OrcaFlexExporter`, `BatchReportData` |

### Components to Modify (Not Replace)

| Component | Modification | Rationale |
|-----------|-------------|-----------|
| `report_generator.py` | Add `mode='sensitivity'` and `mode='batch'` alongside existing `mode='full'`/`mode='compact'` | Reuse existing HTML template infrastructure |
| `OrcaWaveBatchRunner` | Add callback hooks for per-job completion (needed by sensitivity runner to collect results incrementally) | Currently runs to completion; sensitivity needs intermediate results |
| `ReportConfig` (orcawave) | Add `SensitivitySectionConfig` and `BatchSectionConfig` to section registry | Preserves the per-section enable/disable pattern |
| `OrcaWaveReportBuilder` | Register new section modules in `_build_section` call list | Standard extensibility via the existing pattern |
| `cli.py` | Add `sensitivity`, `batch-report`, and `generate-spec` subcommands | Natural extension of existing Click group |

## Data Flow: Analysis Type Selection Through to Client-Ready Report

### Flow 1: Standard Diffraction Analysis (existing, for reference)

```
User selects analysis type + vessel
    |
    v
spec.yml (DiffractionSpec) --- manual authoring or hull_library lookup
    |
    v
SpecConverter.convert(solver="orcawave")
    |
    v
OrcaWaveBackend.generate_single() -> orcawave_input.yml
    |
    v
OrcaWaveRunner.prepare() + .execute()  [on licensed-win-1]
    |
    v
ResultExtractor.extract(run_result) -> DiffractionResults
    |
    v
OutputValidator.run_all_validations()
    |
    v
extract_report_data_from_owr() -> DiffractionReportData
    |
    v
generate_diffraction_report(data, output.html)
    |
    v
client-ready HTML report
```

### Flow 2: Deterministic Spec Generation (NEW)

Replaces manual YAML authoring for standard analysis types.

```
User specifies:
  - analysis_type: "standard_diffraction" | "qtf" | "multi_body"
  - hull_name: "FPSO_A" (from hull_library catalog)
  - environment: {water_depth: 1200, density: 1025}
  - options: {frequencies: "standard_50", headings: "full_360"}
    |
    v
SpecBuilder.from_analysis_type(
    analysis_type="standard_diffraction",
    hull_name="FPSO_A",
    environment=EnvironmentSpec(water_depth=1200),
    frequency_preset="standard_50",  # predefined frequency sets
    heading_preset="full_360",       # predefined heading sets
)
    |
    v
DiffractionSpec (fully populated, deterministic, repeatable)
    |
    v
spec.to_yaml("analysis/FPSO_A/spec.yml")  # saved for audit trail
    |
    v
[continues to Flow 1 from SpecConverter.convert() step]
```

**Key design decision:** `SpecBuilder` does NOT bypass `DiffractionSpec`. It produces a validated `DiffractionSpec` object, which then flows through the same pipeline. This means all downstream code (converter, runner, extractor, validator) works unchanged.

### Flow 3: Sensitivity Analysis (NEW)

```
User specifies:
  - base_spec: DiffractionSpec (from Flow 2 or manual)
  - sweep_parameters:
      - parameter: "environment.water_depth"
        values: [100, 500, 1000, 1500, "infinite"]
      - parameter: "vessel.inertia.mass"
        values: [50000, 55000, 60000]  # tonnes
      - parameter: "frequencies.range.count"
        values: [25, 50, 100]
  - sweep_mode: "one_at_a_time" | "full_factorial" | "latin_hypercube"
    |
    v
SensitivitySpecFactory.create_variants(base_spec, sweep_params, mode)
    |
    v
List[DiffractionSpec]  (N variants, each with one or more parameters changed)
    |    each spec tagged with: variant_id, changed_params, base_spec_hash
    |
    v
SensitivityRunner.run(variants, execution_config)
    |    internally delegates to OrcaWaveBatchRunner
    |    collects: Dict[variant_id, DiffractionResults]
    |
    v
DiffractionSensitivityAnalyzer.analyze(
    base_results, variant_results, sweep_params
)
    |    computes:
    |    - per-parameter influence on each DOF RAO peak
    |    - per-parameter influence on natural period estimates
    |    - parameter ranking (tornado chart data)
    |    - response surfaces (2-parameter interaction)
    |
    v
SensitivityReportData (Pydantic model)
    |
    v
generate_diffraction_report(data, mode="sensitivity")
    |    renders standard sections (from base case)
    |    PLUS sensitivity-specific sections:
    |    - tornado chart (parameter importance)
    |    - parameter sweep plots (RAO vs parameter)
    |    - response surface contours (if 2+ parameters)
    |    - tabulated results matrix
    |
    v
client-ready sensitivity report HTML
```

### Flow 4: Batch Reporting / Fleet Processing (NEW)

```
User specifies:
  - vessels: ["FPSO_A", "Barge_B", "Spar_C"]
  - per-vessel config overrides (optional)
  - report_template: "client_deliverable" | "internal_review" | "benchmark"
    |
    v
BatchReportOrchestrator.run(vessel_configs, template)
    |
    |  For each vessel:
    |    SpecBuilder -> DiffractionSpec
    |    SpecConverter -> OrcaWave input
    |    OrcaWaveRunner -> execute
    |    ResultExtractor -> DiffractionResults
    |    extract_report_data_from_owr -> DiffractionReportData
    |    generate_diffraction_report -> per_vessel_report.html
    |
    |  After all vessels:
    |    BatchReportData.from_vessel_reports(all_report_data)
    |    generate_batch_summary -> fleet_summary.html
    |
    v
BatchExporter.package(
    per_vessel_reports,
    fleet_summary,
    orcaflex_exports,
    metadata
)
    |
    v
deliverable_package/
  ├── fleet_summary.html
  ├── FPSO_A/
  │   ├── FPSO_A_diffraction_report.html
  │   ├── FPSO_A_vessel_type.yml
  │   └── FPSO_A_hydrodynamics.xlsx
  ├── Barge_B/
  │   ├── ...
  ├── Spar_C/
  │   ├── ...
  └── README.md
```

### Flow 5: OrcaFlex Integration Enhancement (MODIFY existing)

The existing OrcaFlex integration path is:

```
DiffractionResults -> OrcaFlexExporter -> vessel_type.yml + CSV + Excel
```

The enhancement adds automated validation and model integration:

```
DiffractionResults
    |
    v
OrcaFlexExporter.export_all()  (existing — no change)
    |
    v
vessel_type.yml + CSV + XLSX
    |
    v
OrcaFlexModelIntegrator (NEW — optional, requires OrcFxAPI)
    |    - Loads an OrcaFlex .dat template model
    |    - Imports vessel_type.yml as vessel type
    |    - Validates import (RAO count, frequency range, heading coverage)
    |    - Optionally attaches mooring/riser configuration
    |    - Saves .dat model ready for simulation
    |
    v
integrated_model.dat  [ready for OrcaFlex simulation on licensed-win-1]
    |
    v
OrcaFlexReportBuilder  (existing — generates HTML from .sim results)
```

**Execution constraint:** Both OrcaWave execution and OrcaFlex model integration require `licensed-win-1`. The spec generation, validation, report template preparation, and analysis steps run on any machine. The architecture must cleanly separate "needs license" from "license-free" operations.

## Architectural Patterns

### Pattern 1: Pydantic Config as Contract Between Layers

**What:** Every inter-layer data transfer uses a Pydantic v2 model. No raw dicts crossing component boundaries.

**When to use:** All new components. Already established by `DiffractionSpec`, `ReportConfig`, `DiffractionReportData`.

**Trade-offs:** Slightly more boilerplate than raw dicts, but catches schema drift at validation time rather than runtime KeyError. The existing codebase already pays this cost consistently.

**Example:**
```python
class SensitivityConfig(BaseModel):
    """Configuration for a sensitivity analysis run."""
    base_spec_path: Path
    sweep_parameters: list[SweepParameter]
    sweep_mode: SweepMode = SweepMode.ONE_AT_A_TIME
    output_dir: Path = Path("sensitivity_output")
    generate_report: bool = True
    report_template: str = "sensitivity"

class SweepParameter(BaseModel):
    """Single parameter to sweep."""
    json_path: str  # dot-notation path into DiffractionSpec
    values: list[float | str]
    label: str | None = None  # human-readable label for reports
```

### Pattern 2: Section Registry for Reports

**What:** Report sections are independent modules that register via a config toggle. The builder iterates the registry, calling `build_*(data, config)` for each enabled section.

**When to use:** All new report sections (sensitivity, batch). Already established by both `OrcaWaveReportBuilder` and `OrcaFlexReportBuilder`.

**Trade-offs:** Adding a section requires touching (1) a section module, (2) the config model, and (3) the builder's section list. But each section is independently testable and toggleable.

**Example:**
```python
# In orcawave/reporting/sections/tornado_chart.py
def build_tornado_chart(
    sensitivity_data: SensitivityReportData,
    config: TornadoChartConfig,
    include_plotlyjs: str = "cdn",
) -> str:
    """Build HTML for parameter sensitivity tornado chart."""
    # ... returns HTML string
```

### Pattern 3: Factory for Spec Variants

**What:** A factory class that takes a base spec and a set of parameter overrides, producing N validated variant specs. Each variant carries metadata about what was changed.

**When to use:** Sensitivity analysis (parameter sweeps) and batch processing (per-vessel overrides).

**Trade-offs:** Requires deep-copy of Pydantic models and careful path-based mutation. Pydantic v2's `model_copy(update=...)` handles this cleanly.

**Example:**
```python
class SensitivitySpecFactory:
    @staticmethod
    def create_variants(
        base: DiffractionSpec,
        parameters: list[SweepParameter],
        mode: SweepMode,
    ) -> list[VariantSpec]:
        variants = []
        if mode == SweepMode.ONE_AT_A_TIME:
            for param in parameters:
                for value in param.values:
                    variant = base.model_copy(deep=True)
                    _set_nested(variant, param.json_path, value)
                    variants.append(VariantSpec(
                        spec=variant,
                        variant_id=f"{param.json_path}={value}",
                        changed={param.json_path: value},
                    ))
        return variants
```

### Pattern 4: License-Aware Execution Boundary

**What:** Components are explicitly tagged as license-free or license-required. Orchestrators check `RunConfig.dry_run` or detect license availability before crossing the boundary.

**When to use:** All new orchestrators. The existing `OrcaWaveRunner` already implements this with executable detection and dry-run fallback.

**Trade-offs:** Adds conditional logic, but without it, CI and development environments would fail on every test. The boundary is already well-established.

**Boundary map:**
```
LICENSE-FREE (any machine):              LICENSE-REQUIRED (licensed-win-1):
  SpecBuilder                              OrcaWaveRunner.execute()
  SensitivitySpecFactory                   OrcaWaveReportBuilder._load_diffraction()
  SpecConverter                            OrcaFlexReportBuilder._load_simulation()
  SensitivityAnalyzer                      OrcaFlexModelIntegrator
  All report builders (given data)
  All exporters (given DiffractionResults)
  BatchReportOrchestrator (orchestration)
  OutputValidator (given results)
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Bypass DiffractionSpec for "Simple" Cases

**What people do:** Directly construct OrcaWave YAML dicts in new code, skipping DiffractionSpec validation.
**Why it's wrong:** Loses validation, breaks traceability (spec.yml audit trail), and creates a second path through the pipeline that every downstream component must handle.
**Do this instead:** Always construct a `DiffractionSpec` first, even for programmatic/automated cases. The `SpecBuilder` exists precisely to make this easy.

### Anti-Pattern 2: God Orchestrator

**What people do:** Put sensitivity loop, result collection, analysis, and report generation in a single class.
**Why it's wrong:** The existing codebase already suffered this (`report_generator.py` was split in WRK-591). Monolithic orchestrators are untestable and unmaintainable.
**Do this instead:** Separate concerns: `SensitivitySpecFactory` (variant creation), `SensitivityRunner` (orchestration), `DiffractionSensitivityAnalyzer` (analysis), report sections (rendering). Each is independently testable.

### Anti-Pattern 3: Duplicate Report Infrastructure

**What people do:** Create a new report builder class for sensitivity reports instead of extending the existing one.
**Why it's wrong:** Both `OrcaWaveReportBuilder` and the `generate_diffraction_report` function already handle section-based HTML generation. A third parallel implementation means three places to update CSS, three places to fix Plotly version issues, etc.
**Do this instead:** Add new section modules and register them in the existing builders. Use `mode='sensitivity'` to control which sections render.

### Anti-Pattern 4: Sensitivity Analysis Recomputes Everything

**What people do:** Re-extract all data from .owr files for each sensitivity variant, even when only water depth changed.
**Why it's wrong:** OrcaWave result extraction via OrcFxAPI is slow. For a 15-variant sensitivity sweep, this wastes significant time.
**Do this instead:** Extract once per variant, cache `DiffractionResults` per variant_id, and pass the cached results to the analyzer.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| OrcaWave solver | Subprocess via `OrcaWaveRunner` | Windows-only, license-locked to licensed-win-1. Batch script invocation with YAML input. |
| OrcFxAPI Python | Direct import in extraction/report code | `try: import OrcFxAPI` pattern throughout. Not available in CI. |
| Hull Library | File-based lookup in `hull_library/catalog.py` | GDF/DAT mesh files + profile_schema metadata. SpecBuilder reads this. |
| Plotly | CDN link in HTML reports (default) or inline JS | 259 existing benchmark plots use Plotly. New sensitivity/batch plots continue this. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Spec layer <-> Solver layer | `DiffractionSpec` Pydantic model | Clean contract. No changes needed. |
| Solver layer <-> Result layer | `RunResult` dataclass + file paths | Runner produces files; extractor reads them. |
| Result layer <-> Analysis layer | `DiffractionResults` dataclass | Unified schema. Sensitivity adds `List[DiffractionResults]`. |
| Analysis layer <-> Report layer | `DiffractionReportData` / `SensitivityReportData` / `BatchReportData` | Pydantic models. Report layer never touches raw solver output. |
| Report layer <-> Export layer | HTML files + OrcaFlex YAML/CSV/Excel | File-based handoff into deliverable package. |

## Recommended Project Structure (New/Modified Files Only)

```
src/digitalmodel/
├── hydrodynamics/diffraction/
│   ├── spec_builder.py           # NEW: Deterministic spec construction
│   ├── sensitivity_spec_factory.py  # NEW: Variant spec generation
│   ├── sensitivity_runner.py     # NEW: Sweep orchestration
│   ├── sensitivity_analyzer.py   # NEW: Statistical analysis of sweep results
│   ├── batch_report_orchestrator.py # NEW: Multi-vessel report orchestration
│   ├── batch_exporter.py         # NEW: Deliverable package creation
│   ├── report_data_models.py     # MODIFY: Add SensitivityReportData, BatchReportData
│   ├── report_generator.py       # MODIFY: Add mode='sensitivity', mode='batch'
│   ├── orcawave_batch_runner.py  # MODIFY: Add completion callbacks
│   ├── cli.py                    # MODIFY: Add sensitivity, batch-report, generate-spec
│   └── ...                       # Existing files unchanged
├── orcawave/reporting/
│   ├── config.py                 # MODIFY: Add sensitivity/batch section configs
│   ├── builder.py                # MODIFY: Register new sections
��   ├── sections/
│   │   ├── tornado_chart.py      # NEW: Parameter importance tornado
│   │   ├── parameter_matrix.py   # NEW: Sweep results matrix
│   │   ├── response_surface.py   # NEW: 2D parameter interaction contours
│   │   ├── batch_summary.py      # NEW: Cross-vessel comparison table
��   │   └── ...                   # Existing sections unchanged
│   └── templates/
│       ├── client_deliverable.yml  # NEW: Report template preset
│       ├── internal_review.yml     # NEW: Report template preset
│       └── sensitivity.yml         # NEW: Report template preset
└── orcaflex/
    ├── model_integrator.py       # NEW: Automated vessel type import into .dat model
    └── ...                       # Existing files unchanged
```

### Structure Rationale

- **All new diffraction files stay in `hydrodynamics/diffraction/`:** This is the established home for the pipeline. Moving to a new location would fragment the data flow.
- **New report sections go in `orcawave/reporting/sections/`:** Follows the existing section-module pattern. Sensitivity and batch sections are OrcaWave-report-specific (they render hydrodynamic data).
- **Report templates go in `orcawave/reporting/templates/`:** YAML presets that configure which sections are enabled for each report type. Avoids hardcoding section lists in code.
- **`model_integrator.py` goes in `orcaflex/`:** It operates on OrcaFlex models, not OrcaWave results. Correct conceptual home.

## Build Order (Dependency-Driven)

The dependency graph determines build order. Components at the bottom of the stack must exist before components above them.

```
Phase 1: Foundation (no new runtime dependencies)
  SpecBuilder -> DiffractionSpec (uses existing schemas)
  Report template presets (YAML config files)
  CalcReport enhancements (section toggle, metadata injection)

Phase 2: Sensitivity Infrastructure
  SensitivitySpecFactory (depends on: DiffractionSpec, SpecBuilder)
  DiffractionSensitivityAnalyzer (depends on: DiffractionResults)
  SensitivityReportData (depends on: report_data_models)
  Sensitivity report sections (depends on: SensitivityReportData)

Phase 3: Orchestration
  SensitivityRunner (depends on: SensitivitySpecFactory, OrcaWaveBatchRunner,
                     DiffractionSensitivityAnalyzer)
  BatchReportOrchestrator (depends on: OrcaWaveBatchRunner, CalcReportBuilder)
  BatchReportData + batch sections (depends on: DiffractionReportData)

Phase 4: Integration & Packaging
  OrcaFlexModelIntegrator (depends on: OrcaFlexExporter, OrcFxAPI)
  BatchExporter (depends on: BatchReportOrchestrator output)
  CLI extensions (depends on: all orchestrators)

Phase 5: Polish
  Report template refinement based on client feedback
  End-to-end integration tests (dry-run mode for CI)
```

**Phase ordering rationale:**
- Phase 1 is license-free and testable on any machine. It delivers immediate value (deterministic spec generation eliminates manual YAML errors).
- Phase 2 builds the analysis engine without requiring solver execution (analyzer works on pre-existing DiffractionResults from benchmarks).
- Phase 3 wires everything together but requires solver access for end-to-end testing.
- Phase 4 is the OrcaFlex-specific integration that only runs on licensed-win-1.
- Phase 5 is iterative refinement after real usage.

## Scaling Considerations

| Concern | 1-3 vessels | 10-20 vessels | 50+ vessels |
|---------|-------------|---------------|-------------|
| Spec generation | Sequential, instant | Sequential, instant | Sequential, instant |
| Solver execution | Sequential, 5-30 min each | Parallel (2-4 workers), 20-60 min total | Batch queue, hours. Consider job scheduler. |
| Result extraction | Sequential, seconds each | Sequential, minutes total | Parallel extraction, cache aggressively |
| Report generation | Sequential, seconds each | Sequential, minutes total | Parallel report gen, shared Plotly CDN |
| Deliverable packaging | Single ZIP, trivial | Single ZIP, manageable | Chunked packaging, index HTML |

**First bottleneck:** OrcaWave solver execution time. Each analysis takes 5-30 minutes depending on mesh density and frequency count. For sensitivity sweeps with 15+ variants, this is 1-8 hours. Mitigation: `OrcaWaveBatchRunner` already supports parallel execution with configurable `max_workers`.

**Second bottleneck:** OrcFxAPI result extraction for large .owr files. Mitigation: Extract once, cache `DiffractionResults` as JSON/pickle per variant.

## Sources

- Direct codebase inspection of `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/` (30+ files)
- Direct codebase inspection of `digitalmodel/src/digitalmodel/orcawave/reporting/` (10 files)
- Direct codebase inspection of `digitalmodel/src/digitalmodel/orcaflex/reporting/` (10 files)
- Direct codebase inspection of `digitalmodel/src/digitalmodel/solvers/orcawave/` (orchestrator)
- Direct codebase inspection of `digitalmodel/src/digitalmodel/visualization/orcaflex_dashboard/backend/app/services/sensitivity_analysis.py`
- Direct codebase inspection of `digitalmodel/src/digitalmodel/structural/fatigue/parametric_sweep.py`
- Existing spec examples: `docs/domains/orcawave/L00_validation_wamit/2.1/spec.yml`
- Existing report config: `docs/domains/orcawave/examples/report_config_template.yml`

---
*Architecture research for: OrcaWave automation features (report templates, deterministic YAML, sensitivity analysis, batch reporting, OrcaFlex integration)*
*Researched: 2026-03-29*
