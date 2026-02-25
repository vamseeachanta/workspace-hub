---
name: freecad-automation
description: AI-powered automation agent for FreeCAD CAD operations including natural
  language processing, batch processing, parametric design, and marine engineering
  applications. Use for CAD automation, drawing generation, FEM preprocessing, and
  integration with offshore analysis tools.
version: 1.0.0
updated: 2025-01-02
category: cad-engineering
triggers:
- FreeCAD automation
- parametric modeling
- CAD batch processing
- technical drawings
- assembly management
- FEM preprocessing
- hull design
- marine CAD
- .FCStd files
- Python scripting CAD
capabilities:
- input_generation
- execution
- output_parsing
- failure_diagnosis
- validation
requires: []
see_also: []
---
# FreeCAD Automation Skill

AI-powered automation for FreeCAD CAD operations with natural language processing, batch processing, and marine engineering specialization.

## Version Metadata

```yaml
version: 1.0.0
python_min_version: '3.10'
dependencies:
  cad-engineering: '>=1.0.0,<2.0.0'
  gmsh-meshing: '>=1.0.0,<2.0.0'
compatibility:
  tested_python:
  - '3.10'
  - '3.11'
  - '3.12'
  - '3.13'
  os:
  - Windows
  - Linux
  - macOS
```

## Changelog

### [1.0.0] - 2026-01-07

**Added:**
- Initial version metadata and dependency management
- Semantic versioning support
- Compatibility information for Python 3.10-3.13

**Changed:**
- Enhanced skill documentation structure


## When to Use

- CAD automation and scripting
- Batch processing of FreeCAD files
- Parametric design and design tables
- Assembly management and constraint solving
- FEM preprocessing and mesh generation
- Drawing generation with automatic dimensioning
- Marine engineering hull design
- Natural language CAD commands
- Integration with OrcaFlex/AQWA workflows

## Agent Capabilities

This skill integrates agent capabilities from `/agents/freecad/`:

### Core Capabilities
- **CAD Automation**: Script-based FreeCAD operations
- **Batch Processing**: Parallel file processing with pattern matching
- **Parametric Design**: Design tables and parameter variations
- **Assembly Management**: Constraint solving and assembly creation
- **FEM Preprocessing**: Mesh generation and boundary conditions
- **Drawing Generation**: Automatic dimensioning and views
- **Natural Language Processing**: Convert commands to CAD operations
- **Script Generation**: Auto-generate Python scripts from prompts

### Marine Engineering Specialization
- Hull design automation
- Stability calculations
- Mooring system configuration
- Structural analysis preprocessing

### Integration Points
- **OrcaFlex**: Data exchange for hydrodynamic analysis
- **AQWA**: Diffraction analysis geometry
- **Signal Analysis**: Module connectivity
- **REST API**: External system integration

## Prerequisites

- Python 3.8+
- FreeCAD 1.0+ (November 2024 release)
- `digitalmodel` package installed

## Configuration

### Agent Settings

```json
{
  "settings": {
    "parallel_workers": 4,
    "max_workers": 8,
    "cache_enabled": true,
    "cache_size_mb": 500,
    "auto_save": true,
    "auto_save_interval": 300,
    "validation_level": "strict",
    "error_recovery": true,
    "retry_attempts": 3,
    "timeout_seconds": 600
  }
}
```

### Marine Engineering Settings

```json
{
  "marine_engineering": {
    "units": "metric",
    "standards": ["DNV", "ABS", "API"],
    "vessel_types": ["FPSO", "FSO", "FLNG", "Semi-sub", "TLP", "Spar"],
    "analysis_types": ["stability", "mooring", "structural", "hydrodynamic"]
  }
}
```

## Python API

### Basic Operations

```python
from digitalmodel.agents.freecad import FreeCADAgent

# Initialize agent
agent = FreeCADAgent()

# Natural language operation
result = agent.execute_prompt("Create a box 100x50x25mm with chamfered edges")

# Check result
print(f"Created: {result['object_name']}")
print(f"Volume: {result['properties']['volume']} mm3")
```

### Batch Processing

```python
# Batch processing with pattern matching
results = agent.batch_process(
    pattern="*.FCStd",
    input_directory="./models",
    operation="export_step",
    parallel_workers=4
)

# Process results
for file_name, result in results.items():
    if result["success"]:
        print(f"Exported: {file_name}")
    else:
        print(f"Failed: {file_name} - {result['error']}")
```

### Parametric Design

