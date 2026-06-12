---
name: crossprovider hermes non-anchored-path-rewriting-acceptable-with-docu
description: Non-anchored path rewriting acceptable with documented limitations and targeted tests
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [architecture, paths, design-philosophy]
---

A shared workspace path normalizer that rewrites suffixes without canonical anchoring is acceptable if limitations are documented and tested explicitly. This avoids over-engineering full canonical resolution for log-processing use cases.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
