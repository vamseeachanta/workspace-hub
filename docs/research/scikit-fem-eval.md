# scikit-fem Evaluation — Offshore Structural Use

**Date:** 2026-03-29
**Issue:** vamseeachanta/workspace-hub#1489
**Version evaluated:** 11.0.0 (latest stable)

## Summary

scikit-fem is a pure-Python FEM assembler (numpy + scipy only, no compiled code) that excels at rapid prototyping of custom weak-form PDEs. It supports 1D/2D/3D volume elements and Euler-Bernoulli beam and Kirchhoff plate elements, covers eigenvalue problems (modal analysis), and integrates with meshio for broad mesh I/O. However, it lacks shell elements (no Reissner-Mindlin, no 3D curved shell), making it insufficient as a standalone solver for thin-walled offshore structures; it is better positioned as a matrix-assembly utility than a full structural analysis suite.

---

## Element Library

| Domain | Element | Notes |
|---|---|---|
| 1D Beam | `ElementLineHermite` | Cubic Hermite, Euler-Bernoulli only; no shear deformation |
| 2D Tri (plate) | `ElementTri15ParamPlate` | 15-parameter non-conforming, Kirchhoff plate bending |
| 2D Tri | `ElementTriP1`, `ElementTriP2`, `ElementTriMini` | Scalar / vector Lagrange, mixed |
| 2D Quad | `ElementQuad1`, `ElementQuad2` | Serendipity |
| 3D Tet | `ElementTetP1`, `ElementTetP2` | Linear / quadratic tetrahedral |
| 3D Hex | `ElementHex1`, `ElementHex2` | Trilinear / serendipity hexahedral |
| Nedelec / H(div) | Various | Electromagnetics / mixed methods |
| **Shell** | **None** | No Reissner-Mindlin or curved shell element |

---

## Mesh Support

Mesh formats are handled via **meshio** (optional dependency). All formats meshio supports are available, including:

- Gmsh `.msh` (versions 2 and 4)
- VTK / VTU, XDMF/HDF5
- Abaqus `.inp`, Nastran `.bdf`, STL, Exodus, and ~30 others

Built-in mesh generators cover simple geometries (lines, quads, tris, boxes, L-shapes). Subdomains and boundary tags are preserved through the load/save cycle (with some caveats on boundary saving, tracked in upstream issue #261).

---

## Eigenvalue / Modal Analysis

Yes — supported natively. `skfem.utils.solve()` accepts a mass matrix argument to form the generalized eigenvalue problem **K·u = λ·M·u**, backed by `scipy.sparse.linalg.eigsh` (ARPACK). The official examples include:

- Vibration of a 3D elastic solid (linear elastic eigenvalue problem)
- Biharmonic plate buckling
- Acoustic cavity modes

For offshore structures, natural frequencies of jacket legs, risers (as beams), or simple hull sections (as 3D solid) can be obtained directly. Shell-type modal analysis (e.g., local panel buckling modes) is not possible without custom element implementation.

---

## Performance

Assembly cost is dominated by scipy sparse-solve, not by Python-level assembly. Key data points:

- Assembly time is sub-dominant vs. direct sparse solve for typical mesh sizes; solve time dominates beyond ~50k DOFs
- `np.int32` internal indexing (recent) gives ~10% speed boost and proportional memory reduction
- No parallelism in assembly by default (GitHub discussion #713 tracks this); assembly is single-threaded NumPy loops
- Estimated practical ceiling before solve bottleneck: **~50k–100k DOFs** for interactive workflows; 10k-element meshes (tetrahedral P1 → ~60k DOFs) run in seconds on a desktop
- For larger problems, PETSc / PyAMG can be plugged in as external solvers (no compiled coupling required)

---

## Strengths and Limitations for Offshore Structural Use

### Strengths
- **Zero-compilation install** — `pip install scikit-fem`; works on any Python 3.10+ environment with no MPI, no Docker
- **Transparent assembly** — weak forms written in Python; easy to add custom constitutive models or coupling terms
- **Eigenvalue support** — modal analysis works out-of-the-box for beam/solid elements
- **meshio integration** — accepts Gmsh models from any pre-processor; outputs VTK/XDMF for ParaView post-processing
- **Scipy interoperability** — assembled matrices are standard CSR; any scipy/PyAMG/PETSc4py solver applies
- **Active maintenance** — Python 3.14 support in progress as of 2025/2026; JOSS-published, 1k+ GitHub stars

### Limitations
- **No shell elements** — the critical gap for offshore structures (jacket panels, hull, riser casing, subsea pipework); 3D solid modeling of thin walls is mesh-inefficient
- **No built-in contact or nonlinear material** — geometric/material nonlinearity requires user implementation
- **No prestress or follower loads** — hydrostatic pressure on deforming shells not built in
- **Single-threaded assembly** — impractical for meshes >500k elements without external solver coupling
- **No integrated post-processor** — stress recovery requires manual interpolation; no built-in von Mises / principal stress output
- **Thin documentation for advanced structural topics** — examples focus on academic PDEs, not engineering workflows

---

## Comparison with FEniCSx

| Criterion | scikit-fem | FEniCSx |
|---|---|---|
| Install complexity | `pip install scikit-fem` | Conda / Docker; compiled C++/MPI stack |
| Shell elements | None | Via FEniCS-Shells extension |
| Eigenvalue support | Built-in (scipy ARPACK) | Built-in (SLEPc) |
| Nonlinear mechanics | Manual | Built-in Newton solver |
| Parallel scalability | Single-threaded assembly | MPI-parallel, HPC-capable |
| Custom weak forms | Very easy (pure Python) | Easy (UFL DSL, but more ceremony) |
| Performance at 10k elements | Fast, seconds | Fast, seconds (comparable) |
| Performance at 1M+ DOFs | Bottleneck: serial assembly | MPI scales well |
| Ecosystem size | Small, academic | Large, industry + research |
| Offshore structural suitability | Low (no shell) | Medium (shell via extension) |

For simple structural problems (beam deflection, 3D solid stress, modal frequencies of compact structures), scikit-fem is **simpler to set up and faster to prototype** than FEniCSx. FEniCSx wins on shell elements, parallel scale, and nonlinear mechanics.

---

## Recommendation

**Defer** for offshore structural production use; **Adopt for targeted research utilities**.

Rationale:
- The missing shell element is a hard blocker for panel stress and thin-wall analyses that dominate offshore structural work
- For Euler-Bernoulli beam models (risers, mooring lines, jacket legs as line elements) and simple 3D modal analysis of compact components, scikit-fem is the easiest pure-Python path
- Recommend adopting as a **beam-assembly utility** for the existing Python toolchain (no compilation), with FEniCSx or CalculiX reserved for shell/nonlinear work

**Action items if deferring:**
1. Spike: implement a single Euler-Bernoulli beam modal analysis for a jacket leg using scikit-fem to validate integration with existing mesh pipeline
2. Watch upstream for shell element PRs (the project accepts community element contributions)
3. Revisit when/if Reissner-Mindlin shell element is merged

---

## One-Liner Verdict

> scikit-fem is the easiest pure-Python FEM assembler for beams, plates, and 3D solids with eigenvalue support — but the absence of shell elements is a hard blocker for most offshore structural use cases; **defer for production, adopt for beam-level research utilities**.
