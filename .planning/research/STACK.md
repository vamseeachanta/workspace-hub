# Stack Research: OrcaWave Automation — New Capabilities

**Domain:** Offshore hydrodynamic analysis automation — calculation reports, YAML generation, sensitivity analysis, batch processing
**Researched:** 2026-03-29
**Confidence:** HIGH

## Context: What Already Exists (DO NOT re-add)

The digitalmodel codebase already has a mature stack. These are **not** new additions; they are the foundation this research builds on:

| Already In Stack | Version (locked) | Role |
|------------------|------------------|------|
| OrcFxAPI | (proprietary, unlocked) | OrcaWave diffraction analysis engine |
| Pydantic | 2.12.5 | Schema validation — `DiffractionSpec`, `ReportConfig` |
| Plotly | 5.17.0 | Interactive RAO/coefficient plots |
| ruamel.yaml | 0.19.1 | YAML round-trip with comment/format preservation |
| PyYAML | 6.0.1 | Basic YAML load/dump |
| NumPy | <2.0.0 | Numerical computation |
| SciPy | <2.0.0 | Scientific computation |
| pandas | <3.0.0 | Data manipulation |
| Bootstrap 5.3.2 | (CDN) | Report HTML layout |
| KaTeX 0.16.11 | (CDN) | LaTeX equation rendering in calc reports |
| Chart.js 4.4.6 | (CDN) | Charts in calc reports |
| click | <9.0.0 | CLI framework |
| loguru | <1.0.0 | Logging |

Key existing infrastructure:
- `hydrodynamics/diffraction/input_schemas.py` — `DiffractionSpec` Pydantic model (solver-agnostic)
- `hydrodynamics/diffraction/orcawave_backend.py` — Converts `DiffractionSpec` to OrcaWave PascalCase YAML
- `hydrodynamics/diffraction/orcawave_batch_runner.py` — Batch execution with ThreadPoolExecutor
- `hydrodynamics/diffraction/report_generator.py` — Self-contained HTML diffraction report
- `orcawave/reporting/` — Section-based HTML report builder (model summary, RAOs, hydro matrices, QA)
- `structural/fatigue/parametric_sweep.py` — Cartesian product sweep pattern (precedent for sensitivity)
- `scripts/reporting/generate-calc-report.py` — Warm-parchment YAML-to-HTML pipeline
- `scripts/reporting/calc_report_css.py` — Warm-parchment design system CSS variables

## Recommended Stack Additions

### 1. Jinja2 — Report Template Engine

| Attribute | Value |
|-----------|-------|
| Technology | Jinja2 |
| Version | >=3.1.6 (already resolved in uv.lock as transitive dep) |
| Purpose | HTML template engine for calculation report templates with narrative flow |
| Why | Replaces f-string HTML concatenation in `report_generator.py` and `orcawave/reporting/builder.py` |

**Rationale:** The existing report generators use Python f-string concatenation to build HTML (see `_HTML_TEMPLATE` in `builder.py` and the 100+ line HTML template in `report_generator.py`). This works for simple section assembly but breaks down for:
- **Narrative flow** — client-facing reports need conditional paragraphs, section reordering, and prose templates that change based on analysis type (single body vs. multi-body, deep water vs. shallow, with/without QTF)
- **Batch variation** — L01 through L06 examples each need slightly different report structure (L03/L04 enable multi-body, L05 enables panel pressures, L06 enables QTF)
- **Maintainability** — template files are editable by non-developers; f-strings in Python source are not

Jinja2 is already in the dependency tree as a transitive dependency of Flask, mkdocs, and FastAPI. Adding it as an explicit dependency costs zero new packages. Template inheritance lets you define a `base_report.html.j2` and extend it per analysis type.

**Integration point:** New `orcawave/reporting/templates/` directory with `.html.j2` files. The existing `OrcaWaveReportBuilder.build()` method calls section builders that return HTML strings; Jinja2 replaces this with `template.render(sections=section_data)`. Plotly figures are passed as pre-rendered HTML divs (unchanged from current pattern in `rao_plots.py`).

**What NOT to do:** Do not replace the existing warm-parchment CSS system. Jinja2 templates should `{% include 'warm_parchment_base.css' %}` or reference the existing CSS variables from `calc_report_css.py`. The design system is separate from the template engine.

