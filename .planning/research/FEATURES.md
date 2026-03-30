# Feature Research

**Domain:** OrcaWave automation, hydrodynamic diffraction analysis reports, sensitivity analysis, batch processing
**Researched:** 2026-03-29
**Confidence:** HIGH (industry practice verified against DNV/BV/Orcina documentation + existing codebase audit)

## Feature Landscape

### Table Stakes (Users Expect These)

Features any engineer receiving a diffraction analysis calculation report expects. Missing these means the report cannot be submitted to a classification society or used as a basis for downstream mooring/riser analysis.

#### 1. Calculation Report Templates for Diffraction Analysis

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Design basis section | Every calculation report starts with inputs: water depth, vessel dimensions, mass, CoG, inertia tensor, environment. Classification societies (DNV, BV, LR) require traceability from input to output. | LOW | Existing warm-parchment YAML schema has `inputs` section. Map OrcaWave data items to it. |
| Hull geometry and mesh description | Panel count, symmetry, mesh format, waterline, dry body panels. Reviewer needs to assess mesh adequacy. OrcaWave validation page warnings (non-planar panels, irregular frequencies) must be reported. | MEDIUM | Existing geometry QA gates (watertight, normals, panel count, aspect ratio) feed directly into this section. |
| Mesh QA summary with pass/fail | Mesh quality metrics: panel count, non-planar panel count, aspect ratio warnings, irregular frequency treatment, interior surface panels. Without this, the reviewer cannot assess result credibility. | LOW | Already built in existing QA gates. Wire into report template. |
| Hydrostatic results table | Displacement, waterplane area, metacentric heights (GM), centre of buoyancy, centre of flotation. This is the first sanity check any reviewer performs. | LOW | OrcaWave computes these on the mesh details page before diffraction runs. Extract via `hydrostaticResults` API property. |
| RAO plots (displacement) for all 6 DOFs | Amplitude vs period/frequency plots for surge, sway, heave, roll, pitch, yaw at multiple headings. This is the primary deliverable of a diffraction analysis. | MEDIUM | Existing benchmark plotter handles amplitude overlay plots. Adapt for single-solver report output with multi-heading overlay. |
| RAO plots (load) with Haskind/Diffraction comparison | Load RAO comparison between Haskind and Diffraction methods serves as internal QA check. Classification societies expect to see method agreement. | MEDIUM | OrcaWave produces both when calculation method is "Both". Extract via `loadRAOsHaskind` and `loadRAOsDiffraction` API properties. |
| Added mass and damping coefficient plots | 6x6 matrix coefficients vs frequency. Added mass should converge at high frequency (infinite frequency added mass). Damping should tend to zero. Divergence flags mesh or numerical issues. | MEDIUM | Extract via `addedMass`, `infiniteFrequencyAddedMass`, `damping` API properties. Plot diagonal terms (6 plots) + key off-diagonal coupling terms. |
| Mean drift load results | Mean wave drift forces/moments for station-keeping assessment. Required for mooring design downstream (DNV-OS-E301, API RP 2SK). | MEDIUM | OrcaWave produces via control surface, momentum conservation, and pressure integration methods. Compare methods as QA. |
| Standards traceability | Every section must reference the governing standard clause (DNV-RP-C205 for environmental loads, DNV-RP-H103 for marine ops modelling). | LOW | Existing YAML manifest schema (Pydantic `ModuleManifest`) already supports clause-level traceability. |
| Executive summary with key findings | One-page summary: vessel ID, analysis type, key RAO peaks, natural periods, identified resonances, mesh convergence status, overall confidence assessment. | LOW | Template assembly from computed results. No new calculation logic. |
| OrcaFlex vessel type export confirmation | Downstream consumers need confirmation that the OrcaWave results import cleanly into OrcaFlex without warnings. The L01 example shows this is a common issue (frequency range, phase origin). | LOW | Existing OrcaFlex vessel type converter handles this. Report the import status and any warnings. |
| Appendix: full tabular results | Complete displacement RAO, load RAO, added mass, damping tables exportable to Excel. Engineers downstream need numbers, not just plots. | LOW | OrcaWave API `SaveResultsSpreadsheet()` produces Excel directly. Include as appendix or companion file. |

