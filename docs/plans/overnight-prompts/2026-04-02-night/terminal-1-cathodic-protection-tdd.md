# Terminal 1 — Cathodic Protection Package TDD Expansion
# Provider: Claude (high-context synthesis + TDD)
# Issues: #1676 (P0 cathodic_protection expansion)
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
- digitalmodel/src/digitalmodel/ansys/ (Terminal 2)
- digitalmodel/tests/ansys/ (Terminal 2)
- digitalmodel/src/digitalmodel/fatigue/ (Terminal 3)
- digitalmodel/tests/fatigue/ (Terminal 3)
- digitalmodel/src/digitalmodel/solvers/ (Terminal 5)
- digitalmodel/src/digitalmodel/web/ (Terminal 4)
- digitalmodel/src/digitalmodel/reservoir/ (Terminal 4)
- scripts/solver/ (Terminal 5)
- scripts/document-intelligence/ (Terminal 4)

Only write to:
- digitalmodel/src/digitalmodel/cathodic_protection/
- digitalmodel/tests/cathodic_protection/
- digitalmodel/src/digitalmodel/cathodic_protection/examples/ (new dir OK)

---

## TASK 1: Cathodic Protection — Anode Sizing Calculator (TDD)
GH Issue: #1676 (P0 — cathodic_protection expansion, item 1)

The cathodic_protection package currently has 15 source files but only 4 test files.
Market signal: 131 jobs (Jacobs, HDR, Energy Transfer). This is a P0 priority gap.

### Existing source files to review first:
- digitalmodel/src/digitalmodel/cathodic_protection/dnv_rp_b401.py
- digitalmodel/src/digitalmodel/cathodic_protection/anode_depletion.py
- digitalmodel/src/digitalmodel/cathodic_protection/coating.py

### Implementation:
1. Read existing modules to understand patterns and data models
2. Write tests first: `digitalmodel/tests/cathodic_protection/test_anode_sizing.py`
   - Test sacrificial anode sizing per DNV-RP-B401
   - Test anode mass calculation given current demand and design life
   - Test anode resistance formulas (McCoy, Dwight)
   - Test multiple anode types (bracelet, stand-off, flush-mount)
   - At least 8 test cases with parametric edge cases
3. Implement: `digitalmodel/src/digitalmodel/cathodic_protection/anode_sizing.py`
   - `AnodeSizingInput` Pydantic model
   - `calculate_current_demand(surface_area, coating_breakdown, current_density)` 
   - `calculate_anode_mass(current_demand, design_life, utilization, capacity)`
   - `calculate_anode_resistance(anode_type, dimensions, resistivity)` — McCoy formula
   - `design_cp_system(input: AnodeSizingInput) -> AnodeSizingResult`
4. Verify all tests pass: `cd digitalmodel && uv run pytest tests/cathodic_protection/test_anode_sizing.py -v`

Commit message: `feat(cathodic_protection): anode sizing calculator per DNV-RP-B401 — TDD (#1676)`

---

## TASK 2: Cathodic Protection — Pipeline CP Design (TDD)
GH Issue: #1676 (P0 — pipeline CP per API RP 1169 / ISO 15589-1)

### Implementation:
1. Write tests first: `digitalmodel/tests/cathodic_protection/test_pipeline_cp.py`
   - Test pipeline current demand for bare vs coated pipe
   - Test anode spacing calculation for long pipelines
   - Test soil resistivity correction factors
   - Test CP potential criteria (-850 mV CSE, -950 mV for anaerobic)
   - At least 6 test cases
2. Implement: `digitalmodel/src/digitalmodel/cathodic_protection/pipeline_cp.py`
   - `PipelineCPInput` Pydantic model (pipe diameter, length, coating type, soil resistivity)
   - `calculate_pipeline_current_demand(pipe: PipelineCPInput) -> float`
   - `calculate_anode_spacing(total_demand, anode_output) -> float`
   - `check_potential_criteria(measured_potential, environment) -> CriteriaResult`
   - `design_pipeline_cp(input: PipelineCPInput) -> PipelineCPResult`
3. Verify: `cd digitalmodel && uv run pytest tests/cathodic_protection/test_pipeline_cp.py -v`

Commit message: `feat(cathodic_protection): pipeline CP design per API RP 1169 — TDD (#1676)`

---

## TASK 3: Cathodic Protection — Marine Structure CP Assessment (TDD)
GH Issue: #1676 (P0 — marine structure CP)

### Implementation:
1. Write tests first: `digitalmodel/tests/cathodic_protection/test_marine_cp.py`
   - Test offshore jacket CP assessment
   - Test seawater current density lookup by temperature and depth
   - Test calcareous deposit effects on current demand reduction
   - Test multi-zone CP design (splash zone, submerged, mudline)
   - At least 6 test cases
2. Implement: `digitalmodel/src/digitalmodel/cathodic_protection/marine_cp.py`
   - `MarineCPInput` Pydantic model (structure type, zones, water depth, temperature)
   - `get_seawater_current_density(temp, depth, calcareous=False) -> float`
   - `calculate_zone_demand(zone: Zone) -> float` for each zone type
   - `design_marine_cp(input: MarineCPInput) -> MarineCPResult`
3. Update `digitalmodel/src/digitalmodel/cathodic_protection/__init__.py` to export new modules
4. Verify all CP tests pass: `cd digitalmodel && uv run pytest tests/cathodic_protection/ -v`

Commit message: `feat(cathodic_protection): marine structure CP assessment — multi-zone TDD (#1676)`

---

After all tasks, post a brief progress comment on GH issue #1676:
```
gh issue comment 1676 --repo vamseeachanta/workspace-hub --body "Terminal 1 overnight (2026-04-02): cathodic_protection P0 expansion complete.
- Added anode_sizing.py with DNV-RP-B401 calculations
- Added pipeline_cp.py with API RP 1169 design
- Added marine_cp.py with multi-zone CP assessment
- All with TDD: 20+ new test cases
CP package: 15 modules → 18 modules, 4 test files → 7 test files"
```