```python
# Generate parametric variations
agent.parametric_study(
    base_model="hull_template.FCStd",
    parameters={
        "length": [150, 175, 200, 225],
        "beam": [25, 30, 35],
        "draft": [10, 12, 15]
    },
    output_directory="hull_variations/",
    export_formats=["STEP", "STL"]
)
```

### Script Generation

```python
# Generate Python script from natural language
script = agent.generate_script(
    "Create parametric gear with 20 teeth, module 2mm,
     pressure angle 20 degrees, exportable to STEP"
)

# Save script
with open("gear_generator.py", "w") as f:
    f.write(script)

# Execute script
exec(script)
```

### Hull Design Automation

```python
from digitalmodel.agents.freecad.marine import HullDesigner

# Initialize hull designer
hull = HullDesigner()

# Create hull from parameters
hull_model = hull.create(
    length=280.0,
    beam=48.0,
    depth=26.0,
    draft=18.0,
    block_coefficient=0.85,
    hull_type="FPSO"
)

# Generate panel mesh for hydrodynamics
hull.generate_panel_mesh(
    model=hull_model,
    panel_size=2.0,
    output_file="hull_panels.dat"
)

# Export for OrcaFlex
hull.export_orcaflex(
    model=hull_model,
    output_file="orcaflex_models/fpso_hull.yml"
)
```

## Command Line Interface

```bash
# Show capabilities
python run_freecad_agent.py --show-capabilities

# Process single file
python run_freecad_agent.py --file model.FCStd --operation "add fillet radius 5mm"

# Batch processing
python run_freecad_agent.py \
    --pattern "*.FCStd" \
    --input-directory ./models \
    --output-directory ./exports \
    --parallel 4

# Natural language command
python run_freecad_agent.py \
    --prompt "Create a hull with 150m length and 25m beam"
```

## Batch Processing Patterns

| Pattern | Description |
|---------|-------------|
| `*.FCStd` | All FreeCAD files |
| `*_asm.FCStd` | Assembly files |
| `*_part.FCStd` | Part files |
| `*_drw.FCStd` | Drawing files |

## Output Formats

Supported export formats:
- **STEP** - Standard for CAD exchange
- **IGES** - Legacy CAD exchange
- **STL** - 3D printing, mesh applications
- **DXF** - 2D drawings
- **PDF** - Technical documentation

## MCP Tool Integration

### Swarm Coordination
```javascript
// Initialize CAD processing swarm
mcp__claude-flow__swarm_init { topology: "star", maxAgents: 4 }

// Spawn specialized agents
mcp__claude-flow__agent_spawn { type: "coder", name: "freecad-automator" }
mcp__claude-flow__agent_spawn { type: "reviewer", name: "geometry-validator" }
```

### Memory Coordination
```javascript
// Store CAD operation status
mcp__claude-flow__memory_usage {
  action: "store",
  key: "freecad/batch/status",
  namespace: "cad",
  value: JSON.stringify({
    operation: "batch_export",
    files_processed: 45,
    files_total: 100,
    format: "STEP"
  })
}

// Share geometry with analysis agents
mcp__claude-flow__memory_usage {
  action: "store",
  key: "freecad/geometry/hull",
  namespace: "shared",
  value: JSON.stringify({
    file: "hull_panels.dat",
    panels: 5000,
    ready_for_analysis: true
  })
}
```

## Performance Metrics

| Metric | Value |
|--------|-------|
| Batch Processing | Up to 5x faster than sequential |
| Memory Optimization | Efficient large assembly handling |
| Error Recovery | Automatic retry with exponential backoff |
| Caching | Intelligent operation caching |

## Error Handling

### FreeCAD Import Error
```python
# Add FreeCAD to Python path
import sys
sys.path.append('/path/to/FreeCAD/lib')
```

### Memory Issues
```python
# Reduce parallel workers for large files
agent = FreeCADAgent(config={
    "settings": {
        "parallel_workers": 2,
        "memory_limit_mb": 2048
    }
})
```

## Output Parsing

### Extract Geometry Properties

```python
import FreeCAD
import Part

def extract_geometry_properties(doc_path):
    """Extract geometric properties from FreeCAD document."""
    doc = FreeCAD.openDocument(doc_path)
    results = {}

    for obj in doc.Objects:
        if hasattr(obj, 'Shape') and obj.Shape:
            shape = obj.Shape
            results[obj.Name] = {
                "type": obj.TypeId,
                "volume_mm3": shape.Volume if hasattr(shape, 'Volume') else None,
                "area_mm2": shape.Area if hasattr(shape, 'Area') else None,
                "center_of_mass": tuple(shape.CenterOfMass) if shape.Volume > 0 else None,
                "bounding_box": {
                    "min": (shape.BoundBox.XMin, shape.BoundBox.YMin, shape.BoundBox.ZMin),
                    "max": (shape.BoundBox.XMax, shape.BoundBox.YMax, shape.BoundBox.ZMax),
                },
                "is_valid": shape.isValid(),
            }

    FreeCAD.closeDocument(doc.Name)
    return results
```

