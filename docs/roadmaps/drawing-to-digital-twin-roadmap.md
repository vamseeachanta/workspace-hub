# Drawing-to-digital-twin roadmap (ShipHULL-class capability)

**Date:** 2026-09-29 · **Owner intent:** "our vision is also to get to this stage" (owner, 2026-09-29, on a
ShipReality ShipHULL announcement) · **Tracking epic:** [digitalmodel #2272](https://github.com/vamseeachanta/digitalmodel/issues/2272) · **Related:** `.planning/ROADMAP.md` Phase 999.1 "Ship Plan CAD Pipeline" (WRK-5055),
digitalmodel #2170 (HullProd screening), #2191 / #2241 (parametric forms), #1004 (CAD inventory),
#1839 (defendable hydrodynamic coefficients), llm-wiki source page
`naval-architecture/sources/shipreality-2026-shiphull-2d-to-3d-reconstruction.md`.

## Target state (the benchmark)

A commercial product now claims: legacy 2D construction drawings, to a 3D hull and propeller, to
internal structure (frames, girders, stiffeners, bulkheads, decks, tanks, compartments), managed in
a browser, feeding CFD, FEM, structural reassessment, life extension and alternative-fuel retrofit
studies from one geometry. The public material gives no input formats, accuracy, turnaround or
validation figures; the pipeline shape is the benchmark, not the claims.

## Where the ecosystem stands (survey of 2026-09-29, paths under C:\ws)

| Stage | Exists | Notes |
|---|---|---|
| A. Drawing digitisation (DWG/DXF/PDF/scan to geometry) | **No** | No DXF/DWG geometry reader anywhere (no ezdxf, dxfgrabber, ODA, LibreDWG). PDF/OCR tooling extracts text, tables and charts only. WRK-5055 produced page-level skeleton DXFs for three public lines plans; traces are fragmented; no vectorisation code is in the repos. |
| B. Offsets to hull surface | Yes | `hull_library/line_generator` (offset table to surface to panels to GDF/OrcaWave), `parametric_form.py` (parameters to dense `HullProfile`), `hull_surface_brep.py` (B-spline face, STEP), `freecad_hull.py`, `HullMeshGenerator`. |
| C. Hull quality and screening | Yes | HullProd curvature signatures (mesh and BRep), diffraction quality gates, hydrostatics, form coefficients. |
| D. Hydrodynamics | Yes | OrcaWave, AQWA, Capytaine, BEMRosetta chains; OpenFOAM case builder; one end-to-end client resistance chain that starts from an existing Rhino model. |
| E. Structure | Partial | Hull girder strength, section modulus check, plate and stiffener buckling, corrugated bulkhead, grillage, plate metal-loss FFS: component-level. **No assembled ship structural model** (frames, bulkheads, decks, tanks as one geometry-derived model), no geometry-derived section modulus, no global FE model. FEM solvers exist (open-source Nastran chain, CalculiX writer, licensed FEA on the licensed host). |
| F. Life extension, retrofit | Partial | API 579 FFS, RBI, inspection planning; alternative-fuel ship sizing and LH2 chain. **No retrofit workflow that consumes a hull model.** |
| G. Shared model and viewer | **No** | No browser 3D hull viewer; no digital-twin data model tying drawings, geometry, analyses and results; no as-built reconciliation. |
| Source material | Yes | Six DWG lines plans in `digitalmodel/docs/domains/freecad/src/hulls`; in the client wiki sibling about 1,470 DWG drawings (one hull's structural set alone is over 800 sheets) and 25 Rhino hull models. These are the reuse asset the whole vision rests on. |

## Phases (each phase is one or more owner-approved plans; implementation on the Codex lane where bounded)

**A1. DXF lines-plan reader (first slice, bounded, closed-form testable).** `ezdxf` reader for
body plan, half-breadth and sheer views on named layers: polylines and splines to station
curves to an offset table to `HullProfile`. DWG enters via a one-time DWG-to-DXF conversion
(ODA File Converter, user-run; LibreDWG as a later automated option). Tests: a DXF body plan
synthesised from the analytic Wigley and from `parametric_form.generate_profile` must round-trip
to offsets within 0.5 % of B/2; then the six repo-local DWG lines plans (after conversion) as
the first real cases, with hydrostatics and HullProd signatures as the acceptance evidence.

**A2. View segmentation and scale recovery.** Title block, scale bar and dimension recognition
on DXF and vector PDF; automatic assignment of body-plan stations to x positions from the
sheer-plan station grid. Raster scans deferred to A4.

**A3. Offset-table digitisation from scans.** Reuse the existing OCR and table extraction for
tabulated offsets (the fastest path for older ships), validated against A1 on the same hull.

**A4. Raster lines plans.** Resume WRK-5055 with curve reconstruction rather than
skeletonisation; accept only what passes the A1 round-trip tolerances.

**B1. Assembled structural model.** A ship structural data model (frames at frame spacing,
longitudinals, bulkheads, decks, tanks and compartments as regions of the hull surface),
generated from the hull surface plus a midship-section drawing digitised by A1/A2; section
modulus derived from geometry and checked against `hull_girder_strength`; export to the
open-source Nastran chain for a global FE model; comparator: closed-form box-girder section
modulus and a known published midship section.

**C1. One geometry, several analyses.** A single `HullModel` record (surface, structure,
compartments, provenance) that the diffraction, CFD, hydrostatics, hull-girder and FFS chains
consume without re-modelling; provenance and comparator class recorded on every result
(reproducibility rule).

**D1. Retrofit and life-extension workflows on the model.** Alternative-fuel tank placement and
weight/stability re-checks on the compartment model; FFS on plate regions of the structural
model.

**E1. Browser viewer and shared model.** A local-first viewer (three.js or pyvista-to-HTML) for
hull, structure and analysis fields, reading the `HullModel` record; commentable HTML per the
reporting conventions; hosted only through the report-audience rules.

## Ordering and gates

A1 first: it is small, closed-form testable, and unlocks the reuse of the drawing sets that
already exist. B1 next, because life extension and retrofit (the commercial value named in the
benchmark) need structure, not just the shell. A2 to A4 widen the input funnel and can run in
parallel with B1. C1 and E1 follow once two analysis chains consume the same model. Every phase
needs its own plan and owner approval; client drawings stay in the client wiki sibling and are
never copied into public repositories.

## Risks

- DWG has no pure-Python reader; the conversion step must stay explicit and reproducible.
- Legacy drawings are inconsistent (layers, units, scale, partial views); A1 must fail loudly
  and report what it could not read rather than fill gaps.
- Structural reconstruction from drawings is far larger than the hull surface; B1 must start
  from the midship section and frame table, not from the full structural set.
