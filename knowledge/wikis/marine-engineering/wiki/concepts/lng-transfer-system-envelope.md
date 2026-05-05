---
title: "LNG Transfer System Envelope"
tags: [lng, transfer, loading-arm, hose, terminal, operability]
sources:
  - lng2026-tp04-shipping-marine-port-operations
  - sigtto-lng-operations-port-areas
  - mooring-failures-lng-terminals
added: 2026-04-23
last_updated: 2026-04-23
---

# LNG Transfer System Envelope

The LNG transfer system envelope is the range of relative vessel position and motion within which ship/shore transfer equipment can remain connected and operate safely. In marine-terminal practice, this usually becomes one of the governing limits on berth operability because the transfer system is less tolerant of motion than the berth structure itself.

## Scope

This page covers the marine engineering meaning of transfer envelope rather than detailed mechanical design of loading arms or cryogenic hoses. The supported current sources justify the topic because LNG terminal engineering, port operations, mooring integrity, and ship/shore transfer are already linked in the existing wiki cluster.

## Why the Transfer Envelope Governs Terminals

An LNG berth can appear structurally robust and still be operationally weak if the vessel manifold moves too far relative to the shore connection. In practice, the transfer system envelope couples together:
- vessel motions at berth
- berth geometry and manifold location
- loading-arm reach or hose geometry
- fender offset and mooring stiffness
- emergency shutdown and release philosophy

This is why the main terminal concept page treats the ship/shore transfer interface as a separate subsystem rather than a detail of cargo handling.

## Main Engineering Variables

### Relative position
The transfer interface depends on the geometry between the vessel manifold and the terminal connection point, including:
- stand-off distance from the fender line
- longitudinal position of the vessel alongside
- vertical variation due to tide, draft change, and water-level effects
- manifold height and reach compatibility between ship and berth

### Relative motion
Even when the static geometry is acceptable, the system can become unacceptable under dynamic motion such as:
- surge and sway
- yaw-driven manifold displacement
- low-frequency drift motions
- motion amplification from long-period swell or harbour response

### Operating state
The acceptable envelope may differ between:
- connection and cooldown
- steady transfer
- shutdown or purging
- emergency disconnect

## Relationship to Mooring and Fendering

The transfer system envelope should not be checked in isolation. It is directly affected by:
- mooring line pretension and restoring behavior
- line material behavior and degradation risk
- fender stiffness and allowable compression
- dolphin layout and berth orientation
- local wave climate and basin response

This means the transfer envelope is one of the main ways that a mooring problem becomes a cargo-transfer problem.

## Failure-Relevant Lessons from Current Sources

The current sources do not provide vendor-specific arm limits, but they do support several practical lessons:
- mooring incidents at LNG terminals show that low-frequency vessel motion can become safety-critical
- LNG terminal engineering should treat mooring, transfer, and operations as one system
- port-area LNG guidance implies that cargo transfer depends on controlled marine conditions, not only process readiness
- conference-level topic signals from LNG2026 justify transfer-interface engineering as a live capability area for LNG infrastructure

## What an Engineering Team Usually Needs to Define

A usable terminal basis typically needs:
- vessel classes to be served at the berth
- manifold and berth connection geometry
- motion and offset limits for the intended transfer equipment
- triggers for alarm, transfer suspension, ESD, and emergency release
- weather and harbour conditions associated with those triggers
- operational hold points for berthing, connecting, transferring, and disconnecting

## What Current Sources Do Not Yet Support

The existing source set does not justify quoting:
- numerical motion limits for particular loading arms
- hose minimum bend-radius requirements for a specific manufacturer
- universal disconnection criteria
- detailed formulae for transfer-arm load assessment

Those details require equipment-specific documentation and dedicated terminal design references.

## Relationship to LNG Terminal Types

Transfer-envelope checks apply differently across terminal types:
- conventional export or import jetties focus on loading-arm geometry between carrier and jetty head
- bunkering and ship-to-ship transfers must manage motion between two floating bodies
- FSRU facilities add interface constraints between the floating regas unit, visiting carrier, and shore utility systems

## Cross-References

- [[lng-marine-terminal-engineering]]
- [[lng-berth-operability]]
- [[lng-carrier-mooring]]
- [[fsru-marine-terminal-interface]]
- [[mooring-line-failure]]
- [[long-period-swell-resonance]]
- [LNG2026 TP04: Shipping, Marine and Port Operations](../sources/lng2026-tp04-shipping-marine-port-operations.md)
- [SIGTTO LNG Operations in Port Areas](../sources/sigtto-lng-operations-port-areas.md)
- [Mooring Failures at LNG Terminals](../sources/mooring-failures-lng-terminals.md)
- **Cross-wiki (lng-projects)**: [LNG Marine Transfer Systems](../../../lng-projects/wiki/concepts/lng-marine-transfer-systems.md) -- similar slugs (69%); similar titles (69%); shared tags: transfer; shared keywords: and, cross-references, lng, mooring, not; shared entities: FSRU, LNG, SIGTTO
