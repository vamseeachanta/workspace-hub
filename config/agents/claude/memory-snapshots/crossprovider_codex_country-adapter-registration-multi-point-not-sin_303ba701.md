---
name: crossprovider codex country-adapter-registration-multi-point-not-sin
description: Country adapter registration: multi-point, not single file
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [adapter-registration, multi-file-change]
---

Adding a new country adapter requires updates across: router query handler, test count assertions, fiscal coefficient mappings, module manifest registry, package metadata, and import-forbid test lists. Missing any point leaves adapter partially unwired or discoverable but untestable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
