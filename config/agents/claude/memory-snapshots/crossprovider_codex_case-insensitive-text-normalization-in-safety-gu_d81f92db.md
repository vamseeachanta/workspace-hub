---
name: crossprovider codex case-insensitive-text-normalization-in-safety-gu
description: Case-insensitive text normalization in safety guards needs bidirectional normalization
metadata:
  type: reference
  source: codex
  bridged: 2026-06-16
  tags: [security, string-matching, safety-gates]
---

String-matching guard lowercases output text but compared against non-normalized catalog, creating bypass risk: `C:\path` and `/Volumes/path` were allowed when they should be blocked. Normalize both the text and each catalog term to the same case before comparison.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
