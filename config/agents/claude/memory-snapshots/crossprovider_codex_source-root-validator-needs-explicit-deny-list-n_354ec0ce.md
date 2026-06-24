---
name: crossprovider codex source-root-validator-needs-explicit-deny-list-n
description: Source-root validator needs explicit deny-list, not syntax-only checks
metadata:
  type: reference
  source: codex
  bridged: 2026-06-23
  tags: [validation, security, quirk]
---

Syntactic validation of source-root labels does not reject raw/private/local/mnt path aliases that appear valid structurally. Validators must include explicit deny-list rules to block suspicious path patterns by name.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
