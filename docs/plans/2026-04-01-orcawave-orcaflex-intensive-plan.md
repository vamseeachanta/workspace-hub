# OrcaWave & OrcaFlex Intensive — 24-Hour Execution Plan (v2)

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Advance all OrcaWave/OrcaFlex engineering work — solver queue hardening, high-level spec.yml → OrcaWave pipeline, parametric RAO generation, and OrcaFlex frame analysis — in a focused 24-hour sprint using remaining Claude credit.

**Architecture:** Three waves of work, ordered by dependency. Wave 1 hardens the solver queue + syncs with licensed-win-1. Wave 2 scales the DiffractionSpec → OrcaWave pipeline for parametric hulls. Wave 3 extends OrcaFlex frame analysis for parachute project (static + dynamic).

**Tech Stack:** Python (via `uv run`), OrcFxAPI (on licensed-win-1 only), Pydantic v2, matplotlib, numpy, PyYAML, git-based solver queue

**Machine topology:**
- dev-primary (this machine): planning, code, tests, job submission, post-processing
- licensed-win-1: OrcFxAPI execution (OrcaWave + OrcaFlex), polls queue every 30 min
- licensed-win-2: secondary licensed machine (same tools)

---

## KEY EXISTING INFRASTRUCTURE

### DiffractionSpec — The High-Level YAML Pipeline (ALREADY EXISTS)

The repo already has a **solver-agnostic spec.yml → OrcaWave/AQWA input** pipeline:

- **Schema:** `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/input_schemas.py`
  - `DiffractionSpec` (Pydantic v2) — 789 lines, full validation
  - Sub-models: VesselSpec, EnvironmentSpec, FrequencySpec, WaveHeadingSpec, SolverOptions, etc.
  - `DiffractionSpec.from_yaml("spec.yml")` loads, validates, converts units
  - OrcaWave backend divides mass/density/inertia by 1000 (kg→te) automatically

- **Backend:** `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py`
  - Converts DiffractionSpec → OrcaWave native YAML (.yml with %YAML 1.1 header)
  - Handles mesh path resolution, frequency conversion, unit scaling

- **Live spec.yml examples (13 total):**
  - `L00_validation_wamit/` — 10 WAMIT validation cases (2.1 through 3.3)
  - `L02_barge_benchmark/spec.yml` — standard diffraction
  - `L03_ship_benchmark/spec.yml` — full QTF + external roll damping
  - `L04_spar_benchmark/spec.yml` — rad/s frequency input

- **Pattern (PAT-002):** `.claude/knowledge/entries/patterns/PAT-002-orcawave-input-yml-freq-extension.md`
  - Export .owd → _input.yml, modify frequencies, reload — extend grid without touching binary

- **THIS IS THE SCALING LEVER:** Write a simple high-level spec.yml (20-30 lines), the `DiffractionSpec` validates it, `OrcaWaveBackend` generates the full OrcaWave YAML (~180 lines), and an LLM or parametric script can generate spec.yml files by the hundreds.

### Hull Library & Parametric Analysis (PARTIALLY EXISTS)

- `digitalmodel/src/digitalmodel/hydrodynamics/hull_library/` — 20+ modules
  - `catalog.py`, `lookup.py`, `rao_database.py`, `parametric_hull.py`
  - `mesh_generator.py`, `mesh_refiner.py`, `mesh_scaler.py`
  - `line_generator/` — hull surface, panelizer, exporter
  - `panel_catalog.py`, `panel_inventory.py`
- `digitalmodel/src/digitalmodel/hydrodynamics/parametric_hull_analysis/`
  - `sweep.py`, `charts.py`, `models.py`, `shallow_water.py`, `forward_speed.py`
- `digitalmodel/docs/domains/orcawave/hull_forms/` — 1 hull (NeptuneBatchTestCase.yml)
- `digitalmodel/docs/domains/hull_library/` — exists but sparse
- **GAP:** No centralized hull parameter database (L, B, T, Cb) tracking what's been run

### Parachute Frame Analysis (2D DONE, OrcaFlex PENDING)

