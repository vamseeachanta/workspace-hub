---
name: orcaflex-visualization-orcawave-mesh-export-via-diffraction
description: 'Sub-skill of orcaflex-visualization: OrcaWave Mesh Export via Diffraction
  (+4).'
version: 1.1.0
category: engineering
type: reference
scripts_exempt: true
---

# OrcaWave Mesh Export via Diffraction (+4)

## OrcaWave Mesh Export via Diffraction


`OrcFxAPI.Diffraction` exposes mesh export methods that output GDF geometry files.
These can be parsed and rendered programmatically (Plotly 3D mesh → Figure 30 style).

```python
import OrcFxAPI as ofx

d = ofx.Diffraction()
d.LoadData("model.owd")           # or d.LoadResults("model.owr")

# Body mesh (GDF format) — corresponds to red mesh in Figure 30

*See sub-skills for full details.*

## Programmatic Mesh Rendering (Plotly — Figure 30 style)


Since `SaveModelView` is not available, render mesh from GDF/panelGeometry data:

```python
import numpy as np
import plotly.graph_objects as go

def gdf_to_mesh3d(gdf_path, color="red"):
    """Parse WAMIT GDF file and return Plotly Mesh3d trace."""
    panels = []
    with open(gdf_path) as f:

*See sub-skills for full details.*

## OrcaFlex: Canonical SaveModelView Pattern


```python
import OrcFxAPI as ofx

def save_model_view(model: ofx.Model, filepath: str, **view_params):
    """Save OrcaFlex model screenshot. NOT available for OrcaWave."""
    vp = model.defaultViewParameters
    for k, v in view_params.items():
        if hasattr(vp, k):
            setattr(vp, k, v)
    model.SaveModelView(str(filepath), vp)

*See sub-skills for full details.*

## Existing Codebase Implementations


| Script / Module | Coverage | Notes |
|----------------|----------|-------|
| `scripts/capture_riser_views.py` | Minimal `SaveModelView` | OrcaFlex `.dat`; verified |
| `src/.../orcaflex/pipeline_schematic.py` | Multi-view YAML config | `OrcaFlexViewCapture` class |
| `src/.../orcaflex/opp_visualization.py` | Batch parallel (30 workers) | `save_all_views()` |
| `scripts/benchmark/qtf_postprocessing.py` | `panelGeometry` 3D scatter | OrcaWave body panels, used in benchmark report |
| `scripts/build_sme_report.py` | `img_to_base64()` | HTML embedding of BMP/PNG/JPG |

For HTML embedding use `img_to_base64()` from `scripts/build_sme_report.py` —
converts BMP/PNG/JPG to `data:image/...;base64` URI for inline `<img>` tags.

## panelGeometry Structured Array Schema


`d.panelGeometry` returns a numpy structured array (one record per panel):

```
dtype fields:
  objectId          int32       body object index
  objectName        str (U31)   body name e.g. 'test101 bottom mounted cylinder'
  vertices          float64 (4,3) four quad panel corners [x, y, z] metres
  centroid          float64 (3)  panel centroid [x, y, z]
  normal            float64 (3)  outward unit normal vector
  area              float64      panel area (m²)

*See sub-skills for full details.*
