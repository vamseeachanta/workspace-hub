---
name: crossprovider codex approval-comment-parsing-via-token-matching-crea
description: Approval-comment parsing via token matching creates truncation ambiguity
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [approval-gate, parsing-hazard, workflow]
---

`has_canonical_approval_comment()` in `scripts/ai/continuous-planning-pipeline.py` matches keywords rather than validating schema. When review artifacts are truncated mid-delivery, the parser cannot distinguish between incomplete evidence and missing canonical request.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
