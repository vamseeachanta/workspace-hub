---
title: "Long-Period Swell & Resonance Amplification"
tags: [mooring, resonance, swell, infragravity, waves, lng]
sources:
  - mooring-failures-lng-terminals
added: 2026-04-07
last_updated: 2026-04-07
---

# Long-Period Swell & Resonance Amplification

The phenomenon where very small long-period swells (periods 20-250 seconds, heights as low as 50mm) excite resonant surge, sway, and yaw motions in moored vessels, amplifying mooring line forces far beyond what wave height alone would suggest.

## Core Physics

**The danger is not the wave height — it is the wave period.** Long-period swells at very low amplitude can generate catastrophic mooring loads through resonance amplification.

| Mechanism | Description |
|-----------|-------------|
| Second-order difference frequency forces | Increase dramatically with wave period in shallow water, creating large low-frequency drift forces |
| Resonant vessel motions | Surge, sway, and yaw at natural frequency of vessel-mooring system |
| Infragravity waves | Periods 25-250s; cause harbour seiching and resonance amplification |
| Bound waves | Low-frequency drift forces are the key physics, not direct wave force |

## Key Finding: NWS LNG 2014 Incident

Three mooring lines parted at Withnell Bay during a swell event with just **~50mm wave height** — seemingly benign conditions. The real mechanism was resonance: the long-period swell matched the natural frequency of the vessel-mooring system.

## Yaw Motion Dominance

Per Van der Molen & Ligteringen (2003):
- **Yaw motions are dominant for maximum breast line forces** for 125,000m³ LNG carriers at swell-exposed jetties
- Calculated maximum mooring forces **underestimate prototype measurements by 10-20%**

## Wave Refraction Effects

Dredging new channels can alter wave propagation and create unexpected mooring loads at existing berths. After the Pluto LNG channel was dredged at NWS LNG, more westerly waves were observed that were not captured by the permanent wave buoy.

## Operational Impact

Long-period swell events can make LNG loading impossible for a full week, forcing production ramp-backs.

## Cross-References

- **Source**: [Mooring Failures at LNG Terminals](../sources/mooring-failures-lng-terminals.md)
- **Related entity**: [[lng-carrier-mooring]]
- **Related concept**: [[mooring-line-failure]]
- **Related concept**: [[cathodic-protection-system]] (both are offshore marine engineering topics)
- **Cross-wiki (engineering)**: [CFD Offshore Hydrodynamics](../../../engineering/wiki/concepts/cfd-offshore-hydrodynamics.md) — CFD and diffraction methods for modelling wave-induced vessel response
- **Cross-wiki (engineering)**: [DNV-RP-C205](../../../engineering/wiki/standards/dnv-rp-c205.md) — wave spectra (JONSWAP) and second-order drift force methods
- **Cross-wiki (engineering)**: [Wave Theory for Offshore Engineering](../../../engineering/wiki/concepts/wave-theory-offshore.md) — wave spectra theory and long-period swell physics driving resonant mooring response
- **Cross-wiki (engineering)**: [Seakeeping and 6-DOF Ship Dynamics](../../../engineering/wiki/concepts/seakeeping-6dof.md) — 6-DOF vessel motion amplification from long-period swell excitation
