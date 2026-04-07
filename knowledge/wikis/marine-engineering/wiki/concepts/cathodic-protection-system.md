---
title: "Cathodic Protection System"
tags: [corrosion, protection, electrochemistry, offshore]
sources:
  - dnv-rp-b401
added: 2026-04-07
last_updated: 2026-04-07
---

# Cathodic Protection System

An electrochemical technique used to protect metallic structures from corrosion by making the structure
the cathode of an electrochemical cell.

## Types

### Galvanic (Sacrificial Anode) CP

Uses anodes made of more active metals (Al-Zn-In alloys) connected directly to the protected structure.
The anode corrodes sacrificially, protecting the steel.

**Advantages**: Simple, no external power, self-regulating
**Limitations**: Limited current output, limited design life per anode mass

### Impressed Current CP (ICCP)

Uses rectifiers to apply external DC current via inert anodes (mixed metal oxide, platinum).

**Advantages**: High current output, adjustable, long design life
**Limitations**: Complex, requires power, risk of over/under protection

## Design Methodology (DNV-RP-B401)

1. **Determine current density requirements** for each environmental zone
2. **Account for coating breakdown** over design life
3. **Calculate total current demand** = sum of zone demands
4. **Size total anode mass** = (current demand x design life x 8760) / (electrochemical capacity x utilization)
5. **Number of anodes** = total mass / mass per anode
6. **Current distribution check** — ensure adequate potential at all protected areas

## Environmental Zones

| Zone | Current Density (new coating) | 30yr breakdown |
|------|-------------------------------|----------------|
| Splash zone | 200–300 mA/m² | ~60% breakdown |
| Submerged zone | 100–150 mA/m² | ~30% breakdown |
| Buried/soil zone | 20–50 mA/m² | ~10% breakdown |
| Mudline | 30–50 mA/m² | ~20% breakdown |

## Cross-References

- **Standard**: [DNV-RP-B401: Cathodic Protection Design](../sources/dnv-rp-b401-cathodic-protection.md)
- **Related entity**: [[anode]]
- **Related concept**: [[corrosion-control]]
- **Related concept**: [[coating-breakdown]]
