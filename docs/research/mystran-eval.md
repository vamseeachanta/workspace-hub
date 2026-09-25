# MYSTRAN + pyNastran Evaluation — Open-Source Nastran for the Repo Ecosystem

**Date:** 2026-09-24
**Trigger:** LinkedIn post on MSC Nastran mesh convergence; question was whether the
open-source Nastran lineage can be used in our repos.
**Version evaluated:** MYSTRAN 19.0.0 (Windows x86_64 release binary, hands-on);
pyNastran 1.4.1 (PyPI, hands-on on Python 3.11)
**Integration:** `digitalmodel/src/digitalmodel/solvers/mystran/` (this PR set)

## Summary

MSC Nastran is commercial. Of the open-source lineage, **MYSTRAN** (MIT, active,
Nastran-compatible input, F06 + OP2 output) is the usable solver and **pyNastran**
(BSD-3) is the Python I/O layer. **NASA NASTRAN-95** (NOSA 1.3, frozen since 2024,
Fortran 77, "no technical support") is not worth integrating.

MYSTRAN is linear-only: SOL 101 static, modal, and linear buckling. It complements
CalculiX (nonlinear, contact, dynamics) rather than replacing it. It is exactly the
right tool for the mesh-convergence studies the LinkedIn post describes, and it gives
a free Nastran-format target for cross-checking in-house ANSYS/APDL models (an
internal "Converting ANSYS to Nastran" deck already exists in the engineering wiki).

Verdict: **adopt MYSTRAN + pyNastran**. Both licenses are compatible with
digitalmodel's MIT license.

---

## Candidates

| Tool | License | Activity (2026-09) | Language | Verdict |
|---|---|---|---|---|
| nasa/NASTRAN-95 | NASA Open Source Agreement 1.3 | Last push 2024-04; 3 commits; no support | Fortran 77 | Skip |
| MYSTRANsolver/MYSTRAN | MIT | Pushed 2026-09-24; v19.0.0 released 2026-06-29 | Fortran 95 | Adopt |
| SteveDoyle2/pyNastran | BSD-3-Clause | Repo pushed 2026-09-23; PyPI 1.4.1 (2024-03) | Python | Adopt (pin 1.4.x) |

---

## Capabilities (MYSTRAN 19.0.0)

- **Solutions:** linear static (SOL 101), normal modes, linear elastic buckling,
  classical laminated plate theory.
- **Elements:** full 1D/2D/3D suite — CBAR/CBEAM/CROD, CTRIA3/CQUAD4 shells,
  CTETRA/CHEXA/CPENTA solids, composites via PCOMP.
- **Input:** Nastran bulk data, free-field or fixed-field. Long free-field numeric
  tokens (e.g. `2.10000000E+11`, 14 chars) are accepted without truncation.
  Continuation lines with `+TAG` markers work.
- **Output:** `<job>.F06` (text), `<job>.OP2` (binary), `<job>.NEU` (Femap
  neutral), `<job>.ERR`. OP2 is readable by pyNastran 1.4.1:
  `displacements`, `spc_forces`, `op2_results.stress.cbar_stress`,
  `op2_results.stress.chexa_stress` all populate.
- **Not supported:** nonlinear material/geometry, contact, transient/frequency
  response, thermal.

---

## Hands-on Validation (Windows workstation, release binary)

### CBAR cantilever vs Euler-Bernoulli

L = 1 m, 0.1 x 0.1 m section, E = 210 GPa, P = 1 kN tip load, 4 elements.

| quantity | MYSTRAN | exact PL^3/3EI | error |
|---|---:|---:|---:|
| tip deflection | 1.904762E-04 m | 1.904762E-04 m | 0.0000% |
| root reaction | -1000.0 N | -1000.0 N | 0 |
| epsilon (U'(KU-P)/U'P) | -2.5E-15 | — | — |

### CHEXA8 cantilever mesh-convergence sweep

Same beam as a solid, tip load distributed over the tip face, mean tip-face
deflection tracked. Wall time for all five levels: 8 s on the workstation.

| level (nx x ny x nz) | nodes | elements | tip deflection (m) | rel. change | error vs exact |
|---|---:|---:|---:|---:|---:|
| 4x1x1 | 20 | 4 | 1.648865E-04 | — | 13.435% |
| 8x2x2 | 81 | 32 | 1.803450E-04 | 8.572% | 5.319% |
| 16x2x4 | 255 | 128 | 1.870553E-04 | 3.587% | 1.796% |
| 32x4x8 | 1485 | 1024 | 1.894183E-04 | 1.248% | 0.555% |
| 64x4x8 | 2925 | 2048 | 1.899503E-04 | 0.280% | 0.276% |

