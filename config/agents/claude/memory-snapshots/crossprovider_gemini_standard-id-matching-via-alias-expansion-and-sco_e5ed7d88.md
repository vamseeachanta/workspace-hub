---
name: crossprovider gemini standard-id-matching-via-alias-expansion-and-sco
description: Standard ID matching via alias expansion and score-based ranking
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [matching, standards-lookup, robustness]
---

Expand each standard ID to aliases (e.g., DNV-OS-F101 → ['dnv os f101', 'dnv-os-f101', 'osf101']); score document records by alias hits, prefer multi-hit records. Handles variant formatting and abbreviations gracefully.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
