---
title: "Pile Capacity — Alpha Method"
description: "The alpha method is the standard approach for estimating axial pile capacity in cohesive (clay) soils per API RP 2GEO Section 7.3. It relates the unit skin..."
keywords: "geotechnical, pile-capacity, api-rp-2geo, alpha-method, clay"
author: "ACE Engineer"
url: "/knowledge/engineering/pile-capacity-alpha-method"
canonical: "https://aceengineer.com/knowledge/engineering/pile-capacity-alpha-method"
domain: "engineering"
---

# Pile Capacity — Alpha Method

*By [ACE Engineer](https://aceengineer.com) -- Expert Offshore and Marine Engineering Consulting*

The alpha method is the standard approach for estimating axial pile capacity in cohesive (clay) soils per API RP 2GEO Section 7.3. It relates the unit skin friction to the undrained shear strength through an adhesion factor alpha.

## Core Equations

### Adhesion Factor

$$\alpha = 0.5 \times \left(\frac{S_u}{\sigma'_v}\right)^{-0.5}$$

Where alpha is capped at 1.0. For normally consolidated clays where Su/sigma_v' is around 0.25, alpha approaches 1.0. For overconsolidated clays, alpha decreases.

### Unit Skin Friction

$$f = \alpha \times S_u$$

### Total Axial Capacity

$$Q = \pi D L f + N_c \times S_u \times A_p$$

Where the first term is skin friction and the second is end bearing.

- Skin friction component: `pi * D * L * f`
- End bearing component: `Nc * Su * Ap` where `Ap = pi * D^2 / 4`

## Key Inputs

| Symbol | Parameter | Units | Typical Range | Notes |
|--------|-----------|-------|---------------|-------|
| D | Pile diameter | m | 0.3 - 3.0 | Driven pipe piles |
| L | Embedded length | m | 10 - 100 | Below mudline |
| Su | Undrained shear strength | kPa | 10 - 200 | From CPT or lab tests |
| sigma_v' | Effective overburden stress | kPa | 10 - 500 | Increases with depth |
| Nc | Bearing capacity factor | - | 9.0 | API recommended value |
| alpha | Adhesion factor | - | 0.3 - 1.0 | Computed from Su/sigma_v' |
| f | Unit skin friction | kPa | 5 - 100 | alpha * Su |
| Ap | Pile tip area | m^2 | 0.07 - 7.07 | pi * D^2 / 4 |

## Methodology Notes

1. **Depth segmentation**: Divide pile into segments, compute alpha and f at each segment midpoint using local Su and sigma_v' values.
2. **Su profile**: Undrained shear strength typically increases with depth. Use site-specific CPT or triaxial data.
3. **Effective overburden**: `sigma_v' = gamma_sub * z` where `gamma_sub` is submerged unit weight (typically 6-10 kN/m^3).
4. **Alpha limits**: API RP 2GEO caps alpha at 1.0. Values above 1.0 indicate the formula is outside its validated range.
5. **Safety factors**: Design capacity = Q / FoS, where FoS is typically 1.5 - 2.0 depending on load case.

## Example Calculation

For a 1.2m diameter pile, 40m long, in clay with Su = 50 kPa and sigma_v' = 100 kPa:

- alpha = 0.5 * (50/100)^(-0.5) = 0.5 * 1.414 = 0.707
- f = 0.707 * 50 = 35.4 kPa
- Skin friction = pi * 1.2 * 40 * 35.4 = 5,339 kN
- End bearing = 9.0 * 50 * pi * 1.2^2 / 4 = 509 kN
- Total Q = 5,848 kN

## Cross-References

- **Source**: Dark Intelligence Extractions
- **Related concept**: S-N Curve Fatigue Definitions (structural capacity comparison)

---

## Work With Us

ACE Engineer provides expert engineering consulting across offshore, marine, and subsea disciplines. Our team combines deep domain expertise with modern computational tools to deliver reliable, auditable results.

[Contact us](https://aceengineer.com/contact) to discuss how we can support your project.

*Visit [aceengineer.com](https://aceengineer.com) for our full range of services.*