### 2. No New YAML Library — Use Existing `ruamel.yaml` + `DiffractionSpec.to_yaml()`

| Attribute | Value |
|-----------|-------|
| Technology | ruamel.yaml (already at 0.19.1) + existing Pydantic `DiffractionSpec` |
| Version | 0.19.1 (locked) |
| Purpose | Deterministic YAML generation for OrcaWave input files |
| Why | Already has the right abstraction — do not add another layer |

**Rationale:** The deterministic YAML generation pipeline already exists in two layers:
1. **Canonical spec** (`DiffractionSpec.to_yaml()`) — Uses PyYAML `yaml.dump()` with `sort_keys=False` for field-order-preserving output
2. **OrcaWave backend** (`orcawave_backend.py`) — Custom `_CleanDumper` that outputs OrcaWave conventions (PascalCase keys, `Yes`/`No` unquoted booleans, SI units)

The "deterministic YAML generation" capability means: given vessel parameters (name, mesh file, COG, radii of gyration, water depth, frequencies, headings), produce a complete OrcaWave `.yml` project file deterministically. This is already implemented in `orcawave_backend.py` via `spec_to_orcawave_yaml()`.

What is actually needed is **parametric YAML generation** — creating multiple spec variants from a base template by substituting parameter values. This requires:
- `DiffractionSpec.model_copy(update={...})` (Pydantic v2 deep copy with field overrides)
- The existing `orcawave_backend.py` conversion pipeline

No new libraries needed. The `ruamel.yaml` round-trip capability is relevant only if we need to modify existing OrcaWave YAML files while preserving comments — which applies to the "match closest example YAML and parametric update" workflow.

**Integration point:** New `hydrodynamics/diffraction/parametric_generator.py` that takes a `DiffractionSpec` base + parameter overrides dict, produces N specs, and calls the existing backend for each.

### 3. No SALib — Use Existing Cartesian Product Pattern for Sensitivity Analysis

| Attribute | Value |
|-----------|-------|
| Technology | `itertools.product` + pandas + existing sweep pattern |
| Version | stdlib |
| Purpose | Parameter sweep for sensitivity analysis (mesh density, frequency count, water depth, heading spacing) |
| Why | SALib is overkill; engineering sensitivity is exhaustive enumeration, not statistical sampling |

**Rationale:** SALib provides Sobol, Morris, and FAST methods for global sensitivity analysis — these are sampling-based methods for models with 10+ parameters where exhaustive enumeration is infeasible. OrcaWave sensitivity analysis has 3-5 parameters (mesh density, frequency range, heading spacing, water depth, symmetry choice), each with 2-4 discrete values. The total combination space is 16-256 runs, which is feasible to enumerate exhaustively.

The codebase already has this exact pattern in `structural/fatigue/parametric_sweep.py`:
- Cartesian product of parameter values via `itertools.product`
- Results collected in a pandas DataFrame
- Tornado chart showing parameter influence
- HTML report with interactive Plotly visualization

Replicating this pattern for OrcaWave sensitivity (replacing SCF/curve/thickness/DFF with mesh_density/freq_count/heading_spacing/water_depth) requires zero new dependencies.

**When SALib WOULD be needed:** If sensitivity analysis expands to 10+ parameters with continuous ranges (e.g., full vessel optimization). Not in scope for v1.1.

**Integration point:** New `hydrodynamics/diffraction/sensitivity_sweep.py` following the `parametric_sweep.py` pattern. Input: base `DiffractionSpec` + parameter ranges. Output: pandas DataFrame + tornado chart HTML.

### 4. `concurrent.futures` — Batch Report Generation Orchestration

| Attribute | Value |
|-----------|-------|
| Technology | `concurrent.futures.ProcessPoolExecutor` (stdlib) |
| Version | stdlib (Python 3.11) |
| Purpose | Parallel batch report generation across L01-L06 + benchmarks |
| Why | Already used in `orcawave_batch_runner.py` (ThreadPoolExecutor) and `batch_processor.py` (ProcessPoolExecutor) |

**Rationale:** Batch report generation (run all examples through the pipeline) is CPU-bound for the report rendering phase and IO-bound for the OrcaWave solver phase. The existing `OrcaWaveBatchRunner` uses `ThreadPoolExecutor` for solver execution (because OrcFxAPI releases the GIL during computation). Report generation should use `ProcessPoolExecutor` because HTML rendering + Plotly figure generation is CPU-bound Python.