#### 2. Automated Sensitivity Analysis

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Mesh convergence study | Systematic refinement of panel count (coarse/medium/fine) with convergence plots showing results stabilize. This is the primary QA check for any BEM analysis. Orcina's own documentation recommends this. | HIGH | Requires running multiple OrcaWave analyses with different meshes. Needs mesh generation or multiple pre-prepared meshes. Use OrcFxAPI `Diffraction` class to automate. |
| Water depth sensitivity | Deep water vs finite depth comparison. The L01 example demonstrates 100m vs 400m produces significantly different surge RAOs at long periods. | MEDIUM | Parametric: change one data item (`WaterDepth`) in OrcaWave model, re-run, compare. Straightforward OrcFxAPI automation. |
| Draft/loading condition sensitivity | Vessels operate at multiple draughts (ballast, intermediate, full load). Each draught produces different RAOs. Consultancies routinely deliver multi-draught hydrodynamic databases. | HIGH | Each draught requires different mesh (different waterline), different mass/inertia/CoG. Needs a draught-parameterized workflow. |
| Roll damping sensitivity | Viscous roll damping is not captured by potential theory. External damping matrix applied as percentage of critical. The L01 example shows undamped vs damped roll resonance. | LOW | Single parameter change in constraints page (external damping matrix). Re-run and compare. |
| Heading resolution sensitivity | Standard analyses use 10-degree increments (0-180 degrees, 19 headings). Some applications need 5-degree or finer resolution. Cost scales linearly with headings for iterative solvers. | LOW | Change heading list in environment data, re-run. Report computation time vs heading count. |

#### 3. Batch Report Generation

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Batch execution of OrcaWave models | Run multiple `.owd` or `.yml` files sequentially without manual intervention. OrcaWave already has native batch processing (`.lst` job lists). | LOW | OrcaWave batch processor accepts `.lst` files. Also automatable via OrcFxAPI Python loop. Already built into OrcaWave. |
| Standardized output directory structure | Each analysis produces results in a predictable location: `{vessel_id}/{draught}/{results/}`. Essential for downstream automation. | LOW | Convention + mkdir. No complex logic. |
| Automated report generation from results | After batch execution, generate HTML calculation reports for each completed analysis without manual intervention. | MEDIUM | Loop over `.owr` result files, extract data via API, feed into report template. The warm-parchment pipeline (YAML to Markdown to HTML) already exists. |
| Batch comparison across examples | Run all L00-L06 examples through pipeline and produce a summary matrix showing which examples pass QA gates. | MEDIUM | Existing benchmark runner + multi-solver comparator infrastructure. Extend to single-solver QA mode. |
| Error handling and retry for failed analyses | OrcaWave batch processing abandons failed jobs but continues with others. Need to capture which jobs failed and why. | LOW | OrcaWave batch processor already does this. Wrap with Python error capture and reporting. |

### Differentiators (Competitive Advantage)