- `digitalmodel/src/digitalmodel/structural/parachute/` — 11 Python modules
  - `parachute_drag.py` — F = 0.5*rho*V²*Cd*A*Cx
  - `frame_model.py`, `frame_solver.py` — 2D direct stiffness, 3 DOF/node
  - `frame_geometry_3d.py` — 3D geometry already exists
  - `member_check.py` — Von Mises, unity ratios, bolt/weld/pin
  - `freecad_frame_builder.py` — CAD generation
- Tests: 8 test files in `digitalmodel/tests/structural/parachute/`
- **#1264 is STATIC analysis** (drag force applied statically to frame)
- **#1292 is DYNAMIC analysis** (time-domain parachute deployment snap loads)
- Both are children of #1242 (WRK-5082)

### Solver Queue (WORKING, NEEDS HARDENING)

- 1 completed OrcaWave run (test01.owd, 7.8s)
- 1 failed run (bad path — `.owr` extension instead of `.owd`/`.yml`)
- Batch submission not yet built
- No result watcher/auto-post-processing

---

## Current State Summary

### Open issues (16 total OrcaWave/OrcaFlex related)
- Priority:high: #1264 (OrcaFlex frame static), #569 (Vandiver damping, archived)
- Priority:medium: #24, #23, #21, #19, #1292, #29
- Priority:low: #22, #28, #20, #1464

---

## WAVE 1: Solver Queue Hardening + Licensed-Win-1 Sync
**Issues:** #29 (3-way benchmark), queue infrastructure
**Duration:** ~2 hours
**Prerequisite for:** Waves 2 and 3

### Task 1.1: Assign licensed jobs to licensed-win-1

**Objective:** Verify licensed-win-1 is polling, check Task Scheduler status, and confirm solver queue is actively pulling jobs

**Files:**
- Read: `config/workstations/registry.yaml` (current machine status)
- Read: `scripts/solver/setup-scheduler.ps1`
- Check: `queue/completed/`, `queue/failed/` for timestamps of last activity

**Steps:**
1. Review config/workstations/registry.yaml for licensed-win-1 tool list and status
2. Check git log for any commits from licensed-win-1 (author or machine-id in commit)
3. Document: last poll time, last job processed, queue health
4. If no recent activity: flag and create a verification checklist for next RDP session
5. Ensure all future OrcaWave/OrcaFlex jobs in this plan reference licensed-win-1

**Verification:** Confirm last licensed-win-1 activity timestamp

**Commit:** `docs(queue): licensed-win-1 assignment and health check`

### Task 1.2: Check latest files and code updated from licensed-win-1

**Objective:** Pull latest and review what licensed-win-1 has pushed since deployment

**Steps:**
1. `git pull origin main`
2. `git log --oneline --since="2026-03-31" -- queue/` to see all queue activity
3. Check `queue/completed/` for new results
4. Check `queue/failed/` for new failures
5. Verify process-queue.py matches current schema
6. Document findings

**Verification:** Timeline of all queue activity from licensed-win-1

### Task 1.3: Fix the failed job path pattern

---

### Task 1.2: Add batch job submission to submit-job.sh

**Objective:** Enable submitting multiple solver jobs from a YAML manifest

**Files:**
- Create: `scripts/solver/submit-batch.sh`
- Create: `scripts/solver/batch-manifest.yaml.example`
- Test: `tests/solver/test_batch_submit.sh`

**Step 1: Write batch manifest schema**

```yaml
# batch-manifest.yaml.example
# Submit multiple solver jobs at once
jobs:
  - solver: orcawave
    input_file: "digitalmodel/docs/domains/orcawave/L00_validation_wamit/2.1/OrcaWave v11.0 files/test01.owd"
    description: "L00 WAMIT validation"
    export_excel: true

  - solver: orcawave
    input_file: "digitalmodel/docs/domains/orcawave/examples/L01_default_vessel/L01_license_test.yml"
    description: "L01 default vessel"
    export_excel: true
```

**Step 2: Write submit-batch.sh**

Script reads the manifest, calls submit-job.sh for each entry, and does a single git push at the end (avoids N pushes).

**Step 3: Test with dry-run flag**

```bash
bash scripts/solver/submit-batch.sh --dry-run scripts/solver/batch-manifest.yaml.example
```

**Commit:** `feat(queue): batch job submission from YAML manifest`

---

### Task 1.3: Add result watcher with auto-pull and post-processing hook

