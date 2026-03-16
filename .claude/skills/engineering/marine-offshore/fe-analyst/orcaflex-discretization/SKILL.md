---
name: fe-analyst-orcaflex-discretization
description: 'Sub-skill of fe-analyst: OrcaFlex Discretization (+3).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# OrcaFlex Discretization (+3)

## OrcaFlex Discretization


OrcaFlex segments are the mesh elements. Each segment has:
- **Length**: controls resolution along the structure
- **Bend stiffness**: `EI` of the element
- **Mass**: lumped at nodes


## Mesh Quality Criteria


```python
def assess_mesh_quality(segment_lengths, OD, min_radius_of_curvature):
    """
    Assess FE mesh quality for a slender structure.

    Returns a dict of quality flags.
    """
    L_max = max(segment_lengths)
    L_min = min(segment_lengths)
    ratio = L_max / L_min

    # Rule 1: Segments should not be longer than ~5×OD in regions of high curvature
    max_seg_high_curve = min_radius_of_curvature * 0.1  # ~10 segs per 90° arc

    # Rule 2: Adjacent segment length ratio (gradual variation)
    from itertools import pairwise
    adjacent_ratios = [max(a, b) / min(a, b) for a, b in pairwise(segment_lengths)]
    max_adj_ratio = max(adjacent_ratios)

    # Rule 3: Minimum segment — avoid < OD/2 (over-discretized)
    over_refined = any(L < OD / 2 for L in segment_lengths)

    return {
        "total_segments": len(segment_lengths),
        "L_min_m": L_min,
        "L_max_m": L_max,
        "global_ratio": ratio,
        "max_adjacent_ratio": max_adj_ratio,   # flag if > 3.0
        "over_refined_segments": over_refined,
        "high_curvature_adequate": L_max <= max_seg_high_curve,
        "pass": max_adj_ratio <= 3.0 and not over_refined and L_min > 0.01,
    }
```


## Mesh Report Table Format


```
Mesh Summary:
┌─────────────────────┬──────────┬──────────┬──────────┬──────────┐
│ Region              │ N segs   │ L_min [m]│ L_max [m]│ Ratio    │
├─────────────────────┼──────────┼──────────┼──────────┼──────────┤
│ Top section         │ 20       │ 0.50     │ 1.00     │ 2.0  ✓  │
│ Mid catenary        │ 150      │ 1.00     │ 2.00     │ 2.0  ✓  │
│ TDP zone            │ 30       │ 0.25     │ 1.00     │ 4.0  ✗  │
│ Seabed section      │ 50       │ 1.00     │ 2.00     │ 2.0  ✓  │
└─────────────────────┴──────────┴──────────┴──────────┴──────────┘
TOTAL: 250 segments | PASS: 3/4 regions
```


## Refinement Guidelines by Region


| Region | Guideline | Reason |
|---|---|---|
| TDP zone | ≤ 0.5 × D | Highest curvature, most critical for fatigue |
| Sag bend | ≤ 1.0 × D | Second-highest curvature |
| Free catenary | ≤ 5.0 × D | Low curvature — efficiency |
| Seabed (laid) | ≤ 3.0 × D | Axial walking, upheaval |
| Near clamp/BSJ | ≤ 0.2 × D | Local stress concentration |
| Mooring at fairlead | ≤ 2.0 × D | Curvature under vessel offset |
| Stinger (S-lay) | ≤ 0.5 × D | Bending control critical |

---
