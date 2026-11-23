# pycatenary Evaluation — Mooring Line Catenary Solver

**Issue:** workspace-hub#1488
**Date:** 2026-03-30 (updated with live test results; original eval 2026-03-29)
**Evaluator:** research agent + live validation agent

---

## Summary

pycatenary (`tridelat/pycatenary`) is a pure-Python, MIT-licensed catenary solver for quasi-static mooring line geometry and tension. It reached v1.0.0 in January 2026 and covers the core use case—single or multi-segment lines with optional elastic stretch, flat-seabed contact, and 3D geometry—cleanly. It does not, however, reach the system-level completeness of MoorPy, which already exists in our ecosystem and adds whole-system equilibrium, stiffness matrices, and RAFT coupling. For isolated single-line geometry lookups pycatenary is lighter and simpler; for anything involving a coupled floating platform, MoorPy is the right tool.

---

## API Overview

| Item | Detail |
|---|---|
| **Package** | `pycatenary` v1.0.0 (PyPI / GitHub: tridelat/pycatenary) |
| **Primary class** | `MooringLine` |
| **Key constructor inputs** | `l` (fairlead xyz), `anchor` (anchor xyz), `L` (unstretched length, m), `w` (submerged weight N/m), `EA` (axial stiffness N, or `None` for inextensible), `floor` (bool, flat seabed contact) |
| **Solution call** | `line.compute_solution()` |
| **Position along line** | `line.s2xyz(s)` — returns xyz at arc length s |
| **Tension along line** | `line.getTension(s)` — scalar tension at arc length s |
| **End-point forces** | Retrieved via tension at s=0 (anchor) and s=L (fairlead) |
| **Multi-segment** | Yes — pass arrays to `L` and `w`; each segment has own properties |
| **3D support** | Yes — fairlead and anchor accept full xyz coordinates |
| **Elastic stretch** | Yes — EA parameter; set `None` for inextensible |
| **Seabed contact** | Yes — flat-floor only; no uneven or sloped seabed |
| **Visualization** | `line.plot()` — matplotlib 2D/3D |
| **Dependencies** | NumPy, SciPy, Matplotlib (pure Python, no compiled extensions) |
| **License** | MIT |
| **Maintenance** | Active — v1.0.0 released 2026-01-04; GitHub shows active issues/PRs |

---

## Comparison with MoorPy Catenary Module

| Capability | pycatenary | MoorPy (`Catenary.py`) |
|---|---|---|
| Single-line catenary | Yes | Yes |
| Multi-segment lines | Yes | Yes |
| Elastic stretch (EA) | Yes | Yes |
| Flat seabed contact | Yes | Yes |
| Seabed slope (alpha) | No | Yes (`alpha` parameter) |
| Uneven / non-flat seabed | No | Partial (slope only) |
| 3D geometry | Yes | Projected 2D internally, 3D at system level |
| Clump weights / floats | Partially (via segments) | Yes (explicit support) |
| Stiffness matrix output | No | Yes (HF, VF, HA, VA + Jacobian) |
| Full mooring system equilibrium | No — single-line tool | Yes — coupled system solver |
| RAFT / OpenFAST coupling | No | Yes |
| Standalone install footprint | Minimal (pure Python) | Larger (system-level dependencies) |
| API style | OOP (`MooringLine` class) | Functional (`catenary(XF, ZF, L, EA, W, ...)`) |
| Convergence control | Internal | Exposed (`Tol`, `MaxIter`, `HF0`, `VF0`) |

**Key delta:** MoorPy's `catenary()` function returns full stiffness components and supports seabed slope, which matters for anchored spread-mooring design work. pycatenary's OOP interface is cleaner for scripting individual line queries.

---

## Known Limitations

1. **Flat seabed only** — The `floor` option assumes a horizontal flat seabed. Sloped or irregular bathymetry is not handled.
2. **No stiffness output** — pycatenary does not return linearized stiffness components (dHF/dXF, etc.). MoorPy does.
3. **No system-level coupling** — Cannot directly compute platform equilibrium or mooring restoring matrix; intended for single-line use.
4. **Single catenary shape** — Even multi-segment lines follow one continuous catenary arc; no intermediate attachment points to structure.
5. **No clump-weight / buoy mid-line objects** — MoorPy explicitly models these; pycatenary approximates via segment weight changes only.
6. **No dynamic solver** — Quasi-static only, consistent with its scope, but notable.

