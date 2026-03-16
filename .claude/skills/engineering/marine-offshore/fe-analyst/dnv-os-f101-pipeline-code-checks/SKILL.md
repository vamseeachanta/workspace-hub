---
name: fe-analyst-dnv-os-f101-pipeline-code-checks
description: 'Sub-skill of fe-analyst: DNV-OS-F101 Pipeline Code Checks (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# DNV-OS-F101 Pipeline Code Checks (+2)

## DNV-OS-F101 Pipeline Code Checks


```python
def check_pipeline_utilization(Te, Mx, My, Pi, Pe, D, t, SMYS, SMTS, alpha_fab=0.96):
    """
    DNV-OS-F101 combined loading utilization check for pipelines.
    Sec.5 D400 — system collapse check (simplified).
    """
    # Pressure containment
    p_b = (2 * t * SMYS) / (D - t)  # Burst pressure
    UC_pressure = (Pi - Pe) / p_b

    # Bending + tension utilization (DNV Eq. D-5)
    M_resultant = (Mx**2 + My**2)**0.5
    M_p = SMYS * (D - t)**2 * t    # Plastic moment capacity
    T_yield = SMYS * math.pi * (D - t) * t   # Yield tension

    UC_combined = (M_resultant / M_p)**2 + (Te / T_yield)**2

    return {
        "UC_pressure": UC_pressure,
        "UC_combined": UC_combined,
        "PASS_pressure": UC_pressure < 1.0,
        "PASS_combined": UC_combined < 1.0,
    }
```


## API RP 2RD Riser Code Checks


```
UC_axial = |Te| / (SMYS × A_steel)                          # ≤ 0.67 (ASD)
UC_bending = |M_resultant| × (OD/2) / (SMYS × I / (OD/2))  # ≤ 0.75
UC_combined = UC_axial + UC_bending                         # ≤ 1.0
```


## Design Check Summary Table (Report Format)


| Check | Value | Allowable | UC | Status |
|---|---|---|---|---|
| Effective tension (min) | > 0 kN | > 0 kN | — | ✅ PASS |
| Burst pressure | 15.2 MPa | 20.1 MPa | 0.76 | ✅ PASS |
| Combined bending + tension | — | — | 0.82 | ✅ PASS |
| Curvature at TDP | 0.08 1/m | 0.10 1/m | 0.80 | ✅ PASS |
| Fatigue damage | 0.07 | 0.10 | 0.70 | ✅ PASS |

---
