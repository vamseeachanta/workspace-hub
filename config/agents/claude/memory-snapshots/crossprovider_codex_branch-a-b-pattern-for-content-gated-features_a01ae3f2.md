---
name: crossprovider codex branch-a-b-pattern-for-content-gated-features
description: Branch A/B pattern for content-gated features
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architectural-pattern, content-gates, branching-strategy]
---

When a feature's full implementation (Branch A) is blocked by external content availability (e.g., missing wiki preview data), design a Branch B that adds guards and tests without content writes. Execute Branch B when content gate fails, deferring Branch A to follow-up issues; approval can bind conditionally to either path.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
