---
name: crossprovider codex csv-jsonl-parity-validators-must-detect-content-
description: CSV+JSONL parity validators must detect content drift, not just row counts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, multi-format-data, fail-closed, csv-jsonl-sync]
---

When validating multi-format graph manifests, header-only CSV paired with populated JSONL is a silent data loss failure. Validator must check not just row counts but actual content parity between formats, failing closed on any discrepancy. Row-count matching is insufficient.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
