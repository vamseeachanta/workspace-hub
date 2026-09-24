---
name: crossprovider codex approval-comment-parser-is-token-based-not-schem
description: Approval-comment parser is token-based, not schema-backed
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow-architecture, approval-gate, continuous-planning]
---

The continuous-planning-pipeline's `has_canonical_approval_comment()` function uses token-matching (looking for specific phrases like 'approve', 'revise', 'hold', plan filename, SHA) rather than schema validation. This brittleness means future approval-workflow changes should migrate to structured comment validation (JSON/YAML block or similar) to reduce false positives and enable robust parsing at scale.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
