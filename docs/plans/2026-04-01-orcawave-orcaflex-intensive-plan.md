# OrcaWave & OrcaFlex Intensive — 24-Hour Execution Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Advance all OrcaWave/OrcaFlex engineering work — solver queue hardening, parametric RAO pipeline, OrcaFlex frame analysis — in a single focused 24-hour sprint.

**Architecture:** Three waves of work, ordered by dependency. Wave 1 hardens the solver queue infrastructure (unblocks everything else). Wave 2 builds the parametric OrcaWave/RAO pipeline. Wave 3 builds the OrcaFlex frame analysis for the parachute project. Each wave produces submittable solver jobs.

**Tech Stack:** Python (via `uv run`), OrcFxAPI (on licensed-win-1 only), matplotlib, numpy, PyYAML, git-based solver queue

**Machine topology:**
- dev-primary (this machine): planning, code, tests, job submission, post-processing
- licensed-win-1: OrcFxAPI execution (OrcaWave + OrcaFlex), polls queue every 30 min

---

## Current State Summary

### What works
- Solver queue: submit-job.sh → queue/pending/ → licensed-win-1 polls → queue/completed/
- 1 successful OrcaWave run (test01.owd, 7.8s)
- OrcaWave reporting module: src/digitalmodel/orcawave/reporting/
- OrcaFlex dat-to-yaml enrichment pipeline
- 20+ skills for OrcaWave/OrcaFlex sub-tasks
- Comprehensive OrcFxAPI reference: .claude/memory/orcawave-lessons.md

