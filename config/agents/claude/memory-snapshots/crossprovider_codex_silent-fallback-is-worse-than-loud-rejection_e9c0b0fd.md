---
name: crossprovider codex silent-fallback-is-worse-than-loud-rejection
description: Silent fallback is worse than loud rejection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [error-handling, robustness, automation]
---

When automation scripts auto-default to a fallback (e.g., unknown domain → generic template, typo in domain arg → generic), they create invalid output that succeeds silently. This masks errors and makes troubleshooting harder. Prefer explicit rejection with a clear error message over silent degradation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
