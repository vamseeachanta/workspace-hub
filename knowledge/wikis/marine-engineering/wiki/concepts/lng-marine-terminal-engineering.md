---
title: "LNG Marine Terminal Engineering"
tags: [lng, terminal, jetty, berth, mooring, port-operations, fsru]
sources:
  - lng2026-tp04-shipping-marine-port-operations
  - sigtto-lng-operations-port-areas
  - mooring-failures-lng-terminals
added: 2026-04-23
last_updated: 2026-04-23
---

# LNG Marine Terminal Engineering

Engineering scope for LNG marine terminals spans the berth, jetty, ship/shore transfer interface, marine operability envelope, and hazard-critical operating procedures needed to load, unload, bunker, or regasify LNG safely.

This page is intentionally scoped as an engineering synthesis page rather than a single-source summary. It combines:
- LNG2026 programme evidence that marine terminal topics remain active in industry discussion
- SIGTTO-style terminal operations framing
- incident-driven lessons from LNG terminal mooring failures

## Why This Topic Matters

LNG projects often focus attention on liquefaction, regasification, containment, and commercial strategy. But marine terminals are where those systems meet:
- live ship motions
- weather windows
- berth geometry
- mooring loads
- loading-arm or hose envelopes
- navigation and tug operations
- emergency release and shutdown scenarios

For many terminals, the marine interface is the limiting system for uptime and safety, especially where swell, seiche, passing-vessel effects, shallow-water wave transformation, or constrained harbour geometry drive operability losses.

## Core Engineering Subsystems

### 1. Berth and jetty layout
Engineering questions include:
- berth orientation relative to dominant wave, swell, current, and wind directions
- approach channel and under-keel clearance constraints
- spacing and arrangement of breasting and mooring dolphins
- jetty-head geometry and structural load paths
- breakwater / basin / harbour interaction with long-period waves and seiche behavior

### 2. Mooring and fendering system
This is often the most visible marine-terminal integrity problem.

Key work includes:
- mooring arrangement and line-management philosophy
- breast / spring / headline / sternline distribution
- fender reaction and energy absorption requirements
- dynamic vessel motion and line-load amplification under environmental forcing
- snap-back, HMPE degradation, resonance, and passing-vessel wake sensitivity

See also:
- [[lng-carrier-mooring]]
- [[mooring-line-failure]]
- [[long-period-swell-resonance]]

### 3. Ship/shore transfer interface
Transfer equipment creates additional geometry and motion constraints beyond berth survival.

Key engineering checks include:
- loading-arm reach envelope or hose geometry
- allowable relative motion between vessel manifold and terminal connection point
- emergency release coupling and shutdown logic
- segregation between normal transfer, cooldown, purging, and emergency disconnect states
- compatibility for LNG carrier, bunkering vessel, FSRU, or ship-to-ship transfer scenarios

### 4. Marine operability and downtime analysis
A terminal is not just designed for survival; it must achieve usable uptime.

Engineering work includes:
- environmental criteria definition
- berth operability by Hs, Tp, direction, current, and wind
- wave agitation, harbour resonance, and vessel response analysis
- downtime prediction and production/throughput impact
- weather forecast integration and operational decision rules

### 5. Navigation and marine operations
Terminal performance depends on safe arrival and departure, not only alongside condition.

Typical work includes:
- manoeuvring and tug philosophy
- escort requirements and restricted-weather criteria
- channel transit limits
- berth approach and departure envelope
- simultaneous operations constraints

### 6. Safety, isolation, and emergency systems
LNG terminal engineering is heavily shaped by consequence management.

Marine-terminal-specific requirements include:
- ESD hierarchy and trip philosophy at the ship/shore interface
- release prevention and emergency release systems
- exclusion zones and marine traffic controls
- fire, gas, and spill response integration with berth layout
- tug, pilot, and terminal operator coordination under abnormal conditions

## Research and Engineering Required for Marine Terminals

