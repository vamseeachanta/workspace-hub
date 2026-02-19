---
name: mesh-utilities
version: 1.0.0
description: Quick mesh inspection, conversion, quality checks, and coarsening for hydrodynamic solvers
author: workspace-hub
category: engineering-utilities
tags: [mesh, gdf, dat, stl, bem, panel-mesh, quality, coarsening, aqwa, orcawave, bemrosetta]
platforms: [engineering]
invocation: /mesh
capabilities: []
requires: []
see_also: []
---

# Mesh Utilities Skill

Quick mesh handling for hydrodynamic analysis: inspect, convert, validate, and coarsen panel meshes before running complex solver analyses. Saves significant time by catching mesh issues early.

## When to Use This Skill

Use mesh utilities when you need to:
- **Quick inspect** - View mesh statistics (panels, vertices, bounding box) before running solvers
- **Format conversion** - Convert between GDF (OrcaWave/WAMIT), DAT (AQWA/NEMOH), and STL
- **Quality validation** - Check watertightness, normals, aspect ratios, panel counts
- **Mesh coarsening** - Reduce panel count for faster preliminary runs
- **Pre-solver checks** - Validate mesh suitability for specific solvers (AQWA, OrcaWave, BEMRosetta)

## Quick Reference

### Supported Formats

| Format | Extension | Solvers | Description |
|--------|-----------|---------|-------------|
| **GDF** | `.gdf` | WAMIT, OrcaWave | Panel definition with vertices and quads/tris |
| **DAT** | `.dat` | AQWA, NEMOH | Panel mesh for BEM solvers |
| **STL** | `.stl` | Visualization | Surface triangulation (ASCII or binary) |

### Quality Thresholds

| Metric | Good | Acceptable | Warning |
|--------|------|------------|---------|
| Aspect Ratio | < 2.0 | < 3.0 | > 5.0 |
| Panel Count | 500-5000 | 100-15000 | > 20000 |
| Degenerate Panels | 0 | 0-5 | > 5 |
| Duplicate Vertices | 0 | 0-10 | > 50 |
| Normals Consistent | Yes | Yes | No |

## Core Operations

### 1. Quick Mesh Inspection

```python
from digitalmodel.hydrodynamics.bemrosetta.mesh import GDFHandler
from pathlib import Path

def inspect_mesh(mesh_path: str) -> dict:
    """Quick inspection of panel mesh file."""
    path = Path(mesh_path)

    if path.suffix.lower() == '.gdf':
        handler = GDFHandler()
        mesh = handler.read(path)
    elif path.suffix.lower() == '.dat':
        from digitalmodel.hydrodynamics.bemrosetta.mesh import DATHandler
        handler = DATHandler()
        mesh = handler.read(path)
    elif path.suffix.lower() == '.stl':
        from digitalmodel.hydrodynamics.bemrosetta.mesh import STLHandler
        handler = STLHandler()
        mesh = handler.read(path)
    else:
        raise ValueError(f"Unsupported format: {path.suffix}")

    stats = {
        'file': str(path),
        'format': path.suffix.upper(),
        'n_panels': mesh.n_panels,
        'n_vertices': mesh.n_vertices,
        'total_area': mesh.total_area,
        'bounding_box': mesh.bounding_box,
        'is_quad_mesh': mesh.is_quad_mesh,
        'is_tri_mesh': mesh.is_tri_mesh,
        'symmetry': mesh.symmetry_plane,
    }

    print(f"Mesh: {path.name}")
    print(f"  Panels:   {stats['n_panels']}")
    print(f"  Vertices: {stats['n_vertices']}")
    print(f"  Area:     {stats['total_area']:.2f} m²")
    print(f"  Type:     {'Quads' if stats['is_quad_mesh'] else 'Tris' if stats['is_tri_mesh'] else 'Mixed'}")

    return stats

# Usage
stats = inspect_mesh("vessel.gdf")
```

### 2. Format Conversion

