# Terminal 1: #1814 — Promote API RP 2GEO Alpha Method to digitalmodel/geotechnical/
# Agent: Claude (high-context, cross-referencing dark-intel YAML against existing code)
# Estimated: 2-3 hours
# Repo: digitalmodel (commit to main, push)

We are in /mnt/local-analysis/workspace-hub/digitalmodel.
Execute these tasks in order. Use `uv run` for all Python. Do NOT ask the user any questions.
Commit to main and push after each logical unit. TDD: write tests before implementation.

## Context

The dark-intelligence YAML archive at:
  /mnt/local-analysis/workspace-hub/knowledge/dark-intelligence/geotechnical/pile_capacity/dark-intelligence-api-rp-2geo-alpha-method.yaml

Contains the extracted API RP 2GEO alpha method for pile capacity in clay. It has:
- 3 equations (alpha factor, unit skin friction, total axial capacity)
- 5 inputs with typical ranges and test values
- 5 outputs with expected values and tolerances
- 1 worked example with exact input/output assertions
- Assumptions and validity bounds

The existing module at:
  src/digitalmodel/geotechnical/piles.py (234 LOC)

Already implements skin_friction_clay (alpha method), skin_friction_sand (beta method),
end_bearing_clay, end_bearing_sand, and axial_capacity. It has dataclass results.

Existing tests at:
  tests/test_geotechnical_piles.py
  tests/geotechnical/test_geotechnical.py

## TASK 1: Wire dark-intel worked examples as test assertions

Read the dark-intelligence YAML and existing piles.py. Write NEW tests in
tests/geotechnical/test_pile_capacity_dark_intel.py that:

1. Import the existing functions from digitalmodel.geotechnical.piles
2. Call skin_friction_clay with the YAML test inputs:
   - undrained_shear_strength_kpa=60.0
   - effective_overburden_kpa=150.0
3. Assert alpha approx 0.7906 (tolerance 0.001)
4. Assert unit_skin_friction_kpa approx 47.43 (tolerance 0.01)
5. Call axial_capacity with full inputs and assert:
   - skin_friction_kn approx 4470.56 (tolerance 0.5)
   - end_bearing_kn approx 424.12 (tolerance 0.5)
   - total_capacity_kn approx 4894.68 (tolerance 1.0)
6. Add input range validation tests:
   - pile_diameter_m in [0.3, 3.0]
   - pile_length_m in [10.0, 100.0]
   - undrained_shear_strength_kpa in [10.0, 200.0]

Run tests: `uv run pytest tests/geotechnical/test_pile_capacity_dark_intel.py -v`
Fix any failures by adjusting the code in piles.py if needed.

Commit: "test(geotechnical): wire API RP 2GEO alpha method dark-intel assertions (#1814)"

## TASK 2: Add input range validation to piles.py

Add validation functions to piles.py that raise ValueError for out-of-range inputs:
- validate_pile_inputs(pile_diameter_m, pile_length_m, su_kpa, sigma_v_kpa)
- Ranges from the dark-intel YAML: D in [0.3, 3.0], L in [10, 100], Su in [10, 200], sigma_v in [10, 500]
- Wire validation into skin_friction_clay and axial_capacity (optional validate=True param)
- Write tests for boundary values (at-boundary passes, just-outside fails)

Run: `uv run pytest tests/geotechnical/ -v`

Commit: "feat(geotechnical): add input range validation per API RP 2GEO spec (#1814)"

## TASK 3: Add pile_capacity.py with composite API

Create src/digitalmodel/geotechnical/pile_capacity.py that provides a higher-level API:
- `alpha_method_capacity(D, L, Su, sigma_v, Nc=9.0) -> PileCapacityResult`
  wrapping the existing lower-level functions into a single call
- PileCapacityResult dataclass with all intermediate and final values
- Multi-layer support: accept list of (thickness, Su, sigma_v) tuples for layered soils
- Write tests in tests/geotechnical/test_pile_capacity_composite.py

Run: `uv run pytest tests/geotechnical/ -v`

Commit: "feat(geotechnical): composite pile capacity API with multi-layer support (#1814)"

## TASK 4: Update standards-transfer-ledger

Update /mnt/local-analysis/workspace-hub/data/document-index/standards-transfer-ledger.yaml:
- Find the API-RP-2GEO entry and update status from "reference" to "implemented"
- Add implementation_path: "digitalmodel/src/digitalmodel/geotechnical/piles.py"
- Add test_path: "digitalmodel/tests/geotechnical/"

This file is in the workspace-hub repo, not digitalmodel. Commit separately:
  cd /mnt/local-analysis/workspace-hub
  git add data/document-index/standards-transfer-ledger.yaml
  git commit -m "chore(ledger): mark API RP 2GEO as implemented (#1814)"
  git push origin main

## TASK 5: Post progress comment on GH issue

  gh issue comment 1814 --repo vamseeachanta/workspace-hub --body "Overnight run completed:
  - Wired dark-intel worked examples as test assertions
  - Added input range validation per API RP 2GEO spec
  - Created composite pile_capacity.py with multi-layer support
  - Updated standards-transfer-ledger status to implemented
  All tests passing."

## IMPORTANT BOUNDARIES

Do NOT write to:
- digitalmodel/tests/structural/ (owned by Terminal 2)
- digitalmodel/tests/hydrodynamics/ (owned by Terminal 2)
- data/document-index/conference-* (owned by Terminal 3)
- data/document-index/dde-* (owned by Terminal 3)

Only write to:
- digitalmodel/src/digitalmodel/geotechnical/
- digitalmodel/tests/geotechnical/
- data/document-index/standards-transfer-ledger.yaml (workspace-hub repo, single edit)
