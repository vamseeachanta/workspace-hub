---
title: "Sour Service"
tags: [h2s, corrosion, materials, nace]
sources:
  - dnvgl-os-e201
added: 2026-04-07
last_updated: 2026-04-07
---

# Sour Service

Operating conditions where hydrogen sulfide (H2S) is present in sufficient concentration to cause
hydrogen embrittlement and sulfide stress cracking (SSC) in susceptible metals.

## Definition (per NACE MR0175/ISO 15156)

A system/condition is "sour" when:
- H2S partial pressure exceeds 0.05 psi (0.0034 bar) absolute
- AND the pH is low enough for SSC to be a concern

## Failure Mechanisms

| Mechanism | Description |
|-----------|-------------|
| SSC (Sulfide Stress Cracking) | Hydrogen-induced cracking under tensile stress |
| HIC (Hydrogen Induced Cracking) | Blistering and cracking from atomic H diffusion |
| SOHIC (Stress-Oriented HIC) | HIC aligned with applied stress |
| SCC (Stress Corrosion Cracking) | Cracking in specific environments |

## Material Selection

- **Carbon steel**: Susceptible above SSC threshold; requires hardness control (max HRC 22)
- **Stainless steels**: Duplex (22Cr, 25Cr) and super stainless for severe service
- **Nickel alloys**: For extreme H2S and CO2 conditions
- **Cladding**: Carbon steel with stainless cladding for corrosion resistance

## Cross-References

- **Standard**: [DNVGL-OS-E201: Oil and Gas Processing Systems](../sources/dnvgl-os-e201-oil-gas-processing.md)
- **Related concept**: [[process-safety]]
- **Related entity**: [[separator]]
- **Cross-wiki (engineering)**: [Pipeline Integrity Assessment](../../../engineering/wiki/concepts/pipeline-integrity-assessment.md) — H2S-induced cracking (SSC, HIC) as a pipeline integrity threat assessed via API 579
