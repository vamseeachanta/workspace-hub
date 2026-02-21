# Hull Analysis Setup Skill

Zero-config agent-callable wrapper that chains hull form lookup, mesh scaling,
mesh refinement, and RAO linking into a single call. Returns a structured result
ready for diffraction analysis — no catalog files or registry paths required for
the core lookup path.

## Invocation

```python
from digitalmodel.hydrodynamics.hull_library.analysis_setup import (
    HullAnalysisInput,
    setup_hull_analysis,
)

result = setup_hull_analysis(
    HullAnalysisInput(loa_m=250, beam_m=43, draft_m=11.5)
)
print(result.hull_id)           # "LNGC-250"
print(result.similarity_score)  # ~1.0 (exact match)
print(result.scaling_factors)   # {"loa": 1.0, "beam": 1.0, "draft": 1.0}
```

## Input: `HullAnalysisInput`

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `loa_m` | `float` | Yes | — | Length overall in metres (must be > 0) |
| `beam_m` | `float` | Yes | — | Breadth/beam in metres (must be > 0) |
| `draft_m` | `float` | Yes | — | Design draft in metres (must be > 0) |
| `displacement_t` | `float \| None` | No | `None` | Displacement in tonnes |
| `mesh_refinement_levels` | `int` | No | `1` | Quad-subdivision levels after scaling; 0 = skip refinement |
| `include_rao` | `bool` | No | `True` | Attempt RAO registry lookup; graceful fallback if missing |

Raises `ValueError` for missing or non-positive required dimensions.

## Output: `HullAnalysisResult`

| Attribute | Type | Description |
|---|---|---|
| `hull_id` | `str` | Selected hull identifier (e.g. `"LNGC-250"`) |
| `similarity_score` | `float` | Normalised match quality in [0, 1]; 1.0 = exact match |
| `scaling_factors` | `dict` | `{"loa": float, "beam": float, "draft": float}` — scale ratios applied to resize reference hull |
| `mesh_quality` | `dict \| None` | Quality metrics if PanelMesh pipeline succeeded; `None` for catalog-only or builtin hulls |
| `rao_available` | `bool` | True if RAO data was found in the registry |
| `rao_data` | `dict \| None` | Full RAO dataset dict if available, else `None` |
| `summary` | `dict` | Human-readable summary with `hull_id`, target dims, scaling, and optional panel count |
| `source` | `str` | Always `"skill:hull_analysis_setup"` |

### `mesh_quality` dict keys (when not None)

| Key | Type | Description |
|---|---|---|
| `panel_count` | `int` | Total panel count after scaling + refinement |
| `vertex_count` | `int` | Total vertex count |
| `min_area` | `float` | Minimum panel area (m²) |
| `max_area` | `float` | Maximum panel area (m²) |
| `mean_area` | `float` | Mean panel area (m²) |
| `total_area` | `float` | Total wetted surface area (m²) |
| `min_aspect_ratio` | `float` | Best (lowest) panel aspect ratio |
| `max_aspect_ratio` | `float` | Worst (highest) panel aspect ratio |
| `mean_aspect_ratio` | `float` | Mean panel aspect ratio |
| `degenerate_count` | `int` | Panels with area < 1e-6 m² |

## Processing Chain

```
HullAnalysisInput
    │
    ├─ 1. Validation — ValueError on non-positive dims
    │
    ├─ 2. HullLookup.get_hull_form()
    │       Normalised L2 distance across [loa, beam, draft]
    │       Falls back to built-in fleet (8 hull forms) when no catalog
    │
    ├─ 3. Mesh pipeline (optional, graceful fallback)
    │       Only runs if matched_entry is a PanelCatalogEntry with a
    │       resolvable HullProfile in HullCatalog.
    │       a. HullMeshGenerator.generate() → source PanelMesh
    │       b. scale_mesh_to_target() → scaled PanelMesh
    │       c. refine_mesh(levels=N) → refined PanelMesh (if levels > 0)
    │       d. compute_quality_metrics() → mesh_quality dict
    │       Any failure → mesh_quality = None, proceed
    │
    └─ 4. RAO lookup (optional, graceful fallback)
            Only runs when include_rao=True and raos_dir is provided.
            RaoRegistry.get_raos(hull_id, draft_m) → RaoReference list
            registry.load_rao_data(refs[0]) → rao_data dict
            Not found or file missing → rao_available=False, rao_data=None
```

## Built-in Hull Set

The fallback hull set (used when no catalog is provided) covers:

| Hull ID | LOA (m) | Beam (m) | Draft (m) | Type |
|---|---|---|---|---|
| BOX-50 | 50 | 12 | 2.0 | Small barge/box |
| FST-100 | 100 | 18 | 5.5 | Fast ship |
| FST-150 | 150 | 25 | 7.0 | Fast ship |
| SEMI-100 | 100 | 80 | 22.0 | Semi-submersible |
| LNGC-250 | 250 | 43 | 11.5 | LNG carrier |
| FPSO-260 | 260 | 46 | 14.0 | FPSO |
| LNGC-300 | 300 | 50 | 13.0 | Large LNG carrier |
| FPSO-320 | 320 | 60 | 18.0 | Large FPSO |

## Examples

```python
# Minimal — hull lookup only (no mesh file, no RAO dir)
from digitalmodel.hydrodynamics.hull_library.analysis_setup import (
    HullAnalysisInput, setup_hull_analysis,
)

result = setup_hull_analysis(HullAnalysisInput(loa_m=250, beam_m=43, draft_m=11.5))
# result.hull_id == "LNGC-250"
# result.similarity_score ≈ 1.0
# result.mesh_quality is None   (builtin hulls have no PanelMesh)
# result.rao_available is False (no raos_dir provided)

# Skip RAO lookup explicitly
result = setup_hull_analysis(
    HullAnalysisInput(loa_m=320, beam_m=60, draft_m=18, include_rao=False)
)

# No mesh refinement
result = setup_hull_analysis(
    HullAnalysisInput(loa_m=150, beam_m=25, draft_m=7, mesh_refinement_levels=0)
)

# Full pipeline with RAO registry
from pathlib import Path
result = setup_hull_analysis(
    HullAnalysisInput(loa_m=250, beam_m=43, draft_m=11.5),
    raos_dir=Path("data/raos"),
)
if result.rao_available:
    freqs = result.rao_data["frequencies_rad_s"]
```

## Fallback Behaviour

| Condition | Behaviour |
|---|---|
| No catalog provided | Uses built-in 8-hull fleet |
| PanelMesh not available for matched hull | `mesh_quality = None`, no exception |
| `mesh_refinement_levels = 0` | Scaling still attempted; refinement skipped |
| `include_rao = False` | `rao_available = False`, `rao_data = None`, no registry query |
| `raos_dir = None` | `rao_available = False`, `rao_data = None` |
| RAO file missing from disk | Warning logged, `rao_available = False` |
| Any unexpected exception in mesh/RAO step | Warning logged, step skipped, result returned |

## Module Location

- Skill implementation: `digitalmodel/src/digitalmodel/hydrodynamics/hull_library/analysis_setup.py`
- Skill name constant: `SKILL_NAME = "hull_analysis_setup"`
- Tests: `digitalmodel/tests/hydrodynamics/hull_library/test_analysis_setup.py`
