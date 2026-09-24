---
name: crossprovider gemini sequencing-gate-verify-prior-issues-landed-befor
description: Sequencing gate: verify prior issues landed before proceeding
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [planning, sequencing]
---

When a plan depends on prior issues, verify at plan-write time via `gh issue view`, `ls`, `sha256sum`. Don't assume merges happened; prevents rework caused by waiting on stale assumptions.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
