---
name: crossprovider gemini patch-preservation-and-intelligent-reapply-patte
description: Patch preservation and intelligent reapply pattern for tool updates
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [tool-management, update-lifecycle, local-state-preservation, patch-merge-strategy]
---

When a tool update wipes local modifications, implement a patch backup/reapply system that detects backed-up patches, intelligently merges them (skipping if upstream incorporated), and handles conflicts interactively. This prevents loss of machine-specific customizations across forced updates.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
