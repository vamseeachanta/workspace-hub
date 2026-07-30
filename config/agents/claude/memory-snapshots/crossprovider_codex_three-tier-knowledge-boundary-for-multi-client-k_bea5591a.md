---
name: crossprovider codex three-tier-knowledge-boundary-for-multi-client-k
description: Three-tier knowledge boundary for multi-client knowledge systems
metadata:
  type: reference
  source: codex
  bridged: 2026-07-12
  tags: [governance, privacy-firewall, multi-client-architecture]
---

When processing knowledge across multiple clients: raw source documents remain in controlled locations; client-specific processed knowledge routes to `llm-wiki-<client>` private repos; only deduplicated, de-identified, generalized knowledge routes to shared `llm-wiki`. This pattern prevents confidential leakage while enabling knowledge reuse.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
