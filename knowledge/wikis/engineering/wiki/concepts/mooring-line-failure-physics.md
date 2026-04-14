---
title: "Mooring Line Failure Physics"
tags: [mooring-failure, hmpe, resonance, snap-back, long-period-swell, axial-compression-fatigue]
sources:
  - mooring-failures-seed
added: 2026-04-09
last_updated: 2026-04-09
---

# Mooring Line Failure Physics

Comprehensive analysis of mooring line failure mechanisms compiled from 40+ entries in the mooring failures knowledge seed, covering LNG terminals, FPSOs, FSRUs, and general cargo berths worldwide.

## Failure Mechanisms

### 1. Long-Period Swell Resonance
Small-amplitude long-period swells (T > 15s, H as low as 50mm) excite resonant vessel motions through second-order difference frequency forces. In shallow water, these forces increase dramatically with wave period. Infragravity waves (25-250s) cause harbour seiching. This mechanism is responsible for the NWS LNG mooring investigation findings.

### 2. HMPE Rope Degradation
During 2007-2011, approximately 3% of HMPE ropes in LNG service failed. Root causes identified by TTI/DSM Dyneema Users Group:
- **Axial compression fatigue (ACF)**: Jacketed HMPE construction increases likelihood
- **Low HMPE content**: Cost reduction led to weaker ropes
- **Increased lay lengths**: Created internal distortion
- Aft breast lines failed 2x as often as other positions
- Failure tensions at 10-60% of MBL indicate premature degradation, not overload

### 3. Snap-Back
HMPE ropes DO recoil on failure -- manufacturer claims of "no snap-back" are misleading. The Zarga incident showed a 44mm UHMPE line with Euroflex tail snapped back over 15m in less than 1 second. MEG4 now treats the entire mooring deck as a danger zone.

### 4. Equipment-Material Incompatibility
At Prelude FLNG, nylon rope on nylon fairlead liner generated excessive heat and abrasion, destroying all 16 lines in a single event. Pedestal rollers are also failure initiation points for HMPE ropes under tension (TSB M23F0012).

### 5. Passing Vessel Effects
At Elba Island (2006), a 14-knot passing vessel's wake knocked the Golar Freeze loose, causing mooring line and fuel hose breakage. Remediation cost $35M (dedicated slip carved out of river bank). Port expansion/breakwater construction can also create wave reflection that worsens mooring loads (Veracruz 2024-2025).

## Industry Statistics (IG P&I 2016-2021)

- 858 injuries, 31 fatalities during mooring operations (~170 injuries/year)
- 53% of injuries from parted ropes/wires
- 42% from lines jumping off drum ends/bitts
- 32% from improper spooling
- 28% from mixed-material lines

## Norwegian Shelf Findings (DNV 2022)

18 mooring component failures on semi-submersible MODUs. Primary mechanism: hydrogen embrittlement of high-strength chain. Actual failure rate: ~3 per 2 years vs design target of 1 per 10,000 operating years -- orders of magnitude worse than assumed.

## Mitigation Strategies

- **Real-time tension monitoring**: Reduced failures 35% at Port Hedland (BHP)
- **Non-jacketed HMPE**: Samson AmSteel-Blue (Dyneema SK78) eliminated failures fleet-wide for BW Fleet Management
- **Wave forecasting**: SLAM project (UWA+Woodside) uses ML for long-period swell prediction
- **SOLAS II-1/3-8 (Jan 2024)**: Mandatory design-based mooring arrangements, retirement at 75% of Ship Design MBL

## Cross-References

- **Related entity**: [NW Shelf LNG Mooring Investigation](../entities/nws-lng-mooring-investigation.md)
- **Related entity**: [Mooring Analysis System](../entities/mooring-analysis-system.md)
- **Related concept**: [Wave Theory for Offshore Engineering](../concepts/wave-theory-offshore.md)
- **Related standard**: [OCIMF MEG4](../standards/ocimf-meg4.md)
- **Related standard**: [DNV-OS-E301](../standards/dnv-os-e301.md)
- **Cross-wiki (marine-engineering)**: [Mooring Line Failure](../../../marine-engineering/wiki/concepts/mooring-line-failure.md) -- similar slugs (83%); similar titles (83%); shared tags: hmpe, snap-back; shared keywords: concept, cross-references, failure, hmpe, line
