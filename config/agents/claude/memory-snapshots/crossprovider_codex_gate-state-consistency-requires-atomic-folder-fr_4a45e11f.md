---
name: crossprovider codex gate-state-consistency-requires-atomic-folder-fr
description: Gate state consistency requires atomic folder + frontmatter + evidence
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [workflow-integrity, state-management, validation]
---

Work queue items must keep three pieces synchronized: folder location (pending/working/done), frontmatter status field, and evidence artifacts (logs, review output, legal scan). If any diverges, validation fails silently downstream. Use an atomic close gate that updates all three together.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
