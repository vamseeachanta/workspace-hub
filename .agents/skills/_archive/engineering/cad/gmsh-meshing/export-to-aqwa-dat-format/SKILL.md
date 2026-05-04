---
name: gmsh-meshing-export-to-aqwa-dat-format
description: 'Sub-skill of gmsh-meshing: Export to AQWA (.DAT Format) (+4).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Export to AQWA (.DAT Format) (+4)

## Export to AQWA (.DAT Format)


AQWA requires panel meshes in its proprietary .DAT format. gmsh cannot export directly to AQWA format, so a post-processing conversion is needed.

```python
def msh_to_aqwa_panels(msh_file: str, dat_file: str):
    """Convert gmsh MSH to AQWA panel data.

    AQWA expects quad panels (QPPL DIFF cards) with nodes
    defined in counter-clockwise order when viewed from outside.

    See: skills/data/scientific/cad-mesh-generation/SKILL.md

*See sub-skills for full details.*

## Export to WAMIT (GDF Format)


```python
def msh_to_gdf(msh_file: str, gdf_file: str, ulen: float = 1.0,
               gravity: float = 9.81):
    """Convert gmsh MSH to WAMIT/OrcaWave GDF format.

    See: skills/data/scientific/cad-mesh-generation/SKILL.md
    for complete GDF export implementation.
    """
    # GDF format reference:
    # Line 1: header

*See sub-skills for full details.*

## Export to Nemoh/BEMRosetta


```python
def export_for_nemoh(msh_file: str, nemoh_dir: str):
    """Export gmsh mesh for Nemoh solver.

    Nemoh expects mesh in its own format. Use BEMRosetta for conversion:
      BEMRosetta_cl.exe -mesh -i input.msh -o output.dat -f nemoh

    Alternative: export MSH v2.2 and use BEMRosetta CLI.
    """
    gmsh.initialize()

*See sub-skills for full details.*

## MSH v2.2 for BEM Tools


Many BEM tools require MSH v2.2 format (ASCII). Always set:

```python
gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
gmsh.option.setNumber("Mesh.Binary", 0)  # ASCII
gmsh.write("output.msh")
```

## Quality Targets for Hydrodynamic Analysis


| Metric | Target | Critical |
|--------|--------|----------|
| Panel count | 500-3000 | Min 200 per body |
| Aspect ratio | < 3:1 | < 5:1 |
| Adjacent panel ratio | < 2:1 | < 3:1 |
| Min panel angle | > 30° | > 15° |
| Panel size | ~L/20 to L/40 | Depends on frequency |
| Normals | Outward pointing | Consistent orientation |

**Rule of thumb**: Element size <= lambda/7 where lambda is the shortest wavelength of interest.