Features that set this tooling apart from manual diffraction analysis workflows. Not required, but valuable for efficiency and client impression.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Narrative report structure (not just data dump) | Engineering consultancy reports tell a story: design basis, methodology, results, interpretation, recommendations. Most automated tools produce data dumps. A narrative-structured report with engineering interpretation differentiates from generic solver output. | MEDIUM | Requires templated narrative blocks (Jinja2) with conditional logic: "Roll natural period of X.X seconds identified at heading Y degrees. External damping of Z% critical applied per [standard]. Damped response shows adequate convergence." |
| Integrated validation summary (multi-case) | Single HTML dashboard showing all validation cases (L00 WAMIT comparison) with per-DOF correlation, semantic equivalence, and pass/fail. Already partially built (validation_summary.html). | LOW | Extend existing validation summary infrastructure. Already has per-DOF correlation, PASS/FAIL, and semantic score columns. |
| Automatic natural period identification | Detect resonance peaks in RAO data, report natural periods for all 6 DOFs, compare against wave period range to flag potential resonance issues. | LOW | Peak detection on displacement RAO curves. Simple signal processing (scipy.signal.find_peaks). High value for quick engineering assessment. |
| QTF convergence study automation | Full QTF (second-order) calculations are expensive. Automated convergence study showing QTF results stabilize with mesh refinement and frequency resolution proves result adequacy. | HIGH | Full QTF requires "Full QTF calculation" solve type. Memory-intensive. Convergence study multiplies cost. Defer unless client specifically requires second-order analysis. |
| Cross-solver comparison as QA | Run same vessel through OrcaWave + AQWA (or BEMRosetta) and report agreement. Provides independent verification that classification societies value. | HIGH | Existing 3-way benchmark framework (WRK-031) already built. Integration into report pipeline needed. Requires AQWA license availability. |
| Interactive HTML reports with Plotly | Zoomable, hoverable plots in single-file HTML. Classification society reviewers can inspect specific data points without requesting raw data. | LOW | Already using Plotly HTML output throughout the codebase (benchmark plotter, OrcaFlex reports). Consistent with existing design decisions. |
| Report versioning and revision tracking | Track which input parameters changed between report revisions. Engineering reports require revision history (Rev A, B, C) with change descriptions. | MEDIUM | Leverage the warm-parchment schema `metadata.change_log` field. Git-based: diff between YAML input versions. |
| Automated OrcaFlex vessel type database delivery | Generate a complete OrcaFlex-ready vessel type database (.yml or direct API import) as a companion deliverable alongside the calculation report. This is what downstream analysts actually need. | LOW | Existing OrcaFlex vessel type converter already handles this. Package as part of the automated pipeline output. |
| Multi-draught database in single report | Present all loading conditions in a single report with side-by-side comparison plots (ballast vs loaded vs intermediate). Classification societies expect multi-draught databases. | HIGH | Requires running multiple analyses and merging results into comparative plots and tables. High value but significant orchestration complexity. |
| Spider/tornado diagram for sensitivity results | Visual summary showing which parameters most influence which DOF responses. Immediately shows where to focus analysis effort. | MEDIUM | Requires multiple sensitivity runs. Plot relative change in key metrics (natural period, peak RAO, mean drift) vs parameter variation. |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Real-time solver status dashboard | Users want to see solver progress live. | OrcaWave calculations run on licensed Windows machines. Building a real-time progress UI adds WebSocket/polling complexity for a solo-engineer workflow. OrcaWave's own `calculationProgressHandler` provides string updates but requires a running Python process. | Use OrcaWave native batch progress. Log completion timestamps to file. Post-completion notification via email (existing alerting infrastructure from worldenergydata). |
| Automatic mesh generation from CAD | Users want to go from STEP/IGES to mesh automatically. | Mesh generation for BEM analysis requires engineering judgment: waterline treatment, panel density distribution, symmetry exploitation, lid panels for irregular frequency removal. Fully automated mesh generation produces poor meshes that silently degrade results. | Provide mesh QA gates that flag problems in user-supplied meshes. Use pre-prepared meshes from the hull panel catalog (WRK-114). Support multiple mesh formats (GDF, DAT, HST). |
| Natural language problem description | "Analyse this vessel at 3 draughts in 100m water depth" should auto-configure everything. | The Tier 2 NLP routing layer is not built. Attempting it prematurely creates a brittle mapper that misinterprets domain-specific terms. A YAML input file is already a near-natural-language spec. | Provide well-documented YAML templates for common analysis types (single-body vessel, semi-sub, multi-body, TLP). Template selection is the "NLP" for now. |
| PDF report generation | Classification societies accept PDF. | PDF generation from HTML (Chrome headless `--print-to-pdf`) adds a system dependency. The rendering can break on complex Plotly charts. Interactive features (zoom, hover) are lost. | Deliver HTML as primary format (single-file, works offline). Add PDF as optional output via `weasyprint` or Chrome headless, clearly documented as lossy conversion. |
| GUI for report customization | Users want to drag-and-drop sections, change colors, add logos. | Building a GUI is a multi-month effort that serves one user (solo engineer). Report structure should be standardized, not customizable per report. | Use Jinja2 templates with CSS theming (warm-parchment design system). Client branding via a `branding.yaml` config (logo path, company name, color scheme). |
| Automatic result interpretation AI | "Tell me if these RAOs look reasonable." | LLM-based interpretation of engineering results is unreliable and could produce dangerous conclusions. RAO reasonableness depends on vessel geometry, loading condition, and environmental context that the LLM cannot fully assess. | Implement deterministic QA checks: natural period within expected range for vessel type, RAO convergence with mesh refinement, Haskind/Diffraction method agreement, hydrostatic property sanity checks. Flag anomalies for human review. |

