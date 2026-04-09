# Dossier: Drilling Rig Fleet Adapter — Issue #2062

| Field        | Value |
|--------------|-------|
| Issue        | #2062: feat(naval-arch): drilling rig fleet adapter — 2,210 rigs into hull form validation |
| Labels       | enhancement, cat:engineering, domain:code-promotion, agent:claude |
| Depends on   | #1859 (vessel fleet adapter pattern) — DONE; #1319 (hull form parametric design) — DONE |
| Dossier date | 2026-04-09 |

---

## 1. Current-State Findings

### 1.1 Files/Modules Already Present

| File | Status | Notes |
|------|--------|-------|
| `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py` | Partial | `normalize_drilling_rig_record()` (L233-262) exists; `register_fleet_vessels()` (L200-229) exists; `estimate_vessel_hydrostatics()` (L271-302) exists but uses single DEFAULT_CB=0.65 |
| `digitalmodel/src/digitalmodel/naval_architecture/hull_form.py` | Complete | `block_coefficient()`, `prismatic_coefficient()`, `midship_coefficient()`, `waterplane_coefficient()` all present (L21-67) |
| `digitalmodel/src/digitalmodel/naval_architecture/ship_dimensions.py` | Complete | `validate_vessel_entry()` (L97-139) requires hull_id, name, loa_ft, beam_ft, draft_ft; `merge_template_into_registry()` (L142-173) |
| `digitalmodel/src/digitalmodel/naval_architecture/__init__.py` | Partial | Already exports `normalize_drilling_rig_record` (L10) |
| `worldenergydata/data/modules/vessel_fleet/curated/drilling_rigs.csv` | Data source | 2,210 rows, 23 columns |
| `worldenergydata/src/worldenergydata/vessel_fleet/models/drilling_rig.py` | Complete | `DrillingRigEntry` dataclass with 40+ fields, rig type display maps |
| `worldenergydata/src/worldenergydata/vessel_fleet/schemas/drilling_rig.py` | Complete | Pydantic schema with HULL_FORM_TYPE, HULL_LIBRARY_REF fields |
| `worldenergydata/src/worldenergydata/vessel_fleet/bridge/rig_fleet_bridge.py` | Complete | Legacy BSEE format bridge |

### 1.2 Tests Already Present

| Test file | Class | Count | Coverage |
|-----------|-------|-------|----------|
| `digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py` | `TestNormalizeDrillingRigRecord` | 6 tests | Covers: full drillship (Deepwater Horizon), rig type/category preservation, water depth, missing name → None, partial rig, registration failure without draft |
| Same file | `TestEstimateVesselHydrostatics` | 4 tests | Covers: Thialf with displacement, DDG-51, missing displacement fallback, missing critical dims → None |
| Same file | `TestNormalizeFleetRecord` | 6 tests | Covers: full record, no displacement, partial record, empty name, metadata, sanity check |
| Same file | `TestRegisterFleetVessels` | 5 tests | Covers: batch register, skip invalid, skip empty name, no-overwrite, overwrite |
| `digitalmodel/tests/naval_architecture/test_hull_form.py` | Multiple | 10 tests | Covers: Cb, Cp, Cm, Cwp, displacement, Froude, Series 60, LCB |

### 1.3 Data Quality Analysis (drilling_rigs.csv)

| Rig Type | Count | Has LOA+BEAM | Has DRAFT | Has Displacement |
|----------|-------|--------------|-----------|------------------|
| jack_up | 1,009 | **0** | N/A (no column) | **0** |
| semi_submersible | 309 | 87 | N/A | **0** |
| drillship | 134 | 51 | N/A | **0** |
| platform_rig | 182 | ? | N/A | **0** |
| Others (wireline, lift_boat, etc.) | 576 | sparse | N/A | **0** |
| **Total** | **2,210** | **~143** | **0** | **0** |

**Critical data gaps:**
- **NO `DRAFT_M` column** in the CSV at all (23 columns listed; DRAFT_M is absent)
- **DISPLACEMENT_TONNES is 100% empty** across all 2,210 rows
- Jack-ups have zero geometric data (LOA/BEAM both empty for all 1,009)
- Only ~6.5% of records (143/2210) have any principal dimensions

### 1.4 Latest Relevant Commits

No direct commits referencing #2062 found. The adapter infrastructure was added as part of the #1859 vessel fleet adapter work. The `normalize_drilling_rig_record` function and its tests are present in the current codebase.