```python
from digitalmodel.hydrodynamics.diffraction.mesh_pipeline import MeshPipeline

def convert_mesh(
    input_path: str,
    output_format: str,
    output_dir: str = "."
) -> str:
    """Convert mesh between formats (GDF, DAT, STL)."""
    pipeline = MeshPipeline()

    # Load mesh
    mesh = pipeline.load(input_path)

    # Convert and save
    output_path = pipeline.convert(mesh, output_format, output_dir)

    print(f"Converted: {input_path} -> {output_path}")
    return str(output_path)

# Examples
convert_mesh("vessel.gdf", "dat", "output/")  # GDF -> DAT
convert_mesh("hull.stl", "gdf", "output/")     # STL -> GDF
convert_mesh("model.dat", "stl", "output/")    # DAT -> STL
```

### 3. Quality Validation

```python
from digitalmodel.hydrodynamics.diffraction.geometry_quality import (
    GeometryQualityChecker,
)

def validate_mesh_quality(mesh_path: str) -> dict:
    """Run full quality validation on mesh."""
    checker = GeometryQualityChecker()
    report = checker.generate_report(mesh_path)

    print(f"Quality Report: {mesh_path}")
    print(f"  Valid:        {report.is_valid}")
    print(f"  Quality Score: {report.quality_score:.1f}/100")
    print(f"  Panels:       {report.n_panels}")
    print(f"  Aspect Ratio: {report.aspect_ratio_max:.2f} (max)")
    print(f"  Watertight:   {'Yes' if report.is_watertight else 'No'}")
    print(f"  Normals OK:   {'Yes' if report.normals_consistent else 'No'}")

    if report.warnings:
        print("  Warnings:")
        for w in report.warnings:
            print(f"    - {w}")

    if report.errors:
        print("  Errors:")
        for e in report.errors:
            print(f"    - {e}")

    return report.to_dict()

# Usage
quality = validate_mesh_quality("barge.gdf")
```

### 4. Prepare Mesh for Solver

```python
from digitalmodel.hydrodynamics.diffraction.mesh_pipeline import MeshPipeline

def prepare_for_solver(
    mesh_path: str,
    solver: str,
    output_dir: str = "solver_input"
) -> str:
    """Prepare mesh for specific solver with validation.

    Args:
        mesh_path: Path to input mesh
        solver: Target solver ("aqwa", "orcawave", "bemrosetta")
        output_dir: Output directory

    Returns:
        Path to solver-ready mesh file
    """
    pipeline = MeshPipeline()

    # Validate and convert
    output_path = pipeline.prepare_for_solver(
        mesh_path=mesh_path,
        solver=solver,
        output_dir=output_dir
    )

    print(f"Prepared mesh for {solver.upper()}: {output_path}")
    return str(output_path)

# Examples
prepare_for_solver("vessel.stl", "aqwa")      # -> vessel.dat
prepare_for_solver("vessel.dat", "orcawave")  # -> vessel.gdf
```

### 5. Mesh Coarsening (Decimation)

```python
import numpy as np
from pathlib import Path

def coarsen_mesh_simple(
    mesh_path: str,
    target_panels: int,
    output_path: str = None
) -> str:
    """Simple mesh coarsening by vertex clustering.

    For more sophisticated coarsening, use GMSH remeshing
    or external tools (VTK, PyVista).

    Args:
        mesh_path: Path to input mesh
        target_panels: Target number of panels
        output_path: Output path (auto-generated if None)

    Returns:
        Path to coarsened mesh
    """
    from digitalmodel.hydrodynamics.bemrosetta.mesh import GDFHandler

    handler = GDFHandler()
    mesh = handler.read(mesh_path)

    current_panels = mesh.n_panels
    if current_panels <= target_panels:
        print(f"Mesh already has {current_panels} panels (target: {target_panels})")
        return mesh_path

    # Calculate reduction ratio
    ratio = target_panels / current_panels

    # Simple approach: skip every N panels
    keep_every = int(1 / ratio)

    # Select panels to keep
    keep_indices = np.arange(0, current_panels, keep_every)

    # Create reduced mesh
    reduced_panels = mesh.panels[keep_indices]

    # Find unique vertices
    unique_verts, inverse = np.unique(
        reduced_panels.flatten(),
        return_inverse=True
    )
    reduced_vertices = mesh.vertices[unique_verts]
    reduced_panels = inverse.reshape(-1, reduced_panels.shape[1])

    # Save
    if output_path is None:
        p = Path(mesh_path)
        output_path = p.parent / f"{p.stem}_coarse_{len(keep_indices)}p{p.suffix}"

    handler.write(output_path, reduced_vertices, reduced_panels)

    print(f"Coarsened: {current_panels} -> {len(keep_indices)} panels")
    print(f"Output: {output_path}")

    return str(output_path)

# Usage
coarsen_mesh_simple("detailed_hull.gdf", target_panels=500)
```

