---
title: "Integrity Management Cycle"
tags: [asset-management, engineering-scope, operating-practices, integrity-management, anomaly-management]
added: 2026-05-03
last_updated: 2026-05-03
manual-review: pending
sources:
  - dnv-rp-g101
  - norsok-z-008
cross_links:
  - asset-management/concepts/risk-based-inspection
  - engineering/concepts/cathodic-protection-design
---

# Integrity Management Cycle

## Scope

Engineering / integrity asset management — see scope-boundary block in [index.md](../index.md). The closed-loop operating practice that ties inspection planning to anomaly management to engineering re-evaluation to scheduled-work execution.

## Definition

The integrity management cycle is the continuous, closed-loop sequence by which an asset operator plans, executes, evaluates, and acts on integrity activities — typically: identify threats → assess risk → plan inspection → execute → evaluate findings → manage anomalies → update risk model → re-plan.

## Methodology / Mechanics

- Anomaly management (sub-section): every recorded anomaly carries a disposition decision (acceptable as-is / monitor / repair / replace) traceable through the cycle.
- Closed-loop KPIs: inspection backlog, anomaly aging, repair-MTTR, RBI-coverage.
- Governance via integrity steering committee at the installation / fleet level.

## Standards Backbone

- [DNV-RP-G101](../standards/dnv-rp-g101.md) — RBI substrate.
- [API RP 580](../standards/api-rp-580.md) — qualitative methodology.
- [NORSOK Z-008](../standards/norsok-z-008.md) — consequence classification.
- [ISO 55001](../standards/iso-55001.md) §9 (Performance evaluation) — closed-loop requirement.

## Cross-links

- Inspection driver: [Risk-Based Inspection](./risk-based-inspection.md).
- Engineering peer: [Cathodic Protection Design](../../../engineering/wiki/concepts/cathodic-protection-design.md) (CP is a maintenance-side input).

## Open questions / gaps

- Dedicated anomaly-management page may split out if this section grows.