---

## 2. Remaining Implementation Delta

### 2.1 Exact Missing Behaviors

| # | Missing Behavior | Severity | Notes |
|---|-----------------|----------|-------|
| M1 | **Rig type → hull form mapping** | Critical | drillship→monohull, semi_submersible→twin-hull, jack_up→barge — no mapping constant exists anywhere in codebase |
| M2 | **Hull-form-specific Cb/Cm defaults** | Critical | `estimate_vessel_hydrostatics()` uses single DEFAULT_CB=0.65 for all vessel types; no per-hull-form coefficient tables |
| M3 | **Draft estimation from hull type** | Critical | CSV has no DRAFT_M; `validate_vessel_entry()` requires `draft_ft`; all rigs fail registration |
| M4 | **`register_drilling_rigs()` batch function** | High | Must call `normalize_drilling_rig_record` (not `normalize_fleet_record`); needs draft estimation to pass validation |
| M5 | **Cp computation from Cb/Cm** | Medium | `prismatic_coefficient()` exists in hull_form.py but never called from the rig adapter pipeline |
| M6 | **Coefficient range validation** | Medium | No function checks whether estimated Cb/Cm/Cp fall within published ranges for each rig type |
| M7 | **Integration pipeline test** | Medium | No test covers: CSV row → normalize → register → estimate hydrostatics → validate coefficients |

### 2.2 Exact File Paths That Must Change

| File | Change Type | Description |
|------|-------------|-------------|
| `digitalmodel/src/digitalmodel/naval_architecture/ship_data.py` | **Modify** | Add `_RIG_TYPE_HULL_FORM_MAP`, `_HULL_FORM_CB_DEFAULTS`, draft estimation logic, `register_drilling_rigs()` |
| `digitalmodel/src/digitalmodel/naval_architecture/hull_form.py` | **Modify** | Add `estimate_rig_hull_coefficients(rig_type, dims)` returning Cb/Cm/Cp with range validation |
| `digitalmodel/src/digitalmodel/naval_architecture/ship_dimensions.py` | **Possibly modify** | Relax `validate_vessel_entry()` to allow draft-less entries when draft can be estimated, OR add separate validation path |
| `digitalmodel/src/digitalmodel/naval_architecture/__init__.py` | **Modify** | Export new functions (`register_drilling_rigs`, `estimate_rig_hull_coefficients`) |
| `digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py` | **Modify** | Add tests for drilling rig batch registration, hull form coefficient validation |
| `digitalmodel/tests/naval_architecture/test_hull_form.py` | **Modify** | Add tests for rig-type-specific coefficient estimation and range validation |

---

## 3. TDD-First Execution Plan

### Phase 1: Failing Tests First

**Test file: `digitalmodel/tests/naval_architecture/test_hull_form.py`**

```python
class TestRigHullFormCoefficients:
    """Hull form coefficient estimation by drilling rig type."""

    def test_drillship_cb_in_range(self):
        """Drillships are monohulls: Cb typically 0.55-0.70."""
        from digitalmodel.naval_architecture.hull_form import estimate_rig_hull_coefficients
        coeffs = estimate_rig_hull_coefficients("drillship")
        assert 0.55 <= coeffs["cb"] <= 0.70

    def test_semi_submersible_cb_in_range(self):
        """Semi-subs are twin-hull: Cb typically 0.40-0.60 (low fullness)."""
        from digitalmodel.naval_architecture.hull_form import estimate_rig_hull_coefficients
        coeffs = estimate_rig_hull_coefficients("semi_submersible")
        assert 0.40 <= coeffs["cb"] <= 0.60

    def test_jack_up_cb_in_range(self):
        """Jack-ups are barges: Cb typically 0.75-0.90 (high fullness)."""
        from digitalmodel.naval_architecture.hull_form import estimate_rig_hull_coefficients
        coeffs = estimate_rig_hull_coefficients("jack_up")
        assert 0.75 <= coeffs["cb"] <= 0.90

    def test_all_types_have_cm_and_cp(self):
        from digitalmodel.naval_architecture.hull_form import estimate_rig_hull_coefficients
        for rig_type in ("drillship", "semi_submersible", "jack_up"):
            coeffs = estimate_rig_hull_coefficients(rig_type)
            assert "cm" in coeffs
            assert "cp" in coeffs
            assert 0 < coeffs["cp"] < 1

    def test_cp_equals_cb_over_cm(self):
        from digitalmodel.naval_architecture.hull_form import estimate_rig_hull_coefficients
        coeffs = estimate_rig_hull_coefficients("drillship")
        assert coeffs["cp"] == pytest.approx(coeffs["cb"] / coeffs["cm"], rel=1e-6)
```

