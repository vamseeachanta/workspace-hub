---
name: mooring-analysis-3-mooring-line-components
description: 'Sub-skill of mooring-analysis: 3. Mooring Line Components (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 3. Mooring Line Components (+1)

## 3. Mooring Line Components


**Chain:**
```python
def chain_properties(
    diameter: float,  # mm
    grade: str = "R4"
) -> dict:
    """
    Get chain properties.

    Args:
        diameter: Nominal chain diameter
        grade: Chain grade (R3, R4, R5)

    Returns:
        Chain properties
    """
    # Minimum Breaking Load (MBL) for studless chain
    # API RP 2SK Table 4-1
    grade_factors = {
        'R3': 0.0219,  # tonnes/mm²
        'R4': 0.0246,
        'R5': 0.0273
    }

    k = grade_factors.get(grade, 0.0246)
    MBL = k * diameter**2  # tonnes

    # Weight in air (approximate)
    weight_air = 0.0218 * diameter**2  # kg/m

    # Weight in water (steel in seawater)
    submerged_factor = (7.85 - 1.025) / 7.85  # Steel in seawater
    weight_water = weight_air * submerged_factor  # kg/m

    return {
        'diameter_mm': diameter,
        'grade': grade,
        'MBL_tonnes': MBL,
        'MBL_kN': MBL * 9.81,
        'weight_air_kg_m': weight_air,
        'weight_water_kg_m': weight_water
    }
```

**Wire Rope:**
```python
def wire_rope_properties(
    diameter: float,  # mm
    construction: str = "6x36"
) -> dict:
    """
    Get wire rope properties.

    Args:
        diameter: Wire rope diameter
        construction: Wire construction (6x36, 6x19, etc.)

    Returns:
        Wire properties
    """
    # Approximate MBL (6x36 IWRC)
    MBL = 0.0175 * diameter**2  # tonnes

    # Weight in air
    weight_air = 0.040 * diameter**2  # kg/m (steel core)

    # Weight in water
    submerged_factor = (7.85 - 1.025) / 7.85
    weight_water = weight_air * submerged_factor

    return {
        'diameter_mm': diameter,
        'construction': construction,
        'MBL_tonnes': MBL,
        'MBL_kN': MBL * 9.81,
        'weight_air_kg_m': weight_air,
        'weight_water_kg_m': weight_water
    }
```

**Polyester Rope:**
```python
def polyester_rope_properties(
    diameter: float,  # mm
    linear_density: float = None  # kg/m
) -> dict:
    """
    Get polyester rope properties.

    Args:
        diameter: Rope diameter
        linear_density: Mass per unit length (if known)

    Returns:
        Polyester properties
    """
    # Approximate MBL
    MBL = 0.0048 * diameter**2  # tonnes

    # Weight in air (if not provided)
    if linear_density is None:
        linear_density = 0.0045 * diameter**2  # kg/m

    # Weight in water (polyester is neutrally buoyant in seawater)
    # Specific gravity ~1.38, seawater ~1.025
    submerged_factor = (1.38 - 1.025) / 1.38
    weight_water = linear_density * submerged_factor

    # Axial stiffness (EA)
    EA = 850 * MBL  # kN (approximate)

    return {
        'diameter_mm': diameter,
        'MBL_tonnes': MBL,
        'MBL_kN': MBL * 9.81,
        'weight_air_kg_m': linear_density,
        'weight_water_kg_m': weight_water,
        'EA_kN': EA
    }
```


## 4. Design Standards and Criteria


**Safety Factors (API RP 2SK):**
```yaml
safety_factors:
  intact_condition:
    ULS:  # Ultimate Limit State
      permanent_mooring: 1.67
      temporary_mooring: 1.50
    ALS:  # Accidental Limit State
      permanent: 1.25
      temporary: 1.15

  damaged_condition:  # One line failed
    ULS:
      permanent: 1.40
      temporary: 1.25
    ALS:
      permanent: 1.15
      temporary: 1.05

  fatigue:
    design_factor: 10.0
```

**Design Load Cases:**
```yaml
load_cases:
  operating:
    return_period: "1 year"
    vessel_offset: "Normal operation"
    mooring_check: "Fatigue dominant"

  extreme:
    return_period: "100 year"
    vessel_offset: "Maximum excursion"
    mooring_check: "ULS"

  survival:
    return_period: "10,000 year"
    vessel_offset: "Survival condition"
    mooring_check: "ALS"

  damaged:
    condition: "One line failed"
    environment: "100 year"
    mooring_check: "Damaged ULS"
```
