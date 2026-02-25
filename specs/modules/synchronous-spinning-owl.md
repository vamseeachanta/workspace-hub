# Plan: OrcaWave Examples Workflow — WRK-317 through WRK-322

## Context

The user wants to systematically work through the 6 official OrcaWave example models
(L01–L06) in `docs/domains/orcawave/examples/`, building a complete analysis+QA workflow
and packaging the learnings into skills and an HTML report capability.

The distinction between OrcaWave (diffraction/frequency-domain) and OrcaFlex
(time-domain/structural) was also flagged as a confusion point to be documented.

**Current state of examples:**

| Example | Description | YML | Run Script | Excel | OWD/OWR |
|---------|-------------|-----|-----------|-------|---------|
| L01 | Default vessel | ✓ (2) | ✓ (3 py) | ✓ | ✗ |
| L02 | OC4 Semi-sub | ✓ (1) | ✗ | ✗ | ✗ |
| L03 | Semi-sub multibody | ✓ (1) | ✗ | ✗ | ✗ |
| L04 | Sectional bodies | ✓ (1) | ✗ | ✗ | ✗ |
| L05 | Panel pressures | ✓ (1) | ✗ | ✗ | ✗ |
| L06 | Full QTF diffraction | ✓ (2) | ✗ | ✗ | ✓ (4) |

**Existing OrcaWave skills** (all in `.claude/skills/engineering/marine-offshore/`):
- `orcawave-analysis` — core diffraction, 40+ properties documented
- `orcawave-to-orcaflex` — .owr → OrcaFlex vessel type conversion
- `orcawave-aqwa-benchmark` — cross-validation with AQWA
- `orcawave-qtf-analysis` — second-order QTF workflows
- `orcawave-mesh-generation` — panel mesh creation and quality
- `orcawave-damping-sweep` — exists but sparse
- `orcawave-multi-body` — exists but sparse
- `orcawave-visualization` — model views, mesh screenshots
- `diffraction-analysis` — master orchestration skill

**DIFFRACTION_CAPABILITIES_EXPANSION_PLAN.md**: Phases 1–3 complete;
**Phase 4 (Templates + Examples)** is listed as "not yet started" — our work directly maps to Phase 4.

---

## Work Items to Capture

### WRK-317 — Audit & document all OrcaWave input parameters from L01–L06
**Route B (Medium) | Target: digitalmodel**

**What**: Review all 6 example .yml files, extract every unique input parameter key,
and produce a comprehensive parameter reference document in the examples folder.

**Scope**:
- Read all .yml files (L01–L06) exhaustively
- Categorise parameters: Solver, Environment, Mesh quality, Output, QTF, Restart, Body
- Cross-reference with OrcFxAPI to confirm completeness
- Produce `docs/domains/orcawave/examples/PARAMETER_REFERENCE.md`

**Files**:
- All `Lxx/*.yml` in `docs/domains/orcawave/examples/`
- Output: `docs/domains/orcawave/examples/PARAMETER_REFERENCE.md`

**Acceptance criteria**:
- [ ] All unique parameter keys from L01–L06 listed with type, default, and description
- [ ] Parameters that differ across examples highlighted (e.g., solver method, QTF config)
- [ ] Reference committed to repo

---

### WRK-318 — Create run scripts for L02–L06 and generate Excel outputs
**Route B (Medium) | Target: digitalmodel | Blocked by: WRK-317**

**What**: Write a Python run script for each of L02–L06 following the L01 pattern
(`run_orcawave_diffraction_improved.py`), execute each, and save the .owr result +
Excel export in the same folder.

**Scope**:
- Template: `L01_default_vessel/run_orcawave_diffraction_improved.py` (canonical pattern)
- Create `run_orcawave.py` per folder (L02–L05; L06 has binary .owd so script restarts from those)
- Execute each script → write `.owr` and `.xlsx` alongside the .yml
- Excel sheet must cover: RAOs (all DOFs), added mass/damping, mean drift, headings summary

**Files per example folder**:
- `run_orcawave.py` (new)
- `Lxx_<name>_owr.xlsx` (new)
- `Lxx_<name>.owr` (new, from API run)

**Acceptance criteria**:
- [ ] Run scripts created for L02, L03, L04, L05, L06
- [ ] Excel outputs saved for all 6 examples in their respective folders
- [ ] OWR result files saved alongside

---

### WRK-319 — OrcaWave output QA suite for L01–L06
**Route C (Complex) | Target: digitalmodel | Blocked by: WRK-318**

**What**: Build a systematic QA module that reads each example's Excel output and
validates the results against expected ranges and known physical checks.

**Scope**:
- QA checks per example (based on what output type is produced):
  - RAO monotonicity / peak location vs known vessel period
  - Added mass high-frequency limit (approaches displaced volume)
  - Damping positivity at each frequency
  - Mean drift non-negative (for head seas)
  - QTF symmetry checks (L06)
  - Multi-body coupling symmetry (L03)
  - Panel pressure continuity (L05)
- QA report: `docs/domains/orcawave/examples/QA_REPORT.md` + per-example `QA_PASS.json`
- Cross-example consistency: confirm common parameters (water depth, density) produce consistent trends

**Files**:
- `docs/domains/orcawave/examples/qa/orcawave_example_qa.py` (new module)
- `docs/domains/orcawave/examples/qa/QA_REPORT.md` (generated)
- Per-folder: `Lxx_qa_results.json`

