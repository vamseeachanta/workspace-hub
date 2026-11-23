# Plan: WRK-597 Geotechnical Module — Phase Split, Skills, Package Adoption

## Context

WRK-597 defines a geotechnical module covering 5 sub-domains (foundations, piles,
anchors, on-bottom stability, soil models). Review identified it as too large for
a single WRK item and missing scour, settlement, and several standards. This plan:

1. Splits WRK-597 into 6 phased WRK items (WRK-618..623)
2. Defines package adoption strategy (groundhog, openpile, pygef, python-AGS4)
3. Creates 3 reusable skills for engineering module planning
4. Maps existing codebase calculations to integration points

WRK-597 becomes the umbrella tracker — done when all children complete.

---

## 1. Phased WRK Split

### Dependency Graph

```
WRK-618 (Soil Models)  ← foundation layer, no blockers
    ├── WRK-619 (Piles)          ← depends on 618
    ├── WRK-620 (On-Bottom Stability) ← depends on 618
    ├── WRK-621 (Foundations)    ← depends on 618
    ├── WRK-623 (Scour)         ← depends on 618
    └── WRK-622 (Anchors)       ← depends on 618 + 619
```

Phases 2–4 and 6 are parallelisable after Phase 1. Phase 5 needs Phase 2
(suction caisson reuses pile lateral methods).

---

### Phase 1 — WRK-618: Soil Models & Shared Types

**Title**: `feat(geotechnical): soil profile models, CPT correlation, shared types`
**Blocked by**: none
**Packages**: pygef (MIT), python-AGS4 (LGPL-3.0) — direct deps, safe
**Standards**: API RP 2GEO (soil characterisation), DNV-RP-C212 (soil mechanics)

**Deliverables**:
- `geotechnical/soil_models/models.py` — `SoilProfile`, `SoilLayer`, `CPTData`, `SoilType` dataclasses
- `geotechnical/soil_models/su_profile.py` — undrained shear strength profile
- `geotechnical/soil_models/cpt_correlation.py` — Robertson (1990/2009) Ic, Qt, su/σ'
- `geotechnical/soil_models/cyclic_degradation.py` — cyclic strength ratio curves
- `geotechnical/parsers/` — gef_reader.py (pygef), ags4_reader.py (python-AGS4), yaml_reader.py

**Validation**: Robertson CPT classification tables, API RP 2GEO Table 6.3.4-1

---

### Phase 2 — WRK-619: Pile Capacity

**Title**: `feat(geotechnical): pile axial/lateral capacity, p-y/t-z/q-z curves`
**Blocked by**: WRK-618
**Packages**: openpile (GPL-3.0, optional), groundhog (GPL-3.0, optional)
**Standards**: API RP 2GEO (Sec 6-8), DNV-RP-C212, API RP 2A-WSD (legacy)

**Deliverables**:
- `piles/axial_capacity.py` — API RP 2GEO driven piles (clay + sand)
- `piles/lateral_capacity.py` — p-y curves: Matlock (soft clay), Reese (stiff clay), API (sand)
- `piles/tz_qz_curves.py` — t-z / q-z soil springs
- `piles/pile_driving.py` — simplified Smith wave equation
- `piles/_openpile_adapter.py` — optional openpile wrapper

**Validation**: Reese & Van Impe (2001) p-y examples, Randolph & Gourvenec (2011)

**Note**: vertical_riser module (`vertical_riser_components.py` line 89-95) already
references `self.py_model_name = "p-y_" + self.geotechnical_application_type` and
loads from Excel. Phase 2 provides the canonical p-y implementation for migration.

---

### Phase 3 — WRK-620: On-Bottom Stability

**Title**: `feat(geotechnical): pipeline on-bottom stability per DNV-RP-F109`
**Blocked by**: WRK-618
**Packages**: none — entirely custom (no open-source F109 implementation exists)
**Standards**: DNV-RP-F109 (2021)

