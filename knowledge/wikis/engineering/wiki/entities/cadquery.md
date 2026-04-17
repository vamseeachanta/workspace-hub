---
title: "CadQuery"
tags: [cadquery, python, cad, parametric, opencascade, brep, step-export, code-first-cad]
sources:
  - 2026-04-17-hn-cadquery
added: 2026-04-17
last_updated: 2026-04-17
domain: engineering
cross_links:
  - marine-engineering/entities/cadquery
---

# CadQuery

**CadQuery** is a Python library for programmatic, parametric 3D CAD modeling. It wraps the **OpenCASCADE** geometric kernel, providing a fluent API for constructive solid geometry (CSG), boolean operations, fillets, chamfers, sweeps, lofts, and STEP export.

## Why It Matters Here

Parametric families (fasteners, brackets, connectors, mooring hardware, instrument housings) are exactly the shape where code-first CAD wins: one script generates N variants, each guaranteed consistent and re-generatable from source. For the workspace-hub ecosystem, the interesting integration surfaces are `digitalmodel/` (offshore component geometry) and `CAD-DEVELOPMENTS/` (tooling experimentation).

## Kernel and Representation

| Aspect | CadQuery | OpenSCAD |
|---|---|---|
| Kernel | OpenCASCADE (B-rep) | CGAL / triangle mesh |
| Native curved surfaces | Yes | No — meshed at authoring time |
| Fillets / chamfers | First-class | Approximated |
| STEP export | Direct, high-fidelity | Awkward / lossy |
| Boolean ops | On exact solids | On meshes (watertight fragility) |

B-rep matters downstream: STEP files carry exact surfaces, so FEA meshers and CFD preprocessors can remesh at the needed density without degrading the geometry.

## Minimal Example

```python
import cadquery as cq

# Parametric flange: ring with bolt pattern
od, id_, thickness = 120.0, 40.0, 12.0
n_bolts, bolt_pcd, bolt_hole = 8, 90.0, 6.0

flange = (
    cq.Workplane("XY")
    .circle(od / 2).circle(id_ / 2)
    .extrude(thickness)
    .faces(">Z").workplane()
    .polarArray(bolt_pcd / 2, 0, 360, n_bolts)
    .hole(bolt_hole)
)

cq.exporters.export(flange, "flange.step")
```

One script → any `(od, id_, thickness, n_bolts, …)` tuple → a STEP file.

## Ecosystem Siblings

| Tool | Relationship |
|---|---|
| [build123d](https://github.com/gumyr/build123d) | Sister library, same authors, same kernel, different idioms |
| [ReplicAD](https://replicad.xyz/) | Web/JS alternative on OpenCASCADE.js |
| FluidCAD | Interactive UI on top of CadQuery-style workflow |
| [OpenSCAD](https://openscad.org/) | Older DSL, mesh-based, larger public corpus |
| SolveSpace | Constraint-based, limited for parametric scaling |

## Candidate Workflows

### Offshore component generation → solver input

```
CadQuery script  →  STEP file  →  gmsh / Salome  →  AQWA DAT / OrcaFlex / Abaqus
```

### Parametric library build-out

```
parameter CSV / YAML  →  CadQuery loop  →  /library/{sku}.step + /library/{sku}.png
```

## LLM Code Generation Notes

Training-corpus asymmetry is real: OpenSCAD has a larger public example base, so generic LLM suggestions skew there. For reliable CadQuery codegen in agentic workflows, expect to need:
- A local exemplar library (5-20 well-commented scripts covering the shape primitives your domain actually uses)
- A retrieval step that injects relevant exemplars into the prompt
- Tight feedback from STEP validation / visual render before acceptance

See [Claude API skill](../../../../../.claude/skills/) practices around prompt caching for exemplar libraries.

## Known Limitations (from HN community)

- B-rep operations can fail with obscure "OCC error" messages; recovery is harder than in mesh tools
- Learning curve steeper than OpenSCAD for first-time programmers
- No built-in assembly mate-style UI — if your workflow needs visual constraint sketching, OnShape-family tools still win

## Cross-References

- **Source summary**: [HN CadQuery thread, 2026-04-17](../sources/2026-04-17-hn-cadquery.md)
- **Cross-wiki (marine-engineering)**: [CadQuery entity](../../../marine-engineering/wiki/entities/cadquery.md)
- **Related entity**: [AQWA Solver](./aqwa-solver.md) — consumes STEP geometry for panel diffraction
- **Related entity**: [BEMRosetta Tool](./bemrosetta-tool.md) — mesh conversion in the solver pipeline
