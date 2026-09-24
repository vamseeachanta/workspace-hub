---
name: crossprovider codex yaml-canonical-with-generated-markdown-and-drift
description: YAML-canonical with generated Markdown and drift validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, configuration, validation-pattern]
---

Use YAML as the single source of truth for structured data (e.g., maturity ledgers), generate derived Markdown for human consumption, and validate them against each other via pre-commit hooks to prevent divergence. This pattern prevents the Markdown becoming stale documentation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
