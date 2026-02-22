# Plan: WRK-272 — DNV-RP-B401-2021 Offshore Platform CP Route

## Context

The `CathodicProtection` class in `digitalmodel` currently covers submarine pipelines
(DNV-RP-F103-2010) and ships/floating structures (ABS GN Ships 2018, ABS GN Offshore 2018).
Offshore **fixed platforms** — jacket structures, gravity-based structures, topsides steel — have
no implementation despite being the highest-value A&CE market use case.

DNV-RP-B401-2021 is the applicable standard and is available locally at
`acma-projects/B1522/ctr-2/cal/DNV-RP-B401-2021.pdf`. WRK-269 confirmed GO status for this
route. F103 defects G-1→G-5 were already fixed in a prior session (WRK-279 CP-stream).

F103-2016 standalone PDF is not available; the 2019 amended 2021 edition is present in
`doris/codes/`. F103-2016/2019 is deferred to a separate WRK item.

---

## Critical Files

| Role | Path |
|------|------|
| Main class (1806 lines) | `digitalmodel/src/digitalmodel/infrastructure/common/cathodic_protection.py` |
| F103 helpers (pattern to follow) | `digitalmodel/src/digitalmodel/infrastructure/common/cp_DNV_RP_F103_2010.py` |
| Comprehensive DNV tests (927 lines) | `digitalmodel/tests/marine_ops/marine_engineering/test_cathodic_protection_dnv.py` |
| ABS tests | `digitalmodel/tests/specialized/cathodic_protection/test_abs_cathodic_protection_calcs.py` |
| SKILL.md | `.claude/skills/engineering/marine-offshore/cathodic-protection/SKILL.md` |
| B401-2021 standard | `acma-projects/B1522/ctr-2/cal/DNV-RP-B401-2021.pdf` |
| Standards inventory | `digitalmodel/docs/domains/cathodic_protection/standards-inventory.md` |

---

## Implementation Plan

### Step 1 — TDD: Write tests first

Create `digitalmodel/tests/specialized/cathodic_protection/test_cathodic_protection_b401.py`.

Test classes in order (Red → Green cycle):

| Class | Tests |
|-------|-------|
| `TestB401CoatingBreakdown` | Linear formula f = f_ci + k×T; categories I–IV from B401-2021 Sec 3.4.6 |
| `TestB401CurrentDensities` | Zone lookup (submerged/splash/atmospheric) × temperature band; bare vs coated |
| `TestB401CurrentDemand` | Per-zone demand I = A × i_mean × f_c; total across zones |
| `TestB401AnodeResistance` | Dwight formula flush-mounted; modified Dwight stand-off; bracelet formula |
| `TestB401AnodeRequirements` | Mass M = (I_mean × T × 8760)/(ε × u); count N = M/m_a |
| `TestB401VerifyCurrentOutput` | N × I_a ≥ I_design check; flag if insufficient |
| `TestB401Router` | Router dispatches `"DNV_RP_B401_offshore"` key correctly |
| `TestB401Integration` | Full jacket platform end-to-end; known-answer validation |

Minimum 10 tests; target 20+.

---

### Step 2 — New helper module

Create `digitalmodel/src/digitalmodel/infrastructure/common/cp_DNV_RP_B401_2021.py`.

Following the `cp_DNV_RP_F103_2010.py` pattern exactly (private helper methods, class tables
as module-level constants).

**Module-level data tables (from B401-2021 Section 3.3 and 3.4):**

```python
# B401-2021 Table 3-1: Mean design current densities (A/m²) by zone and temperature
_B401_2021_CURRENT_DENSITIES = {
    "submerged": {
        "<=7":   {"coated": 0.040, "bare": 0.060},
        ">7-12": {"coated": 0.050, "bare": 0.080},
        ">12-17":{"coated": 0.060, "bare": 0.100},
        ">17":   {"coated": 0.070, "bare": 0.120},
    },
    "splash":      {"coated": 0.100, "bare": 0.200},  # Zone-only, temp-independent
    "atmospheric": {"coated": 0.010, "bare": 0.030},
}

# B401-2021 Table 3-2: Coating breakdown factors (f_ci, k) per category
_B401_2021_COATING_CATEGORIES = {
    "I":   {"f_ci": 0.05, "k": 0.020},  # High quality (≥300 μm epoxy)
    "II":  {"f_ci": 0.10, "k": 0.030},  # Anti-friction thin film (NEW 2021)
    "III": {"f_ci": 0.25, "k": 0.050},  # Standard quality
    "bare":{"f_ci": 1.00, "k": 0.000},  # No coating
}
```