No new library needed. The orchestration pattern from `orcawave_batch_runner.py` (config -> job list -> parallel execution -> result collection -> summary report) is reusable.

**Integration point:** Extend `OrcaWaveBatchRunner` or create a `ReportBatchRunner` that wraps the existing batch runner output and adds report generation as a post-processing step.

### 5. `deepdiff` — Report Regression Testing

| Attribute | Value |
|-----------|-------|
| Technology | deepdiff |
| Version | >=8.0.0 (already in pyproject.toml) |
| Purpose | Detect regressions in batch report output between runs |
| Why | Already a dependency; structural diff of YAML/dict outputs catches numerical drift |

**Rationale:** When running batch reports across all examples, you need to detect when a code change causes numerical differences in outputs. `deepdiff` is already in the dependency list and provides `DeepDiff(t1, t2, significant_digits=6)` for floating-point-aware comparison of nested structures. Use it to compare the extracted report data (before HTML rendering) between the current run and a stored baseline.

**Integration point:** Test fixtures store baseline `DiffractionReportData.model_dump()` as JSON. Tests use `deepdiff` to compare current extraction against baseline with configurable tolerance.

## Supporting Libraries (Already Present, New Usage)

| Library | Version | New Usage | When |
|---------|---------|-----------|------|
| Jinja2 | 3.1.6 | Report templates with inheritance | Report template redesign |
| ruamel.yaml | 0.19.1 | Round-trip edit of example YAMLs preserving comments | Parametric update workflow |
| deepdiff | >=8.0.0 | Report regression testing | Batch validation |
| tabulate | >=0.9.0 | Hydro matrix formatting in reports | Report sections |
| tqdm | >=4.67.1 | Batch progress bars | Batch runner UI |

## Installation

```bash
# Jinja2 is the ONLY new explicit dependency. All others already present.
# Add to pyproject.toml [project] dependencies:
#   "Jinja2>=3.1.0,<4.0.0",

# No pip install needed if already resolved in uv.lock (it is — transitive dep).
# Making it explicit ensures it survives dependency tree changes.

uv sync
```

## Alternatives Considered

| Recommended | Alternative | Why Not |
|-------------|-------------|---------|
| Jinja2 for templates | Mako | Jinja2 already a transitive dep, better docs, more common in Python ecosystem |
| Jinja2 for templates | Django templates | Pulls in Django; Jinja2 is standalone |
| Jinja2 for templates | Continue with f-strings | Narrative flow requires conditional blocks, loops, and inheritance that f-strings cannot express cleanly |
| `itertools.product` sweep | SALib | SALib is for statistical sampling (Sobol, Morris) when exhaustive sweep is infeasible; OrcaWave has 3-5 discrete params |
| `itertools.product` sweep | Custom grid search | Reinventing stdlib; `itertools.product` + pandas is the established pattern in this codebase |
| ruamel.yaml for round-trip | StrictYAML | StrictYAML rejects standard YAML features OrcaWave needs (bare Yes/No, flow sequences) |
| Pydantic `model_copy` | dataclasses replace | Pydantic v2 is already the schema layer; `model_copy(update=...)` is purpose-built for this |
| ProcessPoolExecutor | Dask/Ray | Massive overkill for 6-20 batch jobs; stdlib is sufficient |
| ProcessPoolExecutor | asyncio | Report rendering is CPU-bound, not IO-bound; multiprocessing is correct |
| deepdiff for regression | Custom JSON diff | deepdiff already handles float tolerance, nested structures, and type coercion |

## What NOT to Add

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| SALib | Overkill for 3-5 parameter engineering sweeps; adds scipy/matplotlib deps that would conflict with pinned versions | `itertools.product` + pandas (existing pattern) |
| WeasyPrint / wkhtmltopdf | PDF generation adds OS-level dependencies (Cairo, Pango, Qt); HTML reports are the deliverable | HTML with `@media print` CSS for print-to-PDF |
| Celery / Redis | Task queue for batch processing is architectural overkill for 6-20 jobs | `concurrent.futures` stdlib |
| pydantic-yaml | Thin wrapper around ruamel.yaml + pydantic; adds indirection without value when both are already used directly | `DiffractionSpec.to_yaml()` + ruamel.yaml directly |
| Cookiecutter / copier | Template scaffolding tools for project generation, not report templates | Jinja2 directly |
| ReportLab | PDF-native rendering; reports are HTML-first | Jinja2 + HTML |
| nbconvert / Jupyter | Notebook-based reports add Jupyter kernel dependency | Standalone HTML generation |
| Dash (for reports) | Dash is for live dashboards, not static calculation reports; already a dep but wrong tool | Jinja2 + Plotly static HTML |

