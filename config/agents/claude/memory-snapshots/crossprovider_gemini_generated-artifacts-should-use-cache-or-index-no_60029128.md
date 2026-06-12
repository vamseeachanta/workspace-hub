---
name: crossprovider gemini generated-artifacts-should-use-cache-or-index-no
description: Generated artifacts should use cache/ or .index/, not config/
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [storage, gitignore, architecture]
---

Storing generated indices, baselines, or reports in version-controlled `config/` directories risks accidental commits. Use `.cache/`, `.index/`, or `tmp/` for ephemeral artifacts; reserve `config/` for authored config files only (WRK-1085).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
