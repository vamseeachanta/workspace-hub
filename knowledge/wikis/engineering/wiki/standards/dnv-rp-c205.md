---
title: "DNV-RP-C205: Environmental Conditions and Loads"
tags: [standard, dnv, environmental, wave-loading, morison, hydrodynamics]
sources: [dnv-rp-c205]
added: 2026-04-08
last_updated: 2026-04-08
---

# DNV-RP-C205: Environmental Conditions and Environmental Loads

**Full title:** DNV-RP-C205 "Environmental Conditions and Environmental Loads"

## Scope

Provides methods for determining environmental conditions (waves, current, wind) and calculating the resulting loads on offshore structures. Covers both slender members (Morison) and large-volume bodies (diffraction), with guidance on load coefficients, wave theories, and current profiles.

## Wave Loading Regimes

The appropriate loading model depends on the ratio of member diameter (D) to wavelength (lambda):

| D/lambda | Regime | Method |
|----------|--------|--------|
| < 0.2 | **Drag/inertia dominated** | Morison equation |
| 0.2 - 0.7 | **Transition** | Morison with diffraction correction, or full diffraction |
| > 0.7 | **Diffraction dominated** | Full diffraction/radiation analysis |

## Morison Equation

For slender cylindrical members (D/lambda < 0.2), the inline force per unit length is:

```
f = 0.5 * rho * Cd * D * |u - u_s| * (u - u_s) + rho * Cm * (pi/4) * D^2 * du/dt
    |_____________ drag term _______________|   |________ inertia term ________|
```

where:
- **rho** = seawater density (~1025 kg/m^3)
- **Cd** = drag coefficient
- **Cm** = inertia coefficient
- **D** = member diameter (including marine growth)
- **u** = water particle velocity
- **u_s** = structural velocity
- **du/dt** = water particle acceleration

## Hydrodynamic Coefficients

### Default Values for Smooth Cylinders

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Cd** | 1.05 | Smooth circular cylinder |
| **Cm** | 2.0 | Smooth circular cylinder |

### Effect of Surface Roughness (Marine Growth)

| Surface | Cd | Cm |
|---------|----|----|
| Smooth (k/D < 10^-4) | 1.05 | 2.0 |
| Rough (k/D ~ 10^-2) | 1.05 increasing to 1.4+ | 1.8 |

where k = surface roughness height.

## Keulegan-Carpenter Number (KC)

The KC number classifies the flow regime around a cylinder:

```
KC = u_max * T / D
```

| KC Range | Flow Regime | Dominant Force |
|----------|-------------|----------------|
| KC < 3 | Inertia-dominated | Inertia |
| 3 < KC < 15 | Intermediate | Both drag and inertia |
| KC > 20 | Drag-dominated | Drag |

- At low KC, vortex shedding is suppressed; inertia force dominates
- At high KC, flow separation and vortex shedding drive drag forces
- Intermediate KC is the most complex: both forces are significant and phase-dependent

## Current Profiles

Typical current profile models:

### Power-Law Profile (Wind-Driven)

```
u(z) = u_surface * ((z + d) / d) ^ alpha
```

where:
- **z** = depth below surface (negative downward)
- **d** = water depth
- **alpha** = profile exponent (typically 1/7)

### Tidal Current

Often assumed uniform over depth, or linearly decreasing to a fraction at the seabed.

### Current-Wave Interaction

When waves and currents coexist, the current modifies the wave kinematics. Two approaches:
1. **Vector addition** of current velocity to wave particle velocity (simpler, conservative)
2. **Doppler-shifted wave** (more accurate, accounts for wavelength stretching)

## Wave Spectra

| Spectrum | Application |
|----------|------------|
| **JONSWAP** | Fetch-limited seas (most common for design) |
| **Pierson-Moskowitz** | Fully-developed seas |
| **Torsethaugen** | Combined wind-sea and swell (double-peaked) |
| **Ochi-Hubble** | Bimodal seas with independently specified peaks |

### JONSWAP Parameters

| Parameter | Typical Value |
|-----------|---------------|
| Peak enhancement factor (gamma) | 1.0 - 7.0 (default 3.3) |
| Spectral width (sigma_a) | 0.07 for f < f_p |
| Spectral width (sigma_b) | 0.09 for f > f_p |

## Wind Loading

Wind loads on exposed structural components and topsides:

```
F_wind = 0.5 * rho_air * Cs * A * u_wind^2
```

where:
- **rho_air** = air density (~1.225 kg/m^3)
- **Cs** = shape coefficient (drag)
- **A** = projected area
- **u_wind** = wind velocity at elevation (apply gust factor for dynamic response)

Wind profiles follow a logarithmic or power-law variation with height.

## Key Considerations

- **Marine growth:** increases effective diameter (D) and surface roughness (k), affecting both Cd and Cm and the direct wave loading area
- **Shielding effects:** members in the wake of upstream members experience reduced loading; array effects should be considered for multi-column structures
- **Wave stretching:** for crest kinematics above mean water level, use Wheeler stretching or extrapolation methods
- **Return periods:** 100-year conditions for ULS design, 10,000-year for ALS (accidental limit state)

## Related Pages

- [CFD Offshore Hydrodynamics](../concepts/cfd-offshore-hydrodynamics.md) -- computational methods for complex flow problems beyond Morison
- [DNV-RP-C203: Fatigue Design](dnv-rp-c203.md) -- fatigue damage driven by wave loading from this RP
- [Pipeline Integrity Assessment](../concepts/pipeline-integrity-assessment.md) -- subsea pipeline loading from waves and currents
- **Cross-wiki (marine-engineering)**: [Long-Period Swell & Resonance](../../../marine-engineering/wiki/concepts/long-period-swell-resonance.md) — wave spectra and second-order drift forces relevant to long-period swell-induced mooring loads
- **Cross-wiki (naval-architecture)**: [Seakeeping and Ship Motions](../../../naval-architecture/wiki/concepts/seakeeping.md) — wave spectra (JONSWAP, Pierson-Moskowitz) and RAO computation for vessel motions