## Feature Dependencies

```
[Geometry QA Gates] (existing)
    |
    +---requires--> [Mesh QA Summary in Report]
    |
    +---requires--> [Mesh Convergence Study]

[OrcaWave YAML Input Files] (existing, 206+ files)
    |
    +---requires--> [Batch Execution Pipeline]
    |                    |
    |                    +---requires--> [Automated Report Generation]
    |                    |
    |                    +---enhances--> [Batch Comparison Across Examples]
    |
    +---requires--> [Sensitivity Analysis Framework]
                         |
                         +---requires--> [Water Depth Sensitivity]
                         +---requires--> [Roll Damping Sensitivity]
                         +---requires--> [Mesh Convergence Study]
                         +---requires--> [Draft/Loading Condition Sensitivity]

[DiffractionSpec Schema] (existing, Pydantic v2)
    |
    +---requires--> [Report Template Data Model]
    |                    |
    |                    +---requires--> [Calculation Report HTML]
    |                    |
    |                    +---enhances--> [Narrative Report Structure]
    |
    +---enhances--> [Cross-Solver Comparison as QA]

[Warm-Parchment Design System] (existing)
    |
    +---requires--> [Calculation Report HTML]
    |
    +---enhances--> [Interactive Plotly Reports]

[OrcaFlex Vessel Type Converter] (existing)
    |
    +---enhances--> [OrcaFlex Export Confirmation in Report]
    |
    +---enhances--> [Automated OrcaFlex Database Delivery]

[Benchmark Plotter] (existing, 5 plot types)
    |
    +---requires--> [RAO Plots in Report]
    |
    +---enhances--> [Cross-Solver Comparison as QA]

[OrcFxAPI Python Diffraction Class]
    |
    +---requires--> [All automated execution features]
    +---requires--> [Result extraction for reports]
    +---requires--> [Sensitivity analysis parameter sweeps]
```

### Dependency Notes

- **Geometry QA Gates already built** -- watertight checks, normal validation, panel count, aspect ratio. These feed directly into mesh QA reporting without new work.
- **DiffractionSpec (Pydantic v2) already built** -- canonical schema with 20 sub-models, 9 enums. 166 tests. This is the data model foundation for report templates.
- **Benchmark Plotter already built** -- amplitude, phase, combined, difference, heatmap HTML plots. Adapt overlay plots for single-solver multi-heading report output.
- **Warm-parchment design system already built** -- CSS theming, KaTeX math, Chart.js charts. The calculation report skill (WRK-1178) defines the YAML-to-HTML pipeline.
- **OrcFxAPI Diffraction class is the critical external dependency** -- all automated execution, result extraction, and sensitivity analysis requires the Python API running on `licensed-win-1` (Windows, Orcina license). Without API access, only manual batch processing via OrcaWave GUI is possible.
- **Draft sensitivity requires new meshes** -- unlike water depth or roll damping (single parameter changes), different draughts need different hull meshes with different waterlines. This is the highest-complexity sensitivity parameter.