**Acceptance criteria**:
- [ ] QA module written with per-example check functions
- [ ] All 6 examples pass QA or failures documented with explanation
- [ ] QA report committed

---

### WRK-320 — Enhance OrcaWave skills with examples-derived patterns
**Route B (Medium) | Target: workspace-hub | Blocked by: WRK-319**

**What**: Update existing OrcaWave skills with the concrete patterns, parameters,
and QA lessons learned from working through L01–L06.

**Scope (targeted updates, not full rewrites)**:
- `orcawave-analysis/SKILL.md`: Add full parameter reference table (from WRK-317),
  example-specific run patterns, Excel output section
- `orcawave-qtf-analysis/SKILL.md`: Add L06 restart workflow, full QTF vs first-order
  comparison pattern
- `orcawave-multi-body/SKILL.md`: Flesh out with L03 patterns (currently sparse)
- `orcawave-damping-sweep/SKILL.md`: Add drag linearisation patterns from L02
- New: `orcawave-analysis/EXAMPLES.md` — concise 1-page example map (L01–L06 at a glance)

**Acceptance criteria**:
- [ ] Parameter table added to orcawave-analysis skill
- [ ] L06 restart workflow documented in qtf-analysis skill
- [ ] orcawave-multi-body and orcawave-damping-sweep fleshed out
- [ ] EXAMPLES.md created

---

### WRK-321 — OrcaWave modular HTML report (custom per example)
**Route C (Complex) | Target: digitalmodel | Independent**

**What**: Build a modular, user-configurable HTML report for OrcaWave analysis results.
Each section is optional and user-controlled. Output is a single self-contained HTML file.

**Sections (all optional, driven by config)**:
- Model summary (geometry, mesh stats, periods, headings)
- RAO plots (per DOF, interactive Plotly)
- Added mass / damping matrices
- Mean drift table + polar plot (if QTF enabled)
- Panel pressure contour (if L05-style output)
- Multi-body coupling matrix (if multi-body)
- QTF heatmap (if full QTF)
- QA pass/fail summary

**Entry point**:
```python
from digitalmodel.orcawave.reporting import generate_orcawave_report
generate_orcawave_report(owr_path, config_yml, output_html)
```

**Config driven by a YAML** (user specifies which sections to include).

**Files**:
- `src/digitalmodel/orcawave/reporting/__init__.py`
- `src/digitalmodel/orcawave/reporting/builder.py` (section orchestrator)
- `src/digitalmodel/orcawave/reporting/sections/` (one module per section)
- `src/digitalmodel/orcawave/reporting/config.py` (Pydantic config schema)
- `docs/domains/orcawave/examples/report_config_template.yml`

**Acceptance criteria**:
- [ ] All 8 section types implemented with toggle on/off
- [ ] L01 example produces valid HTML report with all sections
- [ ] Config YAML documented in skill and example folder
- [ ] Tests cover builder + each section renderer

---

### WRK-322 — Clarify OrcaWave vs OrcaFlex distinction in skills and docs
**Route A (Simple) | Target: workspace-hub, digitalmodel | Independent**

**What**: Add a clear, concise distinction between OrcaWave (diffraction,
frequency-domain) and OrcaFlex (time-domain, structural) in all places where
confusion arises. This is a documentation-only item.

**Scope**:
- `orcawave-visualization/SKILL.md`: Update description to state OrcaWave scope upfront
- `orcawave-analysis/SKILL.md`: Add "OrcaWave vs OrcaFlex" section near the top
- `diffraction-analysis/SKILL.md`: Add tool selection guidance
- `MEMORY.md`: Add a "OrcaWave vs OrcaFlex" gotcha entry (or create
  `.claude/knowledge/entries/gotchas/GOT-XXX-orcawave-vs-orcaflex.md`)

**Distinction to document**:
| Aspect | OrcaWave | OrcaFlex |
|--------|----------|---------|
| Domain | Frequency-domain diffraction | Time-domain FEM/dynamics |
| API class | `OrcFxAPI.Diffraction` | `OrcFxAPI.Model` |
| Input file | `.owd` (binary) / `.yml` (config) | `.dat` (binary) |
| Results | `.owr` (RAOs, added mass, QTF) | `.sim` (time histories) |
| SaveModelView | NOT available | Available |
| Primary output | Hydrodynamic coefficients | Structural responses |

**Acceptance criteria**:
- [ ] Distinction table added to orcawave-analysis SKILL.md
- [ ] Memory/knowledge entry created
- [ ] All 3 skills updated with scope clarity at the top

---

## Dependency Chain

```
WRK-322 (Simple — independent, do first)
WRK-317 (Medium — audit .yml parameters)
  └→ WRK-318 (Medium — run scripts + Excel outputs)
       └→ WRK-319 (Complex — QA suite)
            └→ WRK-320 (Medium — skill updates)
WRK-321 (Complex — HTML report, independent track)
```

## IDs and Metadata

Next available WRK ID: **317** (highest in pending is WRK-316)

| WRK | Title | Route | Priority | Depends |
|-----|-------|-------|----------|---------|
| 317 | Audit OrcaWave .yml parameters L01-L06 | B | high | — |
| 318 | Run scripts + Excel outputs for L02-L06 | B | high | 317 |
| 319 | OrcaWave examples QA suite | C | medium | 318 |
| 320 | Enhance OrcaWave skills with example patterns | B | medium | 319 |
| 321 | OrcaWave modular HTML report | C | medium | — |
| 322 | OrcaWave vs OrcaFlex distinction docs | A | high | — |
