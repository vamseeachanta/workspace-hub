---
name: crossprovider gemini multi-provider-degraded-mode-policy-must-be-docu
description: Multi-provider degraded-mode policy must be documented and approved before execution
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [multi-agent, operations]
---

When orchestrating work across multiple providers (e.g., Claude, Codex, Gemini planning passes), explicit policy for handling unavailability (quota-block, auth failure) is needed before starting. Default should be to pause; degraded mode continues only after explicit user approval naming the missing provider.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
