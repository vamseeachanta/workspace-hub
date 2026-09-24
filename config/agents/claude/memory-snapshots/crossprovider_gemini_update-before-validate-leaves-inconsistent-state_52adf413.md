---
name: crossprovider gemini update-before-validate-leaves-inconsistent-state
description: Update-before-validate leaves inconsistent state on failure
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [state-management, validation, scripts]
---

Scripts that modify files before running validation leave those files in an inconsistent state if validation fails (e.g., status: working but gate fails). Validate first, then update, or implement transactional semantics (backup on failure).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
