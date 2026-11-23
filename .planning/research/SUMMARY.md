# Project Research Summary

**Project:** OrcaWave Automation -- Calculation Reports, YAML Generation, Sensitivity Analysis, Batch Processing
**Domain:** Offshore hydrodynamic diffraction analysis automation
**Researched:** 2026-03-29
**Confidence:** HIGH

## Executive Summary

This project automates the hydrodynamic diffraction analysis workflow built on OrcaWave/OrcFxAPI, delivering three capabilities: deterministic YAML generation for OrcaWave input files, automated HTML calculation reports conforming to classification society expectations (DNV/BV/LR), and parametric sensitivity analysis with batch processing across vessel fleets. The existing codebase is mature -- a solver-agnostic `DiffractionSpec` Pydantic schema (655 lines, 20 sub-models, 9 enums, 166 tests), an OrcaWave backend converter, batch runner, benchmark plotter (259 Plotly plots), and warm-parchment HTML design system are all in place. The new work extends this foundation rather than building from scratch.

The recommended approach is conservative: only one new explicit dependency (Jinja2 for report templates, already a transitive dep), no new analysis frameworks (SALib rejected in favor of existing `itertools.product` + pandas pattern), and deterministic template-based YAML generation rather than LLM-based generation. Architecture follows established codebase patterns -- Pydantic config as contract, section-based report builders, factory pattern for spec variants, and license-aware execution boundaries that separate Linux-testable logic from Windows-licensed solver execution. The build order is strictly dependency-driven: foundation (spec generation, report data model), then analysis infrastructure (sensitivity analyzer, report sections), then orchestration (batch runner integration), then packaging (OrcaFlex integration, deliverable export).

The primary risks are operational, not technical. The single highest-risk item is solver verification on the target machine (`licensed-win-1`) -- the WRK-031 benchmark stalled for exactly this reason, with a complete framework built on Linux that could not execute on Windows. A Phase 0 smoke test is non-negotiable. Secondary risks include OrcFxAPI frequency unit conventions (Hz descending vs rad/s ascending -- a documented source of silent data corruption), QTF parameter dependency ordering (causes runtime "Change not allowed" errors), and batch report generation without per-case correctness gates (200 reports that "look done" but contain subtle errors).

## Key Findings

### Recommended Stack

The stack is deliberately minimal. The existing codebase already contains every major dependency needed. The only new explicit addition is Jinja2 (already resolved as a transitive dependency in `uv.lock`). All other capabilities are delivered through new usage of existing libraries and stdlib patterns.

**Core technologies (new usage of existing):**
- **Jinja2 3.1.6**: Report template engine with inheritance -- replaces f-string HTML concatenation for narrative flow, conditional sections, and analysis-type-specific report structures
- **ruamel.yaml 0.19.1**: Round-trip YAML editing for parametric updates to existing example files while preserving comments and formatting
- **Pydantic v2 `model_copy(update=...)`**: Parametric spec variant generation -- deep copy with field overrides for sensitivity sweeps
- **`itertools.product` + pandas**: Sensitivity parameter sweeps using the established pattern from `structural/fatigue/parametric_sweep.py`
- **`concurrent.futures.ProcessPoolExecutor`**: Parallel batch report generation (CPU-bound HTML rendering), extending the existing `ThreadPoolExecutor` pattern used for solver execution
- **deepdiff 8.0+**: Report regression testing with float-tolerance-aware structural comparison of extracted data

**Explicitly rejected:**
- SALib (overkill for 3-5 parameter engineering sweeps)
- WeasyPrint/wkhtmltopdf (OS-level dependencies for PDF; HTML is the deliverable)
- Celery/Redis (architectural overkill for 6-20 batch jobs)
- Dash (live dashboards, not static calculation reports)

### Expected Features

**Must have (table stakes -- classification societies expect these in any diffraction analysis report):**
- Design basis section with full input traceability (vessel, environment, mesh, standards)
- Hydrostatic results table (displacement, waterplane area, metacentric heights)
- RAO plots for all 6 DOFs at multiple headings
- Added mass and damping coefficient plots (6x6 matrix diagonal + coupling terms)
- Mesh QA summary with pass/fail gates
- Executive summary with key findings and identified resonances
- OrcaFlex vessel type export confirmation
- Haskind/Diffraction method comparison as internal QA
- Mean drift load results for mooring design downstream
- Standards traceability (DNV-RP-C205, DNV-RP-H103 clause references)

**Should have (differentiators):**
- Narrative report structure with engineering interpretation (not just data dump)
- Automatic natural period identification via peak detection
- Water depth and roll damping sensitivity analysis
- Tornado/spider diagrams for parameter sensitivity ranking
- Batch comparison dashboard across all examples (L00-L06)
- Interactive Plotly charts (zoomable, hoverable)
- Automated OrcaFlex vessel type database as companion deliverable

