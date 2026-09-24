---
name: crossprovider codex manifest-validation-must-verify-artifact-claims-
description: Manifest validation must verify artifact claims against filesystem
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, data-integrity, manifests, testing]
---

Schema-level validation (field presence, vocabulary) hides artifact-binding gaps. For manifests claiming files, verify existence and measure size/hash match actual filesystem at validation time. Tests using fake checksums and non-existent paths hide real gaps.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
