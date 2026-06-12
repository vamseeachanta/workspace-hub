---
name: crossprovider hermes cross-layer-boundary-vocabularies-must-be-exact-
description: Cross-layer boundary vocabularies must be exact-matched strings or enum-backed
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [architecture-boundaries, integration-contract, fail-open-risk]
---

Data layer defined source registries as mounted_source_registry (underscore), but execution layer used mounted-source-registry (dash). Boundary validation failed silently; manifests satisfied local contract but couldn't cross-check against data-layer registry definitions. Boundaries require either strict enum backing or canonicalized vocabulary spec shared across layers, not free-form strings.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
