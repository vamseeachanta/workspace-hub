---
name: crossprovider gemini baseline-floor-schema-enforcement-emits-warnings
description: Baseline-floor schema enforcement emits warnings, not hard failures
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [standards, data-governance, schema, enforcement]
---

Wiki CLAUDE.md files declare required frontmatter fields (title, last_updated, doc_key, source_ref, promoted_from for regulatory domain). Non-compliance is emitted as a warning during promotion, not a block. This allows incremental rollout of standards while flagging drift that should eventually be resolved.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