## MVP Definition

### Launch With (v1.1 Milestone)

Minimum viable automation -- what's needed to prove the pipeline works end-to-end and generate reports for all existing examples.

- [ ] **Report data model** (Pydantic) mapping OrcaWave results to report sections -- essential foundation for all report generation
- [ ] **Single-vessel calculation report template** (HTML) with design basis, hydrostatics, RAO plots (6 DOF), added mass/damping, mean drift, mesh QA, executive summary -- core deliverable
- [ ] **Automated result extraction via OrcFxAPI** -- load `.owr` files, extract all result arrays as numpy, feed into report data model -- enables automation
- [ ] **Batch execution script** for L00-L06 examples using OrcaWave batch processing or OrcFxAPI loop -- proves pipeline works across all existing examples
- [ ] **Standardized report for each example** (L00-L06) -- demonstrates template handles different vessel types (ship, semi-sub, multibody, TLP)
- [ ] **Water depth and roll damping sensitivity** -- simplest sensitivity parameters (single data item change), high demonstration value
- [ ] **OrcaFlex vessel type export** as companion output -- downstream consumers need this immediately

### Add After Validation (v1.x)

Features to add once the core pipeline is producing correct reports reliably.

- [ ] **Narrative report blocks** (Jinja2 conditional templates) -- trigger: after first client delivery reveals data-dump reports need interpretation
- [ ] **Mesh convergence study automation** -- trigger: when mesh QA gates flag marginal mesh quality
- [ ] **Natural period auto-detection** -- trigger: when reviewers ask "what are the natural periods?"
- [ ] **Multi-draught database workflow** -- trigger: when a project requires ballast + loaded condition databases
- [ ] **Spider/tornado sensitivity diagrams** -- trigger: when parameter sweeps are running and results need visual summary
- [ ] **Cross-solver comparison integration** -- trigger: when both OrcaWave and AQWA licenses are available on the same machine

### Future Consideration (v2+)

Features to defer until the automation pipeline is proven and client demand justifies the investment.

- [ ] **Full QTF convergence study** -- expensive computations, niche requirement (only for moored floating production systems with slow-drift resonance)
- [ ] **Multi-body interaction reports** -- requires additional data model complexity for body-to-body coupling matrices
- [ ] **PDF report generation** -- only when a client explicitly cannot accept HTML
- [ ] **Report versioning system** -- only when multiple revisions of the same analysis become routine
- [ ] **Branding/theming system** -- only when serving multiple clients who need different report branding

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Report data model (Pydantic) | HIGH | MEDIUM | P1 |
| Single-vessel calc report template | HIGH | MEDIUM | P1 |
| OrcFxAPI result extraction | HIGH | MEDIUM | P1 |
| Batch execution (L00-L06) | HIGH | LOW | P1 |
| Hydrostatic results table | HIGH | LOW | P1 |
| RAO plots (displacement, 6 DOF) | HIGH | MEDIUM | P1 |
| Added mass/damping plots | HIGH | MEDIUM | P1 |
| Mesh QA summary | HIGH | LOW | P1 |
| Executive summary | HIGH | LOW | P1 |
| Standards traceability | HIGH | LOW | P1 |
| OrcaFlex vessel type export | HIGH | LOW | P1 |
| Water depth sensitivity | MEDIUM | LOW | P1 |
| Roll damping sensitivity | MEDIUM | LOW | P1 |
| Load RAO Haskind/Diffraction QA | MEDIUM | MEDIUM | P2 |
| Mean drift load results | MEDIUM | MEDIUM | P2 |
| Tabular results appendix (Excel) | MEDIUM | LOW | P2 |
| Narrative report blocks | MEDIUM | MEDIUM | P2 |
| Natural period auto-detection | MEDIUM | LOW | P2 |
| Interactive Plotly reports | MEDIUM | LOW | P2 |
| Heading resolution sensitivity | LOW | LOW | P2 |
| Mesh convergence study | HIGH | HIGH | P2 |
| Multi-draught database | HIGH | HIGH | P3 |
| Draft/loading condition sensitivity | HIGH | HIGH | P3 |
| Cross-solver comparison | MEDIUM | HIGH | P3 |
| Spider/tornado diagrams | MEDIUM | MEDIUM | P3 |
| QTF convergence study | LOW | HIGH | P3 |
| Multi-body interaction reports | LOW | HIGH | P3 |