### What failed
- queue/failed/orcawave_001_ship_raos_rev2: "Input file not found" (bad path prefix)
- Parametric hull RAO batch pipeline: deferred (no batch submission)
- OrcaFlex frame analysis (#1264): not started
- 3-way benchmark (#29): synthetic results only, needs real solver runs

### Open issues (16 total OrcaWave/OrcaFlex related)
- Priority:high: #1264 (OrcaFlex frame), #569 (Vandiver damping, archived)
- Priority:medium: #24, #23, #21, #19, #1292, #29
- Priority:low: #22, #28, #20, #1464

---

## WAVE 1: Solver Queue Hardening + 3-Way Benchmark
**Issues:** #29 (3-way benchmark), queue infrastructure
**Duration:** ~2 hours
**Prerequisite for:** Waves 2 and 3

### Task 1.1: Fix the failed job path pattern

**Objective:** Diagnose and document the path resolution bug that caused orcawave_001_ship_raos_rev2 to fail

**Files:**
- Read: `queue/failed/20260401T005235Z-orcawave_001_ship_raos_rev2/result.yaml`
- Read: `queue/failed/20260401T005235Z-orcawave_001_ship_raos_rev2/20260401T005235Z-orcawave_001_ship_raos_rev2.yaml`
- Investigate: `digitalmodel/docs/domains/orcawave/` for actual file paths

**Steps:**
1. The failed job requested: `digitalmodel/docs/domains/orcawave/L01_aqwa_benchmark/orcawave_001_ship_raos_rev2.owr`
2. Note: `.owr` is an OUTPUT file, not input — likely should have been `.owd` or `.yml`
3. Verify what files actually exist in L01_aqwa_benchmark/
4. Document the correct path pattern in a comment on the job schema

**Verification:** Identify the correct input file path and confirm it exists

**Commit:** `fix(queue): document path resolution pattern for OrcaWave jobs`

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

## WAVE 2: Parametric Hull Form RAO Pipeline (#22)
**Issues:** #22 (Parametric hull form RAOs), #1319 (hull form parametric design)
**Duration:** ~3 hours
**Depends on:** Wave 1 (batch submission)

### Task 2.1: Design the parametric hull form input generator

**Objective:** Create a module that generates OrcaWave input YAML for hull form variations

**Files:**
- Create: `digitalmodel/src/digitalmodel/orcawave/parametric/__init__.py`
- Create: `digitalmodel/src/digitalmodel/orcawave/parametric/hull_generator.py`
- Test: `digitalmodel/tests/orcawave/test_parametric_hull.py`

**Design:**
```
Input: hull_params.yaml (ranges for L, B, T, Cb, Cw)
  → generate GDF meshes for each combination
  → generate OrcaWave YAML configs
  → output batch manifest for solver queue
```

**Parameters to vary:**
- Length (L): 100m, 150m, 200m, 250m, 300m
- Beam (B): ratios L/B = 5, 6, 7
- Draft (T): ratios T/B = 0.3, 0.4, 0.5
- Block coefficient (Cb): 0.6, 0.7, 0.8
- Frequency range: 0.1 to 2.0 rad/s (20 frequencies)
- Headings: 0, 45, 90, 135, 180 degrees

**TDD:** Write tests for mesh generation, YAML output, and parameter validation first.

**Commit:** `feat(orcawave): parametric hull form input generator (#22)`

---

### Task 2.2: Build RAO extraction and database module

**Objective:** Extract RAOs from completed OrcaWave .owr files into a queryable database

**Files:**
- Create: `digitalmodel/src/digitalmodel/orcawave/parametric/rao_database.py`
- Create: `digitalmodel/src/digitalmodel/orcawave/parametric/rao_extractor.py`
- Test: `digitalmodel/tests/orcawave/test_rao_database.py`

**Design:**
```python
# rao_extractor.py — runs on licensed-win-1 after solver completes
class RAOExtractor:
    def extract(self, owr_path: Path) -> RAOResult:
        """Extract 6-DOF RAOs, added mass, damping from .owr file."""
        # Uses OrcFxAPI.Diffraction().LoadResults()
        # Returns structured RAOResult dataclass

# rao_database.py — runs anywhere
class RAODatabase:
    def __init__(self, db_path: Path):  # YAML/JSON storage
    def add(self, hull_params: dict, rao_result: RAOResult)
    def query(self, L=None, B=None, T=None, Cb=None) -> List[RAOResult]
    def compare(self, results: List[RAOResult]) -> ComparisonReport
```

**Note:** rao_extractor.py requires OrcFxAPI (licensed-win-1 only). rao_database.py is pure Python.

**Commit:** `feat(orcawave): RAO extraction and database module (#22)`

---

### Task 2.3: Build client-facing RAO lookup and graph system

**Objective:** Generate polished RAO plots suitable for client deliverables

**Files:**
- Create: `digitalmodel/src/digitalmodel/orcawave/parametric/rao_plots.py`
- Create: `digitalmodel/src/digitalmodel/orcawave/parametric/rao_report.py`
- Test: `digitalmodel/tests/orcawave/test_rao_plots.py`

**Graph types:**
1. Single hull: 6-DOF RAO vs frequency for all headings (6 subplots)
2. Comparison: overlay RAOs for multiple hulls at same heading
3. Heatmap: peak RAO vs hull parameter (e.g., L vs Cb, colored by heave RAO)
4. Summary table: key statistics per hull form

**Styling:** Professional, client-facing. Clean axes, proper labels, engineering notation.

**Commit:** `feat(orcawave): client-facing RAO lookup and graph system (#22)`

---

### Task 2.4: Submit parametric batch and wire up post-processing

**Objective:** Generate and submit a starter batch of hull form variations

**Steps:**
1. Generate hull forms for a reduced matrix (e.g., 3 lengths × 2 beams × 2 drafts = 12 cases)
2. Create batch manifest
3. Submit via submit-batch.sh
4. Configure post-process-hook.py to auto-extract RAOs on completion

**Commit:** `feat(orcawave): submit parametric hull form batch (#22)`

---

## WAVE 3: OrcaFlex Frame Analysis (#1264, #1242)
**Issues:** #1264 (OrcaFlex frame), #1242 (WRK-5082 parent)
**Duration:** ~3 hours
**Depends on:** Wave 1 (queue infrastructure)

### Task 3.1: Gather frame geometry and section properties from WRK-5082

**Objective:** Extract the parachute frame geometry that the 2D solver already uses

**Files:**
- Read: `digitalmodel/` — find existing parachute_drag.py, frame_model.py, frame_solver.py
- Create: `digitalmodel/src/digitalmodel/solvers/orcaflex/frame_builder/__init__.py`
- Create: `digitalmodel/src/digitalmodel/solvers/orcaflex/frame_builder/geometry.py`

**Steps:**
1. Read the existing 2D frame_model.py to get node coordinates, member connectivity
2. Extract 4130 chromoly tube section properties (OD, wall thickness, EA, EI, GJ)
3. Create a geometry.py that defines the 3D frame in a solver-neutral format
4. Write tests validating against the 2D model values

**Commit:** `feat(orcaflex): frame geometry extraction from WRK-5082 (#1264)`

---

### Task 3.2: Build OrcaFlex .dat input generator for frame analysis

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

    def add_drag_force(self, force_n: float, attachment_point: str):
        """Apply static drag force at chute attachment point."""

    def generate_yaml(self) -> dict:
        """Generate OrcaFlex YAML input suitable for solver queue."""

    def generate_dat(self, output_path: Path):
        """Generate .dat file via OrcFxAPI (licensed-win-1 only)."""
```

**Load cases:**
- 200 MPH: F = from parachute_drag.py (existing calculation)
- 250 MPH: F = from parachute_drag.py (existing calculation)

**TDD:** Test YAML output structure, member count, section properties, boundary conditions.

**Commit:** `feat(orcaflex): frame model builder for parachute analysis (#1264)`

---

### Task 3.3: Build cross-tool comparison framework

**Objective:** Compare results from 2D direct stiffness, CalculiX FEM, and OrcaFlex

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
    def generate_report(self, output_dir: Path)  # HTML + plots + YAML
```

**Commit:** `feat(solvers): cross-tool comparison framework (#1264, #1242)`

---

### Task 3.4: Submit OrcaFlex frame jobs and configure post-processing

**Objective:** Submit the 200 MPH and 250 MPH frame analysis jobs

**Steps:**
1. Generate OrcaFlex input YAML for both load cases
2. Submit via solver queue (2 jobs)
3. Configure post-process-hook.py for OrcaFlex frame result extraction
4. Document expected output format for cross-tool comparison

**Commit:** `feat(orcaflex): submit parachute frame analysis jobs (#1264)`

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
- [ ] Solver queue: batch submission working, result watcher deployed
- [ ] Failed job diagnosed, resubmitted successfully
- [ ] Parametric hull form: 12+ hull variations submitted as batch
- [ ] RAO database module: extraction + storage + query tested
- [ ] Client-facing RAO plots: 4 graph types generated from test data
- [ ] OrcaFlex frame: model builder tested, 2 jobs submitted
- [ ] Cross-tool comparison: framework tested with 2D results as baseline
- [ ] Issues commented with progress: #22, #29, #1264, #1242

### Issue close criteria
- #29: Close when 3-way benchmark has real solver results compared
- #22: Close when parametric batch runs + RAO plots generated
- #1264: Close when OrcaFlex frame results extracted + compared to 2D/CalculiX
- #1242: Comment with progress on child 6 (OrcaFlex frame)