---

## Live Validation Results (2026-03-30)

pycatenary v1.0.0 was pip-installed and tested against analytical catenary equations
and the digitalmodel `CatenarySolver` (source-level comparison; runtime cross-check
blocked by NumPy 2.x vs system matplotlib incompatibility in digitalmodel).

### Test configuration: 500m water depth mooring

| Parameter | Value |
|---|---|
| Water depth | 500 m |
| Fairlead depth | 20 m (below surface) |
| Anchor radius | 1500 m (horizontal) |
| Line length | 1800 m (unstretched) |
| Submerged weight | 1500 N/m (R4 chain ~127mm) |
| EA | 1.5e9 N |

### Results

| Metric | Elastic (EA=1.5e9) | Rigid (no EA) |
|---|---|---|
| H_fairlead | 210,515 N (210.5 kN) | 211,130 N (211.1 kN) |
| V_fairlead | 906,134 N (906.1 kN) | 906,878 N (906.9 kN) |
| T_fairlead | 930,266 N (930.3 kN) | 931,130 N (931.1 kN) |
| T_anchor | 210,515 N (210.5 kN) | 211,130 N (211.1 kN) |
| Catenary param a | -- | 140.8 m |
| Lifted length | -- | 604.6 m |
| Grounded length | -- | 1195.4 m |

### Analytical identity checks

- **T = H + w*h** (rigid catenary with seabed): 211,130 + 1500 x 480 = 931,130 N. pycatenary returns 931,130 N. **Exact match.**
- **T = sqrt(H^2 + V^2)** (elastic): 930,266 N vs pycatenary 930,266 N. **Exact match.**
- **Elastic vs rigid delta**: H differs by -0.29%, V by -0.08%, T by -0.09%. Physically correct -- elastic line stretches, reducing tension.

### Additional tests passed

- 3D mooring line (README example) -- converged, forces physically reasonable
- 2D catenary line -- converged
- Multi-segment line (chain + polyester rope, 3 segments) -- converged, 657.8 kN fairlead tension
- Tension distribution along line -- constant in grounded section, increasing toward fairlead

### Comparison with digitalmodel CatenarySolver (source analysis)

Both tools solve the same general catenary BVP (3-equation system for H, x1, x2 using scipy). Key differences:

| Aspect | pycatenary | digitalmodel solver |
|---|---|---|
| Multi-segment | Native support | Not implemented |
| 3D geometry | Native (projects to 2D internally) | 2D only |
| Elastic stretch | Per-segment elongation | Average tension approximation |
| Seabed contact | Floor detection built-in | water_depth parameter, manual |
| API | OOP, clean | Dataclass in/out, functional |
| Maturity | v1.0.0, published, tested | In-house, less exercised |

pycatenary's multi-segment and 3D support are improvements over the in-house solver. However, MoorPy remains the more complete tool for system-level work.

---

## Recommendation

**Defer.**

MoorPy is already integrated in the ecosystem and covers every capability pycatenary offers, plus stiffness matrices, seabed slope, system-level equilibrium, and RAFT coupling. Adding pycatenary would create a second catenary code path with no net gain for the current engineering workflows.

Revisit only if a specific use case emerges that needs a lightweight, OOP, single-line solver decoupled from the MoorPy system model (e.g., a utility script or notebook that must not carry MoorPy's dependency tree).

---

## Verdict

**Skip.** MoorPy's catenary module already covers pycatenary's scope and adds stiffness output, seabed-slope support, and system-level coupling that pycatenary lacks.

---

## References

- [GitHub: tridelat/pycatenary](https://github.com/tridelat/pycatenary)
- [pycatenary PyPI](https://pypi.org/project/pycatenary/)
- [pycatenary docs v1.0.0](https://tridelat.github.io/pycatenary)
- [MoorPy GitHub: NREL/MoorPy](https://github.com/NREL/MoorPy)
- [MoorPy Catenary.py source](https://github.com/NREL/MoorPy/blob/master/moorpy/Catenary.py)
- [MoorPy documentation](https://moorpy.readthedocs.io/en/latest/)