**Priority key:**
- P1: Must have for v1.1 milestone launch
- P2: Should have, add when pipeline is proven
- P3: Nice to have, future consideration

## Competitor Feature Analysis

The "competitors" here are manual engineering workflows and commercial software report generators. The comparison reflects what classification societies and engineering consultancies currently deliver vs. what this automation pipeline can provide.

| Feature | Manual Workflow (Current) | DNV Wadam/HydroD | Orcina OrcaWave GUI | Our Approach |
|---------|--------------------------|-------------------|---------------------|--------------|
| Report generation | Manual: copy data from solver into Word/Excel template. Hours per vessel. | Built-in report generator in HydroD. Follows DNV template. | No report generator -- results viewable in GUI graphs/tables page, exportable to Excel. | Automated: OrcFxAPI extracts results, Pydantic data model structures them, Jinja2+warm-parchment produces HTML. Minutes per vessel. |
| Batch processing | Run each model manually or use solver batch mode. No report automation. | Sesam Manager handles job queuing. | Native batch processing (.lst files). No post-processing automation. | OrcFxAPI Python loop or .lst batch with automated post-processing and report generation. |
| Sensitivity analysis | Manual: engineer creates model variants by hand, runs each, compares in spreadsheet. | Parametric study capability in HydroD for mesh and frequency sensitivity. | No built-in sensitivity tooling. Manual: modify OWD, re-run. | Automated parameter sweeps via OrcFxAPI: modify data items programmatically, run, extract, compare, plot. |
| Multi-solver QA | Run same vessel in multiple tools manually. Compare in Excel. | N/A (vendor lock-in to Sesam suite). | OrcaWave produces Haskind/Diffraction dual methods as internal QA. | Existing 3-way benchmark framework (AQWA, OrcaWave, BEMRosetta) with consensus metrics. |
| Standards traceability | Engineer manually writes standard references in report text. | Built into HydroD workflow (DNV standards integrated). | No standards traceability. | YAML manifests with clause-level traceability (existing ModuleManifest schema). Automated citation in report. |
| Mesh QA | Engineer visually inspects mesh in solver GUI. | HydroD mesh validation integrated. | OrcaWave validation page: non-planar panels, irregular frequencies, panel arrangement. | Existing geometry QA gates (watertight, normals, panel count, aspect ratio) + OrcaWave validation warnings captured in report. |
| OrcaFlex integration | Manual: export from diffraction tool, import to OrcaFlex, check warnings. | DNV tools export to Sesam format, not OrcaFlex. | Native: .owr files directly importable to OrcaFlex. Best integration available. | Automated: generate .owr, import via OrcFxAPI, validate, report import status. Companion OrcaFlex vessel type file as deliverable. |

## How Classification Societies Expect Hydrodynamic Analysis Deliverables

Based on DNV-RP-C205 (Environmental Conditions and Environmental Loads), DNV-RP-H103 (Modelling and Analysis of Marine Operations), and Bureau Veritas Homer/Hydrostar workflow, the standard deliverable structure is:

### Required Report Sections (per industry practice)

