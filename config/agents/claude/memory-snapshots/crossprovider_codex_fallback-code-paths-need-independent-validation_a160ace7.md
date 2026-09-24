---
name: crossprovider codex fallback-code-paths-need-independent-validation
description: Fallback code paths need independent validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, testing, code-review]
---

Issue #51's `--scan-public-path` flag applied only generic regexes, not full traversal checks from main paths, creating a coverage gap. Don't assume fallback/conditional code paths inherit validation logic; verify empirically in review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