**Deliverables**:
- `on_bottom_stability/absolute_stability.py` — F109 Sec 3.3
- `on_bottom_stability/generalized_stability.py` — F109 Sec 3.4
- `on_bottom_stability/soil_resistance.py` — passive resistance, Coulomb (clay/sand)
- `on_bottom_stability/hydro_loads.py` — seabed pipeline Morison loads

**Integration**: `lateral_buckling.py` (line 52-61) currently uses constant
`friction_cfg["lateral_breakout_friction_coeff"]`. Phase 3 provides physically-derived
friction coefficients from soil properties to replace this. Also feeds WRK-478 (CP
anode sled OBS checks).

**Validation**: DNV-RP-F109 Appendix B design examples

---

### Phase 4 — WRK-621: Shallow Foundations

**Title**: `feat(geotechnical): shallow foundation bearing capacity (gravity base, mudmat)`
**Blocked by**: WRK-618
**Packages**: groundhog (GPL-3.0, optional — cross-validation only)
**Standards**: DNV-RP-C212 (Sec 5), ISO 19901-4, API RP 2GEO

**Deliverables**:
- `foundations/undrained_bearing.py` — Brinch Hansen general formula
- `foundations/drained_bearing.py` — Terzaghi/Meyerhof
- `foundations/mudmat_design.py` — iterative sizing for given load
- `foundations/gravity_base.py` — sliding, overturning, bearing checks

**Validation**: Brinch Hansen (1970) worked examples, DNV-RP-C212 examples

---

### Phase 5 — WRK-622: Anchor Capacity

**Title**: `feat(geotechnical): anchor capacity — drag, suction caisson, torpedo/SEPLA`
**Blocked by**: WRK-618 + WRK-619 (suction caisson reuses pile lateral methods)
**Packages**: none — all custom
**Standards**: DNVGL-RP-E301 (fluke/drag), DNV-RP-E303 (suction), API RP 2SK

**Deliverables**:
- `anchors/drag_anchor.py` — Neubecker-Randolph method
- `anchors/suction_caisson.py` — DNV-RP-E303 (vertical/horizontal/inclined)
- `anchors/torpedo_anchor.py` — torpedo/SEPLA simplified capacity
- `anchors/anchor_selection.py` — capacity vs soil type matrix

**Integration**: `mooring_analysis/models.py` line 56 — `AnchorProperties.holding_capacity`
is currently user-provided. Phase 5 provides `AnchorCapacity.compute()` to populate it.
`anchor_type` field already supports "drag", "suction", "pile", "driven_pile".

**Validation**: DNV-RP-E303 appendix, Vryhof Anchor Manual

---

### Phase 6 — WRK-623: Scour Prediction (NEW — not in original WRK-597)

**Title**: `feat(geotechnical): scour prediction per DNV-RP-F107`
**Blocked by**: WRK-618
**Packages**: none — custom
**Standards**: DNV-RP-F107

**Deliverables**:
- `scour/pipeline_scour.py` — F107 pipeline scour depth
- `scour/structure_scour.py` — monopile/jacket leg scour
- `scour/scour_protection.py` — rock dumping design

**Location rationale**: `geotechnical/scour/` not `pipeline/` because scour is a
soil erosion phenomenon applicable to pipelines, monopiles, jackets, and GBS equally.

**Validation**: Sumer & Fredsoe (2002), DNV-RP-F107 examples

---

### Deferred to Future WRK Items

| Topic | Reason | Suggested WRK |
|---|---|---|
| Settlement (elastic, consolidation) | Adds complexity; needs Phase 1+4 first | WRK-624 |
| Slope stability | Specialist sub-discipline; PySlope available | WRK-625 |
| ISO 19901-2 (Seismic design) | Separate domain | separate WRK |

---

## 2. Package Adoption Strategy

### License Compatibility

digitalmodel is MIT-licensed. GPL packages cannot be bundled.

| Package | License | Strategy | Phase |
|---|---|---|---|
| pygef | MIT | Direct dependency | 1 |
| python-AGS4 | LGPL-3.0 | Direct dependency | 1 |
| groundhog | GPL-3.0 | Optional extra only | 2, 4 |
| openpile | GPL-3.0 | Optional extra only | 2 |

