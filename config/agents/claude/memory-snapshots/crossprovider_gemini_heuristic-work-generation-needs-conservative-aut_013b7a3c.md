---
name: crossprovider gemini heuristic-work-generation-needs-conservative-aut
description: Heuristic work generation needs conservative auto-action caps
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [automation, heuristics, work-queue, governance]
---

When tools classify items heuristically and auto-generate follow-on work (e.g., child WRKs), cap auto-creation to top N or generate report-only; never auto-create without human review of the heuristic itself. Prevents work-queue spam from misclassifications (WRK-1144).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
