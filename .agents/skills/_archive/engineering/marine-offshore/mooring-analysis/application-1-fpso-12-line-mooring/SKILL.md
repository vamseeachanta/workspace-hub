---
name: mooring-analysis-application-1-fpso-12-line-mooring
description: 'Sub-skill of mooring-analysis: Application 1: FPSO 12-Line Mooring (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Application 1: FPSO 12-Line Mooring (+1)

## Application 1: FPSO 12-Line Mooring


```yaml
mooring_configuration:
  vessel: "FPSO"
  water_depth: 1500  # m
  number_of_lines: 12
  configuration: "3x4 spread"  # 3 bundles, 4 lines each

  line_composition:
    upper_chain:
      length: 500  # m
      diameter: 127  # mm
      grade: "R4"
    wire_rope:
      length: 1000  # m
      diameter: 120  # mm
      construction: "6x36 IWRC"
    lower_chain:
      length: 500  # m
      diameter: 127  # mm
      grade: "R4"

  pretension:
    target: 2000  # kN per line
    tolerance: "+/-10%"

  anchor:
    type: "drag_embedment"
    capacity: 5000  # kN
    safety_factor: 2.0
```


## Application 2: Mooring Integrity Check


```python
def mooring_integrity_check(
    tension: float,  # kN
    MBL: float,      # kN
    safety_factor: float
) -> dict:
    """
    Check mooring line integrity against criteria.

    Args:
        tension: Applied tension
        MBL: Minimum Breaking Load
        safety_factor: Required safety factor

    Returns:
        Check results
    """
    utilization = tension / (MBL / safety_factor)
    passed = utilization <= 1.0

    return {
        'tension_kN': tension,
        'MBL_kN': MBL,
        'allowable_tension_kN': MBL / safety_factor,
        'utilization': utilization,
        'passed': passed,
        'margin': (1.0 - utilization) * 100  # Percent
    }
```