**Helper methods:**
```python
def _b401_surface_areas(inputs) -> dict          # Sum zone areas; validate zones list
def _b401_coating_breakdown(inputs, design_life) # f_c = f_ci + k×T per zone
def _b401_current_densities(inputs)              # Table lookup by zone + temperature
def _b401_current_demand(inputs, areas, densities, breakdown) -> dict  # I per zone + total
def _b401_anode_resistance(inputs) -> float      # Dwight (flush/stand-off) or bracelet formula
def _b401_anode_requirements(inputs, current_demand) -> dict  # Mass + count
def _b401_verify_current_output(inputs, anode_req, resistance) -> dict  # Adequacy check
```

---

### Step 3 — New route method in cathodic_protection.py

Add to `CathodicProtection`:

```python
def DNV_RP_B401_offshore_platform(self, cfg):
    """Cathodic protection for offshore fixed platforms per DNV-RP-B401 (2021 edition).

    Covers jacket structures, gravity-based structures, and topsides steel.
    Anode types: flush-mounted, stand-off, bracelet.
    Zones: submerged, splash, atmospheric.
    """
    inputs = cfg.get("inputs", {})
    design_data = inputs.get("design_data", {})
    design_life = design_data.get("design_life", 25.0)

    areas           = _b401_surface_areas(inputs)
    breakdown       = _b401_coating_breakdown(inputs, design_life)
    densities       = _b401_current_densities(inputs)
    current_demand  = _b401_current_demand(inputs, areas, densities, breakdown)
    resistance      = _b401_anode_resistance(inputs)
    anode_req       = _b401_anode_requirements(inputs, current_demand)
    verification    = _b401_verify_current_output(inputs, anode_req, resistance)

    cfg["results"] = {
        "standard": "DNV-RP-B401-2021",
        "design_life_years": design_life,
        "surface_areas_m2": areas,
        "coating_breakdown": breakdown,
        "current_densities_A_m2": densities,
        "current_demand_A": current_demand,
        "anode_resistance_ohm": resistance,
        "anode_requirements": anode_req,
        "current_output_verification": verification,
    }
    return cfg
```

Add router case:
```python
elif cfg["inputs"]["calculation_type"] == "DNV_RP_B401_offshore":
    self.DNV_RP_B401_offshore_platform(cfg)
```

---

### Step 4 — cfg input structure (for SKILL.md and tests)

```python
cfg = {
    "inputs": {
        "calculation_type": "DNV_RP_B401_offshore",
        "design_data": {
            "design_life": 25.0,           # years
            "structure_type": "jacket",    # "jacket"|"gravity_based"|"topsides"
        },
        "structure": {
            "zones": [
                {"zone": "submerged",    "area_m2": 5000.0, "coating_category": "I"},
                {"zone": "splash",       "area_m2":  300.0, "coating_category": "III"},
                {"zone": "atmospheric",  "area_m2":  200.0, "coating_category": "I"},
            ]
        },
        "environment": {
            "seawater_temperature_C":  10.0,
            "seawater_resistivity_ohm_m": 0.30,
        },
        "anode": {
            "material":                   "aluminium",   # electrochemical capacity 2000 Ah/kg
            "type":                       "stand_off",   # "flush_mounted"|"stand_off"|"bracelet"
            "individual_anode_mass_kg":    200.0,
            "utilization_factor":          0.85,
            "length_m":                    1.0,          # for Dwight resistance formula
            "radius_m":                    0.05,
        }
    }
}
```

---

### Step 5 — Update SKILL.md

Add `DNV_RP_B401_offshore` to the routes table, include:
- Config example (above)
- Key outputs description
- Reference: DNV-RP-B401-2021 Sections 3.3, 3.4, 4.9

---

### Step 6 — F103-2016/2019 assessment (documentation only, no code)

Add a note to `standards-inventory.md`:
- F103-2016 standalone PDF not available
- F103-2019 amended 2021 is at `doris/codes/DNV-RP-F103 2019 amended 2021...pdf`
- Key delta from 2010: wet storage period, 200 m max spacing, polarization resistance
  attenuation model
- Recommend separate WRK item for `DNV_RP_F103_2019` route once scoped

---

## Verification

```bash
cd /mnt/local-analysis/workspace-hub
PYTHONPATH=digitalmodel/src python3 -m pytest \
  digitalmodel/tests/specialized/cathodic_protection/test_cathodic_protection_b401.py -v

# Regression — all existing CP tests must still pass
PYTHONPATH=digitalmodel/src python3 -m pytest \
  digitalmodel/tests/specialized/cathodic_protection/ \
  digitalmodel/tests/marine_ops/marine_engineering/test_cathodic_protection_dnv.py -v
```

Then cross-review:
```bash
scripts/review/cross-review.sh \
  digitalmodel/src/digitalmodel/infrastructure/common/cp_DNV_RP_B401_2021.py all
```

---

## Out of Scope

- ICCP (impressed current) — defer; no confirmed standard edition available
- F103-2016/2019 implementation — separate WRK item
- DNV-RP-F112 stainless steel HISC — separate WRK item
