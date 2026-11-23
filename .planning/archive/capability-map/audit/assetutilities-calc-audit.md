# assetutilities Calculation Audit

Generated: 2026-03-13 | WRK-1179 Stream B Task 3

## Summary Statistics

| Metric | Count |
|--------|-------|
| Calculation modules | 12 |
| Public calc functions | 80 |
| Public calc classes | 4 |
| Constants module items | ~30 |
| Steel grades (materials.py) | 11 |
| Unit conversion functions | 27 |
| Unit domains | 2 (energy, metocean) |
| Seawater property functions | 3 |
| Tests passed | 855 |
| Tests skipped | 9 |

## Calculation Modules (12)

### calculations/casing_pipe.py (10 funcs, 3 classes)
API 5C3 / ISO TR 10400 casing and tubing pipe strength.
- Burst, collapse, tensile ratings for OCTG

### calculations/drilling_riser.py (10 funcs)
Deepwater drilling riser analysis from OTC literature.
- Gardner 1982 tension, Kim 1975 frequency, Grant 1977 fairing
- Vandiver 1985 lock-in, Miller 1985 mud pressure, Imas SCR

### calculations/drilling_riser_integrity.py (7 funcs)
Deep water drilling riser integrity per AMJIG Rev 1/2 (1998-2000).
- Inspection guidelines per rpt001-3 Part 1 (Nov 1997)

### calculations/lifecycle_cost.py (7 funcs)
Life cycle costing per BS15663 Part 2 (2001).
- Marine transportation cost modelling per O&G Marine Transportations 0030-4

### calculations/pipeline_dnv.py (5 funcs)
DNV OS-F101 submarine pipeline LRFD design checks.
- Burst pressure, local buckling, von Mises stress, buckle arrest

### calculations/polynomial.py (1 func, 1 class)
General polynomial evaluation utility.

### calculations/riser_array.py (4 funcs)
Riser array design per BP Guidelines v2.
- Equivalent diameter, de-equivalencing, shadow factor, spacing

### calculations/riser_dynamics.py (7 funcs)
Riser dynamics: tow-out, VIV, damping, residual strength.
- Methods from Huse, Norton, Vandiver, Smith, TNE guidelines

### calculations/riser_viv.py (9 funcs)
Riser VIV and hydrodynamics for offshore pipeline/riser.
- Drag, vortex shedding, lock-in, VIV amplitude, fatigue, effective tension

### calculations/scr_fatigue.py (6 funcs)
Steel Catenary Riser fatigue for deepwater.
- Allen 1995 VIV, Brooks 1987 screening, KC number, TDZ fatigue

### calculations/tlp_well_system.py (6 funcs)
TLP well system and riser engineering.
- Javanmardi 1995, Fox 1995, Larimore 1998, Carminati 1999, Barton 1999

### calculations/wellhead_fatigue.py (8 funcs)
Wellhead and conductor fatigue from OTC literature.
- Chen 1989 S-N, Sweeney 1991 HPHT, Allen 1998 VIV, Denison 1997 Mars TLP

## Constants and Material Properties

### Engineering Constants (constants/__init__.py)
- **Physical**: G (9.81), G_PRECISE (9.80665), STD_ATMOSPHERE_KPA
- **Fluid**: RHO_SEAWATER (1025), RHO_FRESHWATER (1000), RHO_CRUDE_OIL range
- **Steel**: E_STEEL (207 GPa), NU_STEEL (0.30), RHO_STEEL (7850), ALPHA_STEEL, G_STEEL
- **Yield strengths**: FY_A36, FY_A572_GR50, FY_X42/X52/X60/X65/X70/X80
- **Concrete**: RHO_CONCRETE_NORMAL (2400), RHO_CONCRETE_MARINE (2250)
- **Offshore**: SEAWATER_PRESSURE_GRADIENT, wave heights (GoM/North Sea), surge/tide

### Steel Grades (constants/materials.py)
SteelGrade frozen dataclass with SMYS, SMUS, reference.
- **API 5L pipeline**: X42, X52, X60, X65, X70, X80 (6 grades)
- **ASTM structural**: A36, A572 Grade 42/50/60/65 (5 grades)
- Public registry via `STEEL_GRADES` dict and `get_steel_grade()` lookup

