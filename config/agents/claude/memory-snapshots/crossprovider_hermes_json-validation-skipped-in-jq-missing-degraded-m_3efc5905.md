---
name: crossprovider hermes json-validation-skipped-in-jq-missing-degraded-m
description: JSON validation skipped in jq-missing degraded mode
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [json, validation, degraded-mode, bug]
---

sync_json_merge() jq-missing branch copies template directly without calling validate_json_file(). Invalid JSON can be written to canonical files when jq is unavailable. Degraded mode must still validate outputs before writing canonical state.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
