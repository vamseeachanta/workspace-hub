---
name: crossprovider hermes yaml-registry-patching-preserves-formatting-bett
description: YAML registry patching preserves formatting better than full rewrite
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [yaml, infra, file-manipulation]
---

PyYAML safe_dump rewrites the entire file, losing comments and formatting. For targeted registry changes (e.g., adding tier1_baseline block), patch specific line ranges manually instead of load-modify-dump cycle.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
