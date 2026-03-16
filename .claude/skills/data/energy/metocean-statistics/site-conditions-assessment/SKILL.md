---
name: metocean-statistics-site-conditions-assessment
description: 'Sub-skill of metocean-statistics: Site Conditions Assessment (+1).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Site Conditions Assessment (+1)

## Site Conditions Assessment


The NREL floating wind methodology provides a standardized approach for
characterizing offshore site conditions for floating wind turbine design.

**Return Period Table Format:**
| Return Period | Hs (m) | Tp (s) | U10 (m/s) | Current (m/s) |
|--------------|--------|--------|-----------|---------------|
| 1-year | 5.2 | 10.5 | 18.3 | 0.45 |
| 10-year | 7.8 | 12.1 | 23.4 | 0.62 |
| 50-year | 9.4 | 13.2 | 27.1 | 0.78 |
| 100-year | 10.2 | 13.8 | 28.9 | 0.85 |

*See sub-skills for full details.*

## Environmental Contour Methods


**IFORM Method:**
- Transform to standard normal space
- Apply reliability index for target probability
- Inverse transform to physical space
- Conservative for design applications

**Direct Sampling:**
- Monte Carlo simulation in physical space
- Empirical exceedance probability
- Better captures complex dependencies
- Computationally intensive
