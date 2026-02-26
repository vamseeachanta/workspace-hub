# Module Index

> Canonical registry of all workspace-hub engineering modules and repositories.
> Source of truth for module discovery, toolchain routing, and workstation assignment.

## Engineering Modules

| Module | Repo | Type | Domain | Tools | Computer |
|--------|------|------|--------|-------|----------|
| CAD-DEVELOPMENTS | [bakkiprasad5669/CAD-DEVELOPMENTS](https://github.com/bakkiprasad5669/CAD-DEVELOPMENTS) | FEA pipeline | Marine / Structural | FreeCAD, Gmsh, CalculiX, FEniCS, Elmer, Blender | ace-linux-2 |

### CAD-DEVELOPMENTS

**Mission**: AI-agent-driven FEA model development from scratch — geometry → mesh → solve → post-process pipeline executed by Python agents.

**Pipeline stages**:

| Stage | Agent | Tool | Status |
|-------|-------|------|--------|
| 1 — Geometry | `agents/geometry_agent.py` | FreeCAD / build123d | Stub (WRK-614) |
| 2 — Meshing | `agents/mesh_agent.py` | Gmsh Python API | Stub (WRK-612) |
| 3 — Solve | `agents/solve_agent.py` | CalculiX / FEniCS | Stub (WRK-613) |
| 4 — Postprocess | `agents/postprocess_agent.py` | VTK / ParaView | Stub (WRK-613) |

**Current geometry**: 12 FreeCAD hull models in `geometry/hull/`, 1 Blender CTD model in `geometry/instruments/`.

**Related WRK items**: WRK-610 (setup), WRK-611 (FCStd parser), WRK-612 (mesh), WRK-613 (solve), WRK-614 (Ship Workbench), WRK-394 (planing hull hydrodynamics)

---

*Add new module entries above. Each entry needs: repo link, type, domain, tools, computer, and a brief mission statement.*