**Test file: `digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py`**

```python
class TestRegisterDrillingRigs:
    """Batch registration of drilling rigs from CSV data."""

    def test_register_drillship_with_loa_beam(self):
        from digitalmodel.naval_architecture.ship_data import register_drilling_rigs
        records = [DEEPWATER_HORIZON_RIG]
        added, skipped = register_drilling_rigs(records)
        assert added == 1

    def test_register_semisub_with_loa_beam(self):
        from digitalmodel.naval_architecture.ship_data import register_drilling_rigs
        records = [SEMISUB_RIG]
        added, skipped = register_drilling_rigs(records)
        assert added == 1

    def test_skips_records_without_dimensions(self):
        from digitalmodel.naval_architecture.ship_data import register_drilling_rigs
        records = [PARTIAL_RIG_RECORD]  # has no LOA/BEAM
        added, skipped = register_drilling_rigs(records)
        assert added == 0
        assert skipped == 1

    def test_hull_form_mapped_after_registration(self):
        from digitalmodel.naval_architecture.ship_data import register_drilling_rigs, get_ship
        register_drilling_rigs([DEEPWATER_HORIZON_RIG])
        ship = get_ship("DEEPWATER HORIZON")
        assert ship is not None
        assert ship.get("hull_form") == "monohull"

    def test_hydrostatics_after_registration(self):
        from digitalmodel.naval_architecture.ship_data import (
            register_drilling_rigs, get_ship, estimate_vessel_hydrostatics,
        )
        register_drilling_rigs([DEEPWATER_HORIZON_RIG])
        ship = get_ship("DEEPWATER HORIZON")
        hydro = estimate_vessel_hydrostatics(ship)
        assert hydro is not None
        assert 0.05 < hydro["cb"] < 0.95
```

### Phase 2: Implementation Steps

1. **Add rig-type-to-hull-form mapping** in `ship_data.py`:
   ```python
   _RIG_TYPE_HULL_FORM_MAP = {
       "drillship": "monohull",
       "semi_submersible": "twin-hull",
       "jack_up": "barge",
       "inland_barge": "barge",
       "submersible": "twin-hull",
   }
   ```

2. **Add hull-form coefficient defaults** in `hull_form.py`:
   ```python
   _HULL_FORM_COEFFICIENTS = {
       "drillship":         {"cb": 0.62, "cm": 0.97, "hull_form": "monohull"},
       "semi_submersible":  {"cb": 0.50, "cm": 0.90, "hull_form": "twin-hull"},
       "jack_up":           {"cb": 0.82, "cm": 0.92, "hull_form": "barge"},
   }
   ```

3. **Add `estimate_rig_hull_coefficients(rig_type)`** in `hull_form.py`:
   - Lookup defaults from `_HULL_FORM_COEFFICIENTS`
   - Compute Cp = Cb / Cm
   - Return dict with cb, cm, cp, hull_form

4. **Add draft estimation logic** in `ship_data.py`:
   - Use L/D ratio heuristics: drillship ~15:1, semi-sub ~4:1, jack-up ~8:1
   - Or estimate from Cb if displacement is available: T = V / (Cb * L * B)
   - Fallback: draft = beam * 0.4 (common approximation)

5. **Add `register_drilling_rigs(records)`** in `ship_data.py`:
   - Normalize via `normalize_drilling_rig_record`
   - Estimate missing draft from hull type heuristics
   - Map rig_type → hull_form
   - Attach hull form coefficients
   - Merge into registry

6. **Update `__init__.py`** to export new functions.

### Phase 3: Verification Commands

