---
name: crossprovider hermes handoff-operational-prompts-should-reference-not
description: Handoff/operational prompts should reference not duplicate numeric data
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [documentation, maintainability, data-duplication]
---

Embedding field values (tax amounts, filing dates) in prompts increases staleness risk and maintenance burden. Reference authoritative source files (filing guide, specs) instead; update source once and prompts inherit.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