### Seawater Properties (constants/seawater.py)
- `seawater_density(temp_c, salinity_ppt)` -- UNESCO 1980 / IES 80
- `seawater_dynamic_viscosity(temp_c, salinity_ppt)` -- ITTC 2011
- `seawater_kinematic_viscosity(temp_c, salinity_ppt)` -- derived mu/rho

## Unit Conversion Coverage

### Direct Conversions (constants/conversions.py) -- 27 functions
| Category | Functions | Coverage |
|----------|-----------|----------|
| Pressure | psi/mpa, bar/mpa, kpa/psi (6) | Good |
| Length | ft/m, inch/mm (4) | Basic |
| Force | n/kn, n/lbf, kn/kip (6) | Good |
| Mass | kg/lb, kg/tonne, tonne/short_ton (6) | Good |
| Temperature | C/F, C/K (4) | Good |
| Offshore | depth_to_pressure_kpa (1) | Basic |

### Pint-based Unit System (units/)
Full pint-backed TrackedQuantity with provenance tracking:
- **Energy domain**: BOE, MCF, MMCF, BCF, TCF, SCF, MMBTU, therm, TOE + volume/mass units (25 mappings)
- **Metocean domain**: speed (5 units), length (7 units), temperature (3 units), pressure (8 units)
- **TrackedQuantity**: unit-aware values with full provenance/audit trail
- **CalculationAuditLog**: aggregated audit trails across calculations
- **UnitSystemPolicy**: SI/Imperial policy enforcement
- **unit_checked decorator**: automatic unit validation on function inputs/outputs

## Common Utilities (common/)

### Data Handling
- data.py (67 funcs, 16 classes) -- DataFrame operations, transformations
- database.py (41 funcs, 1 class) -- database connectivity
- data_management.py (5 funcs) -- data pipeline management
- yml_utilities.py (24 funcs) -- YAML read/write/merge
- saveData.py (10 funcs, 4 classes) -- output serialization

### Visualization
- visualization.py (17 funcs) -- plotting utilities
- visualizations.py (25 funcs) -- extended visualization
- visualization/ subpackage: xy, polar, common, templates (matplotlib + plotly)

### File Management
- file_management.py (8 funcs) -- file operations
- file_edit.py, file_edit_concatenate.py, file_edit_split.py -- file editing

### Other
- ApplicationManager.py (15 funcs) -- application lifecycle
- cli_parser.py (4 funcs) -- CLI argument parsing
- validation.py (3 funcs) -- input validation
- text_analytics.py (2 funcs) -- text processing
- reportgen/ subpackage -- document generation

## Identified Gaps

### HIGH Priority
1. **No shared interpolation helpers** -- no linear/spline interpolation utility; calculations likely use numpy directly without a shared wrapper
2. **No numerical integration helpers** -- no trapezoidal/Simpson's rule wrapper for fatigue damage accumulation
3. **Missing API 5CT casing grades** -- materials.py has API 5L pipe and ASTM structural but no API 5CT OCTG grades (J55, K55, N80, L80, P110) despite casing_pipe.py existing
4. **No angle conversions** in conversions.py -- degrees/radians missing (though math.radians exists)

### MEDIUM Priority
5. **No area/moment of inertia helpers** -- pipe cross-section geometry (area, I, Z, S) not in shared utils; likely duplicated in calculation modules
6. **No density unit conversions** -- kg/m3 to lb/ft3, lb/gal missing from conversions.py
7. **No flow rate conversions** -- bbl/d, m3/hr, gpm not in conversions.py
8. **Limited length conversions** -- no miles, yards, nautical miles in conversions.py (available via pint metocean domain though)
9. **No S-N curve library** -- wellhead_fatigue.py and scr_fatigue.py likely each define their own S-N curves; could be shared

### LOW Priority
10. **No concrete material grades** -- only densities, no fck/fc' values
11. **No soil properties** -- no shared clay/sand undrained shear strength, friction angle constants
12. **Polynomial module is minimal** -- single class, no documentation of standards

## Test Coverage

- **855 tests passed**, 9 skipped (benchmark tests)
- All 12 calculation modules have dedicated test files in `tests/calculations/`
- Test counts per module range from 23 (riser_array) to 57 (drilling_riser)
- py.typed PEP 561 marker present; mypy clean on contracted API