### Export Formats and CLI

```bash
# Export STEP from command line
freecadcmd -c "
import FreeCAD, Part
doc = FreeCAD.openDocument('model.FCStd')
Part.export(doc.Objects, 'output.step')
"

# Export STL
freecadcmd -c "
import FreeCAD, Mesh
doc = FreeCAD.openDocument('model.FCStd')
Mesh.export(doc.Objects, 'output.stl')
"
```

### Parse STEP/IGES Output Metadata

```python
import Part

def parse_export_stats(export_path):
    """Parse exported file and return statistics."""
    shape = Part.read(export_path)
    return {
        "solids": len(shape.Solids),
        "shells": len(shape.Shells),
        "faces": len(shape.Faces),
        "edges": len(shape.Edges),
        "vertices": len(shape.Vertexes),
        "volume_mm3": shape.Volume,
        "bounding_box_mm": {
            "x": shape.BoundBox.XLength,
            "y": shape.BoundBox.YLength,
            "z": shape.BoundBox.ZLength,
        },
    }
```

## Failure Diagnosis

### Common Failures

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'FreeCAD'` | FreeCAD not in Python path | Add to path: `sys.path.append('/usr/lib/freecad-daily/lib')` or use `freecadcmd` |
| `FreeCAD.openDocument(): file not found` | Wrong path or .FCStd corrupted | Check path; try opening in GUI first |
| `Part.BRepBuilderAPI: shape is not valid` | Invalid geometry (self-intersection) | Run `shape.fix(0.1, 0.1, 0.1)` or simplify geometry |
| `Mesh export produces 0-byte STL` | No mesh-compatible objects | Ensure objects have Shape; use Part before Mesh export |
| `Boolean operation failed` | Overlapping/touching geometry | Add small offset (0.01mm) between bodies; check geometry validity |
| `Recompute failed` | Sketches over-/under-constrained | Check `obj.Shape.isValid()` and sketch DOF count |
| `ImportError: No module named 'FreeCADGui'` | Running headless without GUI module (FreeCAD < 0.21) | FreeCAD ≥ 0.21: `freecadcmd` includes FreeCADGui (no-op window); safe to import. FreeCAD < 0.21: use `freecadcmd` and avoid Gui-dependent operations |

### Diagnostic Function

```python
import FreeCAD

def diagnose_freecad_model(doc_path):
    """Diagnose common FreeCAD model issues."""
    diag = {"issues": [], "warnings": [], "info": []}

    try:
        doc = FreeCAD.openDocument(doc_path)
    except Exception as e:
        diag["issues"].append(f"Cannot open document: {e}")
        return diag

    diag["info"].append(f"FreeCAD {FreeCAD.Version()[0]}.{FreeCAD.Version()[1]}")
    diag["info"].append(f"Objects: {len(doc.Objects)}")

    for obj in doc.Objects:
        # Check for invalid shapes
        if hasattr(obj, 'Shape'):
            if not obj.Shape.isValid():
                diag["issues"].append(f"{obj.Name}: invalid shape (self-intersection or gap)")

            if obj.Shape.Volume < 0:
                diag["warnings"].append(f"{obj.Name}: negative volume (inverted normals)")

        # Check for failed features
        if hasattr(obj, 'isValid') and not obj.isValid():
            diag["issues"].append(f"{obj.Name}: feature marked invalid — needs recompute")

        # Check sketches
        if obj.TypeId == 'Sketcher::SketchObject':
            dof = obj.solve()
            if dof > 0:
                diag["warnings"].append(f"{obj.Name}: {dof} unconstrained DOF")
            elif dof < 0:
                diag["issues"].append(f"{obj.Name}: over-constrained sketch")

    FreeCAD.closeDocument(doc.Name)
    return diag
```

### Headless Execution Troubleshooting

```bash
# FreeCAD headless (no GUI)
freecadcmd script.py

# If freecadcmd not found, use full path
/usr/bin/freecadcmd script.py

# Alternative: use FreeCAD with -c flag
freecad -c "exec(open('script.py').read())"

