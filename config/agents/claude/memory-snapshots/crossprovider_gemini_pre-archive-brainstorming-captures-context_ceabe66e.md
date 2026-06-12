---
name: crossprovider gemini pre-archive-brainstorming-captures-context
description: Pre-archive brainstorming captures context
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [workflow, work-queue, capture]
---

Run future-work suggestions BEFORE archiving items, not after. WRK-134 proposes suggest-future-work.sh as pre-archive step (archive-item.sh calls it before moving file), while context is fresh and user can abort to act immediately. Post-archive brainstorming loses context.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
