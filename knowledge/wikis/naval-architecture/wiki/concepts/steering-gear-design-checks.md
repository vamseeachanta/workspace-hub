---
title: "Steering Gear Design Checks"
tags: [steering-gear, machinery, rudder, standards]
sources:
  - /mnt/ace/O&G-Standards/SNAME/textbooks/SOLAS-2020-Consolidated-Edition.pdf
  - /mnt/ace/acma-codes/DNV Rules/2010 DNV/2010 Ship Rules/ts414, steering gear.pdf
  - /mnt/local-analysis/workspace-hub/data/document-index/online-resource-registry.yaml
added: 2026-05-01
last_updated: 2026-05-01
---

# Steering Gear Design Checks

This page defines the concept boundary for steering-gear checks discussed in issue #2567. It separates steering-gear design from the preliminary rudder-stock holding-torque sweep delivered under #2565.

## What this concept includes

Steering-gear design checks may include:

- main steering gear capability and availability
- auxiliary steering gear capability and emergency operability
- actuator design torque / pressure envelope
- steering gear to rudder-stock connection capacity
- stopper arrangements and bearing loads
- control-system independence, alarms, and alternate power provisions
- single-failure / non-duplicated actuator rules where applicable

## What this concept does **not** include

This concept page does **not** mean the repo currently has standards-backed formulas implemented for:

- actuator sizing
- hydraulic component selection
- detailed piping scantlings
- proof of SOLAS or class compliance
- final approval of any particular DNV / ABS / IACS edition as implementation authority

## Regulatory vs class-rule boundary

A critical distinction for #2567:

- **SOLAS / IMO text** states functional and safety requirements, operability expectations, redundancy expectations, and certain threshold triggers.
- **Class rules** such as DNV or ABS typically supply detailed machinery, connection, pressure, stopper, and bearing design formulas.

These should never be collapsed into a single vague "compliance check" bucket.

## Locally verified source roles

### SOLAS II-1 Regulation 29
Local extract confirms coverage of:
- main vs auxiliary steering gear definitions and requirements
- rudder travel timing requirements
- control-system and power-supply expectations
- alternate power requirements for larger rudder-stock diameters in way of tiller

Use: regulatory requirement framing.

### DNV TS414 steering gear chapter
Local extract confirms coverage of:
- design torque
- steering gear / rudder-stock connection
- stopper arrangement
- bearing loads
- additional requirements for non-duplicated rudder actuators

Use: candidate class-rule decomposition source.

## Recommended decomposition slices

1. **Regulatory requirement mapping** — SOLAS functional expectations only.
2. **Actuator load / pressure design slice** — class-rule driven.
3. **Connection-to-rudder-stock capacity slice** — class-rule driven.
4. **Bearing / stopper reaction slice** — class-rule driven.
5. **Control-system / independence / alternate power slice** — regulatory + interpretation crosswalk.

## Why #2565 is not enough

#2565 intentionally stops at a preliminary holding-torque envelope:

```text
T_stock = F_normal * arm_to_center_of_pressure
```

That output is not equivalent to steering-gear machinery design, steering system redundancy checks, actuator pressure sizing, or SOLAS/class proof.

## Related pages

- [[rudder-stock-design-checks]]
- [[rudder-force-modeling]]
- [Issue #2567 source map](../comparisons/issue-2567-steering-gear-rudder-stock-source-map.md)
- [Standards crosswalk](../standards/steering-gear-rudder-stock-rule-crosswalk.md)
