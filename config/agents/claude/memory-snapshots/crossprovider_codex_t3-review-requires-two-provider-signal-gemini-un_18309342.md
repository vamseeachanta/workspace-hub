---
name: crossprovider codex t3-review-requires-two-provider-signal-gemini-un
description: T3 review requires two-provider signal; Gemini unavailability = allowed T3→T2 degradation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [code-review, multi-provider, governance]
---

Multi-provider review (Claude + Codex + Agy) is T3 standard. When a provider is unavailable (authentication or quota), downgrade to T2 and document the degradation. Do not cycle indefinitely waiting for the unavailable provider.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