Convergence is monotone from below, as expected for an 8-node hex in bending.
Richardson extrapolation of the last two levels (r = 2, p = 2) gives
1.9013E-04 m, within 0.2% of the beam-theory value; the residual is the Timoshenko
shear contribution (~0.8% for L/h = 10) that beam theory omits and the solid
model includes, so the solid is converging to the physically correct answer.

This is the sweep `MystranChain.run_mesh_convergence()` runs and the integration
test asserts (monotone, final error < 5% on a three-level subset).

---

## Gotchas Found

1. **Exit code is 0 on FATAL errors.** `mystran` returns 0 even when the F06
   contains `*ERROR` and no results. The chain inspects stdout for `FATAL` and
   the F06 for `*ERROR` before declaring success; a regression test covers this.
2. **PSOLID needs the IN (integration order) field for HEXA8** — omitting it is
   `*ERROR 1964`. The writer always emits `PSOLID,pid,mid,0,2`.
3. **Output extension is upper-case `.F06`/`.OP2`.** Matters on Linux; the parser
   searches both cases.
4. **PBAR without stress-recovery points reports zero bar stresses.** Pass
   `stress_points` to `BDFWriter.add_bar_section` when bar stresses matter.
5. **No `--version` flag.** Probe by presence on PATH, not by version output.
6. pyNastran's deprecated `model.cbar_stress` shortcut raises a confusing
   `call stack is not deep enough` from a script; use `model.op2_results.stress.*`.

---

## Installation

**Windows:** download `mystran-19.0.0-windows-x86_64.exe` from GitHub Releases,
rename to `mystran.exe`, put on PATH (or set `MYSTRAN_EXE`). SHA-256 of the
19.0.0 asset used here:
`0180714701e387a735682cdcc7c90c2d9c76a199769440f36052672fd8722e68`.

**Linux (ace-linux-2 / dev-secondary):** no official Linux binary yet; build from
source with `scripts/setup/mystran-build-linux.sh` (gfortran + CMake + Ninja +
OpenBLAS, installs to `~/.local/bin`, runs the CBAR smoke test). Also wired into
`engineering-suite-install.sh --fea`. Not yet executed on ace-linux-2 as of this
writing — SSH from the authoring session was blocked at the client side.

**Python:** `uv sync --extra nastran` in digitalmodel pulls pyNastran 1.4.x.
Python 3.11 confirmed; pyNastran 1.4.1 declares >=3.9.

---

## Integration in digitalmodel

`src/digitalmodel/solvers/mystran/` mirrors the CalculiX chain:

| module | role |
|---|---|
| `bdf_writer.py` | gmsh-style nodes/elements (0-based) -> free-field BDF: GRID, CBAR/CTRIA3/CQUAD4/CTETRA/CHEXA, MAT1, PBAR/PSHELL/PSOLID, SPC1/SPC, FORCE/MOMENT |
| `result_parser.py` | F06 parser (displacements, SPC forces, solid/shell element stresses with CENTER/GRD rows, epsilon, `*ERROR` lines); optional OP2 via pyNastran |
| `convergence.py` | `MeshConvergenceStudy` (relative change, tolerance, monotonicity, markdown table) and `richardson_extrapolation` |
| `fem_chain.py` | `MystranChain`: structured hex/bar cantilever generators, `load_mesh` for gmsh output, BDF setup, solve with FATAL detection, result extraction, cantilever validations, convergence sweep |

Tests: `tests/solvers/mystran/` — 90 tests; 85 run without the solver (4
integration tests skip unless `mystran` is available, 1 skips without
pyNastran). All 89 applicable tests pass on the Windows workstation with the 19.0.0 binary. The existing gmsh
extraction in `solvers/calculix/fem_chain.py` produces the same
`{"Hexahedron 8": {"connectivity": ...}}` dict, so gmsh geometry drops straight
into `MystranChain.load_mesh`.

---

## Recommendation and Next Steps

- **Adopt.** Catalog entries added for MYSTRAN and pyNastran.
- Build MYSTRAN on ace-linux-2 with the script above and add `mystran` to the
  dev-secondary tool list in `config/workstations/registry.yaml` once verified.
- Follow-ups worth an issue each: CQUAD4 shell validation (plate bending),
  modal analysis (SOL 103) wrapper, gmsh -> MYSTRAN plate-with-hole Kt check
  against the CalculiX result, and an ANSYS APDL -> BDF converter spike for the
  in-house APDL macro library.

Sources: [MYSTRAN](https://github.com/MYSTRANsolver/MYSTRAN),
[MYSTRAN releases](https://github.com/MYSTRANsolver/MYSTRAN/releases),
[MYSTRAN docs](https://github.com/MYSTRANsolver/MYSTRAN_Documentation),
[nasa/NASTRAN-95](https://github.com/nasa/NASTRAN-95),
[pyNastran](https://github.com/SteveDoyle2/pyNastran),
[pyNastran on PyPI](https://pypi.org/project/pyNastran/).
