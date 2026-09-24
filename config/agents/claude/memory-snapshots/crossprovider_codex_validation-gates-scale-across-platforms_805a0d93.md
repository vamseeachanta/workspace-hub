---
name: crossprovider codex validation-gates-scale-across-platforms
description: Validation gates scale across platforms
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, validation, infrastructure, digitalmodel]
---

Model validation complexity increases sequentially: Linux-only validation (schema, YAML determinism, regression tests) precedes Windows-only licensed OrcaFlex validation (load, export, statics). Issue #604 (Ballymore OrcaFlex validation) explicitly depends on #602/#603 Linux gates completing first; don't merge Windows validation into Linux test pipelines.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
