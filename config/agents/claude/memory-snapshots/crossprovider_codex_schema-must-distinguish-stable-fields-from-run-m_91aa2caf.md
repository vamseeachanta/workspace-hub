---
name: crossprovider codex schema-must-distinguish-stable-fields-from-run-m
description: Schema must distinguish stable fields from run metadata
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [planning, schema, determinism]
---

Observed timestamps, sizes, and owner fields are environment-dependent; separate them from stable fields and define normalization. Repeat-scan test alone does not prove determinism; need field taxonomy + byte-identity test.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