1. **Document Control** -- revision, date, author, reviewer, approval status, distribution list
2. **Design Basis** -- vessel principal particulars, loading conditions, environment (water depth, metocean), applicable codes and standards
3. **Geometry Description** -- hull form, mesh details, panel count, symmetry, coordinate system and datum
4. **Mesh Quality Assessment** -- convergence status, non-planar panel treatment, irregular frequency treatment, interior surface panels
5. **Analysis Configuration** -- solve type, frequency/period range, heading range, calculation methods (Haskind/Diffraction, mean drift method), solver settings (thread count, linear solver method)
6. **Hydrostatic Results** -- displacement, waterplane area, metacentric heights, centre of buoyancy/flotation, hydrostatic stiffness matrix
7. **First-Order Results** -- displacement RAOs (6 DOF, all headings), load RAOs, natural periods identification
8. **Hydrodynamic Coefficients** -- added mass matrix (frequency-dependent and infinite frequency), radiation damping matrix, external damping applied
9. **Second-Order Results** (if applicable) -- mean drift loads (all 3 methods if computed), Newman QTFs or full QTFs
10. **Sensitivity Studies** -- mesh convergence, water depth influence, external damping influence
11. **Comparison/Validation** -- cross-solver comparison, comparison with model test data (if available), Haskind vs Diffraction method agreement
12. **OrcaFlex Integration** -- import verification, frequency range coverage, phase convention confirmation
13. **Conclusions and Recommendations** -- key findings, identified resonances, limitations, recommendations for downstream analysis

### What This Means for the Report Template

The report data model must support all 13 sections. Not every report will include all sections (e.g., no QTF for simple transport analysis), so the template must handle optional sections gracefully. The existing warm-parchment schema with its optional `charts`, `data_tables`, and `methodology` sections is well-suited for this.

## Sources

- [OrcaWave Batch Processing Documentation](https://www.orcina.com/webhelp/OrcaWave/Content/html/Automation,Batchprocessing.htm)
- [OrcaWave Automation Introduction](https://www.orcina.com/webhelp/OrcaWave/Content/html/Automation,Introduction.htm)
- [OrcFxAPI Python Diffraction Reference](https://www.orcina.com/webhelp/OrcFxAPI/Content/html/Pythonreference,Diffraction.htm)
- [Orcina L01 Default Vessel Example (PDF)](https://www.orcina.com/wp-content/uploads/examples/l/l01/L01%20Default%20vessel.pdf)
- [Orcina OrcaFlex/OrcaWave Diffraction Examples](https://www.orcina.com/resources/examples/?key=l)
- [DNV Wadam -- Frequency Domain Hydrodynamic Analysis](https://www.dnv.com/services/frequency-domain-hydrodynamic-analysis-of-stationary-vessels-wadam-2412/)
- [DNV HydroD -- Hydrodynamic Analysis Software](https://www.dnv.com/services/hydrodynamic-analysis-and-stability-analysis-software-hydrod-14492/)
- [Bureau Veritas Homer -- Hydro-Structure Calculation](https://marine-offshore.bureauveritas.com/homer-software-essential-hydro-structure-calculation)
- [DNV-RP-C205 Environmental Conditions and Environmental Loads](https://www.researchgate.net/profile/Claes-Fredoe/post/How_do_I_analyze_fluid_structure_interaction_on_tall_towers/attachment/59d642efc49f478072eabb14/AS:273805639913473@1442291759410/download/rp-c205_2010-10.pdf)
- [DNV-RP-H103 Modelling and Analysis of Marine Operations](https://home.hvl.no/ansatte/gste/ftp/MarinLab_files/Litteratur/DNV/rp-h103_2011-04.pdf)
- [ASME OMAE 2020 -- Sensitivity Study of Vessel Hydrodynamic Model Parameters](https://asmedigitalcollection.asme.org/OMAE/proceedings-abstract/OMAE2020/84317/V001T01A039/1092573)
- [MDPI JMSE -- Sensitivity and Uncertainty Analysis of Floating Offshore Structures](https://www.mdpi.com/2077-1312/13/6/1015)
- Existing codebase: WRK-031 (3-way benchmark), WRK-026 (diffraction spec converter), WRK-129 (OrcaFlex report standardization), WRK-1178 (warm-parchment calculation report skill)

---
*Feature research for: OrcaWave automation, hydrodynamic diffraction analysis reports, sensitivity analysis, batch processing*
*Researched: 2026-03-29*