### pyproject.toml Extras

```toml
[project.optional-dependencies]
geotechnical = ["pygef>=0.12", "python-AGS4>=0.4"]
geotechnical-gpl = ["groundhog>=0.12", "openpile>=1.0"]
```

### GPL Guard Pattern

All GPL packages use try/except import guards. Core calculations always work without them:

```python
try:
    import groundhog
    HAS_GROUNDHOG = True
except ImportError:
    HAS_GROUNDHOG = False
```

### Fallback Strategy

If any package is abandoned, only its thin wrapper file (`parsers/gef_reader.py`,
`piles/_openpile_adapter.py`, etc.) needs replacement. No core calculation code changes.

---

## 3. Skills to Create

### 3.1 `geotechnical-engineering` skill

**Path**: `.claude/skills/engineering/marine-offshore/geotechnical-engineering/SKILL.md`
**Purpose**: Domain expertise for geotechnical analysis planning

**Content**:
- Soil classification systems (USCS, Robertson CPT)
- Standard method selection: bearing capacity (Brinch Hansen, Terzaghi), pile capacity
  (API RP 2GEO), anchor capacity (Neubecker-Randolph, DNV-RP-E303)
- Decision tree: which method for which soil type and structure type
- Typical input parameter ranges (su, phi, gamma_sub, OCR, Nkt)
- Standard reference map with clause numbers
- digitalmodel module import paths and facade patterns

### 3.2 `engineering-package-evaluator` skill

**Path**: `.claude/skills/development/engineering-package-evaluator/SKILL.md`
**Purpose**: Reusable evaluation framework for any Python engineering package

**Content**:
- Evaluation checklist: license, maintenance (last commit, releases, issues), docs,
  tests, community (stars, JOSS publication)
- License decision tree: MIT/BSD/Apache → direct | LGPL → direct | GPL → optional only
- Dependency risk: single-maintainer, breaking changes, Python version support
- Integration patterns: thin wrapper, adapter, optional dependency
- Output template: structured YAML evaluation report

### 3.3 `standards-coverage-mapper` skill

**Path**: `.claude/skills/engineering/standards/standards-coverage-mapper/SKILL.md`
**Purpose**: Map standards implementation status across digitalmodel modules

**Content**:
- How to read/update `specs/capability-map/digitalmodel.yaml`
- Status taxonomy: `implemented` | `partial` | `reference` | `gap`
- Clause-level tracking: which equations/sections are coded
- Gap identification workflow: scan capability map → cross-ref WRK items
- Output: markdown table of standard vs implementation status

---

## 4. Existing Codebase Integration Map

### Existing Soil/Seabed Models (to reuse or align with)

| File | What exists | Geotechnical integration |
|---|---|---|
| `solvers/orcaflex/.../environment.py:29-56` | `SeabedStiffness(normal, shear)`, `Seabed(slope, stiffness, friction_coefficient)` | Align SoilProfile → OrcaFlex seabed mapping |
| `solvers/orcaflex/.../campaign.py:32-46` | `SoilVariation(stiffness, friction_coefficient, slope)` | Campaign soil variations should derive from SoilProfile |
| `structural/offshore_resilience/installation_checklist.py:38-48` | `HammerType`, `FoundationType` enums | Reuse enums in pile_driving.py |
| `subsea/pipeline/lateral_buckling.py:52-61` | `friction_cfg["axial_breakout_friction_coeff"]` | Phase 3 replaces with physically-derived values |
| `subsea/mooring_analysis/models.py:52-62` | `AnchorProperties(holding_capacity: float)` | Phase 5 computes this from soil conditions |
| `subsea/vertical_riser/vertical_riser_components.py:89-95` | `self.py_model_name`, Excel-based p-y loading | Phase 2 provides canonical p-y implementation |

### Capability Map Standards Status

