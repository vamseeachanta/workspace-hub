---
name: orcawave-analysis-orcfxapi-result-extraction
description: 'Sub-skill of orcawave-analysis: OrcFxAPI Result Extraction (+3).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# OrcFxAPI Result Extraction (+3)

## OrcFxAPI Result Extraction


| Property | Gotcha | Fix |
|----------|--------|-----|
| `.frequencies` | Returns **Hz**, not rad/s | Multiply by `2 * np.pi` |
| `.frequencies` | Returns **descending** order | `np.argsort()` ascending before comparison |
| `.displacementRAOs` | Shape `(nheading, nfreq, 6)` | Transpose to `(nfreq, nheading, 6)` |
| Rotational RAOs (indices 3,4,5) | In **rad/m** | `np.degrees()` for deg/m (AQWA convention) |
| `.addedMass`, `.damping` | Follow frequency order | Apply same sort index as frequencies |

## Unit Conversion: WAMIT .frc → spec.yml


| Source | Mass Unit | Inertia Unit | Density | To spec.yml |
|--------|-----------|-------------|---------|-------------|
| WAMIT `.frc` (RHO=1) | te | te·m² | 1 te/m³ | ×1000 for kg, kg·m² |
| OrcaWave `.owd` | te | te·m² | 1 te/m³ | ×1000 for kg, kg·m² |
| spec.yml | kg | kg·m² | kg/m³ | — (canonical) |

**TRAP**: When porting from WAMIT `.frc` to spec.yml, multiply inertia by 1000 (te·m² → kg·m²). Do NOT multiply twice — the ISSC TLP case 2.5 had inertia tensors 1000× too large (8.02e13 vs correct 8.02e10) from double conversion.

## Phase Correlation for Zero-Magnitude DOFs


Fixed DOFs (e.g. heave/roll/pitch on TLPs) produce zero RAO magnitudes. Phase is undefined (`atan2(0,0)` noise), so:
- `multi_solver_comparator.py`: when `peak_mag < 1e-10`, overrides phase correlation to `r = 1.0`
- `validate_owd_vs_spec.py`: skips DOFs with `max_diff < 1e-6` in pass/fail verdict

## QTF Settings Guard


When `qtf_calculation: false` in spec.yml, do NOT include any QTF-related keys in the OrcaWave YAML:
- `QTFMinCrossingAngle`, `QTFMaxCrossingAngle`, `PreferredQuadraticLoadCalculationMethod`
- These cause "Change not allowed" errors from OrcaWave
- `QuadraticLoadPressureIntegration: No` is safe (explicitly disabling)

---