**Defer (v2+):**
- Full QTF convergence study automation (expensive, niche requirement)
- Multi-body interaction reports (additional data model complexity)
- PDF report generation (only when a client explicitly cannot accept HTML)
- Cross-solver comparison integration (requires multiple license availability)
- Multi-draught database workflow (requires new meshes per draught)

### Architecture Approach

The architecture slots new capabilities into the existing 7-layer stack: CLI -> Orchestration -> Spec Generation -> Solver Execution -> Result Extraction -> Analysis -> Report Generation -> Export. New components follow established patterns (Pydantic config as contract, section-based report builders, factory pattern for variants, license-aware execution boundaries). The critical design decision is that all new paths flow through `DiffractionSpec` -- the `SpecBuilder` produces validated specs, the `SensitivitySpecFactory` creates variant specs, and all downstream code (converter, runner, extractor, validator, reporter) works unchanged.

**Major new components:**
1. **SpecBuilder** (`spec_builder.py`) -- Deterministic spec construction from analysis type + hull library + environment, eliminating manual YAML authoring
2. **SensitivitySpecFactory** (`sensitivity_spec_factory.py`) -- Creates variant `DiffractionSpec` instances from base spec + parameter ranges for sweep execution
3. **SensitivityRunner** (`sensitivity_runner.py`) -- Orchestrates sweep: factory -> batch run -> collect results -> analyze
4. **DiffractionSensitivityAnalyzer** (`sensitivity_analyzer.py`) -- Statistical analysis of parameter influence on RAOs/coefficients
5. **BatchReportOrchestrator** (`batch_report_orchestrator.py`) -- Multi-vessel report generation with fleet summary
6. **ReportContext layer** -- Decouples Jinja2 templates from data model to prevent template breakage on schema evolution
7. **Sensitivity/Batch report sections** -- New section modules registered in existing `OrcaWaveReportBuilder`

### Critical Pitfalls

1. **Solver not verified on target machine** -- The WRK-031 benchmark stalled because the framework was built on Linux while the solver runs on Windows (`licensed-win-1`). Phase 0 smoke test (`python -c "import OrcFxAPI; d = OrcFxAPI.Diffraction(); ..."`) is mandatory before any development begins.

2. **Frequency unit convention mismatch** -- OrcFxAPI returns Hz descending; the pipeline expects rad/s ascending. A single `normalize_frequencies()` function at the OrcFxAPI boundary, plus monotonicity assertions in every consumer, prevents silent data corruption that manifests as mirrored RAO plots and failed benchmarks.

3. **Non-deterministic LLM YAML generation** -- Prior approach used LLMs for OrcaWave YAML, producing non-deterministic output with semantic drift. Replace entirely with deterministic `DiffractionSpec -> OrcaWaveBackend` pipeline. No LLM in the YAML generation path.

4. **Batch reports without correctness gates** -- 200+ reports that render without errors but contain subtle data mismatches. Per-case assertion suite (frequency monotonicity, heave RAO ~1.0 at low frequency, symmetric added mass matrix, metadata matching source model) before batch scaling.

5. **QTF parameter ordering** -- OrcaWave API enforces parameter dependencies at runtime. `SolveType` must be set before QTF-specific parameters; guard all QTF writes behind solve-type checks using the existing `_DORMANT_QTF_KEYS` set.

6. **Cross-platform path and DLL failures** -- Development on Linux, execution on Windows. Use `pathlib.Path` exclusively, relative paths in configs, conditional `import OrcFxAPI` pattern, and test `uv sync` on the target machine.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 0: Solver Verification Gate
**Rationale:** The single highest-risk item. WRK-031 stalled at this exact point. Every other phase depends on OrcFxAPI being functional on `licensed-win-1`. This is a go/no-go gate, not a development phase.
**Delivers:** Confirmed OrcFxAPI smoke test (load .owd, calculate, extract one result) on licensed-win-1. Confirmed `uv sync` and Python environment on Windows.
**Addresses:** Pitfall 4 (solver not verified), Pitfall 6 (cross-platform failures)
**Avoids:** Building an entire framework that cannot execute on the target machine
**Estimated effort:** 1-2 hours if everything works; potentially days if license/install issues arise

