---
name: fe-analyst-key-results-to-extract-and-plot
description: 'Sub-skill of fe-analyst: Key Results to Extract and Plot (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Key Results to Extract and Plot (+1)

## Key Results to Extract and Plot


```python
RESULT_TYPES = {
    # Tension / Axial
    "effective_tension": {
        "unit": "kN",
        "positive": "tension",
        "check": "Te > 0 (no compression except upheaval buckling design)",
    },
    "wall_tension": {
        "unit": "kN",
        "note": "True wall tension = Te - Pi*Ai + Pe*Ae",
    },

    # Bending
    "x_bending_moment": {"unit": "kN·m"},
    "y_bending_moment": {"unit": "kN·m"},
    "resultant_bending_moment": {
        "unit": "kN·m",
        "computed": "sqrt(Mx² + My²)",
    },
    "curvature": {
        "unit": "1/m",
        "check": "κ < κ_allowable = 1 / (20×OD) typical",
    },

    # Stress
    "von_mises_stress": {"unit": "MPa", "check": "σ_vm < SMYS / γ_m"},
    "combined_utilization": {
        "unit": "−",
        "check": "UC < 1.0 per DNV-OS-F101 or API RP 2RD",
    },

    # Position
    "x_position": {"unit": "m"},
    "z_position": {"unit": "m"},
    "arc_length": {"unit": "m"},

    # Fatigue (if applicable)
    "fatigue_damage": {"unit": "−", "check": "D < 0.1 (factor 10 on 20-yr life)"},
}
```


## Statistical Summary Table


For each result variable, report:

| Statistic | Symbol | Description |
|---|---|---|
| Mean | μ | Time-average |
| Std Dev | σ | Dynamic variation |
| Maximum | max | Most extreme tensile / positive |
| Minimum | min | Most extreme compressive / negative |
| Max Absolute | |max| | Governing amplitude |
| MPM (Most Probable Maximum) | MPM = μ + √(2 ln N) × σ | Storm peak estimate |

---
