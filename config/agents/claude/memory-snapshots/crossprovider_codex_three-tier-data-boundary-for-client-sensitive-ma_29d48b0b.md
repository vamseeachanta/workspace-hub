---
name: crossprovider codex three-tier-data-boundary-for-client-sensitive-ma
description: Three-tier data boundary for client-sensitive material
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-handling, client-confidentiality]
---

When ingesting knowledge from multiple clients: raw documents remain in their controlled source locations, client-specific processed knowledge routes to `llm-wiki-<client>`, and only deduplicated, de-identified, generalized knowledge enters the shared `llm-wiki`. This prevents cross-client knowledge leakage and preserves confidentiality boundaries.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
