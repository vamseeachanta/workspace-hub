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
