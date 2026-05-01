---
title: "Environmental Yaw Moment Coefficients"
tags: [yaw, current-load, wind-load, ocimf, orcaflex]
sources:
  - orcaflex-manoeuvring-current-wind-loads
  - ocimf-yaw-moment-coefficient-figures
added: 2026-04-30
last_updated: 2026-04-30
---

# Environmental Yaw Moment Coefficients

This page captures environmental yaw-moment context that must not be confused with the direct rudder-induced yaw moment in [[yaw-moment-rudder-sweep]].

## OCIMF-style current/wind yaw moment

The OrcaFlex vessel theory pages summarize the OCIMF drag form:

```text
m_z = 0.5 * C_yaw * rho * |v|^2 * A_yaw
```

where:

- `C_yaw`: direction-dependent current or wind yaw coefficient
- `rho`: water or air density
- `|v|`: low-frequency relative fluid speed past the vessel at the load origin
- `A_yaw`: yaw area moment

OCIMF standard area-moment conventions:

- current yaw: `A_yaw = L^2 D`
- wind yaw: `A_yaw = L * A_sway`

Raw locators:

- `/mnt/ace/digitalmodel/llm-wiki/orcaflex/topics/Vesseltheory,Currentandwindloads.md`
- `/mnt/ace/digitalmodel/llm-wiki/orcaflex/topics/Vesseltheory,Manoeuvringload.md`

## Munk moment double-counting caution

OrcaFlex notes that if current load is included, OCIMF current yaw load is assumed already to include classic Munk-moment terms. If both current load and manoeuvring load are enabled, OrcaFlex omits those Munk terms from the manoeuvring yaw moment to avoid double counting.

Preserve this caution when combining environmental yaw moment with maneuvering/rudder yaw moments.

## Yaw-rate drag is separate

OCIMF translational current/wind coefficients do not include vessel yaw angular-velocity drag. OrcaFlex treats current yaw-rate drag separately:

```text
f_x = 0.5 * rho * |omega| * omega * K_surge
f_y = 0.5 * rho * |omega| * omega * K_sway
m_z = 0.5 * rho * |omega| * omega * K_yaw
```

If manoeuvring load is also enabled, yaw-rate drag factors should be viscous-only to avoid potential-flow double counting.

## OCIMF yaw coefficient figure families

Relevant local figures under `/mnt/ace/acma-codes/OCIMF/Figures/`:

- `A11, Current Yaw Moment Coefficient (Cxyc) - Loaded Tanker.pdf`
  - current yaw moment coefficient for loaded tanker
  - independent variable: current angle of attack
  - curve family: water-depth/draft ratio
- `A14, Current Yaw Moment Coefficient {Cxyc) - Ballasted Tanker.pdf`
  - current yaw moment coefficient for ballasted tanker
  - note: “40% T, Based on Midships”
  - curve family: conventional/cylindrical hull form and depth/draft ratio
- `A19, Wind Yaw Moment Coefficient (Cxvw) - Gas Carrier.pdf`
  - wind yaw moment coefficient for gas carrier
  - curve family: prismatic versus spherical tanks

No numeric digitization was performed in the 2026-04-30 sweep. These figures should be digitized into curve tables only when a future issue explicitly needs environmental yaw coefficients.

## Related pages

- [[yaw-moment-rudder-sweep]]
- [[rudder-force-modeling]]
