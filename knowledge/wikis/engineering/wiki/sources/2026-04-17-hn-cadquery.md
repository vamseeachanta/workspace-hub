---
title: "HN Discussion — CadQuery: Python Library for Parametric 3D CAD"
tags: [hn-discussion, cadquery, parametric-cad, python, opencascade, community-review]
sources:
  - https://news.ycombinator.com/item?id=47772725
  - https://cadquery.github.io/
added: 2026-04-17
last_updated: 2026-04-17
domain: engineering
---

# HN Discussion — CadQuery: Python Library for Parametric 3D CAD

**HN thread:** [news.ycombinator.com/item?id=47772725](https://news.ycombinator.com/item?id=47772725)
**Submitted by:** gregsadetsky · **Score:** 180 points · **Comments:** 47 · **Date:** 2026-04-16
**Target URL:** [cadquery.github.io](https://cadquery.github.io/)

## Submission Summary

CadQuery is an open-source Python library for programmatic 3D CAD. It sits on the **OpenCASCADE** boundary-representation (B-rep) kernel, so operations return new mathematical solids rather than triangle meshes. Native curved-surface representation means fillets, chamfers, and sweeps are first-class, and STEP export is straightforward — unlike mesh-based tools (e.g., OpenSCAD) where those operations are approximations or awkward.

## Key Technical Points from Discussion

### B-rep vs mesh (most-discussed axis)
- **gcr**: B-rep libraries let you "think in terms of the enclosed solid and perform operations — boolean add/subtract, fillet/chamfer, stamp text — that return a new solid." OpenSCAD's triangle-mesh approach makes fillets "difficult to do."
- **Doxin**: B-rep "can natively represent a sphere" without resolution concerns during modeling — "that's a consideration for export only."
- **Karliss**: "Triangle mesh based modelers can't easily export good step files because they don't operate at that level of abstraction." (STEP fidelity matters for downstream FEA/CFD/PLM.)

### Use cases reported
- **atoav**: Programmatically generated parametric library of 1000+ electronics parts — "literally saved me days of manual work."
- **hgoel**: Used sister library `build123d` for a 3D-printed cosplay helmet; loaded OBJ models and scripted thickness variations.
- **gcr**: Rotary slide rule bracelet — demonstrated parametric advantages over Fusion 360.

### AI code-generation signal (mixed)
- **tda**: "AI autocomplete at least helps with putting together small snippets"; Opus was "more helpful than expected" but "not good enough to one-shot yet."
- **ifloop**: "AI fails horribly with these libs and frameworks" vs. OpenSCAD comfort level.
- **xrd**: Uses Gemini to generate OpenSCAD; asking whether CadQuery is a better LLM target.
- **Read:** Training-corpus asymmetry — OpenSCAD has more public examples, so LLMs default to it. CadQuery adoption for LLM codegen likely needs project-specific exemplars and prompt scaffolding.

### Ecosystem mentioned
| Tool | Language | Notes |
|---|---|---|
| **CadQuery** | Python | OpenCASCADE B-rep kernel, STEP export |
| **build123d** | Python | Sister library to CadQuery, same authors, stylistically different |
| **ReplicAD** | JavaScript/TypeScript | Web-friendly B-rep alternative |
| **FluidCAD** | — | Interactive UI wrapper inspired by CadQuery |
| **Open(Python)SCAD** | Python (over OpenSCAD) | Python syntax, mesh kernel underneath |
| **SolveSpace** | — | Constraint-based; limited programmatic depth |
| **OnShape** | — | Scripting + UI integrated (cited as the aspirational model) |
| **ModelRift, GrandpaCAD** | — | AI-assisted SaaS (cited with some skepticism) |

## Relevance to Workspace-Hub

| Repo / domain | Possible fit |
|---|---|
| `digitalmodel/` | Parametric generation of offshore components (connectors, clumps, plates) — STEP out, FEA/CFD in |
| `CAD-DEVELOPMENTS/` | Candidate to replace or augment existing CAD-DEVELOPMENTS tooling; compare with build123d |
| marine-engineering families | Mooring hardware, riser connectors, fairlead assemblies — parametric libraries are the natural shape |
| AQWA/OrcaFlex pre-processing | Generate geometry → STEP → mesh → solver input |

## Open Questions Logged

1. Can CadQuery generate meshes suitable for AQWA `QPPL DIFF` panel diffraction, or is a mesher (gmsh?) still required?
2. How does CadQuery compare with build123d for our workflow shape — the sister library is mentioned as "quite different stylistically"?
3. Is the Python-library advantage (SymPy for constraint solving, full ecosystem) real in practice, or is it table-stakes once you leave a DSL?
4. LLM codegen: does CadQuery have enough public corpus for reliable autocomplete in our tooling, or do we need a local exemplar library first?

## Follow-up Issues

- **#2327** — digitalmodel: CadQuery spike for parametric offshore geometry generation
- **#2328** — CAD-DEVELOPMENTS: comparison — CadQuery vs build123d vs ReplicAD vs FluidCAD
- **#2329** — Engineering methodology: code-first vs GUI CAD for offshore parametric hardware families

All three follow the CLAUDE.md planning workflow — plans must hit `status:plan-approved` before implementation.

## Cross-References

- [CadQuery entity](../entities/cadquery.md)
- **Cross-wiki (marine-engineering)**: [CadQuery entity](../../../marine-engineering/wiki/entities/cadquery.md)
- [AQWA Solver](../entities/aqwa-solver.md) — downstream consumer of STEP geometry
- [BEMRosetta Tool](../entities/bemrosetta-tool.md) — mesh conversion step in the same pipeline
