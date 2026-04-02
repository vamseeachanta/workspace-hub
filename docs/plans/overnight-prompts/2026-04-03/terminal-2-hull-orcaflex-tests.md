# Terminal 2 — Hull/OrcaFlex Test Suite (Codex Seat 1)

We are in /mnt/local-analysis/workspace-hub. Execute these 4 tasks in order.
Use `uv run` for all Python — never bare `python3` or `pip`.
Commit to `main` and push after each task. Do not branch.
TDD: write tests before implementation; mock external dependencies (no network, no OrcaFlex license, no mounts).
Run `git pull origin main` before every push.
Do NOT ask the user any questions. Make reasonable decisions autonomously.

IMPORTANT: Do NOT write to any of the following paths — they are owned by other terminals:
- digitalmodel/src/digitalmodel/orcawave/, digitalmodel/tests/orcawave/ (Terminal 1)
- digitalmodel/tests/web/, digitalmodel/tests/field_development/, digitalmodel/tests/geotechnical/, digitalmodel/tests/nde/ (Terminal 3)
- scripts/document-intelligence/, data/document-index/ (Terminal 4)
- digitalmodel/src/digitalmodel/{web,reservoir,infrastructure,marine_ops,solvers,hydrodynamics,specialized,signal_processing}/ (Terminal 5 docstrings)
- config/cron/, scripts/cron/ (Terminal 5)

Only write to:
- digitalmodel/tests/parametric_hull/
- digitalmodel/tests/orcaflex/
- digitalmodel/tests/hydrodynamics/ (only new damping test files)

---

## TASK 1: Parametric Hull Analysis Test Suite — forward_speed (GH issue #1599, #1601)

### Context
- `digitalmodel/src/digitalmodel/naval_architecture/hull_library/` contains parametric hull analysis code
- Module `parametric_hull_analysis.py` (or similar) has forward_speed, shallow_water, passing_ship, charts functions
- These need comprehensive test coverage

### Steps
1. Read the parametric hull analysis source code to understand the API
2. Create test directory: `digitalmodel/tests/parametric_hull/`
3. Write: `digitalmodel/tests/parametric_hull/__init__.py`
4. Write: `digitalmodel/tests/parametric_hull/test_forward_speed.py`
   - Test: compute added resistance in waves for given hull + speed
   - Test: verify output structure (forces, moments, speed range)
   - Test: edge case — zero speed, very high speed
   - Test: multiple hull forms produce different results
5. Write: `digitalmodel/tests/parametric_hull/test_shallow_water.py`
   - Test: shallow water correction factors for given depth/draft ratio
   - Test: deep water limit returns unity corrections
   - Test: boundary conditions at critical depth
6. Run tests: `uv run pytest digitalmodel/tests/parametric_hull/ -v`

### Commit message
```
test(hull): parametric hull analysis tests — forward_speed + shallow_water (#1599, #1601)
```

---

## TASK 2: Parametric Hull Analysis Test Suite — passing_ship + charts (GH issue #1599, #1601)

### Steps
1. Write: `digitalmodel/tests/parametric_hull/test_passing_ship.py`
   - Test: compute passing ship interaction forces
   - Test: symmetric passing (equal vessels) → symmetric forces
   - Test: varying separation distance affects force magnitude
2. Write: `digitalmodel/tests/parametric_hull/test_charts.py`
   - Test: chart generation produces figure objects (mock matplotlib)
   - Test: RAO chart with correct axes labels and data series
   - Test: comparison chart with multiple hull forms
3. Run tests: `uv run pytest digitalmodel/tests/parametric_hull/ -v`

### Commit message
```
test(hull): parametric hull tests — passing_ship + charts (#1599, #1601)
```

---

## TASK 3: OrcaWave-to-OrcaFlex Integration Test (GH issue #1605)

### Context
- OrcaWave produces .owr result files with RAO data
- OrcaFlex imports vessel types from RAO data
- The integration test validates the handoff path

### Steps
1. Read `digitalmodel/src/digitalmodel/orcaflex/` to understand vessel type import
2. Read any existing OrcaWave→OrcaFlex bridge code
3. Write: `digitalmodel/tests/orcaflex/test_orcawave_integration.py`
   - Test: mock .owr file → extract RAOs → create OrcaFlex vessel type dict
   - Test: vessel type dict has required OrcaFlex keys (DisplacementRAOs, Name, etc.)
   - Test: frequency/heading arrays match between source and vessel type
   - Test: handle partial RAO data (missing headings) gracefully
4. Run tests: `uv run pytest digitalmodel/tests/orcaflex/test_orcawave_integration.py -v`

### Commit message
```
test(orcaflex): OrcaWave-to-OrcaFlex integration test — .owr export + RAO import (#1605)
```

---

## TASK 4: OrcaWave Damping-Sweep Test Suite (GH issue #1606)

### Context
- Viscous roll damping is a critical parameter in hydrodynamic analysis
- A damping sweep varies the damping coefficient across a range and measures response

### Steps
1. Read `digitalmodel/src/digitalmodel/hydrodynamics/` for damping-related code
2. Read OrcaWave spec handling of damping parameters in `input_schemas.py`
3. Write: `digitalmodel/tests/hydrodynamics/test_damping_sweep.py`
   - Test: generate damping sweep spec with range of roll damping values
   - Test: verify each sweep case produces distinct RAO results (mocked)
   - Test: convergence — halving sweep step size doubles number of cases
   - Test: output includes roll RAO sensitivity to damping coefficient
4. Run tests: `uv run pytest digitalmodel/tests/hydrodynamics/test_damping_sweep.py -v`

### Commit message
```
test(hydro): OrcaWave damping-sweep test suite — viscous roll damping parametric (#1606)
```

---

Post a brief progress comment on GH issues #1599, #1601, #1605, #1606 when each task completes.
