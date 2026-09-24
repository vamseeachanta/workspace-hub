---
name: crossprovider codex syntax-validation-does-not-prove-provenance
description: Syntax validation does not prove provenance
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, provenance, security]
---

A regex-only format check (e.g., `^ams_[0-9a-f]{32}$`) can be forged independently of the actual evidence it claims to reference. Always anchor validation tokens to their source artifacts; checking only grammar allows any syntactically valid ID to pass, even if it does not exist in the validated evidence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
