# Terminal 3 — Fatigue Package TDD Expansion
# Provider: Codex seat 2 (bounded TDD implementation)
# Issues: #1676 (P0 fatigue expansion)
# Est. Time: 2-3 hours

We are in /mnt/local-analysis/workspace-hub. This is a Python monorepo with
`digitalmodel/` as a nested git repo (separate .git). All commits for
digitalmodel code MUST be made from inside `digitalmodel/`.

Use `uv run` for all Python — never bare `python3` or `pip`.
Do NOT ask the user any questions. Work autonomously.
Do NOT branch — commit to `main` and push after each task.
Run `git pull origin main --rebase` before every push (stash if needed).
TDD mandatory: write tests BEFORE implementation.
Mock all external dependencies — do NOT require network, licenses, or mounts.

IMPORTANT: Do NOT write to any of these paths (owned by other terminals):
- digitalmodel/src/digitalmodel/cathodic_protection/ (Terminal 1)
- digitalmodel/tests/cathodic_protection/ (Terminal 1)
- digitalmodel/src/digitalmodel/ansys/ (Terminal 2)
- digitalmodel/tests/ansys/ (Terminal 2)
- digitalmodel/src/digitalmodel/solvers/ (Terminal 5)
- digitalmodel/src/digitalmodel/web/ (Terminal 4)
- digitalmodel/src/digitalmodel/reservoir/ (Terminal 4)
- scripts/solver/ (Terminal 5)
- scripts/document-intelligence/ (Terminal 4)

Only write to:
- digitalmodel/src/digitalmodel/fatigue/
- digitalmodel/tests/fatigue/

---

## TASK 1: Fatigue — S-N Curve Library API (TDD)
GH Issue: #1676 (P0 — fatigue expansion, expose 221 S-N curves programmatically)

The fatigue package has 8 source files and 5 test files. It already has sn_curves.py
and sn_library.py. The roadmap calls for a proper API to expose all 221 curves.

### Existing source files to review first:
- digitalmodel/src/digitalmodel/fatigue/sn_curves.py
- digitalmodel/src/digitalmodel/fatigue/sn_library.py
- digitalmodel/src/digitalmodel/fatigue/damage.py

### Implementation:
1. Read existing sn_library.py and sn_curves.py to understand data structures
2. Write tests: `digitalmodel/tests/fatigue/test_sn_library_api.py`
   - Test listing all available curves (should find 221+)
   - Test lookup by standard (DNV-RP-C203, BS 7608, API RP 2A)
   - Test lookup by weld class (B, C, D, E, F, F2, G, W)
   - Test getting curve parameters (m1, m2, log_a1, log_a2, knee_point)
   - Test calculating fatigue life for given stress range
   - Test curve comparison (plot-data generation for multiple curves)
   - At least 10 test cases
3. Implement/extend: `digitalmodel/src/digitalmodel/fatigue/sn_library_api.py`
   - `list_curves(standard=None, weld_class=None) -> list[CurveInfo]`
   - `get_curve(name: str) -> SNcurve`
   - `calculate_endurance(curve: SNcurve, stress_range: float) -> float`
   - `compare_curves(names: list[str], stress_ranges: np.ndarray) -> ComparisonData`
   - `CurveInfo` and `SNcurve` Pydantic models
4. Verify: `cd digitalmodel && uv run pytest tests/fatigue/test_sn_library_api.py -v`

Commit message: `feat(fatigue): S-N curve library API — 221 curves exposed programmatically (#1676)`

---

## TASK 2: Fatigue — Hotspot Stress Methodology (TDD)
GH Issue: #1676 (P0 — DNV-RP-C203 hotspot stress)

### Implementation:
1. Write tests: `digitalmodel/tests/fatigue/test_hotspot_stress.py`
   - Test linear surface extrapolation (Type A hotspot)
   - Test through-thickness extrapolation (Type B hotspot)
   - Test read-out point spacing per DNV-RP-C203 Table 4-1
   - Test SCF (stress concentration factor) application
   - Test weld toe classification
   - At least 8 test cases
2. Implement: `digitalmodel/src/digitalmodel/fatigue/hotspot_stress.py`
   - `HotspotInput` Pydantic model (stress_at_points: dict, hotspot_type: str)
   - `extrapolate_hotspot_stress(input: HotspotInput) -> float` (Type A and B)
   - `get_readout_spacing(plate_thickness: float, hotspot_type: str) -> ReadoutConfig`
   - `apply_scf(nominal_stress: float, scf: float) -> float`
   - `classify_weld_toe(geometry: str) -> WeldClass`
3. Verify: `cd digitalmodel && uv run pytest tests/fatigue/test_hotspot_stress.py -v`

Commit message: `feat(fatigue): hotspot stress methodology per DNV-RP-C203 — TDD (#1676)`

---

## TASK 3: Fatigue — Stress Concentration Factor Library (TDD)
GH Issue: #1676 (P0 — SCF library)

### Implementation:
1. Write tests: `digitalmodel/tests/fatigue/test_scf_library.py`
   - Test tubular joint SCF (Efthymiou equations)
   - Test plate SCF (misalignment, angular)
   - Test butt weld SCF per DNV-RP-C203 Table A-5
   - Test fillet weld SCF
   - Test parametric range validation (beta, gamma, tau, theta bounds)
   - At least 8 test cases
2. Implement: `digitalmodel/src/digitalmodel/fatigue/scf_library.py`
   - `TubularJointParams` Pydantic model (beta, gamma, tau, theta, joint_type)
   - `calculate_tubular_scf(params: TubularJointParams) -> SCFResult` (Efthymiou)
   - `calculate_plate_scf(misalignment, angular, t) -> float`
   - `get_weld_scf(weld_type: str, class_: str) -> float`
   - `SCFResult` model (scf_chord, scf_brace, critical_location)
3. Update `digitalmodel/src/digitalmodel/fatigue/__init__.py` exports
4. Verify all fatigue tests: `cd digitalmodel && uv run pytest tests/fatigue/ -v`

Commit message: `feat(fatigue): SCF library with Efthymiou tubular joint equations — TDD (#1676)`

---

After all tasks, post a brief progress comment on GH issue #1676:
```
gh issue comment 1676 --repo vamseeachanta/workspace-hub --body "Terminal 3 overnight (2026-04-02): fatigue P0 expansion complete.
- Added sn_library_api.py — programmatic access to 221 S-N curves
- Added hotspot_stress.py — DNV-RP-C203 methodology
- Added scf_library.py — Efthymiou tubular joint SCFs
- All with TDD: 26+ new test cases
Fatigue package: 8 modules → 11 modules, 5 test files → 8 test files"
```
