---
name: crossprovider hermes schema-strictness-is-load-bearing-for-publicatio
description: Schema strictness is load-bearing for publication gates
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [schema-design, contract-enforcement, publication-gates, vocabulary-alignment]
---

Adversarial reviews of execution/report layers (#2728/#2729) found prose contracts fail closed only if schemas use strict enums, not generic types (string/array/object). Freeform residency fields and unconstrained item schemas silently accept under-specified manifests that violate stated governance; both layers must share closed vocabulary for machine-checkable publication gates.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