# Check FreeCAD Python path
python3 -c "import sys; sys.path.append('/usr/lib/freecad-daily/lib'); import FreeCAD; print(FreeCAD.Version())"
```

> **Note (FreeCAD ≥ 0.21):** `freecadcmd` includes `FreeCADGui` as a no-op stub — `import FreeCADGui` succeeds but GUI operations are non-functional. Safe to use in scripts that conditionally check for GUI availability.

## Validation

### Geometry Validation Checks

```python
def validate_geometry(doc_path, expected=None):
    """Validate FreeCAD geometry against expected parameters."""
    import FreeCAD
    import Part

    checks = {"passed": True, "issues": []}
    doc = FreeCAD.openDocument(doc_path)

    for obj in doc.Objects:
        if not hasattr(obj, 'Shape'):
            continue

        shape = obj.Shape

        # Shape validity
        if not shape.isValid():
            checks["issues"].append(f"{obj.Name}: invalid shape")
            checks["passed"] = False

        # Check for zero-volume solids
        if shape.ShapeType == 'Solid' and shape.Volume < 1e-6:
            checks["issues"].append(f"{obj.Name}: zero-volume solid")
            checks["passed"] = False

        # Check for degenerate faces
        for i, face in enumerate(shape.Faces):
            if face.Area < 1e-8:
                checks["issues"].append(f"{obj.Name}: degenerate face #{i}")

    # Compare against expected values
    if expected:
        total_volume = sum(
            obj.Shape.Volume for obj in doc.Objects
            if hasattr(obj, 'Shape') and obj.Shape.Volume > 0
        )
        if expected.get('volume_mm3'):
            ratio = total_volume / expected['volume_mm3']
            if abs(ratio - 1.0) > 0.05:
                checks["issues"].append(
                    f"Volume {total_volume:.1f} mm3 vs expected {expected['volume_mm3']:.1f} "
                    f"(diff {abs(ratio-1)*100:.1f}%)"
                )
                checks["passed"] = False

    FreeCAD.closeDocument(doc.Name)
    return checks
```

### Export Round-Trip Validation

```python
def validate_step_export(original_fcstd, exported_step):
    """Validate STEP export by comparing with original."""
    import FreeCAD
    import Part

    # Read original
    doc = FreeCAD.openDocument(original_fcstd)
    original_volume = sum(
        o.Shape.Volume for o in doc.Objects if hasattr(o, 'Shape') and o.Shape.Volume > 0
    )
    original_faces = sum(
        len(o.Shape.Faces) for o in doc.Objects if hasattr(o, 'Shape')
    )
    FreeCAD.closeDocument(doc.Name)

    # Read exported
    exported_shape = Part.read(exported_step)
    exported_volume = exported_shape.Volume
    exported_faces = len(exported_shape.Faces)

    checks = {"passed": True, "issues": []}

    vol_diff = abs(original_volume - exported_volume) / max(original_volume, 1e-10)
    if vol_diff > 0.01:
        checks["issues"].append(f"Volume diff {vol_diff*100:.2f}% (original={original_volume:.1f}, exported={exported_volume:.1f})")
        checks["passed"] = False

    checks["original_volume"] = original_volume
    checks["exported_volume"] = exported_volume
    checks["original_faces"] = original_faces
    checks["exported_faces"] = exported_faces
    return checks
```

| Check | Threshold | Action |
|-------|-----------|--------|
| Shape validity | `isValid() == True` | Fix with `shape.fix()` or rebuild |
| Volume | Non-zero for solids | Check boolean operations |
| Export volume match | < 1% difference | Check export settings (tolerance) |
| Sketch constraints | DOF == 0 | Add missing constraints |
| Bounding box | Within expected range | Check units (mm vs m) |

## Related Skills

- [gmsh-meshing](../gmsh-meshing/SKILL.md) - Advanced mesh generation
- [cad-engineering](../cad-engineering/SKILL.md) - General CAD expertise
- [blender-interface](../blender/SKILL.md) - 3D visualization
- [orcaflex-modeling](../../marine-offshore/orcaflex-modeling/SKILL.md) - Hydrodynamic analysis

## References

- FreeCAD Documentation: https://wiki.freecad.org/
- FreeCAD Python API: https://wiki.freecad.org/Python_scripting_tutorial
- Agent Configuration: `agents/freecad/agent_config.json`

---

## Version History

- **1.1.0** (2026-02-24): Added output parsing, failure diagnosis, and validation sections; fixed FreeCADGui availability in freecadcmd ≥ 0.21 (WRK-372 P2-ENHANCE, validated 35/36→36/36)
- **1.0.0** (2025-01-02): Initial release from agents/freecad/ configuration