**Objective:** Script that watches for completed jobs and triggers post-processing

**Files:**
- Create: `scripts/solver/watch-results.sh`
- Create: `scripts/solver/post-process-hook.py`

**Steps:**
1. `watch-results.sh` does `git pull`, checks `queue/completed/` for new results (compares against `.solver-state/last-seen.txt`)
2. For each new completed job, calls `post-process-hook.py` with the result directory
3. `post-process-hook.py` reads result.yaml, and for OrcaWave jobs extracts RAOs/added-mass to JSON
4. Can be run manually or scheduled as cron

**Commit:** `feat(queue): result watcher with post-processing hooks`

---

### Task 1.4: Submit 3-way benchmark jobs for Unit Box (#29)

**Objective:** Submit OrcaWave jobs for the Unit Box hull to complete the benchmark

**Files:**
- Create: `scripts/solver/benchmarks/unit-box-batch.yaml`
- Reference: `digitalmodel/docs/domains/orcawave/` for Unit Box input files

**Steps:**
1. Identify existing Unit Box .owd/.yml input files
2. Create batch manifest for all required runs
3. Submit via `submit-batch.sh`
4. Document expected completion time (30-min poll cycle)

**Commit:** `feat(benchmark): submit Unit Box OrcaWave jobs (#29)`

---

## WAVE 2: DiffractionSpec Pipeline Scaling + Parametric Hull RAOs (#22)
**Issues:** #22 (Parametric hull form RAOs), #1319 (hull form parametric design)
**Duration:** ~3 hours
**Depends on:** Wave 1 (batch submission)

### Task 2.1: Audit existing hull library and parametric infrastructure

**Objective:** Map what already exists before building new — avoid duplicate work

**Files to audit:**
- `digitalmodel/src/digitalmodel/hydrodynamics/hull_library/` (20+ modules)
  - `catalog.py` — what hull forms are catalogued?
  - `rao_database.py` — does a RAO database already exist?
  - `parametric_hull.py` — what parametric generation is implemented?
  - `lookup.py` — what queries are supported?
  - `mesh_generator.py` — can it generate GDF from parameters?
- `digitalmodel/src/digitalmodel/hydrodynamics/parametric_hull_analysis/` (8 modules)
  - `sweep.py` — what parametric sweeps are implemented?
  - `models.py` — what data models exist?
  - `manifest.yaml` — what's configured?
- `digitalmodel/docs/domains/hull_library/` — what's documented?
- `digitalmodel/docs/domains/orcawave/hull_forms/` — only 1 file (NeptuneBatchTestCase.yml)
- GH issues: #1314 (ship-specific hydrostatic tables), #1319 (hull form parametric, Series 60)

**Deliverable:** `docs/assessments/hull-library-audit.md` — current state, gaps, what needs building

**Decision:** If the existing hull_library already has a hull parameter database and mesh generation, extend it. If it's skeleton code, raise a GH issue for proper hull library architecture.

**Key principle:** All parametric hulls tracked in `data/` — no repeat of work. Every hull variation gets a unique ID, and results are stored alongside the spec that generated them.

**Commit:** `docs: hull library and parametric analysis infrastructure audit`

---

### Task 2.2: Build spec.yml generator for parametric hull sweeps

**Objective:** Generate DiffractionSpec-compliant spec.yml files from a high-level parameter sweep definition

**Files:**
- Create: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/parametric_spec_generator.py`
- Test: `digitalmodel/tests/hydrodynamics/diffraction/test_parametric_spec_generator.py`

**Design:**
```
Input: sweep_definition.yaml (high-level, 10-15 lines)
  hull_parameters:
    length: [100, 150, 200]
    beam_ratio: [5, 6, 7]      # L/B
    draft_ratio: [0.3, 0.4]    # T/B
    block_coefficient: [0.65, 0.75]
  environment:
    water_depth: 500
  frequencies:
    range: {start: 0.2, end: 2.0, count: 20}
    input_type: frequency
  headings:
    values: [0, 45, 90, 135, 180]

Output: N spec.yml files in data/parametric_hulls/{hull_id}/spec.yml
  + hull_registry.yaml tracking all generated hulls
