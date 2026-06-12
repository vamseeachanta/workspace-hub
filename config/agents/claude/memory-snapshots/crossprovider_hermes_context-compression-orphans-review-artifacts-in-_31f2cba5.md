---
name: crossprovider hermes context-compression-orphans-review-artifacts-in-
description: Context compression orphans review artifacts in .planning/quick
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [context, artifacts, recovery]
---

Review prompts and provider output written to `.planning/quick/` become inaccessible after context compaction (no automatic recovery). Pattern: cache review artifacts to git-tracked paths or regenerate on resume. Gemini/Codex results should be persisted separately from volatile planning state.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
