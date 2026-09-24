---
name: crossprovider codex hash-boundaries-must-include-transitive-dependen
description: Hash boundaries must include transitive dependencies, not just primary artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [artifact-integrity, architecture, identity, verification]
---

A model hash covering only master.yml while includes/parameters.yml or configuration varies enables identical hashes with different semantics. Define clean staging rules, transitive dependency closure, and separate hashes for transfer bundle (what's shipped) vs solver-loaded/saved state (what executes).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