```

**Semantic verification:** Each generated spec.yml is validated by `DiffractionSpec.from_yaml()` AND cross-checked against L00/L02/L03 reference specs for structural consistency (valid frequency ranges, reasonable mass/inertia, mesh path exists).

**TDD:** Test parameter expansion, spec validation, and reference cross-check.

**Commit:** `feat(orcawave): parametric spec.yml generator with DiffractionSpec validation (#22)`

---

### Task 2.3: RAO extraction, database, and professional reports

**Objective:** Extract RAOs from completed .owr files into queryable database + generate reports

**Files:**
- Extend: `digitalmodel/src/digitalmodel/hydrodynamics/hull_library/rao_database.py` (if exists)
- Create/Extend: `digitalmodel/src/digitalmodel/orcawave/parametric/rao_extractor.py`
- Create: `digitalmodel/src/digitalmodel/orcawave/parametric/rao_plots.py`
- Create: `digitalmodel/src/digitalmodel/orcawave/parametric/rao_report_html.py`
- Test: `digitalmodel/tests/orcawave/test_rao_database.py`

**RAO extractor** (runs on licensed-win-1 after solver completes):
```python
class RAOExtractor:
    def extract(self, owr_path: Path) -> RAOResult:
        """Extract 6-DOF RAOs, added mass, damping from .owr file."""
        # Uses OrcFxAPI.Diffraction().LoadResults()
```

**RAO database** (pure Python, runs anywhere):
```python
class RAODatabase:
    def add(self, hull_id: str, hull_params: dict, rao_result: RAOResult)
    def query(self, L=None, B=None, T=None, Cb=None) -> List[RAOResult]
    def compare(self, results: List[RAOResult]) -> ComparisonReport
```

**Graph types (matplotlib + HTML):**
1. Single hull: 6-DOF RAO vs frequency for all headings (6 subplots)
2. Comparison: overlay RAOs for multiple hulls at same heading
3. Heatmap: peak RAO vs hull parameter (e.g., L vs Cb, colored by heave RAO)
4. Summary table: key statistics per hull form

**HTML report:** Professional, client-facing. Plotly or matplotlib-to-HTML. Similar to existing `benchmark_report.html` in L02_barge_benchmark.

**Commit:** `feat(orcawave): RAO database, extraction, plots, and HTML reports (#22)`

---

### Task 2.4: Submit parametric batch and wire up post-processing

**Objective:** Generate and submit a starter batch of hull form variations

**Steps:**
1. Generate hull forms for a reduced matrix (e.g., 3 lengths × 2 beams × 2 drafts = 12 cases)
2. Each generates a spec.yml → OrcaWave backend converts to solver YAML
3. Create batch manifest for solver queue
4. Submit via submit-batch.sh
5. Configure post-process-hook.py to auto-extract RAOs on completion
6. All results tracked in `data/parametric_hulls/` with hull_registry.yaml

**Commit:** `feat(orcawave): submit parametric hull form batch (#22)`

---

## WAVE 3: OrcaFlex Frame Analysis — Static AND Dynamic (#1264, #1292, #1242)
**Issues:** #1264 (static frame), #1292 (dynamic snap load), #1242 (WRK-5082 parent)
**Duration:** ~3 hours
**Depends on:** Wave 1 (queue infrastructure)

### Analysis Type Decision

**Both static AND dynamic are needed — they answer different questions:**

| Issue | Analysis Type | What it answers |
|-------|--------------|-----------------|
| #1264 | **Static/quasi-static** | Peak member forces, deflections, unity ratios under steady-state drag |
| #1292 | **Time-domain dynamic** | Snap load DAF, peak transient forces, deceleration g-profile |

**#1264 (static) is the starting example** — simpler to implement, validates against existing 2D solver.
**#1292 (dynamic) extends it** — adds time-varying drag deployment, captures shock amplification.

The 2D solver (`frame_solver.py`) currently does static analysis only. The existing `parachute_drag.py` computes steady-state drag (F = 0.5*rho*V²*Cd*A*Cx). The dynamic snap load (#1292) needs a time-dependent drag ramp (chute opens over ~0.5s → peak force → decay).

### Task 3.1: Gather frame geometry and section properties from WRK-5082

**Objective:** Extract the parachute frame geometry that the 2D solver already uses

**Files:**
- Read: `digitalmodel/src/digitalmodel/structural/parachute/frame_model.py`
- Read: `digitalmodel/src/digitalmodel/structural/parachute/frame_geometry_3d.py`
- Read: `digitalmodel/src/digitalmodel/structural/parachute/parachute_drag.py`
- Read: `digitalmodel/src/digitalmodel/structural/parachute/member_check.py`
- Create: `digitalmodel/src/digitalmodel/solvers/orcaflex/frame_builder/__init__.py`
- Create: `digitalmodel/src/digitalmodel/solvers/orcaflex/frame_builder/geometry.py`

**Steps:**
1. Read existing frame_model.py AND frame_geometry_3d.py — 3D geometry already exists!
2. Extract 4130 chromoly tube section properties (OD, wall thickness, EA, EI, GJ)
3. Create a geometry.py that defines the 3D frame in a solver-neutral format
4. Write tests validating against the 2D model values

**Commit:** `feat(orcaflex): frame geometry extraction from WRK-5082 (#1264)`

---

### Task 3.2: Build OrcaFlex .dat input generator for STATIC frame analysis (#1264)

**Objective:** Generate an OrcaFlex model file for the parachute frame static analysis

**Files:**
- Create: `digitalmodel/src/digitalmodel/solvers/orcaflex/frame_builder/model_builder.py`
- Test: `digitalmodel/tests/orcaflex/test_frame_model_builder.py`

**Design:**
```python
class OrcaFlexFrameBuilder:
    def __init__(self, geometry: FrameGeometry):
        """Build OrcaFlex model from frame geometry."""

    def add_members(self):
        """Add line objects for each frame member with correct section props."""

    def add_supports(self):
        """Add fixed supports at vehicle mount points (C3, B1)."""

    def add_static_drag_force(self, force_n: float, attachment_point: str):
        """Apply static drag force at chute attachment point."""

    def generate_yaml(self) -> dict:
        """Generate OrcaFlex YAML input suitable for solver queue."""

    def generate_dat(self, output_path: Path):
        """Generate .dat file via OrcFxAPI (licensed-win-1 only)."""
```

**Load cases (static):**
- 200 MPH: F = from parachute_drag.py (existing calculation)
- 250 MPH: F = from parachute_drag.py (existing calculation)

**TDD:** Test YAML output structure, member count, section properties, boundary conditions.

**Commit:** `feat(orcaflex): static frame model builder for parachute analysis (#1264)`

---

### Task 3.3: Build OrcaFlex template for DYNAMIC snap load analysis (#1292)

**Objective:** Extend the frame builder for time-domain deployment dynamics

**Files:**
- Extend: `digitalmodel/src/digitalmodel/solvers/orcaflex/frame_builder/model_builder.py`
- Create: `digitalmodel/src/digitalmodel/solvers/orcaflex/frame_builder/deployment_dynamics.py`
- Test: `digitalmodel/tests/orcaflex/test_deployment_dynamics.py`

**Design additions for dynamic analysis:**
```python
class DeploymentDynamicsBuilder:
    """Time-domain parachute deployment model."""

    def add_chute_line(self, length: float, cd_profile: dict):
        """Model chute as line object with time-dependent drag."""

    def add_deployment_ramp(self, t_deploy: float, t_peak: float):
        """Define deployment time function (closed → opening → full drag)."""

    def set_simulation_params(self, duration: float, dt: float):
        """Configure time-domain simulation parameters."""
```

**Key OrcaFlex modeling decisions:**
- Chute modeled as a line object with time-dependent drag coefficient
- Deployment ramp: Cd goes from 0 → Cd_max over ~0.5s
- Snap load: peak force at full deployment (~1.5-3x steady-state = DAF)
- Simulation: 5-10 seconds, dt=0.001s for capturing transients

**Load cases (dynamic):**
- 200 MPH deployment: F(t) with ramp, extract peak snap load, DAF
- 250 MPH deployment: F(t) with ramp, extract peak snap load, DAF

**Commit:** `feat(orcaflex): dynamic deployment model for snap load analysis (#1292)`

---

### Task 3.4: Build cross-tool comparison framework

**Objective:** Compare results from 2D direct stiffness, CalculiX FEM, and OrcaFlex (static + dynamic)

**Files:**
- Create: `digitalmodel/src/digitalmodel/solvers/comparison/__init__.py`
- Create: `digitalmodel/src/digitalmodel/solvers/comparison/cross_tool.py`
- Test: `digitalmodel/tests/solvers/test_cross_tool_comparison.py`

**Design:**
```python
class CrossToolComparison:
    """Compare structural analysis results across solvers."""

    def add_result(self, solver_name: str, result: FrameResult)
    def compare_reactions(self) -> pd.DataFrame  # % difference table
    def compare_deflections(self) -> pd.DataFrame
    def compare_member_forces(self) -> pd.DataFrame
    def compare_dynamic_amplification(self) -> pd.DataFrame  # DAF comparison
    def generate_report(self, output_dir: Path)  # HTML + plots + YAML
```

**Commit:** `feat(solvers): cross-tool comparison framework (#1264, #1292, #1242)`

---

### Task 3.5: Submit OrcaFlex frame jobs and configure post-processing

**Objective:** Submit both static (2 jobs) and dynamic (2 jobs) analysis jobs

**Steps:**
1. Generate OrcaFlex input YAML for static load cases (200 + 250 MPH)
2. Generate OrcaFlex input YAML for dynamic load cases (200 + 250 MPH deployment)
3. Submit 4 jobs via solver queue to licensed-win-1
4. Configure post-process-hook.py for OrcaFlex frame result extraction
5. Document expected output format for cross-tool comparison

**Commit:** `feat(orcaflex): submit parachute frame analysis jobs (#1264, #1292)`

---

## Execution Guide

### Provider allocation for 24 hours

| Terminal | Provider | Work |
|----------|----------|------|
| Terminal 1 (this) | Claude | Wave 1 → 2 → 3 planning + orchestration |
| Terminal 2 | Codex | Implementation: batch submit, post-process hooks |
| Terminal 3 | Codex/Gemini | Implementation: parametric hull generator, plots |

### Key constraints
- `uv run` for all Python — never bare `python3`
- OrcFxAPI only on licensed-win-1 (jobs submitted via git queue)
- Commit to main + push immediately after each task
- TDD: tests before implementation, no exceptions

### Success criteria
- [ ] Solver queue: licensed-win-1 verified active, batch submission working, result watcher deployed
- [ ] Failed job diagnosed, resubmitted successfully
- [ ] Hull library audit complete — existing infra documented, gaps identified
- [ ] Parametric spec.yml generator: DiffractionSpec-validated, semantic cross-check vs L00/L02/L03
- [ ] 12+ hull variation spec.yml files generated and submitted as batch
- [ ] RAO database module: extraction + storage + query tested
- [ ] Client-facing RAO plots + HTML reports: 4 graph types generated
- [ ] OrcaFlex static frame: model builder tested, 2 static jobs submitted (#1264)
- [ ] OrcaFlex dynamic frame: deployment ramp model, 2 dynamic jobs submitted (#1292)
- [ ] Cross-tool comparison: framework tested with 2D results as baseline (static + dynamic DAF)
- [ ] Issues commented with progress: #22, #29, #1264, #1292, #1242

### Issue close criteria
- #29: Close when 3-way benchmark has real solver results compared
- #22: Close when parametric batch runs + RAO plots + HTML reports generated
- #1264: Close when OrcaFlex static frame results extracted + compared to 2D/CalculiX
- #1292: Close when dynamic snap load results extracted + DAF reported
- #1242: Comment with progress on children 6 (#1264) and 7 (#1292)

### Key existing assets to leverage (DO NOT REBUILD)
- `DiffractionSpec` (input_schemas.py) — 789-line Pydantic schema, already validates spec.yml
- `OrcaWaveBackend` (orcawave_backend.py) — converts DiffractionSpec → native OrcaWave YAML
- 13 live spec.yml files — use as semantic reference for validation
- PAT-002 pattern — .owd → _input.yml → modify → reload
- `hull_library/` — 20+ modules including rao_database.py, mesh_generator.py
- `parametric_hull_analysis/` — sweep.py, charts.py, models.py
- `structural/parachute/` — 11 modules + 8 test files (2D solver complete)
- `frame_geometry_3d.py` — 3D frame geometry already exists!
