---
name: crossprovider codex completeness-gate-body-fenced-record-label-timin
description: Completeness gate: body-fenced record, label timing, owner verification
metadata:
  type: reference
  source: codex
  bridged: 2026-06-19
  tags: [completeness-gate, github-workflow]
---

Closeout sequence: body edit with fenced ```completeness {...}``` record (body lastEditedAt = freshness base), then apply status:completeness-verified by owner. Gate checks label is newer than record. Sequence matters: record first, label after.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
