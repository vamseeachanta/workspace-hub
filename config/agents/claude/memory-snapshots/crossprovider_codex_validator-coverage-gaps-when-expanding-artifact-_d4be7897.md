---
name: crossprovider codex validator-coverage-gaps-when-expanding-artifact-
description: Validator coverage gaps when expanding artifact types
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [validation, testing, quality-gates]
---

When a validator passes for one artifact type (e.g., manifest JSONL), it may silently fail on related types due to stricter or asymmetric requirements (e.g., manifest validator requires `title` field but candidate JSONL has legitimate blank titles). Expand validators with a test matrix covering all downstream artifact types.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
