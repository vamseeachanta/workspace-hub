---
title: "Riser Global-Analysis Load-Case Taxonomy"
tags: [riser, load-case, uls, als, fls, sls, global-analysis]
added: 2026-05-02
last_updated: 2026-05-02
---

# Riser Global-Analysis Load-Case Taxonomy

## Scope

This page is the load-case taxonomy crosscutting all riser types (SCR, TTR, flexible, hybrid, drilling). It enumerates limit states, drivers, and required outputs. It is NOT a fatigue-mechanics page — see [[viv-riser-fatigue]] for VIV cycle-counting and S-N application. It is NOT a configuration page — see [[riser-configurations]].

## Key Concepts

- **Ultimate Limit State (ULS) / extreme** — 100-year (or 10,000-year for high-consequence) wave + current + wind; checks maximum stress, equivalent strain, and burst.
- **Accidental Limit State (ALS)** — single-line failure of an adjacent line, mooring-line failure, dropped-object impact, fire and blast loads on the riser hang-off; extreme abnormal events.
- **Fatigue Limit State (FLS)** — wave-induced fatigue (1st-order), low-frequency vessel-motion fatigue (2nd-order), VIV fatigue (current-driven), slugging-induced fatigue (multiphase flow), and installation fatigue.
- **Serviceability Limit State (SLS)** — interference clearance, pigging access, tool-passage drift, and operability angle envelope.
- **Installation cases** — pull-in / pull-up, hang-off-during-storm, transfer to the floater, abandonment and recovery; often govern wall thickness for reeled flexibles.
- **Operating envelopes** — top-tension band, vessel-offset envelope, departure-angle envelope, top-angle envelope at the vessel connector.
- **Required outputs** — effective tension, bending moment, von Mises stress, curvature, contact pressure, fatigue damage per node.

## Standards / References

- DNV-OS-F201 (Dynamic Risers) — limit-state framework for metallic risers: [DNV-OS-F201](../../../engineering-standards/wiki/standards/dnv-os-f201.md).
- API STD 2RD (Dynamic Risers for Floating Production Systems): [API STD 2RD](../../../engineering-standards/wiki/standards/api-std-2rd.md).
- API RP 16Q (Marine Drilling Riser Systems) — drilling-riser load cases: [API RP 16Q](../../../engineering-standards/wiki/standards/api-rp-16q.md).
- ISO 19901-7 (Stationkeeping) — vessel-offset envelope feeding the riser load case: [ISO 19901-7](../../../engineering-standards/wiki/standards/iso-19901-7.md).

## Cross-References

- [[riser-steel-catenary-design]] — design state where ULS, ALS, and FLS converge at TDP and hang-off.
- [[riser-top-tensioned-design]] — top-tension envelope as the central design constraint.
- [[riser-flexible-design]] — installation cases that often govern wall design.
- [[riser-drilling-system]] — connected and disconnected cases plus recoil.
- [[viv-riser-fatigue]] — VIV-fatigue mechanics inside the FLS bucket.
