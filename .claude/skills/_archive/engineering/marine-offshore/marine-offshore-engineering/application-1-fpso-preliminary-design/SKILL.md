---
name: marine-offshore-engineering-app-1-fpso-prelim-design
description: 'Sub-skill of marine-offshore-engineering: Application 1: FPSO Preliminary
  Design (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Application 1: FPSO Preliminary Design (+1)

## Application 1: FPSO Preliminary Design


```yaml
fpso_design:
  vessel:
    hull:
      type: "conversion"  # or "newbuild"
      length_pp: 320  # m
      beam: 58  # m
      depth: 32  # m
      draft_design: 22  # m

    capacity:
      oil_storage: 2000000  # barrels
      production: 100000  # bopd
      water_injection: 200000  # bwpd

  topsides:
    modules:
      - production_manifold
      - separation
      - gas_compression
      - water_injection
      - utilities
    weight: 25000  # tonnes

  mooring:
    type: "spread"
    lines: 12
    configuration: "3x4"  # 3 bundles, 4 lines each

  design_codes:
    - ABS MODU
    - API RP 2FPS
    - DNV-OS-C103
```


## Application 2: Environmental Load Calculation


```python
def calculate_total_environmental_load(
    vessel_data: dict,
    environment: dict
) -> dict:
    """
    Calculate combined wind, wave, and current loads.

    Args:
        vessel_data: Vessel dimensions and coefficients
        environment: Environmental parameters

    Returns:
        Total forces and moments
    """
    import numpy as np

    # Wind force
    rho_air = 1.225  # kg/m³
    V_wind = environment['wind_speed']
    A_projected = vessel_data['frontal_area']
    Cd_wind = vessel_data['wind_drag_coef']
    F_wind = 0.5 * rho_air * V_wind**2 * Cd_wind * A_projected / 1000  # kN

    # Wave drift force (simplified)
    rho_water = 1025  # kg/m³
    Hs = environment['wave_Hs']
    F_wave_drift = 0.5 * rho_water * 9.81 * Hs**2 * vessel_data['waterplane_area'] / 1000

    # Current force
    V_current = environment['current_speed']
    A_underwater = vessel_data['underwater_area']
    Cd_current = vessel_data['current_drag_coef']
    F_current = 0.5 * rho_water * V_current**2 * Cd_current * A_underwater / 1000

    # Total horizontal force
    theta_wind = np.radians(environment['wind_direction'])
    theta_wave = np.radians(environment['wave_direction'])
    theta_current = np.radians(environment['current_direction'])

    Fx = (F_wind * np.cos(theta_wind) +
          F_wave_drift * np.cos(theta_wave) +
          F_current * np.cos(theta_current))

    Fy = (F_wind * np.sin(theta_wind) +
          F_wave_drift * np.sin(theta_wave) +
          F_current * np.sin(theta_current))

    return {
        'Fx_kN': Fx,
        'Fy_kN': Fy,
        'F_total_kN': np.sqrt(Fx**2 + Fy**2),
        'direction_deg': np.degrees(np.arctan2(Fy, Fx))
    }
```
