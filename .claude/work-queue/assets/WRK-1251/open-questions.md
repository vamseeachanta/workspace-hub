# WRK-1251 Open Questions

1. **CalculiX installation method** — apt package (`calculix-ccx`) or build from source? Need to verify availability on Ubuntu 24.04.
2. **FreeCAD NURBS hull approach** — generate from parametric equations (Cb, Cm, Cp) or interpolate from station offsets like existing hull_library?
3. **Integration with existing hull_library** — should FreeCAD hull generation be a new module or extend `hull_library/` with a FreeCAD backend?
4. **CalculiX element types** — C3D10 (quadratic tet) for accuracy or C3D4 (linear tet) for speed? Quadratic recommended for stress concentration.
5. **Result visualization** — use VTK Python (since ParaView crashes) or matplotlib for 2D stress contour plots?
6. **Design table parallelism** — sequential batch or parallel execution? FreeCAD is not thread-safe; need process-level parallelism.