### 6. GMSH-Based Mesh Generation

```python
from digitalmodel.solvers.gmsh_meshing import GMSHMeshGenerator

def generate_simple_hull_mesh(
    length: float,
    beam: float,
    draft: float,
    panel_size: float = 2.0,
    output_path: str = "hull.gdf"
) -> str:
    """Generate simple barge mesh using GMSH.

    Args:
        length: Hull length (m)
        beam: Hull beam (m)
        draft: Hull draft (m)
        panel_size: Target panel size (m)
        output_path: Output file path

    Returns:
        Path to generated mesh
    """
    generator = GMSHMeshGenerator()

    mesh = generator.generate_simple_box_mesh(
        length=length,
        width=beam,
        depth=draft,
        element_size=panel_size
    )

    # Export to GDF
    mesh.export(output_path, format='gdf')

    print(f"Generated barge mesh: {length}L x {beam}B x {draft}D")
    print(f"  Panels: ~{mesh.n_panels}")
    print(f"  Output: {output_path}")

    return output_path

# Example: 100m barge
generate_simple_hull_mesh(100, 30, 6, panel_size=3.0)
```

## Batch Operations

### Batch Quality Check

```python
from pathlib import Path

def batch_quality_check(mesh_dir: str, pattern: str = "*.gdf") -> dict:
    """Run quality checks on multiple meshes.

    Args:
        mesh_dir: Directory containing meshes
        pattern: Glob pattern for mesh files

    Returns:
        Summary of quality results
    """
    from digitalmodel.hydrodynamics.diffraction.geometry_quality import (
        GeometryQualityChecker,
    )

    mesh_path = Path(mesh_dir)
    checker = GeometryQualityChecker()

    results = []
    for mesh_file in mesh_path.glob(pattern):
        try:
            report = checker.generate_report(str(mesh_file))
            results.append({
                'file': mesh_file.name,
                'valid': report.is_valid,
                'score': report.quality_score,
                'panels': report.n_panels,
                'warnings': len(report.warnings),
                'errors': len(report.errors),
            })
        except Exception as e:
            results.append({
                'file': mesh_file.name,
                'valid': False,
                'error': str(e),
            })

    # Summary
    valid_count = sum(1 for r in results if r.get('valid', False))
    print(f"Batch Quality Check: {mesh_dir}")
    print(f"  Total meshes: {len(results)}")
    print(f"  Valid: {valid_count}/{len(results)}")

    # Show issues
    for r in results:
        if not r.get('valid', False):
            print(f"  ! {r['file']}: {r.get('error', 'quality issues')}")

    return {'results': results, 'valid_count': valid_count}

# Usage
batch_quality_check("meshes/hulls/", "*.gdf")
```

### Batch Conversion

