---
name: crossprovider hermes public-data-claims-require-explicit-false-positi
description: Public data claims require explicit false-positive exclusion test cases
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-validation, public-artifacts, testing, statistics]
---

Hurricane infographic used broad substring matches ('weather', 'sank', 'overboard') that over-counted non-relevant rows in public statistics claims. Fix required narrowing to explicit incident pathways (storm_weather, wave_sea_state, water_ingress) and adding test cases that explicitly assert exclusion of false-positive rows by incident ID. Public artifacts need data validation beyond generation tests.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
