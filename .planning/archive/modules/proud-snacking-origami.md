# WRK-1155: Microgrid Controller — DER Dispatch, Island Detection, BESS Management

## Context

WRK-1155 is a child of WRK-1048 (power systems portfolio). It builds a rule-based microgrid
energy management controller as a greenfield `power/microgrid/` subpackage in digitalmodel.
This covers DER dispatch, islanding detection (IEEE 1547.4), BESS SOC management, and
mode transitions — key JD deliverables for power systems engineering roles.

## File Structure

**Source** (`digitalmodel/src/digitalmodel/power/microgrid/`):

| File | Contents | ~Lines |
|------|----------|--------|
| `models.py` | `MicrogridMode` enum, `DERType` enum, `DERAsset` dataclass, `MicrogridState` dataclass | 120 |
| `bess_controller.py` | `BESSController` — SOC management, charge/discharge rate, derating | 180 |
| `island_detector.py` | `IslandDetector` — ROCOF (linear regression), vector shift, trip logic | 180 |
| `microgrid_ems.py` | `MicrogridEMS` — merit-order dispatch, mode transitions, black start | 200 |
| `__init__.py` | Explicit re-exports + `__all__` | 50 |

Also: `power/__init__.py` (package marker) and update `digitalmodel/__init__.py` `__all__`.

**Tests** (`digitalmodel/tests/power/microgrid/`):

| File | Min Tests |
|------|-----------|
| `test_models.py` | 5 |
| `test_bess_controller.py` | 10 |
| `test_island_detector.py` | 9 |
| `test_microgrid_ems.py` | 11 |

## Key Algorithms

### ROCOF (IslandDetector.compute_rocof)
Linear regression over frequency samples: f(t) = a + bt → ROCOF = b [Hz/s].
Trip threshold: 1.0 Hz/s (IEEE 1547.4 §6.4). Normal grid <0.1 Hz/s.

### Merit-Order Dispatch (MicrogridEMS.merit_order_dispatch)
Sort available DERs by (dispatch_priority asc, marginal_cost asc).
Dispatch sequentially until load met. BESS constrained by SOC via BESSController.
Report unserved load and curtailment (island mode only).

### SOC Management (BESSController.compute_power_setpoint)
Clamp to max discharge/charge. Linear derating in last 5% above SOC_MIN (prevents
control oscillation). Island mode reserves extra 20% SOC headroom.

## Implementation Order (TDD)

1. **Phase 1 — models.py**: Enums + dataclasses, `__post_init__` validation (5 tests)
2. **Phase 2 — bess_controller.py**: BESSParams/State, max rates, setpoint, SOC update (10 tests)
3. **Phase 3 — island_detector.py**: ROCOF, vector shift, detect/trip (9 tests) — parallel with Phase 2
4. **Phase 4 — microgrid_ems.py**: Merit-order, transitions, black start, update loop (11 tests)
5. **Phase 5 — Package wiring**: `__init__.py` exports, import verification

## Test Plan Highlights

| Test | Type | Key assertion |
|------|------|---------------|
| `test_rocof_declining_frequency` | Happy | 60→59 Hz over 1s = -1.0 Hz/s |
| `test_vector_shift_wraps_at_180` | Edge | 350→10 deg = 20 deg, not 340 |
| `test_max_discharge_derates_near_soc_min` | Edge | SOC 0.12 → ~40% max power |
| `test_merit_order_dispatches_cheapest_first` | Happy | PV (priority 1) before GENSET (priority 3) |
| `test_black_start_requires_minimum_soc` | Error | SOC <0.30 → ValueError |
| `test_update_triggers_island_on_detection` | Integration | ROCOF trip → mode transition |

## Verification

```bash
# Run all microgrid tests
PYTHONPATH=src uv run python -m pytest tests/power/microgrid/ -v

# Verify import
PYTHONPATH=src uv run python -c "from digitalmodel.power.microgrid import MicrogridEMS, IslandDetector, BESSController, MicrogridMode"

# Run full digitalmodel suite (no regressions)
PYTHONPATH=src uv run python -m pytest --tb=short -q
```

## Reference Patterns
- Module init: `digitalmodel/src/digitalmodel/cathodic_protection/__init__.py`
- Docstrings: NumPy style with IEEE 1547.4 section references
- Tests: `pytest.approx()` for floats, class-grouped, `test_<what>_<scenario>_<outcome>`

## No Scripts Needed
All operations are one-time file creation in a single TDD session. No reusable scripts required (below 25% recurrence threshold).
