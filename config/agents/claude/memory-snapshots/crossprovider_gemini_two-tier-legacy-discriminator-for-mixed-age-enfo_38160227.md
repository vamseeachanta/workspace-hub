---
name: crossprovider gemini two-tier-legacy-discriminator-for-mixed-age-enfo
description: Two-tier legacy discriminator for mixed-age enforcement
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [gate-contracts, backward-compat, temporal-logic]
---

When backfilling enforcement onto a system with mixed old/new items, use a primary reliable field (e.g., numeric id < 658) for legacy skip, then secondary date field (created_at) for new items only. Avoids failures from missing/malformed dates in old data—Tier 1 id-based skip is always reliable regardless of created_at state.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
