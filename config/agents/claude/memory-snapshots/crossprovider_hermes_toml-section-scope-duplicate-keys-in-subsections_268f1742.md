---
name: crossprovider hermes toml-section-scope-duplicate-keys-in-subsections
description: TOML section scope: duplicate keys in subsections parse as nested fields
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [toml, config, parsing]
---

Lines after a TOML [section] header belong to that section until the next header. Duplicate keys like `model = "gpt-5.4"` under [features] are parsed as `features.model`, causing type mismatches. Removing duplicates from subsections is simpler than schema changes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
