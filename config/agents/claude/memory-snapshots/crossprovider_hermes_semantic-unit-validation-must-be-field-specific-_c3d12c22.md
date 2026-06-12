---
name: crossprovider hermes semantic-unit-validation-must-be-field-specific-
description: Semantic unit validation must be field-specific, not generic
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [schema-validation, type-safety, unit-systems]
---

Each semantically typed field (pressure_rating, voltage_class, design_temperature, water_depth, density) must enforce its own allowed-unit set independently. Generic unit validation or shared enums fail because pressure-rated fields cannot accept voltage or temperature units. Discovered in #2514 subsea schema validation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
