---
name: crossprovider codex stderr-review-promotion-requires-exit-code-valid
description: stderr review promotion requires exit-code validation; never promote timeout/killed results
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [error-handling, review-validation, artifact-safety]
---

Promoting provider stderr as a review artifact when rc != 0 risks promoting partial/killed output: a timeout (rc=124) or killed process (rc=137) can emit partial structured headers that should never become authoritative review signal. Validation must gate promotion on rc=0, with explicit UNAVAILABLE stubs for nonzero exits.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
