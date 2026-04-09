---
title: "NW Shelf LNG Mooring Investigation"
tags: [mooring-failure, lng, nw-shelf, woodside, long-period-swell, resonance, karratha]
sources:
  - mooring-failures-seed
added: 2026-04-09
last_updated: 2026-04-09
---

# NW Shelf LNG Mooring Investigation

Multi-year investigation programme into mooring line failures at the Karratha Gas Plant (KGP), Withnell Bay, Mermaid Sound, operated by Woodside Energy on the North West Shelf of Australia. Three LNG loading jetties in open water, exporting LNG since 1989 with a vessel loaded every 24-36 hours.

## Timeline

- **2005 onwards**: Multiple mooring line break incidents at NWS LNG
- **2012**: Another break triggers significant investigation effort
- **2014**: Three mooring lines part in long-period swell of just ~50mm height. Woodside launches deep forensic investigation
- **2015**: Dom Allery (NW Shelf Port Operations Superintendent) presents findings at SIGTTO Panel meeting
- **2026 (Mar)**: Cyclone Narelle interrupts production at KGP and other WA LNG facilities

## Root Cause: Long-Period Swell Resonance

The core finding: even very small long-period swells (~20s period, ~50mm amplitude) can excite resonant surge, sway, and yaw motions at the natural frequency of the vessel-mooring system, amplifying forces far beyond what the wave height alone would suggest.

### Physics

- Second-order difference frequency forces on an LNG carrier increase dramatically with increasing wave period in shallow water
- Infragravity waves (periods 25-250s) cause harbour seiching and resonance amplification
- Yaw motions are dominant for maximum line forces in breast lines for 125,000m3 LNG carriers
- Bound waves and low-frequency drift forces are the key mechanism, not direct wave force

### Contributing Factors

- Mermaid Sound protected from S Indian Ocean swell by islands to the west; swell enters from the north
- Waves refract along the slopes of the navigation channel
- After Pluto LNG channel was dredged, more westerly waves observed that were not captured by the permanent wave buoy
- Long-period swell events can make LNG loading impossible for a full week, forcing production ramp-backs

## SLAM Project (UWA + Woodside)

The SLAM (Swell-Local Adjustment via Monitoring) project, led by UWA's Jeff Hansen, uses machine learning and floating wave buoy data to improve forecasting accuracy for long-period swell events.

## Key Technical Papers

- Van der Molen & Ligteringen (2003): "Behavior of a Moored LNG Ship in Swell Waves" — prototype measurements showing yaw dominates breast line forces
- Van der Molen, Garber et al.: "Channel Wave Refraction Effect on Moored LNG Carriers" — post-Pluto-channel wave propagation changes
- Grant & Holboke (2004) OTC 16718: "Shallow Water Effects on Low-Frequency Wave Excitation" — theoretical framework for long-period swell mooring loads

## Cross-References

- **Related concept**: [Mooring Line Failure Physics](../concepts/mooring-line-failure-physics.md)
- **Related concept**: [Wave Theory for Offshore Engineering](../concepts/wave-theory-offshore.md)
- **Related entity**: [Mooring Analysis System](../entities/mooring-analysis-system.md)
- **Related standard**: [DNV-OS-E301](../standards/dnv-os-e301.md)
- **Cross-wiki (marine-engineering)**: [Mooring Line Failure](../../../marine-engineering/wiki/concepts/mooring-line-failure.md)
