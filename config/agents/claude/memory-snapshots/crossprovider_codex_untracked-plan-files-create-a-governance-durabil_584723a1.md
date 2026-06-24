---
name: crossprovider codex untracked-plan-files-create-a-governance-durabil
description: Untracked plan files create a governance/durability gap at review gates
metadata:
  type: reference
  source: codex
  bridged: 2026-06-23
  tags: [governance, git-tracking, review-gates]
---

Plan files must be git-tracked before they enter review; an untracked plan cannot be referenced in a closed review decision or audit trail, even if the content is sound. This creates a durability gap because future work cannot verify what was approved.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
