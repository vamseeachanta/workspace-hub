---
name: crossprovider codex yaml-canonical-generated-markdown-drift-checking
description: YAML canonical + generated Markdown drift checking pattern
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [config-management, automation, data-consistency]
---

When configuration must have both machine-readable (YAML) and human-readable (Markdown) representations, make YAML the canonical source and generate Markdown from it. Enforce drift detection in pre-commit hooks (`sync-maturity-summary.py --check`) to prevent divergence; this is cheaper than post-hoc reconciliation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