```bash
# Run all naval architecture tests
uv run pytest digitalmodel/tests/naval_architecture/ -v

# Run only drilling rig adapter tests
uv run pytest digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py -v -k "drilling"

# Run hull form coefficient tests
uv run pytest digitalmodel/tests/naval_architecture/test_hull_form.py -v -k "Rig"

# Verify imports work
uv run python -c "from digitalmodel.naval_architecture import register_drilling_rigs, normalize_drilling_rig_record"

# Smoke test: load CSV and register
uv run python -c "
import csv
from digitalmodel.naval_architecture.ship_data import normalize_drilling_rig_record, register_drilling_rigs
with open('worldenergydata/data/modules/vessel_fleet/curated/drilling_rigs.csv') as f:
    rows = list(csv.DictReader(f))
print(f'Loaded {len(rows)} rigs')
added, skipped = register_drilling_rigs(rows)
print(f'Registered: {added}, Skipped: {skipped}')
"

# Verify coefficient ranges for registered rigs
uv run python -c "
from digitalmodel.naval_architecture.ship_data import list_ships, get_ship, estimate_vessel_hydrostatics
for hull_id in list_ships():
    ship = get_ship(hull_id)
    if ship and ship.get('vessel_category') == 'drilling':
        hydro = estimate_vessel_hydrostatics(ship)
        if hydro:
            print(f'{hull_id}: Cb={hydro[\"cb\"]:.3f}')
"
```

---

## 4. Risk/Blocker Analysis

### 4.1 Plan-Gate Blockers

| Blocker | Impact | Mitigation |
|---------|--------|------------|
| Issue #2062 not labeled `status:plan-approved` | Cannot implement | User must review this dossier and apply the label |
| No `status:plan-review` label on #2062 | Process compliance | Apply `status:plan-review` after dossier is reviewed |

### 4.2 Data/Source Dependencies

| Dependency | Status | Risk |
|-----------|--------|------|
| `drilling_rigs.csv` — no DRAFT_M column | **Blocking** | Must estimate draft from hull-type heuristics; L/D ratios are approximate |
| `drilling_rigs.csv` — DISPLACEMENT_TONNES 100% empty | **High risk** | Cb computation requires either displacement or hull-type defaults; cannot validate computed Cb against actual displacement |
| Jack-ups have zero LOA/BEAM data | **Medium** | 1,009 jack-ups will all be skipped; only 138 rigs (51 drillships + 87 semi-subs) can register with dimensions |
| No published Cb/Cm ranges for drilling rigs | **Medium** | Must use naval architecture literature estimates; reference: PNA Vol I, offshore platform design handbooks |

### 4.3 Merge/Contention Concerns

| Concern | Likelihood | Notes |
|---------|------------|-------|
| `ship_data.py` is touched by other fleet adapters | Medium | `normalize_fleet_record` and `register_fleet_vessels` are shared; new drilling-specific code should be additive only |
| `ship_dimensions.py` validation relaxation | Low-Medium | If draft requirement is relaxed for all vessels (not just rigs), it could let invalid non-rig records pass; recommend a separate validation path or rig-specific override |
| `hull_form.py` new functions | Low | Purely additive; no existing functions modified |
| Test file `test_vessel_fleet_adapter.py` | Low | Additive test classes; existing tests unchanged |

---

## 5. Architectural Decision: Draft Estimation Strategy

The CSV's missing DRAFT_M column is the single biggest implementation decision. Three options:

| Option | Approach | Pros | Cons |
|--------|----------|------|------|
| **A** | Estimate draft from L/D ratio heuristics per hull type | Simple, deterministic | Inaccurate for unusual vessels |
| **B** | Add DRAFT_M column to CSV (data curation) | Most accurate | Requires worldenergydata data pipeline work; blocks implementation |
| **C** | Relax validation to allow draft-less registration; estimate at hydrostatics time | Non-blocking | Registered vessels may lack critical dimensions; downstream consumers must handle |

**Recommendation: Option A** — Use hull-type-specific L/D heuristics as a fallback:
- Drillship: draft ≈ LOA / 15 (typical L/D ~14-16 for monohull drilling vessels)
- Semi-submersible: draft ≈ beam * 0.25 (pontoon draft relative to overall beam)
- Jack-up: draft ≈ LOA / 8 (barge hull, shallow draft)

These heuristics should be clearly marked as estimated values in the registry entry (e.g., `draft_estimated=True`).

---

## 6. Ready-to-Execute Implementation Prompt

