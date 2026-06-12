---
name: crossprovider codex fallback-code-must-defend-against-both-missing-c
description: Fallback code must defend against both missing columns and type mismatches
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [data-pipeline, error-handling, robustness]
---

Session 13 found RIG_NAME fallback crashed on missing column OR non-string type. Defensive fallback code must check both conditions: column existence + type compatibility, not just one.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
