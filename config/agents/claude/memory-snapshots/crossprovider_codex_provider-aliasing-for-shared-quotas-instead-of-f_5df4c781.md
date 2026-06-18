---
name: crossprovider codex provider-aliasing-for-shared-quotas-instead-of-f
description: Provider aliasing for shared quotas instead of fabricated entries
metadata:
  type: reference
  source: codex
  bridged: 2026-06-16
  tags: [quota, provider-model, multi-provider]
---

When a tool (e.g., Hermes) uses another provider's quota (Codex/OpenAI), use explicit aliasing (H=O) rather than inventing a separate quota entry. Reflects actual shared subscription model and avoids false provider counts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
