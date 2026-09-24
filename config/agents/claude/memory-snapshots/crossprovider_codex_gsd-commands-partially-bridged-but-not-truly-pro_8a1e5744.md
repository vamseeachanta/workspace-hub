---
name: crossprovider codex gsd-commands-partially-bridged-but-not-truly-pro
description: GSD commands partially bridged but not truly provider-neutral
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [command-abstraction, provider-neutrality, architecture]
---

GSD intent (e.g., `plan-phase`) is duplicated across providers with different invocation surfaces: Claude uses `/gsd:plan-phase`, Codex uses skill aliases like `gsd-plan-phase`, with no canonical CLI wrapper. To achieve true provider neutrality, separate command definition (spec + implementation) from provider-specific transport adapters, then generate provider surfaces from a single source.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
