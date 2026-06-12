---
name: crossprovider hermes function-docstring-security-claims-must-cover-bo
description: Function docstring security claims must cover both return value and side effects
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, redaction, API-contract]
---

Functions claiming "secret-free readiness report" were redacting CLI output and file writes but returning raw token material to programmatic callers. Verification must check both: (a) the returned object's fields, and (b) all side effects (stdout, stderr, files). Test coverage gap: programmatic caller redaction is often unmeasured.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
