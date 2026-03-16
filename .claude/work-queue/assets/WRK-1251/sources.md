# WRK-1251 Sources

## Engineering Standards
- USNA EN400 Chapters 2-3 — hydrostatic validation reference (already in naval_architecture)
- Roark's Formulas for Stress and Strain — plate with hole stress concentration (Kt ≈ 3.0)
- DNV-RP-C205 — environmental conditions, hull form coefficients

## Software Documentation
- FreeCAD 0.21 Python API: Part.BSplineSurface, Part.makeShell, FEM workbench
- Gmsh 4.x Python API: mesh generation, format export
- CalculiX documentation: CCX input deck format, element types, material cards

## Workspace Skills
- `.claude/skills/engineering/cad/freecad-automation/SKILL.md`
- `.claude/skills/engineering/cad/gmsh-meshing/SKILL.md`
- `.claude/skills/engineering/workflows/gmsh-openfoam-orcaflex/SKILL.md`
- `.claude/skills/engineering/marine-offshore/fe-analyst/SKILL.md`

## Test Data Sources
- Plate with circular hole: analytical Kt = 3.0 (Peterson's Stress Concentration Factors)
- Simply supported beam: Euler-Bernoulli beam theory
- Pressure vessel: Lame equations for thick-walled cylinders
- Hull hydrostatics: L=100m, B=20m, T=8m, Cb=0.7 → analytical displacement = ρ × L × B × T × Cb
