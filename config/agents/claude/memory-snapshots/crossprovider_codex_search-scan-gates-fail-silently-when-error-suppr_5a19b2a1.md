---
name: crossprovider codex search-scan-gates-fail-silently-when-error-suppr
description: Search/scan gates fail silently when error-suppressed
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [error-handling, gates, validation, shell-safety]
---

The pattern `command || true` converts both "no matches" (exit 0) and errors like permission-denied, timeout, or unreadable path (exit 2) into PASS. Gates claiming "zero security leaks found" or "no legal conflicts" via grep/rg with `|| true` cannot distinguish between "secure" and "failed to scan." Audit every pass verdict and remove error suppression from gates—let failures fail so they surface.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