| Standard | Current status in capability map | Phase |
|---|---|---|
| API RP 2GEO | `gap` (line 1463) | Phases 1-2 |
| DNV-RP-F109 | `gap` (line 3202) | Phase 3 |
| API RP 2SK | `gap` (line 2806) | Phase 5 |
| DNV-RP-C212 | not mapped | Phases 1-4 |
| DNV-RP-E303 | not mapped | Phase 5 |
| DNV-RP-F107 | not mapped | Phase 6 |
| ISO 19901-4 | not mapped | Phase 4 |
| DNVGL-RP-E301 | not mapped | Phase 5 |

---

## 5. Module Architecture

### Directory Structure

```
digitalmodel/src/digitalmodel/geotechnical/
    __init__.py
    soil_models/
        __init__.py
        models.py              # SoilProfile, SoilLayer, CPTData, SoilType
        su_profile.py          # Undrained shear strength
        cpt_correlation.py     # Robertson Ic, Qt, su/sigma'
        cyclic_degradation.py  # Cyclic strength ratio
    parsers/
        __init__.py
        gef_reader.py          # pygef wrapper
        ags4_reader.py         # python-AGS4 wrapper
        yaml_reader.py         # YAML soil profile loader
    piles/
        __init__.py            # PileCapacityAnalysis facade
        models.py
        axial_capacity.py
        lateral_capacity.py    # May split clay/sand if >400 lines
        tz_qz_curves.py
        pile_driving.py
        _openpile_adapter.py   # Optional
    on_bottom_stability/
        __init__.py            # OnBottomStability facade
        models.py
        absolute_stability.py
        generalized_stability.py
        soil_resistance.py
        hydro_loads.py
    foundations/
        __init__.py            # ShallowFoundation facade
        models.py
        undrained_bearing.py
        drained_bearing.py
        mudmat_design.py
        gravity_base.py
    anchors/
        __init__.py            # AnchorCapacity facade
        models.py
        drag_anchor.py
        suction_caisson.py
        torpedo_anchor.py
        anchor_selection.py
    scour/
        __init__.py            # ScourPrediction facade
        models.py
        pipeline_scour.py
        structure_scour.py
        scour_protection.py
```

### Pattern Reference

Follows facade + sub-calculator pattern from `free_span/__init__.py` (line 50-59):
- Each sub-module `__init__.py` exports a facade class
- `models.py` defines input/output dataclasses + enums
- Facade orchestrates sub-calculators in correct sequence
- All units SI, documented in field docstrings

---

## 6. Implementation Sequence

### Step 1: Update WRK-597 to umbrella status
- Change WRK-597 body to reference children WRK-618..623
- Set `compound: true`, add `children:` list

### Step 2: Create WRK-618..623 in `.claude/work-queue/pending/`
- Each with proper `blocked_by` per dependency graph
- Acceptance criteria include validation sources

### Step 3: Create 3 skills
- `geotechnical-engineering` — domain expertise
- `engineering-package-evaluator` — package evaluation framework
- `standards-coverage-mapper` — standards gap analysis

### Step 4: Update capability map
- Add missing standards (DNV-RP-C212, E303, F107, ISO 19901-4, DNVGL-RP-E301)
- Set all to `gap` status with planned WRK references

---

## 7. Verification

- [ ] WRK-597 updated as umbrella with children list
- [ ] 6 new WRK files (618-623) in `.claude/work-queue/pending/`
- [ ] Each WRK has: blocked_by, standards, packages, validation sources, acceptance criteria
- [ ] 3 skill SKILL.md files created
- [ ] Capability map updated with missing standards
- [ ] Legal scan passes on all new files
- [ ] Cross-review passes (Codex hard gate)

---

## Critical Files

- `digitalmodel/src/digitalmodel/subsea/pipeline/free_span/__init__.py` — facade pattern reference
- `digitalmodel/src/digitalmodel/subsea/mooring_analysis/models.py:52-62` — AnchorProperties integration
- `digitalmodel/src/digitalmodel/subsea/pipeline/lateral_buckling.py:52-61` — soil friction integration
- `digitalmodel/src/digitalmodel/subsea/vertical_riser/vertical_riser_components.py:89-95` — p-y migration
- `specs/capability-map/digitalmodel.yaml` — standards gap entries
- `.claude/work-queue/pending/WRK-597.md` — umbrella item to update
