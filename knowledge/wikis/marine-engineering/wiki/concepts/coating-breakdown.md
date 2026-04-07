---
title: "Coating Breakdown Factor"
tags: [corrosion, coating, design, cathodic-protection]
sources:
  - dnv-rp-b401
added: 2026-04-07
last_updated: 2026-04-07
---

# Coating Breakdown Factor

The fraction of the structure's surface area where coating has deteriorated, exposing bare metal
to the corrosive environment. A critical design parameter in cathodic protection system sizing.

## Design Practice

CP systems are designed to protect the **uncoated** area. As coating degrades over time, the CP
system must provide increasing current to protect the newly exposed bare metal.

## Typical Breakdown Factors (DNV-RP-B401)

| Time (years) | Splash zone | Submerged zone | Buried zone |
|--------------|-------------|----------------|-------------|
| 0 | 0.02–0.05 | 0.02–0.05 | 0.02–0.05 |
| 5 | 0.05–0.10 | 0.03–0.08 | 0.02–0.05 |
| 10 | 0.10–0.20 | 0.05–0.15 | 0.03–0.08 |
| 20 | 0.30–0.50 | 0.15–0.30 | 0.05–0.15 |
| 30 | 0.50–0.70 | 0.25–0.40 | 0.10–0.20 |

## Coating Types

- **Epoxy coatings**: Most common offshore coating; good adhesion to steel
- **FBE (Fusion Bonded Epoxy)**: Pipeline coating; excellent mechanical properties
- **3LPE/3LPP**: Three-layer polyethylene or polypropylene; submarine pipelines
- **Thermal spray aluminum**: Splash zone; excellent durability

## Design Impact

The design total current demand = sum of (zone current density x zone area x coating breakdown factor)
This drives total anode mass sizing.

## Cross-References

- **Standard**: [DNV-RP-B401: Cathodic Protection Design](../sources/dnv-rp-b401-cathodic-protection.md)
- **Related concept**: [[cathodic-protection-system]]
  **Related concept**: [[corrosion-control]]
