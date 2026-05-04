---
name: orcaflex-environment-config-complete-environment-configuration
description: 'Sub-skill of orcaflex-environment-config: Complete Environment Configuration
  (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Complete Environment Configuration (+1)

## Complete Environment Configuration


```yaml
# configs/environment_config.yml

environment:
  # General settings
  water_depth: 1500.0     # m
  water_density: 1025.0   # kg/m³
  air_density: 1.225      # kg/m³

  # Wave configuration
  waves:
    type: "JONSWAP"
    significant_height: 5.5    # m (Hs)
    peak_period: 12.0          # s (Tp)
    direction: 180.0           # deg (waves from)
    gamma: 3.3                 # JONSWAP peak enhancement
    spreading: "Cos2s"         # Directional spreading
    spreading_exponent: 2      # s parameter

    # Or multiple wave components
    components:
      - type: "JONSWAP"
        Hs: 4.0
        Tp: 10.0
        direction: 180.0
        gamma: 2.5
      - type: "Swell"
        Hs: 2.0
        Tp: 16.0
        direction: 210.0
        gamma: 6.0

  # Current configuration
  current:
    surface_speed: 1.2      # m/s
    direction: 165.0        # deg (flowing towards)
    profile_type: "Interpolated"

    # Depth profile
    depth_profile:
      - depth: 0.0
        factor: 1.0
      - depth: 50.0
        factor: 0.9
      - depth: 200.0
        factor: 0.5
      - depth: 500.0
        factor: 0.2
      - depth: 1500.0
        factor: 0.05

  # Wind configuration
  wind:
    speed: 25.0           # m/s (1-hour mean)
    direction: 180.0      # deg (from)
    reference_height: 10.0  # m above sea level
    profile: "Power Law"
    exponent: 0.12        # Wind shear exponent

    # Load inclusion
    apply_to:
      vessels: true
      lines: false
      buoys: true

  # Seabed configuration
  seabed:
    type: "Flat"          # or "3D Profile"
    stiffness: 100.0      # kN/m/m²
    friction: 0.5         # Coefficient
    damping: 1.0          # % critical
    slope: 0.0            # deg
```


## Sea State Matrix Configuration


```yaml
# configs/sea_states.yml

sea_states:
  # Design conditions
  100_year:
    Hs: 8.5
    Tp: 14.0
    gamma: 3.3
    current_speed: 1.5
    wind_speed: 35.0

  10_year:
    Hs: 6.5
    Tp: 12.5
    gamma: 3.0
    current_speed: 1.2
    wind_speed: 28.0

  1_year:
    Hs: 5.0
    Tp: 11.0
    gamma: 2.5
    current_speed: 1.0
    wind_speed: 22.0

  operational:
    Hs: 2.5
    Tp: 8.0
    gamma: 2.0
    current_speed: 0.5
    wind_speed: 12.0

# Heading combinations
headings:
  wave: [0, 15, 30, 45, 60, 75, 90]
  current_offset: 0    # degrees from wave
  wind_offset: 0       # degrees from wave
```