```python
def batch_convert(
    input_dir: str,
    input_pattern: str,
    output_format: str,
    output_dir: str
) -> list:
    """Convert multiple meshes to a target format.

    Args:
        input_dir: Input directory
        input_pattern: Glob pattern (e.g., "*.stl")
        output_format: Target format ("gdf", "dat", "stl")
        output_dir: Output directory

    Returns:
        List of converted file paths
    """
    from pathlib import Path
    from digitalmodel.hydrodynamics.diffraction.mesh_pipeline import MeshPipeline

    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    pipeline = MeshPipeline()
    converted = []

    for mesh_file in input_path.glob(input_pattern):
        try:
            mesh = pipeline.load(str(mesh_file))
            out_file = output_path / f"{mesh_file.stem}.{output_format}"
            pipeline.convert(mesh, output_format, str(out_file))
            converted.append(str(out_file))
            print(f"  Converted: {mesh_file.name} -> {out_file.name}")
        except Exception as e:
            print(f"  Failed: {mesh_file.name} - {e}")

    print(f"Batch conversion complete: {len(converted)} files")
    return converted

# Example: Convert all STL files to GDF
batch_convert("cad_exports/", "*.stl", "gdf", "orcawave_input/")
```

## Pre-Solver Checklist

Before running AQWA, OrcaWave, or BEMRosetta, verify:

```python
def pre_solver_checklist(mesh_path: str, solver: str) -> bool:
    """Run pre-solver validation checklist.

    Args:
        mesh_path: Path to mesh file
        solver: Target solver name

    Returns:
        True if mesh passes all checks
    """
    from digitalmodel.hydrodynamics.bemrosetta.mesh import BaseMeshHandler
    from digitalmodel.hydrodynamics.diffraction.geometry_quality import (
        GeometryQualityChecker,
    )

    handler = BaseMeshHandler()
    mesh = handler.read(mesh_path)

    checker = GeometryQualityChecker()
    report = checker.generate_report(mesh_path)

    checks = {
        'format_ok': True,  # Will check below
        'panel_count_ok': 100 <= mesh.n_panels <= 20000,
        'aspect_ratio_ok': report.aspect_ratio_max < 5.0,
        'no_degenerates': report.n_degenerate_panels == 0,
        'normals_consistent': report.normals_consistent,
        'watertight': report.is_watertight,
    }

    # Solver-specific checks
    if solver.lower() == 'aqwa':
        checks['format_ok'] = mesh_path.endswith('.dat')
    elif solver.lower() == 'orcawave':
        checks['format_ok'] = mesh_path.endswith('.gdf')
    elif solver.lower() == 'bemrosetta':
        checks['format_ok'] = mesh_path.endswith(('.gdf', '.dat'))

    # Print results
    print(f"Pre-solver Checklist: {mesh_path}")
    print(f"  Target solver: {solver.upper()}")
    print()

    all_pass = True
    for check, passed in checks.items():
        status = "[OK]" if passed else "[FAIL]"
        print(f"  {status} {check.replace('_', ' ').title()}")
        if not passed:
            all_pass = False

    print()
    if all_pass:
        print("  All checks passed - mesh ready for solver")
    else:
        print("  Some checks failed - review mesh before running")

    return all_pass

# Usage
pre_solver_checklist("vessel.gdf", "orcawave")
```

## CLI Usage

```bash
# Quick inspection
uv run python -c "from mesh_utilities import inspect_mesh; inspect_mesh('vessel.gdf')"

# Quality check
uv run python -c "from mesh_utilities import validate_mesh_quality; validate_mesh_quality('hull.gdf')"

# Conversion
uv run python -c "from mesh_utilities import convert_mesh; convert_mesh('hull.stl', 'gdf', 'output/')"

# Pre-solver check
uv run python -c "from mesh_utilities import pre_solver_checklist; pre_solver_checklist('model.gdf', 'orcawave')"
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| High aspect ratio | Long thin panels | Remesh with more uniform element size |
| Degenerate panels | Collapsed vertices | Clean mesh, remove zero-area panels |
| Inconsistent normals | Mixed orientation | Flip normals to all point outward |
| Not watertight | Gaps/holes in mesh | Check model, close holes |
| Too many panels | Over-refined mesh | Coarsen or regenerate with larger element size |
| Wrong format | Solver incompatibility | Convert to solver-required format |

## Related Skills

- **hydrodynamic-analysis** - BEM theory, RAOs, added mass/damping
- **orcaflex-specialist** - OrcaFlex integration
- **gmsh-meshing** - Advanced mesh generation

---

**Use this skill for quick mesh checks before running expensive solver analyses!**