## Stack Patterns by Capability

**If building narrative calculation reports:**
- Use Jinja2 templates with warm-parchment CSS base
- Template inheritance: `base_report.html.j2` -> `orcawave_single_body.html.j2` / `orcawave_multi_body.html.j2`
- Pass Plotly figures as `fig.to_html(full_html=False, include_plotlyjs=False)` into template context
- Include Plotly JS once in base template via CDN
- Include KaTeX for equation rendering (already in warm-parchment system)

**If generating deterministic OrcaWave YAML:**
- Start from `DiffractionSpec` Pydantic model (canonical source of truth)
- Use `model_copy(update={"field": new_value})` for parametric variants
- Pipe through `orcawave_backend.spec_to_orcawave_yaml()` for OrcaWave format
- Use ruamel.yaml round-trip mode only when modifying existing example YAML files

**If running sensitivity sweeps:**
- Define parameter space as `dict[str, list[Any]]` (param name -> discrete values)
- Generate combinations with `itertools.product`
- For each combination: create `DiffractionSpec` variant, run through pipeline, extract key metrics
- Collect results in pandas DataFrame
- Generate tornado chart with Plotly (existing pattern from `parametric_sweep.py`)

**If batch processing all examples:**
- Enumerate example directories (L01-L06 + benchmarks)
- For each: load/generate spec -> run OrcaWave -> extract results -> generate report
- Use `ProcessPoolExecutor` for report generation phase
- Collect batch summary with timing, pass/fail status, warnings

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| Jinja2 3.1.6 | Python >=3.7 | No conflict with existing deps; already in uv.lock |
| Pydantic 2.12.5 | ruamel.yaml 0.19.1 | `model_dump(mode="json")` produces clean dicts for YAML serialization |
| Plotly 5.17.0 | Jinja2 3.1.6 | `fig.to_html(full_html=False)` produces embeddable div+script for templates |
| ruamel.yaml 0.19.1 | PyYAML 6.0.1 | Can coexist; ruamel for round-trip, PyYAML for simple load/dump |

## Sources

- [Jinja2 3.1.6 on PyPI](https://pypi.org/project/Jinja2/) — version confirmed, release date 2025-03-05 (HIGH confidence)
- [Jinja2 changelog](https://jinja.palletsprojects.com/en/stable/changes/) — stable 3.1.x line (HIGH confidence)
- [ruamel.yaml 0.19.1 on PyPI](https://pypi.org/project/ruamel.yaml/) — version confirmed, release date 2026-01-02 (HIGH confidence)
- [ruamel.yaml documentation](https://yaml.readthedocs.io/) — round-trip preservation features (HIGH confidence)
- [SALib on PyPI](https://pypi.org/project/SALib/) — v1.5.2, evaluated and rejected for this use case (HIGH confidence)
- [SALib documentation](https://salib.readthedocs.io/) — Sobol/Morris methods documentation (HIGH confidence)
- Existing codebase: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py` — OrcaWave YAML generation (HIGH confidence, direct inspection)
- Existing codebase: `digitalmodel/src/digitalmodel/structural/fatigue/parametric_sweep.py` — sweep pattern precedent (HIGH confidence, direct inspection)
- Existing codebase: `digitalmodel/src/digitalmodel/orcawave/reporting/builder.py` — current report builder architecture (HIGH confidence, direct inspection)
- Existing codebase: `scripts/reporting/calc_report_css.py` — warm-parchment design system (HIGH confidence, direct inspection)
- Existing codebase: `digitalmodel/uv.lock` — locked dependency versions (HIGH confidence, direct inspection)

---
*Stack research for: OrcaWave automation — calculation reports, YAML generation, sensitivity analysis, batch processing*
*Researched: 2026-03-29*
