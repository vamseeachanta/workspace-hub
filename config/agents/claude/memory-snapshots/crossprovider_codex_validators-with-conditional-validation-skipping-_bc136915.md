---
name: crossprovider codex validators-with-conditional-validation-skipping-
description: Validators with conditional validation skipping can mask coordination errors
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [validation, schema, state-management]
---

A validator that skips validation in non-ready state (e.g., `implementation_ready=false`) can silently pass stale or wrong data in those conditionally-unchecked fields. The #66 split registry entry had wrong plan path and status but passed validation because plan-path/status checks were skipped for draft rows. Stale coordination state surfaces only during manual artifact review, creating coordination debt.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