```
IMPLEMENTATION PROMPT — Issue #2062
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Context: Implement the drilling rig fleet adapter for GitHub issue #2062.
Pre-requisite: Issue must be labeled status:plan-approved before execution.

Dossier: docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-2-drilling-rig-fleet-adapter.md

## What to implement

### 1. hull_form.py — Add rig-type hull coefficient estimation
File: digitalmodel/src/digitalmodel/naval_architecture/hull_form.py

Add a constant dict _HULL_FORM_COEFFICIENTS mapping rig types to default Cb, Cm values:
- drillship: Cb=0.62, Cm=0.97 (monohull, moderate fullness)
- semi_submersible: Cb=0.50, Cm=0.90 (twin-hull, low fullness)
- jack_up: Cb=0.82, Cm=0.92 (barge, high fullness)

Add function estimate_rig_hull_coefficients(rig_type: str) -> dict:
- Returns {"cb": float, "cm": float, "cp": float, "hull_form": str}
- cp = cb / cm
- Raises ValueError for unknown rig types

### 2. ship_data.py — Add rig registration pipeline
File: digitalmodel/src/digitalmodel/naval_architecture/ship_data.py

Add constant _RIG_TYPE_HULL_FORM_MAP:
- drillship → monohull
- semi_submersible → twin-hull
- jack_up → barge

Add function _estimate_draft(record: dict, rig_type: str) -> Optional[float]:
- drillship: draft_ft = loa_ft / 15
- semi_submersible: draft_ft = beam_ft * 0.25
- jack_up: draft_ft = loa_ft / 8
- Returns None if required dimensions missing

Add function register_drilling_rigs(records, *, overwrite=False) -> tuple[int, int]:
- Normalizes via normalize_drilling_rig_record
- Estimates draft if missing using _estimate_draft
- Maps rig_type → hull_form via _RIG_TYPE_HULL_FORM_MAP
- Attaches hull_form and draft_estimated flag
- Merges into registry via merge_template_into_registry
- Returns (added, skipped)

### 3. __init__.py — Export new functions
File: digitalmodel/src/digitalmodel/naval_architecture/__init__.py
- Add register_drilling_rigs and estimate_rig_hull_coefficients to imports and __all__

### 4. Tests — TDD first
File: digitalmodel/tests/naval_architecture/test_hull_form.py
- TestRigHullFormCoefficients: 5 tests (drillship Cb range, semi-sub Cb range, jack-up Cb range, all types have Cm/Cp, Cp=Cb/Cm identity)

File: digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py
- TestRegisterDrillingRigs: 5 tests (register drillship, register semi-sub, skip no-dims, hull_form mapped, hydrostatics after registration)

## Acceptance Criteria
1. Drilling rig adapter normalizes major fields (name, LOA, beam, draft-estimated, rig type)
2. Hull form coefficients for drillships: 0.55 <= Cb <= 0.70
3. Hull form coefficients for semi-subs: 0.40 <= Cb <= 0.60
4. Hull form coefficients for jack-ups: 0.75 <= Cb <= 0.90
5. Cp = Cb / Cm for all rig types
6. Tests cover drillship, semi-submersible, and jack-up with sanity checks

## Verification
uv run pytest digitalmodel/tests/naval_architecture/ -v
uv run pytest digitalmodel/tests/naval_architecture/test_vessel_fleet_adapter.py -v -k "drilling"
uv run pytest digitalmodel/tests/naval_architecture/test_hull_form.py -v -k "Rig"

## Cross-review requirement
After implementation, request cross-review per project_cross_review_policy.
Post summary comment on issue #2062 after completion.
```

---

## 7. Final Recommendation

### **READY AFTER LABEL UPDATE**

**Rationale:**
- The adapter infrastructure (#1859) is solidly in place with `normalize_drilling_rig_record()` and 6 unit tests
- The hull form coefficient module (#1319) has all required computation functions
- The CSV data source exists with 2,210 rows (though sparse on dimensions)
- The remaining work is well-scoped: ~3 new functions, ~10 new tests, modifications to 4 files
- The biggest risk (missing DRAFT_M column) has a clear mitigation path via hull-type heuristics
- No ambiguity in requirements: the issue body and acceptance criteria are specific

**To unblock implementation:**
1. Apply `status:plan-review` label to #2062
2. User reviews this dossier
3. Apply `status:plan-approved` label to #2062
4. Execute using the ready-to-execute prompt above

**Estimated registerable rigs after implementation:** ~138 of 2,210 (51 drillships + 87 semi-subs with LOA+BEAM; 0 jack-ups due to missing dimensions). Consider filing a follow-up issue for worldenergydata to enrich jack-up dimension data.
