# OrcaWave Lessons Learned

## OrcFxAPI.Diffraction API
- Constructor: `OrcFxAPI.Diffraction(str(yml_path.resolve()), threadCount=4)`
- Must use absolute paths (`.resolve()`)
- `.Calculate()` runs the diffraction analysis
- `.SaveResults(str(path))` saves .owr file
- `.SaveData(str(path))` saves data file for reproducibility

## Result Extraction from .owr
```python
diffraction = OrcFxAPI.Diffraction()
diffraction.LoadResults(str(owr_path.resolve()))

# CRITICAL: frequencies are in Hz (NOT rad/s) and DESCENDING order!
freq_hz = np.array(diffraction.frequencies)        # 1D (nfreq,) Hz descending
frequencies = 2.0 * np.pi * freq_hz                # convert to rad/s
sort_idx = np.argsort(frequencies)                  # sort ascending
frequencies = frequencies[sort_idx]

headings = np.array(diffraction.headings)           # 1D (nhead,)

# RAOs: shape (nheading, nfreq, 6) — transpose then sort
raw = np.transpose(np.array(diffraction.displacementRAOs), (1, 0, 2))
raos = raw[sort_idx, :, :]                         # (nfreq, nhead, 6)
# Rotational DOFs (3,4,5) are in rad/m; convert to deg/m for AQWA compat

# Added mass / damping: sort by frequency
added_mass = np.array(diffraction.addedMass)[sort_idx]   # (nfreq, 6, 6)
damping = np.array(diffraction.damping)[sort_idx]        # (nfreq, 6, 6)
```

## OrcaWave Input YAML Gotchas
- When `qtf_calculation=false`, do NOT include:
  - `QTFMinCrossingAngle`
  - `QTFMaxCrossingAngle`
  - `PreferredQuadraticLoadCalculationMethod`
- These cause "Change not allowed" errors
- `QuadraticLoadPressureIntegration: No` is OK (explicitly disabling)

## AQWA v252 Workbench Format (RESOLVED)
- Column rulers at top (3 lines of `*`)
- Coordinate cards: I6 struct + I5 node + **9-space pad** + 3xF10 coords (50 chars total)
- DECK 1 ends with `END`, DECK 2 ends with `END` then `FINI`
- PMAS element required in ELM1 section: `     1PMAS        18(1)(98000)(98000)(98000)`
- NONE decks 9-20 needed: just `          NONE` (no banners, no END)
- Headings must span -180 to +180 for no-symmetry bodies
- WFS1 (DECK 7) and DRC1 (DECK 8) empty decks required
- Do NOT use GOON option (makes AQWA read beyond DECK 20)
- `displacementRAOs` shape from OrcFxAPI is `(nheading, nfreq, 6)` NOT `(nfreq, nheading, 6)`

## BEMRosetta
- Use `-mesh` mode (not `-bem`) for GDF mesh conversion
- Command: `BEMRosetta_cl.exe -mesh -i <gdf> -cg <x> <y> <z> -c <output.dat>`
- Must use absolute paths (`.resolve()`)

## OrcFxAPI.Diffraction — Complete Property Reference

### Constructor
```python
diff = OrcFxAPI.Diffraction(str(yml_path.resolve()), threadCount=4)  # load YAML
diff = OrcFxAPI.Diffraction()                                         # empty object
```

### Methods
| Method | Description |
|--------|-------------|
| `.Calculate()` | Run diffraction analysis |
| `.SaveResults(path_str)` | Save .owr results file |
| `.LoadResults(path_str)` | Load .owr results file |
| `.SaveData(path_str)` | Save .owd input file |
| `.LoadData(path_str)` | Load .owd input file |

### Result Properties (available after Calculate/LoadResults)
| Property | Shape / Type | Units | Notes |
|----------|-------------|-------|-------|
| `.frequencies` | `(nfreq,)` float | **Hz** | Descending order — sort ascending |
| `.headings` | `(nheading,)` float | degrees | Wave directions |
| `.displacementRAOs` | `(nheading, nfreq, 6N)` complex | m/m, rad/m | N=body count; rotational in rad/m |
| `.addedMass` | `(nfreq, 6N, 6N)` float | tonnes, t·m² | N=body count |
| `.damping` | `(nfreq, 6N, 6N)` float | tonnes/s | N=body count |
| `.infiniteFrequencyAddedMass` | `(6N, 6N)` float | tonnes | |
| `.loadRAOsDiffraction` | `(nheading, nfreq, 6N)` complex | kN/m | Excitation forces |
| `.hydrostaticResults` | list of dicts | — | Per-body stiffness, CoB, waterplane area |
| `.panelGeometry` | list of dicts | — | Per-panel: area (m²), centroid [x,y,z] (m), objectName |
| `.rollDampingPercentCritical` | float | % | |

### panelGeometry access pattern (list-of-dicts)
```python
panels = diff.panelGeometry
areas = np.array([p["area"] for p in panels])
centroids = np.array([p["centroid"] for p in panels])  # shape (N,3)
names = [p["objectName"] for p in panels]
```

- **Symmetry-expanded**: shows full physical geometry, not just GDF half/quarter mesh
- **Eliminates mesh_path resolution**: preferred over GDF loading for mesh schematics
- **Multi-body**: all bodies returned together; `objectName` distinguishes them

### Body count and indexing
```python
n_bodies = diff.addedMass.shape[1] // 6  # diff.bodyCount does NOT exist
r0, r1 = bi*6, bi*6+6
body_i_added_mass = diff.addedMass[:, r0:r1, r0:r1]     # self-coupling
cross_ij = diff.addedMass[:, bi*6:bi*6+6, bj*6:bj*6+6]  # cross-coupling
```

### Unit conversions for comparison
```python
omega = 2 * np.pi * np.array(diff.frequencies)  # Hz → rad/s
idx = np.argsort(omega)                           # sort ascending
raos_deg = np.degrees(np.abs(raos[:, :, 3:6]))  # rad/m → deg/m
```

### OrcaFlex Python API Reference
- Online: https://www.orcina.com/webhelp/OrcaFlex/ → Python scripting section
- Local (if installed): `C:/Program Files/Orcina/OrcaFlex/Help/OrcaFlex.chm`
