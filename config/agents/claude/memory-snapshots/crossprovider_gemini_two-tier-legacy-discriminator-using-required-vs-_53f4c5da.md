---
name: crossprovider gemini two-tier-legacy-discriminator-using-required-vs-
description: Two-tier legacy discriminator using required vs. optional fields
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [patterns, legacy-handling, robustness]
---

When discriminating legacy from new items where legacy items may lack optional metadata, use a required/always-present field as primary tier (e.g., WRK id < 658 = legacy) and optional fields as secondary (e.g., created_at for id >= 658). This avoids brittleness where missing optional fields on legacy items would incorrectly fail validation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
