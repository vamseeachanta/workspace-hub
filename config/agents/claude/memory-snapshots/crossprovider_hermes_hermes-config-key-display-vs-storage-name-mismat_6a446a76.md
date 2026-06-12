---
name: crossprovider hermes hermes-config-key-display-vs-storage-name-mismat
description: Hermes config key display vs. storage name mismatch
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes-config, cli-ux]
---

Hermes displays config keys to users as short names (e.g., `wiki.path`) but stores them with a namespace prefix (`skills.config.wiki.path`). User-facing commands use the short name; programmatic access and `hermes config set` require the prefixed form. This causes confusion when setting values—must use `hermes config set skills.config.wiki.path <value>`, not the short name.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
