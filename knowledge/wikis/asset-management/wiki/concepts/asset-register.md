---
title: "Asset Register"
tags: [asset-management, engineering-scope, foundations, register]
added: 2026-05-03
last_updated: 2026-05-03
manual-review: pending
sources:
  - iso-55000
cross_links:
  - asset-management/concepts/asset-lifecycle
---

# Asset Register

## Scope

Engineering / integrity asset management — see scope-boundary block in [index.md](../index.md). The asset register is the foundation data structure for engineering asset management; it is NOT a financial fixed-asset ledger.

## Definition

An asset register is the authoritative record of every physical asset within scope of the asset-management system. Each entry carries an identifier, classification, location, and pointers to the configuration management, criticality, performance-standard, and inspection-history records.

## Methodology / Mechanics

- Identifier scheme stable across CMMS, EAM, ERP, and engineering document control.
- Hierarchy: site → installation → system → equipment → component.
- Linked to safety-critical-element classification and performance standards.

## Standards Backbone

- [ISO 55001](../standards/iso-55001.md) §7.5 (Information requirements).
- [ISO 55002](../standards/iso-55002.md) — application guidance for register design.

## Cross-links

- Lifecycle context: [Asset Lifecycle](./asset-lifecycle.md).
- Maintenance use: [Integrity Management Cycle](./integrity-management-cycle.md).

## Open questions / gaps

- Register-vs-CMMS-vs-digital-twin source-of-truth ambiguity needs follow-up.
