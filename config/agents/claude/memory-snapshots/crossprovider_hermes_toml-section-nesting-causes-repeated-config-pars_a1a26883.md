---
name: crossprovider hermes toml-section-nesting-causes-repeated-config-pars
description: TOML section-nesting causes repeated config parse failures
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [shell-config, toml-parsing, gotcha]
---

Keys appearing after a [section] header belong to that section, not the top-level scope. The .codex/config.toml case had `model` and `model_reasoning_effort` duplicated under [features], causing "invalid type: string, expected boolean" errors. This pattern has recurred 10+ times; add validation or a lint gate to catch misplaced keys before load.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