The LNG2026 programme page is sufficient to justify this topic as current and relevant, but not sufficient for design work. A usable marine-terminal research stack should cover the following.

### A. Metocean and harbour response
Need:
- wave climate including long-period swell and infragravity content
- wind, current, tide, water-level, and shallow-water transformation effects
- harbour agitation / resonance / seiche behavior
- vessel-response implications at berth and during approach

### B. Berth operability and mooring dynamics
Need:
- vessel motions at berth
- line loads and fender reactions
- low-frequency drift and resonance effects
- passing-vessel and tug/wake effects where relevant
- criteria for downtime, alarm, cargo stop, and unberthing

### C. Structural terminal interface
Need:
- dolphin, jetty, and mooring hardware loads
- local and global structural design basis
- cyclic loading and fatigue exposure
- inspection and maintenance philosophy

### D. Transfer-system envelope
Need:
- loading-arm or hose motion envelope checks
- manifold alignment constraints
- emergency release assumptions
- transfer shutdown criteria linked to vessel motion and berth response

### E. Marine operations and logistics
Need:
- approach / departure / tug strategy
- operational windows for berthing, cargo transfer, bunkering, or STS
- sequencing for import terminal, export terminal, FSRU, or floating transfer case
- human-in-the-loop procedures and communications

### F. Safety and regulatory basis
Need:
- applicable terminal and marine safety guidance
- hazardous area and exclusion-zone logic
- abnormal-event and emergency response basis
- operator / port / terminal interface requirements

## Practical Terminal Archetypes to Distinguish

Marine terminal engineering should not be treated as one generic problem. The wiki should distinguish at least:
- conventional LNG export jetty
- LNG import / regas terminal berth
- FSRU-based receiving terminal
- ship-to-ship transfer arrangement
- LNG bunkering berth or offshore transfer location

Each has different governing constraints, especially around transfer equipment, marine operations, and operability margins.

## What We Can Infer Now vs. What Needs Deeper Sources

### What the current sources support
- marine terminal and port operations are active LNG technical priorities
- port/terminal infrastructure, bunkering, and STS should exist as first-class wiki topics
- mooring and berth operability deserve explicit linkage to terminal uptime and safety
- incident-driven LNG terminal mooring lessons already justify marine-terminal engineering as a distinct knowledge cluster

### What still needs deeper source ingestion
- berth design standards and codes
- loading-arm design/operability criteria
- terminal-specific metocean and harbour-response references
- FSRU-specific marine terminal design guidance
- detailed case studies on berth downtime, terminal operability, and marine transfer incidents

## Candidate Follow-On Wiki Pages

This concept page suggests follow-on pages for:
- [[lng-berth-operability]]
- [[lng-transfer-system-envelope]]
- [[fsru-marine-terminal-interface]]
- mooring dolphin and breasting dolphin design basis
- harbour agitation and seiche effects on LNG terminals

## Cross-References

- [[lng-carrier-mooring]]
- [[mooring-line-failure]]
- [[long-period-swell-resonance]]
- [LNG2026 TP04: Shipping, Marine and Port Operations](../sources/lng2026-tp04-shipping-marine-port-operations.md)
- [SIGTTO LNG Operations in Port Areas](../sources/sigtto-lng-operations-port-areas.md)
- [Mooring Failures at LNG Terminals](../sources/mooring-failures-lng-terminals.md)
- **Cross-wiki (engineering)**: [DNV-OS-E301](../../../engineering/wiki/standards/dnv-os-e301.md) — stationkeeping and mooring-system design basis
- **Cross-wiki (engineering)**: [OrcaFlex Solver](../../../engineering/wiki/entities/orcaflex-solver.md) — likely tool for berth-motion and mooring-load studies
- **Cross-wiki (lng-projects)**: [LNG Marine Transfer Systems](../../../lng-projects/wiki/concepts/lng-marine-transfer-systems.md) -- similar slugs (55%); similar titles (55%); shared tags: jetty; shared entities: FSRU, LNG, SIGTTO, STS
