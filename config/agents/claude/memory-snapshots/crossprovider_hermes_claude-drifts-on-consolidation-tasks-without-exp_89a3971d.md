---
name: crossprovider hermes claude-drifts-on-consolidation-tasks-without-exp
description: Claude drifts on consolidation tasks without explicit keep/remove rosters
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [delegation, ai-behavior, deduplication]
---

When delegating skill/doc dedup, Claude preserves undesired copies unless given explicit 'keep: [list]' and 'remove: [list]' paths. Even explicit instructions may produce partial reverts if phrased ambiguously.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
