---
name: crossprovider codex multi-source-data-systems-declare-availability-m
description: Multi-source data systems declare availability matrix upfront
metadata:
  type: reference
  source: codex
  bridged: 2026-07-05
  tags: [data-architecture, multi-source, requirements]
---

When extending data infrastructure to new sources, explicitly declare what lifecycle/capability stages are available from each source (e.g., via DataAvailability enum) rather than promising complete coverage. This prevents overpromises like 'entire lifecycle' when sources have gaps (RRC public dumps lack well-path/casing data in field-development context).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
