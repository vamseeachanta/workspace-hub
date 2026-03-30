---
name: solver-benchmark-orcawave-via-orcfxapi
description: 'Sub-skill of solver-benchmark: OrcaWave (via OrcFxAPI) (+3).'
version: 2.0.0
category: engineering-utilities
type: reference
scripts_exempt: true
---

# OrcaWave (via OrcFxAPI) (+3)

## OrcaWave (via OrcFxAPI)


Critical data extraction gotchas:

| Property | Convention | Action Required |
|----------|-----------|-----------------|
| `.frequencies` | Returns **Hz** (NOT rad/s) | Multiply by `2 * pi` |
| `.frequencies` | Returns **descending** order | Sort ascending with `np.argsort()` |
| `.displacementRAOs` | Shape `(nheading, nfreq, 6)` | Transpose to `(nfreq, nheading, 6)` |
| `.displacementRAOs` | Rotational DOFs in **rad/m** | Convert to deg/m with `np.degrees()` for AQWA comparison |
| `.addedMass` / `.damping` | Same descending frequency order | Apply same sort index |


*See sub-skills for full details.*

## AQWA Standalone (Non-Workbench)


DAT file generation requirements:

| Setting | Requirement | Consequence if Wrong |
|---------|-------------|----------------------|
| Element type | `QPPL DIFF` (not `QPPL`) | Zero RAOs — "NON-DIFFRACTING" elements |
| ILID card | `ILID AUTO <group>` after ZLWL | "REGLID: NO DIFFRACTING ELEMENTS FOUND" |
| SEAG card | 2 parameters only: `SEAG (nx, ny)` | "FAILED TO READ SEA GRID PARAMETERS" |
| Line length | Max 80 columns | Delimiter read errors |
| Mesh quality | Panels ~square, facet radius check | FATAL error at 90° corners (non-overridable) |
| OPTIONS GOON | Continues past non-fatal errors | Does NOT override FATAL mesh quality |
| Heading range | -180 to +180 for no-symmetry bodies | Missing heading coverage |

## AQWA LIS File Parsing


| Pattern | Gotcha | Fix |
|---------|--------|-----|
| `ADDED  MASS` | Double space between words | Use whitespace normalization |
| Damping frequency | WAVE FREQUENCY line is ~23 lines before DAMPING header | Search backward 30 lines |
| Matrix rows | Separated by blank lines | Skip blank lines in row parsing |
| RAO section | First occurrence = displacement RAOs | Skip subsequent velocity/acceleration sections |
| Heading expansion | 5 input headings may produce 9 output (-180 to +180) | Filter to requested headings |

## BEMRosetta / Nemoh


| Aspect | Status | Notes |
|--------|--------|-------|
| BEMRosetta CLI | Mesh conversion only (`-mesh` mode) | Not a solver itself |
| Nemoh solver | Open source (GPL) | https://gitlab.com/lheea/Nemoh |
| Nemoh docs | Workshop tutorials | https://lheea.gitlab.io/Nemoh-Workshop/running-Nemoh.html |
| Integration | Future work | Nemoh backend adapter not yet implemented |