### Phase 1: Report Data Model and Template Foundation
**Rationale:** The report data model (`DiffractionReportData` extensions + `ReportContext` layer) is the contract that all report sections depend on. Must be stable before building sections. Also includes `SpecBuilder` for deterministic spec generation (foundational for sensitivity and batch).
**Delivers:** `SpecBuilder`, `ReportContext` decoupling layer, Jinja2 template infrastructure with warm-parchment base, frequency normalization at OrcFxAPI boundary, QTF parameter dependency guard
**Addresses:** Report data model (P1), executive summary (P1), standards traceability (P1), mesh QA summary (P1), hydrostatic results (P1)
**Avoids:** Pitfall 1 (non-deterministic YAML), Pitfall 2 (frequency units), Pitfall 3 (QTF errors), Pitfall 8 (template coupling)
**Uses:** Jinja2, Pydantic v2, existing warm-parchment CSS

### Phase 2: Single-Vessel Calculation Report
**Rationale:** The core deliverable. Once the data model is stable, build the full report template with all section modules. This is where classification society expectations are met.
**Delivers:** Complete single-vessel HTML calculation report covering all 13 required sections (design basis through conclusions). RAO plots (6 DOF), added mass/damping, mean drift, Haskind/Diffraction comparison, OrcaFlex export confirmation.
**Addresses:** All P1 report features (RAO plots, added mass/damping, load RAO QA, mean drift, executive summary, tabular appendix)
**Avoids:** Pitfall 5 (batch without correctness -- establish per-case gates here first)
**Uses:** Jinja2 templates, Plotly, existing benchmark plotter patterns

### Phase 3: Sensitivity Analysis Framework
**Rationale:** Depends on Phase 1 (SpecBuilder, data model) and Phase 2 (report sections for base case). Sensitivity analysis creates variant specs, runs them, and produces comparative reports. The analysis engine itself is license-free and testable against cached benchmark results.
**Delivers:** `SensitivitySpecFactory`, `DiffractionSensitivityAnalyzer`, `SensitivityRunner`, tornado chart section, parameter sweep plots, water depth + roll damping sensitivity
**Addresses:** Water depth sensitivity (P1), roll damping sensitivity (P1), heading resolution sensitivity (P2), mesh convergence study (P2), tornado diagrams (P3)
**Avoids:** Pitfall 7 (parameter space explosion -- OAT-first strategy, time estimator before execution)
**Uses:** `itertools.product`, pandas, Pydantic `model_copy`, existing parametric sweep pattern

### Phase 4: Batch Processing and Fleet Reporting
**Rationale:** Depends on Phase 2 (single-vessel report works) and Phase 3 (batch runner modifications). Extends from single vessel to fleet-wide processing with cross-vessel comparison and deliverable packaging.
**Delivers:** `BatchReportOrchestrator`, fleet summary dashboard, cross-vessel comparison table, `BatchExporter` (ZIP deliverable), L00-L06 report generation
**Addresses:** Batch execution (P1), automated report generation (P2), batch comparison (P2), standardized output directories
**Avoids:** Pitfall 5 (batch without correctness -- per-case assertion suite required before scaling)
**Uses:** `ProcessPoolExecutor`, existing `OrcaWaveBatchRunner` with completion callbacks

### Phase 5: OrcaFlex Integration and Polish
**Rationale:** OrcaFlex model integration is downstream of the diffraction pipeline and requires the licensed machine. Polish phase refines templates based on actual usage.
**Delivers:** `OrcaFlexModelIntegrator`, automated vessel type import validation, narrative report blocks (triggered by client feedback), natural period auto-detection, report template refinement
**Addresses:** OrcaFlex database delivery (P1), narrative blocks (P2), natural period detection (P2), interactive reports (P2)
**Avoids:** Building polish features before core pipeline is proven

### Phase Ordering Rationale

- **Phase 0 before everything** because the WRK-031 precedent proves that building frameworks without solver verification wastes effort. Go/no-go gate.
- **Phase 1 before Phase 2** because report sections depend on data model stability and the `ReportContext` decoupling layer prevents the template-coupling pitfall observed in WRK-129 (14 review iterations).
- **Phase 2 before Phase 3** because sensitivity reports extend single-vessel reports with additional sections. Base case must be correct before computing deltas.
- **Phase 3 before Phase 4** because batch processing at scale requires the per-case correctness gates developed alongside sensitivity analysis.
- **Phase 4 before Phase 5** because OrcaFlex integration and polish are downstream consumers of the core pipeline.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 0:** Needs hands-on investigation -- license availability, DLL compatibility, `uv sync` on Windows. Cannot be researched theoretically.
- **Phase 3:** Sensitivity analysis DOE planning (OAT vs factorial vs LHS) may need `/gsd:research-phase` for optimal parameter sweep strategy depending on the specific analysis cases.
- **Phase 5:** OrcaFlex model integration patterns need investigation of OrcFxAPI vessel type import API specifics.

