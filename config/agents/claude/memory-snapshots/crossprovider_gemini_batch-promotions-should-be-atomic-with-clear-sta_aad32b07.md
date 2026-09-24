---
name: crossprovider gemini batch-promotions-should-be-atomic-with-clear-sta
description: Batch promotions should be atomic with clear state tracking
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [atomicity, state-management, promotion]
---

When promoting offline IDs to real IDs, atomic rename (file + asset dir + frontmatter + GitHub update) prevents split-state corruption. Log completions for visibility.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
