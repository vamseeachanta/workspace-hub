---
name: crossprovider hermes hermes-config-key-display-vs-storage-divergence
description: Hermes config key display vs storage divergence
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, config, tooling-quirk]
---

Hermes displays config keys one way (e.g., `wiki.path`) but stores them with a `skills.config.` prefix (e.g., `skills.config.wiki.path`). When debugging config issues, search storage using the prefixed form, not the display key.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