Phases with standard patterns (skip research-phase):
- **Phase 1:** Well-documented patterns -- Jinja2 template inheritance, Pydantic model extension, frequency normalization are all standard.
- **Phase 2:** Report section implementation follows the existing `OrcaWaveReportBuilder` section-module pattern exactly. 7 existing sections serve as direct templates.
- **Phase 4:** Batch orchestration extends existing `OrcaWaveBatchRunner` with well-understood `ProcessPoolExecutor` parallelism.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Nearly zero new dependencies. All recommendations verified against existing codebase (uv.lock, pyproject.toml). Jinja2 already in dependency tree. |
| Features | HIGH | Feature list derived from DNV/BV classification society documentation, Orcina official examples (L01-L06), and direct OrcFxAPI reference. Industry practice well-documented. |
| Architecture | HIGH | Architecture follows patterns already proven in this codebase (section-based builders, Pydantic contracts, factory patterns). Based on direct inspection of 30+ source files. |
| Pitfalls | HIGH | Pitfalls sourced from documented failures in this project's history (WRK-031 stall, piped-splashing-peacock QTF bug, frequency unit mismatch in doc-intelligence-report). Evidence-based, not speculative. |

**Overall confidence:** HIGH

### Gaps to Address

- **Licensed machine readiness:** The state of `licensed-win-1` has 8 pending action items (from hardware inventory). Phase 0 will surface which of these block progress, but the resolution timeline is uncertain.
- **Multi-body report structure:** The architecture supports multi-body (L03/L04 examples) but the report data model for body-to-body coupling matrices needs design during Phase 2 planning. Single-body is prioritized; multi-body deferred to v1.x.
- **Client branding workflow:** Report template YAML presets are designed but the branding injection mechanism (logo, company name, color scheme) is not detailed. Low priority for v1.1 but will surface when delivering to external clients.
- **Mesh generation for draught sensitivity:** Draft/loading condition sensitivity requires different hull meshes per draught. The hull panel catalog (WRK-114) may not have multi-draught meshes for all vessels. This is a data gap, not a code gap.
- **Windows CI runner:** Cross-platform testing requires a Windows GitHub Actions runner with OrcFxAPI access. Cost and licensing implications not evaluated.

## Sources

### Primary (HIGH confidence)
- [OrcaWave Batch Processing Documentation](https://www.orcina.com/webhelp/OrcaWave/Content/html/Automation,Batchprocessing.htm)
- [OrcaWave Automation Introduction](https://www.orcina.com/webhelp/OrcaWave/Content/html/Automation,Introduction.htm)
- [OrcFxAPI Python Diffraction Reference](https://www.orcina.com/webhelp/OrcFxAPI/Content/html/Pythonreference,Diffraction.htm)
- [OrcaWave Data Model Reference](https://www.orcina.com/webhelp/OrcaWave/Content/html/Data,Model.htm)
- [OrcFxAPI PyPI (v11.6.2)](https://pypi.org/project/OrcFxAPI/)
- [DNV-RP-C205 Environmental Conditions and Environmental Loads](https://www.researchgate.net/profile/Claes-Fredoe/post/How_do_I_analyze_fluid_structure_interaction_on_tall_towers/attachment/59d642efc49f478072eabb14/AS:273805639913473@1442291759410/download/rp-c205_2010-10.pdf)
- [DNV-RP-H103 Modelling and Analysis of Marine Operations](https://home.hvl.no/ansatte/gste/ftp/MarinLab_files/Litteratur/DNV/rp-h103_2011-04.pdf)
- Direct codebase inspection: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/` (30+ files), `orcawave/reporting/` (10 files), `orcaflex/reporting/` (10 files)

### Secondary (MEDIUM confidence)
- [Orcina L01 Default Vessel Example](https://www.orcina.com/wp-content/uploads/examples/l/l01/L01%20Default%20vessel.pdf) -- report structure expectations
- [DNV Wadam Hydrodynamic Analysis](https://www.dnv.com/services/frequency-domain-hydrodynamic-analysis-of-stationary-vessels-wadam-2412/) -- competitor capabilities
- [Bureau Veritas Homer Software](https://marine-offshore.bureauveritas.com/homer-software-essential-hydro-structure-calculation) -- competitor capabilities
- [ASME OMAE 2020 Sensitivity Study](https://asmedigitalcollection.asme.org/OMAE/proceedings-abstract/OMAE2020/84317/V001T01A039/1092573) -- sensitivity analysis methodology

### Tertiary (LOW confidence)
- Windows CI runner feasibility with OrcFxAPI -- no source evaluated, needs investigation during Phase 0

---
*Research completed: 2026-03-29*
*Ready for roadmap: yes*
