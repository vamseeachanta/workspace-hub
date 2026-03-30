# BEMRosetta Evaluation — Hydrodynamic Coefficient QA Tool

**Date:** 2026-03-29
**Issue:** vamseeachanta/workspace-hub#1490
**Evaluated by:** Research agent (web-only, no installation)

---

## Summary

BEMRosetta is a mature open-source tool (C++, Windows/Linux) for viewing, comparing, and converting BEM hydrodynamic coefficients across virtually all major solver formats, including Capytaine's native `.nc` output. It ships a GUI, a CLI binary, a DLL library, and Python glue code, making headless/scripted use feasible. For the Capytaine pipeline it adds value primarily as a format bridge and visual QA layer, but it does not replace Capytaine's own xarray-native post-processing for custom analysis.

---

## Format Support Matrix

| Format | Read | Write | Notes |
|---|---|---|---|
| WAMIT (.1 .3 .4 .7 .8 .9 .hst .out …) | Yes | Yes | Most complete coverage |
| Capytaine (.nc NetCDF) | Yes | No | Read only; confirmed in README |
| Nemoh (.cal, .tec, .dat) | Yes | Yes | Full case I/O including folder structure |
| HAMS (ControlFile.in) | Yes | Yes | Full case I/O |
| ANSYS AQWA (.lis, .ah1, .qtf) | Yes | Yes (.qtf) | Partial write |
| OrcaFlex/OrcaWave (.yml, .owr) | Yes | No | Requires OrcaWave installed to read .owr |
| Bemio HDF5 (.h5) | Yes | Yes | OpenFAST ecosystem bridge |
| OpenFAST HydroDyn.dat | Yes | Yes | Direct OpenFAST integration |
| Hydrostar (.out) | Yes | No | Read only |
| Diodore (.hdb) | Yes | Yes | |
| FOAMM / MATLAB (.mat) | Yes | Yes | State-space model export |

**Capytaine .nc caveat:** BEMRosetta reads Capytaine `.nc` files; there are known compatibility edge cases with complex-index formatting in newer Capytaine versions (reported in WEC-Sim#875). Confirm against Capytaine 2.3.1 output before relying on this path.

---

## Headless Usage Assessment

BEMRosetta ships three non-GUI interfaces:

1. **CLI binary** — documented as a "command line version"; enables batch format conversion and case generation without opening the GUI. Exact flags not publicly documented outside the repo; review `other/test/` folder for usage patterns.
2. **DLL library** — embeddable in other C++ tools.
3. **Python glue code** — wraps the DLL; allows scripted load/convert/save workflows from Python. No published `pip` package; requires local build or pre-built binary bundle. API surface is thin — load a file, access coefficient arrays, save to another format.

**Assessment:** Headless use is supported but not polished. The Python bindings are glue-level (not a full SDK), and the CLI lacks published documentation. Scripted format conversion (e.g., Capytaine .nc → WAMIT for OpenFAST) is the strongest headless use case.

---

## QA Capabilities

| Feature | Available |
|---|---|
| Added mass (A) plots vs frequency | Yes |
| Radiation damping (B) plots vs frequency | Yes |
| Excitation force (Froude-Krylov + diffraction) plots | Yes |
| Cross-solver comparison overlays | Yes — primary differentiator |
| Irregular frequency removal (post-processing) | Yes |
| Force symmetrization (heading averaging) | Yes |
| Hydrostatic stiffness matrix display | Yes |
| Mesh viewing and healing | Yes |
| Time-domain simulation viewer (OpenFAST, AQWA Naut, CSV) | Yes |
| State-space (radiation convolution) via FOAMM | Yes |

---

## Comparison: BEMRosetta vs Capytaine Post-Processing

| Criterion | BEMRosetta | Capytaine native (xarray/Python) |
|---|---|---|
| Coefficient plots | GUI-based, multi-solver overlay | Custom matplotlib scripts, single-solver |
| Format conversion | Built-in, broad coverage | Export via `to_netcdf`; no WAMIT/HAMS writer |
| Irregular freq removal | Built-in GUI tool | Not built-in; manual filtering |
| Scripting flexibility | Limited (thin Python glue) | Full xarray/numpy access |
| CI/CD integration | Awkward (binary dependency, no pip) | Natural (pure Python, pip-installable) |
| Cross-solver QA | Strong — explicit feature | Not applicable |
| Maintenance | Active, C++ binary releases | Very active, Python ecosystem |

**Key gap BEMRosetta fills:** converting Capytaine `.nc` output to WAMIT format for OpenFAST HydroDyn, and visual cross-solver QA (e.g., Capytaine vs HAMS vs WAMIT on the same plot).

**What it does not replace:** Capytaine's own post-processing for custom RAO analysis, wave spectrum integration, or anything requiring direct xarray dataset manipulation.

---

## Recommendation

**Defer** — with a targeted integration path defined.

BEMRosetta is the right tool for two specific tasks: (1) converting Capytaine `.nc` output to WAMIT/HydroDyn format for OpenFAST pipelines, and (2) visual cross-solver QA sanity checks. However, the Python bindings are not pip-installable, the Capytaine `.nc` compatibility has known edge cases with recent versions, and the CLI lacks published documentation. Defer full adoption until:

- The Capytaine 2.3.1 `.nc` compatibility is confirmed against a live test case.
- A wrapper script or Makefile target encapsulating the CLI conversion step is established.
- The need for cross-solver visual QA is driven by an actual project deliverable.

For immediate needs, Capytaine's native xarray post-processing plus custom matplotlib scripts covers the QA use case with zero binary dependencies.

---

## One-Liner Verdict

BEMRosetta is the best open-source tool for BEM format conversion and cross-solver visual QA, but its Python integration is glue-level and Capytaine .nc compatibility needs validation — defer until a concrete OpenFAST pipeline conversion need drives adoption.

---

## References

- [BEMRosetta GitHub](https://github.com/BEMRosetta/BEMRosetta)
- [BEMRosetta paper — Tethys Engineering](https://tethys-engineering.pnnl.gov/publications/bemrosetta-open-source-hydrodynamic-coefficients-converter-viewer-integrated-nemoh)
- [ResearchGate paper](https://www.researchgate.net/publication/354543926_BEMRosetta_An_open-source_hydrodynamic_coefficients_converter_and_viewer_integrated_with_Nemoh_and_FOAMM)
- [WEC-Sim Capytaine .nc compatibility issue #875](https://github.com/WEC-Sim/WEC-Sim/issues/875)
- [OpenSourceAgenda BEMRosetta](https://www.opensourceagenda.com/projects/bemrosetta)
