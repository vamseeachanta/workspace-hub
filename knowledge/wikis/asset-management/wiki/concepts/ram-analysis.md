---
title: "RAM Analysis (Reliability, Availability, Maintainability)"
tags: [asset-management, engineering-scope, decision-frameworks, ram, reliability]
added: 2026-05-03
last_updated: 2026-05-03
manual-review: pending
sources:
  - norsok-z-008
cross_links:
  - asset-management/concepts/integrity-management-cycle
---

# RAM Analysis (Reliability, Availability, Maintainability)

## Scope

Engineering / integrity asset management — see scope-boundary block in [index.md](../index.md). Reliability, Availability, Maintainability analysis for production-system performance modelling.

## Definition

RAM analysis quantifies expected production availability of a complex system by modelling component-level reliability, repair distributions, redundancy, sparing, and logistics. The output is typically a P50/P90 availability and a ranked list of availability-killing components.

## Methodology / Mechanics

- Reliability Block Diagrams or Monte-Carlo simulation.
- OREDA / NPRD / proprietary failure-rate datasets.
- Outputs feed sparing strategy, maintenance philosophy, and CAPEX-vs-OPEX trade studies.

## Standards Backbone

- [NORSOK Z-008](../standards/norsok-z-008.md) — consequence classification consumes RAM-style inputs.
- [API RP 581](../standards/api-rp-581.md) — uses generic failure frequencies that overlap RAM datasets.

## Cross-links

- Inspection coupling: [Risk-Based Inspection](./risk-based-inspection.md).
- Operating practice: [Integrity Management Cycle](./integrity-management-cycle.md).

## Open questions / gaps

- Software-tool inventory (Maros, Taro, custom) page deferred.
