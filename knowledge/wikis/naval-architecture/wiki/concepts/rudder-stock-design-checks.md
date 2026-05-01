---
title: "Rudder Stock Design Checks"
tags: [rudder-stock, steering-gear, scantlings, standards]
sources:
  - /mnt/ace/O&G-Standards/SNAME/textbooks/SOLAS-2020-Consolidated-Edition.pdf
  - /mnt/ace/acma-codes/DNV Rules/2010 DNV/2010 Ship Rules/ts414, steering gear.pdf
  - /mnt/local-analysis/workspace-hub/docs/plans/2026-04-30-issue-2565-rudder-stock-torque-sweep-input.md
added: 2026-05-01
last_updated: 2026-05-01
---

# Rudder Stock Design Checks

This page separates **rudder-stock design checks** from the preliminary rudder-force / torque calculations already present in the repo.

## Concept boundary

Rudder-stock design checks can include:

- required stock diameter / section properties
- combined torque and bending checks
- connection details in way of tiller / rotor / hub
- keyway or friction-fit limits where applicable
- bearing load interactions transmitted through the steering gear
- rule-defined safety factors and allowable stresses

## Not the same as preliminary holding torque

The existing preliminary workflow computes a torque envelope useful for sensitivity studies. That does **not** by itself answer:

- whether the stock diameter is sufficient
- whether combined bending + torsion is acceptable
- whether the hub / key / friction connection is adequate
- whether local stress concentrations are acceptable
- whether a given arrangement satisfies class-rule details

## Local rule anchors identified

### SOLAS role
SOLAS II-1 Reg. 29 references the rudder stock mainly as part of the steering system safety envelope:
- components and rudder stock must be of sound and reliable construction
- certain rudder-stock diameter thresholds trigger power-operation / alternate power requirements

Use: regulatory framing only.

### DNV TS414 role
The local DNV steering-gear chapter is the strongest discovered class candidate because the extracted text explicitly exposes headings for:
- rudder stock diameter
- design torque
- safety factor for rudder stock
- connection between steering gear and rudder stock

Use: candidate class-rule basis for later child issues.

## Why this issue stopped at decomposition

The repo currently lacks a promoted, clause-governed standards package for rudder-stock scantling work. Without that, any formula implementation would risk:

- edition drift
- incorrect authority mixing between SOLAS and class rules
- overclaiming compliance
- silent omission of connection / key / bearing interactions

## Practical decomposition slices

1. **Rudder-stock clause extraction** — exact class-rule formulas and definitions.
2. **Connection-capacity checks** — keyed, keyless, split-hub, shrink-fit, or frictional arrangements.
3. **Combined load checks** — torque + bending envelopes.
4. **Bearing / actuator-induced radial load interactions** — separate because these often sit at the steering-gear/rudder-stock boundary.

## Current safe claim

The safe current claim is only:
- workspace-hub has a preliminary torque workflow from #2565
- #2567 now maps the standards and source gaps needed before standards-backed rudder-stock checks can be implemented

## Related pages

- [[steering-gear-design-checks]]
- [[rudder-force-modeling]]
- [Issue #2567 source map](../comparisons/issue-2567-steering-gear-rudder-stock-source-map.md)
- [Standards crosswalk](../standards/steering-gear-rudder-stock-rule-crosswalk.md)
