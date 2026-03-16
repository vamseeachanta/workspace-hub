# WRK-1251 Domain Notes

## Hull Generation via FreeCAD
- FreeCAD `Part.BSplineSurface` can create NURBS surfaces from control points
- Hull form defined by: Length (L), Beam (B), Draft (T), Block Coefficient (Cb)
- Cb = displaced_volume / (L × B × T) — defines hull fullness
- Midship section coefficient (Cm), prismatic coefficient (Cp) refine the shape
- For Cb=0.7 tanker-type: use parabolic waterline + parabolic section curves
- Hydrostatics from NURBS: volume integration over z-slices (Simpson's rule or trapezoidal)

## FEM Chain: Geometry → Mesh → Solve
1. FreeCAD creates parametric solid (e.g., plate with hole)
2. Export to STEP → import to gmsh for meshing
3. Gmsh generates volume mesh (tetrahedral) → export to CalculiX INP format
4. Apply BCs + material + loads in INP deck
5. Run `ccx input_deck` → produces .frd (results) and .dat (summary)
6. Parse .frd for stress/displacement fields

## Stress Concentration: Plate with Hole
- Infinite plate with circular hole under uniaxial tension: Kt = 3.0 (exact)
- Finite plate correction: Kt depends on d/W ratio (d=hole diameter, W=plate width)
- For d/W < 0.3: Kt ≈ 3.0 is valid within 5%
- Mesh refinement around hole critical for accuracy — need ~10 elements across hole radius

## Design Table Studies
- Parameter matrix in YAML: vary dimensions, materials, loads
- Each combination → FreeCAD model → gmsh mesh → CalculiX solve → extract results
- Results aggregation: max stress, max displacement, weight, safety factor
